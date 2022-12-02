import os
os.environ['OPENBLAS_NUM_THREADS'] = '12'
import datetime
import pandas as pd
import functions as fn
from loguru import logger
import auth_data as ad
import pickle
from rich.progress import track
from selenium import webdriver
import time
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By


multicolors = {}
onecolors = []
excepts_url = []


@logger.catch
def get_multicolors(filename):
    data_img = fn.get_data_img(filename)

    # Create session
    s = fn.open_session()
    options = Options()
    driver = webdriver.PhantomJS(ad.catalog_path + '/phantomjs-2.1.1-linux-x86_64/bin/phantomjs',
                                 service_args=['--ignore-ssl-errors=true', '--ssl-protocol=any'])
    # driver = webdriver.PhantomJS('/Users/psamodurov13/PycharmProjects/parse_supliers/venv/bin/phantomjs-2.1.1-macosx/bin/phantomjs')
    # driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
    driver.maximize_window()
    options.add_argument(
        'user-agent=Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Mobile Safari/537.36')

    for prod in track(data_img.values, description='[green] GOROD_KOLYASOK', style='green'):
        result = fn.get_soup(prod, s)
        if result:
            soup, response, colors, url, id = result
            try:
                # Get colors in the same order as that pictures
                all_colors = []
                driver.get(url)
                column_number = 1
                multicolors[str(id) + '-03'] = {}
                for i in soup.select('ul.option-list li label'):
                    color_value = i.find('span', class_='attribute-square-container').get('title')
                    color_id = i.find('input').get('id')
                    if color_value in all_colors:
                        color_value = f'{color_value} ({color_id.split("_")[-1]})'
                    all_colors.append(color_value)
                    choice_color = driver.find_element(By.CSS_SELECTOR, f'ul.option-list label[for="{color_id}"]')
                    choice_color.click()
                    time.sleep(2)
                    img = driver.find_element(By.CSS_SELECTOR, '#sevenspikes-cloud-zoom a img').get_attribute('src')
                    multicolors[str(id) + '-03'][color_value] = [img]
                    data_img, column_number = fn.add_row_dfimg(data_img, url, color_value, [img], column_number)
                    logger.info(f'Color - {color_value} - {img}')
            except Exception:
                logger.exception(f'Exception on product page - {url}')
                excepts_url.append(url)
        else:
            logger.debug(f'Product with one single color - {prod[0]}')
            onecolors.append({prod[0]})
        logger.info('-' * 40)

    with pd.ExcelWriter('full_gorod_kolyasok.xlsx', engine='xlsxwriter', options={'strings_to_urls': False}) as writer:
        data_img.to_excel(writer, sheet_name='Sheet')

    with open('gorod_kolyasok_images.pickle', 'wb') as file:
        pickle.dump(multicolors, file)

    logger.info(f'Products with several colors - {len(multicolors)}')
    logger.info(f'Products with one color - {len(onecolors)}')
    logger.info(f'Exceptions - {len(excepts_url)}')
    fn.report(f'''
    Report GOROD-KOLYASOK
    Products with several colors - {len(multicolors)}\n
    Products with one color - {len(onecolors)}\n
    Exceptions - {len(excepts_url)}\n
    List with one color products - {onecolors}\n
    List with exceptions - {excepts_url}\n
    ''', 'a')
    return multicolors


if __name__ == '__main__':
    filename = ad.files['gorod']
    get_multicolors(filename)
