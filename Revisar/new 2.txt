import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup
from time import sleep
from datetime import date

MAIN_URL = 'https://www.santaisabel.cl'
NAME_SUPERMARKET = 'Santa Isabel'

def get_text_product_selenium(browser, xpath):
    try:
        data = browser.find_element_by_xpath(xpath).text
    except:
        data = 'NA'
    return data


def get_element_product_selenium(browser, xpath):
    try:
        data = browser.find_element_by_xpath(xpath)
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
    price_clean = price.replace('$', '')
    return price_clean


def get_all_products_page(browser, url, category):
    # Get data of the product
    name_product = get_text_product_selenium(browser, '//*[@id="root"]/div/div[2]/div/div/main/div[1]/div[2]/div[2]/h1')
    brand_product = get_text_product_selenium(browser, '//*[@id="root"]/div/div[2]/div/div/main/div[1]/div[2]/div[3]/div[1]/a')
    best_price = get_text_product_selenium(browser, '//*[@id="root"]/div/div[2]/div/div/main/div[1]/div[2]/div[5]/div[2]/div/div/div/span/span/span')
    type_product = get_text_product_selenium(browser, '//*[@id="root"]/div/div[2]/div/div/main/div[4]/div[1]/div[2]/div/div[2]/span')
    ingredients = get_text_product_selenium(browser, '//*[@id="root"]/div/div[2]/div/div/main/div[3]/div[1]/div[4]/div[2]')
    
    # URL of the image is in the style of a div
    image_product = get_element_product_selenium(browser, '//*[@id="root"]/div/div[2]/div/div/main/div[1]/div[1]/div/div/div[1]/div/div').get_attribute('style')
    image_product = clear_url_image(image_product)
    
    # The normal price can has two different xpath
    normal_price = get_text_product_selenium(browser, '//*[@id="root"]/div/div[2]/div/div/main/div[1]/div[2]/div[5]/div[1]/div/div[1]/span[1]')
    if normal_price == 'NA':
        normal_price = get_text_product_selenium(browser, '//*[@id="root"]/div/div[2]/div/div/main/div[1]/div[2]/div[5]/div/span')
    
    # If the tag exists, the product is out of stock
    available = get_text_product_selenium(browser, '//*[@id="root"]/div/div[2]/div/div/main/div[1]/div[2]/div[1]/span')
    if available == 'NA':
        stock = 'Yes'
    else:
        stock = 'No'
        
    # Description can has two different xpath
    description1 = get_text_product_selenium(browser, '//*[@id="root"]/div/div[2]/div/div/main/div[3]/div[1]/div[2]')
    description2 = get_text_product_selenium(browser, '//*[@id="root"]/div/div[2]/div/div/main/div[3]/div[1]/div[2]/p')
    
    if description1 != 'NA' and description1 != '':
        description_product = description1
    
    if description2 != 'NA' and description2 != '':
        description_product += ' ' + description2
    
    data = [str(name_product),
            str(url),
            str(image_product),
            str(brand_product),
            str(best_price),
            str(normal_price),
            str(type_product),
            str(category),
            str(description_product),
            str(ingredients),
            str(stock),
            str(date_scrap)]
    return data


def get_data_categories(df_categories, categories_element):   
    # Remove categories are void and get data of all categories
    categories_void = ['Exclusivo en Santa Isabel', 'Otros']
    for item in categories_element:
        if item.text not in categories_void:
            url_category = MAIN_URL + item.get('href')
            df_row = pd.DataFrame(data=[[url_category, item.text, NAME_SUPERMARKET]], columns=columns_category)
            df_categories = pd.concat([df_categories, df_row], ignore_index=True)
    return df_categories


def print_product_scrap(data, cont_products_category, total_products_category):
    print('[{}/{}] > {} - {} - ${}'.format(cont_products_category,
                                           total_products_category,
                                           data[0],  # Name
                                           data[3],  # Brand
                                           data[5])) # Normal price


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
    

# Main path
main_path = 'D:/Universidad/Asignaturas/Taller Ingeniería de Software/scrapping_proyect'


date_scrap = date.today()
total_products = 0

# DataFrames

# Create DataFrame of Products
columns_product = ['Name', 
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

df_products = pd.DataFrame(columns=columns_product)

columns_category = ['url_category', 'name', 'supermarket']
df_categories = pd.DataFrame(columns=columns_category)

# Connect to website
driver = webdriver.Chrome(main_path + '/chromedriver.exe')
driver.set_window_size(1280, 720)
driver.get(MAIN_URL)
sleep(1)

# Hover mouse in the Navbar
element_path = driver.find_element_by_xpath('//*[@id="root"]/div/header/div[3]/nav/div/div[2]/div[2]/a')
hover = ActionChains(driver).move_to_element(element_path)
hover.perform()

# Imports the HTML of the current page into python
soup = BeautifulSoup(driver.page_source, 'lxml')

# Get all categories data
categories = soup.find_all('a', class_ = 'new-header-supermarket-dropdown-item-name')
df_categories = get_data_categories(df_categories, categories)

# Browse all categories
for i in range(len(df_categories)):
    # Connect to category site
    driver.get(df_categories['url_category'][i])
    sleep(3)
    soup = BeautifulSoup(driver.page_source, 'lxml')
    print('{} ({}):'.format(df_categories['name'][i], df_categories['url_category'][i]))
    
    # Get all urls products from category
    list_url_products = get_all_products_category(driver, soup, df_categories['url_category'][i])   
    cont_products_category = 0
    total_products_category = len(list_url_products)
    for url_product in list_url_products:
        # Connect to product details
        driver.get(url_product)
        sleep(1)
       
        # Get product details
        data = get_all_products_page(driver, url_product, df_categories['name'][i])
        
        # Add to main df
        df_new_row = pd.DataFrame(data=[data], columns=columns_product)
        df_products = pd.concat([df_products, df_new_row], ignore_index=True)

        total_products += 1
        cont_products_category += 1
        print_product_scrap(data, cont_products_category, total_products_category)
    break
    
print('Total products from {}: {}'.format(NAME_SUPERMARKET, total_products))

# Save DataFrame to .csv
index_csv = 1
while True:   
    try:
        df_products.to_csv('{}/Santa Isabel/santaisabel_db_products{}.csv'.format(main_path, index_csv), encoding='utf-8')
        df_categories.to_csv('{}/Santa Isabel/santaisabel_db_categories{}.csv'.format(main_path, index_csv), encoding='utf-8')
        
        print('Saved SantaIsabel Database - santaisabel_db_products{}.csv !^^'.format(index_csv))
        print('Saved SantaIsabel Database - santaisabel_db_categories{}.csv !^^'.format(index_csv))
        break
    except:
        print('Error trying to save files')
        index_csv += 1


 