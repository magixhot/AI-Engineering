# REL-0001 — Distribution and Release Verification Contract

**Status:** COMPLETE / VERIFIED
**Scope:** local distribution verification for the existing `ai-engineering` package and CLI

## Objective

REL-0001 establishes a reproducible local distribution-verification contract. It proves that the
repository can build correct wheel and source-distribution artifacts and that an installed wheel
works in an isolated environment. It does not publish, tag, or otherwise release those artifacts.

## Current Packaging State

| Item | Current factual state | Verification state / gap |
|---|---|---|
| Distribution name | `ai-engineering` in `[project]` | Verified from wheel and installed metadata. |
| Import package | `src/ai_engineering/` | Explicitly discovered and verified in the wheel. |
| Version | `0.1.0` in `[project]` | Verified from wheel and installed metadata. The MCP SDK server also reports a separately maintained `0.1.0`; `uv.lock` records the resolved local package version. |
| Python requirement | `>=3.11` | Verified from wheel and installed metadata. |
| Runtime dependencies | `mcp>=1.27,<1.28` | Verified from wheel and installed metadata. |
| Development dependencies | `pytest>=9.0`, `ruff>=0.13`, `mypy>=1.18` in the `dev` group | Not runtime dependencies. |
| Console script | `ai-engineering = "ai_engineering.cli:main"` | Verified from wheel metadata and an isolated installed-script smoke test. |
| Build backend | `setuptools.build_meta` with `setuptools>=68` | Explicitly configured and verified. |
| Package discovery | Setuptools `package-dir = {"" = "src"}` and discovery below `src` | Explicitly configured and verified. |
| Package data | No package-data configuration or non-Python package data is present | No package-data requirement is currently claimed. |
| README / LICENSE | README is project metadata; the sdist includes README and LICENSE. | Verified by archive inspection. |
| Artifacts / clean install | Wheel and sdist are built from a temporary clean source copy; the wheel is installed into a fresh external venv. | Verified by `tests/release/test_distribution.py`. |

The authoritative distribution metadata source is currently `pyproject.toml`. The independent MCP
server version string is not distribution metadata, but it must remain consistent with the release
line when version changes are separately approved. REL-0001 does not change version ownership or
the version number.

## Release-Layer Separation

| Layer | Scope |
|---|---|
| A. Local distribution verification | **REL-0001 scope.** Build and inspect wheel/sdist locally, then install and smoke-test the wheel in an isolated environment. |
| B. GitHub Release | Future decision: release objects, release notes, and uploaded artifacts. |
| C. PyPI / public package publishing | Future decision: credentials, package ownership, and publication policy. |
| D. CI automation | Future decision: automated execution, caching, and credentials. |

Passing REL-0001 is not a GitHub Release, PyPI publication, or general production-readiness claim.

## Artifact Contract

Implementation must build both artifacts from a clean checkout and a clean build-output directory:

- one wheel named with the normalized distribution name and project version, of the form
  `ai_engineering-0.1.0-<wheel-tags>.whl`;
- one source distribution named `ai_engineering-0.1.0.tar.gz`.

The exact wheel compatibility tags are determined by the selected build backend and build result;
they are not pre-claimed by this design. The metadata version in both artifacts must be `0.1.0`.

## Build-System Contract

The repository uses an explicit PEP 517 backend:

```toml
[build-system]
requires = ["setuptools>=68"]
build-backend = "setuptools.build_meta"
```

The approved supported floor is 68. The `src` layout uses an explicit package-dir mapping and
setuptools package discovery below `src`; it does not rely on working-directory imports or add
speculative package-data settings.

## Wheel Content Policy

The wheel is an installable runtime artifact. It must contain:

- the `ai_engineering` package modules from `src`, including `ai_engineering.cli`;
- distribution metadata in `ai_engineering-0.1.0.dist-info/`; and
- console-script metadata that produces `ai-engineering` from `ai_engineering.cli:main`.

It must not contain tests, repository documentation, `.git`, `.venv`, caches, build/test temporary
files, machine-specific paths, or unapproved package data. Documentation is intentionally excluded
from the wheel: the current docs are repository documentation rather than runtime package data.
The project must not add package-data requirements unless a separately approved runtime need is
identified.

## Source Distribution Policy

The verified sdist contains the files necessary to build and assess the source package:

- `pyproject.toml`, `README.md`, and `LICENSE`;
- `src/ai_engineering/`;
- `tests/`, as source-verification material.
- `docs/`, as approved repository documentation.

`MANIFEST.in` explicitly encodes this policy and excludes `uv.lock`. Archive inspection verifies
that VCS metadata, virtual environments, caches, bytecode, build output, and temporary or
machine-specific files are absent.

## Isolated Install Contract

The future verification procedure is:

1. Build wheel and sdist into a fresh external temporary output directory.
2. Inspect both archives against this contract.
3. Create a fresh virtual environment outside the canonical checkout.
4. Install the built wheel into that environment, without editable installation.
5. Run an import check from a directory outside the checkout and confirm its module path belongs to
   the isolated environment, not `src`.
6. Read `importlib.metadata.version("ai-engineering")` from the isolated environment and require
   `0.1.0`.
