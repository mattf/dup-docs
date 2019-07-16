from minhash import generate_shingles

def test_generate_shingles():
    identity = lambda x: x
    assert list(generate_shingles(["a"], count=2, mapper=identity)) == ["a"]
    assert list(generate_shingles(["b","c"], count=2, mapper=identity)) == ["b c"]
    assert list(generate_shingles(["d","e","f"], count=2, mapper=identity)) == ["d e", "e f"]
    assert list(generate_shingles(["g","h","i","j"], count=2, mapper=identity)) == ["g h", "h i", "i j"]
