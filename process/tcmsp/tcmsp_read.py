import pandas as pd
import os
import pickle
from sqlalchemy import create_engine


class load_tcmsp_database():

    def __init__(self, path_selected):
        self.path_selected = path_selected
        self.tcmsp_database_dict = self.read_files(self.path_selected)

        # herb preparation
        self.new_herb = self.merge_herb_info_dict(self.tcmsp_database_dict)
        self.herb_dict = self.get_herb_dict(self.new_herb)
        self.herb_id_cn_dict = self.get_herb_id_cn_dict(self.new_herb)

        # molecular preparation
        self.new_molecular_info = self.merge_molecular_info(self.tcmsp_database_dict)
        self.molecular_info_dict = self.get_molecular_info_dict(self.new_molecular_info)
        self.mol_inchikey_dict = self.get_mol_inchikey_dict(self.new_molecular_info)

        self.herb_id_mol_id_dict = self.get_herb_cn_mol_inchikey(self.tcmsp_database_dict,
                                                                 self.herb_id_cn_dict,
                                                                 self.mol_inchikey_dict)

        # target preparation
        self.mol_target_validated_dict, self.mol_target_predicted_dict = self.get_mol_target_dict(
            self.tcmsp_database_dict,
            self.mol_inchikey_dict)
        self.target_info_dict = self.get_target_info_dict(self.tcmsp_database_dict)

        # extend mol target info
        self.mol_target_validated_dict_extend = self.extend_parent_child_info(
            self.mol_target_validated_dict,
            self.target_info_dict)
        self.mol_target_predicted_dict_extend = self.extend_parent_child_info(
            self.mol_target_predicted_dict,
            self.target_info_dict)

        # map target info to mol infor
        self.molecular_info_dict = self.map_mol_target_info(self.molecular_info_dict, self.mol_target_validated_dict_extend,
                            self.mol_target_predicted_dict_extend)

        # extend mol_ info to herb id
        self.herb_id_mol_id_dict_extend = self.extend_parent_child_info(
            self.herb_id_mol_id_dict,
            self.molecular_info_dict)

        #mao molecular to herb info
        self.herb_dict = self.map_mol_herb_info(self.herb_dict, self.herb_id_mol_id_dict_extend)


    # read files from local folder
    def read_files(self, path_selected):
        tcmsp_database_dict = {}
        for file in os.listdir(path_selected):
            name = '_'.join(file.split('.')[0].split('_')[1:])
            data = pd.read_csv(path_selected + file, sep='\t')
            if 'tcmsp_herb_id' in list(data.columns):
                data['tcmsp_herb_id'] = data['tcmsp_herb_id'].apply(lambda x:'H'+(5-len(str(x)))*'0' + str(x))
            tcmsp_database_dict[name] = data
        return tcmsp_database_dict


    def merge_herb_info_dict(self, tcmsp_database_dict):
        '''
        herb_info_keys = ['Info_Herbs_Classification', 'Info_Herbs_Name']
        :return:
        '''

        new_herb = pd.merge(tcmsp_database_dict['Info_Herbs_Name'],
                   tcmsp_database_dict['Info_Herbs_Classification'],
                 left_on='tcmsp_herb_child_id',
                 right_on='tcmsp_herb_child_id',
                             how='outer')
        return new_herb

    def get_herb_dict(self, new_herb):
        new_herb.index = new_herb['tcmsp_herb_cn_name']
        herb_dict = new_herb.to_dict(orient='index')
        return herb_dict

    def get_herb_id_cn_dict(self,new_herb):
        herb_id_cn_dict = dict(zip(new_herb['tcmsp_herb_id'], new_herb['tcmsp_herb_cn_name']))
        return herb_id_cn_dict

    # merge molecular_info together
    def merge_molecular_info(self, tcmsp_database_dict):
        '''
        'Molecules_Synonyms_Relationships'
        'Moleculars_Smiles'
        'Molecules_CAS_Relationships'
        'Info_Molecules'
        :return:
        '''

        new_molecular_info = tcmsp_database_dict['Info_Molecules']
        new_molecular_info = pd.merge(new_molecular_info,
                 tcmsp_database_dict['Moleculars_Smiles'],
                 left_on='tcmsp_ingredient_id',
                 right_on='tcmsp_ingredient_id',
                 how='left')

        # prepare the mol cas pairs to dictionary
        mol_cas_dict = dict(tcmsp_database_dict['Molecules_CAS_Relationships'].groupby(
            'tcmsp_ingredient_id')['tcmsp_ingredient_cas'].apply(list))

        mol_synonyms_dict = dict(tcmsp_database_dict['Molecules_Synonyms_Relationships'].groupby(
            'tcmsp_ingredient_id')['tcmsp_ingredient_synonyms'].apply(list))

        # merge cas to dataframe
        new_molecular_info['tcmsp_ingredient_cas'] = new_molecular_info['tcmsp_ingredient_id'].apply(
            lambda x:mol_cas_dict[x] if x in mol_cas_dict else None)
        new_molecular_info['tcmsp_ingredient_synonyms'] = new_molecular_info['tcmsp_ingredient_id'].apply(
            lambda x:  mol_synonyms_dict[x] if x in mol_cas_dict else None)
        return new_molecular_info

    def get_molecular_info_dict(self, new_molecular_info):
        new_molecular_info.index = new_molecular_info['tcmsp_ingredient_inchikey']
        # molecular_info_dict = new_molecular_info.to_dict(orient='index')
        molecular_info_dict = new_molecular_info.to_dict()
        return molecular_info_dict

    def get_mol_inchikey_dict(self, new_molecular_info):
        mol_inchikey_dict = dict(zip(new_molecular_info['tcmsp_ingredient_id'],
                                     new_molecular_info['tcmsp_ingredient_inchikey']))
        return mol_inchikey_dict

    # replace the herb id-mol id to chinese name to molecular inchikey
    def get_herb_cn_mol_inchikey(self, tcmsp_database_dict, herb_id_cn_dict,mol_inchikey_dict ):

        Herbs_Molecules_Relationships = tcmsp_database_dict['Herbs_Molecules_Relationships']
        # replace_herb_id_mol_id
        Herbs_Molecules_Relationships['tcmsp_herb_cn_name'] = Herbs_Molecules_Relationships['tcmsp_herb_id'].apply(
            lambda x:herb_id_cn_dict[x] if x in herb_id_cn_dict else None)
        Herbs_Molecules_Relationships['mol_inchikey_dict'] = Herbs_Molecules_Relationships['tcmsp_ingredient_id'].apply(
            lambda x: mol_inchikey_dict[x] if x in mol_inchikey_dict else None)
        herb_id_mol_id_dict = dict(Herbs_Molecules_Relationships.groupby('tcmsp_herb_cn_name')['mol_inchikey_dict'].apply(list))

        return herb_id_mol_id_dict


    # add target to molecular info dict
    def get_mol_target_dict(self, tcmsp_database_dict,mol_inchikey_dict):
        M_T_Re = tcmsp_database_dict['Molecules_Targets_Relationships']
        M_T_Re['tcmsp_ingredient_inchikey'] = M_T_Re['tcmsp_ingredient_id'].apply(
            lambda x:mol_inchikey_dict[x] if x in mol_inchikey_dict else None)
        M_T_Re = M_T_Re.dropna(subset=['tcmsp_ingredient_inchikey'])
        mol_target_validated = M_T_Re[M_T_Re['validated'] == 'validated']
        mol_target_predicted = M_T_Re[M_T_Re['validated'] != 'validated']
        mol_target_validated_dict = dict(
            mol_target_validated.groupby('tcmsp_ingredient_inchikey')['tcmsp_target_id'].apply(list))
        mol_target_predicted_dict = dict(
            mol_target_predicted.groupby('tcmsp_ingredient_inchikey')['tcmsp_target_id'].apply(list))
        return mol_target_validated_dict, mol_target_predicted_dict

    def get_target_info_dict( self, tcmsp_database_dict):
        Info_Targets = tcmsp_database_dict['Info_Targets']
        Info_Targets.index = Info_Targets['tcmsp_target_id']
        target_info_dict = Info_Targets.to_dict(orient='index')
        return target_info_dict

    def extend_parent_child_info(self, parent_child_dict, child_info_dict):
        for k,c_s in parent_child_dict.items():
            parent_child_dict[k] = ({c:child_info_dict[c] for c in c_s if c in child_info_dict})
        return parent_child_dict

    # map mol target to mol info
    def map_mol_target_info(self, molecular_info_dict,  mol_target_validated_dict_extend, mol_target_predicted_dict_extend):
        for m, v in molecular_info_dict.items():
            molecular_info_dict[m].update({'target_validated': mol_target_validated_dict_extend.get(m)})
            molecular_info_dict[m].update({'target_predicted': mol_target_predicted_dict_extend.get(m)})
        return molecular_info_dict

    # add molecular to herb info

    def map_mol_herb_info(self, herb_dict, herb_id_mol_id_dict_extend):
        for h, _ in herb_dict.items():
            herb_dict[h].update({'ingredients_info': herb_id_mol_id_dict_extend.get(h)})
        return herb_dict

    # add necessary

    def prepare_whole_dict(self):
        self.tcmsp_database_dict['herb_info_merged'] = self.new_herb
        self.tcmsp_database_dict['herb_dict'] = self.herb_dict
        self.tcmsp_database_dict['herb_id_cn_dict'] = self.herb_id_cn_dict

        self.tcmsp_database_dict['molecular_info_merged'] = self.new_molecular_info
        self.tcmsp_database_dict['molecular_info_dict'] = self.molecular_info_dict
        self.tcmsp_database_dict['mol_inchikey_dict'] = self.mol_inchikey_dict

        self.tcmsp_database_dict['herb_id_mol_id_dict'] = self.herb_id_mol_id_dict

        self.tcmsp_database_dict['mol_target_validated_dict'] = self.tcmsp_database_dict
        self.tcmsp_database_dict['mol_target_predicted_dict'] = self.mol_target_predicted_dict
        self.tcmsp_database_dict['target_info_dict'] = self.target_info_dict


