import csv
import operator
import scipy
import scipy.stats
import pickle
import random

from pyyacp.yacp import YACParser


def in_range(test_col, col):
    for x in [test_col, col]:
            return False
    if test_col.min > col.max or test_col.max < col.min:
        return False
    else:
        return True


def ks_classify(test_col, column_set, k):
    X = []
    nodes = []
    #logging.debug('KS features')
    for col in column_set:
        #if col and in_range(test_col, col):
        X.append(col.values)
        nodes.append(col)
    ks_test = KolmogorovSmirnov(X, nodes)
    #logging.debug('KS get neighbors')
    return ks_test.getNeighbors(test_col.values, k)


class KolmogorovSmirnov:
    def __init__(self, X, nodes):
        self.X = X
        self.nodes = nodes

    def getNeighbors(self, x, k):
        distances = []
        for i in range(len(self.X)):
            dist, p = scipy.stats.ks_2samp(x, self.X[i])
            distances.append((self.nodes[i], dist))
        distances.sort(key=operator.itemgetter(1))
        neighbors = []
        for i in range(min(k, len(distances))):
            neighbors.append(distances[i])
        return neighbors


class NumCol:
    def __init__(self, header, values):
        self.header = header
        self.values = values
        self.min = min(self.values)
        self.min = max(self.values)


def get_values(filename, col_id):
    # print filename
    tables = YACParser.from_source(filename=filename)

    values = []
    errors = 0
    for t in tables:
        if len(t.header_rows) > 0 and len(t.header_rows[0].cells) > col_id:
            header = t.header_rows[0].cells[col_id].value
        else:
            header = 'MISSING'
        for c in t.columns[col_id].cells:
            try:
                values.append(float(c.value))
            except:
                errors += 1
        break
    if errors > 0:
        print 'NUMBER OF ERRORS:', errors
    return header, values


def get_num_cols():
    path = '/home/neumaier/Repos/doingdatascience/tables/at_dump_v1/'
    all_cols = []
    with open('column_types.csv', 'r') as f:
        csvr = csv.reader(f)
        for row in csvr:
            if row[2] == 'NUMERIC':
                if row[0].startswith('opat'):
                    filename = path + 'da' + row[0]
                else:
                    filename = path + row[0]
                col_id = int(row[1])

                header, values = get_values(filename, col_id)
                if len(values) > 0:
                    col = NumCol(header, values)
                    all_cols.append(col)

    with open('num_col_data.pkl', 'w') as f:
        pickle.dump(all_cols, f)

    return all_cols

def load_num_cols():
    with open('num_col_data.pkl', 'r') as f:
        return pickle.load(f)


if __name__ == '__main__':
    all_cols = load_num_cols()

    test = random.choice(all_cols)
    neighbors = ks_classify(test, all_cols, 20)
    print 'NEIGHBORS:', len(all_cols)
    print 'TESTNODE:', test.header
    print 'VALS:', test.values[:20]
    for i, n in enumerate(neighbors):
        if n[1] > 0:
            print i
            print 'HEADER:', n[0].header
            print 'DIST:', n[1]
            print 'VALS:', n[0].values[:20]
            print