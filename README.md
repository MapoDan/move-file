# MP3 Directory Watcher Service

Production-ready Dockerized Python service for self-hosted environments (Portainer-friendly) that watches multiple folders and routes each new `.mp3` to a dedicated processing handler.

## Features
- Event-driven filesystem monitoring via `watchdog` (no polling loops).
- Handler/plugin-style routing by source directory.
- Debounce/stability checks (size must be stable before processing).
- Retry + error isolation (single file failures do not crash the service).
- Persistent processed state with SQLite.
- JSON structured logs to stdout.
- Non-root container and Docker healthcheck.
- GHCR CI/CD via GitHub Actions.

## Repository Structure

```text
.
├── .env.example
├── .github/workflows/docker-publish.yml
├── Dockerfile
├── docker-compose.yml
├── entrypoint.sh
├── requirements.txt
├── app
│   ├── main.py
│   ├── config
│   ├── core
│   │   ├── config.py
│   │   ├── logging_config.py
│   │   └── state.py
│   ├── logs
│   ├── scripts
│   │   ├── base.py
│   │   ├── clean_tag_file.py
│   │   ├── set_tag.py
│   │   └── upload_file.py
│   └── watchers
│       ├── router.py
│       └── service.py
└── scripts/healthcheck.py
```

## Directory-to-Handler Mapping
- `INPUT_DIR` -> `clean-tag-file.py` (`CleanTagFileHandler`): remove ID3 tags and move to `DIR_CLEAN`.
- `DIR_CLEAN` -> `set-tag.py` (`SetTagHandler`): call remote OneTagger endpoint.
- `DIR_TAGGED` -> `upload-file.py` (`UploadFileHandler`): upload to Nextcloud path `/[artist]/[album]/[track title].mp3`, then delete local file optionally.

## Why SQLite State Persistence
Pros:
- durable across restarts
- no in-memory duplication
- low operational complexity

Cons:
- single-file DB (not ideal for multi-writer scale-out)
- requires volume persistence

For horizontal scaling, migrate to Redis/PostgreSQL dedup keys.

## Local Run
1. Copy env:
   ```bash
   cp .env.example .env
   ```
2. Build/run:
   ```bash
   docker compose up -d --build
   ```

## Portainer Deployment
1. Push repository to GitHub.
2. Let GitHub Actions publish image to GHCR.
3. In Portainer Stack, use:
   `ghcr.io/<org>/<repo>:latest` (or `:vX.Y.Z`).
4. Configure bind mounts and env vars from `.env.example`.
5. Redeploy stack on new tag.

## GitHub Actions CI/CD
Workflow: `.github/workflows/docker-publish.yml`
- builds image with buildx cache
- pushes to GHCR on branch/tag pushes
- publishes tags: `latest`, branch tags, semver tags

## Extending with New Handlers
1. Add a new class in `app/scripts/*.py` with `handle(file_path, settings)` and `name`.
2. Register in `HandlerRouter.mapping`.
3. Add env vars if needed in `Settings`.

No watcher core changes are needed beyond router mapping registration.

## Scalability Suggestions
- Add bounded worker queue + thread pool.
- Replace SQLite with Redis/Postgres for distributed dedup.
- Emit metrics (Prometheus/OpenTelemetry).
- Add dead-letter directory for repeated failures.
- Add checksum-based dedup for renamed duplicates.
