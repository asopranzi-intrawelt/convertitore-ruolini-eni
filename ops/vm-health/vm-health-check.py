#!/usr/bin/env python3
"""Controllo di salute della VM, lanciato ogni 5 minuti da vm-health-check.timer.

Scrive gli allarmi nel journal con tag `vm-health` e, se in configurazione e'
impostato NOTIFY_CMD, passa il testo dell'allarme sullo standard input di quel
comando (per esempio un invio mail con msmtp, quando ci sara' un relay SMTP).

Controlli:
- un processo sopra CPU_PCT di un core per almeno CPU_INTERVALS esecuzioni
  consecutive (default: 80% per 6 giri, cioe' 30 minuti);
- swap usato oltre SWAP_MAX_MIB o memoria disponibile sotto MEMAVAIL_MIN_MIB;
- eventi dell'OOM killer nel journal del kernel dall'esecuzione precedente;
- servizi di produzione non attivi e risposta HTTP locale di nginx.

Lo stesso allarme non si ripete prima di REALERT_MIN minuti; quando la
condizione rientra si scrive una riga di rientro.
"""
import argparse
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request

DEFAULTS = {
    "CPU_PCT": "80",
    "CPU_INTERVALS": "6",
    "SWAP_MAX_MIB": "1024",
    "MEMAVAIL_MIN_MIB": "200",
    "REALERT_MIN": "60",
    "SYSTEM_SERVICES": "nginx.service",
    "USER_SERVICES": "intrawelt:intrapanel.service",
    "HTTP_URLS": "http://127.0.0.1/",
    "NOTIFY_CMD": "",
}
HZ = os.sysconf("SC_CLK_TCK")
HOST = os.uname().nodename


def load_conf(path):
    conf = dict(DEFAULTS)
    if os.path.exists(path):
        with open(path, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, value = line.split("=", 1)
                conf[key.strip()] = value.strip().strip('"')
    return conf


def read_procs():
    procs = {}
    for pid in os.listdir("/proc"):
        if not pid.isdigit():
            continue
        try:
            with open(f"/proc/{pid}/stat", encoding="utf-8", errors="replace") as fh:
                raw = fh.read()
        except OSError:
            continue
        comm = raw[raw.index("(") + 1:raw.rindex(")")]
        fields = raw[raw.rindex(")") + 2:].split()
        # fields[0] e' il campo 3 di proc(5): utime=14, stime=15, starttime=22
        ticks = int(fields[11]) + int(fields[12])
        procs[pid] = {"comm": comm, "start": fields[19], "ticks": ticks}
    return procs


def meminfo():
    values = {}
    with open("/proc/meminfo", encoding="utf-8") as fh:
        for line in fh:
            key, rest = line.split(":", 1)
            values[key] = int(rest.split()[0]) // 1024
    return values


def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True, check=False)


def top_processes():
    out = run(["ps", "-eo", "pid,user,%cpu,%mem,etime,comm", "--sort=-%cpu"]).stdout
    return "\n".join(out.splitlines()[:6])


def check_cpu(state, procs, now, conf):
    alerts = {}
    prev = state.get("procs", {})
    dt = now - state.get("ts", 0)
    if dt <= 0 or dt > 900:
        # Prima esecuzione o pausa lunga (riavvio, timer fermo): si riparte da zero
        for p in procs.values():
            p["high"] = 0
        return alerts
    limit = float(conf["CPU_PCT"])
    needed = int(conf["CPU_INTERVALS"])
    for pid, p in procs.items():
        old = prev.get(pid)
        p["high"] = 0
        if not old or old["start"] != p["start"]:
            continue
        pct = (p["ticks"] - old["ticks"]) / HZ / dt * 100
        if pct >= limit:
            p["high"] = old.get("high", 0) + 1
            if p["high"] >= needed:
                minutes = round(p["high"] * dt / 60)
                alerts[f"cpu:{p['comm']}"] = (
                    f"processo {p['comm']} (pid {pid}) al {pct:.0f}% di un core "
                    f"da almeno {minutes} minuti"
                )
    return alerts


