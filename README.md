# Fixed-data extensions of high-rate lifted-product codes

Companion data for Kenta Kasai, *Increasing the Distance of High-Rate Lifted-Product Codes by Reusing Fixed Construction Data*.
This release freezes the ten rows of Table 1. A later ongoing search is not part of this release.

## Table-to-data correspondence

All support indices are zero-based. Each row links to the actual constituent words and full physical matrices; `records.json` gives logical supports, ranks, geometry and provenance. Distances in brackets are certified intervals, not estimates.

| Table row | Code | n | k | rate | dX | dZ | d | Words | Matrices |
|---|---|---:|---:|---:|---|---|---|---|---|
| 1 | Mitten-975 (original) | 975 | 195 | 20% | 24 | 24 | 24 | [words](data/selected/Mitten-975_words.json) | [matrices](data/selected/Mitten-975.json) |
| 2 | Mitten-975 (extension) | 1650 | 330 | 20% | [27, 30] | [27, 38] | [27, 30] | [words](data/selected/Mitten-975_p22_r3_v0_words.json) | [matrices](data/selected/Mitten-975_p22_r3_v0.json) |
| 3 | Mitten-975 (extension) | 2325 | 465 | 20% | [30, 84] | 30 | 30 | [words](data/selected/established_2325_words.json) | [matrices](data/selected/established_2325.json) |
| 4 | Hong-390 (original) | 390 | 78 | 20% | [16, 42] | 16 | 16 | [words](data/selected/Hong-390_words.json) | [matrices](data/selected/Hong-390.json) |
| 5 | Hong-390 (extension) | 915 | 183 | 20% | 18 | [18, 88] | 18 | [words](data/selected/Hong-390_p61_r47_v2_words.json) | [matrices](data/selected/Hong-390_p61_r47_v2.json) |
| 6 | Hong-550 (original) | 550 | 110 | 20% | [18, 50] | 18 | 18 | [words](data/selected/Hong-550_words.json) | [matrices](data/selected/Hong-550.json) |
| 7 | Hong-550 (extension) | 1025 | 205 | 20% | 24 | 24 | 24 | [words](data/selected/Hong-550_p41_r18_v1_words.json) | [matrices](data/selected/Hong-550_p41_r18_v1.json) |
| 8 | LS-P31-2X5 (original) | 899 | 279 | 31.03% | 8 | 8 | 8 | [words](data/selected/LS-P31-2X5_words.json) | [matrices](data/selected/LS-P31-2X5.json) |
| 9 | LS-P31-2X5 (extension) | 1363 | 423 | 31.03% | 14 | 14 | 14 | [words](data/selected/LS-P31-2X5_p47_rNone_v5_words.json) | [matrices](data/selected/LS-P31-2X5_p47_rNone_v5.json) |
| 10 | LS-P31-2X5 (extension) | 1769 | 549 | 31.03% | 15 | 15 | 15 | [words](data/selected/LS-P31-2X5_p61_rNone_v1_words.json) | [matrices](data/selected/LS-P31-2X5_p61_rNone_v1.json) |

The machine-readable correspondence is [records.json](data/selected/records.json); [comparison_table.csv](data/comparison_table.csv) also lists rates and sector bounds. The inferior distance-20 Hong-550 extension is outside the paper's selected table. Full search results from the broader campaign are not claimed to be a classification up to equivalence.

## Reconstruct matrices and verify upper bounds

Use Python 3.12 or later on Linux or macOS. The checks use the standard library only.

```sh
python3 verification/verify_matrices.py
python3 verification/verify_parent_sources.py
```

This independently reconstructs every binary entry from the realized words, checks CSS orthogonality and GF(2) ranks, and verifies every supplied logical operator by zero syndrome and nonmembership in the stabilizer row space. It does not infer lower bounds from an unsuccessful search.

## Verify the distance lower bounds

The six release assets contain **all original receipt/stdout/stderr blobs and all partition leaves required for the published extension lower bounds**, along with the corresponding inputs, source files, executable identities and campaign configurations. Historical cutoffs and unrelated scheduler state are omitted. The selected receipt blobs are byte-preserved. This is about 48 MB compressed and 700 MB unpacked.

```sh
python3 verification/download_receipts.py
python3 verification/verify_receipts.py
```

One selected extension can be checked with, for example:

```sh
python3 verification/verify_receipts.py --id established_2325
```

The downloader checks each release asset against [receipt_archives.json](data/receipt_archives.json). The verifier checks every unpacked file hash, the physical code identity, native source and executable identities, configurations, symmetry inputs, receipt hashes and completed frontier coverage. A refined residue class must be replaced by all its disjoint children. All required LP parts and root orbits must be covered; an X/Z exchange is used only after its physical verification. The results go into `verification_results/`.

