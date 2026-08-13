# SDK-0001 Template Design

## Purpose

This document defines the first version of the standalone project template model for SDK-0001.

It describes the structure, required files, placeholder mechanism, branch convention, and generated documentation expectations for new standalone AI-Engineering projects.

## Template Scope

The first version of SDK-0001 focuses on generating a minimal standalone project skeleton with complete engineering documentation and a consistent repository structure.

The generated project is intentionally limited to documentation output. It does not include a
runtime scaffold, CLI implementation, or application code APIs.

## Public Creation API

SDK-0001 exposes a typed Python API for creating a standalone document-first project:

- `StandaloneProjectRequest` supplies the target directory, required project name and
  description, optional project metadata, and optional additional documents.
- `create_standalone_project(request)` is the recommended public entry point.
- `StandaloneProject` reports the target directory, generated files, and default branch.

`ProjectTemplateGenerator` is the internal implementation layer. The existing
`create_project_template()` mapping-based function remains a compatibility-level API and is not
the recommended interface for new callers.

The public creation API does not add a generated CLI, runtime or code scaffold, `LICENSE`, remote
Git operations, or any files beyond the document-first template defined here.

## Required Generated Files

Every generated project must contain the following files:

- `README.md`
- `AI_CHAT_START.md`
- `PROJECT_CONTEXT.md`
- `PROJECT_MAP.md`
- `CURRENT_STATUS.md`
- `ROADMAP.md`
- `DECISIONS.md`
- `CODING_STANDARDS.md`
- `MASTER_INDEX.md`

Each required file must include the following metadata:

- purpose of the file
- ownership of maintenance
- creation timing
- mandatory sections
- forbidden content

### README.md

Purpose:
- provide a project overview, usage guidance, and next steps for contributors.

Maintained by:
- project owner or initial author.

Created:
- at project generation time.

Mandatory sections:
- project name and description
- purpose and scope
- usage or bootstrap guidance
- link to AI_CHAT_START.md
- link to documentation index

Forbidden content:
- implementation details beyond architecture summary
- specific code examples that are not yet implemented
- unrelated release history from AI-Engineering

### AI_CHAT_START.md

Purpose:
- bootstrap a new chat session with the generated project context.

Maintained by:
- project owner or maintainer.

Created:
- at project generation time.

Mandatory sections:
- document purpose and bootstrap order
- core project documents list
- current project status summary
- guidance for continuing work in this generated project

Forbidden content:
- AI-Engineering-specific operational history unrelated to the generated project
- implementation instructions for code generation or CLI usage
- external project references that are not part of the generated workspace

### PROJECT_CONTEXT.md

Purpose:
- describe project vision, objectives, and engineering principles.

Maintained by:
- project owner or maintainer.

Created:
- at project generation time.

Mandatory sections:
- project purpose
- vision statement
- initial objectives
- engineering principles

Forbidden content:
- unrelated corporate or product strategy
- implementation task lists that belong in ROADMAP.md

### PROJECT_MAP.md

Purpose:
- describe repository structure and architecture boundaries.

Maintained by:
- project owner or maintainer.

Created:
- at project generation time.

Mandatory sections:
- repository layout
- runtime or component architecture overview
- development phases or milestones
- relationship to reference projects when relevant

Forbidden content:
- detailed implementation plans or APIs
- overly specific module contents that belong in source files

### CURRENT_STATUS.md

Purpose:
- communicate the current phase, completed work, and next steps.

Maintained by:
- project owner or maintainer.

Created:
- at project generation time.

Mandatory sections:
- status and current phase
- completed items
- in-progress items
- next milestone or next steps

Forbidden content:
- speculative future milestones without current relevance
- detailed technical design content

### ROADMAP.md

Purpose:
- define planned project phases and deliverables.

Maintained by:
- project owner or maintainer.

Created:
- at project generation time.

Mandatory sections:
- project roadmap structure
- sprint or phase goals
- planned deliverables
- status of each phase

Forbidden content:
- excessive detail on individual tickets
- implementation-only task checklists

