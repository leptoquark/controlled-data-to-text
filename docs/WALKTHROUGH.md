# Inspect a generated explanation

This example uses fictional data and demonstrates software behaviour, not an
observed benefit or an administration's performance.

After installation, run from the repository root:

```bash
d2t generate data/synthetic.example.json --output work/example.json
```

This command uses availability rules, not the experimental ML selector. The latter
is a separate path described in the snippets and Italian guide.

| Report field | Interpretation |
| --- | --- |
| `blocks[].text` | Template wording filled from the profile |
| `blocks[].evidence` | Supporting input fields |
| `template_id`, `rule_id` | Template and applicability rule identifiers |
| `decisions` | Requested, available and included status for each block |
| `input_sha256`, `templates_sha256` | Fingerprints of input and template content |
| `confidence_kind` | An uncalibrated selection margin, or unavailable |
| `validation_scope` | Performed checks and explicit exclusions |
| `publication_authorized` | Always false; publication is outside this generator |

Hashes identify content; they do not establish its truth or record human approval.
Archive model and configuration versions separately when adapting the method.

## Routing states

- `blocked`: invalid profile or review-gate inputs; no text is generated.
- `review_required`: draft generated with missing or below-threshold confidence.
- `automated_checks_passed_draft`: valid inputs and confidence at or above threshold.
  This does not establish factual correctness or institutional approval.

The rule-only command has no ML score and routes for review. Both score and threshold
must be finite numbers in [0, 1]; strings and booleans are rejected. Equality passes
the routing comparison. A publication workflow must still record responsible human
approval and domain-appropriate checks.

To explore missing data, replace a numeric field with `null` in a copy of the sample
and generate again. Compare the corresponding `decisions` entry and evidence. Zero
is numeric data and is not treated as missing. The generator checks complete annual
arithmetic but does not reconcile every aggregate against the historical rows.
