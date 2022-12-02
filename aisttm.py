import os
os.environ['OPENBLAS_NUM_THREADS'] = '12'
import datetime
import pandas as pd
import functions as fn
from loguru import logger
import auth_data as ad
import pickle
from rich.progress import track


multicolors = {}
onecolors = []
excepts_url = []


@logger.catch
def get_multicolors(filename):
    data_img = fn.get_data_img(filename)

    # Create session
    s = fn.open_session()

    for prod in track(data_img.values, description='[green] Обход товаров AISTTM', style='green'):
        result = fn.get_soup(prod, s)
        if result:
            soup, response, colors, url, id = result
            try:
                # Get colors name in the same order as that pictures
                all_colors = {i.get('title').replace('Цвет:', '').strip(): i.find('img').get('src').split('/')[-1]
                              for i in soup.select('div.block-property-color-item')}
                # Get sliders with pictures for each color
                sliders = soup.select('div.product-item-detail-slider-controls-block div.swiper-wrapper')
                column_number = 1
                multicolors[str(id) + '-02'] = {}
                # iterate indexes and add to dict {color: img}
                for i in range(len(sliders)):
                    images_tags = sliders[i].select('.product-item-detail-slider-controls-image img')
                    images = ['https://www.aisttm.ru' +
                              img.get('src').replace('/resize_cache', '').replace('/80_80_1', '')
                              for img in images_tags]
                    color = ''
                    for item in all_colors:
                        if all_colors[item] == images[0].split('/')[-1]:
                            color = item
                    if color:
                        multicolors[str(id) + '-02'][color] = images
                        data_img, column_number = fn.add_row_dfimg(data_img, url, color, images, column_number)
                    else:
                        continue
                    logger.info(f'Color - {color}. Images - {images}')
            except Exception:
                logger.exception(f'Exception on product page - {url}')
                excepts_url.append(url)
        else:
            logger.debug(f'Product with one single color - {prod[0]}')
            onecolors.append({prod[0]})
        logger.info('-' * 40)

    with pd.ExcelWriter('full_aisttm.xlsx', engine='xlsxwriter', options={'strings_to_urls': False}) as writer:
        data_img.to_excel(writer, sheet_name='Sheet')

    with open('aisttm_images.pickle', 'wb') as file:
        pickle.dump(multicolors, file)

    logger.info(f'Products with several colors - {len(multicolors)}')
    logger.info(f'Products with one color - {len(onecolors)}')
    logger.info(f'Exceptions - {len(excepts_url)}')
    fn.report(f'''
    Report AISTTM
    Products with several colors - {len(multicolors)}\n
    Products with one color - {len(onecolors)}\n
    Exceptions - {len(excepts_url)}\n
    List with one color products - {onecolors}\n
    List with exceptions - {excepts_url}\n
    ''', 'a')
    return multicolors


if __name__ == '__main__':
    filename = ad.files['aisttm']
    get_multicolors(filename)
