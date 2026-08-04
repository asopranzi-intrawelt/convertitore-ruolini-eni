from flask import Flask, jsonify, request, send_file
import os
from flask_cors import CORS
from odoo_handler.models import sale_order, account_invoice
import openpyxl
from io import BytesIO
import logging

# creating the Flask application
app = Flask(__name__, static_folder=None)
CORS(app)

# setting up logging
logging.basicConfig(filename='app.log', level=logging.DEBUG)

@app.route('/get-login', methods=['GET'])
def get_login():
    return {'login': 'OK', 'token': ''}


@app.route('/trex/orders')
def get_orders():
    param_search = [[['partner_id', '=', 7952], ['state', '=', 'sale'], ['invoice_status', '=', 'no']]]
    orders = sale_order.SaleOrder().get_list(param_search)
    # serializing as JSON
    return jsonify(orders)


@app.route('/trex/order_count', methods=['POST'])
def get_orders_count():
    data = request.json
    state = data.get("state")
    invoice_status = data.get("invoice_status")
    param_search = [[['partner_id', '=', 7952], ['state', '=', state], ['invoice_status', '=', invoice_status]]]
    orders = sale_order.SaleOrder().get_count(param_search)
    # serializing as JSON
    return jsonify(orders)


@app.route('/trex/invoices')
def get_invoices():
    param_search = [[['partner_id', '=', 7952], ['state', 'in', ['open']]]]
    orders = account_invoice.AccountInvoice().get_list(param_search)
    # serializing as JSON
    return jsonify(orders)


@app.route('/trex/invoice_count', methods=['POST'])
def get_invoices_count():
    data = request.json
    state = data.get("state")
    param_search = [[['partner_id', '=', 7952], ['state', '=', state]]]
    orders = account_invoice.AccountInvoice().get_count(param_search)
    # serializing as JSON
    return jsonify(orders)


# A dictionary to store files in memory
files = {}


@app.route('/upload', methods=['POST'])
def upload_file():
    filename = request.files['file'].filename
    file_to_read = request.files['file'].read()
    file_as_bytes = BytesIO(file_to_read)
    workbook = openpyxl.load_workbook(file_as_bytes, data_only=False)
    worksheet = workbook.active
    start_row = 1  # Your desired start row here
    data = []
    for row in worksheet.iter_rows(min_row=start_row, values_only=True):
        data.append([cell for cell in row])
    # Store file in files dictionary
    files[filename] = workbook
    return jsonify(data)


# ---- Conversione ruolino: la logica scrive in posizione sul foglio 'Fattura' i
# valori letti da Odoo, lasciando intatte formule e struttura del sorgente. Le
# colonne sono 1-based e riferite al layout del ruolino Eni. ----
COL_PAGINE = 16          # N° PAGINE
COL_ASSEVERAZIONE = 19   # ASSEVERAZIONE PRIMA COPIA
COL_LEGALIZZAZIONE = 20  # LEGALIZZAZIONE (BOLLI): legalizzazione + apostille
COL_BOLLO = 22           # importo imposta di bollo
COL_NOTE_FORNITORE = 30  # nota "{qty} marche da bollo[ / tariffa maggiorata per urgenza]"
COL_URGENZA = 23         # colonna flag '!': se valorizzata nel sorgente, la riga e' urgente.
                         # NON la col29 (importo sovrapprezzo, sempre 0 nei dati reali): il
                         # segnale operativo di urgenza e' un '!' messo a mano in questa colonna.

# Nomi delle righe d'ordine Odoo, in italiano e inglese
LINEE_TRADUZIONE = ('Traduzione', 'Translation')
LINEE_ASSEVERAZIONE = ('Asseverazione', 'Certification')
LINEE_LEGALIZZAZIONE = ('Legalizzazione', 'Legalization')
LINEE_APOSTILLE = ('Apostille - visto Aja', 'Apostille')
LINEE_BOLLO = ('Imposta di bollo 16 euro\n ', '16 Euro Stamp Duty')


def _valore_riga(order_lines, nomi, campo, default=0):
    """Primo valore di `campo` fra le righe d'ordine il cui nome e' in `nomi`."""
    return next((riga[campo] for riga in order_lines if riga.get('name') in nomi), default)


def _num(v):
    """Valore numerico di una cella, 0 se vuota o non numerica."""
    try:
        return float(v)
    except (TypeError, ValueError):
        return 0.0


def totale_riepilogo(sheet, r):
    """Ricostruisce il totale imponibile della riga `r` replicando la formula del
    template (colonna TOTALE): tariffa per pagine, piu impaginazione, asseverazione,
    legalizzazione, asseverazione copie successive, bollo, rit/cons fuori orario,
    timbro bilingue, ore interprete e urgenza. Serve perche' nel file e' una formula
    non valutata, quindi va calcolata per confrontarla con T-Rex."""
    g = lambda c: _num(sheet.cell(row=r, column=c).value)
    return (g(15) * g(16) + g(18) + g(19) + g(20) + g(21) + g(22)
            + g(24) + g(25) + g(26) * g(27) + g(29))


