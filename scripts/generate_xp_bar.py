#!/usr/bin/env python3
import json
import urllib.request
import os
import datetime

WORKER_URL = "https://devportfolio.manndangrechiya.workers.dev/api/stats"
GITHUB_USER = "MannDangrechiya"
OUTPUT_SVG = os.path.join(os.path.dirname(__file__), "..", "assets", "svg", "xp-bar.svg")

def fetch_metrics():
    """Fetches stats to calculate XP formula: (commits * 2) + (stars * 5) + (PRs * 10)"""
    commits, stars, prs = 450, 85, 32  # Fallback default values
    try:
        req = urllib.request.Request(WORKER_URL, headers={"User-Agent": "XPBarGenerator"})
        with urllib.request.urlopen(req, timeout=5) as response:
            if response.status == 200:
                data = json.loads(response.read().decode('utf-8'))
                gh = data.get("github", {})
                commits = gh.get("totalCommits", commits)
                stars = gh.get("stars", stars)
                prs = gh.get("prs", prs)
    except Exception as e:
        print(f"Worker fetch failed ({e}), using GitHub API / defaults...")
        try:
            url = f"https://api.github.com/users/{GITHUB_USER}/repos?per_page=100"
            req = urllib.request.Request(url, headers={"User-Agent": "XPBarGenerator"})
            with urllib.request.urlopen(req, timeout=5) as resp:
                repos = json.loads(resp.read().decode('utf-8'))
                stars = sum(r.get('stargazers_count', 0) for r in repos)
        except Exception:
            pass

    return commits, stars, prs

