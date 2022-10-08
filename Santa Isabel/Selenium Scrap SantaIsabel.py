from venv import create
import pandas as pd
import string
from os.path import exists
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup
from time import sleep
from datetime import date


MAIN_PATH = 'E:/Universidad/Asignaturas/Taller Ingeniería de Software/scrapping_proyect'
DIRECTORY_PATH = '/Santa Isabel/'
MAIN_URL = 'https://www.santaisabel.cl'
NAME_SUPERMARKET = 'Santa Isabel'


def find_text_by_class_beautifulsoup(soup, tag, class_name):
    try:
        data = soup.find(tag, class_ = class_name).text
    except:
        data = 'NA'
    return data


def find_by_class_beautifulsoup(soup, tag, class_name):
    try:
        data = soup.find(tag, class_ = class_name)
    except:
        data = 'NA'
    return data


def find_firts_text_element_by_class_beautifulsoup(soup, tag, class_name):
    try:
        data = soup.find_all(tag, class_ = class_name)[0].text
    except:
        data = 'NA'
    return data


def find_firts_element_by_class_beautifulsoup(soup, tag, class_name):
    try:
        data = soup.find_all(tag, class_ = class_name)[0]
    except:
        data = 'NA'
    return data


def get_text_selenium(browser, xpath):
    try:
        data = (browser.find_element_by_xpath(xpath).text).upper()
    except:
        data = 'NA'
    return data


def get_element_selenium(browser, xpath):
    try:
        data = (browser.find_element_by_xpath(xpath))
    except:
        data = 'NA'
    return data


def clear_url_image(image):
    # Find start and end of url
    start = image.find('(') + 1
    end = image.find(')')
    
    # Get the url
    image_clean = image[start:end]
    image_clean = image_clean.replace('"', '')
    return image_clean


def clear_price(price):
    price_clean = price.replace('.', '')
    price_clean = price_clean.replace('$', '')
    return price_clean 


def exists_row_dataframe(dataframe, column, element): 
    for i in range(len(dataframe)):
        if dataframe[column][i] == element:
            return True
    return False


def get_data_product_selenium(browser, id_category, id_brand, id_type, id_product):
    # If the product can't load or the product already exists
    error_product = get_element_selenium(browser, '//*[@id="root"]/div/div[2]/main/div/div[2]')
    if error_product != 'NA':
        print('\tError read product - {}'.format(url_product))
        return 'NA'
       
    # Get data of the product
    name_product = get_text_selenium(browser, '//*[@id="root"]/div/div[2]/div/div/main/div[1]/div[2]/div[2]/h1')
    
    # URL of the image is in the style of a div
    image_product = get_element_selenium(browser, '//*[@id="root"]/div/div[2]/div/div/main/div[1]/div[1]/div/div/div[1]/div/div')
    if image_product != 'NA':
        image_product = image_product.get_attribute('style')
        image_product = clear_url_image(image_product)
       
    # Description can has two different xpath
    description1 = get_text_selenium(browser, '//*[@id="root"]/div/div[2]/div/div/main/div[3]/div[1]/div[2]')
    description2 = get_text_selenium(browser, '//*[@id="root"]/div/div[2]/div/div/main/div[3]/div[1]/div[2]/p')
    
    description_product = ''
    if description1 != 'NA' and description1 != '':
        description_product = description1
    
    if description2 != 'NA' and description2 != '':
        description_product += ' ' + description2
    
    ingredients = get_text_selenium(browser, '//*[@id="root"]/div/div[2]/div/div/main/div[3]/div[1]/div[3]/div[2]')
    
    data = [str(id_product),
            str(id_category),
            str(id_brand),
            str(id_type),
            str(name_product),
            str(image_product),
            str(description_product),
            str(ingredients)]
    return data


def get_data_product_beautifulsoup(soup, id_category, id_brand, id_type, id_product):
    # If the product can't load or the product already exists
    error_product = find_text_by_class_beautifulsoup(soup, 'div', 'error-404-empty-message')
    if error_product != 'NA':
        print('\tError read product - {}'.format(url_product))
        return 'NA'
    
    # Get data of the product
    name_product = (find_firts_text_element_by_class_beautifulsoup(soup, 'h1', 'product-name')).upper()
    if name_product == 'NA':
        name_product = (find_text_by_class_beautifulsoup(soup, 'h1', 'product-name')).upper()
        if name_product == 'NA':
            print('\tError read product - {}'.format(url_product))
            return 'NA'
    
    # URL of the image is in the style of a div
    image_product = find_by_class_beautifulsoup(soup, 'div', 'zoomed-image')
    if image_product != 'NA' and type(image_product) != 'NoneType':
        try:
            image_product = image_product.get('style')
            image_product = clear_url_image(image_product)
        except:
            image_product = 'NA'
       
    # Description can has two different xpath
    description1 = find_text_by_class_beautifulsoup(soup, 'p', '')
    description2 = find_text_by_class_beautifulsoup(soup, 'div', 'product-description-content')
    
    description_product = ''
    if description1 != 'NA' and description1 != '':
        description_product = description1
    
    if description2 != 'NA' and description2 != '':
        description_product += ' ' + description2
    
    ingredients = find_text_by_class_beautifulsoup(soup, 'div', 'product-ingredients-text')
    
    data = [str(id_product),
            str(id_category),
            str(id_brand),
            str(id_type),
            str(name_product),
            str(image_product),
            str(description_product),
            str(ingredients)]
    return data


