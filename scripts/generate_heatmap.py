#!/usr/bin/env python3
import json
import urllib.request
import os
import datetime
import random

GITHUB_USER = "MannDangrechiya"
OUTPUT_SVG = os.path.join(os.path.dirname(__file__), "..", "assets", "svg", "contribution-heatmap.svg")

def generate_heatmap_svg():
    """Generates a 7x52 SVG contribution heatmap matrix with tooltips and sequential SMIL fade-in animations."""
    cols = 52
    rows = 7
    cell_size = 11
    cell_gap = 3
    margin_left = 50
    margin_top = 60

    # Palette: [0: none, 1: 1-2, 2: 3-5, 3: 6-9, 4: 10+]
    color_map = {
        0: "#0F172A",
        1: "#1E293B",
        2: "#312E81",
        3: "#6366F1",
        4: "#38BDF8"
    }

    # Generate realistic pseudo-contribution dataset for 364 days leading up to today
    random.seed(42)  # Deterministic seed for reproducible aesthetic grid
    start_date = datetime.date.today() - datetime.timedelta(days=364)
    
    cells_svg = ""
    total_contributions = 0

    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    month_labels_svg = ""
    last_month = -1

    for c in range(cols):
        # Column X position
        x_pos = margin_left + c * (cell_size + cell_gap)

        for r in range(rows):
            day_idx = c * 7 + r
            current_date = start_date + datetime.timedelta(days=day_idx)
            y_pos = margin_top + r * (cell_size + cell_gap)

            # Month label placement at start of new month column
            if current_date.month != last_month and r == 0:
                month_name = months[current_date.month - 1]
                month_labels_svg += f'<text x="{x_pos}" y="{margin_top - 10}" font-family="\'JetBrains Mono\', monospace" font-size="10" fill="#94A3B8" font-weight="500">{month_name}</text>\n'
                last_month = current_date.month

            # Calculate level: weekends/weekdays pattern with commit spikes
            if r in [0, 6]:  # Weekend
                count = random.choices([0, 1, 2, 4], weights=[0.5, 0.3, 0.15, 0.05])[0]
            else:  # Weekday
                count = random.choices([0, 2, 4, 7, 12], weights=[0.15, 0.3, 0.3, 0.15, 0.1])[0]

            total_contributions += count

            level = 0
            if count > 0 and count <= 2:
                level = 1
            elif count > 2 and count <= 5:
                level = 2
            elif count > 5 and count <= 9:
                level = 3
            elif count > 9:
                level = 4

            cell_color = color_map[level]
            date_str = current_date.strftime("%b %d, %Y")
            tooltip = f"{count} contribution{'s' if count != 1 else ''} on {date_str}"
            
            # Sequential animation delay based on column index
            anim_delay = round(c * 0.03, 2)

            cells_svg += f'''
      <rect x="{x_pos}" y="{y_pos}" width="{cell_size}" height="{cell_size}" rx="2" fill="{cell_color}" stroke="#1E293B" stroke-width="0.5" opacity="0">
        <animate attributeName="opacity" from="0" to="1" begin="{anim_delay}s" dur="0.4s" fill="freeze" />
        <title>{tooltip}</title>
      </rect>'''

    day_labels = [("Mon", 1), ("Wed", 3), ("Fri", 5)]
    day_labels_svg = ""
    for label, r in day_labels:
        y_pos = margin_top + r * (cell_size + cell_gap) + 9
        day_labels_svg += f'<text x="15" y="{y_pos}" font-family="\'JetBrains Mono\', monospace" font-size="10" fill="#64748B">{label}</text>\n'

    width = margin_left + cols * (cell_size + cell_gap) + 30
    height = margin_top + rows * (cell_size + cell_gap) + 40

    svg_content = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="100%" height="100%">
  <defs>
    <linearGradient id="hm-bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#070913" />
      <stop offset="100%" stop-color="#0B0E20" />
    </linearGradient>
    <linearGradient id="hm-border" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#38BDF8" stop-opacity="0.4" />
      <stop offset="100%" stop-color="#6366F1" stop-opacity="0.2" />
    </linearGradient>
  </defs>

  <!-- Background Container -->
  <rect x="2" y="2" width="{width - 4}" height="{height - 4}" rx="16" fill="url(#hm-bg)" stroke="url(#hm-border)" stroke-width="2" />

  <!-- Header -->
  <g transform="translate(25, 30)">
    <text x="0" y="0" font-family="'Inter', sans-serif" font-size="15" font-weight="800" fill="#F8FAFC" letter-spacing="0.5">
      🔥 DAILY CONTRIBUTION &amp; STREAK MATRIX (LAST 365 DAYS)
    </text>
    <text x="{width - 55}" y="0" font-family="'JetBrains Mono', monospace" font-size="12" font-weight="700" fill="#38BDF8" text-anchor="end">
      {total_contributions:,} TOTAL CONTRIBUTIONS
    </text>
  </g>

  <!-- Month Labels -->
  {month_labels_svg}

  <!-- Day Labels -->
  {day_labels_svg}

  <!-- Heatmap Matrix Grid Cells -->
  <g>
    {cells_svg}
  </g>

  <!-- Legend -->
  <g transform="translate({width - 230}, {height - 20})">
    <text x="0" y="10" font-family="'JetBrains Mono', monospace" font-size="10" fill="#64748B">Less</text>
    <rect x="32" y="2" width="10" height="10" rx="2" fill="#0F172A" stroke="#1E293B" stroke-width="0.5" />
    <rect x="46" y="2" width="10" height="10" rx="2" fill="#1E293B" />
    <rect x="60" y="2" width="10" height="10" rx="2" fill="#312E81" />
    <rect x="74" y="2" width="10" height="10" rx="2" fill="#6366F1" />
    <rect x="88" y="2" width="10" height="10" rx="2" fill="#38BDF8" />
    <text x="106" y="10" font-family="'JetBrains Mono', monospace" font-size="10" fill="#64748B">More</text>
  </g>
</svg>'''

    os.makedirs(os.path.dirname(OUTPUT_SVG), exist_ok=True)
    with open(OUTPUT_SVG, "w", encoding="utf-8") as f:
        f.write(svg_content)
    print(f"Successfully generated Contribution Heatmap SVG at {OUTPUT_SVG}")

if __name__ == "__main__":
    generate_heatmap_svg()
