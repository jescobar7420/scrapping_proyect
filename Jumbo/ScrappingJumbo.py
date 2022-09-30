import requests
import pandas as pd
from bs4 import BeautifulSoup
from datetime import date


def connect_url(url):
    page = requests.get(url)
    soup = BeautifulSoup(page.text, 'lxml')
    return soup


def scrap_element(soup, tag, clss):
    try:
        element = soup.find(tag, class_ = clss).text
    except:
        element = 'NA'
    return element


def get_data_product(soup, url_product, image):
    # Load page until name is not null
    product_name = scrap_element(soup, 'h1', 'product-name')
    if product_name == 'NA':
        return 'NA'

    brand = scrap_element(soup, 'a', 'product-brand')
    best_price = scrap_element(soup, 'span', 'price-best')
    best_price = best_price.replace('.', '')
    best_price = best_price.replace('$', '')
    
    # Normal price can have two class
    normal_price = scrap_element(soup, 'span', 'price-product-value')
    if normal_price == 'NA':
        normal_price = scrap_element(soup, 'span', 'product-sigle-price-wrapper')
    normal_price = normal_price.replace('.', '')
    normal_price = normal_price.replace('$', '')
                   
    description = scrap_element(soup, 'div', 'product-description-content')
    ingredients = scrap_element(soup, 'div', 'product-ingredients-text')
    type_product = scrap_element(soup, 'span', 'technical-information-flags-value')
    
    # If the tag exists, the product is out of stock
    available = scrap_element(soup, 'span', 'product-flag out-of-stock')
    if available == 'NA':
        # Yes
        stock = 1
    else:
        stock = 0
    
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
   
    return data


def get_product_error(error_product_read, columns):
    df_new_errors = pd.DataFrame(columns=['url_product', 'image'])
    df_new_products = pd.DataFrame(columns=columns)
    total_products = 0
    
    for i in range(len(error_product_read)):
        url = error_product_read.iloc[i]['url_product']
        soup = connect_url(url)
        
        data = get_data_product(soup, url_product, error_product_read.iloc[i]['image'])
        if data == 'NA':
            print('\tError read product - {}'.format(url_product))
            data_error = [str(url_product), str(image)]
            tmp_df_error = pd.DataFrame(data=[data_error], columns=['url_product', 'image'])
            df_new_errors = pd.concat([df_new_errors, tmp_df_error], ignore_index=True)
            continue
    
        df_new_row = pd.DataFrame(data=[data], columns=columns)
        df_new_products = pd.concat([df_new_products, df_new_row], 
                                    ignore_index=True)

        total_products += 1
        print('[{}] > {} - {} - ${}'.format(total_products, 
                                                data[0], # Name
                                                data[3], # Brand
                                                data[5])) # Normal price
    return df_new_products, df_new_errors
    

# Main path
main_path = 'D:/Universidad/Asignaturas/Taller Ingeniería de Software/scrapping_proyect'

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
links_categories = ['{}/busca?fq=H%3A5859'.format(url_main),
                    '{}/mi-bebe'.format(url_main),
                    '{}/congelados'.format(url_main),
                    '{}/desayuno-y-dulces'.format(url_main),
                    '{}/belleza-y-cuidado-personal'.format(url_main),
                    '{}/vinos-cervezas-y-licores'.format(url_main),
                    '{}/quesos-y-fiambres'.format(url_main),
                    '{}/panaderia-y-pasteleria'.format(url_main),
                    '{}/pescaderia'.format(url_main),
                    '{}/comidas-preparadas'.format(url_main),
                    '{}/busca?fq=H%3A5860'.format(url_main),
                    '{}/mundo-bio-natura'.format(url_main),
                    '{}/hogar'.format(url_main),
                    '{}/electro-y-tecnologia'.format(url_main),
                    '{}/deportes'.format(url_main),
                    '{}/jugueteria'.format(url_main),
                    '{}/libreria'.format(url_main),
                    '{}/farmacia'.format(url_main),
                    '{}/automovil-ferreteria-y-jardin'.format(url_main),
                    '{}/lacteos'.format(url_main),
                    '{}/despensa'.format(url_main),
                    '{}/frutas-y-verduras'.format(url_main),
                    '{}/limpieza'.format(url_main),
                    '{}/carniceria'.format(url_main),
                    '{}/bebidas-aguas-y-jugos'.format(url_main),
                    '{}/mascotas'.format(url_main)]

total_products = 0
error_product_read = pd.DataFrame(columns=['url_product', 'image', 'category'])

# First iteration - Access all category URLs
for url_category in links_categories:
    soup = connect_url(url_category)
    
    category = scrap_element(soup, 'h1', 'title-with-bar-text')
    if category == 'NA':
        category = 'Otro'
    
    # Count total pages, if it has
    list_pages_categories = []
    total_pages = soup.find_all('button', class_ = 'page-number')
    if len(total_pages) > 0:
        for i in range(1, int(total_pages[-1].text) + 1):
            # Get link from all pages
            list_pages_categories.append(url_category + '?page={}'.format(i))
    else:
        list_pages_categories.append(url_category)
    print('{} - {}'.format(category, url_category))
    
    # Second iteration - Access each page of the category
    for url in list_pages_categories:
        soup = connect_url(url)

        # Third iteration - Access each product from the category page
        for i in soup.find_all('div', class_ = 'shelf-product-island'):
            url_product = url_main + i.find('a', 'shelf-wrap-image').get('href')
            soup = connect_url(url_product)
            
            # Get data of products
            image = i.find('img', 'lazy-image').get('src')
            data = get_data_product(soup, url_product, image)
            if data == 'NA':
                print('\tError read product - {}'.format(url_product))
                data_error = [str(url_product), str(image), str(category)]
                tmp_df_error = pd.DataFrame(data=[data_error], columns=['url_product', 'image', 'category'])
                error_product_read = pd.concat([error_product_read, tmp_df_error], ignore_index=True)
                continue
           
            df_new_row = pd.DataFrame(data=[data], columns=columns)
            df = pd.concat([df, df_new_row], ignore_index=True)
            total_products += 1
            print('\t[{}] > {} - {} - ${}'.format(total_products, 
                                                    data[0], # Name
                                                    data[3], # Brand
                                                    data[5])) # Normal price

print('\n> Total errors: {}'.format(len(error_product_read)))

# Get product that was not previously obtained
attempts = 0
while len(error_product_read) > 0 and attempts < 3:
    data_recover, error_product_read = get_product_error(error_product_read, columns)
    df = pd.concat([df, data_recover], ignore_index=True)
    attempts += 1

# Save DataFrame to .csv
index_csv = 1
while True:   
    try:
        df.to_csv('{}/Jumbo/jumbo_db{}.csv'.format(main_path, index_csv), encoding='utf-8')
        error_product_read.to_csv('{}/Jumbo/jumbo_db{}_errors.csv'.format(main_path, index_csv), encoding='utf-8')
        
        print('Saved Jumbo Database - jumbo_db{}.csv !^^'.format(index_csv))
        print('Saved Jumbo Database - jumbo_db{}_errors.csv !^^'.format(index_csv))
        break
    except:
        print('Error trying to save files')
        index_csv += 1