def check_memory(conf):
    alerts = {}
    m = meminfo()
    swap_used = m["SwapTotal"] - m["SwapFree"]
    if swap_used > int(conf["SWAP_MAX_MIB"]):
        alerts["swap"] = f"swap usato {swap_used} MiB, soglia {conf['SWAP_MAX_MIB']} MiB"
    if m["MemAvailable"] < int(conf["MEMAVAIL_MIN_MIB"]):
        alerts["memavail"] = (
            f"memoria disponibile {m['MemAvailable']} MiB, soglia {conf['MEMAVAIL_MIN_MIB']} MiB"
        )
    return alerts


def check_oom(state, now):
    since = state.get("ts") or now - 300
    out = run(["journalctl", "-k", "-q", "--no-pager", "-o", "cat", "--since", f"@{int(since)}"]).stdout
    hits = [l for l in out.splitlines() if "oom-kill" in l.lower() or "out of memory" in l.lower()]
    if hits:
        return {f"oom:{int(now)}": "OOM killer intervenuto: " + " | ".join(hits[-3:])}
    return {}


def check_services(conf):
    alerts = {}
    for unit in conf["SYSTEM_SERVICES"].split():
        status = run(["systemctl", "is-active", unit]).stdout.strip()
        if status != "active":
            alerts[f"svc:{unit}"] = f"servizio {unit} in stato {status or 'sconosciuto'}"
    for item in conf["USER_SERVICES"].split():
        user, unit = item.split(":", 1)
        status = run(["systemctl", "--user", "-M", f"{user}@", "is-active", unit]).stdout.strip()
        if status != "active":
            alerts[f"svc:{user}:{unit}"] = f"servizio utente {unit} di {user} in stato {status or 'sconosciuto'}"
    for url in conf["HTTP_URLS"].split():
        try:
            with urllib.request.urlopen(url, timeout=10) as resp:
                code = resp.status
        except urllib.error.HTTPError as exc:
            code = exc.code
        except (urllib.error.URLError, OSError) as exc:
            alerts[f"http:{url}"] = f"{url} non risponde: {exc}"
            continue
        if code >= 500:
            alerts[f"http:{url}"] = f"{url} risponde HTTP {code}"
    return alerts


def emit(text, priority, conf, dry_run):
    if dry_run:
        print(f"[{priority}] {text}")
        return
    run(["logger", "-t", "vm-health", "-p", f"daemon.{priority}", text])
    if conf["NOTIFY_CMD"] and priority == "warning":
        subprocess.run(conf["NOTIFY_CMD"], shell=True, input=text, text=True, check=False)


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--conf", default="/etc/vm-health/vm-health.conf")
    ap.add_argument("--state", default="/var/lib/vm-health/state.json")
    ap.add_argument("--dry-run", action="store_true", help="stampa invece di scrivere nel journal")
    args = ap.parse_args()

    conf = load_conf(args.conf)
    try:
        with open(args.state, encoding="utf-8") as fh:
            state = json.load(fh)
    except (OSError, ValueError):
        state = {}

    now = time.time()
    procs = read_procs()
    active = {}
    active.update(check_cpu(state, procs, now, conf))
    active.update(check_memory(conf))
    active.update(check_oom(state, now))
    active.update(check_services(conf))

    last_alert = state.get("alerts", {})
    realert = int(conf["REALERT_MIN"]) * 60
    new_alerts = {}
    for key, msg in active.items():
        sent = last_alert.get(key, 0)
        if now - sent >= realert:
            emit(f"ALLARME {HOST}: {msg}\n\nProcessi principali:\n{top_processes()}", "warning", conf, args.dry_run)
            sent = now
        new_alerts[key] = sent
    for key in last_alert:
        if key not in active and not key.startswith("oom:"):
            emit(f"RIENTRATO {HOST}: {key}", "notice", conf, args.dry_run)

    state = {"ts": now, "procs": procs, "alerts": new_alerts}
    if not args.dry_run:
        os.makedirs(os.path.dirname(args.state), exist_ok=True)
        tmp = args.state + ".tmp"
        with open(tmp, "w", encoding="utf-8") as fh:
            json.dump(state, fh)
        os.replace(tmp, args.state)
    elif not active:
        print("nessun allarme")
    return 0


if __name__ == "__main__":
    sys.exit(main())