def generate_xp_svg(commits, stars, prs):
    # XP Formula: XP = (total commits * 2) + (stars * 5) + (PRs * 10)
    commits_xp = commits * 2
    stars_xp = stars * 5
    prs_xp = prs * 10
    total_xp = commits_xp + stars_xp + prs_xp

    # Level calculation: Each level requires 200 XP
    level = (total_xp // 200) + 1
    current_level_base = (level - 1) * 200
    next_level_xp = level * 200
    xp_in_level = total_xp - current_level_base
    needed_in_level = next_level_xp - current_level_base
    progress_pct = max(5, min(98, (xp_in_level / needed_in_level) * 100))

    # Overall percentage milestone (e.g. out of 2000 XP cap)
    max_cap_xp = 2000
    bar_width_total = 680
    filled_width = int((total_xp / max_cap_xp) * bar_width_total)
    filled_width = min(bar_width_total - 10, max(40, filled_width))
    glitch_x = filled_width + 40

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 760 150" width="100%" height="100%">
  <defs>
    <!-- Background Card Gradient -->
    <linearGradient id="xp-bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#070913" />
      <stop offset="100%" stop-color="#0B0E20" />
    </linearGradient>

    <!-- Bar Fill Gradient: Indigo -> Cyan -->
    <linearGradient id="xp-bar-grad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#6366F1" />
      <stop offset="70%" stop-color="#38BDF8" />
      <stop offset="100%" stop-color="#22D3EE" />
    </linearGradient>

    <linearGradient id="border-grad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#6366F1" stop-opacity="0.5" />
      <stop offset="100%" stop-color="#38BDF8" stop-opacity="0.2" />
    </linearGradient>

    <!-- Glitch Filter RGB Split -->
    <filter id="glitch-filter" x="-20%" y="-20%" width="140%" height="140%">
      <feTurbulence type="fractalNoise" baseFrequency="0.05 0.95" numOctaves="1" result="noise">
        <animate attributeName="baseFrequency" values="0.05 0.95;0.2 0.5;0.05 0.95" dur="0.8s" repeatCount="indefinite" />
      </feTurbulence>
      <feDisplacementMap in="SourceGraphic" in2="noise" scale="3" xChannelSelector="R" yChannelSelector="G" />
    </filter>

    <filter id="lead-glow" x="-50%" y="-50%" width="200%" height="200%">
      <feGaussianBlur stdDeviation="6" result="blur" />
      <feComposite in="SourceGraphic" in2="blur" operator="over" />
    </filter>
  </defs>

  <!-- Container -->
  <rect x="2" y="2" width="756" height="146" rx="16" fill="url(#xp-bg)" stroke="url(#border-grad)" stroke-width="2" />

  <!-- Header & Level Title -->
  <g transform="translate(30, 36)">
    <text x="0" y="0" font-family="'Inter', sans-serif" font-size="16" font-weight="800" fill="#F8FAFC" letter-spacing="0.5">
      ⚡ DEVELOPER XP &amp; RANK LEVEL
    </text>
    <rect x="280" y="-14" width="130" height="20" rx="10" fill="rgba(99,102,241,0.2)" stroke="#6366F1" stroke-width="1"/>
    <text x="345" y="0" font-family="'JetBrains Mono', monospace" font-size="10" font-weight="700" fill="#818CF8" text-anchor="middle">
      LVL {level} SENIOR NINJA
    </text>

    <!-- XP Stats Counter right aligned -->
    <text x="700" y="0" font-family="'JetBrains Mono', monospace" font-size="15" font-weight="700" fill="#38BDF8" text-anchor="end">
      {total_xp:,} XP <tspan font-size="11" fill="#64748B">/ {next_level_xp:,} XP</tspan>
    </text>
  </g>

  <!-- XP Progress Bar Container -->
  <g transform="translate(40, 60)">
    <!-- Track Background -->
    <rect x="0" y="0" width="{bar_width_total}" height="24" rx="12" fill="#0F172A" stroke="#1E293B" stroke-width="1.5" />

    <!-- Main Gradient Fill -->
    <rect x="0" y="0" width="{filled_width}" height="24" rx="12" fill="url(#xp-bar-grad)" />

    <!-- Glitch Cyber Edge Effect at the tip -->
    <g transform="translate({filled_width - 15}, -2)" filter="url(#glitch-filter)">
      <rect x="0" y="0" width="18" height="28" fill="#22D3EE" opacity="0.9" rx="3">
        <animate attributeName="opacity" values="0.9;0.3;1.0;0.5;0.9" dur="0.3s" repeatCount="indefinite"/>
      </rect>
      <!-- Cyber glitch spark line -->
      <line x1="12" y1="-4" x2="12" y2="32" stroke="#F472B6" stroke-width="2" opacity="0.8">
        <animate attributeName="x1" values="8;16;10;14;8" dur="0.2s" repeatCount="indefinite" />
        <animate attributeName="x2" values="8;16;10;14;8" dur="0.2s" repeatCount="indefinite" />
      </line>
    </g>

    <!-- Leading Tip Glow Pulse -->
    <circle cx="{filled_width}" cy="12" r="10" fill="#38BDF8" filter="url(#lead-glow)" opacity="0.8">
      <animate attributeName="r" values="8;14;8" dur="1.5s" repeatCount="indefinite" />
      <animate attributeName="opacity" values="0.6;1.0;0.6" dur="1.5s" repeatCount="indefinite" />
    </circle>
  </g>

  <!-- XP Subtext & Breakdown Formula -->
  <g transform="translate(40, 122)">
    <text x="0" y="0" font-family="'JetBrains Mono', monospace" font-size="11" font-weight="600" fill="#94A3B8">
      XP Formula: <tspan fill="#38BDF8">Commits ({commits}×2)</tspan> + <tspan fill="#818CF8">Stars ({stars}×5)</tspan> + <tspan fill="#C084FC">PRs ({prs}×10)</tspan>
    </text>

    <!-- Next Level Threshold Info -->
    <text x="{bar_width_total}" y="0" font-family="'JetBrains Mono', monospace" font-size="11" font-weight="700" fill="#38BDF8" text-anchor="end">
      {next_level_xp - total_xp} XP needed for Level {level + 1} 🚀
    </text>
  </g>
</svg>'''

    os.makedirs(os.path.dirname(OUTPUT_SVG), exist_ok=True)
    with open(OUTPUT_SVG, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"Successfully generated XP Bar SVG at {OUTPUT_SVG}")

if __name__ == "__main__":
    commits, stars, prs = fetch_metrics()
    generate_xp_svg(commits, stars, prs)
