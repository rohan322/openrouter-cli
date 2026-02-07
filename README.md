# OpenRouter Org Management Prototype

## Purpose
This tool is a **prototype** designed to explore the capabilities and limits of organization management through the OpenRouter API. It allows us to test:
*   Programmatic key generation and management.
*   Usage tracking via key hashes.
*   Model availability filtering for the organization.

## ⚠️ Prototype Notice
**This is not production code.**
*   **Current State**: Uses local `.config` files (`app.config`, `user.config`) for simplicity during testing.
*   **Future State**: The final implementation will integrate with **Okta** for authentication and store sensitive data (usernames, key hashes) in a **secure database**. No local config files will be used in production.

## Setup
1.  **Prerequisites**: Python 3.x
2.  **Configuration**:
    *   Open `app.config`.
    *   Add your **OpenRouter Provisioning Key** (from your Org settings).
    ```json
    { "provisioning_key": "sk-or-prov-..." }
    ```

## Usage

### 1. Generate a User Key
Simulates on-boarding a user or creating a new service key.
```bash
python openrouter_cli.py make-key --name "test-user-key"
```
*   **Action**: Calls OpenRouter API to create a key.
*   **Output**: Displays the full API key **ONCE**.
*   **Storage**: Saves only the **Key Hash** to `user.config` (simulating DB storage).

### 2. Check Usage
Verifies we can track usage without storing the actual API key.
```bash
python openrouter_cli.py usage
```
*   **Action**: Uses the stored hash and the Provisioning Key to look up usage stats.

### 3. List Authorized Models
Checks which models are available to the organization/user.
```bash
python openrouter_cli.py models
```
*   **Action**: Fetches available models and filters them to our authorized ZDR providers (e.g., Azure, OpenAI, Anthropic).

## Files
*   `openrouter_cli.py`: Main entry point.
*   `utils.py` & `commands/`: detailed implementation logic.
*   `modelChecker.py`: Legacy script (reference only).
