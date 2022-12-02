import auth_data as ad
import datetime
from loguru import logger
import images_to_xls as itx
import farfello
import aisttm
import gorod_kolyasok
import moon_official
import functions as fn

logger.remove()
logger.add('debug.log', format='{time} {level} {message}', level="INFO", rotation="15 MB", compression="zip")

logger.info(f'Start {datetime.datetime.now()}')


def main():
    fn.report(f'Start {datetime.datetime.now()}', 'w')
    product_images = {}
    try:
        product_images.update(farfello.get_multicolors(ad.files['farfello']))
        logger.info('farfello loaded')
    except Exception:
        logger.exception('farfello not loading')
    try:
        product_images.update(aisttm.get_multicolors(ad.files['aisttm']))
        logger.info('aisttm loaded')
    except Exception:
        logger.exception('aisttm not loading')
    try:
        product_images.update(gorod_kolyasok.get_multicolors(ad.files['gorod']))
        logger.info('gorod_kolyasok loaded')
    except Exception:
        logger.exception('gorod_kolyasok not loading')

    moon_official_related = {}
    try:
        moon_official_related = moon_official.get_related(ad.files['moon-official'])
        logger.info('moon_official loaded')
    except Exception:
        logger.exception('moon_official not loading')

    itx.edit_files(product_images, moon_official_related)


if __name__ == '__main__':
    main()
