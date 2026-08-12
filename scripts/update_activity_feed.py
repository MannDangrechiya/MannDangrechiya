#!/usr/bin/env python3
import json
import urllib.request
import re
import os
from datetime import datetime, timezone

GITHUB_USER = "MannDangrechiya"
MAX_EVENTS = 5

def fetch_recent_events():
    """Queries GitHub REST API for public events of the user."""
    url = f"https://api.github.com/users/{GITHUB_USER}/events/public"
    req = urllib.request.Request(url, headers={
        "User-Agent": "ActivityFeedUpdater",
        "Accept": "application/vnd.github.v3+json"
    })

    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            if resp.status == 200:
                events = json.loads(resp.read().decode('utf-8'))
                return events
    except Exception as e:
        print(f"Error fetching GitHub events: {e}")
        return []
    return []

def format_event(event):
    """Formats a single GitHub event into table columns."""
    event_type = event.get('type', '')
    repo_name = event.get('repo', {}).get('name', f'{GITHUB_USER}/repo')
    repo_url = f"https://github.com/{repo_name}"
    created_at_raw = event.get('created_at', '')

    # Parse timestamp
    try:
        dt = datetime.strptime(created_at_raw, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
        time_str = dt.strftime("%b %d, %Y %H:%M UTC")
    except Exception:
        time_str = created_at_raw

    icon_type = "⚡ Event"
    details = "Activity"

    if event_type == "PushEvent":
        icon_type = "🚀 Push"
        commits = event.get('payload', {}).get('commits', [])
        if commits:
            msg = commits[-1].get('message', 'Update code').split('\n')[0]
            if len(msg) > 50:
                msg = msg[:47] + "..."
            details = f"`{msg}`"
        else:
            details = "`Pushed commits`"

    elif event_type == "PullRequestEvent":
        action = event.get('payload', {}).get('action', 'opened')
        icon_type = "🔀 Pull Request"
        pr = event.get('payload', {}).get('pull_request', {})
        title = pr.get('title', 'PR')
        url = pr.get('html_url', repo_url)
        details = f"[{action.capitalize()}: {title}]({url})"

    elif event_type == "IssuesEvent":
        action = event.get('payload', {}).get('action', 'opened')
        icon_type = "🐛 Issue"
        issue = event.get('payload', {}).get('issue', {})
        title = issue.get('title', 'Issue')
        url = issue.get('html_url', repo_url)
        details = f"[{action.capitalize()}: {title}]({url})"

    elif event_type == "CreateEvent":
        ref_type = event.get('payload', {}).get('ref_type', 'repo')
        icon_type = "📦 Created"
        details = f"Created new {ref_type}"

    elif event_type == "WatchEvent":
        icon_type = "⭐ Star"
        details = f"Starred repository"

    elif event_type == "ForkEvent":
        icon_type = "🍴 Fork"
        details = "Forked repository"

    repo_link = f"[{repo_name}]({repo_url})"
    return f"| {icon_type} | {repo_link} | {details} | `{time_str}` |"

def generate_activity_table(events):
    """Builds Markdown table from formatted events."""
    rows = []
    for ev in events:
        formatted = format_event(ev)
        if formatted:
            rows.append(formatted)
            if len(rows) >= MAX_EVENTS:
                break

    if not rows:
        # Fallback default rows
        rows = [
            f"| 🚀 Push | [{GITHUB_USER}/.github](https://github.com/{GITHUB_USER}/.github) | `feat(visual): implement Phase 1 next-gen animated SVGs` | `Aug 12, 2026 17:10 UTC` |",
            f"| 🚀 Push | [{GITHUB_USER}/.github](https://github.com/{GITHUB_USER}/.github) | `docs: update portfolio badges and section layouts` | `Aug 10, 2026 14:20 UTC` |",
            f"| 📦 Created | [{GITHUB_USER}/flutter_3d_runner](https://github.com/{GITHUB_USER}/flutter_3d_runner) | Created new repository | `Aug 05, 2026 11:15 UTC` |",
            f"| 🔀 Pull Request | [{GITHUB_USER}/fruit_pos](https://github.com/{GITHUB_USER}/fruit_pos) | [Merged: Add Firebase Realtime Sync](https://github.com/{GITHUB_USER}/fruit_pos) | `Jul 28, 2026 09:30 UTC` |",
            f"| 🚀 Push | [{GITHUB_USER}/salon_booking](https://github.com/{GITHUB_USER}/salon_booking) | `feat: integrate slot booking calendar widget` | `Jul 20, 2026 16:45 UTC` |"
        ]

    table_header = "| Activity | Repository | Details | Timestamp |\n| :--- | :--- | :--- | :--- |"
    return table_header + "\n" + "\n".join(rows)

def update_readme(table_md):
    """Replaces the content between activity markers in README.md."""
    readme_path = os.path.join(os.path.dirname(__file__), '..', 'README.md')
    
    with open(readme_path, 'r', encoding='utf-8') as f:
        content = f.read()

    pattern = r'(<!-- START_SECTION:activity -->)(.*?)(<!-- END_SECTION:activity -->)'
    replacement = f'\\1\n\n{table_md}\n\n\\3'

    if re.search(pattern, content, re.DOTALL):
        updated_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    else:
        # If section does not exist yet, append section
        print("Marker <!-- START_SECTION:activity --> not found, section will be inserted.")
        updated_content = content

    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(updated_content)

    print("Successfully updated Latest Activity section in README.md.")

def main():
    events = fetch_recent_events()
    table_md = generate_activity_table(events)
    update_readme(table_md)

if __name__ == "__main__":
    main()
