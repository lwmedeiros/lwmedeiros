"""
Metrics generator for lwmedeiros GitHub profile.
Scans all public repos for STATUS.md files, aggregates data, generates metrics.svg.
Run via GitHub Actions or locally with: python update_metrics.py
"""

import json
import urllib.request
import re
import base64
import os

GITHUB_USER = "lwmedeiros"
PROFILE_REPO = "lwmedeiros"


def fetch_repos():
    """Get all public repos for the user."""
    url = f"https://api.github.com/users/{GITHUB_USER}/repos?per_page=100&type=public"
    headers = {"Accept": "application/vnd.github.v3+json"}
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"token {token}"
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode())


def fetch_status_md(repo_name):
    """Try to fetch and parse STATUS.md from a repo."""
    url = f"https://api.github.com/repos/{GITHUB_USER}/{repo_name}/contents/STATUS.md"
    headers = {"Accept": "application/vnd.github.v3+json"}
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"token {token}"
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode())
            content = base64.b64decode(data["content"]).decode()
            return parse_frontmatter(content)
    except Exception:
        return None


def parse_frontmatter(text):
    """Extract YAML frontmatter values from STATUS.md."""
    match = re.search(r"^---\s*\n(.*?)\n---", text, re.DOTALL)
    if not match:
        return None
    
    result = {}
    for line in match.group(1).split("\n"):
        line = line.split("#")[0].strip()  # remove comments
        if ":" in line:
            key, val = line.split(":", 1)
            key = key.strip()
            val = val.strip()
            # try to parse as int
            try:
                val = int(val)
            except ValueError:
                pass
            result[key] = val
    return result