### DECISIONS.md

Purpose:
- capture accepted engineering decisions and policies.

Maintained by:
- project owner or maintainer.

Created:
- at project generation time.

Mandatory sections:
- decision ID and title
- status
- decision statement
- rationale when needed

Forbidden content:
- transient discussion notes
- unresolved debates without decision status

### CODING_STANDARDS.md

Purpose:
- define code and design conventions for the project.

Maintained by:
- project owner or maintainer.

Created:
- at project generation time.

Mandatory sections:
- general principles
- architecture guidance
- naming conventions
- testing and documentation expectations

Forbidden content:
- project-specific implementation details
- informal coding preferences not aligned with project guidance

### MASTER_INDEX.md

Purpose:
- provide the document index and project overview.

Maintained by:
- project owner or maintainer.

Created:
- at project generation time.

Mandatory sections:
- document table and purpose
- active engineering tasks or project status summary
- source tree outline
- current priority

Forbidden content:
- outdated or unrelated document listings
- broad product marketing content

## LICENSE

`LICENSE` is recommended but not mandatory.

The framework should not automatically create a specific license file for every generated project.

The choice of license is a project-level decision and depends on the target project, organization, and legal needs.

## `docs/` Directory Rule

The `docs/` directory is not required by default.

It may be created only when there is a real engineering need for additional project documentation.

Examples of optional docs:

- `docs/feature-design.md`
- `docs/architecture.md`
- `docs/migration-report.md`
- `docs/troubleshooting.md`

The template must not generate empty documentation files automatically.

## AI_CHAT_START.md Model

Generated projects use the same AI_CHAT_START.md model as AI-Engineering.

A new chat should read the generated `AI_CHAT_START.md` and obtain sufficient context to continue work.

The content must be adapted to the generated project, but the bootstrap order remains the same:

1. README.md
2. PROJECT_CONTEXT.md
3. PROJECT_MAP.md
4. CURRENT_STATUS.md
5. ROADMAP.md
6. DECISIONS.md
7. CODING_STANDARDS.md
8. MASTER_INDEX.md

## Branch Convention

Default branch for standalone generated projects:

- `main`

`master` is allowed only for legacy or compatibility reasons.

## Placeholder Mechanism

The initial design uses a minimal placeholder mechanism.

### Supported placeholders

- `{{PROJECT_NAME}}`
- `{{PROJECT_DESCRIPTION}}`
- `{{PROJECT_ID}}`
- `{{AUTHOR}}`
- `{{CREATED_DATE}}`

### Required placeholders

- `{{PROJECT_NAME}}`
- `{{PROJECT_DESCRIPTION}}`

These placeholders must be present in generated project metadata files and documentation templates.

### Optional placeholders

- `{{PROJECT_ID}}`
- `{{AUTHOR}}`
- `{{CREATED_DATE}}`

Optional placeholders may be used when the generator has the data available.

### Naming rules

- Placeholders are uppercase, underscore-separated, and wrapped in double curly braces.
- They must use ASCII letters, digits, and underscores only.
- Example: `{{PROJECT_NAME}}`, `{{CREATED_DATE}}`

### Unknown placeholders

- Unknown placeholders must be preserved in the template source and must cause validation failure during generation if they remain unresolved.
- The first version of the template should require all placeholders to be resolved or explicitly marked as intentionally not applicable.

### Unfilled placeholders

- A placeholder may not remain unfilled in generated output.
- If the framework cannot populate a placeholder, generation must fail and report the unresolved placeholder.

## Template File Structure

The first version of the template has this structure:

```
template/
├── README.md
├── AI_CHAT_START.md
├── PROJECT_CONTEXT.md
├── PROJECT_MAP.md
├── CURRENT_STATUS.md
├── ROADMAP.md
├── DECISIONS.md
├── CODING_STANDARDS.md
├── MASTER_INDEX.md
└── docs/
```

The `docs/` folder should exist only when there is at least one optional additional document to include.

## Open Questions

No blocking questions.
