from sqlalchemy import create_engine
import pandas as pd
import os
import requests
import re
import pickle
import tqdm
import multiprocessing as mp
# Todo: get the inchikey by pubchem id

def read_symmap_files(path_selected):
    database_dict = {}
    for file in os.listdir(path_selected):
        name = '_'.join(file.replace('SymMap v1.0, ', '').replace('.xlsx', '').split(' ')[:-1])
        data = pd.read_excel(path_selected + file, sheet_name=0)
        database_dict[name] = data
    return database_dict


def tcm_symmap_save_to_mysql(path_selected):

    ## first open mysql the local host, than create database tcm_herb, than click right to eit sceme, to utf8mb4

    # open the mysql workbench, the panel of local host one
    # replace password to the real password
    engine = create_engine('mysql://root:password@localhost/symmap?charset=utf8mb4')
    conn = engine.connect()
    database_dict = read_symmap_files(path_selected)
    for k,v in database_dict.items():
        try:
            v.to_sql(name=k, con=conn, if_exists='fail', index=False)
        except:
            continue


# get_herb_sym_mm_relationship from web
def get_herb_sym_mm_relationship(key_term, id_list):
    pairs_all = {}
    for i in tqdm.tqdm(id_list):
        mm_term = key_term + '0'*(5-len(str(i))) + str(i)
        url = 'https://www.symmap.org/network_summary/{}'.format(mm_term)
        response = requests.get(url)
        content = response.text
        pair_dict_one = {}
        for term in ['SMHB', 'SMTS', 'SMTT', 'SMDE', 'SMMS', 'SMIT']:
            if term != key_term:
                term_list = set([i for i in re.findall(r'({}.*?)\"'.format(term), content) if len(i) == 9])
                pair_dict_one[term] = term_list

        pairs_all[mm_term] = pair_dict_one

    return pairs_all


def arrange_herb_sym_mm_relationship(key_term):
    pairs_all = pickle.load(open('processed_data/symm_{}_pairs'.format(key_term), 'rb'))
    pairs = pd.DataFrame.from_dict(pairs_all, orient='index')

    pairs[key_term] = list(pairs.index)
    change_term = {'SMHB': 'Herb_id',
                   'SMTS': 'TCM_sympotom_id',
                   'SMTT': 'Gene_id',
                   'SMMS': 'MM_sympotom_id',
                   'SMDE': 'Disease_id',
                   'SMIT': 'MOL_id'}

    # as id differnt in web and download files, we need uniform them

    for term in list(change_term.keys()):

        if term != key_term:
            pairs_selelcted = pairs[[key_term, term]]

            pairs_selelcted = pairs_selelcted.explode(term, ignore_index=True)
            pairs_selelcted = pairs_selelcted.dropna()
            pairs_selelcted[term] = pairs_selelcted[term].astype(str).apply(lambda x: x.replace(term, ''))
            pairs_selelcted[term] = pairs_selelcted[term].apply(lambda x: int(x))

            pairs_selelcted[key_term] = pairs_selelcted[key_term].astype(str).apply(lambda x: x.replace(key_term, ''))
            pairs_selelcted[key_term] = pairs_selelcted[key_term].apply(lambda x: int(x))

            pairs_selelcted = pairs_selelcted.rename(columns={term_2: change_term[term_2] for term_2 in list(pairs_selelcted.columns)})

            engine = create_engine('mysql://root:Mqxs320321wyy@localhost/symmap?charset=utf8mb4')
            conn = engine.connect()
            pairs_selelcted.to_sql(name='{}_{}'.format(key_term.lower(), term.lower()), con=conn, if_exists='fail', index=False)


def run_pipeline(id_list):
    key_term = 'SMIT'
    ingre_sym_mm = get_herb_sym_mm_relationship(key_term, id_list)
    path_saved = '../../processed_data/symmap_ingre/'
    if not os.path.exists(path_saved):
        os.makedirs(path_saved)
    with(open('{}symm_{}_pairs_{}'.format(path_saved, 'SMIT', id_list[0]), 'wb')) as handle:
        pickle.dump(ingre_sym_mm, handle)


def merge_files(term):
    saved_path = '../../processed_data/symmap_ingre/'
    all_dictionary = {}
    for file in os.listdir(saved_path):
        file_path = saved_path + file
        herb_dict = pickle.load(open(file_path, 'rb'))
        all_dictionary.update(herb_dict)
    pickle.dump(all_dictionary, open('../../processed_data/symm_{}_pairs'.format(term),'wb'))


def main():

    # download_data()
    # def download_data_from_web():
    #     database_selected = 'symmap'
    #     path_selected = 'original_data/{}/'.format(database_selected)
    #     tcm_symmap_save_to_mysql(path_selected)

    # herb_sym_mm = get_herb_sym_mm_relationship('SMMS', list(range(1, 961+1)))
    # with(open('processed_data/symm_{}_pairs'.format('SMMS'), 'wb')) as handle:
    #     pickle.dump(herb_sym_mm, handle)
    # arrange_herb_sym_mm_relationship('SMMS')

    #
    # herb_sym_herb = get_herb_sym_mm_relationship('SMHB', list(range(1, 499+1)))
    # arrange_herb_sym_mm_relationship('SMHB')
    # with(open('processed_data/symm_{}_pairs'.format('SMHB'), 'wb')) as handle:
    #     pickle.dump(herb_sym_herb, handle)

    ingre_sym_mm = get_herb_sym_mm_relationship('SMIT', 19595)
    with(open('processed_data/symm_{}_pairs'.format('SMIT'), 'wb')) as handle:
        pickle.dump(ingre_sym_mm, handle)
    arrange_herb_sym_mm_relationship('SMIT')


    # pairs_all= pickle.load(open('processed_data/symm_SMMS_pairs', 'rb'))

if __name__ == '__main__':
    ingre_id_list_set = [range(200 * i+1, 200 * (i + 1)+1) for i in list(range(70, 100))]
    pool = mp.Pool(6)

    funclist = []
    for ingre_id_list in ingre_id_list_set:
        f = pool.apply_async(run_pipeline, [ingre_id_list])
        funclist.append(f)

    for f in funclist:
        f.get()

    # merge_files('SMIT')
    # arrange_herb_sym_mm_relationship('SMIT')