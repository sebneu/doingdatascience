#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
Created on Mar 6, 2016

.. codeauthor: svitlana vakulenko <svitlana.vakulenko@gmail.com>
'''

from __future__ import division
from hashes.simhash import simhash


def hamming_distance(a, b, base):
    """Calculate the Hamming distance between two bit strings"""
    if len(a) == len(b):
        count, z = 0, int(a, base) ^ int(b, base)
        while z:
            count += 1
            z &= z-1
        return count
    else:
        print 'Hash strings need to be of the same length'


class HashFunction():

    def __init__(self, hashbits=12):
        self.hash_base = 10
        self.hashbits = hashbits

    def compute_hash(self, text):
        raise NotImplemented

    def prepare_input(self, text):
        return text

    def distance_function(self, doc_a, doc_b):
        # percentage-wise
        return hamming_distance(doc_a, doc_b, self.hash_base)/len(doc_a)


class SimHash(HashFunction):

    def __init__(self, hashbits=64):
        HashFunction.__init__(self)
        self.hash_base = 16
        self.hashbits = hashbits

    def compute_hash(self, text):
        return simhash(text, hashbits=self.hashbits)#.hex()


class NilsimsaHash(HashFunction):

    def __init__(self):
        HashFunction.__init__(self)
        self.hash_base = 16

    def compute_hash(self, text):
        from nilsimsa import Nilsimsa
        result = Nilsimsa(data=text)
        result = result.hexdigest()
        return str(result)


def test_hashing_function():
    hash_func = NilsimsaHash()
    print hash_func.compute_hash('yes!')
    print hash_func.compute_hash('yes')


def test_similarity_function():
    hash_func = NilsimsaHash()
    str_long = hash_func.compute_hash('yes!')
    str_short = hash_func.compute_hash('yes')
    str_other1 = hash_func.compute_hash('no')
    str_other2 = hash_func.compute_hash('not')
    print str_long
    print str_short
    print str_other1
    print str_other2
    print len(str_long)  # length of hash string
    print hash_func.distance_function(str_long, str_short)  # similar
    print hash_func.distance_function(str_long, str_other1)  # different
    print hash_func.distance_function(str_long, str_other2)  # different
    assert hamming_distance(str_long, str_long, 16) == 0
    print hamming_distance(str_long, str_short, 16)
    print hamming_distance(str_long, str_other1, 16)


if __name__ == '__main__':
    test_similarity_function()
