import os
import xmlrpc.client
from json import dumps

from utility import util
from odoo_handler.convert_base64 import check_file_type_and_convert
from odoo_handler.convert_base64 import dispath_base64_type


url = "https://intraweltsh-test.openforce.it"
db = "intrawelt-12-0-test-7389154"
username = 'gmandolesi@intrawelt.com'
password = 'IW-2021*'
uid = ""
info = ""


def inizializza_odoo_rpc():
    global uid, info
    info = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
    uid = info.authenticate(db, username, password, {})


def get_freelance_list(search, limit):
    global uid
    if not uid:
        inizializza_odoo_rpc()
    models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))
    freelances = models.execute_kw(db, uid, password, 'res.partner', 'search',
                                   [search],
                                   {'limit': limit})
    freelances_anagrafica = []
    for freelance in freelances:
        [record] = models.execute_kw(db, uid, password,
                                     'res.partner', 'read', [freelance])

        display_name = record['display_name']
        stato = record['stage_id'][1] if record.get('stage_id') else ""
        cv_base64 = record['curriculum_file']
        name_file = dispath_base64_type(cv_base64, display_name)
        cv_expiration_date = record['cv_expiration_date']
        email = record['email']
        supplierinfo_group_ids = record['supplierinfo_group_ids']
        listino_prezzi = get_price_group_list(supplierinfo_group_ids)
        listino_prezzi_txt = create_listino_testuale(listino_prezzi)
        json_price_list = dumps(listino_prezzi)

        freelances_anagrafica.append({
            'Nome e cognome/ragione sociale': display_name,
            'Stato del freelance': stato,
            'Curriculum': name_file,
            'Curriculum testo': check_file_type_and_convert(name_file, display_name).encode('utf-8'),
            'data scadenza Curriculum': cv_expiration_date,
            'email': email,
            'Listino prezzi': json_price_list,
            'Listino prezzi testuale': listino_prezzi_txt,
        })
    return freelances_anagrafica


def get_price_list(supplierinfo_ids, type_list="reduced"):
    global uid
    if not uid:
        inizializza_odoo_rpc()
    if supplierinfo_ids:
        models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))
    listino_prezzi = []
    for id_prod_suppinfo in supplierinfo_ids:
        [listino_item] = models.execute_kw(db, uid, password,
                                           'product.supplierinfo', 'read', [id_prod_suppinfo])

        if type_list == 'all':
            listino_prezzi.append({
                'servizio': listino_item.get('product_tmpl_id')[1] if listino_item.get('product_tmpl_id') else "",
                'capacità giornaliera': listino_item.get('daily_words_capacity'),
                'source language': listino_item.get('lang_from_id')[1] if listino_item.get('lang_from_id') else "",
                'target language': listino_item.get('lang_to_id')[1] if listino_item.get('lang_to_id') else "",
                'Category language': listino_item.get('lang_category_id')[1] if listino_item.get(
                    'lang_category_id') else "",
                'unità di misura (uom)': listino_item.get('freelance_uom_id')[1] if listino_item.get(
                    'freelance_uom_id') else "",
                'parametro di conteggio': listino_item.get('lang_uom_id')[1] if listino_item.get('lang_uom_id') else "",
                'Listino prezzi ragguppato': listino_item.get('supplier_group_id'),
            })
        else:
            listino_prezzi.append({
                'prezzo': listino_item.get('price'),
                'unità di misura (uom)': listino_item.get('freelance_uom_id')[1] if listino_item.get(
                    'freelance_uom_id') else "",
                'parametro di conteggio': listino_item.get('lang_uom_id')[1] if listino_item.get('lang_uom_id') else "",
                'capacità giornaliera': listino_item.get('daily_words_capacity'),
            })

    return listino_prezzi


