import json
import os
import random

from minhash import generate_shingles, generate_hash_funcs, approx_jaccard_score

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

sigs = []
for doc in docs:
    shingles = list(generate_shingles(doc['text'].split(" ")))
    sigs.append([min(map(hash, shingles)) for hash in hash_funcs])

for sig in sigs[0:4]:
    print("[", " ".join(map(str,sig[1:5])), "...", " ".join(map(str,sig[-4:])), "]")
print("...")
for sig in sigs[-5:-1]:
    print("[", " ".join(map(str,sig[1:5])), "...", " ".join(map(str,sig[-4:])), "]")

# this builds a diagonal, upper-right matrix
# locations along the main diagonal and below (lower-left) are invalid
# access scores[x][y] at scores[x][y-x-1]
scores = [
    [
        approx_jaccard_score(a, b) for b in sigs[i+1:]
    ] for i, a in enumerate(sigs)
]

bins = {0: 0, .1: 0, .2: 0, .3: 0, .4: 0, .5: 0, .6: 0, .7: 0, .8: 0, .9: 0, 1: 0}
for row in scores:
    for score in row:
        if score > 0:
            bins[int(score * 10) / 10] += 1
print(bins)

threshold = .7
for i in range(len(scores)):
    for j in range(i + 1, len(scores)):
        if threshold < scores[i][j-i-1] and scores[i][j-i-1] < 1:
            print(ids[i], ids[j])
