#!/usr/bin/env bash
#
# Build and deploy the todo apps to Google Cloud Run.
#
#   SAFE BY DEFAULT: without --yes this script only PRINTS the commands it would run. Nothing is created,
#   built or deployed until you add --yes.
#
# Usage:
#   deploy/gcp/deploy.sh [deploy|teardown] <openspec|speckit|hve|all> [options]
#
# Options:
#   --project ID       Google Cloud project id            (or env PROJECT_ID)
#   --region NAME      Cloud Run region, default us-central1 (or env REGION)
#   --repo NAME        Artifact Registry repository, default todo-apps
#   --tag TAG          Image tag, default the git short commit, else a timestamp
#   --groq-model NAME  Groq model for the assistant, default openai/gpt-oss-20b
#   --skip-ai          Deploy without a Groq key (the assistant says "not configured"; the todo app works)
#   --public           Let anyone on the internet open the app (default: private, sign-in required)
#   --yes              Actually run the commands (otherwise: print only)
#   -h, --help         Show this help
#
# The Groq key is read from the GROQ_API_KEY environment variable of your shell, or asked for with a hidden
# prompt. It is stored in Secret Manager and is never put in an image, a file, a log or a command line.

set -euo pipefail

# ---------------------------------------------------------------- settings
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

ACTION="deploy"
TARGET=""
PROJECT_ID="${PROJECT_ID:-}"
REGION="${REGION:-us-central1}"
AR_REPO="todo-apps"
TAG=""
GROQ_MODEL="openai/gpt-oss-20b"
SKIP_AI=0
PUBLIC=0
EXECUTE=0

SECRET_NAME="groq-api-key"
RUNTIME_SA_NAME="todo-app-run"

# ---------------------------------------------------------------- helpers
say()  { printf '\n== %s\n' "$*"; }
note() { printf '   %s\n' "$*"; }
die()  { printf 'ERROR: %s\n' "$*" >&2; exit 1; }

usage() { sed -n '2,23p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'; }

# Print a command; run it only with --yes.
run() {
  printf '+'; printf ' %q' "$@"; printf '\n'
  if [ "$EXECUTE" = 1 ]; then "$@"; fi
}

app_dir()   { case "$1" in openspec) echo todo-openspec ;; speckit) echo todo-speckit ;; hve) echo todo-hve ;; *) die "unknown app '$1'" ;; esac; }
app_title() { case "$1" in openspec) echo "Todo App (OpenSpec build)" ;; speckit) echo "Todo App (Spec Kit build)" ;; hve) echo "Todo App (HVE build)" ;; esac; }
service()   { echo "todo-$1"; }

# ---------------------------------------------------------------- arguments
while [ $# -gt 0 ]; do
  case "$1" in
    deploy|teardown)            ACTION="$1" ;;
    openspec|speckit|hve|all)   TARGET="$1" ;;
    --project)    [ $# -ge 2 ] || die "--project needs a value"; PROJECT_ID="$2"; shift ;;
    --region)     [ $# -ge 2 ] || die "--region needs a value"; REGION="$2"; shift ;;
    --repo)       [ $# -ge 2 ] || die "--repo needs a value"; AR_REPO="$2"; shift ;;
    --tag)        [ $# -ge 2 ] || die "--tag needs a value"; TAG="$2"; shift ;;
    --groq-model) [ $# -ge 2 ] || die "--groq-model needs a value"; GROQ_MODEL="$2"; shift ;;
    --skip-ai)    SKIP_AI=1 ;;
    --public)     PUBLIC=1 ;;
    --yes)        EXECUTE=1 ;;
    -h|--help)    usage; exit 0 ;;
    *)            die "unknown argument '$1' (try --help)" ;;
  esac
  shift
done

[ -n "$TARGET" ] || { usage; die "say which app: openspec, speckit, hve or all"; }
if [ "$TARGET" = all ]; then APPS="openspec speckit hve"; else APPS="$TARGET"; fi

