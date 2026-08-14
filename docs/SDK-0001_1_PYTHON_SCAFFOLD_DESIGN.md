# SDK-0001.1 — Standalone Python Scaffold Contract

**Status:** IMPLEMENTED / VERIFIED
**Scope:** additive follow-up to SDK-0001 V1

## Objective

SDK-0001.1 defines an optional **Standalone Python Project Scaffold** for the
existing standalone project template generator. When selected, it produces a
minimal, portable Python packaging, source, and test baseline alongside the
existing documentation-first project. It is generic engineering infrastructure;
it does not generate application or business logic.

## Relationship to SDK-0001 V1

SDK-0001 V1 remains the authoritative document-first baseline. Its nine root
documents, placeholder behavior, optional `docs/` directory, default `main`
branch, nested-Git protection, and initial-commit behavior are unchanged.

With the Python scaffold disabled, the generated file set and behavior MUST be
identical to V1. In particular, V1 continues to exclude generated
`pyproject.toml`, `src/`, `tests/`, `LICENSE`, CLI code, remote Git operations,
filename substitution, and application-specific runtime code. SDK-0001.1 adds
only an explicit opt-in path; it does not reinterpret those V1 exclusions.

## Exact Scaffold File Contract

When enabled, the scaffold adds these required files to the V1 output:

| Candidate | Classification | Contract and rationale |
|---|---|---|
| `pyproject.toml` | REQUIRED | Provides portable build, project, test, lint, and type-check configuration. |
| `.gitignore` | REQUIRED | Ignores common Python caches, virtual environments, coverage output, and build artifacts without machine-specific paths. |
| `src/<package_name>/__init__.py` | REQUIRED | Establishes an importable `src`-layout package. |
| `tests/test_smoke.py` | REQUIRED | Proves that the generated package imports under the declared test runner. |
| Existing `README.md` | EXCLUDED | V1 already creates it; this scope does not rewrite its generated contents. |
| Additional README integration | EXCLUDED | No scaffold-specific commands or implementation guidance are added automatically. |
| `LICENSE` | EXCLUDED | License selection remains a project/legal decision. |
| `src/<package_name>/py.typed` | EXCLUDED | The scaffold does not claim typed-distribution support. |
| `tests/__init__.py` | EXCLUDED | Pytest does not require it and omitting it avoids imposing package-style tests. |

`<package_name>` is a derived directory name, not filename placeholder
substitution. Optional user-supplied documentation remains governed by V1 and
is not part of this scaffold contract.

## Package-Name Derivation

The implementation derives one ASCII Python package name from
`StandaloneProjectRequest.project_name` as follows:

1. Trim surrounding whitespace and convert to lowercase.
2. Replace every run of spaces or hyphens with one underscore.
3. Replace every remaining character outside ASCII letters, digits, and
   underscores with an underscore; collapse repeated underscores and strip
   leading/trailing underscores.
4. If the result begins with a digit, prefix it with `project_`.
5. If the result is a Python keyword, prefix it with `project_`.
6. Require the final result to be a non-empty ASCII `str.isidentifier()` value
   and not a keyword.

For example, `My Sample-App` becomes `my_sample_app`, and `123 Start` becomes
`project_123_start`. A name that normalizes to empty, such as one containing
only unsupported characters, is invalid and generation fails. Unicode is not
transliterated; unsupported characters follow the replacement rule so results
remain portable across tools and filesystems.

There is one package per generated project, so there is no intra-project
collision namespace. Distinct display names can normalize to the same package
name; that deterministic ambiguity is accepted because generation occurs in an
empty target directory. SDK-0001.1 provides no package-name override.

## `pyproject.toml` Contract

The generated file uses standard, portable PEP 517/PEP 621 metadata:

```toml
[build-system]
requires = ["setuptools>=68"]
build-backend = "setuptools.build_meta"

[project]
name = "<distribution-name>"
version = "0.1.0"
description = "<project description>"
requires-python = ">=3.11"
dependencies = []

[project.optional-dependencies]
dev = ["pytest>=8", "ruff>=0.6", "mypy>=1.11"]
```

`<distribution-name>` is the derived package name with underscores replaced by
hyphens. This makes it a stable packaging identifier while the V1 project name
continues to be the human-facing name in the generated documents. The scaffold
does not install dependencies.

If V1 `author` metadata is supplied, `project.authors` contains one `{ name =
"..." }` entry. If it is absent, the field is omitted. No maintainer field is
generated because V1 has no distinct maintainer input. The project has no
runtime dependencies.

The file also contains only these tool settings:

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]

[tool.ruff]
line-length = 88
target-version = "py311"

[tool.ruff.lint]
select = ["E", "F", "I"]

