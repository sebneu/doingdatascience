#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Created on Jun 17, 2016

.. codeauthor: svitlana vakulenko
    <svitlana.vakulenko@gmail.com>

'''

import pandas as pd


class ColumnTypesReader():
    """
    Class for reading the column_types.csv file
    and filtering the columns of the specified data types
    """

    def __init__(self, columns_file, delimiter):
        self.df = pd.read_csv(columns_file, sep=delimiter)

    def get_rows_by_column(self, column_name, column_values):
        """
        column_name String
        column_values list
        """
        return self.df.loc[self.df[column_name].isin(column_values)]

    def get_columns_by_types(self, data_types):
        return self.get_rows_by_column('type', data_types)


def get_textual_columns():
    reader = ColumnTypesReader('column_types.csv', ',')
    textual_columns = reader.get_columns_by_types(['TEXT'])
    assert len(textual_columns) == 510
    return textual_columns.iterrows()


if __name__ == '__main__':
    textual_columns_iterator = get_textual_columns()
    for i, column in textual_columns_iterator:
        print column['file'], column['column']
