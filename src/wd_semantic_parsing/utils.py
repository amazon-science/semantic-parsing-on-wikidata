# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0
import os
import io
from os import path
import json
import sqlite3
from datetime import timedelta, date
from typing import Iterable
import logging
from collections import Counter
from pathlib import Path
import subprocess


def init_logging(debug=False):
    logging.basicConfig(level=logging.DEBUG if debug else logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s', datefmt='%Y-%m-%d %H:%M.%S')


def mkdir(dirpath):
    if not path.exists(dirpath):
        os.makedirs(dirpath)


def load_text_lines(filepath, encoding="utf-8"):
    for line in io.open(filepath, encoding=encoding):
        try:
            yield line.strip()
        except Exception:
            logging.error("Error loading line in: %s" % filepath)


def load_dict_pairs(filepath):
    for line in load_text_lines(filepath):
        try:
            string, count = line.split('\t')
            yield (string.strip(), int(count))
        except Exception as e:
            logging.error(e)


def load_dict(filepath, is_counter=False):
    counter = Counter() if is_counter else {}
    for question, count in load_dict_pairs(filepath):
        counter[question] = count
    return counter


def dump_counter(filename, counter, minimum_count=None):
    with io.open(filename, encoding="utf-8", mode='w') as f:
        for string, count in counter.most_common():
            if minimum_count is not None and count < minimum_count:
                break
            try:
                f.write(str("%s\t%d\n" % (string, count)))
            except Exception as e:
                logging.error(e)
    return counter


def get_json_lines(filepath,
                   throw_errors=True,
                   gzipped=False,
                   encoding="utf-8"):
    if gzipped:
        import gzip
        f = gzip.open(filepath, mode='rt', encoding=encoding)
    else:
        f = io.open(filepath, mode='r', encoding=encoding)
    
    line_no = 0
    while True:
        try:
            line_no += 1
            line = f.readline()
            if line == '':
                break
            yield json.loads(line)
        except Exception as e:
            logging.error("Error loading line %d in: %s" % (line_no, filepath))
            if throw_errors:
                raise e


class JsonEntries:
    def __init__(self,
                 filepath: str,
                 append: bool = False):
        self.filepath = filepath
        self.file = open(filepath, 'a' if append else 'w')
        self.count = 0
    
    def save_entry(self, entry):
        self.file.write(json.dumps(entry) + '\n')
        self.count += 1
        return self
    
    def save_entries(self, entries):
        for entry in entries:
            try:
                self.save_entry(entry)
            except Exception as e:
                logging.warn("Fail to save entry due to %s." % e)
        return self
    
    def close(self):
        self.file.close()
    
    def __del__(self):
        self.file.close()



class JsonSQLite:
    def __init__(self, filepath, auto_commit=False):
        new_db = not path.exists(filepath)
        
        self.db = sqlite3.connect(filepath)
        self.cursor = self.db.cursor()
        self.auto_commit = auto_commit
        
        if new_db:
            self.cursor.execute('CREATE TABLE data (key TEXT PRIMARY KEY, value TEXT)')
            self.db.commit()
        
        self.__opened = True
    
    def close(self):
        if self.__opened:
            self.__opened = False
            self.db.commit()
            self.db.close()
    
    def write(self, key, value):
        self.cursor.execute("REPLACE INTO data VALUES (?, ?)", (key, json.dumps(value)))
        if self.auto_commit:
            self.commit()
    
    def commit(self):
        self.db.commit()
    
    def read(self, key):
        self.cursor.execute('SELECT value FROM data WHERE key=?', (key, ))
        row = self.cursor.fetchone()
        if row is None: return None
        return json.loads(row[0])
    
    def iteritems(self):
        for key, value in self.cursor.execute('SELECT key, value FROM data'):
            yield (key, json.loads(value))
    
    def __enter__(self):
        return self
    
    def __del__(self):
        self.db.close()
    
    def __len__(self):
        return self.cursor.execute("SELECT COUNT(*) FROM data").fetchone()[0]
    
    def __exit__(self , *_ ):
        self.close()


def interactive(cli_handler, prompt='\n> ', history_name=None, exit_msg=('quit', 'exit')):
    if history_name:
        set_cli_history(history_name)
    
    try:
        while True:
            command = input(prompt).strip()
            if not command or command in exit_msg: break
            
            if cli_handler(command) == False:
                break
    except EOFError:
        pass


def set_cli_history(history_name):
    try:
        import atexit
        import gnureadline as cli_history
        history_file = Path.home() / ('.%s/cli_history' % history_name)
        if history_file.exists():
            cli_history.read_history_file(history_file)
        else:
            history_file.parents[0].mkdir()
        atexit.register(cli_history.write_history_file, history_file)
    except ImportError:
        logging.info("Unable to find readline module, disabling CLI history.")


def dates(start_date: date, end_date: date) -> Iterable[date]:
    days = (end_date - start_date).days + 1
    for i in range(days):
        yield start_date + timedelta(i)


def format_date(date):
    return date.strftime("%Y%m%d")


def wget(src, trg):
    logging.info(f"Downloading: {src}")
    cmd = ['wget', '--no-check-certificate', '--continue', '-O', trg, src]
    logging.info(' '.join(cmd))
    subprocess.call(cmd)
