with open("known_dups") as fp:
    known_dups = set()
    for line in fp.readlines():
        id0, id1 = map(int, line.strip().split(" "))
        if id0 != id1:
            known_dups.add((min(id0, id1), max(id0, id1)))

with open("discovered_dups") as fp:
    discovered_dups = set()
    scores = {}
    for line in fp.readlines():
        id0, id1, score = map(float, line.strip().split(" "))
        dup = (min(id0, id1), max(id0, id1))
        discovered_dups.add(dup)
        scores[dup] = score

found = 0
for known in known_dups:
    if known in discovered_dups:
        print(known, scores[known])
        found += 1

print("known", "discovered", "found", "hit_rate")
print(len(known_dups), len(discovered_dups), found, found / len(known_dups))
