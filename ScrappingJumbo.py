import requests
import pandas as pd
from bs4 import BeautifulSoup
from datetime import date


def scraping_element(soup, tag, clss):
    try:
        element = soup.find(tag, class_ = clss).text
    except:
        element = 'NA'
    return element


def main():
    # Main URL (JUMBO)
    url_main = 'https://www.jumbo.cl'
    
    # Date of scraping
    date_scrap = date.today()
    
    # Create DataFrame of Products
    columns = ['Name', 
               'Link',
               'Image',
               'Brand',
               'Best price', 
               'Normal price', 
               'Type of product',
               'Category',
               'Description',
               'Ingredients',
               'Available',
               'Date']
    
    df = pd.DataFrame(columns=columns)
    
    # List of categories from main url
    #'https://www.jumbo.cl/busca?fq=H%3A5859',
    links_categories = [
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
    
    total_products = 0
    error_product_read = pd.DataFrame(columns=['url_product', 'image'])
    
    # First iteration - Access all category URLs
    for url_category in links_categories:
        page = requests.get(url_category)
        soup = BeautifulSoup(page.text, 'lxml')
        
        
        category = scraping_element(soup, 'h1', 'title-with-bar-text')
        if category == 'NA':
            category = 'Otro'
        
        # Count total pages, if it has
        list_pages_categories = []
        total_pages = soup.find_all('button', class_ = 'page-number')
        if len(total_pages) > 0:
            for i in range(1, int(total_pages[-1].text) + 1):
                list_pages_categories.append(url_category + '?page={}'.format(i))
        else:
            list_pages_categories.append(url_category)
        
        
        print('{} - {}'.format(category, url_category))
        
        # Second iteration - Access each page of the category
        for url in list_pages_categories:
            page = requests.get(url)
            soup = BeautifulSoup(page.text, 'lxml')
            

            # Third iteration - Access each product from the category page
            for i in soup.find_all('div', class_ = 'shelf-product-island'):
                url_product = url_main + i.find('a', 'shelf-wrap-image').get('href')
                page = requests.get(url_product)
                soup = BeautifulSoup(page.text, 'lxml')
                
                # Get the image of the product
                image = i.find('img', 'lazy-image').get('src')
                
                # Load page until name is not null
                product_name = scraping_element(soup, 'h1', 'product-name')
                if product_name == 'NA':
                    print('\tError read product - {}'.format(url_product))
                    data_error = [str(url_product), str(image)]
                    tmp_df_error = pd.DataFrame(data=[data_error], columns=['url_product', 'image'])
                    error_product_read = pd.concat([error_product_read, tmp_df_error], ignore_index=True)
                    continue
   
                brand = scraping_element(soup, 'a', 'product-brand')
                best_price = scraping_element(soup, 'span', 'price-best')
                best_price = best_price.replace('.', '')
                best_price = best_price.replace('$', '')
                
                # Normal price can have two class
                normal_price = scraping_element(soup, 'span', 'price-product-value')
                if normal_price == 'NA':
                    normal_price = scraping_element(soup, 'span', 'product-sigle-price-wrapper')
                normal_price = normal_price.replace('.', '')
                normal_price = normal_price.replace('$', '')
                               
                description = scraping_element(soup, 'div', 'product-description-content')
                ingredients = scraping_element(soup, 'div', 'product-ingredients-text')
                type_product = scraping_element(soup, 'span', 'technical-information-flags-value')
                
                # If the tag exists, the product is out of stock
                available = scraping_element(soup, 'span', 'product-flag out-of-stock')
                if available == 'NA':
                    stock = 0
                else:
                    stock = 1
                
                data = [str(product_name),
                        str(url_product),
                        str(image),
                        str(brand),
                        str(best_price),
                        str(normal_price),
                        str(type_product),
                        str(category),
                        str(description),
                        str(ingredients),
                        str(stock),
                        str(date_scrap)]
                
               
                df_new_row = pd.DataFrame(data=[data], columns=columns)
                df = pd.concat([df, df_new_row], ignore_index=True)

                total_products += 1
                print('\t* [{}] - {}, {}, ${}'.format(total_products, product_name, brand, normal_price))
      
    
    df.to_csv('D:/Curso Udemy/Scrapping/jumbo_db.csv', encoding='latin1')


if __name__ == '__main__':
    main()
