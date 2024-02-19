import pandas as pd
from process.mysql_setting.connections import query_mysql_pd, save_to_mysql_pd


def get_herb_info_tcmio(herb_chinese_list):
    database_name = 'tcmio'
    herb_list_str = ','.join(["'{}'".format(x) for x in set(herb_chinese_list)])
    sql = """SELECT * FROM tcm as h
                where h.chinese_name in ({});
               """.format(herb_list_str)
    pd_result = query_mysql_pd(sql_string=sql, database_name=database_name)

    return pd_result

def get_ingredient_info_tcmio(ingredient_id_list):
    database_name = 'tcmio'
    ingredient_id_str = ','.join(["'{}'".format(x) for x in set(ingredient_id_list)])
    sql = """SELECT * FROM 
                ingredient as m
                where m.id in ({});
                """.format(ingredient_id_str)
    pd_result = query_mysql_pd(sql_string=sql, database_name=database_name)
    return pd_result


def get_herb_ingredient_tcmio(herb_list):
    database_name = 'tcmio'
    herb_list_str = ','.join(["'{}'".format(x) for x in set(herb_list)])
    sql = """SELECT * FROM tcm as h,
            ingredient as m,
            tcm_ingredient_relation as h_m
            where h.chinese_name in ({})
            and h.id = h_m.tcm_id
            and h_m.ingredient_id = m.id
            ;
            """.format(herb_list_str)
    pd_result = query_mysql_pd(sql_string=sql, database_name=database_name)
    return pd_result


def get_ingre_tar_tcmio(ingredient_id_list):
    database_name = 'tcmio'
    ingredient_id_str = ','.join(["'{}'".format(x) for x in set(ingredient_id_list)])
    sql = """SELECT * FROM 
            ingredient as m,
            ingredient_target_relation as m_t,
            target as t
            where m.ingredient_id in ({})
            and m.id = m_t.ingredient_id
            and m_t.target_id = t.target_id
            ;""".format(ingredient_id_str)
    pd_result = query_mysql_pd(sql_string=sql, database_name=database_name)
    return pd_result


def get_herb_ingredient_tar_etcm(herb_chinese_list):
    database_name = 'tcmio'
    pd_result_h_m = get_herb_ingredient_tcmio(herb_chinese_list)
    ingredient_id_list = list(pd_result_h_m['ingredient_id'].unique())
    pd_result_m_t = get_ingre_tar_tcmio(ingredient_id_list)
    return pd_result_h_m, pd_result_m_t


def main():
    suhuang_sapsule = ['麻黄', '紫苏叶', '地龙', '枇杷叶', '紫苏子', '蝉蜕', '前胡', '牛蒡子', '五味子']
    pd_result_h = get_herb_ingredient_tcmio(suhuang_sapsule)
    pd_result_h.to_excel('result/case/suhuang_tcmio_pd.xlsx')