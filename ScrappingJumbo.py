import requests
from bs4 import BeautifulSoup
import pandas as pd
from time import sleep

url_main = 'https://www.jumbo.cl'

df = pd.DataFrame({'Name': [''],
                   'Link': [''],
                   'Best price': [''],
                   'Normal price': [''],
                   'Type of product': [''],
                   'Description': [''],
                   'Ingredients': [''],
                   'Available': ['']})

links_categories = ['https://www.jumbo.cl/busca?fq=H%3A5859',
                    'https://www.jumbo.cl/mi-bebe',
                    'https://www.jumbo.cl/congelados',
                    'https://www.jumbo.cl/desayuno-y-dulces',
                    'https://www.jumbo.cl/belleza-y-cuidado-personal',
                    'https://www.jumbo.cl/vinos-cervezas-y-licores',
                    'https://www.jumbo.cl/quesos-y-fiambres',
                    'https://www.jumbo.cl/panaderia-y-pasteleria',
                    'https://www.jumbo.cl/pescaderia',
                    'https://www.jumbo.cl/comidas-preparadas',
                    'https://www.jumbo.cl/busca?fq=H%3A5860',
                    'https://www.jumbo.cl/mundo-bio-natura',
                    'https://www.jumbo.cl/hogar'
                    'https://www.jumbo.cl/electro-y-tecnologia',
                    'https://www.jumbo.cl/deportes',
                    'https://www.jumbo.cl/jugueteria',
                    'https://www.jumbo.cl/libreria',
                    'https://www.jumbo.cl/farmacia',
                    'https://www.jumbo.cl/automovil-ferreteria-y-jardin',
                    'https://www.jumbo.cl/lacteos',
                    'https://www.jumbo.cl/despensa',
                    'https://www.jumbo.cl/frutas-y-verduras',
                    'https://www.jumbo.cl/limpieza',
                    'https://www.jumbo.cl/carniceria',
                    'https://www.jumbo.cl/bebidas-aguas-y-jugos',
                    'https://www.jumbo.cl/mascotas']


for url_category in links_categories:
    page = requests.get(url_category)
    soup = BeautifulSoup(page.text, 'lxml')
    sleep(1)
    
    total_page = soup.find_all('button', class_ = 'page-number')
    
    list_pages_categories = []
    
    if len(total_page) > 0:
        for i in range(1, int(total_page[-1].text) + 1):
            list_pages_categories.append(url_category + '?page={}'.format(i))
    else:
        list_pages_categories.append(url_category)
    
    for url in list_pages_categories:
        page = requests.get(url)
        soup = BeautifulSoup(page.text, 'lxml')
        sleep(1)
        
    
        for i in soup.find_all('a', class_ = 'shelf-wrap-image'):  
            url_product = url_main + i.get('href')
            page = requests.get(url_product)
            soup = BeautifulSoup(page.text, 'lxml')
            sleep(1)
            
            try:
                product_name = soup.find('h1', class_ = 'product-name').text
            except:
                product_name = 'NA'
            
            try:
                best_price = soup.find('span', class_ = 'price-best').text
            except:
                best_price = 'NA'
            
            try:
                normal_price = soup.find('span', class_ = 'price-product-value').text
            except:
                try:
                    normal_price = soup.find('span', class_ = 'product-sigle-price-wrapper').text
                except:
                    normal_price = 'NA'
            
            try:
                description = soup.find('div', class_ = 'product-description-content').text
            except:
                description = 'NA'
            
            try:
                ingredients = soup.find('div', class_ = 'product-ingredients-text').text
            except:
                ingredients = 'NA'
            
            try:
                type_product = soup.find('span', class_ = 'technical-information-flags-value').text
            except:
                type_product = 'NA'
                
            
            
            try:
                available = soup.find('span', class_ = 'product-flag out-of-stock')
                if available:
                    stock = 0
                else:
                    stock = 1
            except:
                stock = 'NA'
            
            df = df.append({'Name': product_name,
                            'Link': url_product,
                            'Best price': best_price,
                            'Normal price': normal_price,
                            'Type of product': type_product,
                            'Description': description,
                            'Ingredients': ingredients,
                            'Available': stock}, ignore_index=True)

    
df.to_csv('D:/Curso Udemy/Scrapping/products_jumbo.csv')
