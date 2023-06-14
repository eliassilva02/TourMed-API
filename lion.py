import psycopg2
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from time import sleep
from bs4 import BeautifulSoup
import pandas as pd
from re import match
from selenium.webdriver.support.select import Select
from selenium.webdriver.chrome.options import Options
from flask import abort, jsonify


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

    elif match("^[a-zA-Z\s]+$", produto):
    # Executando uma consulta
        cur.execute("SELECT public.precos_maximos.ean, public.precos_maximos.nome, public.precos_maximos.principio_ativo, public.precos_maximos.categoria, public.precos_maximos.lista, public.cest.cest FROM public.precos_maximos JOIN public.cest ON public.precos_maximos.id_cest = public.cest.id_cest WHERE public.precos_maximos.nome = '%s' LIMIT 1;" % (produto))
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
        cest = []

        for row in rows:
            for barras, nome, p_a, cat, lis, num in [(row[0], row[1], row[2], row[3], row[4], row[5])]:
                ean.append(barras)
                desc.append(nome)
                pa.append(p_a)
                categoria.append(cat)
                lista.append(lis)
                cest.append(num)

        # NÃO ADICIONAR VALIDAÇÃO(IF LEN SET PA....) DE DADOS NA LISTA DE PA POIS DEMORA MAIS PRA FAZER A REQUISIÇÃO
        cur.execute("SELECT ncm FROM public.pa_ncm WHERE substancia = '%s' LIMIT 1;" % (pa[0]))
        qrpa = cur.fetchall()

        if len(qrpa) == 0:
            ncm = ''
        else:
            ncm = qrpa[0][0]
        
        return {
            "EAN": ean[0],
            "Categoria": categoria[0],
            "Lista": lista[0],
            "Nome": desc[0],
            "Principio Ativo": pa[0],
            "NCM": ncm,
            "CEST": cest[0]
        }
    

def Pesquisa(produto):
    options = webdriver.ChromeOptions() 
    options.add_argument("--headless") 
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    driver = webdriver.Chrome(options=options)

    url = 'https://www.smerp.com.br/anvisa/?ac=prodSearch&page=1&fastSearch=&anvisaType=0&anvisaId=&anvisaIdType=0&anvisaProcN=&anvisaProcNType=0&anvisaProdDesc=ultracler&anvisaProdDescType=0&anvisaProdCat=&anvisaProdCatType=0&anvisaProdMod=&anvisaProdModType=0&anvisaHolderReg=&anvisaHolderRegType=0&anvisaProdOrig=&anvisaProdOrigType=0#results'
    driver.get(url)

    login = driver.find_element('name', 'anvisaProdDesc')
    login.clear()
    login.send_keys("%s" % (produto))
    tipo = driver.find_element('name', 'anvisaProdDescType')
    tipo = Select(tipo).select_by_value('1')

    btn = driver.find_element(By.ID, 'submitSearch')
    btn.click() 
    

    try:
        driver.find_element(By.CLASS_NAME, 'error')
        abort(404, 'Item não encontrado')

    except:
        tr_tags = driver.find_elements(By.TAG_NAME, 'tr')

        # Variáveis para armazenar a descrição e o link
        descricao = None
        link = None

        # Percorre as tags <tr> e verifica se contêm a descrição desejada
        for tr in tr_tags:
            td_tags = tr.find_elements(By.TAG_NAME, 'td')
            if len(td_tags) >= 2 and 'MG' in td_tags[1].text or len(td_tags) >= 2 and 'MCG' in td_tags[1].text or len(td_tags) >= 2 and 'MG/G' in td_tags[1].text:
                descricao = td_tags[1].text
                link = tr.find_element(By.XPATH, './/a')
                break

        # Clica no link se encontrado
        if link:
            link.click()
        try:
            nome = driver.find_element(By.XPATH,'//*[@id="anvisa"]/div[1]/div[3]/div[2]').text
            p_ativo = driver.find_element(By.XPATH,'//*[@id="anvisa"]/div[1]/div[9]/div[2]').text
            categoria = driver.find_element(By.XPATH,'//*[@id="anvisa"]/div[1]/div[10]/div[2]').text
            lista = driver.find_element(By.XPATH,'//*[@id="anvisa"]/div[1]/div[25]/div[2]').text
            lista_ = ''
            cat_ = ''

            if categoria != 'Novo' and categoria != 'Similar' and categoria != 'Genérico' and categoria != 'Generico':
                cat_ = 'Outros'
            else:
                cat_ = categoria            
        

            if 'Venda Sob' in lista or 'Venda sob' in lista or 'venda sob' in lista or 'venda Sob' in lista:
                lista_ = 'Positiva'
            elif 'Venda Sem' in lista or 'Venda sem' in lista or 'venda sem' in lista or 'venda Sem' in lista:
                lista_ = 'Negativa'

            conn = psycopg2.connect(
            host="localhost",
            database="Anvisa",
            user="postgres",
            password="BateraDeus"
            )

            # Criando um cursor
            cur = conn.cursor()
            
            if p_ativo == 'Fitoterápico' or 'Fitoterapico':
                ncm = 30049099
            else:
                # Executando a consulta NCM
                cur.execute("SELECT ncm FROM public.pa_ncm WHERE substancia = '%s' LIMIT 1;" % (p_ativo))
                qrpa = cur.fetchall()
                if len(qrpa) == 0:
                    ncm = ''
                else:
                    ncm = qrpa[0][0]
            
            # Executando a consulta CEST
            cur.execute("SELECT cest FROM public.cest WHERE categoria ILIKE '%s' AND lista ILIKE '%s';" %(cat_, lista_))
            qrcest = cur.fetchall()
            if len(qrcest) == 0:
                cest = ''
            else:
                cest = qrcest[0][0]

            return jsonify({
                'Nome' : nome,
                'Principio Ativo' : p_ativo,    
                'Categoria' : '%s ou %s'%(categoria, cat_),
                'Lista' : '%s ou %s'%(lista, lista_),
                'NCM': ncm,
                'CEST': cest
            })
        
        except NoSuchElementException:
            return 'Item não encontrado'