# ---------------------------------------------------------------- checks
if [ "$EXECUTE" = 1 ]; then
  command -v gcloud >/dev/null 2>&1 || die "gcloud is not installed (https://cloud.google.com/sdk/docs/install)"
  [ -n "$PROJECT_ID" ] || PROJECT_ID="$(gcloud config get-value project 2>/dev/null || true)"
  [ -n "$PROJECT_ID" ] || die "no project: pass --project ID or set PROJECT_ID"
  [ -n "$(gcloud auth list --filter=status:ACTIVE --format='value(account)' 2>/dev/null)" ] \
    || die "not signed in: run 'gcloud auth login' first"
else
  [ -n "$PROJECT_ID" ] || PROJECT_ID="YOUR_PROJECT_ID"
fi

if [ -z "$TAG" ]; then
  TAG="$(git -C "$REPO_ROOT" rev-parse --short HEAD 2>/dev/null || date +%Y%m%d%H%M%S)"
fi

REGISTRY="${REGION}-docker.pkg.dev/${PROJECT_ID}/${AR_REPO}"
RUNTIME_SA="${RUNTIME_SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"

say "Plan"
note "action:   $ACTION"
note "apps:     $APPS"
note "project:  $PROJECT_ID    region: $REGION"
note "registry: $REGISTRY    tag: $TAG"
if [ "$EXECUTE" = 1 ]; then
  note "mode:     EXECUTE (--yes given): commands below WILL run"
else
  note "mode:     DRY RUN: only printing. Add --yes to run for real."
fi
if [ "$PUBLIC" = 1 ] && [ "$ACTION" = deploy ]; then
  note "WARNING:  --public means anyone on the internet can open the app and use your Groq quota."
fi

# ---------------------------------------------------------------- teardown
if [ "$ACTION" = teardown ]; then
  for app in $APPS; do
    say "Delete Cloud Run service $(service "$app")"
    run gcloud run services delete "$(service "$app")" --region "$REGION" --project "$PROJECT_ID" --quiet
  done
  say "Left in place on purpose (delete by hand if you want them gone)"
  note "images:  gcloud artifacts repositories delete $AR_REPO --location $REGION --project $PROJECT_ID"
  note "secret:  gcloud secrets delete $SECRET_NAME --project $PROJECT_ID"
  note "account: gcloud iam service-accounts delete $RUNTIME_SA --project $PROJECT_ID"
  exit 0
fi

# ---------------------------------------------------------------- one-time setup
say "1. Turn on the Google Cloud services this needs"
run gcloud services enable run.googleapis.com artifactregistry.googleapis.com cloudbuild.googleapis.com \
  secretmanager.googleapis.com iam.googleapis.com --project "$PROJECT_ID"

say "2. Create the image repository (Artifact Registry) if it is missing"
if [ "$EXECUTE" = 1 ]; then
  gcloud artifacts repositories describe "$AR_REPO" --location "$REGION" --project "$PROJECT_ID" >/dev/null 2>&1 \
    || gcloud artifacts repositories create "$AR_REPO" --repository-format=docker --location "$REGION" \
         --description "Todo app images" --project "$PROJECT_ID"
else
  note "+ (create Artifact Registry repository '$AR_REPO' in $REGION if it does not exist)"
fi

say "3. Create a low-privilege identity for the running apps if it is missing"
if [ "$EXECUTE" = 1 ]; then
  gcloud iam service-accounts describe "$RUNTIME_SA" --project "$PROJECT_ID" >/dev/null 2>&1 \
    || gcloud iam service-accounts create "$RUNTIME_SA_NAME" --display-name "Todo apps runtime" --project "$PROJECT_ID"
else
  note "+ (create service account $RUNTIME_SA if it does not exist)"
fi

say "4. Store the Groq key in Secret Manager"
if [ "$SKIP_AI" = 1 ]; then
  note "--skip-ai: no key is stored; the assistant will answer 'not configured' (the todo features still work)."