def save_as_sql():
    tcmsp_database = pickle.load(open('processed_data/tcmsp_database', 'rb'))
    tcmsp_database_dict = tcmsp_database.tcmsp_database_dict

    def import_way():
        for k,v in tcmsp_database_dict.items():
            v.to_csv('processed_data/tcmsp_csv/{}.csv'.format(k),index=None)
        tcmsp_database.new_herb.to_csv('processed_data/tcmsp_csv/{}.csv'.format('herb_all') ,index=None)
        tcmsp_database.new_molecular_info.to_csv('processed_data/tcmsp_csv/{}.csv'.format('molecularr_all'), index=None)

    def python_to_mysql():
        # open the mysql workbench, the panel of local host one
        # replace password to real password
        engine = create_engine('mysql://root:password@localhost/tcmsp?charset=utf8mb4')
        conn = engine.connect()
        for k,v in tcmsp_database_dict.items():
            v.to_sql(name=k, con=conn, if_exists='fail', index=False)

        tcmsp_database.new_herb.to_sql(name='new_herb', con=conn, if_exists='fail', index=False)
        new_molecular_info = tcmsp_database.new_molecular_info
        new_molecular_info = new_molecular_info.drop(columns=['tcmsp_ingredient_synonyms','tcmsp_ingredient_cas'])
        tcmsp_database.new_molecular_info.to_sql(name='new_molecular_info', con=conn, if_exists='fail', index=False)

    python_to_mysql()


def main():

    database_selected = 'tcmsp'
    path_selected = 'original_data/{}/'.format(database_selected)
    tcmsp_database = load_tcmsp_database(path_selected)
    with(open('processed_data/tcmsp_database','wb')) as handle:
        pickle.dump(tcmsp_database, handle)



    # import pickle
    # tcmsp_database = pickle.load(open('processed_data/tcmsp_database','rb'))



