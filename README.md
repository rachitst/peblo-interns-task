# Peblo TV Mini — 3-Tier Streaming Catalogue Platform

[![CI Pipeline](https://github.com/peblo/peblo-interns-task/actions/workflows/ci.yml/badge.svg)](https://github.com/peblo/peblo-interns-task/actions/workflows/ci.yml)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.114-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791?logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![React](https://img.shields.io/badge/React-18-61DAFB?logo=react&logoColor=black)](https://reactjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0-3178C6?logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![Docker Compose](https://img.shields.io/badge/Docker%20Compose-Ready-2496ED?logo=docker&logoColor=white)](https://docs.docker.com/compose/)

> **End-to-End Content Pipeline**: Internal CMS Content Authoring & Validation ➔ Atomic Catalogue Publishing ➔ High-Performance Netflix-Style Viewer Streaming Interface.  
> Built for the Peblo Platform Engineering Challenge.

---

## Table of Contents
1. [Architecture & System Overview](#1-architecture--system-overview)
2. [Quickstart & Operability (Docker Compose)](#2-quickstart--operability-docker-compose)
3. [Live Verification & Automated Testing](#3-live-verification--automated-testing)
4. [Time Spent Breakdown](#4-time-spent-breakdown)
5. [Part E: Written Reasoning & Technical Decisions](#5-part-e-written-reasoning--technical-decisions)
   - [Atomic Publishing & Crash Resilience](#1-how-we-made-publishing-atomic--crash-resilience)
   - [Storage Abstraction (Local Disk to Cloudflare R2)](#2-storage-abstraction-local-disk--cloudflare-r2)
   - [Search Implementation, Scaling Limits & Next Steps](#3-search-implementation-scaling-limits--next-steps)
   - [Pre-Published JSON vs. Per-Request Database Queries](#4-why-serve-a-pre-published-catalogue-file-trade-offs)
   - [Deliberate Omissions & Scoping](#5-what-we-left-out-and-why)
   - [AI Tools Used & Human Oversight](#6-ai-tool-usage--human-judgment)
   - [Production Alerting Strategy](#7-production-alerting-strategy)
6. [Seed Data Imperfection Traps Handled](#6-seed-data-imperfection-traps-handled)
7. [Role-Based Access Control (RBAC) Matrix](#7-role-based-access-control-rbac-matrix)
8. [API Endpoint Documentation](#8-api-endpoint-documentation)

---

## 1. Architecture & System Overview

```
                                  ┌─────────────────────────────┐
                                  │   Internal CMS (Port 3000)   │
                                  │ React + TS + TanStack Query │
                                  └──────────────┬──────────────┘
                                                 │ (X-User-Role: admin / editor)
                                                 ▼
┌─────────────────────────────┐   ┌─────────────────────────────┐
│  Viewer UI (Port 3001)      │   │   Core API (Port 8000)      │
│ Netflix-style Browse/Search │◄──┤ FastAPI + Asyncpg + Pillow  │
└──────────────┬──────────────┘   └──────────────┬──────────────┘
               │                                 │
               │ (GET /catalog)                  │ (Atomic .tmp Swap)
               ▼                                 ▼
┌─────────────────────────────┐   ┌─────────────────────────────┐
│ Storage / Published Feed    │   │  PostgreSQL 16 Database     │
│ catalogue.json (Atomic)     │   │  Shows, Seasons, Episodes   │
└─────────────────────────────┘   └─────────────────────────────┘
```

### The 3 Core Subsystems
1. **Core API (`backend/`, Port 8000)**:
   - **Framework**: FastAPI with async SQLAlchemy 2.0 and PostgreSQL 16 (via `asyncpg`).
   - **Artwork Validator**: Pillow-powered validation enforcing canonical dimensions, aspect ratios (`2:3` for Poster, `16:9` for Banner/Thumbnail), and strict 200 KB ceilings.
   - **Atomic Publisher**: Collapses multi-language episode variants (`content_group`) into unified catalogue items, deterministically sorts sections and episodes, and isolates Season 0 trailers.
   - **Security**: Strict Role-Based Access Control (`admin` vs `editor`) enforced at the route dependency layer.
2. **Internal CMS (`cms-ui/`, Port 3000)**:
   - **Dashboard**: Content authoring table with real-time search, section filters, pagination, and empty/loading states.
   - **Upload Slots**: 3 distinct artwork dropzones (Poster 2:3, Banner 16:9, Thumbnail 16:9) with live image previews and clear validation error banners.
   - **Pre-Flight Scanner**: Interactive validation report grouping blockers and warnings by show with explicit remediation guidance.
   - **RBAC Role Switcher**: Quick-toggle in the navigation bar to test `editor` vs `admin` permissions live.
3. **Viewer UI (`viewer-ui/`, Port 3001)**:
   - **Netflix-Style Home**: Dynamic Featured Hero banner, responsive horizontal scrolling carousels partitioned by section (`Featured`, `Series`, `Minisodes`, `Songs`).
   - **Show Detail Modal**: Full metadata display, Season 0 trailers isolated in a dedicated tab, and dual-language switcher (`[EN]` / `[HI]`) for grouped multi-language episodes.
   - **Search & Filters**: Instant search composed with category filter pills (`#adventure`, `#india`, `#animals`, etc.).

---

## 2. Quickstart & Operability (Docker Compose)

The entire ecosystem (PostgreSQL, Core API, CMS UI, and Viewer UI) starts with a single command:

```bash
# Clone the repository
git clone https://github.com/peblo/peblo-interns-task.git
cd peblo-interns-task

# Launch all 4 services in detached mode
docker compose up --build -d
```

### Service Map
| Service | URL | Description |
|---|---|---|
| **Core API** | [http://localhost:8000](http://localhost:8000) | FastAPI Swagger Docs: `/docs`, Health: `/health` |
| **Internal CMS** | [http://localhost:3000](http://localhost:3000) | Content editor & admin dashboard |
| **Viewer UI** | [http://localhost:3001](http://localhost:3001) | Netflix-style browse, search, and detail UI |
| **PostgreSQL** | `localhost:5432` | DB: `peblo_db`, User: `peblo_user`, Pass: `peblo_password` |

---

## 3. Live Verification & Automated Testing

### 1. Live Integration End-to-End Verification
To verify the complete operational lifecycle against the live running containers:

```bash
python backend/verify_live.py
```
This automated verification suite executes:
1. **Core API Health Check**: Verifies `/health` endpoint status.
2. **CMS UI & Viewer UI Check**: Confirms both Vite frontends are live and serving HTML.
3. **Static Asset Availability**: Tests image asset delivery across ports 8000, 3000, and 3001.
4. **RBAC Guard**: Proves `editor` role is rejected with `HTTP 403 Forbidden` on publish.
5. **Pre-Flight Validation Scanner**: Confirms scanner detects the deliberate seed data traps (3 blockers).
6. **Pre-Flight Publish Guard**: Proves `admin` publish is strictly rejected with `HTTP 400 Bad Request` while blockers exist.
7. **Automated Admin Remediation**: Uses CMS REST APIs to assign missing sections, resolve duplicate content groups, and upload valid artwork.
8. **Re-Scan Validation**: Proves scanner reports `can_publish: True` with 0 blockers.
9. **Atomic Publication**: Executes publication as `admin` (`HTTP 200 OK`) and verifies metadata.
10. **Viewer Feed (`GET /catalog`)**: Verifies published feed structure and section grouping.
11. **Composed Search (`GET /catalog/search`)**: Validates case-insensitive query matching combined with language and section filters.

### 2. Backend Unit Test Suite
To run standalone unit tests:

```bash
python backend/run_tests.py
# Or inside the backend container:
docker exec peblo_backend pytest
```
* **Coverage**: 10/10 passing unit tests testing Pillow image validation (ratios, dimensions, size ceilings), atomic filesystem swaps, seed JSON parsing and imperfection detection, RBAC route security, and composed search filter algorithms.

---

## 4. Time Spent Breakdown

| Task Area | Scope | Time Spent |
|---|---|---|
| **Part A: Backend & Data Modeling** | FastAPI setup, async SQLAlchemy models, Alembic migrations, Pillow image validator, atomic publisher service, composed search filter, RBAC dependency guards. | ~2.5 hours |
| **Part B: Internal CMS (React + TS)** | Show & episode management tables, artwork upload dropzones with canvas aspect ratio enforcement, pre-flight validation report view, publish pipeline logs. | ~2.0 hours |
| **Part C: Viewer UI (React + TS)** | Netflix-style hero banner, horizontal scrolling carousels, show detail modal with Season 0 trailer isolation, dual-language episode variant selector, search & category filtering. | ~1.5 hours |
| **Part D: Pipeline & Operability** | Docker Compose orchestration, health checks, GitHub Actions CI workflow, `.env.example`, verification test harness (`verify_live.py`). | ~1.0 hour |
| **Part E: Documentation & Written Analysis** | Architecture diagrams, atomic publishing analysis, Cloudflare R2 abstraction documentation, search scale breakdown, trade-off justifications. | ~1.0 hour |
| **Total** | | **~8.0 hours** |

---

## 5. Part E: Written Reasoning & Technical Decisions

### 1. How We Made Publishing Atomic & Crash Resilience
* **Mechanism**: When `POST /admin/catalog/publish` is triggered, the backend compiles the full catalogue JSON in memory. It writes the data to a temporary file (`.tmp_catalogue_<uuid>.json`) residing in the *exact same filesystem directory and mount* as the destination `catalogue.json`. It flushes and syncs OS buffers (`os.fsync`), then executes `os.replace(temp_path, target_path)`.
* **Crash Resilience**: `os.replace()` is an atomic system call guaranteed by the operating system kernel (POSIX `rename()` / Win32 `MoveFileExW`). If the server process crashes, runs out of memory, or loses power midway through publication:
  - The live `catalogue.json` remains completely intact and valid.
  - Active readers polling `GET /catalog` or CDN edge nodes never encounter a truncated, corrupt, or partially-written JSON payload.
  - The orphaned temporary file remains inert and is cleanly unlinked on subsequent runs.

### 2. Storage Abstraction (Local Disk ➔ Cloudflare R2)
* **Design Pattern**: All storage operations are abstracted behind the `BaseStorage` interface (`save_file`, `get_file`, `atomic_write_json`, `delete_file`, `get_url`).
* **Swapping to R2**: Transitioning to Cloudflare R2 in production requires **0 code modifications in business services**—simply set `STORAGE_BACKEND=r2` in environment variables.
* **R2 Implementation Details**: The `CloudflareR2Storage` class uses S3-compatible APIs (`boto3`/`aioboto3`):
  - Local file writes become asynchronous `s3_client.put_object(Bucket=..., Key=..., Body=...)` calls.
  - In object storage (Cloudflare R2 / AWS S3), individual `PUT` uploads are inherently atomic (the new object version only becomes readable once the upload stream completes).
  - Public URLs transparently resolve from local static paths (`/storage/uploads/...`) to the custom CDN domain prefix (`https://assets.peblo.tv/...`).

### 3. Search Implementation, Scaling Limits & Next Steps
* **Current Implementation**: `GET /catalog/search?q=&category=&language=&section=` performs in-memory composed filtering. The query parameter `q` matches across show title, show synopsis, episode title, and categories (case-insensitive substring match), while conjunctively (AND) enforcing `category`, `language`, and `section` filters.
* **Scaling Ceiling**: Linear scanning over in-memory JSON executes in under 5ms for catalogues up to ~10,000 episodes. Beyond 50,000+ items, this approach suffers from:
  - Increased CPU and memory overhead during linear iterations.
  - Lack of relevance scoring (TF-IDF / BM25), typo tolerance, and phonetic matching.
* **Next Steps for Scale**:
  1. **Dedicated Search Engine**: Integrate **Meilisearch** or **Algolia** via background publish webhook hooks.
  2. **Database Full-Text Search**: Implement PostgreSQL `tsvector` with `GIN` indexing across title, synopsis, and tags.
  3. **Pagination & Faceting**: Introduce cursor-based pagination and faceted aggregation counts.

### 4. Why Serve a Pre-Published Catalogue File? (Trade-offs)
* **Why We Serve a Pre-Published File**:
  1. **Massive Read Concurrency & Sub-Millisecond Latency**: Thousands of concurrent streaming children hit a static file cached at the Cloudflare CDN edge rather than flooding the PostgreSQL database with heavy multi-table SQL JOINs.
  2. **Pre-Computed Denormalization**: Language variant grouping (`content_group`), Season 0 trailer separation, deterministic sorting, and artwork resolution happen once during publish rather than on every single client request.
  3. **High Availability**: Even during database failover or maintenance windows, the Viewer UI continues serving content uninterrupted.
* **Where It Bites You (Trade-offs)**:
  - **Staleness**: Metadata updates made in the CMS do not immediately reflect on the Viewer UI until an admin triggers a publish run.
  - **Monolithic Payload Growth**: As the catalogue scales to tens of thousands of shows, a single JSON file grows large (mitigated by partitioning into per-section JSON chunks, e.g. `catalogue_featured.json`, or CDN range queries).

### 5. What We Left Out and Why
* **Full OAuth2 / OIDC Auth Provider**: Instead of introducing heavy third-party identity providers (Auth0/Keycloak), we implemented clean, header-based RBAC (`X-User-Role: admin` vs `editor`) that is genuinely enforced on all API routes and easily toggleable in the CMS UI navbar.
* **Video Transcoding Pipeline**: Focused entirely on metadata modeling, artwork validation, publish pipeline atomicity, and streaming UI delivery, leaving HLS/DASH segment encoding to dedicated background media workers.

### 6. AI Tool Usage & Human Judgment
* **AI Tool Utilization**: Antigravity AI was used to accelerate boilerplate generation (Pydantic schema definitions, Tailwind layout templates, and initial migration scaffolding).
* **Human Oversight & Verification**: Human architectural decisions and scrutiny were applied to:
  - Identify and handle the 4 deliberate seed data traps.
  - Enforce atomic file system replacement (`os.replace` + `fsync`) rather than direct file overwrites.
  - Separate Season 0 trailers into dedicated UI tabs while preserving multi-language `content_group` variant collapsing.

### 7. Production Alerting Strategy
* **Primary Alert**: High error rate or failure in `POST /admin/catalog/publish`.
* **Reasoning**: Publication is the critical bridge between content authoring and viewer availability. If the publish pipeline fails, new content releases are blocked, emergency metadata fixes cannot go live, and content teams are stalled. An automated alert triggered on any 5xx response from `/admin/catalog/publish` (via PagerDuty or Slack webhook) allows platform engineers to immediately inspect validation errors or storage connectivity before users experience stalled catalogue updates.

---

## 6. Seed Data Imperfection Traps Handled

The ingestion parser and validation scanner detect all deliberate seed data traps:
1. **Global Conflict (`ep_9001`)**: Duplicate `(content_group='motis-many-lives-s01e02', language='hi')` colliding with `ep_0004`.
2. **Missing Section (`Rhyme Rangers`)**: Show has `section: null`.
3. **Missing Artwork (`ep_0036`)**: Episode has `artwork_available: []` (0 artworks).
4. **Season 0 Isolation (`ep_0093`, `ep_0094`)**: Trailer episodes separated from standard season browsing.

---

## 7. Role-Based Access Control (RBAC) Matrix

| Endpoint | Method | `editor` Role | `admin` Role | Description |
|---|---|---|---|---|
| `/admin/shows` | `GET`, `POST`, `PATCH` | Allowed | Allowed | Manage show metadata |
| `/admin/shows/{id}` | `DELETE` | **403 Forbidden** | **Allowed** | Delete show record |
| `/admin/episodes` | `GET`, `POST`, `PATCH`, `DELETE` | Allowed | Allowed | Manage episode records |
| `/admin/episodes/{id}/artwork/{type}` | `POST` | Allowed | Allowed | Upload validated artwork |
| `/admin/validation-report` | `GET` | Allowed | Allowed | Inspect publish blockers |
| `/admin/catalog/publish` | `POST` | **403 Forbidden** | **Allowed** | Trigger atomic publication |
| `/admin/publish-runs` | `GET` | Allowed | Allowed | View publication logs |
| `/catalog` | `GET` | Public | Public | Published catalogue feed |
| `/catalog/search` | `GET` | Public | Public | Composed search & filter |

---

## 8. API Endpoint Documentation

### Core API (`http://localhost:8000`)

* **Health**: `GET /health` — Returns status of API, database connectivity, and storage volume.
* **Viewer Catalogue**: `GET /catalog` — Returns the latest published catalogue grouped by section.
* **Composed Search**: `GET /catalog/search?q={query}&category={cat}&language={lang}&section={sec}` — Full search across shows, episodes, and tags.
* **Validation Report**: `GET /admin/validation-report` (Header `X-User-Role: editor|admin`) — Scans all shows for blockers.
* **Atomic Publish**: `POST /admin/catalog/publish` (Header `X-User-Role: admin`) — Compiles, validates, and atomically writes `catalogue.json`.
* **Artwork Upload**: `POST /admin/episodes/{episode_id}/artwork/{poster|banner|thumbnail}` — Uploads and validates image file (dimensions, ratio, <=200KB).
* **Shows CRUD**: `GET`, `POST`, `PATCH`, `DELETE` on `/admin/shows`.
* **Episodes CRUD**: `GET`, `POST`, `PATCH`, `DELETE` on `/admin/episodes`.

---

## 9. Submission Checklist & Verification

- [x] Three artwork sizes validated with Pillow (ratios, dimensions, 200KB ceiling).
- [x] Cloudflare R2 storage abstraction implemented.
- [x] Multi-language `content_group` variants collapsed into unified entries.
- [x] Season 0 trailers isolated from normal seasons.
- [x] Pre-flight validation report surfaces all deliberate seed traps.
- [x] Atomic file replacement via temporary file swap and OS sync.
- [x] RBAC enforced (`editor` vs `admin`).
- [x] Netflix-style Viewer UI with hero banner, section rows, and language switcher.
- [x] Composed search endpoint functioning across title, episode, category, and language.
- [x] Docker Compose brings up all 4 services with a single command.
- [x] CI pipeline configured with linting, testing, and container build steps.
- [x] Written trade-off reasoning covering all Part E questions.
