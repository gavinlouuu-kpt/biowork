# Biowork Upgrade: main -> 1.21.0 base

This document captures the merge of project features from `main` into the upstream `1.21.0` base while preserving the original 1.21.0 build system.

## Branch
- `upgrade/biowork-1.21.0-merge-main`

## Approach
1. Checked out a new upgrade branch from the 1.21.0-based branch (`branch-from-1.21.0`).
2. Merged with `git merge -X theirs main --no-commit --no-ff` to prefer feature code from `main` on conflicts.
3. Restored build files from 1.21.0 using `git restore --source=HEAD` before committing the merge.

## Preserved Build Files
- Root: `pyproject.toml`, `poetry.lock`, `Makefile`, `Dockerfile*`, `docker-compose*.yml`, `.gitignore`
- Web: `web/package.json`, `web/yarn.lock`, `web/tsconfig*.json`, `web/webpack.config.js`, `web/tailwind.config.js`, `web/postcss.config.js`, `web/jest.config.ts`, `web/babel.config.json`, `web/nx.json`, `web/biome.json`

## Next Steps
- Backend: `poetry install` then run core smoke tests
- Frontend: in `web/` run `yarn install && yarn build`
- Validate that custom features from `main` function on 1.21.0 base

## Notes
- Push may require auth: `git push -u origin upgrade/biowork-1.21.0-merge-main`
- If additional build files need pinning, repeat `git restore --source=HEAD -- <file>` before committing.

