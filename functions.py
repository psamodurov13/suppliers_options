import os
os.environ['OPENBLAS_NUM_THREADS'] = '12'
import datetime
import requests as rq
import pandas as pd
from bs4 import BeautifulSoup as bs
from loguru import logger
import auth_data as ad


headers = {
        'User-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15'
    }


def max_colors(data, col_index):
    """The function of counting the maximum number of colors in the product to further create columns in the
    dataframe"""
    max_color = 1
    for prod in data.values:
        if type(prod[col_index]) == str:
            colors = prod[col_index]
            if len(colors.split(';')) > max_color:
                max_color = len(colors.split(';'))
    return max_color


def open_session():
    s = rq.Session()
    return s


def sort_dataframe(data, column):
    data = data.sort_values(column)
    return data


def get_data_img(filename):
    # Create dataframe from suppliers file
    data = pd.read_excel(filename, converters={'ID': str, 'Артикул': str})
    try:
        if filename == ad.files['gorod']:
            data['ID'] = data['Артикул']
    except KeyError:
        logger.exception('Supplier gorod not loading')

    # Create new dataframe
    data_img = data[['Ссылка на товар', 'ID', 'Цвет']]
    columns = list(data_img.columns)

    for i in range(1, max_colors(data_img, 2) + 1):
        columns.append('Цвет' + str(i))
        columns.append('Картинки' + str(i))
    data_img = data_img.reindex(columns, axis=1)
    return data_img


def get_soup(prod, s):
    # get soup for parsing
    colors = prod[2]
    url = prod[0]
    id = prod[1]
    if type(colors) == str:
        logger.info(f'{url} - {colors}')
        response = s.get(url, headers=headers)
        response.encoding = 'utf-8'
        soup = bs(response.text, 'html.parser', )
        result = (soup, response, colors, url, id)
    else:
        result = None
    return result


def add_row_dfimg(data_img, url, color, images, column_number):
    # Add color name and photos to dataframe
    data_img.loc[data_img['Ссылка на товар'] == url, 'Цвет' + str(column_number)] = color
    data_img.loc[data_img['Ссылка на товар'] == url, 'Картинки' + str(column_number)] = ', '.join(
        images)
    column_number += 1
    return data_img, column_number


def report(text, mode):
    print(text)
    with open('report.txt', mode) as file:
        file.write(text)

