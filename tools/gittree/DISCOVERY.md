# gittree — Git Repository Tree Manager

## Problem Statement
Managing multiple git repositories scattered across a server filesystem is tedious. You must manually `cd` into each directory, run `git status`, check for uncommitted changes, and `git pull` individually. There's no single command that gives you a bird's-eye view of all git repos in a directory tree.

## Who Has This Problem
- Developers maintaining multiple projects on one server
- DevOps engineers managing deployment repos
- Anyone using the daily-app-builder workflow (multiple repos per day)
- Server operators with scattered git clones

## Why Existing Solutions Are Not Enough
- **myrepos/mr**: Perl-based, not commonly pre-installed, complex configuration
- **gh CLI**: GitHub-only, doesn't scan local repos
- **git loop scripts**: Ad-hoc, not reusable, no consistent output format
- **Manual**: Tedious and error-prone (forgetting to pull/push)

## Why This Matters Today
This server has 8+ git repos (daily-app projects, hermes, homepage, n8n, etc.). Running `gittree status` from `/root` would instantly show the state of all of them. This saves time and prevents deployment errors.
