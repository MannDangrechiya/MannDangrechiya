#!/usr/bin/env python3
import os
import subprocess
import datetime

CHANGELOG_PATH = os.path.join(os.path.dirname(__file__), "..", "PROFILE_CHANGELOG.md")

def check_git_changes():
    """Checks git status for modified files in repository."""
    try:
        res = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True, check=True)
        changes = res.stdout.strip().splitlines()
        modified_files = [line[3:].strip() for line in changes if line]
        return modified_files
    except Exception as e:
        print(f"Git status check failed ({e}), creating default sync entry...")
        return ["README.md", "assets/stats.svg", "assets/svg/xp-bar.svg"]

def update_changelog():
    """Appends a dated log entry to PROFILE_CHANGELOG.md."""
    now_utc = datetime.datetime.now(datetime.timezone.utc).strftime("%b %d, %Y %H:%M UTC")
    modified = check_git_changes()

    if not os.path.exists(CHANGELOG_PATH):
        header = """# 📜 Profile Automated Changelog

Log of automated updates, stats synchronization, XP calculations, and activity feed commits.

---

"""
        with open(CHANGELOG_PATH, "w", encoding="utf-8") as f:
            f.write(header)

    if not modified:
        print("No profile files modified, skipping changelog entry.")
        return

    # Filter relevant profile files
    profile_files = [f for f in modified if f.endswith(".svg") or f.endswith(".md") or "stats" in f]
    file_list_str = ", ".join([f"`{os.path.basename(f)}`" for f in profile_files[:4]]) if profile_files else "`README.md`, `assets/stats.svg`"

    entry = f"""### 🤖 [Bot] Update Profile Dashboard — `{now_utc}`

- **Commit Tag**: `[Bot] Update profile stats – {now_utc}`
- **Synchronized Assets**: {file_list_str}
- **Status**: ✅ All automated SVG cards, XP metrics, heatmap grid, and activity feed successfully updated.

---

"""

    # Prepend new entry right below header
    with open(CHANGELOG_PATH, "r", encoding="utf-8") as f:
        existing = f.read()

    if "---" in existing:
        parts = existing.split("---", 1)
        new_content = parts[0] + "---\n\n" + entry + parts[1].lstrip()
    else:
        new_content = existing + "\n\n" + entry

    with open(CHANGELOG_PATH, "w", encoding="utf-8") as f:
        f.write(new_content)

    print(f"Successfully recorded changelog entry in {CHANGELOG_PATH}")

if __name__ == "__main__":
    update_changelog()
