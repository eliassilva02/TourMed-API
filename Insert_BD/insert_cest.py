import psycopg
import pandas as pd
import traceback
# insert data from csv file into dataframe.
# working directory for csv file: type "pwd" in Azure Data Studio or Linux
# working directory in Windows c:\users\username
df = pd.read_excel("C:\\Dev\\Projetos\\Python\\Python_meds\\Insert_BD\\cest's.xlsx", header=0)
df = pd.DataFrame(df)

# Some other example server values are
# server = 'localhost\sqlexpress' # for a named instance
# server = 'myserver,port' # to specify an alternate port

connect =  psycopg.connect(host = "localhost", port ="5432", dbname="Anvisa", user="postgres", password="BateraDeus")

#criando a classe cursor que é usada para gerenciar atributos de dados
cursor = connect.cursor()
# # Insert Dataframe into SQL Server:
try:
    for index, row in df.iterrows():
            query = ("INSERT INTO cest (id_cest, categoria, lista, posicao_ncm, cest) VALUES (%s,%s,%s,%s,%s)")
            values = (row['id_cest'], row['categoria'], row['lista'], row['posicao_ncm'], row['cest'])
            cursor.execute(query, values)
    connect.commit()
    cursor.close()
except Exception as e:
    traceback.print_exc()