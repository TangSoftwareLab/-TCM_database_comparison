import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from math import pi
import pickle
import ast
import seaborn as sns
from process.pyvenn import venn
from process.mysql_setting.connections import query_mysql_pd, save_to_mysql_pd
import asyncio
import pyecharts.options as opts
from pyecharts.charts import Tree
from pyecharts.charts import Sankey
import matplotlib.gridspec as gridspe
import matplotlib.pyplot as plt
from PIL import Image


def prepare_union_value_(value_dict):
    all_herbs = set()
    for k, v in value_dict.items():
        all_herbs.update(v)
    over_pd = pd.DataFrame(columns=list(value_dict.keys()), index=list(all_herbs))
    over_pd['name'] = over_pd.index
    for k, v in value_dict.items():
        over_pd[k] = over_pd['name'].apply(lambda x: 1 if x in list(v) else 0)
    over_pd = over_pd.drop(columns=['name'])
    return over_pd


def plot_radar_2():
    def make_spider(row, title, color):
        df_new = df.loc[[row],:].dropna(axis=1)
        # number of variable
        categories = list(df_new.columns)[1:]
        N = len(categories)

        # What will be the angle of each axis in the plot? (we divide the plot / number of variable)
        angles = [n / float(N) * 2 * pi for n in range(N)]
        angles += angles[:1]

        # Initialise the spider plot
        ax = plt.subplot(3, 3, row + 1, polar=True, )

        # If you want the first axis to be on top:
        ax.set_theta_offset(pi / 2)
        ax.set_theta_direction(-1)

        # Draw one axe per variable + add labels labels yet
        plt.xticks(angles[:-1], categories, color='black', size=8)

        # Draw ylabels
        ax.set_rlabel_position(0)
        plt.yticks(color="black", size=8)

        # Ind1
        values = df_new.drop(['DATABASE'], axis=1).values.flatten().tolist()
        values += values[:1]
        ax.plot(angles, values, color=color, linewidth=2, linestyle='solid')
        ax.fill(angles, values, color=color, alpha=0.4)

        # Add a title
        plt.title(title, size=10, y=1.15)

    df = pd.read_csv("result/statistic_database.csv")
    change_name_dict = {
        'No of herbs': 'Herb',
                           'No of herbs with ingredient': 'Herb with ingredients',
                           'No of ingredient': 'Ingredient',
                           'No of target': 'Target',
                           'No of disease': 'Disease',
                           'No of ingredients with struture info': 'Ingredient with structure',
                           'No of ingredients with target': 'Ingredient with target',
                           'ingredient_target pairs': 'Ingredient-Target associations',
                           'herb_ingredient_pair': 'Herb-Ingredient pairs',
                            'No of formulae':'Formulae'}
    df['DATABASE'] = df['DATABASE'].apply(lambda x: change_name_dict[x])

    # order the types of annoataion by specidic order

    order_dict = { 'Herb':1,
                   'Herb with ingredients':2,
                   'Herb-Ingredient pairs':3,
                   'Ingredient':4,
                   'Ingredient with structure': 5,
                   'Ingredient with target': 6,
                    'Target':7,
                   'Ingredient-Target associations':8,
                    'Disease':9,
                   'Formulae':10}
    df['order'] = df['DATABASE'].apply(lambda x: order_dict[x])
    df = df.sort_values(by='order', axis=0, ascending=True)
    df = df.drop(columns='order')
    #
    # ------- PART 2: Apply to all individuals
    # initialize the figure
    my_dpi = 500
    plt.figure(figsize=(5000 / my_dpi, 5000 / my_dpi), dpi=my_dpi)

    # Create a color palette:
    my_palette = plt.cm.get_cmap("Set2", len(df.index))

    # Loop to plot

    for row in range(0, 9):
        make_spider(row=row, title=df['DATABASE'][row], color=my_palette(row))

    plt.tight_layout()

    # save out
    plt.savefig('result/figure/figure 1.pdf', format='pdf')
    plt.savefig('result/figure/figure 1.png', dpi=300)
    plt.savefig('result/figure/figure 1.svg', dpi=300, format='svg')


