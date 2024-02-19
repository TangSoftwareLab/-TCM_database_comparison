
import pandas as pd
import os
from process.mysql_setting.connections import query_mysql_pd, save_to_mysql_pd

def read_tcmio_files(path_selected):
    for file in os.listdir(path_selected):
        name = file.split('.')[0]
        data = pd.read_excel(path_selected + file, sheet_name=0)
        save_to_mysql_pd(data, 'tcmio', name)

def main():
    path_selected = 'original_data/TCMIO/'
    read_tcmio_files(path_selected)