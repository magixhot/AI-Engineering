# REL-0001 — Distribution and Release Verification Contract

**Status:** DESIGN / IMPLEMENTATION PENDING
**Scope:** local distribution verification for the existing `ai-engineering` package and CLI

## Objective

REL-0001 establishes a reproducible local distribution-verification contract. It proves that the
repository can build correct wheel and source-distribution artifacts and that an installed wheel
works in an isolated environment. It does not publish, tag, or otherwise release those artifacts.

## Current Packaging State

| Item | Current factual state | Verification state / gap |
|---|---|---|
| Distribution name | `ai-engineering` in `[project]` | Declared, not artifact-verified. |
| Import package | `src/ai_engineering/` | Source layout present. |
| Version | `0.1.0` in `[project]` | Declared, not artifact-verified. The MCP SDK server also reports a separately maintained `0.1.0`; `uv.lock` records the resolved local package version. |
| Python requirement | `>=3.11` | Declared, not artifact-verified. |
| Runtime dependencies | `mcp>=1.27,<1.28` | Declared, not clean-install verified. |
| Development dependencies | `pytest>=9.0`, `ruff>=0.13`, `mypy>=1.18` in the `dev` group | Not runtime dependencies. |
| Console script | `ai-engineering = "ai_engineering.cli:main"` | Declared; previously smoke-tested from the project environment, not from a built artifact. |
| Build backend | No `[build-system]` section | Explicit build contract is absent. |
| Package discovery | No explicit setuptools `package-dir` or discovery configuration | `src`-layout discovery must be made explicit before building. |
| Package data | No package-data configuration or non-Python package data is present | No package-data requirement is currently claimed. |
| README / LICENSE | `README.md` is project metadata; no explicit artifact-inclusion policy exists. `LICENSE` exists but has no packaging declaration. | Wheel/sdist inclusion is unverified. |
| Artifacts / clean install | No wheel, sdist, artifact-content, or clean-install evidence is recorded. | REL-0001 work. |

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

Before implementation, the repository must add and justify an explicit PEP 517 backend. The
preferred baseline to evaluate is:

```toml
[build-system]
requires = ["setuptools>=<supported-floor>"]
build-backend = "setuptools.build_meta"
```

The exact supported setuptools floor is an implementation decision and must be recorded with its
tooling rationale; this design does not select or add it. Because this is a `src` layout, the
implementation must explicitly configure setuptools to discover packages under `src` (normally a
package-dir mapping and a `find` location). It must not rely on implicit working-directory imports
or add speculative package-data settings.

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

The sdist must contain the files necessary to build and assess the source package:

- `pyproject.toml`, `README.md`, and `LICENSE`;
- `src/ai_engineering/`;
- `tests/`, as source-verification material.

The implementation must explicitly decide and encode the following currently undefined policy
points, then inspect the resulting archive: whether `docs/` belongs in the sdist (default proposed
policy: exclude repository-internal milestone documentation) and whether `uv.lock` belongs in it
(default proposed policy: exclude it because it is a local resolution record rather than build
metadata). No claim is made until the selected backend configuration and an artifact inspection
prove the policy. The sdist must exclude VCS metadata, virtual environments, caches, generated
build outputs, and temporary or machine-specific files.

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

REL-0001 becomes **COMPLETE / VERIFIED** only when:

1. explicit, justified build configuration is present;
2. wheel and sdist builds succeed;
3. artifact contents match the approved policy;
4. isolated wheel installation succeeds;
5. the installed package imports and reports correct installed metadata/version;
6. the installed `ai-engineering` console script works without a source-tree or `PYTHONPATH`
   dependency;
7. full pytest, Ruff, mypy, and `git diff --check` pass;
8. the release checklist records the evidence; and
9. no publishing or general production-readiness claim is made.
