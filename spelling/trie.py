# coding=utf-8
import pickle
import heapq
import numpy as np

MISPLACE_LIMIT = 1
ADDITIVE_LIMIT = 1
REMOVAL_LIMIT = 1
MAX_ERRORS = 0.10

symbols = ("QWERTYUIOPASDFGHJKLZXCVBNM", "ЙЦУКЕНГШЩЗФЫВАПРОЛДЯЧСМИТЬ")
tr = {a:b for a, b in zip(*symbols)}
tr_ = {a:b for b, a in zip(*symbols)}

def mislayout(word, dic):
    new_word = []
    for letter in word:
        if letter in dic.keys():
            new_word.append(dic[letter])
        else:
            new_word.append(letter)
    return ''.join(new_word)

class Node:
    def __init__(self, label=None, is_word_end=False, freq=-1):
        self.label = label
        self.is_word_end = is_word_end
        self.freq = freq
        self.children = dict()


class Traverse():
    def __init__(self, node, addins, misplaces, removal, letters, required, trans = False):
        self.addings = addins
        self.misplaces = misplaces
        self.node = node
        self.letters = letters
        self.required = required
        self.removal = removal
        self.trans = trans

    def multiplier(self):
        multiplier = np.power(0.0001, (self.misplaces + self.addings + self.removal + int(self.trans)))
        #multiplier = float(len(self.letters) - self.misplaces - self.addings - self.removal) / len(self.letters)

        return multiplier

    def q(self):
        return self.node.freq

    def can_error(self):
        return float(len(self.letters) + len(self.required)) * 0.10 > (self.addings + self.removal + self.misplaces)


class TraverseResult:
    def __init__(self, word, freq):
        self.word = word
        self.freq = freq

class Trie:
    def __init__(self):
        self.root = Node()

    def save(self):
        file = open('dump.pickle', 'wb')
        pickle.dump(self.root, file)
        file.close()

    def load(self):
        file = open('dump.pickle', 'rb')
        self.root = pickle.load(file)
        file.close()

    def fill_trie(self, zip_word_freq):
        i = 0
        def add_word_to_bor(letters, freq, node):
            lt = letters.pop(0)
            if lt not in node.children:
                node.children[lt] = Node(lt)

            if letters:
                add_word_to_bor(letters, freq, node.children[lt])
            else:
                node.children[lt].is_word_end = True
                node.children[lt].freq = freq

        def normalize_freq(node):
            for child in node.children.values():
                normalize_freq(child)

            if (node.freq == -1):
                node.freq = max([child.freq for child in node.children.values()])

        for word, freq in zip_word_freq:
            i+=1
            if (i%5000 == 0):
                print i
            letters = list(word)
            add_word_to_bor(letters, freq, self.root)

        normalize_freq(self.root)

    def fuzzy_search(self, word):
        words = []
        word1 = mislayout(word, tr)
        word2 = mislayout(word, tr_)
        queue = []
        if (word1 != word2):
            queue = [(1, Traverse(self.root, 0, 0, 0, [], list(word1)), word1 != word),
                     (1, Traverse(self.root, 0, 0, 0, [], list(word2)), word2 != word)]
        else:
            queue = [(1, Traverse(self.root, 0, 0, 0, [], list(word)))]

        while len(queue):
            traverse = heapq.heappop(queue)[1]
            current_node = traverse.node
            if (len(traverse.required) == 0):
                if (current_node.is_word_end):
                    words.append(TraverseResult(''.join(traverse.letters), traverse.q() * traverse.multiplier()))
                    if (len(words) >= 7):
                        break
                continue

            children_sorted = sorted(current_node.children.values(), key=lambda child: child.freq, reverse=True)
            children_sorted = children_sorted[:30]
            for child in children_sorted:
                if (traverse.required[0] == child.label):
                    new_traverse = Traverse(child, traverse.addings, traverse.misplaces, traverse.removal, traverse.letters + [child.label], traverse.required[1:])
                    heapq.heappush(queue, (new_traverse.q() * new_traverse.multiplier(), new_traverse))
                elif(traverse.can_error()):
                    if (traverse.misplaces < MISPLACE_LIMIT):
                        new_traverse = Traverse(child, traverse.addings, traverse.misplaces + 1, traverse.removal,
                                          traverse.letters + [child.label], traverse.required[1:])
                        heapq.heappush(queue, (new_traverse.q() * new_traverse.multiplier(), new_traverse))
                    if (traverse.addings < ADDITIVE_LIMIT):
                        new_traverse = Traverse(child, traverse.addings + 1, traverse.misplaces, traverse.removal, traverse.letters + [child.label], traverse.required)
                        heapq.heappush(queue, (new_traverse.q() * new_traverse.multiplier(), new_traverse))
                    if (traverse.removal < REMOVAL_LIMIT):
                        new_traverse = Traverse(child, traverse.addings, traverse.misplaces, traverse.removal + 1, traverse.letters, traverse.required[1:])
                        heapq.heappush(queue, (new_traverse.q() * new_traverse.multiplier(), new_traverse))

        return sorted(words, key=lambda word: word.freq, reverse=True)

