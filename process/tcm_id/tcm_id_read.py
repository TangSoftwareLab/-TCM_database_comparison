import pandas as pd
import os
import pickle
import tqdm
from process.mysql_setting.connections import query_mysql_pd, save_to_mysql_pd
import multiprocessing as mp


def get_basic_info():
    # defining the html contents of a URL.
    df = pd.read_html('http://bidd.group/TCMID/results.php?browse_formula_all=yes')
    # df[0].to_csv('original_data/tcm_id/formulae_info.txt', sep='\t')
    #
    # df_all = pd.read_html('http://bidd.group/TCMID/browse.php')
    # df_all[0].to_csv('original_data/tcm_id/disease_info.txt', sep='\t')
    # df_all[1].to_csv('original_data/tcm_id/functional_class_info.txt', sep='\t')
    # df_all[2].to_csv('original_data/tcm_id/functional_target_info.txt', sep='\t')
    # write the prescription id out
    prescription_id_list = df[0]['Prescription ID']

    return prescription_id_list


def get_one_formulae_dict(formu_key, df_formu):
    one_dict = {}
    for i in list(formu_key.keys()):
        df_formu_one = df_formu[i]
        if i >= 1:
            df_formu_one.columns = df_formu_one.iloc[0]
            df_formu_one = df_formu_one.drop(df_formu_one.index[0])
            df_formu_one.index = list(df_formu_one.iloc[:, 0])
            df_formu_one_dict = df_formu_one.to_dict(orient='index')
            one_dict[formu_key[i]] = df_formu_one_dict
        elif i == 0:
            df_formu_one.index = list(df_formu_one.iloc[:, 0])
            df_formu_one_dict = df_formu_one.to_dict(orient='index')
            one_dict.update(df_formu_one_dict)
    return one_dict


def get_formulae_relationship(prescription_id_list):
    formulae_dict = {}
    for f in tqdm.tqdm(prescription_id_list):
        print(f)

        formu_key = {0: 'Prescription_Description',
                     1: 'Prescription Components',
                     2: 'Targeted_Human_Proteins',
                     3: 'Targeted_Pathogenic_Microbes',
                     4: 'Gene_Ontology',
                     5: 'KEGG_Pathways'}
        try:
            df_formu = pd.read_html('http://bidd.group/TCMID/tcmf.php?formula={}'.format(f))
            one_dict = get_one_formulae_dict(formu_key, df_formu)
        except:
            print('wrong for'.format(f))
            continue

        formulae_dict[f] = one_dict
    return formulae_dict



def get_herb_text(herb_id_list):

    herb_dict = {}
    for c in tqdm.tqdm(herb_id_list):
        herb_id = 'TCMH' + str(c)
        herb_key = {0: 'herb_info',
                     2: 'Targeted_Human_Proteins',
                     3: 'Targeted_Pathogenic_Microbes'}

        try:
            df_herb = pd.read_html('http://bidd.group/TCMID/herb.php?herb=TCMH{}'.format(c))
            one_dict = get_one_formulae_dict(herb_key, df_herb)
        except:
            print('wrong for TCMH{}'.format(c))
            continue

        herb_dict[herb_id] = one_dict
    return herb_dict


def prepare_formulae():

    def process_one(x, column_name):
        need_extend_cols = {'Indications': ',',
                            'Disease ICD-11 Category': ';',
                            'Human Tissues Associated with Indication': ',',
                            'Function Description': ','}
        return x.split(need_extend_cols[column_name])

    def process_two(x):
        return list(x.keys())


    # save detail out
    def prepare_formulae_detail_more(result_pd_simple, column_name, process_type):
        result_pd_simple_one = result_pd_simple[['Prescription ID', column_name]]
        result_pd_simple_one = result_pd_simple_one.dropna()

        if process_type == 1:
            result_pd_simple_one[column_name] = result_pd_simple_one[column_name].apply(lambda x: process_one(x, column_name))
        elif process_type == 2:
            result_pd_simple_one[column_name] = result_pd_simple_one[column_name].apply(lambda x: process_two(x))

        result_pd_simple_one = result_pd_simple_one.explode(column_name, ignore_index=True)
        result_pd_simple_one = result_pd_simple_one.dropna()
        result_pd_simple_one[column_name] = result_pd_simple_one[column_name].apply(lambda x: x.strip())
        save_name = column_name.replace(' ', '_')
        result_pd_simple_one.to_csv('original_data/tcm_id/formulae_{}.txt'.format(save_name),
                                    index=None, sep='\t')
        return result_pd_simple_one


    def extend_diction(result_pd, single_keys, more_keys):
        result_pd_simple = result_pd[single_keys]

        # clean the data for simple
        for c in result_pd_simple.columns:
            result_pd_simple[c] = result_pd_simple[c].apply(lambda x: x[1])

        result_pd_simple.to_csv('original_data/tcm_id/formulae_detail.txt', index=None, sep='\t')

        need_extend_cols = {'Indications': 1,
                            'Disease ICD-11 Category': 1,
                            'Human Tissues Associated with Indication': 1,
                            'Function Description': 1
                            }

        for col, process_type in need_extend_cols.items():
            prepare_formulae_detail_more(result_pd_simple, col, 1)

        # process those target related
        result_pd_more = result_pd[more_keys]
        result_pd_more['Prescription ID'] = result_pd_more.index
        for c in more_keys:
            prepare_formulae_detail_more(result_pd_more, c, 2)


    # do real process
    formu_keys = ['Prescription_Description',
                 'Prescription Components',
                 'Targeted_Human_Proteins',
                 'Targeted_Pathogenic_Microbes',
                 'Gene_Ontology',
                 'KEGG_Pathways']

    tcmid_formulae = pickle.load(open('processed_data/tcm_id_formulae', 'rb'))
    all_keys = tcmid_formulae.get(list(tcmid_formulae.keys())[0]).keys()

    # selelct only simple formulae related details
    single_keys = set(list(all_keys)) - set(formu_keys)

    # prepare to dataframe
    result_pd = pd.DataFrame.from_dict(tcmid_formulae, orient='index')
    more_keys = set(list(all_keys)) - single_keys

    # save separate files
    extend_diction(result_pd, single_keys, more_keys)


