import pandas as pd
import numpy as np
from datetime import datetime
import re
df = pd.read_csv(r'C:\\Users\\ADMIN\Downloads\\laptop_da\\ama_laptop.csv')
df.drop_duplicates(inplace=True)
df
df['diem_danh_gia'] = df['diem_danh_gia'].str.replace(" out of 5 stars", '', regex=False).astype(float)

rename_dict = {
    'Name': 'name',
    'Price': 'price',
    'ngay_giao_hang': 'delivery_date',
    'luot_mua_thang_truoc': 'lmsales',
    'diem_danh_gia': 'rating',
    'luot_danh_gia': 'reviews',
    'so_option_khac': 'other_opts'
}
df = df.rename(columns=rename_dict)

df = df[df['lmsales'].str.contains('bought in past month', na=False)]

def convert_lmsales(text):
    match = re.search(r'(\d+(?:K)?)\+', text)
    if match:
        value = match.group(1)
        if 'K' in value:
            return int(value.replace('K', '')) * 1000
        else:
            return int(value)
    return 0

df['lmsales_converted'] = df['lmsales'].apply(convert_lmsales)
df['lmsales_converted']
df['delivery_date'] = df['delivery_date'].str.replace("Delivery", '', regex=False)
df['delivery_date'] = df['delivery_date'].str.replace("nan", '', regex=False)
df['delivery_date'] = df['delivery_date'].str.replace("NaN", '', regex=False)


def convert_date(date_str):
    if isinstance(date_str, str):
        try:
            date_str = date_str.strip()
            return datetime.strptime(date_str, '%a, %b %d').replace(year=datetime.now().year).strftime('%Y%m%d')
        except ValueError as e:
            print(f"Error converting date: {e} - for date_str: {date_str}")
            return None
    return date_str

df['delivery_date'] = df['delivery_date'].apply(convert_date)

df['delivery_date'] = df['delivery_date'].fillna(0).astype(int)
df['delivery_date']

def calculate_wait_days(delivery_int):
    if delivery_int == 0:
        return 0
    delivery_date = datetime.strptime(str(delivery_int), '%Y%m%d')
    now = datetime.now()
    wait_days = (delivery_date - now).days
    return wait_days

df['wait_days'] = df['delivery_date'].apply(calculate_wait_days)
df['wait_days']

df['reviews'] = df['reviews'].str.replace(",", '', regex=False).astype(float)
df['reviews']
df['price'] = df['price'].str.replace(",", '', regex=False).astype(float)
df['price']

brand_dict = {
    'Lenovo': 'Lenovo',
    'HP': 'HP',
    'LG': 'LG',
    'Dell': 'Dell',
    'Acer': 'Acer',
    'acer': 'Acer',
    'ASUS': 'ASUS',
    'MSI': 'MSI',
    'GIGABYTE': 'GIGABYTE',
    'ZAGG': 'ZAGG',
    'Apple': 'Apple',  # Consider 'Macbook' as Apple product
    'SAMSUNG': 'SAMSUNG',
    'Core Innovations': 'Core Innovations',
    'Razer Blade': 'Razer Blade',
    'Kensington': 'Kensington', 
    'Amazon': 'Amazon', 
    'Kingston' : 'Kingston',
    'UBeesize' : 'UBeesize'
}

def find_brand(name):
    for key in brand_dict:
        if key in name:
            return brand_dict[key]
    return 'Other'

df['brand'] = df['name'].apply(find_brand)
brand_counts = df['brand'].value_counts()
brand_counts

ram_pattern = re.compile(r'(\d+\s*GB\s*(?:DDR[2345]|LPDDR[34])?\s*(?:RAM|Memory)?)', re.IGNORECASE)
capacity_pattern = re.compile(r'\b(\d+\s?(?:GB|TB)(?!\s*(?:RAM|Memory|DDR|LPDDR)))\b', re.IGNORECASE)
type_pattern = re.compile(r'\b(SSD|HDD|eMMC)\b', re.IGNORECASE)

def extract_ram(name):
    match = ram_pattern.search(name)
    if match:
        ram_value = int(re.search(r'\d+', match.group(1)).group())
        if ram_value > 100: 
            return 'RAM not defined'
        return match.group(1)
    return 'RAM not found'

# Functions to extract storage capacity and type
def extract_capacity(name):
    match = capacity_pattern.findall(name)
    return match[-1] if match else None

def extract_type(name):
    match = type_pattern.search(name)
    return match.group() if match else None

df['ram'] = df['name'].apply(extract_ram)
df['storage_capacity'] = df['name'].apply(extract_capacity)
df['storage_type'] = df['name'].apply(extract_type)

print(df[['name', 'storage_capacity', 'storage_type', 'ram']])

def categorize_product(row):
    if row['price'] < 240 and row['ram'] == 'RAM not found' and pd.isna(row['storage_capacity']):
        return 'accessory'
    else:
        return 'laptop'

df['type'] = df.apply(categorize_product, axis=1)
df['type']

type_counts = df['type'].value_counts()
type_counts

cpu_pattern = re.compile(r'\b(?:Intel|AMD|MediaTek)\b.*?(?:Processor)?')

def extract_cpu(name):
    match = cpu_pattern.search(name)
    return match.group(0) if match else 'CPU not found'
df['cpu_brand'] = df['name'].apply(extract_cpu)
df['cpu_brand']

df['ram'] = df['ram'].str.replace("RAM", '', regex=False)
df['ram'] = df['ram'].str.replace("GB", '', regex=False)
df['ram'] = df['ram'].str.replace("DDR5", '', regex=False)
df['ram'] = df['ram'].str.replace("Memory", '', regex=False)
df['ram'] = pd.to_numeric(df['ram'].str.replace(" ", '', regex=False), errors='coerce')
df['ram'].fillna(0, inplace=True)
df['ram']

def convert_tb_to_gb(capacity):
    if capacity is None:
        return None
    if 'TB' in capacity:
        return float(capacity.replace('TB', '')) * 1024
    elif 'GB' in capacity:
        return float(capacity.replace('GB', ''))
    else:
        return capacity

df['storage_capacity'] = df['storage_capacity'].apply(convert_tb_to_gb)
df['storage_capacity']

df.to_csv('cleaned_asin_added.csv', index=False)
