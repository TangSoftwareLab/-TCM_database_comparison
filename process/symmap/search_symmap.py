import pandas as pd
from process.mysql_setting.connections import query_mysql_pd, save_to_mysql_pd

def get_herb_ingredient_sym(herb_chinese_list):
    database_name = 'symmap'
    herb_list_str: str = ','.join(["'{}'".format(x) for x in set(herb_chinese_list)])
    sql = """SELECT * FROM all_herb_ingre_detail as h
            where h.Chinese_name in ({});
            """.format(herb_list_str)

    pd_result = query_mysql_pd(sql_string=sql, database_name=database_name)

    return pd_result


def get_herb_info_symm(herb_chinese_list):
    database_name = 'symmap'
    herb_list_str = ','.join(["'{}'".format(x) for x in set(herb_chinese_list)])
    sql = """SELECT * FROM smhb as h
                where h.Chinese_name in ({});
               """.format(herb_list_str)
    pd_result = query_mysql_pd(sql_string=sql, database_name=database_name)

    return pd_result


def get_herb_symm(herb_chinese_list):
    database_name = 'symmap'
    herb_list_str = ','.join(["'{}'".format(x) for x in set(herb_chinese_list)])
    sql = """SELECT * FROM smhb as h,
            smms as m,
            smhb_smms as h_m
            where h.Chinese_name in ({})
            and h.Herb_id = h_m.Herb_id
            and h_m.MM_sympotom_id = m.MM_symptom_id;
                   """.format(herb_list_str)
    pd_result = query_mysql_pd(sql_string=sql, database_name=database_name)

    return pd_result

def get_herb_symm_gene(herb_chinese_list):
    database_name = 'symmap'
    herb_list_str = ','.join(["'{}'".format(x) for x in set(herb_chinese_list)])
    sql = """SELECT * FROM smhb as h,
            smms as m,
            smhb_smms as h_m
            where h.Chinese_name in ({})
            and h.Herb_id = h_m.Herb_id
            and h_m.MM_sympotom_id = m.MM_symptom_id;
                       """.format(herb_list_str)
    pd_result = query_mysql_pd(sql_string=sql, database_name=database_name)
    # map symptom id to geneid
    symptom_id_list = list(pd_result['MM_symptom_id'].unique())
    symptom_id_list_str_2 = ','.join(["'{}'".format(x) for x in set(symptom_id_list)])
    sql_2 = """SELECT * FROM smms as m,
                smms_smtt as m_g,
                smtt as g
                where m.MM_symptom_id in ({})
                and m.MM_symptom_id = m_g.MM_sympotom_id
                and m_g.Gene_id = g.Gene_id;
                           """.format(symptom_id_list_str_2)
    pd_result_2 = query_mysql_pd(sql_string=sql_2, database_name=database_name)
    return pd_result, pd_result_2

def main():
    suhuang_sapsule = ['麻黄', '紫苏叶', '地龙', '枇杷叶', '紫苏子', '蝉蜕', '前胡', '牛蒡子', '五味子']
    #result_pd_symm = get_herb_symm(suhuang_sapsule)
    result_pd_symm, pd_result_sym_tar = get_herb_symm_gene(suhuang_sapsule)
    result_pd_symm.to_excel('result/case/suhuang_symptoms.xlsx')
    pd_result_sym_tar.to_excel('result/case/suhuang_symptoms_target.xlsx')
    result_pd_herb_ingre_sym = get_herb_ingredient_sym(suhuang_sapsule)
    result_pd_herb_ingre_sym.to_excel('result/case/suhuang_sym_herb_ingre.xlsx')


