# Deploying the todo apps to Google Cloud (Cloud Run)

`deploy.sh` builds and deploys any of the three apps (`openspec`, `speckit`, `hve`) to **Google Cloud Run**.

> **It never deploys by accident.** Without `--yes` the script only *prints* the commands it would run.

## What is Cloud Run, in one minute

Cloud Run runs a **container** (your app packed into a box with everything it needs) and gives it a web address.
You do not manage any server. When nobody uses the app it scales down to zero, so you pay almost nothing.

```text
your code ──► Cloud Build ──► image in Artifact Registry ──► Cloud Run service (https address)
                                                                   ▲
                                          Groq key from Secret Manager (never inside the image)
```

## What you need first (one time)

1. A Google Cloud **project with billing turned on**.
2. The `gcloud` command-line tool: <https://cloud.google.com/sdk/docs/install>
3. Sign in: `gcloud auth login`
4. Permission to create things in that project. On your own project, the **Owner** role is enough. In a company
   project ask for: Cloud Run Admin, Cloud Build Editor, Artifact Registry Admin, Secret Manager Admin,
   Service Account Admin, Service Usage Admin and Service Account User.

## How to use it

Run from the project folder (`Todo App/`). Replace `my-project` with your project id.

```bash
# 1. LOOK FIRST: print the plan, change nothing (this is the default)
deploy/gcp/deploy.sh all --project my-project

# 2. Deploy one app for real
export GROQ_API_KEY=...            # your key, only in your own shell (or leave it out and type it when asked)
deploy/gcp/deploy.sh hve --project my-project --yes

# 3. Deploy all three
deploy/gcp/deploy.sh all --project my-project --yes

# Without the AI assistant (no key needed; the todo features still work)
deploy/gcp/deploy.sh hve --project my-project --skip-ai --yes

# Remove the services again (images, secret and service account are left; the script prints how to delete them)
deploy/gcp/deploy.sh teardown all --project my-project --yes
```

Options: `--region` (default `us-central1`), `--repo`, `--tag`, `--groq-model`, `--public`, `--skip-ai`, `--yes`, `--help`.
You can also set `PROJECT_ID` and `REGION` as environment variables.

## What the script does, step by step

| Step | What happens |
|---|---|
| 1 | Turns on the Google Cloud services it needs (Cloud Run, Cloud Build, Artifact Registry, Secret Manager, IAM) |
| 2 | Creates an image repository called `todo-apps` if it is missing |
| 3 | Creates a low-privilege identity `todo-app-run` that the running apps use |
| 4 | Stores your Groq key in **Secret Manager** and lets only that identity read it |
| 5 | Builds each app's image with Cloud Build, using the `Dockerfile` in the app folder |
| 6 | Deploys each app as its own Cloud Run service: `todo-openspec`, `todo-speckit`, `todo-hve` |
| 7 | Checks that the right app answers: it reads `/openapi.json`, compares the app title, and calls `/todos` |

## The files it uses

- `todo-*/Dockerfile`: builds the image (Python 3.12, runtime packages only, runs as a normal user, listens on `$PORT`)
- `todo-*/.dockerignore` and `todo-*/.gcloudignore`: **allow-lists** that send only `requirements.txt`, `app/` and
  `static/`. Your `.env`, tests, docs and databases are never uploaded or put in an image.
- `deploy/gcp/deploy.sh`: this script

## Safety choices (and why)

- **Private by default.** The apps have no login of their own, so a public address would let anyone use your Groq quota.
  They are deployed with `--no-allow-unauthenticated`; only people with IAM permission can open them. Add `--public`
  only if you really want that (the script prints a warning).
- **The Groq key lives only in Secret Manager.** It is passed through a pipe, never typed on a command line, never written
  to a file, and never inside an image or this repository.
- **Least privilege.** The running apps use their own identity, which can read only the one secret.
- **One instance at most** (`--max-instances 1`), because the apps keep data in a single SQLite file.

## How to open a private app

```bash
gcloud run services proxy todo-hve --region us-central1 --project my-project --port 8081
# then open http://localhost:8081
```

## Important limits (read this)

1. **Your todos are not permanent on Cloud Run.** The apps store todos in a SQLite file on the instance's temporary
   disk (`/tmp/todos.db`). When the instance restarts or scales to zero, **the todos are lost**. This is fine for a demo.
   For real use, move the data to a database (for example Cloud SQL for PostgreSQL), or run the app on a Compute Engine
   VM with a persistent disk. That needs code changes and is not part of this script.
2. **The AI assistant needs internet access to Groq**, which Cloud Run allows by default.
3. **Costs.** Cloud Run scales to zero, and light use should fit within Google's free tiers, but Cloud Build, Artifact
   Registry and Secret Manager can add small charges. Check current pricing and set a billing alert.

## What was and was not tested

Tested on the development machine (no Google Cloud account used, nothing deployed):

- `bash -n` syntax check (macOS bash 3.2), and dry runs of every mode (`deploy`, `teardown`, `--public`, `--skip-ai`,
  environment variables, bad arguments). `--yes` refuses to run when `gcloud` is missing.
- The upload allow-lists (`.gcloudignore`) tested with git's ignore rules: only the 5 intended items are uploaded, with
  `.env` present locally and not uploaded.
- A replica of the container (same filtered requirements, only `app/` and `static/`, no `.env`, `PORT` set): each app
  starts, shows its own title, creates and lists a todo, serves the page, and answers "not configured" with no key.

**Not tested:** the real `docker build` (Docker was not running), `shellcheck`, and every `gcloud` command against a real
project. Expect to fix small things on the first real run, for example a missing permission on Cloud Build's service
account (grant it `roles/artifactregistry.writer`) or a service that needs a few more seconds to become ready.
