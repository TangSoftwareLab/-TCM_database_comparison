import re
import requests
import pandas as pd
import ast
import os
import tqdm
import pickle
import multiprocessing as mp
from process.mysql_setting.connections import query_mysql_pd, save_to_mysql_pd

def clean_properties(property_herb):

    def prepare_component(component):
        components = component.split('<a ')
        com_clean = [[re.findall(r'id=(.*?)\'', c, re.DOTALL), re.findall('\>(.*?)\<', c, re.DOTALL)] for c in
                     components]
        com_clean_dict = [{'ingre_id': c[0][0], 'ingre_name': c[1][0]} for c in com_clean if
                          all([len(i) != 0 for i in c])]
        return com_clean_dict


    def prepare_related_target(target):
        target_s = target.split('<a ')
        target_clean = [re.findall(r'>(.*?)</a>', c, re.DOTALL) for c in target_s]
        target_clean = [d[0] for d in target_clean if len(d) != 0]
        return target_clean

    def prepare_related_databse(database):
        database_s = database.split('<a ')
        database_clean = [re.findall(r'>(.*?)</a>', c, re.DOTALL) for c in database_s]
        target_clean = [d[0] for d in database_clean if len(d) != 0]
        return database_clean


    def prepare_related_disease(disease):
        disease_s = disease.split('<a ')
        disease_clean = [re.findall(r'name=(.*?)\'', c, re.DOTALL) for c in disease_s]
        disease_clean = [d[0] for d in disease_clean if len(d) != 0]
        return disease_clean


    def prepare_formulae(formulae):
        formulae_s = formulae.split('<a ')
        formulae_clean = [[re.findall(r'id=(.*?)\'', c, re.DOTALL), re.findall('\>(.*?)\<', c, re.DOTALL)] for c in
                          formulae_s]
        formulae_clean_dict = [{'formulae_id': c[0][0], 'formule_name': c[1][0]} for c in formulae_clean if
                               all([len(i) != 0 for i in c])]
        return formulae_clean_dict


    property_clean = [re.findall('\>(.*?)\<\/div\>', p, re.DOTALL) for p in property_herb]

    new_property_clean = [p + [re.findall('Item Name":"(.*?)"}', property_herb[i], re.DOTALL)[0]] if len(p)==1 else p for i,p in enumerate(property_clean)]
    new_property_clean = [p for p in new_property_clean if len(p) != 0]
    new_property_clean = [[p[0], p[1].replace('<i>', '').replace('</i>', '')] if 'Herb Name in Ladin' in p else  p for p in new_property_clean]
    new_property_clean_dict = {i[0]: i[1] for i in new_property_clean}

    component = new_property_clean_dict['Components']
    component_clean = prepare_component(component)
    new_property_clean_dict['Components'] = component_clean


    target = new_property_clean_dict['Candidate Target Genes']
    target_clean = prepare_related_target(target)
    new_property_clean_dict['Candidate Target Genes'] = target_clean

    database = new_property_clean_dict['Database Cross References']
    database_clean = prepare_related_target(database)
    new_property_clean_dict['Database Cross References'] = database_clean

    disease = new_property_clean_dict['Diseases Associated with This Herb']
    disease_clean = prepare_related_disease(disease)
    new_property_clean_dict['Diseases Associated with This Herb'] = disease_clean

    formulae = new_property_clean_dict['Formulas Containing This Herb']
    formulae_clean = prepare_formulae(formulae)
    new_property_clean_dict['Formulas Containing This Herb'] = formulae_clean

    return new_property_clean_dict


def get_herb_info_one(id):
    url = 'http://www.tcmip.cn/ETCM/index.php/Home/Index/yc_details.html?id={}'.format(id)
    ingre_target_s = pd.read_html(url)
    if len(ingre_target_s) == 0:
        ingre_target = pd.DataFrame(columns=['Chemical Component', 'Candidate Target genes'])
    elif len(ingre_target_s) == 1:
        ingre_target = ingre_target_s[0]
    else:
        ingre_target = ingre_target_s[1]

    a = requests.get(url)
    content = a.content.decode("utf-8")

    table_list = re.findall(r' data : \[(.*?)\],', content, re.DOTALL)

    property_herb = table_list[0].split('\r\n')[1:]

    new_property_clean_dict = clean_properties(property_herb)

    if len(table_list) > 2:
        go_dict = ast.literal_eval(table_list[1])
        pathways_dict = ast.literal_eval(table_list[2])
    else:
        go_dict = None
        pathways_dict = None

    new_property_clean_dict['ingre_target'] = ingre_target
    new_property_clean_dict['go_dict'] = go_dict
    new_property_clean_dict['pathways_dict'] = pathways_dict
    return new_property_clean_dict


def get_all_herb_info(herb_id_list):
    herb_dict = {}
    for id in tqdm.tqdm(herb_id_list):
        print(id)
        try:
            new_property_clean_dict = get_herb_info_one(id)
        except:
            continue
        herb_dict[id] = new_property_clean_dict

    saved_path = '../../processed_data/etcm_id/'
    if not os.path.exists(saved_path):
        os.makedirs(saved_path)
    pickle.dump(herb_dict, open('{}etcm_dict_{}'.format(saved_path, herb_id_list[0]), 'wb'))


def merge_files():
    saved_path = 'processed_data/etcm_id/'
    all_dictionary = {}
    for file in os.listdir(saved_path):
        file_path = saved_path + file
        herb_dict = pickle.load(open(file_path, 'rb'))
        all_dictionary.update(herb_dict)

    pickle.dump(all_dictionary, open('processed_data/etcm_herb_dict', 'wb'))

def prepare_herb_ingre_all():
    database_name = 'etcm'
    sql = """SELECT * FROM herb_info as h,
                herb_ingredient_target as h_m,
                ingredient_info as m
                where h.herb_id = h_m.herb_id
                and m.Ingredient_id = h_m.ingre_id;
                """
    pd_result = query_mysql_pd(sql_string=sql, database_name=database_name)
    save_to_mysql_pd(pd_result, database_name=database_name, saved_name='herb_ingre_all')


def main():
    # merge_files()
    # herb_dict = pickle.load(open('processed_data/etcm_herb_dict', 'rb'))
    # all_id = set(range(1, 403))
    # in_ids = set(herb_dict.keys())
    #
    # left_ids = all_id.difference(in_ids)
    # get_all_herb_info(left_ids)
    prepare_herb_ingre_all()

#
# if __name__ == '__main__':
#     herb_id_list_set = [list(range(10 * i, 10 * (i + 1))) for i in list(range(0, 40))]
#     pool = mp.Pool(6)
#
#     funclist = []
#     for herb_id_list in herb_id_list_set:
#             f = pool.apply_async(get_all_herb_info, [herb_id_list])
#             funclist.append(f)
#
#     for f in funclist:
#         f.get()