def get_data_categories(df_categories, categories_element):   
    # Remove categories are void and get data of all categories
    for item in categories_element:
        if item.get('href') != '/' and exists_row_dataframe(df_categories, 'category', item.text) == False:
            df_row = pd.DataFrame(data=[[len(df_categories), (item.text).upper()]], columns=columns_category)
            df_categories = pd.concat([df_categories, df_row], ignore_index=True)
    return df_categories


def get_all_url_from_elements(list_elements):
    list_url = []
    for item in list_elements:
        if item.get('href') != '/':
            url = MAIN_URL + item.get('href')
            list_url.append(url)
    return list_url


def get_all_pages_category(soup, url_category):
    list_pages_categories = []
    # Count total pages, if it has
    total_pages = soup.find_all('button', class_ = 'page-number')
    if len(total_pages) > 0:
        for i in range(1, int(total_pages[-1].text) + 1):
            # Get link from all pages
            list_pages_categories.append(url_category + '?page={}'.format(i))
    else:
        list_pages_categories.append(url_category)
    return list_pages_categories


def get_item_dataframe(dataframe, column_search, column_get, item):
    for i in range(len(dataframe)):
        if dataframe[column_search][i] == item:
            return dataframe[column_get][i]
    return None


def get_all_products_category(browser, soup, url_category):
    list_url_products = []
    # Get url of all categories
    pages_categories = get_all_pages_category(soup, url_category)
    for page in pages_categories:
        # Connect to page category
        browser.get(page)
        sleep(3)
        
        # Get url of all products from page category
        soup = BeautifulSoup(browser.page_source, 'lxml')
        for i in soup.find_all('div', class_ = 'shelf-product-island'):
            url_product = MAIN_URL + i.find('a', 'shelf-wrap-image').get('href')
            list_url_products.append(url_product)
    return list_url_products
    

def save_data_csv(dataframe, name_file, columns):
    attemps = 0
    path = MAIN_PATH
    if not exists(path + name_file):
        while attemps < 10:
            try:
                dataframe.to_csv('{}/{}.csv'.format(MAIN_PATH, name_file), encoding='utf-8', index=False, columns=columns)
                print('Saved .CSV - {}.csv !^^'.format(name_file))
                break
            except:
                attemps += 1
                print('Error trying to save files... ({}/10)'.format(attemps))
    else:
        print('File already exists.')


def get_id_dataframe(dataframe, column, column_id, element):
    for i in range(len(dataframe)):
        if dataframe[column][i] == element:
            return dataframe[column_id][i]
    return None


def exists_superproduct(df, id_supermarket, id_product, date_scrap):
    for i in range(len(df)):
        if df['id_supermarket'][i] == id_supermarket and df['id_product'][i] == id_product and df['date'][i] == date_scrap:
            return True
    return False
    
    
def get_data_superproduct_selenium(browser, id_supermarket, id_product, url, date):
    sale_price = clear_price(get_text_selenium(browser, '//*[@id="root"]/div/div[2]/div/div/main/div[1]/div[2]/div[5]/div[1]/div/div[1]/span[1]'))    
    
    # If the tag exists, the product is out of stock
    available = get_text_selenium(browser, '//*[@id="root"]/div/div[2]/div/div/main/div[1]/div[2]/div[1]/span')
    if available == 'NA':
        stock = 'Yes'
    else:
        stock = 'No'
    
    # The normal price can has two different xpath
    if stock == 'Yes':
        normal_price = get_text_selenium(browser, '//*[@id="root"]/div/div[2]/div/div/main/div[1]/div[2]/div[5]/div[2]/div/div/div/span/span/span')
        if normal_price == 'NA':
            normal_price = get_text_selenium(browser, '//*[@id="root"]/div/div[2]/div/div/main/div[1]/div[2]/div[5]/div/span')
        normal_price = clear_price(normal_price)
    else:
        normal_price = 'NA'
    
    data = [str(id_supermarket),
            str(id_product),
            str(sale_price),
            str(normal_price),
            str(url),
            str(date),
            str(stock)]
    return data


