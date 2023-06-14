import psycopg2
import pandas as pd
import traceback
import numpy as np
# insert data from csv file into dataframe.
# working directory for csv file: type "pwd" in Azure Data Studio or Linux
# working directory in Windows c:\users\username

df = pd.read_excel("C:\Dev_backup\Projetos\Python\Python_meds\Insert_BD\lista_anvisa.xlsx", header=0)
df = pd.DataFrame(df)

# Some other example server values are
# server = 'localhost\sqlexpress' # for a named instance
# server = 'myserver,port' # to specify an alternate port
print('Iniciando conexão. Aguarde....')
connect =  psycopg2.connect(host = "localhost", port ="5432", dbname="Anvisa", user="postgres", password="BateraDeus")

#criando a classe cursor que é usada para gerenciar atributos de dados
cursor = connect.cursor()
# # Insert Dataframe into SQL Server:
try:
    for index, row in df.iterrows():
            query = ("INSERT INTO precos_maximos VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)")
            values = (row['id_med'], row['registro'], row['ean'], row['nome'], row['principio_ativo'], row['classe'], row['categoria'], row['lista'], row['fk_cest'])
            values = [None if pd.isna(value) else value for value in values]
            cursor.execute(query, values)
    connect.commit()
    cursor.close()
except Exception as e:
    traceback.print_exc()