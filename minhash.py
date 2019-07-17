from collections import deque
import numpy as np
import random
import zlib

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
    return [func(coeffs.pop(), coeffs.pop(), 4294969733) for i in range(count)]

# this is...
# a = b = range(100); c = d = np.array(range(100))
# 1M iterations
#  np.count_nonzero(c==d) / len(c) ~= 2.6
#  sum(x == y for x, y in zip(a, b)) / len(a) ~= 12.5
#  sum(a[i] == b[i] for i in range(len(a))) / len(a) ~= 31.7
#  count = 0; for i in range(len(a)): if a[i] == b[i]: count += 1; count / len(a) ~= 27.6
# it takes longer to construct a np.array when calculating the signatures, but that cost
# increase is more than made up for in the scoring cost decrease
def approx_jaccard_score(a, b):
    #return sum(x == y for x, y in zip(a, b)) / len(a)
    return np.count_nonzero(a==b) / len(a)


def __main__():
    import json
    import os

    import time
    class Timer:
        def __enter__(self):
            self.start = time.process_time()
            return self
        def __exit__(self, *args):
            self.end = time.process_time()
            self.interval = self.end - self.start

    sig_len = 42

    seed = os.getenv("SEED")
    random.seed(seed)
    print("using seed:", seed)
    print("signature length:", sig_len)

    with open("docs.json") as fp:
        docs = json.load(fp)

    ids = [doc['id'] for doc in docs]
    print(len(ids), ":", " ".join(map(str,ids[1:5])), "...", " ".join(map(str,ids[-4:])))

    hash_funcs = list(generate_hash_funcs(sig_len))

    with Timer() as sig_time:
        sigs = []
        for doc in docs:
            shingles = list(generate_shingles(doc['text'].split(" ")))
            sigs.append(np.array([min(map(hash, shingles)) for hash in hash_funcs]))
    print("signature time:", sig_time.interval)

    for sig in sigs[:4]:
        print("[", " ".join(map(str,sig[:4])), "...", " ".join(map(str,sig[-4:])), "]")
    print("...")
    for sig in sigs[-4:]:
        print("[", " ".join(map(str,sig[:4])), "...", " ".join(map(str,sig[-4:])), "]")

    # this builds a diagonal, upper-right matrix
    # locations along the main diagonal and below (lower-left) are invalid
    # access scores[x][y] at scores[x][y-x-1]
    with Timer() as score_time:
        scores = [
            [
                approx_jaccard_score(a, b) for b in sigs[i+1:]
            ] for i, a in enumerate(sigs)
        ]
    print("score time:", score_time.interval)

    with Timer() as bin_time:
        bins = {0: 0, .1: 0, .2: 0, .3: 0, .4: 0, .5: 0, .6: 0, .7: 0, .8: 0, .9: 0, 1: 0}
        for row in scores:
            for score in row:
                if score > 0:
                    bins[int(score * 10) / 10] += 1
    print("bin time:", bin_time.interval)
    print(bins)

    threshold = .7
    for i in range(len(scores)):
        for j in range(i + 1, len(scores)):
            if threshold < scores[i][j-i-1] and scores[i][j-i-1] < 1:
                print(ids[i], ids[j])



if __name__ == "__main__":
    __main__()
