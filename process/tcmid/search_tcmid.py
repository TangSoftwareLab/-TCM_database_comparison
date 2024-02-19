import pandas as pd
from process.mysql_setting.connections import query_mysql_pd, save_to_mysql_pd


def get_herb_info_tcmid(herb_chinese_list):
    database_name = 'tcmid'
    herb_list_str = ','.join(["'{}'".format(x) for x in set(herb_chinese_list)])
    sql = """SELECT * FROM herb_new as h
                where h.`Chinese Name` in ({});
               """.format(herb_list_str)
    pd_result = query_mysql_pd(sql_string=sql, database_name=database_name)

    return pd_result


def get_herb_ingredient_tcmid(herb_list):
    database_name = 'tcmid'
    herb_list_str = ','.join(["'{}'".format(x) for x in set(herb_list)])
    sql = """SELECT * FROM herb_ingre_new as h_m
            where h_m.`Chinese Name` in ({})
            ;
            """.format(herb_list_str)
    pd_result = query_mysql_pd(sql_string=sql, database_name=database_name)
    return pd_result


def get_ingre_tar_tcmid_stitch(ingredient_id_list):
    database_name = 'tcmid'
    ingredient_id_str = ','.join(["'{}'".format(x) for x in set(ingredient_id_list)])
    sql = """SELECT * FROM ingre_new as m,
                stitch_interaction_all as m_t
                where m.`Ingredient id` = ({})
                and m.Stitch_cid_m = m_t.stitch_id;""".format(ingredient_id_str)
    pd_result = query_mysql_pd(sql_string=sql, database_name=database_name)
    return pd_result


def get_ingre_tar_tcmid(ingredient_id_list):
    database_name = 'tcmid'
    ingredient_id_str = ','.join(["'{}'".format(x) for x in set(ingredient_id_list)])
    sql = """SELECT * FROM ingre_new as m,
                    ingredient_targets_disease_drug as m_t
                    where m.`Ingredient id` = ({})
                    and m.`Ingredient id` = m_t.`Ingredient id`;""".format(ingredient_id_str)
    pd_result = query_mysql_pd(sql_string=sql, database_name=database_name)

    return pd_result

def get_herb_info():
    database_name = 'tcmid'
    sql = """SELECT * FROM herb_info
                """
    pd_result = query_mysql_pd(sql_string=sql, database_name=database_name)

    return pd_result

def main():
    suhuang_sapsule = ['麻黄', '紫苏叶', '地龙', '枇杷叶', '紫苏子', '蝉蜕', '前胡', '牛蒡子', '五味子']
    pd_result_h = get_herb_ingredient_tcmid(suhuang_sapsule)
    pd_result_h.to_excel('result/case/suhuang_tcmid_pd.xlsx')