import pandas as pd
import os
import pickle
import tqdm
from sqlalchemy import create_engine
import multiprocessing as mp
from process.mysql_setting.connections import query_mysql_pd, save_to_mysql_pd

def read_tcmid_files(path_selected):
    database_dict = {}
    for file in os.listdir(path_selected):
        name = file.split('.')[0]

        if name == 'prescription':
            data = pd.read_csv(path_selected + file, sep=':')
        elif name in ['herb_ingredient_pairs', 'ADMET prediction']:
            data = pd.read_csv(path_selected + file)
        else:
            data = pd.read_csv(path_selected + file, sep='\t')

        cols = [c for c in data.columns if not c.startswith('Unname')]
        data = data[cols]
        database_dict[name] = data

    return database_dict



def tcmid_save_to_mysql(path_selected):
    # open the mysql workbench, the panel of local host one
    engine = create_engine('mysql://root:Mqxs320321wyy@localhost/tcmid?charset=utf8mb4')
    conn = engine.connect()
    database_dict = read_tcmid_files(path_selected)
    for k, v in database_dict.items():
        try:
            v.to_sql(name=k, con=conn, if_exists='fail', index=False)
        except:
            continue


def prepare_herb_ingre():
    database_name = 'tcmid'
    sql_herb = """SELECT * FROM herb_info_detail as h_detail,
                herb_info as h
                where h.`Latin Name`= h_detail.`Latin Name`
                ;"""

    sql_ingre = """SELECT * FROM 
                    stitch_annotation as m,
                    admet_prediction as m_ad
                    where m.SMILES = m_ad.smiles
                    ;"""

    sql_herb_ingre = """SELECT * FROM herb_new as h,
                        ingre_new as m,
                        herb_ingredient_pairs as h_m
                        where h_m.herb_id = h.`herb-id`
                        and h_m.Ingredients_id = m.`Ingredient id`
                        ;"""

    pd_result_herb = query_mysql_pd(sql_string=sql_herb, database_name=database_name)
    save_to_mysql_pd(pd_result=pd_result_herb,
                     database_name=database_name,
                     saved_name='herb_new')

    pd_result_ingre = query_mysql_pd(sql_string=sql_ingre, database_name=database_name)
    pd_result_ingre = pd_result_ingre.rename(columns={'smiles':'tcmid_smiles'})
    save_to_mysql_pd(pd_result=pd_result_ingre,
                     database_name=database_name,
                     saved_name='ingre_new')

    pd_result_herb_ingre = query_mysql_pd(sql_string=sql_herb_ingre, database_name=database_name)
    save_to_mysql_pd(pd_result=pd_result_herb_ingre,
                     database_name=database_name,
                     saved_name='herb_ingre_new')


def main():
    database_selected = 'tcmid'
    path_selected = 'original_data/{}/'.format(database_selected)
    database_dict = read_tcmid_files(path_selected)
    tcmid_save_to_mysql(path_selected)