elif [ "$EXECUTE" = 1 ]; then
  gcloud secrets describe "$SECRET_NAME" --project "$PROJECT_ID" >/dev/null 2>&1 \
    || gcloud secrets create "$SECRET_NAME" --replication-policy automatic --project "$PROJECT_ID"
  if [ -n "${GROQ_API_KEY:-}" ]; then
    printf '%s' "$GROQ_API_KEY" | gcloud secrets versions add "$SECRET_NAME" --data-file=- --project "$PROJECT_ID"
  elif [ -z "$(gcloud secrets versions list "$SECRET_NAME" --limit 1 --format='value(name)' --project "$PROJECT_ID")" ]; then
    printf 'Paste your Groq API key (it will not be shown): '
    IFS= read -rs KEY_INPUT; printf '\n'
    [ -n "$KEY_INPUT" ] || die "no key entered (or use --skip-ai)"
    printf '%s' "$KEY_INPUT" | gcloud secrets versions add "$SECRET_NAME" --data-file=- --project "$PROJECT_ID"
    unset KEY_INPUT
  else
    note "the secret already has a version; leaving it as it is (set GROQ_API_KEY in your shell to replace it)"
  fi
  gcloud secrets add-iam-policy-binding "$SECRET_NAME" --member "serviceAccount:${RUNTIME_SA}" \
    --role roles/secretmanager.secretAccessor --project "$PROJECT_ID" >/dev/null
else
  note "+ (create secret '$SECRET_NAME' if missing)"
  note "+ (add a version from your shell's GROQ_API_KEY, or from a hidden prompt; the key never appears on a command line)"
  note "+ (let $RUNTIME_SA read only that secret)"
fi

# ---------------------------------------------------------------- build and deploy each app
for app in $APPS; do
  dir="$REPO_ROOT/$(app_dir "$app")"
  svc="$(service "$app")"
  image="${REGISTRY}/${svc}:${TAG}"
  [ -f "$dir/Dockerfile" ] || die "missing $dir/Dockerfile"

  say "5. Build the image for $app (Cloud Build)"
  run gcloud builds submit "$dir" --tag "$image" --project "$PROJECT_ID"

  say "6. Deploy $svc to Cloud Run"
  args="run deploy $svc --image $image --region $REGION --project $PROJECT_ID --platform managed"
  args="$args --service-account $RUNTIME_SA --port 8080 --cpu 1 --memory 512Mi"
  args="$args --min-instances 0 --max-instances 1 --concurrency 20 --timeout 60"
  args="$args --set-env-vars TODO_DB_PATH=/tmp/todos.db,GROQ_MODEL=$GROQ_MODEL,GROQ_TIMEOUT_SECONDS=15"
  if [ "$SKIP_AI" = 0 ]; then args="$args --set-secrets GROQ_API_KEY=${SECRET_NAME}:latest"; fi
  if [ "$PUBLIC" = 1 ]; then args="$args --allow-unauthenticated"; else args="$args --no-allow-unauthenticated"; fi
  # shellcheck disable=SC2086  # the words are plain flags with no spaces inside them
  run gcloud $args

  say "7. Check that the right app is answering"
  if [ "$EXECUTE" = 1 ]; then
    url="$(gcloud run services describe "$svc" --region "$REGION" --project "$PROJECT_ID" --format 'value(status.url)')"
    token="$(gcloud auth print-identity-token)"
    expected="$(app_title "$app")"
    found="$(curl -fsS -H "Authorization: Bearer $token" "$url/openapi.json" \
      | python3 -c 'import json,sys; print(json.load(sys.stdin)["info"]["title"])')"
    [ "$found" = "$expected" ] || die "$svc answered with '$found', expected '$expected'"
    curl -fsS -o /dev/null -H "Authorization: Bearer $token" "$url/todos" || die "$svc: GET /todos failed"
    note "OK: $svc is serving '$found' at $url"
  else
    note "+ (get the service URL, call /openapi.json and confirm the title is '$(app_title "$app")', then GET /todos)"
  fi
done

say "Done"
if [ "$EXECUTE" = 1 ]; then
  if [ "$PUBLIC" = 0 ]; then
    note "The apps are private. To open one in your browser through your own login:"
    note "  gcloud run services proxy <service-name> --region $REGION --project $PROJECT_ID --port 8081"
  fi
else
  note "Nothing was created. Review the commands above, then run again with --yes."
fi
note "Remember: todos are stored on the instance's temporary disk and are lost when it restarts (see deploy/gcp/README.md)."
