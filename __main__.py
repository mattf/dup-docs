from gensim.utils import simple_preprocess

from mfoops.timer import Timer

import numpy as np

import random

import json

from minhash import approx_jaccard_score, generate_hash_funcs, generate_shingles, calculate_signature

import os


def __main__():
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
            sigs = np.empty((len(data), sig_len))  # TODO: sig_len may be different
            for i, doc in enumerate(data):
                ids.append(doc['id'])
                sigs[i] = doc['sig']
    else:
        with open("docs.json") as fp:
            docs = json.load(fp)

        ids = [doc['id'] for doc in docs]
        print(len(ids), ":", " ".join(map(str, ids[1:5])), "...", " ".join(map(str, ids[-4:])))

        hash_funcs = list(generate_hash_funcs(sig_len))

        with Timer("signature time"):
            sigs = np.empty((len(docs), sig_len))
            for i, doc in enumerate(docs):
                shingles = list(generate_shingles(simple_preprocess(doc['text'], min_len=0, max_len=4242)))
                sigs[i] = calculate_signature(shingles, hash_funcs)

        with open("signatures.json", 'w') as fp:
            json.dump([{"id": id, "sig": sig.astype(int).tolist()} for id, sig in zip(ids, sigs)], fp)

    for sig in sigs[:4]:
        print("[", " ".join(map(str, sig[:4])), "...", " ".join(map(str, sig[-4:])), "]")
    print("...")
    for sig in sigs[-4:]:
        print("[", " ".join(map(str, sig[:4])), "...", " ".join(map(str, sig[-4:])), "]")

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
