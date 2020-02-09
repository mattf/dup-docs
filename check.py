with open("testset") as fp:
    known_dups = set()
    known_nondups = set()
    for line in fp.readlines():
        id0, id1, score = map(float, line.strip().split(" "))
        if id0 != id1:
            pair = (min(id0, id1), max(id0, id1))
            if score == 1:
                known_dups.add(pair)
            elif score == 0:
                known_nondups.add(pair)

with open("discovered_dups") as fp:
    discovered_dups = set()
    scores = {}
    for line in fp.readlines():
        id0, id1, score = map(float, line.strip().split(" "))
        dup = (min(id0, id1), max(id0, id1))
        discovered_dups.add(dup)
        scores[dup] = score

POSITIVES = len(known_dups)
NEGATIVES = len(known_nondups)
TOTAL = POSITIVES + NEGATIVES
PREDICTED = len(discovered_dups)

TN = len(known_nondups.difference(discovered_dups))
FP = len(known_nondups.intersection(discovered_dups))
FN = len(known_dups.difference(discovered_dups))
TP = len(known_dups.intersection(discovered_dups))


def pct(n):
    return "%i%%" % (n * 100,)


print("known dups:", POSITIVES)
print("known non-dups:", NEGATIVES)
print("discovered dups:", PREDICTED)
print("TP:", TP)
print("FN:", FN)
print("TN:", TN)
print("FP:", FP)
print("accuracy:", pct((TP + TN) / TOTAL))
print("misclassification rate:", pct((FP + FN) / TOTAL))
print("true positive rate | sensitivity | recall:", pct(TP / POSITIVES))
print("false positive rate:", pct(FP / NEGATIVES))
print("true negative rate | specificity:", pct(TN / NEGATIVES))
print("precision:", pct(TP / PREDICTED))
print("prevalence:", pct(POSITIVES / TOTAL))
