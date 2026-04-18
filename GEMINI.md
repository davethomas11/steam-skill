# Gemini CLI Instructions: Steam Stats Project

These instructions are foundational mandates for any Gemini CLI agent working within this workspace.

## 🛡️ Security & Privacy Mandates (Priority 1)

1.  **Strict Credential Protection**:
    *   **NEVER** log, print, or echo the contents of any `.env` file.
    *   **NEVER** output the value of `STEAM_API_KEY` or `STEAM_ID` to the terminal or any file.
    *   **NEVER** include real API keys or personal SteamIDs in code, documentation, or commit messages. Always use placeholders (e.g., `your_api_key_here`).
    *   **NEVER** commit the `.env` file. Verify it is always listed in `.gitignore`.

2.  **Redaction Protocol**:
    *   When running scripts that use environment variables, rely on Gemini CLI's built-in redaction. If you suspect a tool might bypass redaction, DO NOT execute it with sensitive variables.

3.  **PII Handling**:
    *   Treat SteamIDs as Private Personally Identifiable Information (PII). Do not store them in the repository history.

## 🛠️ Operational Guidelines

1.  **Skill Integrity**:
    *   The `.skill` file is a build artifact. If you modify any files in the `steam-stats/` folder, you **must** repackage the skill using the `package_skill.cjs` script.
    *   Always validate the skill before packaging.

2.  **User Guidance**:
    *   When troubleshooting Steam API Key creation, always point users to the **Steam Mobile App -> Hamburger Menu -> Confirmations** path, as it does not send push notifications.

3.  **Testing**:
    *   Before suggesting an installation, always verify the core script (`steam-stats/scripts/steam_query.py`) works by running it directly against the source, assuming the user has configured their `.env` file.
