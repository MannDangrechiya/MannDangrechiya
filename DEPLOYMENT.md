# 🚢 Deployment & GitHub Actions Setup

This document explains how automated updates, workflow permissions, and secret keys operate.

---

## 🔐 Required Secrets Configuration

Go to your repository: **Settings > Secrets and variables > Actions > New repository secret**.

| Secret Name | Required For | Description |
| :--- | :--- | :--- |
| `GH_PAT` | WakaTime & Stats Sync | Personal Access Token with `repo` and `user` scope |
| `WAKATIME_API_KEY` | Coding Metrics | WakaTime secret key from [wakatime.com/settings/api-key](https://wakatime.com) |
| `SPOTIFY_CLIENT_ID` | Spotify Widget | Spotify Developer API Client ID |
| `SPOTIFY_CLIENT_SECRET` | Spotify Widget | Spotify Developer API Secret |
| `SPOTIFY_REFRESH_TOKEN` | Spotify Widget | OAuth2 Refresh Token for live track feed |

---

## ⚙️ GitHub Workflow Execution

### 1. Contribution Snake Workflow (`snake.yml`)
- Runs automatically at **00:00 UTC** daily.
- Generates `assets/svg/github-contribution-grid-snake.svg`.

### 2. Profile Stats Updater (`profile-stats-updater.yml`)
- Runs automatically every **12 hours**.
- Automatically syncs WakaTime coding hours and active language statistics into `README.md`.

---

## 🛠️ Manual Workflow Dispatch
You can manually trigger any workflow at any time:
1. Go to the **Actions** tab on GitHub.
2. Select the desired workflow (e.g. `Generate Contribution Snake Animation`).
3. Click **Run workflow**.