7. Run the isolated environment's `ai-engineering --help` and require exit code `0`.
8. Optionally and deterministically run `ai-engineering project create` against a temporary
   destination, then verify its expected output and generated project.

The procedure must not use an editable install, `PYTHONPATH=<checkout>/src`, the checkout as the
current import source, a global `ai-engineering` installation, a OneDrive path, or a
machine-specific source path.

## Dependency-Install Policy

Build dependencies, runtime dependencies, and development/test dependencies are distinct:

- the PEP 517 build requirements install only what artifact construction needs;
- the wheel declares its runtime dependency on `mcp`;
- pytest, Ruff, and mypy remain development/test dependencies and must not become runtime
  requirements merely to verify an installed artifact.

Initial clean-install verification may require network access when the selected build backend or
runtime wheels are not already cached or supplied by a controlled local source. REL-0001 should
prefer pre-resolved or cached dependencies for final reproducibility runs, while recording whether
network was used. It does not claim offline-install support and does not vendor dependencies.

## Metadata and CLI Verification

Artifact and installed-distribution checks must read metadata from the wheel or installed
distribution, not solely from `pyproject.toml`. They must verify:

- distribution name `ai-engineering` and import package `ai_engineering`;
- version `0.1.0`;
- Python requirement `>=3.11`;
- runtime dependency `mcp>=1.27,<1.28`; and
- console entry point `ai-engineering = ai_engineering.cli:main`.

The installed console script is verified only from the isolated environment with
`ai-engineering --help`. The optional project-creation smoke test must use an isolated temporary
destination and prove delegation works without source-tree imports.

## Reproducibility Definition

REL-0001 defines reproducible verification as repeatable commands, metadata expectations, artifact
types, content policy, and isolated-install behavior. It does not promise byte-for-byte identical
artifacts; timestamp normalization and binary reproducibility are outside this milestone.

## Release Checklist Integration

REL-0001 implementation must add evidence—not a publication claim—to `RELEASE_CHECKLIST.md` for:

- wheel build PASS;
- sdist build PASS;
- wheel content PASS;
- sdist content PASS;
- isolated wheel install PASS;
- installed import PASS;
- installed version PASS; and
- installed console script PASS.

## Failure Classification

| Class | Evidence required before changing configuration |
|---|---|
| A. Build configuration | Build command, selected backend/version, full non-secret stderr, and `pyproject.toml` build section. |
| B. Package discovery | Wheel file listing and expected versus actual `src/ai_engineering` modules. |
| C. Artifact content | Wheel/sdist listing, policy row violated, and the configuration that selected the files. |
| D. Metadata | Built/installed metadata fields and the matching source declaration. |
| E. Dependency install | Installer command, resolver result, cache/index context, and non-secret error output. |
| F. Console entry point | Isolated executable path, entry-point metadata, exit code, stdout, and stderr. |
| G. Clean-install isolation | Interpreter/module paths, environment variables, working directory, and proof of any source-tree leakage. |
| H. Version consistency | `pyproject.toml`, built metadata, installed metadata, and independently maintained runtime version evidence. |
| I. Unknown | Exact commands, environment summary, artifact hashes/listings, and minimally sufficient logs. |

## Implementation Strategy

Use bounded release-verification evidence rather than running distribution builds from the entire
unit suite. Preferred layers are metadata/unit checks, archive-inspection checks, a subprocess build
test or script, isolated-venv wheel-install smoke, and installed-CLI smoke. A focused release
verification test module or script is preferred; broad test-suite packaging work is not implied.

## Non-Goals

REL-0001 excludes PyPI publishing, GitHub Release creation, signing, provenance systems, CI
workflows, release-tag automation, semantic-version-policy redesign, changelog automation, Docker
packaging, binary installers, dependency vendoring, workspace safety changes, new CLI features, and
MCP behavior changes.

## Completion Criteria

REL-0001 is **COMPLETE / VERIFIED** because:

1. explicit, justified build configuration is present;
2. wheel and sdist build successfully;
3. artifact contents match the approved policy;
4. isolated wheel installation succeeds;
5. the installed package imports and reports correct installed metadata/version;
6. the installed `ai-engineering` console script works without a source-tree or `PYTHONPATH`
   dependency;
7. full pytest, Ruff, mypy, and `git diff --check` pass;
8. the release checklist records the evidence; and
9. no publishing or general production-readiness claim is made.

## Completion Evidence

`tests/release/test_distribution.py` builds a wheel and sdist from a temporary clean source copy,
programmatically inspects their contents and metadata, and installs the wheel into a fresh external
virtual environment. It verifies the installed import path, installed distribution metadata,
`ai-engineering --help`, the `project create` hierarchy, and a safe generated-project Git smoke
with `main` and an initial commit. The artifacts are not committed and the canonical checkout is not
used as the installed import source.

The verified artifact names are `ai_engineering-0.1.0-py3-none-any.whl` and
`ai_engineering-0.1.0.tar.gz`. The complete suite passed with 90 tests; Ruff and mypy reported no
findings. The current verification required package-index access to provision `setuptools>=68` in
the isolated build environment; it did not establish offline-build or offline-install support.
GitHub Release creation, PyPI publishing, and CI implementation were not performed.