def get_formulae_properties():
    formulae_all_dict = {'etcm': 'formulae_info',
                     'tcm_herb': 'herb_disease_info',
                     'tcm_id': 'formulae_detail',
                     'tcmid': 'prescription',
                     'tcmio': 'prescription'
                     }
    formulae_properties_dict = {}
    formulae_pd_dict = {}
    for d, v in formulae_all_dict.items():
        database_name = d
        table = v
        sql_formu = """SELECT * FROM {};""".format(table)
        pd_result_formu = query_mysql_pd(sql_string=sql_formu, database_name=database_name)
        formulae_pd_dict[d] = pd_result_formu
        formulae_properties_dict[d] = list(pd_result_formu.columns)

    return formulae_properties_dict, formulae_pd_dict


def get_herb_properties():
    herb_all_dict = {'etcm': 'herb_info',
                     'symmap': 'smhb',
                     'tcm_herb': 'herb_herb_info',
                     'tcm_id': 'tcm_herb_new',
                     'tcm_mesh': 'herb_info',
                     'tcmid': 'herb_info_detail',
                     'tcmio': 'tcm',
                     'tcmsp': 'new_herb',
                     'tm_mc': 'herb'
                     }

    herb_properties_dict = {}
    herb_pd_dict = {}
    for d, v in herb_all_dict.items():
        database_name = d
        table = v
        sql_herb = """SELECT * FROM {};""".format(table)
        pd_result_herb = query_mysql_pd(sql_string=sql_herb, database_name=database_name)
        herb_pd_dict[d] = pd_result_herb
        herb_properties_dict[d] = list(pd_result_herb.columns)

    return herb_properties_dict, herb_pd_dict


def get_herb_overlap():
    herb_all_dict = {'etcm': ('herb_info', 'Herb Name in Chinese'),
                     'symmap': ('smhb', 'Chinese_name'),
                     'tcm_herb': ('herb_herb_info', 'Herb_cn_name'),
                     'tcm_id': ('tcm_herb_new', '中文名'),
                     'tcm_mesh': ('herb_info', 'chinese name_processed'),
                     'tcmid': ('herb_info_detail', 'Chinese Name'),
                     'tcmio': ('tcm', 'chinese_name'),
                     'tcmsp': ('new_herb', 'tcmsp_herb_cn_name'),
                     'tm_mc': ('herb', 'CHINESE')
                     }

    database_all = list(herb_all_dict.keys())

    herb_dict = {}
    herb_pd_dict = {}

    for d, v in herb_all_dict.items():
        database_name = d
        table, col = v[0], v[1]
        if d in database_all:
            sql_herb = """SELECT * FROM {};""".format(table)
            pd_result_herb = query_mysql_pd(sql_string=sql_herb, database_name=database_name)
            herb_pd_dict[d] = pd_result_herb
            herbs = list(pd_result_herb[col].dropna())
            herb_dict[d] = list(set(herbs))

    # Prepare file to o, 1. save file to R for upset, prep
    herb_over_pd = prepare_union_value_(herb_dict)
    #herb_over_pd.to_csv('result/table/herb_overlap_new.csv')

    # plot figure by venne
    def plot_herb_venne(herb_dict):
        database_selelcted = ['etcm', 'symmap', 'tcm_herb', 'tcm_id', 'tcmid', 'tcmsp']
        herb_dict = {herb_dict[d] for d in database_selelcted}
        labels = venn.get_labels([v for k, v in herb_dict.items()], fill=['number', 'logic'])
        names_sum = [':'.join([k, str(len(v))]) for k, v in herb_dict.items()]
        venn.venn6(labels, names=names_sum)
        # fig.show()
        plt.savefig('result/figure/herb_overlap.png')
    return herb_dict, herb_pd_dict, herb_over_pd

def get_ingredients_properties():
    ingre_all_dict = {'etcm': ('ingredient_info', 'External Link to PubChem'),
                     'symmap': ('smit', 'PubChem_id'),
                     'tcm_herb': ('herb_ingredient_info', 'PubChem_id'),
                     'tcm_id': ('tcm_ingredients_all', 'pubchem_cid', 'canonical_smiles', 'standard_inchi_key'),
                     'tcm_mesh': ('tcm_compounds', 'pubchem_id', 'CAN string'),
                     'tcmid': ('ingredients_info', 'cid', 'smiles'),
                     'tcmio': ('ingredient', 'smiles', 'inchi', 'inchikey'),
                     'tcmsp': ('new_molecular_info',
                               'tcmsp_ingredient_pubChem_Cid',
                               'tcmsp_ingredient_inchikey',
                               'tcmsp_ingredient_isosmiles'),
                    'tm_mc': ('ingredient_info', 'CID')
                     }

    ingre_properties_dict = {}
    ingre_pd_dict = {}
    for d, v in ingre_all_dict.items():
        database_name = d
        table = v[0]
        sql_herb = """SELECT * FROM {};""".format(table)
        pd_result_herb = query_mysql_pd(sql_string=sql_herb, database_name=database_name)
        ingre_pd_dict[d] = pd_result_herb
        ingre_properties_dict[d] = list(pd_result_herb.columns)

    return ingre_properties_dict, ingre_pd_dict


