'''
Creates column_types.csv
'''
import csv
import json

import anycsv
import os
from collections import defaultdict

import operator


class ColumnLabel:
    NUMERIC = 'NUMERIC'
    ENTITY = 'ENTITY'
    TEXT = 'TEXT'
    ID = 'ID'

def isfloat(value):
  try:
    float(value)
    return True
  except:
    return False

def get_label(v):
    if v.isnumeric() or isfloat(v):
        return ColumnLabel.NUMERIC
    if isfloat(v):
        return ColumnLabel.NUMERIC
    return ColumnLabel.TEXT


class Column:
    def __init__(self, values):
        self.values = values
        self._classify()

    def _classify(self):
        self.char_dist = defaultdict(int)
        labels = defaultdict(int)
        lengths = defaultdict(int)
        tokens = defaultdict(int)

        for value in self.values:
            for c in value:
                self.char_dist[c] += 1

            labels[get_label(value)] += 1
            lengths[len(value)] += 1
            tok = len(value.split(' '))
            length = '4+' if tok >= 4 else str(tok)
            tokens[length] += 1

        if len(labels) == 1 and ColumnLabel.NUMERIC in labels:
            self.label = ColumnLabel.NUMERIC
        elif len(lengths) == 1:
            self.label = ColumnLabel.ID
        elif '4+' in tokens and tokens['4+'] >= len(self.values) * 0.3:
            self.label = ColumnLabel.TEXT
        else:
            self.label = ColumnLabel.ENTITY

        self.length = max(tokens.iteritems(), key=operator.itemgetter(1))[0]


if __name__ == '__main__':
    col_stats = {'labels': defaultdict(int), 'lengths': defaultdict(int), 'columns': 0, 'tables': 0, 'errors': 0}

    classification = [['file', 'column', 'type', 'avg_tokens']]

    for root, subdirs, files in os.walk('tables'):
        for filename in files:
            if filename.endswith('.csv'):
                try:

                    path = os.path.join(root, filename)
                    csvr = anycsv.reader(filename=path)
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
                    for col_id, c in enumerate(columns):
                        col = Column(c)
                        col_stats['labels'][col.label] += 1
                        col_stats['lengths'][col.length] += 1
                        col_stats['columns'] += 1
                        classification.append([path.lstrip('tables/at_dump_v1/'), col_id, col.label, col.length])
                    col_stats['tables'] += 1
                    print 'processed table: ', filename
                except Exception as e:
                    print e
                    col_stats['errors'] += 1

    with open('col_stats.json', 'w') as f:
        json.dump(col_stats, f)

    with open('column_types.csv', 'w') as f:
        csvw = csv.writer(f)
        csvw.writerows(classification)
