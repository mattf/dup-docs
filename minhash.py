from gensim.utils import simple_preprocess

from mfoops.timer import Timer

from collections import deque
import numpy as np
import random
import zlib

import json

def generate_shingles(words, count=2, mapper=lambda x: zlib.adler32(x.encode())):
    memory = deque(words[:count], maxlen=count)
    yield mapper(" ".join(memory))
    for word in words[count:]:
        memory.append(word)
        yield mapper(" ".join(memory))

def generate_hash_funcs(count, max=2**32-1, prime=4294969733):
    def func(a, b, c):
        return lambda x: (a * x + b) % c
    coeffs = random.sample(range(2**32 - 1), count * 2)
    with open("coeffs.json", 'w') as fp:
        json.dump({"prime": prime, "coeffs": coeffs}, fp)
    return [func(coeffs.pop(), coeffs.pop(), prime) for i in range(count)]

def calculate_signature(shingles, hash_funcs):
    return np.array([min(map(hash, shingles)) for hash in hash_funcs])

# this is...
# a = b = range(100); c = d = np.array(range(100))
# 1M iterations
#  np.count_nonzero(c==d) / len(c) ~= 2.6
#  sum(x == y for x, y in zip(a, b)) / len(a) ~= 12.5
#  sum(a[i] == b[i] for i in range(len(a))) / len(a) ~= 31.7
#  count = 0; for i in range(len(a)): if a[i] == b[i]: count += 1; count / len(a) ~= 27.6
# it takes longer to construct a np.array when calculating the signatures, but that cost
# increase is more than made up for in the scoring cost decrease
def approx_jaccard_score(a, b, axis=0):
    return np.count_nonzero(a==b, axis) / len(a)


def __main__():
    import json
    import os

    sig_len = 42

    seed = os.getenv("SEED")
    random.seed(seed)
    print("using seed:", seed)
    print("signature length:", sig_len)

    if os.path.isfile("signatures.json"):
        print("loading known signatures")
        with open("signatures.json", "r") as fp:
            data = json.load(fp)
            ids = []
            sigs = np.empty((len(data), sig_len)) # TODO: sig_len may be different
            for i, doc in enumerate(data):
                ids.append(doc['id'])
                sigs[i] = doc['sig']
    else:
        with open("docs.json") as fp:
            docs = json.load(fp)

        ids = [doc['id'] for doc in docs]
        print(len(ids), ":", " ".join(map(str,ids[1:5])), "...", " ".join(map(str,ids[-4:])))

        hash_funcs = list(generate_hash_funcs(sig_len))

        with Timer("signature time"):
            sigs = np.empty((len(docs), sig_len))
            for i, doc in enumerate(docs):
                shingles = list(generate_shingles(simple_preprocess(doc['text'], min_len=0, max_len=4242)))
                sigs[i] = calculate_signature(shingles, hash_funcs)

        with open("signatures.json", 'w') as fp:
            json.dump([{"id": id,"sig": sig.astype(int).tolist()} for id, sig in zip(ids, sigs)], fp)

    for sig in sigs[:4]:
        print("[", " ".join(map(str,sig[:4])), "...", " ".join(map(str,sig[-4:])), "]")
    print("...")
    for sig in sigs[-4:]:
        print("[", " ".join(map(str,sig[:4])), "...", " ".join(map(str,sig[-4:])), "]")

    # this builds a diagonal, upper-right matrix
    # locations along the main diagonal and below (lower-left) are invalid
    # access scores[x][y] at scores[x][y-x-1]
    with Timer("score time"):
        scores = [approx_jaccard_score(a, sigs[i+1:], 1) for i, a in enumerate(sigs)]

    with Timer("bin time"):
        # np.histogram uses last bin as max, to include 1.0 need a bin >1.0
        bins = (0, .1, .2, .3, .4, .5, .6, .7, .8, .9, 1, 42)
        hist = {0: 0, .1: 0, .2: 0, .3: 0, .4: 0, .5: 0, .6: 0, .7: 0, .8: 0, .9: 0, 1: 0}
        for row in scores:
            counts, _ = np.histogram((row*10).astype(int)/10, bins)
            for i, c in enumerate(counts):
                hist[bins[i]] += c
    print(hist)

    with open("discovered_dups", "w") as fp:
        threshold = .42
        for i in range(len(scores)):
            for j in range(i + 1, len(scores)):
                if threshold < scores[i][j-i-1] and scores[i][j-i-1] < 1:
                    print(ids[i], ids[j], scores[i][j-i-1], file=fp)


if __name__ == "__main__":
    __main__()
