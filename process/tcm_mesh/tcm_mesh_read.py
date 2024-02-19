import pandas as pd
from sqlalchemy import create_engine
import pandas as pd
import io
import requests
import os
from process.mysql_setting.connections import query_mysql_pd, save_to_mysql_pd


def download_data():
    down_load_links_1 = {
        'gene_disease_associations': 'http://mesh.tcm.microbioinformatics.org/download/gene-disease%20associations.txt',
        'herb_info': 'http://mesh.tcm.microbioinformatics.org/download/herb-info.txt',
        'herb_ingredients': 'http://mesh.tcm.microbioinformatics.org/download/herb-ingredients.txt',
        'protein_gene_links': 'http://mesh.tcm.microbioinformatics.org/download/protein-gene%20links.txt',
        'side_effect': 'http://mesh.tcm.microbioinformatics.org/download/side%20effect.txt',
        'toxicity': 'http://mesh.tcm.microbioinformatics.org/download/toxicity.txt'}

    down_load_links_2 = {
        'chemical_protein_associations': 'http://mesh.tcm.microbioinformatics.org/download/gene%20interactions.txt',
        'gene_interactions': 'http://mesh.tcm.microbioinformatics.org/download/chemical-protein%20associations.txt'}

    for info_name, site in down_load_links_1.items():
        data = pd.read_csv(site, sep='\t')
        data.to_csv('original_data/tcm_mesh/{}.txt'.format(info_name), sep='\t')

    for info_name, site in down_load_links_2.items():
        print(info_name)
        s = requests.get(site).content
        data = pd.read_csv(io.StringIO(s.decode('utf-8')), sep='\t')
        data.to_csv('original_data/tcm_mesh/{}.txt'.format(info_name), sep='\t')

# read files from local folder
def read_tcm_sh_files(path_selected):
    database_dict = {}
    for file in os.listdir(path_selected):
        name = file.split('.')[0]
        if name != 'side_effect':
            data = pd.read_csv(path_selected + file, sep='\t', index_col=0)
        else:
            data = pd.read_csv(path_selected + file, sep=',', index_col=0)
        database_dict[name] = data
    return database_dict



def tcm_mesh_save_to_mysql(path_selected):
    # open the mysql workbench, the panel of local host one
    engine = create_engine('mysql://root:Mqxs320321wyy@localhost/tcm_mesh?charset=utf8mb4')
    conn = engine.connect()
    database_dict = read_tcm_sh_files(path_selected)
    for k,v in database_dict.items():
        try:
            v.to_sql(name=k, con=conn, if_exists='fail', index=False)
        except:
            continue


def simply_herb_ingre_target():
    database_name = 'tcm_mesh'
    sql_ingre_target = """SELECT * FROM chemical_protein_associations
                    ;"""

    sql_ingre = """SELECT * FROM 
                        compounds
                        ;"""

    sql_herb_ingre = """SELECT * FROM herb_ingredients
                            ;"""

    pd_result_herb_ingre = query_mysql_pd(sql_string=sql_herb_ingre, database_name=database_name)
    pd_result_ingre_target = query_mysql_pd(sql_string=sql_ingre_target, database_name=database_name)
    tcm_ingre = list(pd_result_herb_ingre['chemical'].unique())
    pd_result_ingre_target_tcm = pd_result_ingre_target[pd_result_ingre_target['chemical'].isin(tcm_ingre)]
    save_to_mysql_pd(pd_result=pd_result_ingre_target_tcm,
                     database_name=database_name,
                     saved_name='tcm_chemical_protein_associations')

    pd_result_ingre = query_mysql_pd(sql_string=sql_ingre, database_name=database_name)

    pd_result_ingre_tcm = pd_result_ingre[pd_result_ingre['chemical'].isin(tcm_ingre)]
    save_to_mysql_pd(pd_result=pd_result_ingre_tcm,
                     database_name=database_name,
                     saved_name='tcm_compounds')


def add_simple_cid():
    database_name = 'tcm_mesh'

    def remove_pre(x):
        string_term = list(x[3:])
        for i, s in enumerate(string_term):
            if s == '0':
                continue
            else:
                break
        cid = int(x[3+i:])
        return cid

    table_list = ['tcm_chemical_protein_associations', 'tcm_compounds', 'herb_ingredients']
    for t in table_list:
        sql_term = """SELECT * FROM {}
                            ;""".format(t)

        pd_result = query_mysql_pd(sql_string=sql_term, database_name=database_name)

        pd_result['pubchem_id'] = pd_result['chemical'].apply(remove_pre)

        save_to_mysql_pd(pd_result=pd_result,
                         database_name=database_name,
                         saved_name=t+'_cid')

def add_chinese_name():
    database_name_1 = 'tcm_mesh'
    sql_mesh_term = """SELECT * FROM herb_info
                                ;"""
    pd_mesh_result = query_mysql_pd(sql_string=sql_mesh_term, database_name=database_name_1)

    # use herb database
    database_name_herb = 'tcm_herb'
    sql_term_herb = """SELECT * FROM herb_herb_info
                                    ;"""

    pd_herb_result = query_mysql_pd(sql_string=sql_term_herb, database_name=database_name_herb)
    pd_herb_result = pd_herb_result[pd_herb_result['Herb_pinyin_name'] != None]
    herb_pinyin_chin_dict = dict(zip(pd_herb_result['Herb_pinyin_name'], pd_herb_result['Herb_cn_name']))

    # dictiobary from tcmid
    database_name_tcmid = 'tcmid'
    sql_term_tcmid = """SELECT * FROM herb_info
                                        ;"""
    pd_tcmid_result = query_mysql_pd(sql_string=sql_term_tcmid, database_name=database_name_tcmid)
    pd_tcmid_result =pd_tcmid_result[pd_tcmid_result['Pinyin Name'] != None]
    tcmid_pinyin_chin_dict = dict(zip(pd_tcmid_result['Pinyin Name'], pd_tcmid_result['Chinese Name']))

    herb_pinyin_chin_dict.update(tcmid_pinyin_chin_dict)

    # map
    def map_yinyin_chinese(x, herb_pinyin_chin_dict,  tcmid_pinyin_chin_dict):

        if x != None:
            y = herb_pinyin_chin_dict.get(x)
        else:
            y = None
        return y


    pd_mesh_result['chinese name_processed'] = pd_mesh_result['pinyin name'].apply(lambda x:map_yinyin_chinese(x,
                                                                                                    herb_pinyin_chin_dict,
                                                                                                    tcmid_pinyin_chin_dict))
    save_to_mysql_pd(pd_mesh_result, database_name=database_name_1, saved_name='herb_info')


def main():
    # download_data()
    # database_selected = 'tcm_mesh'
    # path_selected = 'original_data/{}/'.format(database_selected)
    # tcm_mesh_save_to_mysql(path_selected)
    add_simple_cid()
