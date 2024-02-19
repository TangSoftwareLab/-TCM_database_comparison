from database_statistic import get_herb_overlap, \
    get_ingredient_overlap, get_herb_ingre_pairs_detail
import sys
import os
import time
import pandas as pd
import tqdm._tqdm

sys.path.insert(0, 'C://Users//yinyin//Desktop//Project//Drug repurposing')

from process import drug_annoataion_pipeline

def merge_all_data():
    herb_dict, herb_pd_dict, herb_over_pd = get_herb_overlap()
    herb_over_pd.to_csv('result/table/herb_overlap.csv')
    ingre_dict, ingre_pd_dict, ingre_over_pd = get_ingredient_overlap()
    ingre_over_pd.to_csv('result/table/ingredient_overlap.csv')
    herb_ingre_result_dict, herb_ingre_result_pd,herb_ingre_overlap_pd = get_herb_ingre_pairs_detail()
    herb_ingre_result_pd.to_csv('result/table/herb_ingredient_merged.csv')
    # herb_ingre_overlap_pd.to_csv('result/table/herb_ingre_overlap.csv')

def anno_ingredient():
    pass
    #TODO: IMPORT ANNO PIPLELINE FROM REPURPOSING,
    # anno ingredient with pubchem id, smiles, inchikey, synomewa
    save_path = 'result/table/ingre_anno/'
    if not os.path.exists(save_path):
        os.mkdir(save_path)
    ingre_df = pd.read_csv('result/table/ingredient_overlap.csv', index_col=0)
    ingre_df['pubchem_id'] = ingre_df.index
    ingre_df['pubchem_id'] = ingre_df['pubchem_id'].astype(int)
    n =ingre_df.shape[0]//200
    ingre_add_pd = []
    for x in tqdm.tqdm(list(range(n))[1:]):
        start = x * 200
        end = 200 * (x + 1)
        if end > ingre_df.shape[0]:
            end = ingre_df.shape[0]
        ingre_df_one = ingre_df.iloc[start:end, :]
        # mape annottaion
        ingre_df_one_add = drug_annoataion_pipeline.use_cid_yin(ingre_df_one, 'pubchem_id')
        ingre_df_one_add.to_csv('{}ingre_anno_{}.csv'.format(save_path, x), index=None)
        ingre_add_pd.append(ingre_df_one_add)
        time.sleep(120)
    # merge all
    ingre_add_pd_all = pd.concat(ingre_add_pd, axis=0)
    ingre_add_pd_all.to_csv('{}ingre_add_pd_all.csv'.format(save_path))


def experiment_target_collection():
    pass
    #TODO:

def admet_preidction():
    #TODO:
    pass

def target_predition():
    pass
    #TODO

def calculate_stru_simi_compounds_drugs():
    pass
    #TODO

def calculate_disease_association():
    pass
    #TODO

def main():
    anno_ingredient()