def get_price_group_list(supplierinfo_ids):
    global uid
    if not uid:
        inizializza_odoo_rpc()
    if supplierinfo_ids:
        models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))
    listino_prezzi = []
    for id_prod_suppinfo in supplierinfo_ids:
        [listino_item] = models.execute_kw(db, uid, password,
                                           'product.supplierinfo.group', 'read', [id_prod_suppinfo])

        prezzi = get_price_list(listino_item['supplierinfo_ids'])

        listino_prezzi.append({
            'servizio': listino_item.get('product_tmpl_id')[1] if listino_item.get('product_tmpl_id') else "",
            'source language': listino_item.get('lang_from_id')[1] if listino_item.get('lang_from_id') else "",
            'target language': listino_item.get('lang_to_id')[1] if listino_item.get('lang_to_id') else "",
            'category language': listino_item.get('lang_category_id')[1] if listino_item.get(
                'lang_category_id') else "",
            'listino prezzi': prezzi
        })

    return listino_prezzi


def create_listino_testuale(listino_prezzi):
    testo_listino = ""
    for prezzo_group in listino_prezzi:
        testo_listino += prezzo_group['servizio'].replace("\n", " ")+" "
        testo_listino += prezzo_group['source language'] + " a " + prezzo_group['target language']
        testo_listino += " " + prezzo_group['category language']
        for prezzo in prezzo_group.get("listino prezzi"):
            testo_listino += ", " + str(prezzo['prezzo'])
            testo_listino += " per " + prezzo['unità di misura (uom)']
            testo_listino += " " + prezzo['parametro di conteggio']
        testo_listino += ". \n"
    return testo_listino

def get_order_list(search, limit):
    global uid
    if not uid:
        inizializza_odoo_rpc()
    models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))
    freelances = models.execute_kw(db, uid, password, 'res.partner', 'search',
                                   [search],
                                   {'limit': limit})
    freelances_anagrafica = []
    for freelance in freelances:
        [record] = models.execute_kw(db, uid, password,
                                     'res.partner', 'read', [freelance])

        display_name = record['display_name']
        stato = record['stage_id'][1] if record.get('stage_id') else ""
        cv_base64 = record['curriculum_file']
        name_file = dispath_base64_type(cv_base64, display_name)
        cv_expiration_date = record['cv_expiration_date']
        email = record['email']
        supplierinfo_group_ids = record['supplierinfo_group_ids']
        listino_prezzi = get_price_group_list(supplierinfo_group_ids)
        listino_prezzi_txt = create_listino_testuale(listino_prezzi)
        json_price_list = dumps(listino_prezzi)

        freelances_anagrafica.append({
            'Nome e cognome/ragione sociale': display_name,
            'Stato del freelance': stato,
            'Curriculum': name_file,
            'Curriculum testo': check_file_type_and_convert(name_file, display_name).encode('utf-8'),
            'data scadenza Curriculum': cv_expiration_date,
            'email': email,
            'Listino prezzi': json_price_list,
            'Listino prezzi testuale': listino_prezzi_txt,
        })
    return freelances_anagrafica


def open_file(filepath):
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as infile:
        return infile.read()


def save_file(filepath, content):
    with open(filepath, 'w', encoding='utf-8') as outfile:
        outfile.write(content)


def format_cv_txt(inputdir, outdir):
    utility_function = util.Util()
    for file_name in os.listdir(inputdir):
        if file_name.endswith(".txt"):
            testual_cv = open_file(os.path.join(inputdir, file_name))
            cv_formatted = utility_function.remove_newlines_txt(testual_cv.strip())
            print(cv_formatted)
            save_file(outdir+"/"+file_name, cv_formatted)
            print(cv_formatted)

# legge i file txt e cerca di riformattarli
#format_cv_txt('../CV/txt/reformat', '../CV/txt/txt_formatted')


#converted = get_freelance_list([
#     ["name", "in", ["Aljosa Marinkovic", "Andra Hazaparu", "Aoife Marie Fitzgerald"]]], 40)

#converted = get_freelance_list([
#    ['stage_id', 'ilike', 'VERIFICATO'],
#    ['supplier', '=', True],
#    ['parent_id', '=', False],
#    ['translator', '=', True],
#    ["purchase_order_count", ">", 0]], 40)


#export_to_csv(converted)


