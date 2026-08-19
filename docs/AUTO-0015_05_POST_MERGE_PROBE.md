# AUTO-0015-05 — Post-Merge Verification Probe

This branch-only probe exists solely to exercise the read-only exact post-merge Quality verifier against its pull request base SHA.

Target exact `master` SHA:

`adefd9a51071983f4687c4fb884c08f5475c7479`

The probe must not be merged. Its pull-request Quality run is successful only if the verifier observes the exact push-triggered `Quality` run for that base SHA with status `completed` and conclusion `success`.

No mutation authority is added by this probe.
