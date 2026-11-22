# Fixed-data extensions of high-rate lifted-product codes

Version 1.1.0 contains the four codes selected in the current manuscript, their explicit constructions, binary parity-check matrices, logical operators and distance-verification records. The two original codes and their extensions have rate 20%.

| Family | Code | n | k | Rate | dX | dZ | d | Column weight | Row weight |
|---|---|---:|---:|---:|---:|---:|---:|---|---:|
| Mitten LP | Original | 975 | 195 | 20% | 24 | 24 | 24 | {3,6} | 9 |
| Mitten LP | Extension | 1650 | 330 | 20% | 30 | [30,38] | 30 | {3,6} | 9 |
| Hong-550 LP | Original | 550 | 110 | 20% | [18,50] | 18 | 18 | {3,6} | 9 |
| Hong-550 LP | Extension | 1025 | 205 | 20% | 24 | 24 | 24 | {3,6} | 9 |

Here d=min(dX,dZ). Intervals give the established lower and upper bounds. The Mitten extension has exact distance 30 even though its Z-sector distance remains between 30 and 38. For sector X the check is HZ and the stabilizer space is row(HX); sector Z interchanges them. Supports use zero-based qubit indices.

[Selected records](data/selected/records.json) contain both sector supports, ranks and matrix identities. [The comparison table](data/comparison_table.csv) is machine-readable. Each `data/selected/<id>.json` contains sparse `hx` and `hz` row supports and `n`; `*_words.json` contains the evaluated construction input and conventions. The selected IDs are:

- `Mitten-975`
- `Mitten-975_p22_r3_v0`
- `Hong-550`
- `Hong-550_p41_r18_v1`

## Reproduce the construction and upper bounds

Python 3.12 or later and its standard library suffice for the verification commands. Run them from this directory:

```sh
python3 verification/verify_constructions.py
python3 verification/verify_matrices.py
python3 verification/verify_parent_sources.py
python3 build_codes.py check
```

The construction verifier evaluates the explicit expressions of manuscript Table 2, reconstructs every binary entry, checks CSS orthogonality, ranks, row weights and column weights, and checks that the Hong extension expressions also reproduce its original code when evaluated at the original group parameters. Its output is saved in `verification_results/construction_table_verification.json`. The matrix verifier also checks that every stored upper-bound support has zero syndrome and lies outside the stabilizer row space.

The group is G(p,m,rho)=<x,w | x^p=w^m=1, wxw^-1=x^rho>, with gcd(rho,p)=1 and rho^m=1 modulo p. Normal coordinates (i,j) denote x^i w^j and multiply as (i,j)(u,t)=(i+rho^j u,j+t), modulo p and m. Left and right regular actions commute; this establishes CSS orthogonality for the lifted-product construction. The resulting dimension is calculated from the binary ranks.

| Code | (p,m,rho) | Coordinate order |
|---|---|---|
| Mitten original | (13,15,9) | i then j |
| Mitten extension | (22,15,3) | i then j |
| Hong-550 original | (22,5,3) | j then i |
| Hong-550 extension | (41,5,18) | j then i |

[Construction data](data/constructions.json) specify each product as an ordered list of generator/exponent pairs. These expressions use positive right multiplication R_h e_u=e_(u h), with the Mitten inverses written explicitly. The older `*_words.json` representation stores those Mitten terms before inversion and marks `inverse_right=true`; inversion must be evaluated at the target parameters. The Hong extension uses integer representatives congruent to the original exponents, including a negative exponent. Retain those integers when changing the group. The verifier checks both representations against the same matrices.

Changing the group changes which small supports have zero syndrome or represent nontrivial logical operators. Distance improvement is established for the selected matrices by the exhaustive computations below; the group conditions alone ensure orthogonality.

## Verify the distance lower bounds

```sh
python3 verification/download_receipts.py
python3 verification/verify_receipts.py
```

To check one extension:

```sh
python3 verification/verify_receipts.py --id Mitten-975_p22_r3_v0
```

The two release assets contain the original receipt/stdout/stderr bytes, completed partition leaves, physical inputs, source files, executable identities and configurations needed to exclude all nontrivial logical operators of weight at most 29 for Mitten and at most 23 for Hong-550. The downloader checks sizes and SHA-256 hashes against [receipt_archives.json](data/receipt_archives.json).

The verifier checks every archived file hash, code identity, native source and executable identities, configurations, physical symmetries, original receipts and completed frontier coverage. Each refined residue class must be replaced by all its disjoint children. All required LP parts and symmetry orbits must be covered. An X/Z exchange is used only after physical verification. Results are written to `verification_results/`.

These are source-bound exhaustive execution records, rather than formal per-node proof traces. Record verification does not rerun the DFS. The stored TSUBAME binaries are hashed, not executed. Each receipt retains the native invocation and time/node limits; source and compiler details are in `campaigns/w*/engine/build.json`. Timeouts do not contribute lower bounds. The completed Mitten exclusion contains 233,792 terminal partitions across both sectors and 281,626 recorded attempts, including interrupted attempts and partition refinement.

Parent lower bounds come from the QEDist paper/catalogue. The original matrices and upper witnesses are matched to its pinned public data; see [parent provenance](data/parent_provenance.json). The Mitten construction article gives the construction and an upper bound of 24; QEDist establishes exactness at 24.

## Run a new distance search

The bundled upstream CLI can launch a new exhaustive search after compiling its C++17 source. For example:

```sh
PYTHONPATH=vendor/QEDist python3 -m cssdist certify data/selected/Hong-550_p41_r18_v1.json --out verification_results/fresh_hong550 --profile lp --cutoff 23 --shards 32 --split-weight 4 --workers 4 --seconds-per-shard 300 --no-large-capacity
PYTHONPATH=vendor/QEDist python3 -m cssdist audit verification_results/fresh_hong550
```

This command starts a new computation with a uniform partition. Completion is not guaranteed within its per-partition time limit. The release records preserve the original adaptive partition schedule.

## Sources and software

- Mitten construction: [High-rate qLDPC processors](https://arxiv.org/abs/2607.28795v2), Sec. III, Table I. Matrix provenance additionally records a7b/yarn commit `1b58edd24e19b6b5da6814fd3a74ebb376b6e90f`, directory `processor_codes/mitten/[[975,195,24]]`.
- Hong construction: [Quantum LDPC codes with design rate 1/5 and good performance below 1000 physical qubits](https://arxiv.org/abs/2607.27644v1).
- Parent distances and LP distance reduction: [QEDist: Practical Exact Distance Certification for Stabilizer Codes](https://arxiv.org/abs/2611.21709v1).
- [QEDist software](https://github.com/yeon-lee/QEDist/tree/aeb7006147b777c121fd3ab8c6841da99238a84e), pinned commit `aeb7006147b777c121fd3ab8c6841da99238a84e`. The retained runtime is unmodified and distributed under its [MIT license](vendor/QEDist/LICENSE), with [notices](vendor/QEDist/NOTICE.md). [Software provenance](data/software_provenance.json) records the public-tree comparison. The added `verification/nested_audit.py` checks the union of refined partitions without modifying the native search.

Earlier candidates are preserved in [history](history/README.md) and the v1.0.1 tag for provenance. They are not part of the current manuscript's selected comparison.

## Citation

Kenta Kasai, “Fixed-data extensions of high-rate lifted-product codes: code data and distance-verification records,” version 1.1.0, 2026. [Fixed release](https://github.com/kasaikenta/lp-fixed-data-extensions/releases/tag/v1.1.0).

Machine-readable citation details are in [CITATION.cff](CITATION.cff).