def get_ingredient_overlap():
    # 'tcmio': ('ingredient', 'smiles', 'inchi', 'inchikey'),
    ingre_all_dict = {'etcm': ('ingredient_info', 'External Link to PubChem'),
                      'symmap': ('smit', 'PubChem_id'),
                      'tcm_herb': ('herb_ingredient_info', 'PubChem_id'),
                      'tcm_id': ('tcm_ingredients_all', 'pubchem_cid', 'canonical_smiles', 'standard_inchi_key'),
                      'tcm_mesh': ('tcm_compounds', 'pubchem_id', 'CAN string'),
                      'tcmid': ('ingredients_info', 'cid', 'smiles'),
                      'tcmsp': ('new_molecular_info',
                                'tcmsp_ingredient_pubChem_Cid',
                                'tcmsp_ingredient_inchikey',
                                'tcmsp_ingredient_isosmiles'),
                      'tm_mc': ('ingredient_info', 'CID')
                      }

    database_all = list(ingre_all_dict.keys())

    ingre_dict = {}
    ingre_pd_dict = {}
    for d, v in ingre_all_dict.items():
        database_name = d
        table, col = v[0], v[1]
        if d in database_all:
            sql_ingre = """SELECT * FROM {};""".format(table)
            pd_result_herb = query_mysql_pd(sql_string=sql_ingre, database_name=database_name)
            pd_result_herb = pd_result_herb[~pd_result_herb[col].isin(['Not Available', ''])]
            ingre_pd_dict[d] = pd_result_herb
            ingredients = list(pd_result_herb[col].dropna().astype(int))
            ingre_dict[d] = list(set(ingredients))

    # Prepare file to o, 1. save file to R for upset, prep
    ingre_over_pd = prepare_union_value_(ingre_dict)
    # ingre_over_pd.to_csv('result/table/ingredient_overlap.csv')

    # plot figure by venne
    def plot_ingre_venne(ingre_dict):
        database_selelcted = ['etcm', 'symmap', 'tcm_herb', 'tcm_id', 'tcmid', 'tcmsp']
        ingre_dict = {ingre_dict[d] for d in database_selelcted}
        labels = venn.get_labels([v for k, v in ingre_dict.items()], fill=['number', 'logic'])
        names_sum = [':'.join([k, str(len(v))]) for k, v in ingre_dict.items()]
        venn.venn6(labels, names=names_sum)
        # fig.show()
        plt.savefig('result/figure/ingre_overlap.png')
    return ingre_dict, ingre_pd_dict, ingre_over_pd

def get_adme_properties():
    ingre_pro = get_ingredients_properties()
    clean_tree_list = []
    for d, p in ingre_pro.items():
        print(d)
        if d == 'tcmsp':
            p = [p_i[17:] for p_i in p]
        if d == 'etcm':
            p = [p_i if 'ADMET' not in p_i else p_i[5] for p_i in p]
        clean_tree_list.append({d: detect_annotation(p)})
    return d


def detect_annotation(pro_list):
    structure = ['struc', 'smil', ' formula', 'can', 'inchi']
    annotation = ['name', 'alia', 'synony']
    links = ['_id', 'pubchem', 'cid', 'chem', 'cas']
    term_dict = {'Structure': structure,
                 'Annotation': annotation,
                 'Links': links,
                 'ADMET': structure+annotation+links+['references', 'diseases', 'formula', 'ingredient', 'weight']}

    child_dict = []
    for type_term, terms in term_dict.items():
        type_term_list = []
        if type_term != 'ADMET':
            for p in pro_list:
                if any(t in p.lower() for t in terms):
                    type_term_list.append({'name': p})
        else:
            for p in pro_list:
                if all(t.lower() not in p.lower() for t in terms):
                    type_term_list.append({'name': p})

        child_dict.append({"children": type_term_list, 'name': type_term})

    return child_dict


