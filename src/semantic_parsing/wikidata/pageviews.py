# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0
from os import path
import gzip
from collections import Counter
from datetime import datetime, timedelta
import logging

from semantic_parsing.wikidata import WIKIDATA_PAGEVIEWS_URL, WIKIDATA_PAGEVIEWS_DIR, WIKIDATA_PAGEVIEWS
from semantic_parsing.utils import init_logging, dates, dump_counter, load_dict, mkdir, format_date, wget


PAGEVIEWS_FILE = 'pageviews-%Y%m%d-%%02d0000.gz'
NUM_DAYS = 7


def load_views(filepath, url, domain_code='en'):
    logging.info("Extracting pageviews from: %s" % filepath)
    counter_cache = "%s_%s.counter" % (filepath, domain_code)
    if path.exists(counter_cache):
        return load_dict(counter_cache, is_counter=True)
    
    if not path.exists(filepath):
        wget(url, filepath)
    
    views = Counter()
    for i, line in enumerate(gzip.open(filepath, mode='rt', encoding='utf-8'), 1):
        if (i % 1000000) == 0: logging.info("Processed Lines: %d" % i)
        tokens = line.split()
        if len(tokens) != 4: continue
        domain, page, count, _ = tokens
        if domain != domain_code: continue
        views[page] += int(count)
    dump_counter(counter_cache, views)
    return views


def get_dayly_pageviews(date, domain_code='en'):
    logging.info("Getting pageviews for: %s" % date)
    views_file = path.join(WIKIDATA_PAGEVIEWS_DIR, '%s_views.daily' % format_date(date))
    if path.exists(views_file):
        return load_dict(views_file, is_counter=True)
    
    views = Counter()
    url_base = date.strftime(WIKIDATA_PAGEVIEWS_URL)
    file_base = date.strftime(PAGEVIEWS_FILE)
    for hour in range(0, 24):
        filename = file_base % hour
        url = url_base + filename
        filepath = path.join(WIKIDATA_PAGEVIEWS_DIR, filename)
        views += load_views(filepath, url, domain_code)
    dump_counter(views_file, views)
    return views


def download_pageviews_data(domain_code='en'):
    mkdir(WIKIDATA_PAGEVIEWS_DIR)
    end_date = datetime.now() - timedelta(days=1)
    start_date = end_date - timedelta(days=(NUM_DAYS - 1))
    views = Counter()
    days = list(dates(start_date, end_date))
    days.reverse()
    for date in days:
        views += get_dayly_pageviews(date, domain_code)
    
    dump_counter(WIKIDATA_PAGEVIEWS, views)


if __name__ == '__main__':
    init_logging()
    download_pageviews_data()
