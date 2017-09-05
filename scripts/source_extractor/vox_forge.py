from __future__ import absolute_import

import glob
import shutil
import tarfile
import tempfile

from bs4 import BeautifulSoup
import requests

from source_extractor.constants import (
    OUTPUT_DIR,
    CATEGORIZED_DIR
)

from logger import get_logger
from concurrent_fetcher import ConcurrentFetcher

CATALOG_URL = 'http://www.repository.voxforge1.org/downloads/SpeechCorpus/Trunk/Audio/Main/8kHz_16bit/?C=M;O=D'

ROOT_URL = 'http://www.repository.voxforge1.org/downloads/SpeechCorpus/Trunk/Audio/Main/8kHz_16bit/'

failed_files = []

logger = get_logger(__name__)


def parser(raw_html):
    links = []
    bs = BeautifulSoup(raw_html, 'html.parser')
    for link in bs.find_all('a'):
        href = str(link.get('href'))
        if href.endswith('.tgz'):
            links.append(href)
    logger.debug('Found %d links', len(links))
    return links


def fetch_catalog(url):
    logger.debug('Fetching audio at %s', url)
    a = requests.get(url)
    if not a.ok:
        logger.error('Status is not 200')
        return None
    webpage = a.content
    return webpage


def runner():
    processed_count = 0
    """
    Concurrently fetch URLs from Vox Forge
    """
    if len(glob.glob(OUTPUT_DIR.format('*'))) > 0:
        logger.debug('Not executing web-crawl. Files are at ' + OUTPUT_DIR.format(''))
    else:
        catalog_webpage = fetch_catalog(CATALOG_URL)
        relative_links = parser(catalog_webpage)
        full_urls = [ROOT_URL + rel_link for rel_link in relative_links]
        cf = ConcurrentFetcher(urls_list=full_urls, processing_callback=process_each_catalog_link)
        cf.run()
    logger.debug('Unpacking tars')
    files = glob.glob(OUTPUT_DIR.format('*'))
    for f in files:
        logger.debug('Unpacking %s', f)
        unpack_tgz(f)
        processed_count += 1
        logger.info('Processed %d of %d files', processed_count, len(files))


def process_each_catalog_link(request_obj, link):
    tgz = request_obj.content
    fname = OUTPUT_DIR.format(link)
    logger.debug('Opening file for output {}'.format(fname))
    f = open(fname, 'wb+')
    f.write(tgz)
    f.close()
    logger.debug('Wrote file {}'.format(fname))


def wav_renamer(read_path, gender_char, output_dir):
    if not output_dir.endswith('/'):
        output_dir += '/'
    local_name = read_path.split('/')[-1]
    recorder = read_path.split('/')[-3]
    write_path = output_dir + gender_char + '_' + recorder + '_' + local_name
    logger.debug('Generating file at %s', write_path)
    shutil.copyfile(read_path, write_path)


def readme_extractor(path_to_readme):
    """
    Returns U if gender isn't in the readme
    F or M if gender is listed as female or male
    O if gender if listed but isn't the specified string
    """
    gender_letter = 'U'
    with open(path_to_readme) as readme:
        for line in readme.readlines():
            ll = line.lower()
            if ll.startswith('gender'):
                # Real-life fizzbuzz
                if 'female' in ll:
                    gender_letter = 'F'
                elif 'male' in ll:
                    gender_letter = 'M'
                else:
                    gender_letter = 'O'
    return gender_letter


def unpack_tgz(fpath):
    if not tarfile.is_tarfile(fpath):
        raise Exception("{} is not a tar file".format(fpath))
    tempfile_path = tempfile.mkdtemp() + '/'
    logger.debug('Added temporary file at %s', tempfile_path)
    try:
        gender_char = ''
        tf = tarfile.open(fpath, 'r:*')
        logger.debug('Opened file')
        relevant_files = [
            x for x in tf.getmembers()
            if x.name.endswith('.wav') or x.name.endswith('README')
        ]
        # Extract to tempfile dir
        for f in relevant_files:
            logger.debug('Unpacking %s', f.name)
            tf.extract(f, tempfile_path)
        files_at_temp = glob.glob(tempfile_path + '*/*/*')
        logger.debug('Current files in temp directory: %s', str(files_at_temp))
        # Get speaker gender
        readme_fpath = [x for x in files_at_temp if x.endswith('README')][0]
        logger.debug('Getting README at %s', readme_fpath)
        gender_char = readme_extractor(readme_fpath)
        logger.debug('Gender of speaker is %s', gender_char)
        # Get write data out
        wavs = [f for f in files_at_temp if f.endswith('.wav')]
        for wav in wavs:
            wav_renamer(wav, gender_char, CATEGORIZED_DIR)
    except Exception:
        logger.warn("Failed to process %s", fpath)
        failed_files.append(fpath)
    finally:
        shutil.rmtree(tempfile_path)
