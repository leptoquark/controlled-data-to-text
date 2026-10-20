# Public release checklist

This checklist records decisions still needed before publishing a reusable release.
It does not grant a licence or assert institutional approval.

- [ ] Confirm the rights holder and permission to redistribute the historical generator in `legacy.py`.
- [ ] Confirm ownership and release terms for the new demonstrator code, templates and synthetic examples.
- [ ] Add the approved licence text and consistent package metadata. The paper's CC BY licence does not automatically cover software.
- [ ] Confirm attribution and the wording describing the relationship with ANAC's operational service.
- [ ] Review all files and repository history for material not intended for public release; keep `data/real/` and operational configuration excluded.
- [ ] Run the GitHub Actions workflow and inspect its results. A workflow file alone is not a successful CI run.
- [ ] Test the notebook in an actual Colab runtime if advertising cloud execution as verified.
- [ ] Verify links without signing in after making the approved material accessible.
- [ ] Tag a tested version and record the commit used for the contest. A tag must not imply permission to reuse before licensing is resolved.

Until the rights questions are resolved, describe this as a companion demonstrator,
not an open-source release. Public visibility and permission to reuse are separate matters.