def prepared_ingre_anno_pd():
    ingre_pro = get_ingredients_properties()

    database_name_dict = {'etcm': 'ETCM',
                          'symmap': 'SymMap',
                          'tcm_herb':'HERB',
                         'tcm_id':'TCM-ID',
                         'tcm_mesh':'TCM-Mesh',
                         'tcmid':'TCMID',
                         'tcmio':'TCMIO',
                         'tcmsp':'TCMSP',
                         'tm_mc':'TM-MC'}

    original_pair_list = []
    for d, p in ingre_pro[0].items():
        db_record = list(zip([database_name_dict[d]]*len(p), p))
        db_record = [list(i) for i in db_record]
        original_pair_list += db_record
    db_record_pd = pd.DataFrame(original_pair_list, columns=['Database', 'Records'])
    db_record_pd.to_csv('result/database_anno_table.csv', index=None)

def plot_physical_adme_tree():
    ingre_pro = get_ingredients_properties()

    database_name_dict = {'etcm': 'ETCM',
                          'symmap': 'SymMap',
                          'tcm_herb':'HERB',
                         'tcm_id':'TCM-ID',
                         'tcm_mesh':'TCM-Mesh',
                         'tcmid':'TCMID',
                         'tcmio':'TCMIO',
                         'tcmsp':'TCMSP',
                         'tm_mc':'TM-MC'}
    clean_tree_list = []


    for d, p in ingre_pro[0].items():
        print(d)
        if d == 'tcmsp':
            p = [p_i[17:] for p_i in p]
        if d == 'etcm':
            p = [p_i if 'ADMET' not in p_i else p_i[6:] for p_i in p ]
        clean_tree_list.append({"children": detect_annotation(p), 'name': database_name_dict.get(d)})
    data = {"children": clean_tree_list, 'name': 'TCM_database'}

    (
        Tree(init_opts=opts.InitOpts(width="2000px", height="1200px"))
            .add(
            series_name="",
            data=[data],
            pos_top='18%',
            pos_bottom='14%',
            layout='radial',
            symbol='emptyCircle',
            symbol_size=7,
            initial_tree_depth=4,
            is_expand_and_collapse=True,
            label_opts=opts.LabelOpts(position="left"),
        )
            .set_global_opts(
            tooltip_opts=opts.TooltipOpts(trigger="item", trigger_on="mousemove")
        )
            .render("result/figure/radial_tree.html")
    )

def plot_physical_adme_tree_v2():
    ingre_pro = pd.read_csv('result/database_anno_table_modified.csv')

    first_dict = ingre_pro.groupby(['Database'])[['Claasification', 'Records']].apply(
        lambda x: x.groupby(['Claasification'])['Records'].apply(list).to_dict())
    clean_tree_list_1 = []
    for d, c in first_dict.items():
        print(d)
        clean_tree_list_2 = []
        for c2,r in c.items():
            clean_tree_list_3 = []
            for r2 in r:
                clean_tree_list_3.append({"children": [], 'name': r2})
            clean_tree_list_2.append({"children": clean_tree_list_3, 'name': c2})
        clean_tree_list_1.append({"children": clean_tree_list_2, 'name': d})
    data = {"children": clean_tree_list_1, 'name': 'TCM_database'}

    (
        Tree(init_opts=opts.InitOpts(width="1200px", height="1200px"))
            .add(
            series_name="",
            data=[data],
            pos_top='5%',
            pos_bottom='5%',
            pos_left='8%',
            pos_right='7%',
            layout='radial',
            symbol='emptyCircle',
            symbol_size=10,
            initial_tree_depth=5,
            is_expand_and_collapse=True,
            label_opts=opts.LabelOpts(position='top', font_size=14,
                                      font_family='Arial', color='black',
                                      font_weight='normal'),
        )
            .set_global_opts(
            tooltip_opts=opts.TooltipOpts(trigger="item", trigger_on="mousemove")
        )
            .render("result/figure/ingre_anno_tree_modified.html")
    )

def get_target_properties():
    target_all_dict = {'etcm': 'herb_target',
                         'symmap': 'smtt',
                         'tcm_herb': 'herb_target_info',
                         'tcm_id': 'cp_targets',
                         'tcm_mesh': 'protein_gene_links',
                         'tcmid': 'stitch_interaction_all',
                         'tcmio': 'target',
                         'tcmsp': 'info_targets'
                         }

    target_properties_dict = {}
    target_pd_dict = {}
    for d, v in target_all_dict.items():
        database_name = d
        table = v
        sql_target = """SELECT * FROM {};""".format(table)
        pd_result_target = query_mysql_pd(sql_string=sql_target, database_name=database_name)
        target_pd_dict[d] = pd_result_target
        target_properties_dict[d] = list(pd_result_target.columns)
    return target_properties_dict, target_pd_dict


