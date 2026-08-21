## Purpose

Dedicated public control channel for the repository's bounded read-only control requests, claims, results, and terminal recovery evidence.

## Authority boundary

This issue is transport only. It grants no mutation authority.

Allowed requests must use the repository's typed control protocol and one of: `status`, `inspect`, `plan`, `diff`, `quality_verify`.

`quality_verify` requires an exact `expected_head` and runs through the deterministic read-only Quality relay without invoking OpenCode. Other task classes use only the existing bounded read-only OpenCode adapter.

Unknown, malformed, write-capable, or privacy-unsafe requests fail closed.

## Claim recovery

A visible claim remains an execution fence. An aged unresolved claim may receive a separate bounded terminal recovery envelope only after immediate reinspection confirms that no terminal result or newer claim supersedes it.

Recovery does not call the task executor, OpenCode, or `quality_verify`, and never replays or re-executes the claimed request.

## Privacy and exclusions

Do not post secrets, tokens, credentials, environment values, local absolute paths, hostnames, usernames, or unrelated workstation information.

Write/apply, Git or filesystem mutation, commit, push, automatic repository repair, workflow rerun/cancel/dispatch, service or credential mutation, deployment, release, publication, and reconciliation mutation remain outside this channel's authority.
