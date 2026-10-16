# ComojueCamCloud Agent Guide

## Project Scope

ComojueCamCloud is an optional Python server that complements the ComojueCam Android application. It provides backend support for features such as media synchronization, remote configuration, and telemetry. The server must remain lightweight and optional—ComojueCam must function fully without it.

## Repository Layout

- `src/comojuecamcloud/__init__.py`: package entry point and `main()` function.
- `src/comojuecamcloud/`: all Python source modules.
- `pyproject.toml`: project metadata, dependencies, and `uv_build` configuration.
- `uv.lock`: locked dependency versions.
- `.python-version`: pinned Python version.
- `README.md`: project overview.

## Build And Verify

Use `uv` for environment and dependency management:

```bash
uv sync
uv run comojuecamcloud
```

Always run `uv sync` after modifying `pyproject.toml`. Verify behavior with `uv run comojuecamcloud` or the appropriate test command.

## Implementation Rules

- Keep the server lightweight; avoid heavy frameworks unless explicitly requested.
- Prefer the Python standard library over third-party packages.
- Do not add dependencies for features that can be implemented with stdlib modules.
- All endpoints and services must be optional—the Android app must work without the server.
- Keep configuration external (environment variables or config files), never hardcode secrets.
- Handle errors gracefully; never expose stack traces to clients.
- Preserve compatibility with the ComojueCam Android client's expected API contracts.

## Change Checklist

1. Check whether the change adds a dependency that can be avoided with stdlib.
2. Run `uv sync` after modifying `pyproject.toml`.
3. Verify the server starts and responds correctly.
4. Test that ComojueCam still functions when the server is unavailable.

## Code Rules

1. KISS for all the code.
2. POO principles to the limit: abstraction, encapsulation, inheritance, and polymorphism.
3. SOLID for all.
4. Human-Understandable code: keep functions short, prioritize small classes and functions that do one thing or groups of related things, good code indentation.
5. Clean Code always: variables, functions, and classes should have meaningful names.
6. Don't put comments everywhere, and if you do include them, keep them short.
7. English first, all the code has to be in English.

## Workflow

1. `main` is the main branch, so always fork it when adding new features, fixing bugs, or making any changes.
2. Merge directly to `main` is bad, use pull requests or suggest the user do a pull request.
3. Keep commits under 200 lines (not strict) and under 10 files.
4. SSD for all, and TDD: write the test first, then the code.
