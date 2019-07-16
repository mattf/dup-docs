from collections import deque
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

def approx_jaccard_score(a, b):
    return sum(x == y for x, y in zip(a, b)) / len(a)