def generate_svg(metrics):
    """Generate the metrics.svg from aggregated data."""
    
    projects = metrics["projects_completed"]
    total = metrics["total_projects"]
    decisions = metrics["decisions_made"]
    rejections = metrics["ai_rejections"]
    bugs = metrics["bugs_caught"]
    lines = metrics["lines_tested"]
    
    # Format large numbers
    def fmt(n):
        if n >= 1000:
            return f"{n/1000:.1f}k"
        return str(n)
    
    # Progress bar width (based on completed/total projects)
    progress = (projects / max(total, 1)) * 680 if total > 0 else 0
    progress_text = f"{projects}/{total} projects completed" if total > 0 else "No projects yet"
    
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="800" height="155" viewBox="0 0 800 155">
  <defs>
    <linearGradient id="bg4" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#0a0a0a"/>
      <stop offset="100%" style="stop-color:#0d1117"/>
    </linearGradient>
    <linearGradient id="bar4" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" style="stop-color:#00d4aa"/>
      <stop offset="100%" style="stop-color:#0077b6"/>
    </linearGradient>
  </defs>

  <rect width="800" height="155" fill="url(#bg4)"/>

  <rect x="35" y="18" width="3" height="16" fill="#00d4aa" rx="1"/>
  <text x="48" y="31" font-family="'Segoe UI',Helvetica,Arial,sans-serif" font-size="11" fill="#00d4aa" letter-spacing="2.5" font-weight="600">ENGINEERING METRICS — LIVE</text>
  <line x1="290" y1="25" x2="765" y2="25" stroke="#1a2332" stroke-width="1"/>

  <!-- Card: Projects -->
  <g transform="translate(35,48)">
    <rect width="140" height="75" rx="6" fill="#0d1117" stroke="#1a2332"/>
    <text x="70" y="35" font-family="'Segoe UI',Helvetica,Arial,sans-serif" font-size="28" fill="#e6edf3" font-weight="700" text-anchor="middle">{fmt(projects)}</text>
    <text x="70" y="55" font-family="'Segoe UI',Helvetica,Arial,sans-serif" font-size="9" fill="#6e7681" text-anchor="middle" letter-spacing="1">SHIPPED</text>
    <rect x="15" y="65" width="110" height="3" rx="1" fill="#1a2332"/>
    <rect x="15" y="65" width="{min(110, int(110 * projects / max(total, 1))) if total > 0 else 0}" height="3" rx="1" fill="url(#bar4)" opacity="0.7"/>
  </g>

  <!-- Card: Decisions -->
  <g transform="translate(190,48)">
    <rect width="140" height="75" rx="6" fill="#0d1117" stroke="#1a2332"/>
    <text x="70" y="35" font-family="'Segoe UI',Helvetica,Arial,sans-serif" font-size="28" fill="#e6edf3" font-weight="700" text-anchor="middle">{fmt(decisions)}</text>
    <text x="70" y="55" font-family="'Segoe UI',Helvetica,Arial,sans-serif" font-size="9" fill="#6e7681" text-anchor="middle" letter-spacing="1">DECISIONS</text>
    <rect x="15" y="65" width="110" height="3" rx="1" fill="#1a2332"/>
    <rect x="15" y="65" width="{min(110, decisions * 2)}" height="3" rx="1" fill="url(#bar4)" opacity="0.7"/>
  </g>

  <!-- Card: Rejections -->
  <g transform="translate(345,48)">
    <rect width="140" height="75" rx="6" fill="#0d1117" stroke="#1a2332"/>
    <text x="70" y="35" font-family="'Segoe UI',Helvetica,Arial,sans-serif" font-size="28" fill="#e6edf3" font-weight="700" text-anchor="middle">{fmt(rejections)}</text>
    <text x="70" y="55" font-family="'Segoe UI',Helvetica,Arial,sans-serif" font-size="9" fill="#6e7681" text-anchor="middle" letter-spacing="1">AI REJECTIONS</text>
    <rect x="15" y="65" width="110" height="3" rx="1" fill="#1a2332"/>
    <rect x="15" y="65" width="{min(110, rejections * 5)}" height="3" rx="1" fill="url(#bar4)" opacity="0.7"/>
  </g>

  <!-- Card: Bugs -->
  <g transform="translate(500,48)">
    <rect width="140" height="75" rx="6" fill="#0d1117" stroke="#1a2332"/>
    <text x="70" y="35" font-family="'Segoe UI',Helvetica,Arial,sans-serif" font-size="28" fill="#e6edf3" font-weight="700" text-anchor="middle">{fmt(bugs)}</text>
    <text x="70" y="55" font-family="'Segoe UI',Helvetica,Arial,sans-serif" font-size="9" fill="#6e7681" text-anchor="middle" letter-spacing="1">BUGS CAUGHT</text>
    <rect x="15" y="65" width="110" height="3" rx="1" fill="#1a2332"/>
    <rect x="15" y="65" width="{min(110, bugs * 3)}" height="3" rx="1" fill="url(#bar4)" opacity="0.7"/>
  </g>

  <!-- Card: Lines -->
  <g transform="translate(655,48)">
    <rect width="110" height="75" rx="6" fill="#0d1117" stroke="#1a2332"/>
    <text x="55" y="35" font-family="'Segoe UI',Helvetica,Arial,sans-serif" font-size="28" fill="#e6edf3" font-weight="700" text-anchor="middle">{fmt(lines)}</text>
    <text x="55" y="55" font-family="'Segoe UI',Helvetica,Arial,sans-serif" font-size="9" fill="#6e7681" text-anchor="middle" letter-spacing="1">LINES TESTED</text>
    <rect x="12" y="65" width="86" height="3" rx="1" fill="#1a2332"/>
    <rect x="12" y="65" width="{min(86, int(lines / 50))}" height="3" rx="1" fill="url(#bar4)" opacity="0.7"/>
  </g>

  <!-- Progress bar -->
  <g transform="translate(35,135)">
    <rect width="730" height="16" rx="4" fill="#0d1117" stroke="#1a2332" stroke-width="0.5"/>
    <rect x="2" y="2" width="{max(0, progress)}" height="12" rx="3" fill="url(#bar4)" opacity="0.3"/>
    <text x="12" y="12" font-family="'Courier New',monospace" font-size="10" fill="#6e7681">{progress_text}</text>
    <circle cx="715" cy="8" r="3" fill="#00d4aa" opacity="0.5">
      <animate attributeName="opacity" values="0.5;0.15;0.5" dur="1.5s" repeatCount="indefinite"/>
    </circle>
  </g>
</svg>'''
    
    return svg


def main():
    print("Fetching repos...")
    repos = fetch_repos()
    
    # Aggregate metrics
    metrics = {
        "total_projects": 0,
        "projects_completed": 0,
        "decisions_made": 0,
        "ai_rejections": 0,
        "bugs_caught": 0,
        "lines_tested": 0,
    }
    
    for repo in repos:
        name = repo["name"]
        if name == PROFILE_REPO:
            continue  # skip the profile repo itself
        
        status = fetch_status_md(name)
        if status is None:
            continue
        
        print(f"  Found STATUS.md in {name}: {status.get('status', 'unknown')}")
        
        metrics["total_projects"] += 1
        if status.get("status") == "completed":
            metrics["projects_completed"] += 1
        metrics["decisions_made"] += int(status.get("decisions_made", 0))
        metrics["ai_rejections"] += int(status.get("ai_rejections", 0))
        metrics["bugs_caught"] += int(status.get("bugs_caught", 0))
        metrics["lines_tested"] += int(status.get("lines_tested", 0))
    
    print(f"Aggregated: {metrics}")
    
    # Generate SVG
    svg = generate_svg(metrics)
    
    with open("metrics.svg", "w") as f:
        f.write(svg)
    
    print("metrics.svg updated.")


if __name__ == "__main__":
    main()
