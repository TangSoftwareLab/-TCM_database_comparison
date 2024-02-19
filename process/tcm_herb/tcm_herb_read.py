import pandas as pd
from sqlalchemy import create_engine
import pandas as pd
import io
import requests
import os
from bs4 import BeautifulSoup
from process.mysql_setting.connections import query_mysql_pd, save_to_mysql_pd



# read files from local folder
def read_herb_files(path_selected):
    database_dict = {}
    for file in os.listdir(path_selected):
        name = file.split('.')[0]
        data = pd.read_csv(path_selected + file, sep='\t')
        database_dict[name] = data
    return database_dict


def save_herb_ingre_mysql():
    ingre_pd = pd.read_csv('original_data/tcm_herb/HERB_ingredient_info.txt', sep='\t')
    col_wrong = list(ingre_pd.columns)
    ingre_pd.columns = col_wrong[1:] + [col_wrong[0]]
    save_to_mysql_pd(ingre_pd, database_name='tcm_herb', saved_name='herb_ingredient_info')

def tcm_mesh_save_to_mysql(path_selected):

    ## first open mysql the local host, than create database tcm_herb, than click right to eit sceme, to utf8mb4

    # open the mysql workbench, the panel of local host one
    engine = create_engine('mysql://root:Mqxs320321wyy@localhost/tcm_herb?charset=utf8mb4')
    conn = engine.connect()
    database_dict = read_herb_files(path_selected)
    for k, v in database_dict.items():
        if k != 'herb_ingredient_info':
            try:
                v.to_sql(name=k, con=conn, if_exists='fail', index=False)
            except:
                continue
    save_herb_ingre_mysql()


def extract_web():
    agent = 'Mozilla/5.0 (iPhone; CPU iPhone OS 7_1_2 like Mac OS X) App leWebKit/537.51.2 (KHTML, like Gecko) Version/7.0 Mobile/11D257 Safari/9537.53'
    headers = {'User-Agent': agent,
               }
    session = requests.Session()
    req = session.get(url='http://herb.ac.cn/Detail/?v=HERB001282&label=Herb', headers = headers)

    content = req.content
    bsogj = BeautifulSoup(req)
    from selenium import webdriver
    from selenium.webdriver.common.keys import Keys

    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    url = "http://herb.ac.cn/Detail/?v=HERB001282&label=Herb"
    driver = webdriver.PhantomJS('C:\\hyapp\\phantomjs-2.1.1-windows\\bin\\phantomjs.exe')
    driver.get(url)
    span_element = driver.find_element_by_css_selector("layout-container___3nzkB")
    span_element.text
    #TODO： extract herb-ingredient pairs, herb-disease pairs




def main():
    # download_data()
    database_selected = 'tcm_herb'
    path_selected = 'original_data/{}/'.format(database_selected)
    tcm_mesh_save_to_mysql(path_selected)

