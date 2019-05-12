# coding=utf-8
import pandas as pd
import numpy as np
from multiprocessing.pool import Pool
from multiprocessing import Lock
import sys

from trie import Trie

sys.setrecursionlimit(5000)
a = pd.read_csv('./words.freq.csv', keep_default_na=False)
trie = Trie()
trie.load()
csv = open('subzzbzbzzz.csv', 'w')
csv.write('Id,Expected\n')
input = list(a['Id'])
def process(word):
    result = word
    findings = trie.fuzzy_search(word)
    if (len(findings)):
        result = findings[0].word
    print(word, result)
    return word, result

pool = Pool(7)
for word, fix in pool.map(process, input, chunksize=1):
    csv.write(str(word) + ',' + str(fix) + '\n')
csv.close()