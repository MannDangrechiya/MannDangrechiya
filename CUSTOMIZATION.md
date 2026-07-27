# 🎨 Customization Guide

This document details how to customize color schemes, SVG graphics, bio data, and dynamic API integrations for this profile.

---

## 🎨 Color Palette & Design System

The profile follows a cyber-luxury dark theme inspired by **Linear**, **Vercel**, **Apple**, and **Raycast**:

| Element | Hex Code | Purpose |
| :--- | :--- | :--- |
| **Obsidian Void** | `#07090E` | Main Background Surface |
| **Card Surface** | `#0D111A` | Secondary Glass Container |
| **Indigo Glow** | `#6366F1` | Primary Accent / Pulsing Nodes |
| **Cyan Spark** | `#38BDF8` | Flutter / Subhead Highlights |
| **Emerald Active** | `#10B981` | Status Pill & Live Metrics |
| **Purple Shimmer** | `#C084FC` | State & Architecture Accents |

---

## ✏️ Customizing `whoami.dart` Card

To update the Dart code snippet rendered in `assets/svg/whoami-card.svg`:
1. Open [whoami-card.svg](assets/svg/whoami-card.svg).
2. Locate lines inside `<g class="mono">`.
3. Update values for `name`, `role`, `location`, `coreStack`, and `currentMission`.

---

## 📊 Updating Dynamic GitHub Stats & Badges

In `README.md`, stats cards use `github-readme-stats` and `github-readme-streak-stats` configured with dark mode parameters:
- `theme=react`
- `bg_color=090D16`
- `title_color=38BDF8`
- `text_color=94A3B8`
- `icon_color=6366F1`
- `border_color=1E293B`

---

## 🎵 Spotify Now Playing Widget Integration

To display live music playback:
1. Setup a Spotify Developer App at [developer.spotify.com](https://developer.spotify.com).
2. Follow `spotify-github-readme` guide to obtain `SPOTIFY_CLIENT_ID`, `SPOTIFY_CLIENT_SECRET`, and `SPOTIFY_REFRESH_TOKEN`.
3. Add these as GitHub Repository Secrets under **Settings > Secrets and variables > Actions**.
