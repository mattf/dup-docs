import json

with open("testset") as fp:
    known_dups = set()
    for line in fp.readlines():
        id0, id1, _ = map(int, line.strip().split(" "))
        if id0 != id1:
            known_dups.add(id0)
            known_dups.add(id1)

with open("docs.json") as fp:
    docs = json.load(fp)
    observed_ids = set([doc['id'] for doc in docs])

string = ""
for known in known_dups:
    if known not in observed_ids:
        string += " -e %i" % (known,)
print(string)
