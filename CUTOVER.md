# Cutover: ASP.NET → FastAPI

Ordering matters. The new tables already exist on production but are **empty**, so
migrating data must happen *before* the API switches over, or the site shows zero events.

Legacy tables (`"Events"`, `"AspNetUsers"`, …) are quoted PascalCase identifiers and are
therefore distinct relations from the new lowercase ones. Nothing is dropped until step 7,
so every step before it is reversible.

Backups already taken: `backups/nuieee-backup-*.sql` (local) and `~/nuieee-backup-*.sql` (VPS).

## Progress

- [x] **Step 1** — data migrated: 18 events, 35 photos, 2 users in the new tables
- [x] **Step 2** — `JWT_SECRET` (64 chars) and `API_TAG` added to the VPS `.env`
- [ ] **Step 3** — commit and push
- [ ] **Step 4** — watch the deploy
- [ ] **Step 5** — point the frontend at the new API
- [ ] **Step 6** — verify end to end
- [ ] **Step 7** — drop the legacy tables (wait a week)

---

## 1. Migrate the data

The VPS database binds to loopback, so open a tunnel first.

```bash
# terminal 1 - leave running
ssh -o ExitOnForwardFailure=yes -N -L 15432:127.0.0.1:5432 alinur@65.108.155.254
```

`ExitOnForwardFailure=yes` matters: without it, ssh stays connected even when the forward
fails, so the tunnel looks up but nothing is listening.

If it reports `bind [127.0.0.1]:15432: Permission denied`, the port is already held —
Windows reports an exclusively-bound port as a permission error rather than "in use".
Find and clear the holder:

```powershell
Get-NetTCPConnection -LocalPort 15432 -State Listen |
  ForEach-Object { Get-Process -Id $_.OwningProcess }
# then: Stop-Process -Id <pid> -Force
```

Or just pick another port and change it in both places (`-L 15433:` and the `--dsn`).

```bash
# terminal 2
cd ~/Desktop/NuIeee
DB_PASSWORD=$(ssh alinur@65.108.155.254 'grep ^DB_PASSWORD= ~/apps/backend/NuIeee/.env | cut -d= -f2-')

# dry run first - prints the UTC -> +05 conversion for all 18 events
uv run python scripts/migrate_legacy_data.py \
  --dsn "postgresql+asyncpg://postgres:$DB_PASSWORD@127.0.0.1:15432/nuieee"

# apply
uv run python scripts/migrate_legacy_data.py \
  --dsn "postgresql+asyncpg://postgres:$DB_PASSWORD@127.0.0.1:15432/nuieee" --apply
```

**Save the two generated passwords it prints** - they are the only copy. The script refuses
to run twice, so a re-run cannot duplicate rows.

Verify:

```bash
ssh alinur@65.108.155.254 'docker exec nuieee-db psql -U postgres -d nuieee \
  -c "SELECT (SELECT count(*) FROM events) e, (SELECT count(*) FROM event_photos) p, (SELECT count(*) FROM users) u;"'
# expect: 18 | 35 | 2
```

## 2. Add the new environment variables on the VPS

`JWT_SECRET` replaces the .NET-style `JWT__KEY` and must be at least 32 characters.

```bash
ssh alinur@65.108.155.254
cd ~/apps/backend/NuIeee
echo "JWT_SECRET=$(openssl rand -hex 32)" >> .env
echo "API_TAG=latest" >> .env
grep -c . .env        # sanity: GHCR_OWNER and DB_PASSWORD are already there
```

## 3. Commit and push

Everything below is driven by CI. Nothing needs to be edited on the VPS by hand — the
deploy job runs `git reset --hard origin/main` on the server first, so the compose file
always matches what is on `main`.

```bash
cd ~/Desktop/NuIeee
git add -A
git commit -F- <<'MSG'
feat: Replace ASP.NET backend with FastAPI. Add JWT auth with role hierarchy, events CRUD, user management and MinIO presigned uploads. Add Alembic migrations and legacy data migration script. refactor: Rebuild frontend API layer on TanStack Query, add route guards and split the event creation page. fix: Correct detached-graph photo orphaning, missing 404s, open registration endpoint and alt-text misalignment on upload.
MSG
git push origin main
```

## 4. Watch the deploy

```bash
gh run watch
```

The workflow runs ruff and pytest, builds and pushes the image to GHCR, syncs the server
from git, runs migrations as a one-shot container, starts the API, then polls
`/health` for 60s and rolls back automatically if it does not come up.

The old .NET container is named `nuieee-api`, and so is the new one, so compose replaces
it in place. nginx needs no change: `api.ieee.nu` already proxies to `localhost:8080`,
which is where the new container publishes.

## 5. Point the frontend at the new API

The frontend lives in the separate `nuieee-client` repo and deploys from Vercel.

**There is an unavoidable window here.** The live frontend calls the old endpoints
(`/events/create-event`, `/superadmin/users`), which no longer exist once step 4 lands, so
the events page breaks until this step completes. Do step 5 straight after step 4.

First set the environment variable in the Vercel dashboard for `nuieee-client`: 

```
VITE_API_BASE_URL = https://api.ieee.nu/api
```

`VITE_MINIO_HOST` can be deleted — the API returns `publicUrl` directly now, so the
frontend no longer builds MinIO URLs itself.

Then push, which triggers the Vercel deploy:

```bash
cd ~/Desktop/nuieee-client
git add -A
git commit -F- <<'MSG'
refactor: Rebuild API layer against the FastAPI backend and move server state to TanStack Query. Split the 474-line event creation page into a hook and focused components. feat: Add role-aware route guards for admin and superadmin pages. fix: Correct auth token claim names, alt-text misalignment when uploading photos, and handle 401 by clearing the session.
MSG
git push origin main
```

Vercel picks up the env var on the next build, so set it **before** pushing.

## 6. Verify end to end

```bash
curl -s https://api.ieee.nu/health
curl -s https://api.ieee.nu/api/events | head -c 200
curl -s -o /dev/null -w "%{http_code}\n" https://api.ieee.nu/api/users   # expect 401
```

Then in the browser: log in with a password from step 1, create a test event with a photo,
confirm the image renders from `minio.ieee.nu`, and delete it again.

nginx needs **no change** - `api.ieee.nu` already proxies to `localhost:8080`, which is
where the new container publishes.

## 7. Only after the site is confirmed healthy: drop the legacy tables

Keep them for at least a week. When ready:

```sql
DROP TABLE "EventPhotos", "Events", "TeamMembers", "Teams",
           "AspNetUserRoles", "AspNetUserClaims", "AspNetUserLogins",
           "AspNetUserTokens", "AspNetRoleClaims", "AspNetUsers", "AspNetRoles",
           "__EFMigrationsHistory" CASCADE;
```

Then delete the .NET projects (`NuIeee.WebApi/`, `NuIeee.Application/`,
`NuIeee.Infrastructure/`, `NuIeee.Domain/`, `NuIeee.sln`, `Dockerfile`) and rename
`Dockerfile.api` to `Dockerfile`.

## Rollback

The deploy workflow rolls back automatically on a failed health check. To roll back to the
.NET API manually, the legacy tables are still intact until step 7:

```bash
cd ~/apps/backend/NuIeee
git checkout HEAD~1 -- docker-compose.prod.yml
docker compose -f docker-compose.prod.yml up -d
```

Migration applied. Generated passwords (save these now):
  superadmin   cjnG2lR7a6FnXjbOOBOzZQ
  admin        9-_whrbjzGicdIbH_vURZw