#!/usr/bin/env bash

curl -LsSf https://astral.sh/uv/install.sh | sh
source $HOME/.local/bin/env
make install
if command -v npm >/dev/null 2>&1; then
  npm ci && npm run build:css
else
  echo "npm not found, skipping Tailwind CSS build"
fi
psql -a -d $DATABASE_URL -f database.sql