def prepare_herb_info():
    tcmid_herb = pickle.load(open('processed_data/tcm_id_herb','rb'))
    result_pd = pd.DataFrame.from_dict(tcmid_herb, orient='index')
    herb_keys = ['TCM Properties',
                'Functions',
                'Targeted_Human_Proteins',
                'Targeted_Pathogenic_Microbes']

    # selelct only simple formulae related details
    single_keys = set(list(result_pd.columns)) - set(herb_keys)

    for c in single_keys:
        result_pd[c] = result_pd[c].apply(lambda x: x[1])

    result_pd[list(single_keys)+['TCM Properties', 'Functions']].to_csv('original_data/tcm_id/herb_detail.txt',
                                                                        index=None,
                                                                        sep='\t')

    result_pd['Herb ID'] = list(result_pd.index)

    for column_name in ['Targeted_Human_Proteins',
                'Targeted_Pathogenic_Microbes']:
        result_pd_simple_one = result_pd[['Herb ID', column_name]]
        result_pd_simple_one = result_pd_simple_one.dropna()
        result_pd[column_name] = result_pd[column_name].apply(lambda x: list(x.values()))
        result_pd_simple_one = result_pd_simple_one.explode(column_name, ignore_index=True)
        result_pd_simple_one = result_pd_simple_one.dropna()
        result_pd_simple_one[column_name] = result_pd_simple_one[column_name].apply(lambda x: x.strip())
        save_name = column_name.replace(' ', '_')
        result_pd_simple_one.to_csv('original_data/tcm_id/herb_{}.txt'.format(save_name),
                                    index=None, sep='\t')

def read_tcm_id_files(path_selected):
    database_dict = {}
    for file in os.listdir(path_selected):
        name = file.replace('CMAUPv1.0_download_', 'cp_')
        name = name.replace('Associations', 'pairs')
        name = name.replace('Associated', 'pairs')

        name = name.split('.')[0]
        data = pd.read_csv(path_selected + file, sep='\t')
        database_dict[name] = data
    return database_dict



def tcm_id_save_to_mysql(path_selected):
    # open the mysql workbench, the panel of local host one
    database_name = 'tcm_id'
    database_dict = read_tcm_id_files(path_selected)
    for k, v in database_dict.items():
        try:
            save_to_mysql_pd(pd_result=v,
                             database_name=database_name,
                             saved_name=k)
        except:
            continue


# as we map the herb information by herb latin in tcm-id to CMAUP, as a result, we create herb ingredients pairs for only tcm
def prepare_herb_ingredient_pairs():
    database_name = 'tcm_id'
    sql = """SELECT
                *
                FROM
                tcm_id.cp_plant_ingredient_pairs_allingredients as h,
                tcm_id.herb_detail as d,
                tcm_id.cp_plants as p,
                tcm_id.cp_ingredients_all as cp_i
                where
                h.Plant_ID = p.Plant_ID
                and p.Plant_Name = d.`Latin Name`
                and h.Ingredient_ID = cp_i.zinc_id;"""

    pd_result = query_mysql_pd(sql_string=sql, database_name=database_name)
    save_to_mysql_pd(pd_result=pd_result,
                     database_name=database_name,
                     saved_name='tcm_plant_ingredient_pairs_allingredients')

    return pd_result


def prepare_herb_all_info():
    database_name = 'tcm_id'
    sql = """SELECT
                *
                FROM
                tcm_id.cp_plant_ingredient_pairs_allingredients as h,
                tcm_id.herb_detail as d,
                tcm_id.cp_plants as p
                where
                h.Plant_ID = p.Plant_ID
                and p.Plant_Name = d.`Latin Name`;"""

    pd_result = query_mysql_pd(sql_string=sql, database_name=database_name)
    save_to_mysql_pd(pd_result=pd_result,
                     database_name=database_name,
                     saved_name='tcm_herb_new')

    return pd_result

