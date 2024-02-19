
import os
import pandas as pd
from process.mysql_setting.connections import query_mysql_pd, save_to_mysql_pd


def get_herb_info_tcm_id(herb_chinese_list):
    database_name = 'tcm_id'
    herb_list_str = ','.join(["'{}'".format(x) for x in set(herb_chinese_list)])
    sql = """SELECT * FROM tcm_herb_new as h
                where h.中文名 in ({});
               """.format(herb_list_str)
    pd_result = query_mysql_pd(sql_string=sql, database_name=database_name)

    return pd_result


def get_herb_ingredient_pairs(herb_chinese_list):
    database_name = 'tcm_id'
    herb_list_str = ','.join(["'{}'".format(x) for x in set(herb_chinese_list)])
    if herb_chinese_list == 'all':
        sql = """SELECT
                    *
                    FROM
                    tcm_plant_ingredient_pairs_allingredients;"""
    else:
        sql = """SELECT * FROM tcm_plant_ingredient_pairs_allingredients as h_m
                where h_m.中文名 in ({});""".format(herb_list_str)

    pd_result = query_mysql_pd(sql_string=sql, database_name=database_name)
    return pd_result


def get_herb_ingredient_tcm_id(herb_list):
    database_name = 'tcm_id'
    herb_list_str = ','.join(["'{}'".format(x) for x in set(herb_list)])
    sql = """SELECT * FROM
    tcm_id.tcm_plant_ingredient_pairs_allingredients
    where
    tcm_id.tcm_plant_ingredient_pairs_allingredients.中文名 in ({})""".format(herb_list_str)
    pd_result = query_mysql_pd(sql_string=sql, database_name=database_name)

    return pd_result

def get_herb_active_ingredient_pairs(herb_chinese_list):
    database_name = 'tcm_id'
    herb_list_str = ','.join(["'{}'".format(x) for x in set(herb_chinese_list)])
    if herb_chinese_list == 'all':
        sql = """SELECT
                        *
                        FROM
                         tcm_plant_ingredient_pairs_onlyactiveingredients;"""
    else:
        sql = """SELECT * FROM  tcm_plant_ingredient_pairs_onlyactiveingredients as h_m
                    where h_m.中文名 in ({});""".format(herb_list_str)

    pd_result = query_mysql_pd(sql_string=sql, database_name=database_name)
    return pd_result


def get_ingredient_info(ingredient_id_list):
    database_name = 'tcm_id'
    ingredient_id_str = ','.join(["'{}'".format(x) for x in set(ingredient_id_list)])
    if ingredient_id_list !='all':
        ingredient_id_str = ','.join(["'{}'".format(x) for x in set(ingredient_id_list)])
        sql = """SELECT * FROM 
                        tcm_ingredients_all as m
                        where m.Ingredient_ID in ({});
                        """.format(ingredient_id_str)
        sql_2 = """SELECT * FROM 
                        tcm_activate_ingredients_all as m
                        where m.Ingredient_ID in ({});
                        """.format(ingredient_id_str)
    else:
        sql = """SELECT
                            *
                            FROM
                            tcm_ingredients_all;"""

        sql_2 = """SELECT
                                *
                                FROM
                                tcm_activate_ingredients_all;"""

    result_all_ingredient = query_mysql_pd(sql_string=sql, database_name=database_name)
    result_activate_ingredient = query_mysql_pd(sql_string=sql_2, database_name=database_name)
    return result_all_ingredient, result_activate_ingredient



def get_ingredient_activate(ingredient_id_list):
    database_name = 'tcm_id'
    ingredient_id_str = ','.join(["'{}'".format(x) for x in set(ingredient_id_list)])
    sql = """SELECT
    *
    FROM
    tcm_id.cp_ingredient_target_pairs_activityvalues_references as c_i_acti
    where
    c_i_acti.Ingredient_ID in ({});""".format(ingredient_id_str)
    pd_result = query_mysql_pd(sql_string=sql, database_name=database_name)
    return pd_result



def get_herb_target(herb_list):
    database_name = 'tcm_id'
    herb_list_str = ','.join(["'{}'".format(x) for x in set(herb_list)])
    sql_1 = """SELECT * FROM
    tcm_id.tcm_herb_new as h,
    tcm_id.herb_targeted_pathogenic_microbes as h_t_m,
    tcm_id.cp_targets as t
    where
    h.中文名 = in ({})
    and h_t_m.`Herb ID` = h.`Component ID`
    and h_t_m.Targeted_Pathogenic_Microbes = t.Target_ID;
    ;""".format(herb_list_str)


    sql_2 = """SELECT * FROM
    tcm_id.tcm_herb_new as h,
    tcm_id.herb_targeted_human_proteins as h_t_h,
    tcm_id.cp_targets as t
    where
    h.中文名 in ({})
    and h_t_h.`Herb ID` = h.`Component ID`
    and h_t_h.Targeted_Human_Proteins = t.Target_ID;
    ;""".format(herb_list_str)

    pd_result_1 = query_mysql_pd(sql_string=sql_1, database_name=database_name)
    pd_result_2 = query_mysql_pd(sql_string=sql_1, database_name=database_name)
    targets_pd = pd.concat([pd_result_1, pd_result_2], axis=0)

    return targets_pd


def get_herb_formuae_disease():
    pass

def get_disease_related_formulae():
    pass


# statistic import value for how many record in thm-id database
def get_key_numbers_values():

    def get_herb_ingredient_stat():
        herb_ingredient_all_pairs = get_herb_ingredient_pairs('all')
        herb_active_ingredient_pairs = get_herb_active_ingredient_pairs('all')
        herb_ingredient_all_pairs.name = 'all'
        herb_active_ingredient_pairs.name = 'activate'

        for herb_ingredient_pairs in [herb_ingredient_all_pairs, herb_active_ingredient_pairs]:
            herb_ingredients_no = herb_ingredient_pairs.shape[0]
            print('The number of herb ingredient pairs {} is {}'.format(herb_ingredient_pairs.name, herb_ingredients_no))

            ingredients_no = len(herb_ingredient_pairs['Ingredient_ID'].unique())
            print('The number of {} ingredient is {}'.format(herb_ingredient_pairs.name, ingredients_no))

            plant_no = len(herb_ingredient_pairs['Plant_ID'].unique())
            print('The number of herb with at least one {} ingredient is {}'.format(herb_ingredient_pairs.name, plant_no))


            ''''
            The number of herb all ingredient pairs is 115806
            The number of all ingredient is 23630
            The number of herb with at least one all ingredient is 471
            
            The number of herb activate ingredient pairs is 29639
            The number of activate ingredient is 3564
            The number of herb with at least one activate ingredient is 471
        '''
    def get_ingredient_structure():
        result_all_ingredient, result_activate_ingredient = get_ingredient_info()
        print('the number of ingredients with structure is {}'.format(result_all_ingredient.shape[0]))
        print('the number of ingredients with activate structure is {}'.format(result_activate_ingredient.shape[0]))


# if __name__ == '__main__':
#     get_herb_ingredient_pairs()

def main():
    suhuang_sapsule = ['麻黄', '紫苏叶', '地龙', '枇杷叶', '紫苏子', '蝉蜕', '前胡', '牛蒡子', '五味子']
    pd_result_h = get_herb_ingredient_tcm_id(suhuang_sapsule)
    pd_result_h.to_excel('result/case/suhuang_tcm_id_pd.xlsx')
