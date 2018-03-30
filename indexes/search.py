#!/usr/bin/env python
import pickle
import sys
import time
import boolean

import numpy as np

import simple9
import varbyte

allIdx = None


class merger:
    def __init__(self, ids):
        self.ids = frozenset(ids)

    def orr(self, rhs):
        return merger(self.ids | rhs.ids)

    def andd(self, rhs):
        return merger(self.ids & rhs.ids)

    def non(self):
        return merger(allIdx.ids.difference(self.ids))


def getIds(encoding, w):
    if encoding == 'varbyte':
        return varbyte.vb_decode(index['index'][w])
    elif encoding == 'simple9':
        compressed_bytes = index['index'][w][0]
        urls_count = index['index'][w][1]
        ints = np.fromstring(compressed_bytes, dtype=np.dtype(int))
        return simple9.simple9_decode_lst(ints)[:urls_count]

def get_doc_ids(encoder, tree):
    if isinstance(tree, boolean.Symbol):
        word = tree.obj.strip().lower().encode('utf-8')
        return merger(getIds(encoder, word))
    elif isinstance(tree, boolean.NOT):
        ids = get_doc_ids(encoder, tree.args[0])
        return ids.non()
    elif isinstance(tree, boolean.AND):
        first = get_doc_ids(encoder, tree.args[0])
        for a in tree.args[1:]:
            first = first.andd(get_doc_ids(encoder, a))
        return first
    elif isinstance(tree, boolean.OR):
        first = get_doc_ids(encoder, tree.args[0])
        for a in tree.args[1:]:
            first = first.orr(get_doc_ids(encoder, a))
        return first
    else:
        raise Exception(u"Unexpected operator!")

if __name__ == '__main__':
    index = pickle.load(open("index_20.p", "rb"))
    allIdx = merger(xrange(len(index['urls'])))
    encoding = index['encoding']
    for query in sys.stdin:
        algebra = boolean.BooleanAlgebra()
        tree_query = algebra.parse(query.decode('utf-8'))
        result = get_doc_ids(encoding, tree_query)
        rl = list(result.ids)
        print query[:-1]
        if len(rl) > 0:
            print len(rl)
            for d in sorted(rl):
                print index['urls'][d]
        else:
            print 0