[tool.mypy]
python_version = "3.11"
files = ["src", "tests"]
warn_unused_configs = true
```

These settings establish a small, conventional quality baseline without
copying AI-Engineering-specific plugin, path, or strictness policy.

## Source and Test Scaffold

`src/<package_name>/__init__.py` contains only a package docstring. It does not
export a version, define an entry point, or contain application logic.

`tests/test_smoke.py` imports `<package_name>` and asserts that the imported
module is present. Its test function is fully typed. The expected runner is
pytest, invoked after installing the generated project's optional `dev` extra
or otherwise making pytest available. No framework-specific test conventions
or application tests are generated.

`.gitignore` contains only relative, generic patterns for Python cache files,
virtual environments, coverage output, build artifacts, and editor-local
metadata. It contains no absolute paths or user- or machine-specific entries.

## Git Behavior

SDK-0001.1 preserves V1 Git safety behavior:

- Generation fails when the target is inside an existing Git working tree.
- The target must be non-existent or an empty directory.
- A new repository initializes with `main`, using the existing compatibility
  fallback when `git init --initial-branch=main` is unavailable.
- The same initial commit includes every file generated in that invocation:
  the V1 documents, optional V1 `docs/` files, and all enabled scaffold files.
- The commit message remains `Initial project scaffold: <project-name>
  (Standalone template)`.
- No remote, upstream, push, hosting, or GitHub operation is performed.

Validation failures use `ProjectTemplateError`. A Git initialization, staging,
or commit failure is a hard generation failure with an actionable error; the
implementation must not claim success, attempt remote recovery, or promise
rollback of files already written.

## API Extension

SDK-0001.1 uses option A: add
`include_python_scaffold: bool = False` to `StandaloneProjectRequest`.

The default is deliberately `False`, so existing typed callers preserve V1
behavior. `create_standalone_project()` consumes this field, and
`StandaloneProject.generated_files` includes the scaffold files only when it is
enabled. `ProjectTemplateGenerator` may receive the corresponding internal
option. The compatibility-level `create_project_template()` remains unchanged
and V1-only. This is the smallest explicit extension and avoids profiles,
parallel request types, or a public API redesign.

## Validation Rules

Future implementation MUST validate before writing files:

| Input or condition | Required behavior |
|---|---|
| `project_name` / `project_description` | Retain V1 required-metadata validation. |
| Scaffold option | Require an actual boolean; unsupported scaffold options fail. |
| Derived package name | Apply the derivation rules and reject an empty, non-identifier, or keyword result. |
| Destination | Retain V1 non-existent-or-empty directory validation. |
| Nested Git | Retain V1 parent `.git` protection. |
| Placeholders | Retain V1 unresolved-placeholder failure. |
| Generated paths | Precompute the complete file set and reject any duplicate or existing generated-file collision. |

All validation failures raise `ProjectTemplateError` with the invalid value or
condition identified. Scaffold enablement must not weaken V1 optional-document
filename validation.

## Portability Rules

All generated references use project-relative paths. Generated content MUST NOT
contain `C:\\Users\\...`, `D:\\...`, OneDrive paths, machine-specific Python
executables, or absolute filesystem paths. The scaffold assumes only a
supported Python interpreter satisfying `>=3.11`; it creates neither a virtual
environment nor dependencies.

## Automated Test Matrix

All items below are **IMPLEMENTED / VERIFIED** by the SDK-0001.1 test suite.

| Test | Status |
|---|---|
| Scaffold disabled preserves exact V1 output | IMPLEMENTED / VERIFIED |
| Scaffold enabled generates the exact required file set | IMPLEMENTED / VERIFIED |
| Package-name normalization, leading digit, keyword, and empty-result cases | IMPLEMENTED / VERIFIED |
| `pyproject.toml` metadata and tool configuration | IMPLEMENTED / VERIFIED |
| Generated package is importable | IMPLEMENTED / VERIFIED |
| Generated smoke test is valid under pytest | IMPLEMENTED / VERIFIED |
| Initial commit includes scaffold files | IMPLEMENTED / VERIFIED |
| Nested-Git protection remains enforced | IMPLEMENTED / VERIFIED |
| Invalid package-name behavior | IMPLEMENTED / VERIFIED |
| Existing typed and compatibility APIs remain backward compatible | IMPLEMENTED / VERIFIED |

## Non-Goals

SDK-0001.1 does not add a CLI, Docker, remote repository creation, GitHub
integration, generated CI workflows, dependency installation, virtualenv
creation, framework-specific templates (including FastAPI, Django, or Flask),
application entry-point logic, or code generation beyond the minimal package
scaffold.

## Completion Criteria

The implementation preserves disabled V1 behavior, includes all generated files
in the initial commit, and passes the repository quality gates.
