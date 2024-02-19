import pandas as pd
import re
from process.mysql_setting.connections import query_mysql_pd, save_to_mysql_pd

def prepare_mysql_table(com_pd):
    database = 'tm_mc'
    # science_name_pd = com_pd['SCIENCE'].str.split(']', n=1, expand=True).rename(columns={0:'science_names', 1:'web'})
    # def clean(x):
    #     return x.replace('[<i>', '').replace('</i> ', ' ').split(', <i>')
    #
    # science_name_pd['science_names'] = science_name_pd['science_names'].apply(lambda x: clean(x) if not isinstance(x, float) else None)
    # science_name_pd['web'] = science_name_pd['web'].apply(
    #     lambda x: x.replace('<a href="', '').replace('" target="new">[NCBI link', '') if not isinstance(x, float) else None)
    #
    # com_new = pd.merge(com_pd, science_name_pd, axis=0)

    # herb
    com_pd['CID'] = com_pd['CID'].apply(lambda x:x.split('|') if not isinstance(x, float) else None)
    com_pd = com_pd.explode('CID', ignore_index=True)

    herb_col = ['LATIN', 'COMMON', 'CHINESE']
    herb_pd = com_pd[herb_col].drop_duplicates()
    herb_pd['herb_id'] = list(range(1, herb_pd.shape[0]+1))
    herb_dict = dict(zip(herb_pd['CHINESE'], herb_pd['herb_id']))
    save_to_mysql_pd(herb_pd, database_name=database, saved_name='herb')

    # ingredient
    ingre_col = ['COMPOUND', 'CID', 'CSID']
    ingre_pd = com_pd[ingre_col].drop_duplicates()
    ingre_pd['ingre_id'] = list(range(1, ingre_pd.shape[0] + 1))
    ingre_dict = dict(zip(ingre_pd['CID'], ingre_pd['ingre_id']))
    save_to_mysql_pd(ingre_pd, database_name=database, saved_name='ingredient_info')

    # add id
    com_pd['ingre_id'] = ingre_pd['CID'].apply(lambda x: ingre_dict.get(x))
    com_pd['herb_id'] = com_pd['CHINESE'].apply(lambda x: herb_dict.get(x))
    save_to_mysql_pd(com_pd, database_name=database, saved_name='herb_ingredient_info')



def main():
    com_pd = pd.read_csv('original_data/tm_mc/compounds.txt', sep='\t')
    prepare_mysql_table(com_pd)