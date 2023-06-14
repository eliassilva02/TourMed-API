import psycopg2
from lion import Anvisa
import pandas as pd

def Anvisa(produto):
    conn = psycopg2.connect(
    host="localhost",
    database="Anvisa",
    user="postgres",
    password="BateraDeus"
    )

    # Criando um cursor
    cur = conn.cursor()
    if type(produto) == int:
        cur.execute("SELECT ean, nome, principio_ativo, categoria, lista FROM public.precos_maximos WHERE ean = %d;" % (produto))

    elif produto.isalpha():
    # Executando uma consulta
        cur.execute("SELECT ean, nome, principio_ativo, categoria, lista FROM public.precos_maximos WHERE nome = '%s' LIMIT 1;" % (produto))
    else:
        return 'Tipo de dado inválido, use nome ou barras'
    # Obtendo os resultados
    rows = cur.fetchall()
    if len(rows) == 0:
        return "A consulta não retornou nenhum resultado."
    
    else:
        ean = []
        desc = []
        pa = []
        categoria = []
        lista = []

        for row in rows:
            for barras, nome, p_a, cat, lis in [(row[0], row[1], row[2], row[3], row[4])]:
                ean.append(barras)
                desc.append(nome)
                pa.append(p_a)
                categoria.append(cat)
                lista.append(lis)
        if len(set(pa)) == 1:
            cur.execute("SELECT ncm FROM public.pa_ncm WHERE substancia = '%s' LIMIT 1;" % (pa[0]))
            qrpa = cur.fetchall()
            if len(qrpa) == 0:
                ncm = ''
            else:
                ncm = qrpa[0][0]
        else:
            ncm =''
            
        return {
            "EAN": ean[0],
            "Categoria": categoria[0],
            "Lista": lista[0],
            "Nome": desc[0],
            "Principio Ativo": pa[0],
            "NCM": ncm
        }
    
produto = 7898560664649

print(Anvisa(produto))