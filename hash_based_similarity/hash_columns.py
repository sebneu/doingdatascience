#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
Created on Mar 5, 2016

.. codeauthor: svitlana vakulenko <svitlana.vakulenko@gmail.com>
'''

import os
import pandas as pd
import numpy as np
import anycsv

from hash_functions import NilsimsaHash, SimHash
from hashes.simhash import simhash
from itertools import combinations, permutations
from column_types_reader import get_textual_columns

PATH = '../data/at_dump_v1'
FILES = ['opat/httpwww.wienticket.atfeedsvorverkauf.phpformatcsv',
         'opat/httpwww.apcs.atapcsausgleichsenergiemarktstatistikenopendatastatistikrz2013.csv']


def get_files_from_dir(root, file_type='csv'):
    result = []
    for base, subdirs, files in os.walk(root):
        for name in files:
            if name.lower().endswith('.%s' % file_type.lower()):
                fp = os.path.join(base, name)
                result.append(fp)
    return result


def read_tables(fps, delimiter, shuffle=False, limit=False):
    '''
    Input:
    fps <list of strings>  full paths to files to read tables from

    Output:
    tables <dict> {file_path: rows_generator}
    '''
    tables = {}
    for path in fps:
        df = pd.read_csv(path, sep=delimiter)
        if shuffle:
            df_shuffled = df.iloc[np.random.permutation(len(df))]
            df_shuffled.reset_index(drop=True)
            df = df_shuffled
        if limit:
            df = df[:limit]
        tables[path] = df
    return tables


def test_read_tables():

    # collect file paths
    fps = []
    for file in FILES:
        fps.append(os.path.join(PATH, file))
    print fps
    tables = read_tables(fps, delimiter=';')
    for path, table in tables.items():
        print path
        # print header - columns' labels
        print table.columns.values


def hash_column_str(hash_func, column):
    '''
    Input:
    column <Series>  one column from pandas data frame

    Output:
    hash <str> hash value of the column
    '''
    column_str = str(column)
    return hash_func.compute_hash(column_str)


def hash_column_row_by_row(column, hash_func=None, hash_it=True, ziped=False):
    '''
    Input:
    column <Series>  one column from pandas data frame

    Output:
    hash <str> hash value of the column
    '''

    # column.apply(hash)
    # collect/cluster similar hashes into baskets
    hash_baskets = []
    value_baskets = []
    hash_dic = {}
    for row in column:
        # hash only the first row
        row_value = str(row).strip()

        if hash_it and hash_func:
            row_hash = hash_func.compute_hash(row_value)
            basket_item = row_hash
        else:
            basket_item = row_value
        if basket_item not in hash_baskets:
            hash_baskets.append(basket_item)
            if ziped:
                value_baskets.append(row_value)
            hash_dic[basket_item] = row_value
    # all fields are identical -> single basket for the column
    # if len(baskets) == 1:
    #     return baskets[0]
    # else:
    if ziped:
        return zip(set(hash_baskets), set(value_baskets))
    else:
        return hash_dic


def test_hash_column1(n_rows=False):
    '''
    Input:
    n_rows <int>  limit the number of rows processed from the column
    '''
    fp = os.path.join(PATH, FILES[0])  # choose first sample file
    table = read_tables([fp], delimiter=';')[fp]  # get the table as a df
    print table.columns.values  # show the header
    # get one column of the table
    column = table['Ort']
    # if n_rows:
    #     column = column[:n_rows]    # n times 'Wien'
    # print column  # class Series, shows column info: length and data type
    # represent column as a string
    # hash
    hash_func = NilsimsaHash()
    print hash_column_str(hash_func, column)
    baskets = hash_column_row_by_row(hash_func, column)
    print baskets
    print len(baskets)


def test_hash_column_length():
    fp = os.path.join(PATH, FILES[0])  # choose first sample file
    table = read_tables([fp], delimiter=';')[fp]  # get the table as a df
    print table.columns.values  # show the header
    # get one column of the table
    column = table['Ort'][:1000]
    print column
    column_short = column[:5]  # first 10 rows
    print column_short
    # hash
    hash_func = NilsimsaHash()
    column_hash = hash_column_str(hash_func, column)
    print column_hash
    column_short_hash = hash_column_str(hash_func, column_short)
    print hash_func.distance_function(column_hash, column_short_hash)
    # assert hash_func.distance_function(column_hash, column_short_hash) == 0
    # test row by row hash function
    column_hash = hash_column_row_by_row(hash_func, column)
    print column_hash
    # print int(column_hash, hash_func.hash_base)*2
    column_short_hash = hash_column_row_by_row(hash_func, column_short)
    # print hash_func.distance_function(column_hash, column_short_hash)
    # assert hash_func.distance_function(column_hash, column_short_hash) == 0


def test_hash_functions(texts=['test1test1test1', 'testtest1test1'], hashbits=8):
    hashes = []
    for text in texts:
        # hash_func1 = NilsimsaHash()
        # print hash_func1.compute_sh(text)
        hash_func2 = SimHash(hashbits)
        hashes.append(hash_func2.compute_hash(text))
    pairs = list(combinations(hashes, 2))
    # print pairs
    for hash1, hash2 in pairs:
        print hash1.similarity(hash2)
        print hash_func2.distance_function(hash1.hex(), hash2.hex())


def compare_baskets(basket1, basket2, hashbits=8):
    # exhaustive enumeration of pair combinations
    # print len(basket2)
    # if len(basket1) >= len(basket2):
    #     list1, list2 = basket1, basket2
    # else:
    #     list2, list1 = basket1, basket2
    # pairs = [zip(x,list2) for x in combinations(list1,len(list2))]
    # print pairs
    # print len(pairs)
    hash_func = SimHash(hashbits)
    for hash1 in basket1:
        for hash2 in basket2:
    # for hash1, hash2 in pairs:
            if hash1.similarity(hash2) > 0.6:
                print hash1.hex(), hash2.hex()

            # print hash_func.distance_function(hash1, hash2)


def hash_column_rows(column):
    '''
    Input:
    column <Series>  one column from pandas data frame

    Output:
    [] hash <str> list of hash strings as the column representation
    '''

    # column.apply(hash)
    # collect/cluster similar hashes into baskets
    # baskets = []
    # for row in column:
    #     # hash only the first row
    #     row_value = str(row).strip()
    #     row_hash = hash_func.compute_hash(row_value)
    #     basket_item = row_value
    #     if basket_item not in baskets:
    #         baskets.append(basket_item)
    # all fields are identical -> single basket for the column
    # if len(baskets) == 1:
    #     return baskets[0]
    # else:
    baskets = simhash(column)
    return baskets


def test_hash_column_rows():
    fp = os.path.join(PATH, FILES[0])  # choose first sample file
    table = read_tables([fp], delimiter=';')[fp]  # get the table as a df
    print table.columns.values  # show the header
    # get one column of the table
    column = table['Ort'][:1000]
    print column
    column_short = column[:5]  # first 10 rows
    print column_short
    print hash_column_rows(column_short)


def test_split_column(split_row=False, limit=120, hashbits=8, hash_it=True):
    '''
    Input:
    split_row <int>  index of the row on which to split the column in two
    '''
    fp = os.path.join(PATH, FILES[0])  # choose first sample file
    table = read_tables([fp], delimiter=';')[fp]  # get the table as a df
    # print table.columns.values  # show the header
    # get one column of the table
    column = table['Ort']
    if limit:
        column = column[:limit]
    if not split_row:
        # split the column in halves
        n_rows = len(column)   # the total number of rows
        half = n_rows/2
    column1 = column[:half]
    # print len(column1)
    column2 = column[half:]
    # print len(column2)
    # compute hash basket representations for each column
    hash_func = SimHash(hashbits)
    column1_baskets = hash_column_row_by_row(column1, hash_func, hash_it)
    print column1_baskets
    column2_baskets = hash_column_row_by_row(column2, hash_func, hash_it)
    print column2_baskets
    for hash_obj, value in column2_baskets:
        print hash_obj.hex(), value
    # print column1_baskets.intersection(column2_baskets)
    # compare_baskets(column1_baskets, column2_baskets)


def test_simhash_sort(hashbits=8, limit=120):
    fp = os.path.join(PATH, FILES[0])  # choose first sample file
    table = read_tables([fp], delimiter=';')[fp]  # get the table as a df
    # print table.columns.values  # show the header
    # get one column of the table
    column = table['Ort']
    if limit:
        column = column[:limit]
    hash_func = SimHash(hashbits)
    column_hash_dic = hash_column_row_by_row(column, hash_func)
    hashes = column_hash_dic.keys()
    hashes.sort()
    # show sorted hashes
    print hashes
    for item in hashes:
        print column_hash_dic[item]


def hash_column(column, hash_func):
    hashed_column = hash_func.compute_hash(column)
    # print hashed_column.hex()
    return hashed_column


def sample_column(limit, shuffle=False):
    fp = os.path.join(PATH, FILES[0])  # choose first sample file
    # get the table as a df
    table = read_tables([fp], delimiter=';', shuffle=shuffle)[fp]
    column = table['Ort']
    if limit:
        column = column[:limit]
    # print column
    return column


def column_in_half(column, hash_func):
    # split the column into halves
    columns = []
    n_rows = len(column)   # the total number of rows
    half = n_rows/2
    columns.append(column[:half])
    # print len(column[:half])
    # print column[:half]
    columns.append(column[half:])
    # print len(column[half:])
    # print column[half:]
    # return {'Ort1': column[:half], 'Ort2': column[:half]}
    hashes = []
    for column in columns:
        # column = table[label]
        # columns[label] =
        hashed_column = hash_column(column, hash_func)
        hashes.append(hashed_column)
    return {hashes[0]: 'Ort1', hashes[1]: 'Ort2'}


def test_hash_column(hashbits=8, limit=False):
    # get a sample column
    # column = sample_column(limit, shuffle=True)
    fp = os.path.join(PATH, FILES[0])  # choose first sample file
    # get the table as a df
    table = read_tables([fp], delimiter=';', shuffle=True, limit=limit)[fp]
    # print header - columns' labels
    # print table.columns.values
    # print table
    n_rows = len(table)
    print n_rows

    # produce hashes for columns
    column_labels = ['Adresse', 'Vorverkaufstelle']
    # columns = {}
    hashes = {}
    hash_func = SimHash(hashbits)
    for label in column_labels:
        # get the half
        # print label
        column = table[label][:n_rows/2]
        # print list(column)
        print len(column)
        # columns[label] =
        hashed_column = hash_column(column, hash_func)
        hashes[hashed_column] = label

    hashes.update(column_in_half(table['Ort'], hash_func))

    # compare the hashes
    pairs = list(combinations(hashes.keys(), 2))
    # print pairs
    for hash1, hash2 in pairs:
        print hashes[hash1], hashes[hash2]
        print hash1.similarity(hash2)


def hash_columns(hashbits=8, limit=None):
    hashes = {}
    hash_func = SimHash(hashbits)
    textual_columns_iterator = get_textual_columns(limit)
    for i, column_description in textual_columns_iterator:
        file = column_description['file']
        col_id = column_description['column']
        label = file + '_' + str(col_id)
        print "Column: " + label
        fp = os.path.join(PATH, file)  # choose first sample file
        # get the table as a df
        # df = pd.read_csv(fp)
        try:
            csvr = anycsv.reader(filename=fp)
            # skip first 3 lines to avoid description and header lines
            h = csvr.next()
            h = csvr.next()
            h = csvr.next()
            while len(h) <= 1:
                # possibly description line
                h = csvr.next()
            # setup columns
            columns = [[] for _ in range(len(h))]
            for row in csvr:
                for i, cell in enumerate(row):
                    columns[i].append(cell)
            # for col_id, c in enumerate(columns):
            #     print col_id
            column = columns[col_id]
            print "of length " +  str(len(column))
            hashed_column = hash_column(column, hash_func).hex()
            if hashed_column not in hashes.keys():
                hashes[hashed_column] = []
            hashes[hashed_column].append(label)
        except Exception as e:
            print e

    # print hashes
    similar_columns = [bucket for bucket in hashes.values() if len(bucket) > 1]
    # print similar_columns
    print "Found " + str(len(similar_columns)) + " groups of similar columns:"
    for cluster in similar_columns:
        print str(len(cluster)) + " similar columns:"
        print cluster


if __name__ == '__main__':
    test_hash_column()
    # hash_columns()