def plot_db_links():
    node_pd = pd.read_excel('relationship.xlsx', sheet_name='sy_nodes')
    nodes = [{i: j} for i, j in zip(node_pd['type'], node_pd['db'])]

    link_pd = pd.read_excel('relationship.xlsx', sheet_name='sy_links')
    links =link_pd.to_dict('records')

    c = (
        Sankey(init_opts=opts.InitOpts(width="1600px", height="800px"))
            .add(
            "sankey",
            nodes,
            links,
            pos_top='5%',
            pos_bottom='5%',
            pos_left='15%',
            pos_right='7%',
            focus_node_adjacency=True,
            itemstyle_opts=opts.ItemStyleOpts(border_width=0.2, border_color="black"),
            linestyle_opt=opts.LineStyleOpts(color='source', curve=0.1, opacity=0.2),
            tooltip_opts=opts.TooltipOpts(trigger_on="mousemove"),
            label_opts=opts.LabelOpts(position="left", font_size=14,
                                      font_family='Arial', color='black',
                                      font_weight='normal'),

        )
            .set_global_opts(title_opts=opts.TitleOpts(title=""))
            .render("figure/sankey_database.html")
    )


def get_herb_ingre_pairs():
    h_i_all_dict = {
        'etcm': 'herb_ingredient',
        'symmap': 'smit_smhb',
        'tcm_id': 'tcm_plant_ingredient_pairs_allingredients',
        'tcm_mesh': 'herb_ingredients',
        'tcmid': 'herb_ingre_new',
        'tcmsp': 'herbs_molecules_relationships',
        'tm_mc': 'herb_ingredient_info'
    }

    h_i_pd_dict = {}
    for d, v in h_i_all_dict.items():
        database_name = d
        table = v
        sql_h_i = """SELECT * FROM {};""".format(table)
        pd_result_h_i = query_mysql_pd(sql_string=sql_h_i, database_name=database_name)
        if d == 'tcmsp':
            pd_result_h_i = pd_result_h_i.drop(columns='tcmsp_herb_cn_name')
        h_i_pd_dict[d] = pd_result_h_i
    return h_i_pd_dict


