---
name: antigravity-database-manager
description: Manage, analyze, and recover the internal SQLite databases, workspace storage, and conversation history of the Google Antigravity IDE.
---

# Antigravity IDE Database Manager Skill

This skill provides a comprehensive database administration, analysis, and recovery suite for the Google Antigravity IDE, based on the Agmercium Antigravity IDE Database Manager. It allows developer agents and users to perform diagnostics, recover disappeared history sidebars, repair corruptions, migrate workspace bindings, and auto-rename titles dynamically.

---

## Technical Context
The Antigravity IDE stores session metadata and conversation history across three parallel components:
1. Raw Session Data: Saved as binary Protocol Buffer (.pb) files in:
   - Antigravity IDE 2.0+ (Default): `~/.gemini/antigravity-ide/conversations/`
   - Antigravity Agent 2.0+ (Standalone): `~/.gemini/antigravity/conversations/`
2. UI Sidebar Index: Stored in the SQLite database `state.vscdb` under the key `antigravityUnifiedStateSync.trajectorySummaries` in the `ItemTable` table as a Base64-encoded Protobuf index, and as JSON under the key `chat.ChatSessionStore.index`.
   - Windows (2.0+ IDE): `%APPDATA%\Antigravity IDE\User\globalStorage\state.vscdb`
   - macOS (2.0+ IDE): `~/Library/Application Support/Antigravity IDE/User/globalStorage/state.vscdb`
   - Linux (2.0+ IDE): `~/.config/Antigravity IDE/User/globalStorage/state.vscdb`
   - Legacy/Standalone App: The folders are named `Antigravity` instead of `Antigravity IDE`.
3. Configuration and Binding: Managed inside the sibling `storage.json` file.

Unclean shutdowns, IDE upgrades, or workspace path changes frequently cause the internal SQLite index to lose its mappings while raw files remain intact on disk. This skill contains the modules required to scan, recover, repair, and manage all three layers.

### Antigravity 2.0 Agent vs IDE Separation
Antigravity 2.0 separates the standalone agent command center (`antigravity`) from the integrated editor environment (`antigravity-ide`). This database manager supports both environments by:
- Automatically probing both folders and using appropriate fallbacks.
- Allowing manual path overrides via environment variables:
  - `AGMERCIUM_DB_PATH`: Override path to state.vscdb.
  - `AGMERCIUM_GEMINI_BASE`: Override base Gemini data directory containing brain/conversations.

---

## Skill Modules

All modules are executable via PowerShell/Command Prompt. Replace `$env:USERPROFILE` with your home directory path (or `~` on macOS/Linux).

### Module 1: Database Overview (scan)
This module scans the active database and all available backups in the global directory, generating a comparison table detailing sizes, number of conversations, titled entries, bound workspaces, and index counts.

Command:
```powershell
$env:PYTHONIOENCODING="utf-8"; python "$env:USERPROFILE\.gemini\config\skills\antigravity-database-manager\scripts\__main__.py" scan
```

---

### Module 2: Full-Pipeline History Recovery (recover)
This module automates the complete 6-phase recovery process to restore disappeared conversations back into the IDE sidebar. It performs safety backups, scans the conversations folder, extracts titles, synthesizes Protobuf entries, synchronizes the JSON index, and outputs recovery statistics.

Command:
```powershell
$env:PYTHONIOENCODING="utf-8"; python "$env:USERPROFILE\.gemini\config\skills\antigravity-database-manager\scripts\__main__.py" recover
```

---

### Module 3: Database Health Check (health)
This module runs a comprehensive health check on the active database. It evaluates sync status, active titled counts, bound workspace counts, and structural drift (detecting when files on disk lack indices inside the database, or when indices inside the database lack files on disk).

Command:
```powershell
$env:PYTHONIOENCODING="utf-8"; python "$env:USERPROFILE\.gemini\config\skills\antigravity-database-manager\scripts\__main__.py" health
```

---

### Module 4: Corruption Diagnostics (diagnose)
This module scans the database at a byte level to detect known structural corruptions, including ghost bytes (U+FFFD), double-wrapping of JSON payloads, UUID casing mismatches, invalid wire types, and field ordering violations.

