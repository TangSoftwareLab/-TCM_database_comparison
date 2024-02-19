
import pandas as pd
from process.mysql_setting.connections import query_mysql_pd, save_to_mysql_pd

def get_key_values():

    """SELECT
    count(*)
    FROM
    tcmsp.molecules_targets_relationships;"""

    """SELECT
    count(distinct(tcmsp_ingredient_id))
    FROM
    tcmsp.molecules_targets_relationships;"""

    """SELECT
    count(distinct(tcmsp_target_id))
    FROM
    tcmsp.molecules_targets_relationships;"""

    """SELECT
    count(*)
    FROM
    tcmsp.herbs_molecules_relationships;"""

    """SELECT
    count(distinct(tcmsp_herb_id))
    FROM
    tcmsp.herbs_molecules_relationships;"""

    """SELECT
    count(distinct(tcmsp_ingredient_id))
    FROM
    tcmsp.herbs_molecules_relationships;"""



def get_herb_info_tcmsp(herb_chinese_list):
    database_name = 'tcmsp'
    herb_list_str = ','.join(["'{}'".format(x) for x in set(herb_chinese_list)])
    sql = """SELECT * FROM new_herb as h
                where h.tcmsp_herb_cn_name in ({});
               """.format(herb_list_str)
    pd_result = query_mysql_pd(sql_string=sql, database_name=database_name)

    return pd_result

def get_ingredient_info_tcmsp(ingredient_id_list):
    database_name = 'tcmsp'
    ingredient_id_str = ','.join(["'{}'".format(x) for x in set(ingredient_id_list)])
    sql = """SELECT * FROM 
                new_molecular_info as m
                where m.tcmsp_ingredient_id in ({});
                """.format(ingredient_id_str)
    pd_result = query_mysql_pd(sql_string=sql, database_name=database_name)
    return pd_result


def get_herb_ingredient_tcmsp(herb_list):
    database_name = 'tcmsp'
    herb_list_str = ','.join(["'{}'".format(x) for x in set(herb_list)])
    # sql = """SELECT * FROM new_herb as h,
    #         new_molecular_info as m,
    #         info_targets as t,
    #         herbs_molecules_relationships as h_m
    #         where h.tcmsp_herb_cn_name in ({})
    #         and h.tcmsp_herb_id = h_m.tcmsp_herb_id
    #         and m.tcmsp_ingredient_id = h_m.tcmsp_ingredient_id
    #         ;
    #         """.format(herb_list_str)

    sql = """SELECT * FROM all_herb_ingre_detail as h
                where h.tcmsp_herb_cn_name in ({})
                ;
                """.format(herb_list_str)
    pd_result = query_mysql_pd(sql_string=sql, database_name=database_name)

    return pd_result


def get_ingre_tar_tcmsp(ingredient_id_list):
    database_name = 'tcmsp'
    ingredient_id_str = ','.join(["'{}'".format(x) for x in set(ingredient_id_list)])
    sql = """SELECT * FROM new_molecular_info as m,
            info_targets as t,
            molecules_targets_relationships as m_t
            where m.tcmsp_ingredient_id in ({})
            and m_t.tcmsp_ingredient_id = m.tcmsp_ingredient_id
            and m_t.tcmsp_target_id = t.tcmsp_target_id;""".format(ingredient_id_str)
    pd_result = query_mysql_pd(sql_string=sql, database_name=database_name)

    return pd_result

def get_herb_ingredient_tar_tcmsp(herb_chinese_list):
    pd_result_h_m = get_herb_ingredient_tcmsp(herb_chinese_list)
    ingredient_id_list = list(pd_result_h_m['tcmsp_ingredient_id'].unique())
    pd_result_m_t = get_ingre_tar_tcmsp(ingredient_id_list)

    # known target
    database_name = 'tcmsp'
    herb_list_str = ','.join(["'{}'".format(x) for x in set(herb_chinese_list)])
    sql = """SELECT * FROM molecules_target_known_relationships as h_t
                    where h.tcmsp_herb_cn_name in ({})
                    ;
                    """.format(herb_list_str)
    pd_result_h_t_known = query_mysql_pd(sql_string=sql, database_name=database_name)

    return pd_result_h_m, pd_result_m_t, pd_result_h_t_known


def main():
    suhuang_sapsule = ['麻黄', '紫苏叶', '地龙', '枇杷叶', '紫苏子', '蝉蜕', '前胡', '牛蒡子', '五味子']
    pd_result_h = get_herb_ingredient_tcmsp(suhuang_sapsule)
    pd_result_h.to_excel('result/case/suhuang_tcmsp_pd.xlsx')


