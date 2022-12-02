import os
os.environ['OPENBLAS_NUM_THREADS'] = '12'
import datetime
import auth_data as ad
import pandas as pd
from bs4 import BeautifulSoup as bs
import pickle
import re
import json
from loguru import logger
import functions as fn
from rich.progress import track


multicolors = {}
onecolors = []
excepts_url = []


@logger.catch
def get_multicolors(filename):
    data_img = fn.get_data_img(filename)

    # Create session
    s = fn.open_session()
    # Check all rows in dataframe
    for prod in track(data_img.values, description='[green] FARFELLO', style='green'):
        result = fn.get_soup(prod, s)
        if result:
            soup, response, colors, url, id = result
            try:
                # Get colors in the same order as that pictures
                match = re.search(r'JCCatalogElement\(({.+?})\);', response.text)
                if not match:
                    logger.debug('Not found json')
                value = json.loads(match.group(1).replace("'", '"').replace('\t', ' '))
                all_colors = [i['PROPERTIES']['CML2_ATTRIBUTES']['VALUE'][-1] for i in value['OFFERS']]
                # Get slider with photos for each color
                sliders = soup.select('div.product-slider')
                column_number = 1
                multicolors[str(id) + '-01'] = {}
                # iterate indexes and add to dict {color: img}
                for i in range(len(sliders)):
                    images_tags = sliders[i].find_all('a')
                    images = ['https://farfello.com' + img.get('href') for img in images_tags if img.get('href') != '#youtube-window']
                    color = all_colors[i].strip()
                    logger.info(f'Color - {color}. Photos - {images}')
                    # Add color name and images to dataframe
                    data_img, column_number = fn.add_row_dfimg(data_img, url, color, images, column_number)
                    multicolors[str(id) + '-01'][color] = images
            except Exception:
                logger.exception(f'Exception on product page - {url}')
                excepts_url.append(url)
        else:
            logger.debug(f'Product with one single color - {prod[0]}')
            onecolors.append({prod[0]})
        logger.info('-'*40)

    with pd.ExcelWriter('full_farfello.xlsx', engine='xlsxwriter', options={'strings_to_urls': False}) as writer:
        data_img.to_excel(writer, sheet_name='Sheet')

    with open('products_images.pickle', 'wb') as file:
        pickle.dump(multicolors, file)

    logger.info(f'Products with several colors - {len(multicolors)}')
    logger.info(f'Products with one color - {len(onecolors)}')
    logger.info(f'Exceptions - {len(excepts_url)}')
    fn.report(f'''
    Report FARFELLO
    Products with several colors - {len(multicolors)}\n
    Products with one color - {len(onecolors)}\n
    Exceptions - {len(excepts_url)}\n
    List with one color products - {onecolors}\n
    List with exceptions - {excepts_url}\n
    ''', 'a')
    return multicolors


if __name__ == '__main__':
    filename = ad.files['farfello']
    get_multicolors(filename)
