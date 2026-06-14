# BimpeAI SDKs

Official TypeScript and Python SDKs for the BimpeAI Agent Console API, developed together in one monorepo.

## Packages

| Package | Language | Description |
| --- | --- | --- |
| [`@bimpeai/sdk`](./packages/sdk-typescript) | TypeScript | Zero-dependency client over native fetch; runs on Node 24+, Bun, Deno, browsers, and edge runtimes |
| [`bimpeai`](./packages/sdk-python) | Python | Synchronous and asynchronous clients, typed with Pydantic over httpx; Python 3.10+ |

Both expose the same surface: agents and their sub-resources, workflows, conversations and messages (including SSE streaming), and a calls placeholder, with shared semantics for pagination, typed errors, retries, and idempotency.

## Install

TypeScript:

```bash
pnpm add @bimpeai/sdk
```

Python:

```bash
pip install bimpeai
# or: uv add bimpeai
```

See each package's README for quickstarts, the full resource tree, and configuration.

## Development

The TypeScript packages use pnpm workspaces; the Python package uses uv. They are independent toolchains living side by side.

TypeScript:

```bash
pnpm install
pnpm build
pnpm test
pnpm lint
pnpm typecheck
```

Python (from `packages/sdk-python`):

```bash
uv sync
uv run pytest
uv run ruff check src tests examples
uv run pyright
```

## Releasing

TypeScript ships to npm via changesets. Python ships to PyPI via GitHub Actions using OIDC trusted publishing, with no stored token: a push to `staging` publishes a beta (`X.Y.Z.devN`), and a push to `main` publishes the stable version from `pyproject.toml`.

## License

MIT
