import os

import pandas as pd
import json
from pandas import json_normalize


path = "../CV/"


def export_to_csv(data):
    columns = ['Nome e cognome/ragione sociale',
               'Stato del freelance',
               'Curriculum',
               'Curriculum testo',
               'data scadenza Curriculum',
               'email',
               'Listino prezzi',
               'Listino prezzi testuale']
    # Use json_normalize() to convert JSON to DataFrame
    df = pd.DataFrame(data)
    df.to_csv(path+'freelance_data.csv', sep=';', columns=columns)
    return path+'freelance_data.csv'


def update_testuale(file_csv, path):
    df = pd.read_csv(file_csv, sep=';', index_col=0)

    for index, row in df.iterrows():
        filename = path + row['Nome e cognome/ragione sociale'] + '.txt'
        if not os.path.exists(filename):
            continue
        with open(filename, 'r', encoding='utf-8', errors='ignore') as infile:
            content = infile.read()
            df.loc[index, 'Curriculum testo'] = content.encode('utf-8')
            infile.close()
    df.to_csv(file_csv, sep=';')


def convert_dict_data_to_df(data):
    dict = json.loads(data)
    df = json_normalize(dict)
    return df

#update_testuale("../CV/freelance_data.csv", "../CV/txt/summaries/")
