#!/usr/bin/env python3
"""
Fetch PR data from GitHub using gh CLI and save as JSON.
"""
import argparse
import json
import subprocess
import sys
from datetime import datetime
from typing import Any, Dict, List

DEFAULT_REPO = "AgenticAIPlan/AgenticAISkills"

# Import score calculation and analysis functions
sys.path.insert(0, __file__.replace("fetch_prs.py", ""))
try:
    from analyze_pr import calculate_pr_score, extract_skill_info, generate_skill_advantages, generate_skill_improvements
except ImportError:
    # If not in same directory, define placeholder
    def calculate_pr_score(pr):
        return 50.0
    def extract_skill_info(pr):
        return {}
    def generate_skill_advantages(pr, skill_info):
        return []
    def generate_skill_improvements(pr, skill_info):
        return []


def run_gh_command(args: List[str]) -> Dict[str, Any]:
    """Run gh CLI command and return JSON output."""
    cmd = ["gh"] + args
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )
        return json.loads(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Error running gh command: {e}", file=sys.stderr)
        if e.stderr:
            print(f"stderr: {e.stderr}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON output: {e}", file=sys.stderr)
        sys.exit(1)


def fetch_prs(
    repo: str = DEFAULT_REPO,
    author: str = None,
    state: str = "open",
    limit: int = 100,
    search_query: str = None
) -> List[Dict[str, Any]]:
    """
    Fetch PRs from GitHub.

    Args:
        repo: Repository in format "owner/repo".
        author: Filter by author (e.g., "@me" or username)
        state: PR state (open, closed, all)
        limit: Maximum number of PRs to fetch
        search_query: Custom search query

    Returns:
        List of PR objects with full details
    """
    # Build gh pr list command
    args = [
        "pr", "list",
        "--json", "number,title,state,url,author,reviews,latestReviews,reviewDecision,reviewRequests,createdAt,updatedAt,headRefName,baseRefName,labels,statusCheckRollup,additions,deletions,changedFiles,files,body,isDraft",
        "--limit", str(limit),
        "--search", f"state:{state}"
    ]

    # Add custom search query if provided
    if search_query:
        args[-1] = f"{args[-1]} {search_query}"

    # Add repo filter if specified
    if repo:
        args.extend(["--repo", repo])

    # Add author filter if specified
    if author:
        args.extend(["--author", author])

    print(f"Fetching PRs with command: gh {' '.join(args)}", file=sys.stderr)

    result = run_gh_command(args)
    return result


def extract_ci_status(pr: Dict[str, Any]) -> str:
    """
    Extract CI status from PR's statusCheckRollup.

    Returns:
        "SUCCESS", "FAILURE", "PENDING", or None
    """
    status_rollup = pr.get("statusCheckRollup", [])
    if not status_rollup:
        return None

    # Check if any critical checks have failed
    for check in status_rollup:
        conclusion = check.get("conclusion")
        if conclusion == "FAILURE":
            return "FAILURE"
        if conclusion == "TIMED_OUT":
            return "FAILURE"

    # Check if any checks are still pending
    for check in status_rollup:
        status = check.get("status")
        if status in ("QUEUED", "IN_PROGRESS", "PENDING"):
            return "PENDING"

    # If we have checks and none failed/pending, consider it success
    return "SUCCESS"


def main():
    parser = argparse.ArgumentParser(description="Fetch PR data from GitHub")
    parser.add_argument("--repo", default=DEFAULT_REPO, help=f"Repository to inspect. Defaults to {DEFAULT_REPO}.")
    parser.add_argument("--author", help="Filter by author (@me or username)")
    parser.add_argument("--state", default="open", choices=["open", "closed", "all"], help="PR state")
    parser.add_argument("--limit", type=int, default=100, help="Maximum number of PRs")
    parser.add_argument("--search", help="Custom search query")
    parser.add_argument("--output", default="prs.json", help="Output JSON file")
    parser.add_argument("--pretty", action="store_true", help="Pretty print JSON")

    args = parser.parse_args()

    repo = args.repo or DEFAULT_REPO

    # Fetch PRs
    prs = fetch_prs(
        repo=repo,
        author=args.author,
        state=args.state,
        limit=args.limit,
        search_query=args.search
    )

    # Enrich with additional fields
    for pr in prs:
        pr["ci_status"] = extract_ci_status(pr)
        pr["quality_score"] = calculate_pr_score(pr)

        # Extract skill information and generate evaluation
        skill_info = extract_skill_info(pr)
        pr["skill_info"] = skill_info

        # Generate skill-specific advantages and improvements
        advantages = generate_skill_advantages(pr, skill_info)
        improvements = generate_skill_improvements(pr, skill_info)
        pr["advantages"] = advantages[:2]  # Max 2 advantages
        pr["improvements"] = improvements[:2]  # Max 2 improvements

        pr["repo"] = repo
        pr["fetched_at"] = datetime.now().isoformat()

    # Sort by quality score (descending)
    prs.sort(key=lambda p: p.get("quality_score", 0), reverse=True)

    # Output
    output = {
        "repo": repo,
        "fetched_at": datetime.now().isoformat(),
        "count": len(prs),
        "prs": prs
    }

    with open(args.output, "w", encoding="utf-8") as f:
        if args.pretty:
            json.dump(output, f, indent=2, ensure_ascii=False)
        else:
            json.dump(output, f, ensure_ascii=False)

    print(f"Fetched {len(prs)} PR(s) from {repo}", file=sys.stderr)
    print(f"Saved to {args.output}", file=sys.stderr)


if __name__ == "__main__":
    main()
