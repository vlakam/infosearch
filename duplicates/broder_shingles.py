#!/usr/bin/env python

"""
This is just a draft for homework 'near-duplicates'
Use MinshinglesCounter to make result closer to checker
"""

import sys
import re
import mmh3
from docreader import DocumentStreamReader


class MinshinglesCounter:
    SPLIT_RGX = re.compile(r'\w+', re.U)

    def __init__(self, window=5, n=20):
        self.window = window
        self.n = n

    def count(self, text):
        words = MinshinglesCounter._extract_words(text)
        shs = self._count_shingles(words)
        mshs = self._select_minshingles(shs)

        if len(mshs) == self.n:
            return mshs

        if len(shs) >= self.n:
            return sorted(shs)[0:self.n]

        return None

    def _select_minshingles(self, shs):
        buckets = [None]*self.n
        for x in shs:
            bkt = x % self.n
            buckets[bkt] = x if buckets[bkt] is None else min(buckets[bkt], x)

        return filter(lambda a: a is not None, buckets)

    def _count_shingles(self, words):
        shingles = []
        for i in xrange(len(words) - self.window):
            h = mmh3.hash(' '.join(words[i:i+self.window]).encode('utf-8'))
            shingles.append(h)
        return sorted(shingles)

    @staticmethod
    def _extract_words(text):
        words = re.findall(MinshinglesCounter.SPLIT_RGX, text)
        return words


def main():
    mhc = MinshinglesCounter()
    data = []
    for path in sys.argv[1:]:
        for doc in DocumentStreamReader(path):
            mhc_c = mhc.count(doc.text)
            data.append((doc.url, mhc_c))

    for i in range(len(data)):
        if data[i][1] is None:
            continue
        for j in range(i+1, len(data)):
            a = data[i][1]
            b = data[j][1]
            if b is None or data[i][0] == data[j][0]:
                continue
            ok = 0
            for x in a:
                if x in b:
                    ok += 1
            score = ok/float(ok+2*(20-ok))
            if score >= 0.75:
		print ("{} {} {}".format(data[i][0], data[j][0], score))
		

if __name__ == '__main__':
    main()
