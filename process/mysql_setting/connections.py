import pandas as pd
from sqlalchemy import create_engine
import MySQLdb
import MySQLdb.cursors

def query_mysql_pd(sql_string, database_name):
    #  replace the user name and password
    db_2 = MySQLdb.connect(host="xx.xx.xx.xx", user="xx", passwd="xxxx", db=database_name, charset='utf8mb4',
                           cursorclass=MySQLdb.cursors.DictCursor)
    c = db_2.cursor(cursorclass=MySQLdb.cursors.DictCursor)

    c.execute(sql_string)
    inchey_used_2 = c.fetchall()
    pd_result = pd.DataFrame(list(inchey_used_2))
    db_2.close()
    return pd_result


def save_to_mysql_pd(pd_result, database_name, saved_name):
    # replace the passowrd to the real password
    engine = create_engine('mysql://root:password@localhost/{}?charset=utf8mb4'.format(database_name))
    conn = engine.connect()
    pd_result.to_sql(name=saved_name, con=conn, if_exists='fail', index=False)
    conn.close()