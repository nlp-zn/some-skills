#!/usr/bin/env python3
"""
Compare current PR states with historical data to identify changes.
"""
import argparse
import json
import sys
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple


def load_state_file(filepath: str) -> Dict[str, Any]:
    """Load state file, return empty dict if not exists or invalid."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def extract_pr_snapshot(pr: Dict[str, Any]) -> Dict[str, Any]:
    """Extract relevant fields for state comparison."""
    return {
        "number": pr["number"],
        "title": pr["title"],
        "author": pr["author"]["login"],
        "review_decision": pr.get("reviewDecision"),
        "ci_status": pr.get("ci_status"),
        "approvers": [
            r["author"]["login"]
            for r in pr.get("latestReviews", [])
            if r.get("state") == "APPROVED"
        ],
        "reviewers_requested": [
            r["login"]
            for r in pr.get("reviewRequests", [])
        ],
        "labels": [l["name"] for l in pr.get("labels", [])],
        "created_at": pr["createdAt"],
        "updated_at": pr["updatedAt"],
        "additions": pr.get("additions", 0),
        "deletions": pr.get("deletions", 0),
        "changed_files": pr.get("changedFiles", 0),
        "is_draft": pr.get("isDraft", False)
    }


def detect_changes(
    current_pr: Dict[str, Any],
    history_entry: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Detect changes between current PR state and historical snapshot.

    Returns:
        Dict with change flags and details
    """
    old_snapshot = history_entry.get("snapshot", {})
    current_snapshot = extract_pr_snapshot(current_pr)

    changes = {
        "new_pr": False,  # Set by caller
        "ci_changed": old_snapshot.get("ci_status") != current_snapshot["ci_status"],
        "review_decision_changed": old_snapshot.get("review_decision") != current_snapshot["review_decision"],
        "new_approvals": False,
        "new_review_comments": False,  # Placeholder - would need comment count
        "updated_recently": False,
        "labels_changed": set(old_snapshot.get("labels", [])) != set(current_snapshot["labels"]),
        "draft_status_changed": old_snapshot.get("is_draft") != current_snapshot["is_draft"]
    }

    # Check for new approvals
    old_approvers = set(old_snapshot.get("approvers", []))
    current_approvers = set(current_snapshot["approvers"])
    changes["new_approvals"] = len(current_approvers - old_approvers) > 0

    # Check if updated recently (within 4 hours)
    updated_at = datetime.fromisoformat(current_snapshot["updated_at"].replace("Z", "+00:00"))
    changes["updated_recently"] = (datetime.now(updated_at.tzinfo) - updated_at).total_seconds() < 4 * 3600

    return changes


def has_meaningful_changes(changes: Dict[str, Any]) -> bool:
    """Check if changes are meaningful enough to highlight."""
    return any([
        changes["ci_changed"],
        changes["review_decision_changed"],
        changes["new_approvals"],
        changes["new_review_comments"],
        changes["labels_changed"],
        changes["draft_status_changed"]
    ])


def categorize_pr(
    pr: Dict[str, Any],
    history: Dict[str, Any],
    repo: str
) -> Optional[Tuple[str, Dict[str, Any]]]:
    """
    Categorize PR based on state and changes.

    Returns:
        Tuple of (category, changes) or None if should be ignored
        Categories: "new", "progress", "unchanged", "needs_attention", "ready"
    """
    pr_num = str(pr["number"])
    pr_history = history.get("pr_history", {}).get(repo, {})

    # Check if new PR
    if pr_num not in pr_history:
        return ("new", {"new_pr": True})

    # Get historical data
    history_entry = pr_history[pr_num]
    changes = detect_changes(pr, history_entry)

    # Check if needs author attention
    if pr.get("ci_status") == "FAILURE" or pr.get("reviewDecision") == "CHANGES_REQUESTED":
        return ("needs_attention", changes)

    # Check if ready to merge
    if pr.get("reviewDecision") == "APPROVED" and pr.get("ci_status") == "SUCCESS":
        return ("ready", changes)

    # Check if has meaningful changes
    if has_meaningful_changes(changes):
        return ("progress", changes)

    # Check if unchanged for a long time (>48 hours)
    first_seen = datetime.fromisoformat(history_entry["first_seen"].replace("Z", "+00:00"))
    waiting_hours = (datetime.now(first_seen.tzinfo) - first_seen).total_seconds() / 3600

    if waiting_hours > 48:
        return ("unchanged", {**changes, "waiting_hours": waiting_hours})

    # Otherwise ignore (don't show)
    return None


