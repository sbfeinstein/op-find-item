#!/usr/bin/env sh
# Typically the documentation site is build and deployed automatically via GitHub Actions.
# This script provides an alternative in case it is necessary to force a deploy directly to the gh-pages branch.

# Abort on errors
set -e

# Build

echo "Building"
uv run --group docs zensical build --clean
cd site

# Create .nojekyll to bypass Jekyll processing
touch .nojekyll

echo "Initializing git"
git init
git add -A
git commit -m 'Deploy'

# Deploy to gh-pages branch
echo "Deploying via git push"
git push -f git@github.com:sbfeinstein/op-find-item.git main:gh-pages
cd ..
