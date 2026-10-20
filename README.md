# Controlled Data to Text

A companion demonstrator for exploring how public administrations can explain
complex indicators while retaining control over factual wording.

Machine learning selects explanatory content; deterministic templates express it.
Drafts record supporting fields, template identifiers and hashes so staff can
inspect how each statement was produced.

[Italian technical guide](README.it.md) · [Method](docs/METHOD.md) ·
[Walkthrough](docs/WALKTHROUGH.md) · [Release checklist](docs/RELEASE_CHECKLIST.md)

## Relationship to the ANAC practice

| Material | Purpose | Evidence |
| --- | --- | --- |
| [Operational PUT dashboard](https://dashboard-put.anticorruzione.it/) | ANAC's public transparency service | The institutional practice described in the submission |
| [Biancalana and Sbicca, Ital-IA 2026 paper](https://claudiobiancalana.it/assets/publications/biancalana-sbicca-ital-ia-2026.pdf) | Original method and evaluation | Reported evaluation on 11,033 administration profiles |
| This repository | A separate demonstrator for adaptation | Synthetic examples, inspectable outputs and reuse guidance |

**This is not the production service or the original experimental code.** Its
feature schema, labels, baselines and weighting differ from the paper. It does not
reproduce or independently verify the reported Micro F1 of 0.901. Paper results
are transcribed in `results/paper_reported.json`; laboratory results are separate
in `results/latest/`. See [method differences](docs/METHOD.md) and
[component origins](PROVENANCE.md).

## Public value and design

Publishing data does not by itself make complex indicators understandable. Readers
need to distinguish values, changes over time and comparisons; staff need wording
that can be checked against the underlying information. The demonstrator illustrates
a controlled way to provide these explanations without free-form generation.

```text
Indicator profile -> type and annual arithmetic checks -> content selection
    -> deterministic templates and evidence -> draft and review routing
    -> institutional approval and publication outside this laboratory
```

The confidence score is an uncalibrated selection margin, not a probability of
factual correctness. The illustrative threshold is 0.6. Invalid scores or thresholds
block output. Automated checks do not verify source truth, reconcile all historical
aggregates or validate arbitrary custom-template claims. No output authorizes
publication or records human approval.

## Try a synthetic example

Python 3.11 or later is required. From the repository root:

```bash
python -m venv .venv
# Activate .venv using your operating system's command.
python -m pip install -e '.[test]'
d2t generate data/synthetic.example.json --output work/example.json
python -m streamlit run app.py
```

The interface and sample narratives currently use Italian. A clone runs on synthetic
data without MongoDB credentials. Optional local institutional exports are excluded
from Git and are not needed for the synthetic demonstration.

See the [walkthrough](docs/WALKTHROUGH.md) for interpreting a report, and the
[Italian guide](README.it.md) for Windows, Linux/macOS, Docker and notebook instructions.
The lock file records the earlier Windows environment; CI separately checks package
constraints. These are different environments, not an assertion of identical versions.

## Adaptation by another administration

The reusable pattern is a validated schema, factual templates, content selection,
evidence records and review routing. Adaptation requires:

1. Define indicator meanings, units, applicability and missing-data handling.
2. Map sources and specify domain-appropriate reconciliation checks.
3. Write and review templates, with versioned changes.
4. Collect independent expert labels and train a domain-specific selector.
5. Validate on separate entities, choose review thresholds and assign reviewers.
6. Maintain model versions and a separate approval and publication process.

The 42 laboratory features are a synthetic reconstruction. The 18 observed features
extracted from optional real profiles form a different schema and cannot be passed
directly to this model. This is an adaptation starting point, not an installable
institutional service.

## Tests and results

```bash
d2t synth --n 1200 --seed 42 --output data/synthetic.jsonl
d2t experiment --data data/synthetic.jsonl --output work/experiment --seed 42 --bootstrap 200
python -m pytest -q
```

Experiments measure learning of a simulated editorial policy, not public-sector
impact or performance on real administrations. The weighted committee does not
outperform every baseline on every metric; the treasury block is a weakness in the
saved run. See [results interpretation](results/READING.md).

GitHub Actions regenerates synthetic fixtures and a locally trained model, runs
tests and checks container startup. Inspect the actual workflow run before calling
a release verified. [VERIFICATION.md](VERIFICATION.md) records prior checks and
pending checks. Never load untrusted pickle files; train a fresh model when setting
up a new test environment.

## License and attribution

The software is distributed under the MIT License. Use, modification and
redistribution, including commercial use, are permitted under its terms.
Copies or substantial portions must retain the copyright and permission notice.
Existing attribution notices must be preserved.

If you use or adapt this demonstrator in research, public reporting or another
project, please acknowledge Claudio Biancalana and Fabrizio Sbicca and cite this
repository and the accompanying Ital-IA 2026 paper. Citation metadata are provided
in `CITATION.cff`. This citation request adds no restriction to the MIT License.

The companion demonstrator is separate from ANAC's operational service. Its
software licence does not relicense the paper, third-party dependencies or
institutional data outside this repository.


## Description for supporting material

> Companion demonstrator for exploring and adapting the controlled data-to-text
> approach, with synthetic examples, traceable outputs and reuse guidance. It is
> separate from the operational ANAC service and does not reproduce the paper's
> original evaluation.
