# External Benchmark Position and Validation Plan

Date: 2026-11-26

## Decision

ChAAt will remain a compact, source-linked diagnostic instrument rather than a
large benchmark assembled from unrelated datasets. RegioZH, CHENGYU-BENCH, and
YUE-PUB are related resources and candidates for external validation, not
automatic sources for the ChAAt core.

## License audit

| Resource | Public location checked | Current status | Permitted action now |
|---|---|---|---|
| RegioZH | ACL Anthology paper | No dataset repository or redistribution license was found in the official paper record | Cite and compare only |
| CHENGYU-BENCH | `github.com/sofyc/ChengyuBench` | GitHub API reports `license: null` | Cite and compare; do not copy items |
| YUE-PUB | ACL Anthology paper / related speech dataset | The speech variant documents Apache-2.0, but the text benchmark release terms must be checked separately | Cite and compare only until confirmed |

## Validation sequence

1. Contact the corresponding authors of each candidate resource to confirm the
   data release location, version, license, and whether redistribution of
   adapted items is allowed.
2. Pin each external dataset to a version or commit hash.
3. Build import adapters without altering labels or source provenance.
4. Exclude any external item whose source, license, or answer cannot be
   verified.
5. Run the same six-model, three-repeat, no-tool protocol on licensed external
   subsets.
6. Report the original benchmark metric, the ChAAt-normalized diagnostic view,
   and any adapter exclusions separately.
7. Do not merge external items into the 50-item ChAAt core or report combined
   accuracy. Report external validation as a separate held-out analysis.
8. Publish only aggregates and derived metadata when redistribution is not
   permitted.

## Manuscript position

The paper describes ChAAt as complementary to large resources, not as a
replacement. Until licensed external runs are complete, the paper must not
claim that ChAAt's conclusions replicate on RegioZH, CHENGYU-BENCH, or YUE-PUB.