def prepare_herb_active_ingredient_pairs():
    database_name = 'tcm_id'
    sql = """SELECT
                    h.Plant_ID, h.Ingredient_ID
                    FROM
                    tcm_id.cp_plant_ingredient_pairs_onlyactiveingredients as h,
                    tcm_id.herb_detail as d,
                    tcm_id.cp_plants as p
                    where
                    h.Plant_ID = p.Plant_ID
                    and p.Plant_Name = d.`Latin Name`;"""

    pd_result = query_mysql_pd(sql_string=sql, database_name=database_name)
    save_to_mysql_pd(pd_result=pd_result,
                     database_name=database_name,
                     saved_name='tcm_plant_ingredient_pairs_onlyactiveingredients')
    return pd_result


def prepare_ingredient_info():
    database_name = 'tcm_id'
    sql = """SELECT * FROM tcm_id.cp_ingredients_all;"""
    sql_2 = """SELECT * FROM tcm_plant_ingredient_pairs_allingredients;"""
    sql_3 = """SELECT * FROM tcm_plant_ingredient_pairs_onlyactiveingredients;"""
    ingredients_info = query_mysql_pd(sql_string=sql, database_name=database_name)
    herb_ingredients_pd = query_mysql_pd(sql_string=sql_2, database_name=database_name)
    herb_activate_ingredients_pd = query_mysql_pd(sql_string=sql_3, database_name=database_name)
    tcm_ingredients_info = ingredients_info[ingredients_info['zinc_id'].isin(herb_ingredients_pd['Ingredient_ID'])]
    tcm_activate_ingredients_info = ingredients_info[ingredients_info['zinc_id'].isin(herb_activate_ingredients_pd['Ingredient_ID'])]
    save_to_mysql_pd(pd_result=tcm_ingredients_info,
                     database_name='tcm_id',
                     saved_name='tcm_ingredients_all')

    save_to_mysql_pd(pd_result=tcm_activate_ingredients_info,
                     database_name='tcm_id',
                     saved_name='tcm_activate_ingredients_all')

def prepare_ingre_target_activity():
    database_name = 'tcm_id'
    sql = """SELECT * FROM tcm_id.tcm_ingredients_all as m,
            tcm_id.cp_ingredient_target_pairs_activityvalues_references as c_i_acti
            where
            c_i_acti.Ingredient_ID = m.zinc_id;"""

    activate_ingre_tar = query_mysql_pd(sql_string=sql, database_name=database_name)
    save_to_mysql_pd(pd_result=activate_ingre_tar,
                     database_name=database_name,
                     saved_name='tcm_ingredients_tar_activi')



def main():
    prescription_id_list = get_basic_info()
    formulae_dict = get_formulae_relationship(prescription_id_list)
    with(open('processed_data/tcm_id', 'wb')) as handle:
        pickle.dump(formulae_dict, handle)

    database_selected = 'tcm_id'
    path_selected = 'original_data/{}/'.format(database_selected)
    tcm_id_save_to_mysql(path_selected)


# if we want process it in pipeline, we just use multiple process package like below
def run_formulae():
    if __name__ == '__main__':
        # for foumulae  :prescription_id_list = get_basic_info(), while for herb basic information:prescription_id_list = list(range(1,2752))
        prescription_id_list = get_basic_info()
        start = 0
        prescription_id = []
        while start+100 <= len(prescription_id_list):
            prescription_id.append(prescription_id_list[start:start+100])
            start += 100
        prescription_id.append(prescription_id_list[start:])

        pool = mp.Pool(8) # use 8 processes

        funclist = []
        for prescription_id_set in tqdm.tqdm(prescription_id):
                # process each data frame
                f = pool.apply_async(get_formulae_relationship,
                                     [prescription_id_set])
                funclist.append(f)

        result = {}
        for f in funclist:
            result.update(f.get())


        with(open('../../processed_data/tcm_id_formulae', 'wb')) as handle:
            pickle.dump(result, handle)

        # import pickle
        # tcmsp_database = pickle.load(open('processed_data/tcm_id_formulae','rb'))



def run_herb():
    if __name__ == '__main__':
        # for foumulae  :prescription_id_list = get_basic_info(), while for herb basic information:prescription_id_list = list(range(1,2752))
        prescription_id_list = list(range(1, 2752))
        start = 0
        prescription_id = []
        while start + 100 <= len(prescription_id_list):
            prescription_id.append(prescription_id_list[start:start + 100])
            start += 100
        prescription_id.append(prescription_id_list[start:])

        pool = mp.Pool(8)  # use 8 processes

        funclist = []
        for prescription_id_set in tqdm.tqdm(prescription_id):
            # process each data frame
            f = pool.apply_async(get_herb_text,
                                 [prescription_id_set])
            funclist.append(f)

        result = {}
        for f in funclist:
            result.update(f.get())

        with(open('../../processed_data/tcm_id_herb', 'wb')) as handle:
            pickle.dump(result, handle)

        # import pickle
        # tcmid_herb = pickle.load(open('processed_data/tcm_id_herb','rb'))
        # tcmid_formulae = pickle.load(open('processed_data/tcm_id_formulae','rb'))