def get_herb_ingre_pairs_detail():

    herb_all_dict = {'etcm': ('herb_info', 'Herb Name in Chinese'),
                     'symmap': ('smhb', 'Chinese_name'),
                     'tcm_herb': ('herb_herb_info', 'Herb_cn_name'),
                     'tcm_id': ('tcm_herb_new', '中文名'),
                     'tcm_mesh': ('herb_info', 'chinese name_processed'),
                     'tcmid': ('herb_info_detail', 'Chinese Name'),
                     'tcmio': ('tcm', 'chinese_name'),
                     'tcmsp': ('new_herb', 'tcmsp_herb_cn_name'),
                     'tm_mc': ('herb', 'CHINESE')
                     }


    ingre_all_dict = {'etcm': ('ingredient_info', 'External Link to PubChem'),
                      'symmap': ('smit', 'PubChem_id'),
                      'tcm_herb': ('herb_ingredient_info', 'PubChem_id'),
                      'tcm_id': ('tcm_ingredients_all', 'pubchem_cid', 'canonical_smiles', 'standard_inchi_key'),
                      'tcm_mesh': ('tcm_compounds', 'pubchem_id', 'CAN string'),
                      'tcmid': ('ingredients_info', 'cid', 'smiles'),
                      'tcmio': ('ingredient', 'smiles', 'inchi', 'inchikey'),
                      'tcmsp': ('new_molecular_info',
                                'tcmsp_ingredient_pubChem_Cid',
                                'tcmsp_ingredient_inchikey',
                                'tcmsp_ingredient_isosmiles'),
                      'tm_mc': ('ingredient_info', 'CID')
                      }

    herb_ingre_all_dict = {
                    'etcm': {'table': 'herb_ingredient',
                            'herb': 'herb_id',
                            'herb_ingre': {'herb': 'herb_id',
                                           'ingre': 'ingre_id'},
                            'ingre': 'Ingredient_id'
                             },
                     'symmap': {'table': 'smit_smhb',
                                'herb': 'Herb_id',
                                'herb_ingre': {'herb': 'Herb_id',
                                               'ingre': 'MOL_id'},
                                'ingre': 'MOL_id'
                                },
                     'tcm_id': {
                             'whole_table': 'tcm_plant_ingredient_pairs_allingredients'
                                },
                     'tcm_mesh': {'table': 'herb_ingredients',
                                    'herb': 'pinyin name',
                                    'herb_ingre': {'herb': 'herb',
                                                   'ingre': 'pubchem_id'},
                                    'ingre': 'pubchem_id'
                                  },
                     'tcmid':  {'whole_table': 'herb_ingre_new'
                                },
                     'tcmsp': {'table': 'herbs_molecules_relationships',
                                'herb': 'tcmsp_herb_id',
                                'herb_ingre': {'herb': 'tcmsp_herb_id',
                                               'ingre': 'tcmsp_ingredient_id'
                                               },
                                'ingre': 'tcmsp_ingredient_id'},
                    'tm_mc': {'whole_table': 'herb_ingredient_info'
                              }
                    }

    # get data from mysql
    database_selelcted = ['etcm', 'symmap', 'tcm_herb', 'tcm_id', 'tcmid', 'tcmsp']
    herb_ingre_pd = get_herb_ingre_pairs()
    herb_pro, herb_pd = get_herb_properties()
    ingre_pro, ingre_pd = get_ingredients_properties()

    # prepare herb ingredients dict
    herb_ingre_result_dict = {}
    db_herb_ingre_dict = {}
    herb_ingre_result_pd = pd.DataFrame(columns=['Herb', 'Ingredient'])
    for d in herb_ingre_all_dict.keys():
        print(d)
        herb_to_col = herb_all_dict[d][1]
        ingre_to_col = ingre_all_dict[d][1]
        if 'whole_table' in herb_ingre_all_dict[d]:
            pair_pd_all = herb_ingre_pd[d]
        else:
            h_i_pd = herb_ingre_pd[d]
            # prepare the herb pd
            def pre_single_pd(h_i_pd, single_data_pd, data_to_col, herb_ingre_all_dict, type ):
                data_pd_one = single_data_pd[d]
                data_pd_one = data_pd_one.astype(str)
                data_pd_key_col = herb_ingre_all_dict[d][type]
                data_ingre_h_key_col = herb_ingre_all_dict[d]['herb_ingre'][type]

                data_pd_one = data_pd_one.dropna(how='any',
                                                 subset=[data_pd_key_col, data_to_col],
                                                 axis=0).drop_duplicates()
                if 'id' in data_ingre_h_key_col and d != 'tcmsp':
                    h_i_pd[data_ingre_h_key_col] = h_i_pd[data_ingre_h_key_col].astype(int)
                elif d == 'tcmsp':
                    h_i_pd[data_ingre_h_key_col] = h_i_pd[data_ingre_h_key_col].astype(str)

                if 'id' in data_pd_key_col and d != 'tcmsp':
                    data_pd_one[data_pd_key_col] = data_pd_one[data_pd_key_col].astype(int)
                elif d == 'tcmsp':
                    data_pd_one[data_pd_key_col] = data_pd_one[data_pd_key_col].astype(str)


                pair_pd_all = pd.merge(h_i_pd,
                                       data_pd_one,
                                       left_on=data_ingre_h_key_col,
                                       right_on=data_pd_key_col,
                                       how='left')
                return pair_pd_all

            pair_pd_all = pre_single_pd(h_i_pd, herb_pd, herb_to_col, herb_ingre_all_dict, 'herb')
            pair_pd_all = pre_single_pd(pair_pd_all, ingre_pd, ingre_to_col, herb_ingre_all_dict, 'ingre')
            #save_to_mysql_pd(pair_pd_all, database_name=d, saved_name='all_herb_ingre_detail')

        # further process each dataframe from TCM database
        pair_pd_all = pair_pd_all[~pair_pd_all[ingre_to_col].isin([None, 'nan', '', np.nan, 'Not Available', 'None'])]
        pair_pd_all = pair_pd_all[~pair_pd_all[herb_to_col].isin([None, 'nan', '', np.nan, 'Not Available', 'None'])]
        pair_pd_all = pair_pd_all[pair_pd_all[ingre_to_col].notnull()]
        pair_pd_all = pair_pd_all[pair_pd_all[herb_to_col].notnull()]
        pair_pd_all[ingre_to_col] = pair_pd_all[ingre_to_col].astype(float).astype(int)
        pair_pd_all = pair_pd_all[[herb_to_col, ingre_to_col]].drop_duplicates()

        # prepare dict
        pair_dict = dict(pair_pd_all.groupby(herb_to_col)[ingre_to_col].apply(list))
        herb_ingre_result_dict[d] = pair_dict

        #herb_ingre_result_dict[d] = pair_pd_all
        # merge all the herb ingre pairs
        pair_pd_all.columns = ['Herb', 'Ingredient']
        herb_ingre_result_pd = pd.concat([herb_ingre_result_pd, pair_pd_all], axis=0)
        herb_ingre_result_pd = herb_ingre_result_pd.drop_duplicates()
        db_herb_ingre_dict[d] = list(herb_ingre_result_pd['Herb'] + '_'+ herb_ingre_result_pd['Ingredient'].astype(str))
    # prepare database herb_ingre_dict
    #herb_ingre_overlap_pd = prepare_union_value_(db_herb_ingre_dict)
    herb_ingre_overlap_pd = None
    return herb_ingre_result_dict, herb_ingre_result_pd, herb_ingre_overlap_pd


