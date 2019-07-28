from minhash import generate_shingles, approx_jaccard_score

def test_generate_shingles():
    identity = lambda x: x
    assert list(generate_shingles(["a"], count=2, mapper=identity)) == ["a"]
    assert list(generate_shingles(["b","c"], count=2, mapper=identity)) == ["b c"]
    assert list(generate_shingles(["d","e","f"], count=2, mapper=identity)) == ["d e", "e f"]
    assert list(generate_shingles(["g","h","i","j"], count=2, mapper=identity)) == ["g h", "h i", "i j"]

def test_approx_jaccard_score():
    from numpy import array as a
    assert approx_jaccard_score(a([0,0,0,0]), a([0,0,0,0])) == 1
    assert approx_jaccard_score(a([0,0,0,0]), a([1,0,0,0])) == 3/4
    assert approx_jaccard_score(a([0,0,0,0]), a([1,0,1,0])) == 2/4
    assert approx_jaccard_score(a([0,0,0,0]), a([1,1,1,0])) == 1/4
    assert approx_jaccard_score(a([0,0,0,0]), a([1,1,1,1])) == 0
    assert approx_jaccard_score(a([0,0,0]), a([0,0,0])) == 1
    assert approx_jaccard_score(a([0,0,0]), a([1,0,0])) == 2/3
    assert approx_jaccard_score(a([0,0,0]), a([1,0,1])) == 1/3
    assert approx_jaccard_score(a([0,0,0]), a([1,1,1])) == 0
