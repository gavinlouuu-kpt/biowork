# Upgrade: Merge main into 1.21.0 base (preserve build files)

- Status: completed
- Branch: `upgrade/biowork-1.21.0-merge-main`
- Strategy: `git merge -X theirs main --no-commit`, then restore 1.21.0 build files from `HEAD` before commit
- Preserved build files:
  - Root: `pyproject.toml`, `poetry.lock`, `Makefile`, `Dockerfile*`, `docker-compose*.yml`, `.gitignore`
  - Web: `web/package.json`, `web/yarn.lock`, `web/tsconfig*.json`, `web/webpack.config.js`, `web/tailwind.config.js`, `web/postcss.config.js`, `web/jest.config.ts`, `web/babel.config.json`, `web/nx.json`, `web/biome.json`
- Next steps:
  - Validate backend installs with `poetry install` and run quick smoke tests
  - Validate frontend build with `yarn install && yarn build` in `web/`
  - Manually verify upgraded features from `main` in the 1.21.0 base