def get_data_superproduct_beautifulsoup(soup, id_supermarket, id_product, url, date):
    box_data = find_firts_element_by_class_beautifulsoup(soup, 'div', 'product-info-wrapper')
    if box_data == 'NA':
        box_data = find_by_class_beautifulsoup(soup, 'div', 'product-info-wrapper')
    
    # Get prices
    sale_price = find_firts_text_element_by_class_beautifulsoup(box_data, 'span', 'price-best')  
    sale_price = clear_price(sale_price)
    
    normal_price = find_text_by_class_beautifulsoup(box_data, 'span', 'product-sigle-price-wrapper')
    if normal_price == 'NA':
        normal_price = find_text_by_class_beautifulsoup(box_data, 'span', 'price-product-value')
    normal_price = clear_price(normal_price)
    
    # If the tag exists, the product is out of stock
    available = find_text_by_class_beautifulsoup(soup, 'span', 'no-stock-text')
    if available == 'NA':
        stock = 'Yes'
    else:
        stock = 'No'
    
    data = [str(id_supermarket),
            str(id_product),
            str(normal_price),
            str(sale_price),
            str(url),
            str(date),
            str(stock)]
    return data


def create_row_error_product(url_product, category, id_supermarket, columns):
    data = [str(url_product), str(category), str(id_supermarket)]
    dataframe = pd.DataFrame(data=[data], columns=columns)
    return dataframe


# MAIN
date_scrap = date.today()
total_products = 0

# -- DataFrames --
columns_category = ['id_category', 'category']
columns_brand = ['id_brand', 'brand']
columns_type = ['id_type', 'type']
columns_product = ['id_product', 'category', 'brand', 'type_product', 'name', 'image_url', 'description', 'ingredients']
columns_super_product = ['id_supermarket', 'id_product', 'normal_price', 'sale_price', 'url_product', 'date', 'available']
columns_supermarket = ['id_supermarket', 'supermarket', 'logo_url']
columns_error = ['url_product', 'category', 'id_supermarket']

df_products = pd.DataFrame(columns=columns_product)
df_categories = pd.DataFrame(columns=columns_category)
df_type = pd.DataFrame(columns=columns_type)
df_brand = pd.DataFrame(columns=columns_brand)
df_super_product = pd.DataFrame(columns=columns_super_product)
df_supermarket = pd.DataFrame(columns=columns_supermarket)
df_error_products = pd.DataFrame(columns=columns_error)

if exists(MAIN_PATH + '/Data/products.csv'):
    df_products = pd.read_csv(MAIN_PATH + '/Data/products.csv')
    
if exists(MAIN_PATH + '/Data/type.csv'):
    df_type = pd.read_csv(MAIN_PATH + '/Data/type.csv')
    
if exists(MAIN_PATH + '/Data/brand.csv'):
    df_brand = pd.read_csv(MAIN_PATH + '/Data/brand.csv')
    
if exists(MAIN_PATH + '/Data/categories.csv'):
    df_categories = pd.read_csv(MAIN_PATH + '/Data/categories.csv')
    
if exists(MAIN_PATH + '/Data/supermarketproduct.csv'):
    df_super_product = pd.read_csv(MAIN_PATH + '/Data/supermarketproduct.csv')
    
if exists(MAIN_PATH + '/Data/supermarket.csv'):
    df_supermarket = pd.read_csv(MAIN_PATH + '/Data/supermarket.csv')
    
if exists(MAIN_PATH + '/Data/error_products.csv'):
    df_error_products = pd.read_csv(MAIN_PATH + '/Data/error_products.csv')

# Connect to main website
driver = webdriver.Chrome(MAIN_PATH + '/chromedriver.exe')
driver.set_window_size(1280, 720)
driver.get(MAIN_URL)
sleep(1)

# Hover mouse in the Navbar
element_path = driver.find_element_by_xpath('//*[@id="root"]/div/header/div[3]/nav/div/div[2]/div[2]/a')
hover = ActionChains(driver).move_to_element(element_path)
hover.perform()

# Imports the HTML of the current page into python
soup = BeautifulSoup(driver.page_source, 'lxml')

# Data supermarket
if exists_row_dataframe(df_supermarket, 'supermarket', NAME_SUPERMARKET) == False:
    url_logo = 'https://upload.wikimedia.org/wikipedia/commons/thumb/4/49/Logo_Santa_Isabel_Cencosud_transparente.svg/1200px-Logo_Santa_Isabel_Cencosud_transparente.svg.png'
    data = [len(df_supermarket), NAME_SUPERMARKET, url_logo]
    row = pd.DataFrame(data=[data], columns=columns_supermarket)
    df_supermarket = pd.concat([df_supermarket, row], ignore_index=True)
