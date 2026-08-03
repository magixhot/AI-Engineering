# CODING_STANDARDS.md

# AI-Engineering

## Coding Standards

---

# General Principles

* Readability over cleverness.
* Simplicity over complexity.
* Explicit over implicit.
* Small, focused modules.
* Public API first.
* Testability by design.

---

# Architecture

* Preserve originals.
* Extend, never replace.
* Single Responsibility Principle.
* Dependency Injection.
* Composition over inheritance.
* Clear module boundaries.

---

# Project Structure

Every module should have a single responsibility.

Large files should be split into focused modules.

Avoid circular dependencies.

Shared functionality belongs in `shared/`.

---

# Naming

* Use descriptive names.
* Avoid abbreviations unless widely accepted.
* Use consistent terminology throughout the project.

---

# Type Hints

All public functions and methods must use Python type hints.

New code should be fully typed.

---

# Error Handling

Raise meaningful exceptions.

Do not silently ignore errors.

Provide actionable error messages.

---

# Logging

Use structured logging.

Avoid `print()` in production code.

Log important engineering events.

---

# Testing

Every public component should have automated tests.

Prefer unit tests.

Add integration tests for cross-module behavior.

---

# MCP Tools

Each tool must:

* Have one responsibility.
* Validate its input.
* Return structured results.
* Report failures clearly.
* Be independently testable.

---

# Git

* Small commits.
* One logical change per commit.
* Clear commit messages.
* No unrelated changes in the same commit.

---

# Documentation

Documentation is part of the implementation.

Any architectural change must be reflected in the project documentation before implementation.

No feature is considered complete until its documentation is updated.
