# reproducibility_agent Plan

Owned files:

- `artifact_evaluation.md`
- `requirements.txt`
- `scripts/reproduce_all.sh`

Mission:

Keep the artifact clean, runnable, and honest. One command should run the available local tests and report unavailable tool-dependent steps clearly.

Policy:

- no hardcoded machine-specific paths
- no fake data
- no silent skipping of required external tools
- scripts should produce deterministic outputs where random seeds are used