def update_history(
    prs: List[Dict[str, Any]],
    history: Dict[str, Any],
    repo: str
) -> Dict[str, Any]:
    """Update history with current PR states."""

    if "pr_history" not in history:
        history["pr_history"] = {}

    if repo not in history["pr_history"]:
        history["pr_history"][repo] = {}

    if "repo_last_check" not in history:
        history["repo_last_check"] = {}

    # Update last check time
    history["repo_last_check"][repo] = datetime.now().isoformat()

    pr_history = history["pr_history"][repo]
    now = datetime.now().isoformat()

    for pr in prs:
        pr_num = str(pr["number"])
        snapshot = extract_pr_snapshot(pr)

        if pr_num not in pr_history:
            # New PR
            pr_history[pr_num] = {
                "number": pr["number"],
                "title": pr["title"],
                "snapshot": snapshot,
                "first_seen": pr["createdAt"],
                "last_shown": now,
                "times_shown": 1,
                "last_changes": {}
            }
        else:
            # Existing PR - update
            entry = pr_history[pr_num]
            entry["snapshot"] = snapshot
            entry["last_shown"] = now
            entry["times_shown"] = entry.get("times_shown", 0) + 1

            # Update last_changes timestamps
            changes = detect_changes(pr, entry)
            if changes["ci_changed"]:
                entry["last_changes"]["ci_changed"] = now
            if changes["review_decision_changed"]:
                entry["last_changes"]["review_decision_changed"] = now
            if changes["new_approvals"]:
                entry["last_changes"]["new_approvals"] = now

    # Cleanup old history (>7 days)
    cleanup_old_history(history, repo)

    return history


def cleanup_old_history(history: Dict[str, Any], repo: str, days: int = 7):
    """Remove PRs that haven't been seen in >7 days or are closed/merged."""
    pr_history = history.get("pr_history", {}).get(repo, {})

    cutoff = datetime.now().timestamp() - (days * 24 * 3600)
    to_remove = []

    for pr_num, entry in pr_history.items():
        # Check if last shown was too long ago
        last_shown = datetime.fromisoformat(entry["last_shown"]).timestamp()
        if last_shown < cutoff:
            to_remove.append(pr_num)

    for pr_num in to_remove:
        del pr_history[pr_num]

    if to_remove:
        print(f"Cleaned up {len(to_remove)} old PR(s) from history", file=sys.stderr)


def main():
    parser = argparse.ArgumentParser(description="Compare PR states with historical data")
    parser.add_argument("--current", required=True, help="Current PRs JSON file (output from fetch_prs.py)")
    parser.add_argument("--history", default=".pr-reminder-state.json", help="Historical state file")
    parser.add_argument("--output", required=True, help="Output JSON file with categorized PRs")
    parser.add_argument("--update-history", action="store_true", help="Update and save the history file")

    args = parser.parse_args()

    # Load current PRs
    with open(args.current, "r", encoding="utf-8") as f:
        current_data = json.load(f)

    prs = current_data["prs"]
    repo = current_data["repo"]

    # Load historical state
    history = load_state_file(args.history)

    # Categorize all PRs
    categorized = {
        "new": [],
        "progress": [],
        "unchanged": [],
        "needs_attention": [],
        "ready": [],
        "ignored": []
    }

    changes_by_pr = {}

    for pr in prs:
        result = categorize_pr(pr, history, repo)
        if result:
            category, changes = result
            categorized[category].append(pr)
            changes_by_pr[str(pr["number"])] = changes
        else:
            categorized["ignored"].append(pr)

    # Update history if requested
    if args.update_history:
        history = update_history(prs, history, repo)
        with open(args.history, "w", encoding="utf-8") as f:
            json.dump(history, f, indent=2, ensure_ascii=False)
        print(f"Updated history file: {args.history}", file=sys.stderr)

    # Prepare output
    output = {
        "repo": repo,
        "generated_at": datetime.now().isoformat(),
        "categories": {
            k: [str(p["number"]) for p in v]
            for k, v in categorized.items()
        },
        "changes": changes_by_pr,
        "summary": {
            k: len(v)
            for k, v in categorized.items()
        }
    }

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    # Print summary
    print(f"Categorized {len(prs)} PR(s) from {repo}", file=sys.stderr)
    for category, count in output["summary"].items():
        if count > 0 and category != "ignored":
            print(f"  {category}: {count}", file=sys.stderr)


if __name__ == "__main__":
    main()