def get_herb_ingre_pairs_correlartion():
    '''
    Firstly, we calculate the number of overlapped ingredients in each common herbs as well as the union number of herbs pairs
    Than, we compare the numbers by overlap/ union for each herbs, namely jacard index.
     Also, we want to get the general overlap by the averaged mean jacard among all the common herbs.
     Other other hand, we can compare overlap with the number of ingredients of this commmon herbs in one TCM database as the baseline.
     We can also get the sum

    '''
    def herb_cor(overlap_herb, d_1, d_2, herb_ingre_china_cid):
        jacard_all = []
        rate_all = []
        overlap_all = []
        for h in overlap_herb:
            union_l = len(set(herb_ingre_china_cid[d_1][h]) & set(herb_ingre_china_cid[d_2][h]))
            overlap = len(set(herb_ingre_china_cid[d_1][h]) | set(herb_ingre_china_cid[d_2][h]))
            overlap_all.append(overlap)
            jacard_all.append(union_l/overlap)
            rate_all.append(union_l/len(set(herb_ingre_china_cid[d_1][h])))

        jacard_mean = np.mean(jacard_all)
        rate_mean = np.mean(rate_all)
        overlap_mean = np.mean(overlap_all)
        return jacard_all, rate_all, overlap_all, jacard_mean, rate_mean, overlap_mean, len(overlap_herb)


    def plot_jarcard(cor_pd_list, save_name):

        cmap = sns.diverging_palette(220, 10, as_cmap=True)
        fig = plt.figure(figsize=(16, 8))

        sns.set(font='Arial', style="white", context="paper", font_scale=1.2)
        n_dict = {0: 'A', 1: 'B'}

        for i, cor_pd in enumerate(cor_pd_list):
            ax1 = fig.add_subplot(1, 2, i+1)
            cor_pd = cor_pd.astype(float)
            sns.heatmap(cor_pd,
                             annot=True,
                             linewidths=.5,
                             cmap=cmap,
                             square=True,
                             cbar_kws=dict(use_gridspec=False,
                                           shrink=.7,
                                           location='right'),

                             cbar=True
                             )
            ax1.set_title(n_dict[i], loc='left')

        plt.savefig('result/figure/herb_ingre_overlap.png')


    def plot_density(cor_pd_list, save_name):

        sns.set(font='Arial', style="white", context="paper", font_scale=2.4)

        for i, cor_pd in enumerate(cor_pd_list):
            g = sns.FacetGrid(cor_pd,
                              row='d1',
                              col='d2',
                              margin_titles=True,
                              despine=False,
                              gridspec_kws={"wspace": 0.1, 'hspace': 0.1})
            g.map_dataframe(sns.histplot,
                            "value",
                            palette="Set2")

            plt.savefig('result/figure/herb_ingre_{}.png'.format(save_name[i]))

    # plot density
    def plot_boxbar(pd_melt,col_value, save_name, out_type):

        pd_melt = pd_melt.sort_values(by=['d_1', 'd_2'])
        fig = plt.figure(figsize=(8, 8))

        sns.set(font='Arial', style="whitegrid", context="paper", font_scale=2.4)

        g = sns.FacetGrid(pd_melt,
                          row='d_1',
                          col='d_2',
                          margin_titles=True,
                          despine=False, gridspec_kws={"wspace": 0.1, 'hspace': 0.1})

        g.map_dataframe(sns.boxplot,
                        col_value,
                        palette="Set2")
        g.set_axis_labels("", col_value)
        g.fig.subplots_adjust(wspace=0, hspace=0)
        plt.tight_layout()
        if out_type == 'save_figure':
            plt.savefig('result/figure/{}.png'.format(save_name), dpi=300)
            plt.savefig('result/figure/{}.pdf'.format(save_name), format='pdf')
            plt.savefig('result/figure/{}.svg'.format(save_name), dpi=300, format='svg')

            # Load this image into PIL
            png2 = Image.open('result/figure/{}.png'.format(save_name))

            # Save as TIFF
            png2.save('result/figure/{}.tiff'.format(save_name), format='tiff', dpi=(300, 300))
        elif out_type == 'plot_figure':
            plt.show()

    # Prepare the result data
    def prepare_data():
        herb_ingre_china_cid = get_herb_ingre_pairs_detail()

        databases = list(herb_ingre_china_cid.keys())
        cor_list = []
        for d_1 in databases:
            for d_2 in databases:
                overlap_herb = set(herb_ingre_china_cid[d_1]) & set(herb_ingre_china_cid[d_2])
                jacard_all, rate_all, overlap_all, jacard_mean, rate_mean, overlap_mean,overlap_herb = herb_cor(overlap_herb,
                                                                                                                d_1,
                                                                                                                d_2,
                                                                                                                herb_ingre_china_cid)
                cor_list.append([d_1, d_2, jacard_all, rate_all,
                                 overlap_all, jacard_mean,
                                 rate_mean, overlap_mean,
                                 overlap_herb])

        # extend to dataframe
        col_name = ['d_1', 'd_2', 'jacard_all',
                    'rate_all', 'overlap_all',
                    'jacard_mean', 'rate_mean',
                    'overlap_mean', 'overlap_herb']
        cor_pd = pd.DataFrame(cor_list, columns=col_name)
        return cor_pd

    # plot box for overlap figure
    def plot_tcm_box():
        for i in ['jacard_all', 'rate_all', 'overlap_all']:
            cor_pd_extend = cor_pd[['d_1', 'd_2', i]]
            cor_pd_extend = cor_pd_extend.explode(i, ignore_index=True)
            # cor_pd_extend.loc[(cor_pd_extend['d_1'] == cor_pd_extend['d_2']), i] = 0
            #cor_pd_extend = cor_pd_extend[(cor_pd_extend['d_1'] != 'tcm_id') & (cor_pd_extend['d_2'] != 'tcm_id')]
            grouped = cor_pd_extend.groupby(['d_1', 'd_2']).agg({i: 'min', i: 'max', i: 'mean'})
            grouped.columns = grouped.columns.droplevel(level=0)
            plot_boxbar(cor_pd_extend, i, i, 'save_figure')

    # save correlation
    cor_pd = prepare_data()

    for i in ['jacard_mean', 'rate_mean', 'overlap_mean', 'overlap_herb']:
        cor_pd_extend = cor_pd[['d_1', 'd_2', i]]
        cor_pd_extend = cor_pd_extend.pivot_table(index='d_1', columns='d_2', values=i)
        cor_pd_extend.to_csv('result/table/cor_{}.csv'.format(i))



    # data_list = [cor_rate,
    #              cor_jacard,
    #              cor_rate_extend,
    #              cor_jacard_extend]
    # save_name = ['cor_rate',
    #              'cor_jacard',
    #              'cor_rate_extend',
    #              'cor_jacard_extend']
    # plot_jarcard(data_list[0:2], save_name[0:2] )
    # plot_density(data_list[2:], save_name[2:])



def ADME_correlation():
    pass


def main():
    # plot_radar_2()
    # get_herb_overlap()
    # formulae_properties_dict, formulae_pd_dict = get_formulae_properties()
    # herb_pro, herb_pd = get_herb_properties()
    # ingre_pro, ingre_pd = get_ingredients_properties()
    # target_pro, target_pd = get_target_properties()
    # get_ingredient_overlap()
    # plot_physical_adme_tree()
    plot_db_links()

    # herb_ingre_result_dict = get_herb_ingre_pairs_detail()
    # pickle.dump(herb_ingre_result_dict, open('result/herb_ingre_china_cid.dict', 'wb'))
    # herb_ingre_china_cid  = pickle.load(open('result/herb_ingre_china_cid.dict', 'rb'))

    # get_herb_ingre_pairs_correlartion()
    #plot_physical_adme_tree_v2()

