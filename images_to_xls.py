import os
os.environ['OPENBLAS_NUM_THREADS'] = '12'
import datetime
from stat import S_ISREG, ST_CTIME, ST_MODE
import pandas as pd
import pickle
from loguru import logger
import functions as fn
import auth_data as ad
from rich.progress import track


def get_file(export_type):
    # Get last export file
    all_xlsx = []
    for file in os.listdir(ad.downloads_catalog):
        if file.endswith('.xlsx') and file.startswith(f'{export_type}-'):
            all_xlsx.append(ad.downloads_catalog + file)

    entries = (os.path.join(ad.downloads_catalog, fn) for fn in all_xlsx)
    entries = ((os.stat(path), path) for path in entries)
    entries = ((stat[ST_CTIME], path) for stat, path in entries if S_ISREG(stat[ST_MODE]))
    return os.path.abspath(list(reversed(sorted(entries)))[0][1])


def get_dataframe(filename):
    sheets = pd.ExcelFile(filename, engine='openpyxl').sheet_names
    all_sheets = {}
    for i in sheets:
        all_sheets[i] = pd.read_excel(filename, i, engine='openpyxl', converters={'sku': str, 'model': str})
        logger.info(f'{i} loaded')
    for i in all_sheets:
        for c in all_sheets[i].columns:
            if all_sheets[i][c].dtype == bool:
                all_sheets[i][c] = all_sheets[i][c].astype('str')
                logger.info(f'{i} ==> {c}: replaced by str')
    return all_sheets


def save_dataframe(df, name):
    writer = pd.ExcelWriter(name, engine='xlsxwriter')
    for sheetname in df.keys():
        df[sheetname].to_excel(writer, sheet_name=sheetname, index=False)
    writer.save()
    logger.info(f'File {name} created')


def add_related(data, related):
    # with open(related_pickle, 'rb') as file:
    #     related = pickle.load(file)
    for i in related:
        result = []
        for rel in related[i]:
            res = data['Products']['product_id'].values[data['Products']['model'] == rel][0]
            result.append(str(res))
        logger.info(f'{i} - {",".join(result)}')
        logger.info(data['Products'][data['Products']['model'] == i])
        data['Products'].loc[data['Products']['model'] == i, 'related_ids'] = ','.join(result)
    save_dataframe(data, 'products_for_upload_with_related.xlsx')
    return data


def edit_files(products_images, related):
    options_file = get_file('options')
    logger.info(f'OPTIONS - {options_file}')
    products_file = get_file('products')
    logger.info(f'PRODUCTS - {products_file}')

    s = fn.open_session()
    options_data = get_dataframe(options_file)
    new_values = []
    for prod in products_images:
        for option_name in products_images[prod]:
            new_values.append(option_name)
    logger.debug(f'Total new options - {len(new_values)}')
    new_values = set(new_values)
    logger.debug(f'Total new unique options - {len(new_values)}')
    option_id = options_data['Options']['option_id'][options_data['Options']['name(ru-ru)'] == 'Цвет']
    option_id = option_id.values[0]

    last_value_id = options_data['OptionValues'].values[-1][0]

    for value in new_values:
        last_value_id += 1
        row = [last_value_id, option_id, '', '0', value]
        check_opt = options_data['OptionValues'][options_data['OptionValues']['name(ru-ru)'] == value]
        if check_opt.empty:
            options_data['OptionValues'].loc[len(options_data['OptionValues'].index)] = row
            logger.info(f'Add option {value}')
        else:
            logger.info(f'Skip option {value}')

    save_dataframe(options_data, 'options_for_upload.xlsx')

    products_data = get_dataframe(products_file)
    for product in track(products_images, description='[red] rewrite products', style='red'):
        sku = product
        try:
            prod_id = products_data['Products']['product_id'][products_data['Products']['model'] == sku]
            prod_id = prod_id.values[0]
            for option in products_images[product]:
                logger.debug(f'{option}')
                option_value_id = options_data['OptionValues'][options_data['OptionValues']['name(ru-ru)'] == str(option).strip()]
                logger.debug(f'{option_value_id}')
                option_value_id = option_value_id.values[0][0]
                logger.debug(f'{option_value_id}')
                check_df = products_data['ProductOptionValues'][(products_data['ProductOptionValues']['product_id'] == prod_id) &
                                                    (products_data['ProductOptionValues']['option_value_id'] == option_value_id)]
                if check_df.empty:
                    row = [prod_id, option_id, option_value_id, ad.quantity, 'true', '0', '+', '0', '=', '0', '=',
                           '', '', '', '', '', '', '', '', '', '']
                    count = 11
                    for img in products_images[product][option][:10]:
                        image = s.get(img, headers=fn.headers)
                        img_filename = img.split('/')[-1].replace('%', '')
                        with open(f'{ad.site_directory}image/catalog/options_img/{img_filename}', 'wb') as file:
                            file.write(image.content)
                        row[count] = f'catalog/options_img/{img_filename}'
                        count += 1
                    products_data['ProductOptionValues'].loc[len(products_data['ProductOptionValues'].index)] = row
                    logger.info(f'add option value {prod_id} {option}')
                else:
                    logger.info(f'skip option value {prod_id} {option}')
            check_df_opt = products_data['ProductOptions'][products_data['ProductOptions']['product_id'] == prod_id]
            if check_df_opt.empty:
                products_data['ProductOptions'].loc[len(products_data['ProductOptions'].index)] = [prod_id, option_id, '', 'True']
                logger.info(f'add option {prod_id}')
            else:
                logger.info(f'skip option {prod_id}')
            print('-' * 50)
        except IndexError:
            logger.exception(f'not in file - {product}')

    products_data['ProductOptionValues'] = fn.sort_dataframe(products_data['ProductOptionValues'], 'product_id')
    products_data['ProductOptions'] = fn.sort_dataframe(products_data['ProductOptions'], 'product_id')

    data = add_related(products_data, related)
    save_dataframe(data, 'products_for_upload.xlsx')


if __name__ == '__main__':
    with open('products_images.pickle', 'rb') as file:
        products_images = pickle.load(file)
    with open('moon_official_related.pickle', 'rb') as file:
        related = pickle.load(file)
    edit_files(products_images, related)