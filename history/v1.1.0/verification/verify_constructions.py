"""Verify the explicit expressions used in manuscript Table 2.

Run from any directory: python3 verification/verify_constructions.py
Only standard Python libraries and the bundled verify_matrices.py are needed.
Products are ordered lists of (generator, integer exponent) pairs. In particular,
the Mitten beta entries below already include the inverse used in the archive;
all entries use the manuscript's positive right action R_h e_u = e_{u h}.
"""
from pathlib import Path
import hashlib
import json
import math
from verify_matrices import matrices, basis, supports, transpose

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data/selected'
KEYS = ('a0', 'a1', 'b0', 'b1')
SYMBOLS = (r'\alpha_{00}', r'\alpha_{01}', r'\beta_{00}', r'\beta_{01}')

def xw(i, j):
    return [(g, e) for g, e in [('x', i), ('w', j)] if e]

MITTEN = [
    [xw(11, 7), xw(11, 11), xw(5, 14)],
    [[], xw(9, 0), xw(4, 14)],
    [[('w', -7), ('x', -1)], [('w', -3), ('x', -3)], [('w', -12), ('x', -9)]],
    [[], [('w', -2), ('x', -9)], [('w', -14), ('x', -6)]],
]
HONG_PARENT = [[xw(i, j) for i, j in terms] for terms in [
    [(0, 0), (10, 0), (5, 2)], [(0, 0), (8, 0), (2, 3)],
    [(0, 0), (7, 0), (16, 1)], [(0, 0), (1, 0), (6, 4)],
]]
HONG_EXTENSION = [[xw(i, j) for i, j in terms] for terms in [
    [(0, 0), (32, 0), (27, 2)], [(0, 0), (-14, 0), (24, 3)],
    [(0, 0), (7, 0), (16, 1)], [(0, 0), (23, 0), (28, 4)],
]]
ROWS = [
    ('Mitten-975', 'Mitten LP', 975, (13, 15, 9), 'ij', MITTEN, 'mitten'),
    ('Mitten-975_p22_r3_v0', 'Mitten LP', 1650, (22, 15, 3), 'ij', MITTEN, None),
    ('Hong-550', 'Hong-550 LP', 550, (22, 5, 3), 'ji', HONG_PARENT, 'hong'),
    ('Hong-550_p41_r18_v1', 'Hong-550 LP', 1025, (41, 5, 18), 'ji', HONG_EXTENSION, None),
]

def evaluate(expressions, params, order):
    p, m, rho = params
    assert math.gcd(rho, p) == 1 and pow(rho, m, p) == 1
    ring = {}
    for key, terms in zip(KEYS, expressions):
        ring[key] = []
        for term in terms:
            i, j = 0, 0
            for generator, exponent in term:
                if generator == 'x':
                    i = (i + pow(rho, j, p) * exponent) % p
                else:
                    assert generator == 'w'
                    j = (j + exponent) % m
            ring[key].append((i, j))
        assert len(set(ring[key])) == 3
    return {'kind': 'group', 'p': p, 'm': m, 'rho': rho,
            'ring': ring, 'order': order, 'inverse_right': False}

def verify():
    (ROOT / 'verification_results').mkdir(exist_ok=True)
    results = []
    for ident, name, n, params, order, expressions, citation in ROWS:
        source = DATA / f'{ident}.json'
        doc = json.loads(source.read_text())
        built_n, hx, hz = matrices(evaluate(expressions, params, order))
        assert built_n == n == doc['n']
        assert [list(supports(v)) for v in hx] == doc['hx']
        assert [list(supports(v)) for v in hz] == doc['hz']
        assert all((x & z).bit_count() % 2 == 0 for x in hx for z in hz)
        ranks = [len(basis(hx)), len(basis(hz))]
        assert n - sum(ranks) == n // 5
        results.append({'id': ident, 'n': n, 'parameters': params,
                        'ordered_expressions': dict(zip(KEYS, expressions)),
                        'coordinate_order': order, 'matrix_match': True,
                        'css_orthogonal': True, 'ranks': ranks, 'k': n - sum(ranks),
                        'row_weights': [sorted({v.bit_count() for v in h}) for h in (hx, hz)],
                        'column_weights': [sorted({v.bit_count() for v in transpose(h, n)}) for h in (hx, hz)],
                        'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest()})
    parent = matrices(evaluate(HONG_PARENT, (22, 5, 3), 'ji'))
    reevaluated = matrices(evaluate(HONG_EXTENSION, (22, 5, 3), 'ji'))
    assert parent == reevaluated
    result = {'command': 'python3 verification/verify_constructions.py',
              'right_action': 'R_h e_u = e_(u h); inverses are explicit in the expressions',
              'hong_extension_expressions_reproduce_parent': True,
              'distance_search_rerun': False, 'codes': results}
    (ROOT / 'verification_results/construction_table_verification.json').write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'verified_codes': len(results),
                      'exact_matrix_matches': True,
                      'hong_extension_expressions_reproduce_parent': True}))

if __name__ == '__main__':
    verify()
