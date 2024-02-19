import pandas as pd
from process.mysql_setting.connections import query_mysql_pd, save_to_mysql_pd
import re
import numpy as np



def get_herb_info_herbdb(herb_chinese_list):
    database_name = 'tcm_herb'
    herb_list_str = ','.join(["'{}'".format(x) for x in set(herb_chinese_list)])
    sql = """SELECT * FROM herb_herb_info as h
                where h.Herb_cn_name in ({});
               """.format(herb_list_str)
    pd_result = query_mysql_pd(sql_string=sql, database_name=database_name)

    # experiment
    sql_experiment = """SELECT * FROM herb_herb_info as h,
                    herb_experiment_info as e
                    where h.Herb_cn_name in ({})
                    and h.Herb_ID = e.`Herb/ingredient_id`;
                   """.format(herb_list_str)
    pd_result_experiment = query_mysql_pd(sql_string=sql_experiment, database_name=database_name)

    # reference
    sql_refer = """SELECT * FROM herb_herb_info as h,
                        herb_reference_info as r
                        where h.Herb_cn_name in ({})
                        and h.Herb_ID = r.`Herb/ingredient_id`;
                       """.format(herb_list_str)
    pd_result_refer = query_mysql_pd(sql_string=sql_refer, database_name=database_name)

    # immuno
    sql_immuno = """SELECT * FROM herb_herb_info as h,
                            herb_reference_info as r
                            where h.Herb_cn_name in ({})
                            and h.Herb_ID = r.`Herb/ingredient_id`;
                           """.format(herb_list_str)
    pd_result_immuno = query_mysql_pd(sql_string=sql_immuno, database_name=database_name)

    return pd_result, pd_result_experiment, pd_result_refer, pd_result_immuno


def get_ingredient_info_herbdb(ingredient_id_list):
    database_name = 'tcm_herb'
    ingredient_id_str = ','.join(["'{}'".format(x) for x in set(ingredient_id_list)])
    sql = """SELECT * FROM 
                herb_ingredient_info as m
                where m.Ingredient_id in ({});
                """.format(ingredient_id_str)
    pd_result = query_mysql_pd(sql_string=sql, database_name=database_name)

    return pd_result


def get_herb_ingredient_etcm(herb_chinese_list):
    database_name = 'tcm_herb'
    herb_list_str: str = ','.join(["'{}'".format(x) for x in set(herb_chinese_list)])
    # sql = """SELECT * FROM herb_info as h,
    #         herb_ingredient as h_m,
    #         ingredient_info as m
    #         where h.`Herb Name in Chinese` in ({})
    #         and h.herb_id = h_m.herb_id
    #         and h_m.ingre_id = m.Ingredient_id;
    #         """.format(herb_list_str)
    # TODO:
    #pd_result = query_mysql_pd(sql_string=sql, database_name=database_name)
    #return pd_result


def main():
    suhuang_sapsule = ['灵芝', '麻黄', '紫苏叶', '地龙', '枇杷叶', '紫苏子', '蝉蜕', '前胡', '牛蒡子', '五味子']

    pd_result, pd_result_experiment, pd_result_refer, pd_result_immuno = get_herb_info_herbdb(suhuang_sapsule)
    with pd.ExcelWriter('result/case/suhuang_output_herbdb.xlsx') as writer:
        pd_result.to_excel(writer, sheet_name='herb_info')
        pd_result_experiment.to_excel(writer, sheet_name='experiment')
        pd_result_refer.to_excel(writer, sheet_name='reference')
        pd_result_immuno.to_excel(writer, sheet_name='immuno')