Command:
```powershell
$env:PYTHONIOENCODING="utf-8"; python "$env:USERPROFILE\.gemini\config\skills\antigravity-database-manager\scripts\__main__.py" diagnose
```

---

### Module 5: Autonomous Repair Engine (repair)
This module autonomously repairs all database corruptions identified by the diagnostic module. It secures a backup first and then cleans up ghost bytes, un-wraps double-encoded JSON payloads, and corrects field structure anomalies safely.

Command:
```powershell
$env:PYTHONIOENCODING="utf-8"; python "$env:USERPROFILE\.gemini\config\skills\antigravity-database-manager\scripts\__main__.py" repair
```

---

### Module 6: Database Merging (merge)
This module merges conversation entries from a source database into the current database.
*   **Additive Strategy:** Merges missing conversations while preserving existing target entries.
*   **Overwrite Strategy:** Overwrites existing target entries with identical UUIDs from the source.
*   **Cherry-Picking:** Allows targeted merging of specific conversations by specifying UUIDs.

Commands:
*   **Additive merge:**
    ```powershell
    $env:PYTHONIOENCODING="utf-8"; python "$env:USERPROFILE\.gemini\config\skills\antigravity-database-manager\scripts\__main__.py" merge --source <SOURCE_VSCDB_PATH>
    ```
*   **Overwrite merge:**
    ```powershell
    $env:PYTHONIOENCODING="utf-8"; python "$env:USERPROFILE\.gemini\config\skills\antigravity-database-manager\scripts\__main__.py" merge --source <SOURCE_VSCDB_PATH> --strategy overwrite
    ```
*   **Cherry-pick specific UUIDs:**
    ```powershell
    $env:PYTHONIOENCODING="utf-8"; python "$env:USERPROFILE\.gemini\config\skills\antigravity-database-manager\scripts\__main__.py" merge --source <SOURCE_VSCDB_PATH> --cherry-pick "uuid1,uuid2"
    ```

---

### Module 7: Backup Management (backup)
This module manages the lifecycle of database backups. It lists backups, creates timestamped copies, and restores a specific backup cleanly to revert database states.

Commands:
*   **List all backups:**
    ```powershell
    $env:PYTHONIOENCODING="utf-8"; python "$env:USERPROFILE\.gemini\config\skills\antigravity-database-manager\scripts\__main__.py" backup list
    ```
*   **Create a manual backup:**
    ```powershell
    $env:PYTHONIOENCODING="utf-8"; python "$env:USERPROFILE\.gemini\config\skills\antigravity-database-manager\scripts\__main__.py" backup create
    ```
*   **Restore a backup by index:**
    ```powershell
    $env:PYTHONIOENCODING="utf-8"; python "$env:USERPROFILE\.gemini\config\skills\antigravity-database-manager\scripts\__main__.py" backup restore <INDEX>
    ```

---

### Module 8: Empty Database Creation (create)
This module creates a new, empty state.vscdb database file with the correct schema and standard tables, ready to be indexed by the Antigravity IDE.

Command:
```powershell
$env:PYTHONIOENCODING="utf-8"; python "$env:USERPROFILE\.gemini\config\skills\antigravity-database-manager\scripts\__main__.py" create --output <OUTPUT_PATH>
```

---

### Module 9: Individual Conversation Management (conversations)
This module manages individual conversation entries inside the database index.
*   **list:** Lists all conversation entries in the active database.
*   **show:** Outputs the raw JSON session payload structure of a specific conversation UUID.
*   **delete:** Removes a conversation entry from the active database index.
*   **rename:** Renames the title of a specific conversation UUID.

Commands:
*   **List all conversation index entries:**
    ```powershell
    $env:PYTHONIOENCODING="utf-8"; python "$env:USERPROFILE\.gemini\config\skills\antigravity-database-manager\scripts\__main__.py" conversations list
    ```
*   **Show raw JSON payload of a UUID:**
    ```powershell
    $env:PYTHONIOENCODING="utf-8"; python "$env:USERPROFILE\.gemini\config\skills\antigravity-database-manager\scripts\__main__.py" conversations show <UUID>
    ```
