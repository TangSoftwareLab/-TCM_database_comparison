import pandas as pd
from process.mysql_setting.connections import query_mysql_pd, save_to_mysql_pd
import re
import numpy as np

# TODO: GET THE INCHIKEY BY CHEMID OR PUBCHEM ID

def prepare_ingre_target():
    def split_target_score(x):
        print(x)
        x = x.split('(')
        if len(x)==2:
            target = x[0].strip()
            score = x[1]
            score = score.replace(')', '').strip()
        else:
            target = x[0]
            score = '0'
        return ','.join([target, score])

    database_name = 'etcm'
    sql = """SELECT * FROM etcm.herb_ingredient_target;"""
    pd_result = query_mysql_pd(sql_string=sql, database_name=database_name)
    pd_result['Candidate Target genes'] = pd_result['Candidate Target genes'].apply(lambda x: split_target_score(x))
    pd_result_2 = pd_result.join(pd_result['Candidate Target genes'].str.split(',', expand=True)).rename(
       columns= {'0': 'target', '1': 'score'})
    save_to_mysql_pd(pd_result=pd_result_2, database_name='etcm', saved_name='herb_ingredient_target')

    # keep only ingredient_target
    ingre_target_pd = pd_result_2[['ingre_id', 'target']].drop_duplicates(keep='first')
    save_to_mysql_pd(pd_result=pd_result_2, database_name='etcm', saved_name='ingredient_target')
    return pd_result

def get_herb_info_etcm(herb_chinese_list):
    database_name = 'etcm'
    herb_list_str = ','.join(["'{}'".format(x) for x in set(herb_chinese_list)])
    sql = """SELECT * FROM herb_info as h
                where h.`Herb Name in Chinese` in ({});
               """.format(herb_list_str)
    pd_result = query_mysql_pd(sql_string=sql, database_name=database_name)

    return pd_result


def get_ingredient_info_etcm(ingredient_id_list):
    database_name = 'etcm'
    ingredient_id_str = ','.join(["'{}'".format(x) for x in set(ingredient_id_list)])
    sql = """SELECT * FROM 
                ingredient_info as m
                where m.Ingredient_id in ({});
                """.format(ingredient_id_str)
    pd_result = query_mysql_pd(sql_string=sql, database_name=database_name)

    return pd_result

def get_herb_ingredient_etcm(herb_chinese_list):
    database_name = 'etcm'
    herb_list_str = ','.join(["'{}'".format(x) for x in set(herb_chinese_list)])
    sql = """SELECT * FROM herb_info as h,
            herb_ingredient as h_m,
            ingredient_info as m
            where h.`Herb Name in Chinese` in ({})
            and h.herb_id = h_m.herb_id
            and h_m.ingre_id = m.Ingredient_id;
            """.format(herb_list_str)
    pd_result = query_mysql_pd(sql_string=sql, database_name=database_name)
    return pd_result


def get_ingre_tar_etcm(ingredient_id_list):
    database_name = 'etcm'
    ingredient_id_str = ','.join(["'{}'".format(x) for x in set(ingredient_id_list)])
    sql = """SELECT * FROM 
            ingredient_info as m,
            herb_ingredient_target as m_t
            where m_t.ingre_id in ({})
            and m_t.ingre_id = m.Ingredient_id
            ;""".format(ingredient_id_str)
    pd_result = query_mysql_pd(sql_string=sql, database_name=database_name)
    return pd_result


def get_herb_ingredient_tar_etcm(herb_chinese_list):
    database_name = 'etcm'
    herb_list_str = ','.join(["'{}'".format(x) for x in set(herb_chinese_list)])
    sql = """SELECT * FROM herb_info as h,
            herb_ingredient_target as h_m_t
            where h.`Herb Name in Chinese` in ({})
            and h.herb_id = h_m_t.herb_id;
            """.format(herb_list_str)
    pd_result_h_m_t = query_mysql_pd(sql_string=sql, database_name=database_name)

    # # amp ingre_id to ingredient info
    # ingre_id_list = list(pd_result_h_m_t['ingre_id'].unique())
    # pd_result_m_t = get_ingre_tar_etcm(ingre_id_list)
    return pd_result_h_m_t


def get_important_key():
    database_name = 'etcm'
    sql = """SELECT * FROM etcm.ingredient_info;"""
    pd_ingre_info_result = query_mysql_pd(sql_string=sql, database_name=database_name)
    pd_ingre_info_target_left = pd_ingre_info_result[pd_ingre_info_result['Candidate Target Genes'].notnull()]
    pd_ingre_info_struc_left = pd_ingre_info_result[pd_ingre_info_result['Molecular Formula'].notnull()]


def main():
    suhuang_sapsule = ['麻黄', '紫苏叶', '地龙', '枇杷叶', '紫苏子', '蝉蜕', '前胡', '牛蒡子', '五味子']
    # pd_result = get_herb_ingredient_etcm(suhuang_sapsule)
    pd_result_h_m_t = get_herb_ingredient_tar_etcm(suhuang_sapsule)
    pd_result_h_m_t.to_excel('result/case/suhuang_etcm_herb_ingre_target.xlsx')
    #pd_result_m_t.to_excel('result/case/suhuang_etcm_ingre_target.xlsx')