id_supermarket = get_id_dataframe(df_supermarket, 'supermarket', 'id_supermarket', NAME_SUPERMARKET)

# Get all categories data
categories_supermarket = soup.find_all('a', class_ = 'new-header-supermarket-dropdown-item-name')
categories_navbar = soup.find_all('a', class_ = 'new-header-supermarket-title')
categories = categories_supermarket + categories_navbar
df_categories = get_data_categories(df_categories, categories)

# Get all urls from categories
list_url_categories = get_all_url_from_elements(categories)

# Create a dataframe for this supermarket
df_categories_supermarket = pd.DataFrame(columns=columns_category)
df_categories_supermarket = get_data_categories(df_categories_supermarket, categories)

# Browse all categories
for i in range(len(list_url_categories)):
    driver.get(list_url_categories[i])
    sleep(3)
    soup = BeautifulSoup(driver.page_source, 'lxml')
    print('{} - {}:'.format(df_categories_supermarket['category'][i], list_url_categories[i]))
    
    # Get all urls products from category
    list_url_products = get_all_products_category(driver, soup, list_url_categories[i])
    
    cont_products_category = 0
    total_products_category = len(list_url_products)
    for url_product in list_url_products:
        # Connect to product details
        driver.get(url_product)
        sleep(1)
        soup = BeautifulSoup(driver.page_source, 'lxml')
               
        # Add to dataframe if doesn't exists and get its id
        brand_product = (find_text_by_class_beautifulsoup(soup, 'a', 'product-brand')).upper()
        type_product = 'NA'
        element_type = find_text_by_class_beautifulsoup(soup, 'span', 'technical-information-flags-title')
        if element_type == 'Tipo de Producto':
            type_product = (find_text_by_class_beautifulsoup(soup, 'span', 'technical-information-flags-value')).upper()
               
        # Get brand and add to dataframe is not exists
        if exists_row_dataframe(df_brand, 'brand', brand_product) == False:
            row = pd.DataFrame(data=[[len(df_brand), brand_product]], columns=columns_brand)
            df_brand = pd.concat([df_brand, row], ignore_index=True)
        
        # Get type of product and add to dataframe is not exists
        if exists_row_dataframe(df_type, 'type', type_product) == False:
            row = pd.DataFrame(data=[[len(df_type), type_product]], columns=columns_type)
            df_type = pd.concat([df_type, row], ignore_index=True)
        
        # Get ids
        id_brand = get_id_dataframe(df_brand, 'brand', 'id_brand', brand_product)
        id_type = get_id_dataframe(df_type, 'type', 'id_type', type_product)
        id_supermarket = get_id_dataframe(df_supermarket, 'supermarket', 'id_supermarket', NAME_SUPERMARKET)
        id_category = get_id_dataframe(df_categories, 'category', 'id_category', df_categories_supermarket['category'][i])
        id_product = len(df_products)
        
        # Get product details
        data_product = get_data_product_beautifulsoup(soup, id_category, id_brand, id_type, id_product)
        if data_product == 'NA':
            tmp_df = create_row_error_product(url_product, df_categories_supermarket['category'][i], id_supermarket, columns_error)
            df_error_products = pd.concat([df_error_products, tmp_df], ignore_index=True)
            cont_products_category += 1
            continue
               
        # Add product if doesn't exists in dataframe
        elif exists_row_dataframe(df_products, 'name', data_product[4]) == False:
            df_new_row = pd.DataFrame(data=[data_product], columns=columns_product)
            df_products = pd.concat([df_products, df_new_row], ignore_index=True)
        
        # Add supermarket_product if doesn't exists in dataframe
        if exists_superproduct(df_super_product, id_supermarket, id_product, date_scrap) == False:
            data_superproduct = get_data_superproduct_beautifulsoup(soup, id_supermarket, id_product, url_product, date_scrap)
            df_new_row = pd.DataFrame(data=[data_superproduct], columns=columns_super_product)
            df_super_product = pd.concat([df_super_product, df_new_row], ignore_index=True)
        
        total_products += 1
        cont_products_category += 1
        print('[{}/{}] > {} - ${} < ${}'.format(cont_products_category, total_products_category, data_product[4], data_superproduct[3], data_superproduct[2]))

print('Total products from {}: {}'.format(NAME_SUPERMARKET, total_products))

# Save DataFrame to .csv
save_data_csv(df_products, 'Data/products', columns_product)
save_data_csv(df_categories, 'Data/categories', columns_category)
save_data_csv(df_type, 'Data/type', columns_type)
save_data_csv(df_brand, 'Data/brand', columns_brand)
save_data_csv(df_super_product, 'Data/supermarketproduct', columns_super_product)
save_data_csv(df_supermarket, 'Data/supermarket', columns_supermarket)
save_data_csv(df_error_products, 'Data/error_products', columns_error)