*   **Delete a conversation entry by UUID:**
    ```powershell
    $env:PYTHONIOENCODING="utf-8"; python "$env:USERPROFILE\.gemini\config\skills\antigravity-database-manager\scripts\__main__.py" conversations delete <UUID> --force
    ```
*   **Rename a conversation title by UUID:**
    ```powershell
    $env:PYTHONIOENCODING="utf-8"; python "$env:USERPROFILE\.gemini\config\skills\antigravity-database-manager\scripts\__main__.py" conversations rename <UUID> "<NEW_TITLE>"
    ```

---

### Module 10: Workspace Path Diagnostics and Migrations (workspace)
This module manages workspace pathways bound to conversation entries in the database. It is critical when project directories are renamed, moved, or when drive letters undergo case shifts.
*   **list:** Lists all unique bound workspace URIs.
*   **check:** Verifies the physical existence and access permissions of all bound paths.
*   **migrate:** Rebinds all conversation entries inside the database to a new absolute workspace path.

Commands:
*   **List bound workspace paths:**
    ```powershell
    $env:PYTHONIOENCODING="utf-8"; python "$env:USERPROFILE\.gemini\config\skills\antigravity-database-manager\scripts\__main__.py" workspace list
    ```
*   **Run path checks:**
    ```powershell
    $env:PYTHONIOENCODING="utf-8"; python "$env:USERPROFILE\.gemini\config\skills\antigravity-database-manager\scripts\__main__.py" workspace check
    ```
*   **Migrate conversation bindings to a new workspace path:**
    ```powershell
    $env:PYTHONIOENCODING="utf-8"; python "$env:USERPROFILE\.gemini\config\skills\antigravity-database-manager\scripts\__main__.py" workspace migrate <NEW_ABSOLUTE_PATH>
    ```

---

### Module 11: Configuration Storage Management (storage)
This module inspects and patches the configuration storage settings inside storage.json, which is crucial for managing active workspace layout preferences and remote setups.
*   **inspect:** Lists all key-value pairs inside storage.json.
*   **backup:** Creates a backup of the current storage.json.
*   **patch:** Sets a value for a specific configuration path.
*   **delete:** Removes a specific configuration path.

Commands:
*   **Inspect storage configuration:**
    ```powershell
    $env:PYTHONIOENCODING="utf-8"; python "$env:USERPROFILE\.gemini\config\skills\antigravity-database-manager\scripts\__main__.py" storage inspect
    ```
*   **Patch storage key path:**
    ```powershell
    $env:PYTHONIOENCODING="utf-8"; python "$env:USERPROFILE\.gemini\config\skills\antigravity-database-manager\scripts\__main__.py" storage patch "<KEY_PATH>" "<VALUE>"
    ```
*   **Delete storage key path:**
    ```powershell
    $env:PYTHONIOENCODING="utf-8"; python "$env:USERPROFILE\.gemini\config\skills\antigravity-database-manager\scripts\__main__.py" storage delete "<KEY_PATH>"
    ```

---

### Module 12: AI-Powered Conversation Auto-Renamer (auto_rename)
This module dynamically parses the transcript logs of all conversations, extracts the content of the first user request, and uses the Gemini AI API to automatically update conversation titles in both their task artifacts (`task.md`) and database index to descriptive, highly professional summaries.

Command:
```powershell
$env:PYTHONIOENCODING="utf-8"; python "$env:USERPROFILE\.gemini\config\skills\antigravity-database-manager\scripts\auto_rename.py"
```

---

### Module 13: Global Operations and Safety Guarantees
This module outlines global flags and safety operations integrated into the database manager.
*   **JSON Output Mode:** The `--json` flag formats subcommand outputs into structured JSON (available for `scan`, `recover`, `health`, `diagnose`, `conversations list`, `workspace list`, and `storage inspect`).
*   **Headless Mode:** The `--headless` flag forces the tool to bypass the full-screen Visual TUI in favor of command-line operations.
*   **Debug Mode:** Setting `$env:AGMERCIUM_DEBUG = "1"` enables verbose logging to standard output.
*   **Automatic Rollback Guarantee:** If a database write operation fails mid-run, the manager immediately restores the active database from the automatic pre-write backup, preventing database corruption.
