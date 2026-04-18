# Agentic Skill - Steam API

This project provides a specialized, agent-agnostic skill for interacting with the Steam Web API to retrieve game statistics, owned games, and achievements.

> **Note:** This skill was built and tested primarily using **Gemini CLI**. While it includes installation support for Claude and GitHub Copilot, compatibility with those agents is provided on a best-effort basis.

## 🧠 What is an Agentic Skill?

Think of an **Agentic Skill** as a specialized "instruction manual" for your AI assistant. 

By default, AI agents are generalists. When you "install" this skill, you are giving your AI agent the specific tools, API knowledge, and procedural instructions it needs to become an expert on the Steam Web API. This allows the agent to safely and accurately perform tasks like checking your game library or stats without you having to explain how the API works every time.

## 🛡️ Security & Transparency

### What is a `.skill` file?
The `steam-stats.skill` file is **not a binary**. It is a standard **ZIP archive** containing the human-readable source code for this skill.
- **SKILL.md**: Instructions for the AI agent.
- **scripts/**: Python scripts that perform the API calls.
- **references/**: Documentation for the API endpoints.

You can verify the contents at any time by renaming the file to `.zip` and extracting it.

### Safe Key Management
This skill is designed to use **environment variables** for sensitive information. By using a `.env` file, your keys are automatically redacted from all CLI logs and terminal output by Gemini CLI's security system.

---

## ⚠️ Common Hurdles (Updated April 2026)

### Steam API Key Creation: The "App Auth" Trap
As of April 2026, Steam has added a mandatory authentication step via the **Steam Mobile App** when creating a new API key. This step **does not send a push notification** to your device.

**The Process:**
1.  Go to [steamcommunity.com/dev/apikey](https://steamcommunity.com/dev/apikey).
2.  After clicking Register, open your **Steam Mobile App**.
3.  **Where to find it:** Tap the **hamburger menu (three lines)** and select **Confirmations**. The request will be waiting there.
4.  **Avoid Rate Limits:** If you don't see it, do **not** keep clicking Register. Wait or restart the app. Repeated attempts will lead to a lockout.

---

### 1. Obtain your Steam API Credentials
1.  **Steam Web API Key**: 
    *   Visit [steamcommunity.com/dev/apikey](https://steamcommunity.com/dev/apikey).
2.  **SteamID64**: 
    *   Your 17-digit ID can be found in your Steam Profile URL (e.g., `76561198...`).

### 2. Configure Environment Variables
Create a file named `.env` in this root directory:

```env
STEAM_API_KEY=your_api_key_here
STEAM_ID=your_17_digit_id_here
```

### 3. Use System Secure Store (Optional)
For extra security, you can store your keys in your OS keychain instead of a `.env` file.

#### Why use a Secure Store?
Using a system secure store (like the macOS Keychain or PowerShell SecretStore) provides a significantly higher level of protection than a standard `.env` file:

- **Encryption at Rest:** Unlike a `.env` file, which is plain text, these stores encrypt your keys using industry-standard algorithms (like AES). Even if someone gains access to your files, they cannot read the keys.
- **Session-Based Access:** These stores are often tied to your **User Login Session**. This means the keys are only "unlocked" when you are actively logged in.
- **Protection from Network Attacks:** If an attacker gains unauthorized access to your file system through the network, they might be able to steal your `.env` file, but they **cannot** decrypt the secrets in a secure store without your system password or a specific master key.
- **Agent Context:** Because the AI agent (Gemini CLI) runs with your user permissions, it can securely request the keys on your behalf while you are at the terminal, keeping them out of permanent cleartext files.

**On Windows (PowerShell SecretStore):**
```powershell
Set-Secret -Name STEAM_API_KEY -Secret "your_key"
Set-Secret -Name STEAM_ID -Secret "your_id"
```

**On macOS (Keychain):**
```bash
security add-generic-password -s STEAM_API_KEY -w "your_key"
security add-generic-password -s STEAM_ID -w "your_id"
```
The skill will automatically check these locations if the environment variables are not set.

---

## 🧪 Testing & Installation

### Testing (Pre-installation)
You can test the skill directly using the source script before installing it:
```bash
python steam-stats/scripts/steam_query.py IPlayerService GetOwnedGames v1 include_appinfo=true
```

### Installation
The easiest way to install the skill for all supported agents (Gemini, Claude, Copilot) is to use the provided scripts:

**On Windows (PowerShell):**
```powershell
.\install.ps1
```

**On Linux/macOS (Bash):**
```bash
chmod +x install.sh
./install.sh
```

**Manual Installation (Gemini CLI only):**
Once you are satisfied, install the skill to Gemini CLI:
...

**Local (This workspace only):**
```bash
gemini skills install steam-stats.skill --scope workspace
```

**Global (All projects):**
```bash
gemini skills install steam-stats.skill --scope user
```

**Note:** After installation, run `/skills reload` in your interactive Gemini session to enable it.
