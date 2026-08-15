# REL-0003 — v0.2.0 Post-Release Reconciliation

**Status:** COMPLETE / VERIFIED

## Publication

- Version: `0.2.0`
- Tag: `v0.2.0`
- Tag target: `1faf14c121b7b5da7c8781e3de4e836f85838a76`
- GitHub Release: `AI-Engineering 0.2.0`
- Release state: published, not draft, not prerelease
- PyPI: not approved / not published

## Release Assets

- `ai_engineering-0.2.0-py3-none-any.whl`
  - SHA-256: `5b86945e861cd22c6e67306e533bb7d446f6bc35207b209c96aa27b4928897bb`
- `ai_engineering-0.2.0.tar.gz`
  - SHA-256: `6594377eda9324aeec82f5db7c7874f68d8cca3dbbbe2ef7f97532a0f341a9b2`

Both assets were freshly built from the approved exact candidate SHA before upload.

## Verification Evidence

The exact candidate passed:

- PR preparation Quality #78;
- post-merge candidate Quality #79 on Linux/Python 3.11;
- Windows-local full pytest: 153 passed, 2 permitted symlink-fixture skips;
- Windows-local Ruff: 0 findings;
- Windows-local mypy: 0 issues in 79 source files;
- Windows-local focused release distribution test: 1 passed;
- `git diff --check`;
- clean Windows working tree.

The readiness documentation PR passed Quality #80. Its post-merge master Quality #81 also passed.

## Scope

The 0.2.0 release includes the verified post-0.1.0 AUTO-0001, AUTO-0002, and SAFE-0002 capabilities together with the previously verified MCP, SDK, tool, distribution, and CI foundation.

SAFE-0001/SAFE-0002 remain bounded authorization/execution contracts and are not an operating-system sandbox. MCP client compatibility claims remain limited to specifically recorded VS Code and Antigravity evidence.

## Publication Boundary

REL-0003 authorized only the Git tag, GitHub Release, and approved wheel/sdist assets. No TestPyPI or PyPI publication occurred. No publishing automation, credentials, secrets, or deployment workflow was added.

## Reconciliation Result

REL-0003 is complete and verified for the approved GitHub publication scope. `v0.2.0` is now the current published release. Future release/version work requires a new explicit decision; PyPI remains separately gated.
