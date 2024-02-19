import re
import requests
import pandas as pd
import ast
import os
import tqdm
import pickle
import multiprocessing as mp


def clean_properties(property_herb):

    def prepare_related_target(target):
        target_s = target.split('<a ')
        target_clean = [re.findall(r'>(.*?)</a>', c, re.DOTALL) for c in target_s]
        target_clean = [d[0] for d in target_clean if len(d) != 0]
        return target_clean


    def prepare_related_disease(disease):
        disease_s = disease.split('<a ')
        disease_clean = [re.findall(r'name=(.*?)\'', c, re.DOTALL) for c in disease_s]
        disease_clean = [d[0] for d in disease_clean if len(d) != 0]
        return disease_clean


    def prepare_herb(china_herb):
        herb_s = china_herb.split('<a ')
        herb_clean = [[re.findall(r'id=(.*?)\'', c, re.DOTALL), re.findall('\>(.*?)\<', c, re.DOTALL)] for c in
                          herb_s]
        herb_clean_dict = [{'herb_id': c[0][0], 'herb_name': c[1][0]} for c in herb_clean if
                               all([len(i) != 0 for i in c])]
        return herb_clean_dict


    property_clean = [re.findall('\>(.*?)\<\/div\>', p, re.DOTALL) for p in property_herb]

    new_property_clean = [p + [re.findall('Item Name":"(.*?)"}', property_herb[i], re.DOTALL)[0]] if len(p)==1 else p for i,p in enumerate(property_clean)]
    new_property_clean = [p for p in new_property_clean if len(p) != 0]
    new_property_clean_dict = {i[0]: i[1] for i in new_property_clean}

    target = new_property_clean_dict['Candidate Target Genes']
    target_clean = prepare_related_target(target)
    new_property_clean_dict['Candidate Target Genes'] = target_clean

    china_formu_name = new_property_clean_dict['Formula Name in Chinese']
    china_formu_name_clean = prepare_related_target(china_formu_name)
    new_property_clean_dict['Formula Name in Chinese'] = china_formu_name_clean[0]

    disease = new_property_clean_dict['Diseases Associated with This Formula']
    disease_clean = prepare_related_disease(disease)
    new_property_clean_dict['Diseases Associated with This Formula'] = disease_clean

    china_herb = new_property_clean_dict['Herbs Contained in This Formula (Chinese)']
    herb_clean = prepare_herb(china_herb)
    new_property_clean_dict['Herbs Contained in This Formula (Chinese)'] = herb_clean

    pin_herb = new_property_clean_dict['Herbs Contained in This Formula (Chinese Pinyin)']
    herb_clean_pin = prepare_herb(pin_herb)
    new_property_clean_dict['Herbs Contained in This Formula (Chinese Pinyin)'] = herb_clean_pin

    return new_property_clean_dict


def get_formulae_info_one(id):
    url = 'http://www.tcmip.cn/ETCM/index.php/Home/Index/fj_details.html?id={}'.format(id)

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

    new_property_clean_dict['go_dict'] = go_dict
    new_property_clean_dict['pathways_dict'] = pathways_dict
    return new_property_clean_dict



def get_all_formulae_info(formulae_id_list):
    formula_dict = {}
    for id in tqdm.tqdm(formulae_id_list):
        print(id)
        try:
            new_property_clean_dict = get_formulae_info_one(id)
        except:
            continue
        formula_dict[id] = new_property_clean_dict

    saved_path = '../../processed_data/etcm_id_formulae/'
    if not os.path.exists(saved_path):
        os.makedirs(saved_path)
    pickle.dump(formula_dict, open('{}etcm_dict_formulae_{}'.format(saved_path, formulae_id_list[0]), 'wb'))


def merge_files_formulae():
    saved_path = 'processed_data/etcm_id_formulae/'
    all_dictionary = {}
    for file in os.listdir(saved_path):
        file_path = saved_path + file
        formulae_dict = pickle.load(open(file_path, 'rb'))
        all_dictionary.update(formulae_dict)

    pickle.dump(all_dictionary, open('processed_data/etcm_formulae_dict', 'wb'))


def main():
    merge_files_formulae()


# if __name__ == '__main__':
#     formulae_id_list_set = [list(range(100 * i, 100 * (i + 1))) for i in list(range(0, 39))]
#     pool = mp.Pool(6)
#
#     funclist = []
#     for formulae_id_list in formulae_id_list_set:
#             f = pool.apply_async(get_all_formulae_info, [formulae_id_list])
#             funclist.append(f)
#
#     for f in funclist:
#         f.get()