# Antigravity IDE Database Manager Skill

This repository contains a custom AI agent skill and management tool for the Google Antigravity IDE's internal SQLite database, workspace storage, and conversation history.

## What is this?

This project exposes database administration, analysis, and recovery tools directly to AI developer agents in the Antigravity IDE. It allows agents (and users) to run diagnostics, recover missing chat history sidebars, repair database corruption, migrate workspace path bindings, and automatically rename conversation titles.

## Upstream Project and Modifications

The code in the `scripts` directory is a modified clone of the open-source project:
https://github.com/ag-donald/Antigravity-Database-Manager

### Added Features and Extensions:
- **AI Agent Skill Integration**: Packaged with a `SKILL.md` definition at the root, making it fully compatible and auto-loadable by AI agents in the Antigravity IDE.
- **AI-Powered Auto-Renamer (auto_rename.py)**: A script that parses conversation logs, extracts initial user requests, and uses the Gemini API to automatically rename conversation titles in both task.md and the SQLite database.
- **Improved Root Git Configuration**: Added root-level .gitignore and ignore rules to prevent committing development keys or SQLite state caches.
- **Dynamic Path Resolution**: Removed all hardcoded absolute user paths (`C:\Users\dyzulk\...`) from scripts and metadata, replacing them with dynamic, cross-platform path resolution based on standard environment locations (`~` / `%USERPROFILE%`) and script locations.

## Antigravity 2.0 Support

This manager fully supports Antigravity 2.0+, which separates the standalone **Antigravity Agent** command center from the integrated **Antigravity IDE** editor environment. 

### Data Paths Probed:
- **SQLite Database (state.vscdb)**: Probes `%APPDATA%\Antigravity IDE` (new 2.0+ default) first, and falls back to `%APPDATA%\Antigravity` (legacy/standalone).
- **Gemini Base Directory**: Probes `~/.gemini/antigravity-ide` (new 2.0+ default) first, and falls back to `~/.gemini/antigravity` (legacy/standalone).

### Environment Overrides:
You can manually force the database manager to target a specific database or directory structure by setting the following environment variables before launching the tool:
- `AGMERCIUM_DB_PATH`: The absolute file path to the target `state.vscdb` database.
- `AGMERCIUM_GEMINI_BASE`: The absolute path to the Gemini home directory (containing `brain` and `conversations` subdirectories).

Example (PowerShell):
```powershell
$env:AGMERCIUM_DB_PATH="C:\custom\path\to\state.vscdb"
$env:AGMERCIUM_GEMINI_BASE="C:\custom\path\to\.gemini\antigravity"
python scripts/__main__.py scan
```

## Directory Structure

- `SKILL.md` - The entry point definition that registers this project as a reusable skill for AI agents in the Antigravity IDE.
- `.gitignore` - Root-level ignore rules for Python environment, caching, and local database storage.
- `scripts/` - The core application codebase (cloned from upstream with custom features added).
  - `scripts/config/settings.json.example` - Example configuration file for credentials/API keys.
  - `scripts/auto_rename.py` - Custom script for AI-powered conversation renaming.
  - `scripts/delayed_recover.py` - Reusable background daemon script to execute recovery after the IDE has closed.
  - `scripts/__main__.py` - Core CLI/TUI entrypoint for database scan, recovery, diagnostics, repair, merge, and workspace utilities.

## How to Use

### As an AI Agent Skill
Since this repository has a `SKILL.md` at the root and is placed in the Antigravity skills directory, it is automatically discovered by the IDE's agent runner. Developer agents can call it directly to run database scans, diagnostics, and recovery pipelines when asked.

### Running Manually
For manual execution of the CLI or the interactive Terminal User Interface (TUI):

```bash
# Enter the scripts directory
cd scripts

# Run the interactive TUI
python __main__.py

# Run the headless interactive menu
python __main__.py --headless

# Run the AI conversation auto-renamer (requires Gemini API Key configured in config/settings.json)
python auto_rename.py

# Run delayed recovery (pass the target workspace path if you wish to run a workspace migration as well)
python delayed_recover.py [target_workspace_path]
```

Refer to the documentation in the `scripts` directory or the `SKILL.md` at the root for a complete list of commands, safety features, and recovery options.