These are source-bound exhaustive execution records, not independently checkable formal per-node proof traces. Rechecking records does not rerun the DFS. Stored binaries are only hashed during the audit. They were compiled on TSUBAME4 and are not executed by these verification commands. Every original native invocation and time/node limit is in the receipt's `command` and `limits` fields. Source and compiler details are in each `campaigns/w*/engine/build.json`.

Parent lower bounds are adopted from the QEDist paper/catalogue rather than re-established by these extension searches. Their public fixed-version matrices and upper witnesses were separately matched; see [parent provenance](data/parent_provenance.json). In particular, the Mitten construction paper reports an upper bound of 24, while exactness at 24 is taken from QEDist.

## Construction and experiment parameters

The shared construction uses commuting left and right regular actions. The five-block inputs have three terms per entry. Their group parameters obey gcd(rho,p)=1 and rho^m=1 mod p. Stored Mitten right words are inverted at the **target** parameters; the other group inputs use right multiplication directly. `*_words.json` records `order` and `inverse_right` explicitly, so reconstruction does not depend on a pseudorandom seed. Per-code `*_parameters.json` records the generation parameters.

The main Mitten example changes (p,m,rho)=(13,15,9) to (31,15,4), retaining the stored words and m. Selecting the third smallest unit satisfying rho^15=1, with cyclic indexing for shorter lists, reproduces both endpoints. Its group orders prevent a surjection to the parent group. The shorter Mitten example uses (22,15,3).

The compact campaign tested 1104 assignments from four parents, with n<=2000, actual rate at least the parent rate, and maximum check weight no larger than the parent's. For each parent, 16 rules chose integer representatives congruent to the parent exponents. Group rules also tested admissible rho=(rho0+p0*t) mod p, 0<=t<64, at fixed m. [manifest.json](data/manifest.json) and [build_codes.py](build_codes.py) retain these rules. The separately established 2325-qubit example is outside that compact length budget.

The cyclic family uses a 2 by 5 constituent with the monomial/binomial pattern in the paper. [cofactor_bound.py](cofactor_bound.py) and [cofactor_witnesses.json](data/cofactor_witnesses.json) supplement the paper's proof of the uniform sector-distance upper bound 17.

## Start a fresh exhaustive search

The pinned upstream CLI can start an independent search after compiling its C++17 source. For example, the following command tests the Hong-390 extension through weight 17 using a uniform partition:

```sh
PYTHONPATH=vendor/QEDist python3 -m cssdist certify data/selected/Hong-390_p61_r47_v2.json --out verification_results/fresh_hong390 --profile lp --cutoff 17 --shards 32 --split-weight 4 --workers 4 --seconds-per-shard 300 --no-large-capacity
PYTHONPATH=vendor/QEDist python3 -m cssdist audit verification_results/fresh_hong390
```

This is a new computation, not the recorded adaptive schedule. Any timed-out class remains incomplete; it is never evidence for a lower bound. For the exact original schedule, the release's receipts retain every invocation, cutoff, shard, time/node limit and source identity.

## Sources and software

- Mitten construction: [High-rate qLDPC processors](https://arxiv.org/abs/2607.28795v2), Sec. III, Table I. The original matrix source is a7b/yarn commit `1b58edd24e19b6b5da6814fd3a74ebb376b6e90f`, directory `processor_codes/mitten/[[975,195,24]]`; the paper cites the construction article.
- Hong inputs: [Quantum LDPC codes with design rate 1/5 and good performance below 1000 physical qubits](https://arxiv.org/abs/2607.27644v1).
- Cyclic input: [Logical Spectroscopy: Lifted-Product Codes with Addressable Bases](https://arxiv.org/abs/2607.05386v2).
- Parent distances and LP reduction: [QEDist: Practical Exact Distance Certification for Stabilizer Codes](https://arxiv.org/abs/2611.21709v1).
- [QEDist software](https://github.com/yeon-lee/QEDist/tree/aeb7006147b777c121fd3ab8c6841da99238a84e), fixed commit `aeb7006147b777c121fd3ab8c6841da99238a84e`. The retained runtime is unmodified and distributed under its [MIT license](vendor/QEDist/LICENSE), with its [notices](vendor/QEDist/NOTICE.md). [Software provenance](data/software_provenance.json) records a byte-for-byte public-tree comparison. The added `verification/nested_audit.py` checks the union of refined partitions; it does not modify the native search.

## Citation

Cite the fixed release, rather than an evolving default branch:

> Kenta Kasai, “Fixed-data extensions of high-rate lifted-product codes: code data and distance-verification records,” version 1.0.0, 2026. https://github.com/kasaikenta/lp-fixed-data-extensions/releases/tag/v1.0.0

Use [CITATION.cff](CITATION.cff) for machine-readable citation details. Receipt archive checksums are pinned in the tagged repository.
