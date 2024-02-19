import re
import requests
import pandas as pd
import ast
import os
import tqdm
import pickle
import multiprocessing as mp


def clean_properties(property_herb):
    def prepare_related_link(target):
        target_s = target.split('<a ')
        target_clean = [re.findall(r'>(.*?)</a>', c, re.DOTALL) for c in target_s]
        target_clean = [d[0] for d in target_clean if len(d) != 0]
        return ','.join(target_clean)

    def prepare_image_id(image):
        target_clean = re.findall(r'molecular/(.*?).svg', image, re.DOTALL)
        return ','.join(target_clean)

    property_clean = [re.findall('\>(.*?)\<\/div\>', p, re.DOTALL) for p in property_herb]
    new_property_clean = [p + [re.findall('Item Name":"(.*?)"}', property_herb[i], re.DOTALL)[0]] if len(p)==1 else p for i,p in enumerate(property_clean)]
    new_property_clean = [p for p in new_property_clean if len(p) != 0]
    new_property_clean_dict = {i[0]: i[1] for i in new_property_clean}

    term_process = ['External Link to PubChem',
                    'External Link to ChEMBL',
                    'References',
                    'Candidate Target Genes',
                    'Diseases Associated with This Ingredient']
    for term in term_process:
        key_value = new_property_clean_dict[term]
        key_value_clean = prepare_related_link(key_value)
        new_property_clean_dict[term] = key_value_clean

    key_value = new_property_clean_dict['2D-Structure']
    key_value_clean = prepare_image_id(key_value)
    new_property_clean_dict['2D-Structure'] = key_value_clean

    return new_property_clean_dict


def get_ingre_info_one(id):
    url = 'http://www.tcmip.cn/ETCM/index.php/Home/Index/cf_details.html?id={}'.format(id)
    a = requests.get(url)
    content = a.content.decode("utf-8")

    table_list = re.findall(r' data : \[(.*?)\],', content, re.DOTALL)

    property_herb = table_list[0].split('\r\n')[1:]

    new_property_clean_dict = clean_properties(property_herb)

    return new_property_clean_dict


def get_all_ingre_info(ingre_id_list):
    ingre_dict = {}
    for id in tqdm.tqdm(ingre_id_list):
        print(id)
        try:
            new_property_clean_dict = get_ingre_info_one(id)
        except:
            continue
        ingre_dict[id] = new_property_clean_dict

    saved_path = '../../processed_data/etcm_id_ingre/'
    if not os.path.exists(saved_path):
        os.makedirs(saved_path)
    pickle.dump(ingre_dict, open('{}etcm_dict_{}'.format(saved_path, ingre_id_list[0]), 'wb'))


def merge_files():
    saved_path = 'processed_data/etcm_id_ingre'
    all_dictionary = {}
    for file in os.listdir(saved_path):
        file_path = saved_path + file
        herb_dict = pickle.load(open(file_path, 'rb'))
        all_dictionary.update(herb_dict)

    pickle.dump(all_dictionary, open('processed_data/etcm_ingre_dict', 'wb'))


# if __name__ == '__main__':
#     ingre_id_list_set = [list(range(100 * i, 100 * (i + 1))) for i in list(range(0, 73))]
#     pool = mp.Pool(6)
#
#     funclist = []
#     for ingre_id_list in ingre_id_list_set:
#             f = pool.apply_async(get_all_ingre_info, [ingre_id_list])
#             funclist.append(f)
#
#     for f in funclist:
#         f.get