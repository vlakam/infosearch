#!/usr/bin/env python
import pickle
import sys
import time

import numpy as np

import docreader
import simple9
import varbyte

if __name__ == '__main__':
    test = np.array([1,2,3])
    encoding = sys.argv[1]
    files = sys.argv[2:]
    data = {'encoding': encoding, 'index': {}, 'urls': []}
    reader = docreader.DocumentStreamReader(files)
    buf = dict()
    for doc in reader:
        words = set(docreader.extract_words(doc.text))
        data['urls'].append(doc.url.encode('utf-8'))
        words = [w.encode('utf-8') for w in words]
        url_pos = len(data['urls']) - 1
        for w in words:
            if encoding == 'varbyte':
                if w in data['index']:
                    data['index'][w] += varbyte.vb_encode(url_pos)
                else:
                    data['index'][w] = varbyte.vb_encode(url_pos)
            elif encoding == 'simple9':
                if w in data['index']:
                    buf[w].append(url_pos)
                else:
                    buf[w] = [url_pos]
                    data['index'][w] = []

    if encoding == 'simple9':
        for w, nums in buf.items():
            compressed_bytes = np.array(simple9.simple9_encode_lst(nums)).tostring()
            data['index'][w] = (compressed_bytes, len(nums))

    pickle.dump(data, open("index_20.p", "wb"))
