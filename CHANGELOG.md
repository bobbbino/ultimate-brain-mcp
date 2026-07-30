# Changelog

All notable changes to this project are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.6.1] - 2026-07-30

### Fixed

- Streamable-http serving behind a proxy or MCP gateway: FastMCP bakes in a
  localhost-only DNS-rebinding Host allowlist when the server object is
  constructed, so any non-localhost `Host` header (for example a Docker
  container name) was rejected with `421 Misdirected Request` regardless of
  `UB_HOST`. New env vars `UB_ALLOWED_HOSTS` / `UB_ALLOWED_ORIGINS`
  (comma-separated, `:*` port wildcard supported) replace that allowlist
  while keeping the protection enabled; both unset preserves the previous
  localhost-only behaviour. CI now smoke-tests a gateway-style `Host` and
  asserts unlisted Hosts still get 421.

## [0.6.0] - 2026-07-24

### Added

- Container image publishing: a `Dockerfile` (multi-stage uv build, non-root
  runtime) and a `docker` job in the publish workflow that pushes
  `ghcr.io/bobbyhyam/ultimate-brain-mcp` (`X.Y.Z`, `X.Y`, `latest`;
  linux/amd64 + linux/arm64) on each release. CI builds the image and
  smoke-tests streamable-http `initialize` on every PR.
- `UB_TRANSPORT` env var to select the MCP transport (`stdio`, the default,
  or `streamable-http`); the container defaults to `streamable-http` on
  port 8000.

### Changed

- `scripts/release.sh` now uses a PR-based flow: it rolls the CHANGELOG and
  updates `uv.lock` alongside the version bump, opens an auto-merge PR so the
  release commit passes CI before landing, then tags to trigger publishing.

## [0.5.3] - 2026-06-21

### Added

- Restore the `ub` skill (`.claude/skills/ub/SKILL.md`) so the `release-skill`
  workflow can build and attach the `ultimate-brain-mcp.skill` release asset
  again. Updated to a proactive, system-of-record capture skill for goals,
  projects, tasks, and notes.

## [0.5.2] - 2026-06-21

### Added

- Contributor-readiness tooling: `.pre-commit-config.yaml` (ruff lint + format
  and basic hygiene hooks mirroring CI), Dependabot config for `uv` and
  `github-actions`, GitHub issue templates and a pull-request template, and this
  `CHANGELOG.md`. (`AGENTS.md` points agent tooling at `CLAUDE.md`.)
- Developer tooling baseline (PR #16): Ruff lint/format and mypy config, a
  `unit`/`live` pytest marker split, and a CI workflow running ruff, mypy, and
  the credential-free unit suite across Python 3.11/3.12/3.13.

### Changed

- Page body content now uses Notion's server-side Markdown endpoints, giving
  richer round-trips (tables, toggles, nesting) on `get_page_content`,
  `get_note_content`, and `set_page_content`, plus a new targeted
  find-and-replace `patch_page_content` tool.

### Removed

- In-repo `.claude/skills/ub` files; the skill now ships as the
  `ultimate-brain-mcp.skill` release asset.

## [0.5.1] - 2026-06-04

### Added

- Surface task `location` on every task read and accept `parent_task_id` on
  `update_task`.

## [0.5.0] - 2026-05-09

### Added

- `daily_review_snapshot` and `bulk_update_tasks` workflow consolidator tools.

[Unreleased]: https://github.com/bobbyhyam/ultimate-brain-mcp/compare/v0.6.1...HEAD
[0.6.1]: https://github.com/bobbyhyam/ultimate-brain-mcp/compare/v0.6.0...v0.6.1
[0.6.0]: https://github.com/bobbyhyam/ultimate-brain-mcp/compare/v0.5.3...v0.6.0
[0.5.3]: https://github.com/bobbyhyam/ultimate-brain-mcp/compare/v0.5.2...v0.5.3
[0.5.2]: https://github.com/bobbyhyam/ultimate-brain-mcp/compare/v0.5.1...v0.5.2
[0.5.1]: https://github.com/bobbyhyam/ultimate-brain-mcp/compare/v0.5.0...v0.5.1
[0.5.0]: https://github.com/bobbyhyam/ultimate-brain-mcp/releases/tag/v0.5.0