def valori_odoo(protocollo):
    """Valori Odoo per un protocollo, o None se l'ordine non esiste.

    Un errore di connessione o autenticazione viene rilanciato come errore chiaro
    invece di essere inghiottito; un ordine semplicemente non trovato fa restituire
    None, e in quel caso la riga resta invariata.
    """
    try:
        orders = sale_order.SaleOrder().get_list([[['service_request_customer_id', '=', protocollo]]])
    except Exception as e:
        app.logger.error("Errore Odoo sul protocollo %r: %s", protocollo, e)
        raise RuntimeError(
            "Conversione interrotta: errore nella connessione o nella query Odoo "
            "per il protocollo {}: {}".format(protocollo, e)) from e
    if not orders:
        return None
    lines = orders[0].get('order_line', []) or []
    bollo_qty = _valore_riga(lines, LINEE_BOLLO, 'product_uom_qty', 0)
    valori = {
        COL_PAGINE: _valore_riga(lines, LINEE_TRADUZIONE, 'product_uom_qty', 0),
        COL_ASSEVERAZIONE: _valore_riga(lines, LINEE_ASSEVERAZIONE, 'price_subtotal', 0),
        COL_LEGALIZZAZIONE: (_valore_riga(lines, LINEE_LEGALIZZAZIONE, 'price_subtotal', 0)
                             + _valore_riga(lines, LINEE_APOSTILLE, 'price_subtotal', 0)),
        COL_BOLLO: _valore_riga(lines, LINEE_BOLLO, 'price_subtotal', 0),
        COL_NOTE_FORNITORE: "{} marche da bollo".format(bollo_qty),
    }
    # amount_untaxed = totale imponibile dell'SO su T-Rex, per il check del totale
    return valori, _num(orders[0].get('amount_untaxed', 0))


@app.route('/save', methods=['POST'])
def save_file():
    data = request.get_json()
    filename = data['filename']
    workbook = files[filename]
    sheet = workbook.active  # foglio 'Fattura' del ruolino

    # individua la riga di intestazione
    header_row = None
    for r in range(1, sheet.max_row + 1):
        if sheet.cell(row=r, column=1).value == 'PROTOCOLLO E PROGRESSIVO':
            header_row = r
            break
    if header_row is None:
        return "Intestazione 'PROTOCOLLO E PROGRESSIVO' non trovata nel foglio", 400

    colonne = (COL_PAGINE, COL_ASSEVERAZIONE, COL_LEGALIZZAZIONE, COL_BOLLO, COL_NOTE_FORNITORE)
    intestazioni = {c: sheet.cell(row=header_row, column=c).value for c in colonne}
    modifiche = []      # registro prima/dopo di cio' che il convertitore ha scritto
    check_totale = []   # (protocollo, totale del riepilogo, totale su T-Rex)

    for r in range(header_row + 1, sheet.max_row + 1):
        protocollo = sheet.cell(row=r, column=1).value
        if isinstance(protocollo, str) and protocollo.strip().upper() == 'TOTALE':
            break
        if protocollo in (None, ''):
            continue
        risultato = valori_odoo(protocollo)
        if risultato is None:
            modifiche.append((protocollo, '', 'ORDINE NON TROVATO SU ODOO', '', ''))
            continue
        valori, totale_trex = risultato
        urgente = sheet.cell(row=r, column=COL_URGENZA).value not in (None, '', 0)
        for col in colonne:
            cella = sheet.cell(row=r, column=col)
            dopo = valori[col]
            # la nota fornitore prende la coda di urgenza dalla colonna URGENZA del sorgente
            if col == COL_NOTE_FORNITORE and urgente:
                dopo = dopo + " / tariffa maggiorata per urgenza"
            prima = cella.value
            if prima != dopo:
                cella.value = dopo
                modifiche.append((protocollo, col, intestazioni.get(col), prima, dopo))
        # il totale del riepilogo si calcola DOPO il riempimento, poi si confronta con T-Rex
        check_totale.append((protocollo, totale_riepilogo(sheet, r), totale_trex))

    # foglio di controllo: prima il check del totale imponibile vs T-Rex con esito,
    # poi il registro di cosa il convertitore ha scritto. Transito e urgenza non sono
    # qui perche' T-Rex non offre un riscontro affidabile: restano controllo a vista.
    if 'Controllo IW' in workbook.sheetnames:
        del workbook['Controllo IW']
    controllo = workbook.create_sheet(title='Controllo IW')
    controllo.append(['CHECK TOTALE IMPONIBILE  (riepilogo vs T-Rex)'])
    controllo.append(['PROTOCOLLO', 'TOTALE RIEPILOGO', 'TOTALE T-REX', 'ESITO'])
    for (p, tot_riep, tot_trex) in check_totale:
        esito = 'OK' if abs(tot_riep - tot_trex) < 0.01 else 'INCONGRUENZA'
        controllo.append([p, round(tot_riep, 2), round(tot_trex, 2), esito])
    controllo.append([])
    controllo.append(['REGISTRO MODIFICHE  (cosa ha scritto il convertitore)'])
    controllo.append(['PROTOCOLLO', 'COLONNA', 'VOCE', 'VALORE PRIMA', 'VALORE DOPO'])
    for riga in modifiche:
        controllo.append(list(riga))

    # salva con il nome '<sorgente>_IW.xlsx'
    base, ext = os.path.splitext(filename)
    iwname = base + '_IW' + ext
    workbook.save(iwname)

    # restituisce le righe del foglio Fattura per la tabella del frontend
    righe = [[c for c in row] for row in sheet.iter_rows(values_only=True)]
    return jsonify(righe)


@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    # Serve sempre la versione convertita '<sorgente>_IW.xlsx', con quel nome.
    base, ext = os.path.splitext(filename)
    iwname = filename if base.endswith('_IW') else base + '_IW' + ext
    if not os.path.isfile(iwname):
        return "File not found", 404
    return send_file(iwname, as_attachment=True, download_name=os.path.basename(iwname))


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000)
