import os
os.environ['OPENBLAS_NUM_THREADS'] = '12'
import datetime
import requests as rq
from bs4 import BeautifulSoup as bs
import pandas as pd
import functions as fn
from loguru import logger
import auth_data as ad
import pickle
from rich.progress import track


exceptions = []


@logger.catch
def get_related(filename):
    data = pd.read_excel(filename, converters={'ID': str, 'Артикул': str})

    # Create session
    s = fn.open_session()
    related = {}
    for prod in track(data.values, description='[green] MOON_OFFICIAL', style='green'):
        try:
            url = prod[14]
            prod_id = prod[15]
            response = s.get(url, headers=fn.headers)
            soup = bs(response.text, 'html.parser')
            related_url = ['https://www.moon-official.ru' + i.get('href') for i in soup.find_all('a', class_='product-page-colors-item-thumb')]
            related[prod_id + '-04'] = []
            logger.info(f'{url}: {related_url}')
            for i in related_url:
                sku = data['ID'].values[data['Ссылка на товар'] == i]
                if sku:
                    sku = sku[0] + '-04'
                    related[prod_id + '-04'].append(sku)
            logger.info(related[prod_id + '-04'])
            logger.info('-'*40)
        except Exception:
            logger.exception(f'Exception - {prod[14]}')
            exceptions.append(prod[14])

    with open('moon_official_related.pickle', 'wb') as file:
        pickle.dump(related, file)

    logger.info(f'Exception - {len(exceptions)}')
    fn.report(f'''
    Report MOON_OFFICIAL
    Exceptions - {len(exceptions)}\n
    List with exceptions - {exceptions}\n
    ''', 'a')
    return related


if __name__ == '__main__':
    filename = ad.files['moon-official']
    get_related(filename)
