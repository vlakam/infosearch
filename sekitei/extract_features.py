# -*- coding: utf-8 -*-
import re
import random
from collections import Counter
from urlparse import urlparse
from urllib import unquote

def extract_features(INPUT_FILE_1, INPUT_FILE_2, OUTPUT_FILE):
    sample = 1000
    nu = 0.1
    limit = nu * sample
    result = Counter()
    elinks = []
    glinks = []
    ifstream1 = open(INPUT_FILE_1, "r")
    ifstream2 = open(INPUT_FILE_2, "r")
    ofstream = open(OUTPUT_FILE, "w")

    for line in ifstream1:
        elinks.append(line[:-1])

    for line in ifstream2:
        glinks.append(line[:-1])

    ifstream1.close()
    ifstream2.close()
    random.shuffle(elinks)
    random.shuffle(glinks)
    inputdata = elinks[:sample] + glinks[:sample]
    for url in inputdata:
        parsed_url = urlparse(unquote(url))
        path, query = parsed_url.path, parsed_url.query
        counter = 0

        path_segments = filter(lambda x: len(x), path.split('/'))
        query_segments = filter(lambda x: len(x), query.split('&'))
        result["segments:" + str(len(path_segments))] += 1

        for seg in path_segments:
            result["segment_name_" + str(counter) + ":" + seg] += 1
            if re.match(r'[0-9]+$', seg):
                result["segment_[0-9]_" + str(counter) + ":1"] += 1

            if re.match(r'[^\d]+\d+[^\d]+$', seg):
                result["segment_substr[0-9]_" + str(counter) + ":1"] += 1

            matched = re.match(r'(.+)\.(.+)', seg)
            if matched:
                result["segment_ext_" + str(counter) + ":" + matched.group(2)] += 1

            matched = re.match(r'([^\d]+\d+[^\d]+)\.(\W+)', seg)
            if matched:
                result["segment_ ext_substr[0-9]_" + str(counter) + ":" + matched.group(2)] += 1

            result["segment_len_" + str(counter) + ":" + str(len(seg))] += 1
            counter += 1

        for seg in query_segments:
            matched = re.match(r'(.+)=(.+)$', seg)
            if matched:
                result["param:" + seg] += 1
                result["param_name:" + matched.group(1)] += 1
            else:
                result["param_name:" + seg] += 1

    for feature, count in result.items():
        if count > limit:
            ofstream.write(feature + '\t' + str(count) + '\n')
