import pandas as pd
from process.mysql_setting.connections import query_mysql_pd, save_to_mysql_pd


def get_herb_info_mesh(herb_chinese_list):
    database_name = 'tcm_mesh'
    herb_list_str = ','.join(["'{}'".format(x) for x in set(herb_chinese_list)])
    sql = """SELECT * FROM herb_info as h
                where h.`chinese name_processed` in ({});
               """.format(herb_list_str)
    pd_result = query_mysql_pd(sql_string=sql, database_name=database_name)

    return pd_result

def get_ingredient_info_tcmio(ingredient_id_list):
    database_name = 'tcm_mesh'
    ingredient_id_str = ','.join(["'{}'".format(x) for x in set(ingredient_id_list)])
    sql = """SELECT * FROM 
                tcm_compounds as m
                where m.chemical in ({});
                """.format(ingredient_id_str)
    pd_result = query_mysql_pd(sql_string=sql, database_name=database_name)
    return pd_result


def get_herb_ingredient_mesh(herb_chinese_list):
    database_name = 'tcm_mesh'
    herb_list_str = ','.join(["'{}'".format(x) for x in set(herb_chinese_list)])
    sql = """SELECT * FROM all_herb_ingre_detail as h
            where h.`chinese name_processed` in ({})
            ;
            """.format(herb_list_str)
    pd_result = query_mysql_pd(sql_string=sql, database_name=database_name)

    return pd_result


def get_ingre_tar_mesh(ingredient_id_list):
    database_name = 'tcm_mesh'
    ingredient_id_str = ','.join(["'{}'".format(x) for x in set(ingredient_id_list)])
    sql = """SELECT * FROM 
            tcm_chemical_protein_associations as m_t,
            where m_t.chemical in ({})
            ;""".format(ingredient_id_str)
    pd_result = query_mysql_pd(sql_string=sql, database_name=database_name)

    return pd_result


def get_herb_ingredient_tar_mesh(herb_chinese_list):
    pd_result_h_m = get_herb_ingredient_mesh(herb_chinese_list)
    ingredient_id_list = list(pd_result_h_m['chemical'].unique())
    pd_result_m_t = get_ingre_tar_mesh(ingredient_id_list)
    return pd_result_h_m, pd_result_m_t


def get_side_toxi_effect(ingredient_id_list):
    database_name = 'tcm_mesh'
    ingredient_id_str = ','.join(["'{}'".format(x) for x in set(ingredient_id_list)])
    sql = """SELECT * FROM 
            side_effect as side
            where side.chemical in ({});""".format(ingredient_id_str)

    pd_result_side = query_mysql_pd(sql_string=sql, database_name=database_name)

    return pd_result_side


def get_toxicity(name_list):
    database_name = 'tcm_mesh'
    name_list_str = ','.join(["'{}'".format(x) for x in set(name_list)])
    sql_toxi = """SELECT * FROM 
                    tcm_mesh.toxicity as toxi
                    where toxi.name in ({});""".format(name_list_str)

    pd_result_toxi = query_mysql_pd(sql_string=sql_toxi, database_name=database_name)

    return pd_result_toxi

def main():
    suhuang_sapsule = ['麻黄', '紫苏叶', '地龙', '枇杷叶', '紫苏子', '蝉蜕', '前胡', '牛蒡子', '五味子']
    pd_result_h = get_herb_ingredient_mesh(suhuang_sapsule)
    pd_result_h.to_excel('result/case/suhuang_mesh_pd.xlsx')