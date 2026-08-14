# SDK-0001.2 — Project Template CLI Contract

**Status:** DESIGN / IMPLEMENTATION PENDING
**Scope:** additive CLI adapter over the verified SDK-0001 project-template API

## Objective

SDK-0001.2 exposes the existing standalone project-template capability through a
minimal, stable command-line interface. The CLI MUST construct a
`StandaloneProjectRequest` and call `create_standalone_project()` exactly once;
it MUST NOT duplicate template, scaffold, validation, or Git logic.

SDK-0001 V1 remains the default document-first flow. SDK-0001.1 remains the
explicit optional Python scaffold. This task defines the CLI only; it does not
alter either SDK contract.

## Command Hierarchy

The sole SDK-0001.2 command is:

```text
ai-engineering project create
```

`project` is selected because the command creates a complete standalone
project, not merely a reusable template artifact. `create` leaves room for
future separately approved project operations without introducing them now.
No aliases or further subcommands are part of SDK-0001.2.

## Arguments and Options

| CLI input | Classification | Request mapping / behavior |
|---|---|---|
| `--name NAME` | REQUIRED | `project_name` |
| `--destination PATH` | REQUIRED | `target_directory` |
| `--description TEXT` | REQUIRED | `project_description` |
| `--author NAME` | OPTIONAL | `author`; there is no separate maintainer field in the current API. |
| `--python-scaffold` | OPTIONAL | Sets `include_python_scaffold=True`. |
| `--project-id` | NOT EXPOSED IN V1 CLI | The initial CLI keeps the user-facing surface small. |
| `--created-date` | NOT EXPOSED IN V1 CLI | The initial CLI does not expose generation metadata beyond author. |
| additional documents | NOT EXPOSED IN V1 CLI | Existing `additional_documents` requires a filename-to-content mapping; file ingestion and inline document syntax are deferred. |
| internal generator options | NOT EXPOSED IN V1 CLI | The CLI calls only the public typed API. |

Argument parsing rejects missing required options before any generation call.

## Scaffold and Path Behavior

`--python-scaffold` is the only scaffold-selection option. Its absence passes
`False`, preserving exact V1 document-only behavior. Its presence passes
`True`, enabling the verified SDK-0001.1 file set.

`--destination` accepts relative or absolute paths. Relative paths resolve from
the CLI process current working directory before request construction; the
success output reports the resolved absolute path. No project-root, OneDrive,
drive-letter, or machine-specific default is assumed.

The CLI delegates target existence/emptiness checks and nested-Git protection to
`create_standalone_project()`. It creates no parent policy beyond the SDK, makes
no remote Git calls, and is portable across Windows, Linux, and macOS subject to
the existing SDK and Git availability.

## Output, Errors, and Exit Codes

Success writes concise `key=value` lines to stdout only:

```text
created_project=<resolved absolute path>
project_name=<input name>
git_branch=main
initial_commit=created
```

When `--python-scaffold` is selected, add
`package_name=<derived package name>`. This stable human-readable format is
sufficient for SDK-0001.2 and is easy for simple automation to parse. JSON
output is explicitly deferred.

Expected errors and operational failures write one actionable message to stderr
and no success data to stdout. Expected user errors do not show a traceback.
The stable exit-code contract is:

| Code | Meaning |
|---|---|
| `0` | Project created successfully. |
| `1` | Expected domain or operational failure. |
| `2` | Command usage or argument-parsing error. |
| `3` | Unexpected internal failure. |

`ProjectTemplateError` maps to exit `1` with its message. This covers invalid
project/package names, an existing/non-empty target, nested Git repositories,
unresolved placeholders, and invalid scaffold options. Predictable Git
initialization, staging, or initial-commit failures also map to exit `1` with a
concise operational message. Argument-parser errors use exit `2`. Unexpected
exceptions use exit `3` and a generic message; traceback display is deferred to
a future explicitly designed diagnostic mode.

## Packaging and Module Boundary

Future implementation adds the console script declaration:

```toml
[project.scripts]
ai-engineering = "ai_engineering.cli:main"
```

The implementation module is `src/ai_engineering/cli.py`. It owns argument
parsing, request construction, stdout/stderr, and exit-code translation only.
It imports and calls `create_standalone_project()`; it does not access
`ProjectTemplateGenerator` internals. `python -m ai_engineering` is not
supported by SDK-0001.2 and is explicitly deferred to avoid adding a second
entry-point contract.

## Backward Compatibility

The existing Python API remains unchanged. The CLI is additive, defaults to V1
output, keeps the Python scaffold opt-in, and leaves
`create_project_template()` unchanged as the compatibility-level V1 API.

## Planned Test Matrix

All tests are **PLANNED / TEST MISSING** for implementation.

| Test | Level |
|---|---|
| CLI help | Subprocess/integration |
| Missing required arguments | Subprocess/integration |
| Successful V1 project generation | Subprocess/integration |
| Successful Python scaffold generation | Subprocess/integration |
| Existing-target error | Subprocess/integration |
| Nested-Git error | Subprocess/integration |
| Invalid project/package input | Unit and subprocess/integration |
| Success stdout contract | Subprocess/integration |
| Expected error stderr contract | Subprocess/integration |
| Exit-code contract | Subprocess/integration |
| No traceback for expected errors | Subprocess/integration |
| Generated initial-commit behavior | Subprocess/integration |
| Existing SDK API behavior remains unchanged | Unit |

## Non-Goals

SDK-0001.2 excludes interactive prompts, a TUI, remote GitHub repository
creation, push/clone operations, Docker, CI workflow generation, framework
templates, extra scaffold profiles, dependency installation, virtualenv
creation, JSON output, CLI default configuration files, and a plugin
architecture.

## Completion Criteria

SDK-0001.2 is complete only when the command contract and packaging entry point
are implemented; the CLI calls the public SDK API; V1 and scaffold flows work;
error and exit behavior is verified; all planned tests pass; repository pytest,
Ruff, and mypy are green; documentation is updated; and existing SDK tests have
no regressions.
