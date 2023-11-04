import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np

url_tejar = 'https://www.tejar.pk/lenovo-tab-m10-fhd-plus-2nd-gen'
url_surmawala = 'https://surmawala.pk/lenovo-tab-m10-gen2-2gb-ram-32gb-rom-10-1-inch-android-10'

# scrapeing data
def scrape_data(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    return soup

#  extracting data
def extract_data(soup, site_name):
    if site_name == 'Tejar':
        
        title_tag = soup.find('h1', id='product_name')
        title = title_tag.text.strip() if title_tag else 'Title Not Found'

        sku_tag = soup.find('span', id='sku')
        sku = sku_tag.text.strip() if sku_tag else 'SKU Not Found'

        price_tag = soup.find('p', id='product-price-61094')
        price = price_tag.find('span', class_='price').text.strip() if price_tag else 'Price Not Found'


    elif site_name == 'Surmawala':

        title_tag = soup.find('h1', class_='page-title')
        title = title_tag.find('span', class_='base').text.strip() if title_tag else 'Title Not Found'

        sku_tag = soup.find('div', class_='product attribute sku')
        sku = sku_tag.find('div', class_='value').text.strip() if sku_tag else 'SKU Not Found'

        price_tag = soup.find('span', class_='price')
        price = price_tag.text.strip() if price_tag else 'Price Not Found'


    else:
        title = 'Title Not Found'
        sku = 'SKU Not Found'
        price = 'Price Not Found'

    return {
        'site': site_name,
        'title': title,
        'price': price,
        'sku': sku
    }




data_tejar = scrape_data(url_tejar)
data_surmawala = scrape_data(url_surmawala)


product_tejar = extract_data(data_tejar, 'Tejar')
product_surmawala = extract_data(data_surmawala, 'Surmawala')

df = pd.DataFrame([product_tejar, product_surmawala])

# Remove any characters that are not a digit, a decimal point, or a comma
df['price'] = df['price'].replace('[^\d.,]', '', regex=True)
df['price'] = df['price'].str.replace(',', '')
df['price'] = df['price'].str.lstrip('.')
df['price'] = df['price'].replace('', np.nan)
df['price'] = pd.to_numeric(df['price'], errors='coerce')

print(df)

# Compare prices
if not df.empty and 'price' in df.columns:
    cheaper_site = df.loc[df['price'].idxmin(), 'site']
    print(f"The cheaper option is available on {cheaper_site}.")

