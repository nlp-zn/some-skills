#!/usr/bin/env python3
"""
Generate group chat friendly PR status report.
"""
import argparse
import json
import sys
from datetime import datetime
from typing import Any, Dict, List


def load_json(filepath: str) -> Any:
    """Load JSON file."""
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def format_duration(timestamp: str) -> str:
    """Format timestamp as human-readable duration."""
    dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
    now = datetime.now(dt.tzinfo)
    diff = now - dt

    hours = diff.total_seconds() / 3600

    if hours < 1:
        return f"{int(diff.total_seconds() / 60)}分钟前"
    elif hours < 24:
        return f"{int(hours)}小时前"
    else:
        days = int(hours / 24)
        return f"{days}天前"


def format_waiting_hours(created_at: str) -> str:
    """Format waiting time since PR creation."""
    dt = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
    now = datetime.now(dt.tzinfo)
    hours = (now - dt).total_seconds() / 3600

    if hours < 24:
        return f"{int(hours)}小时"
    else:
        return f"{int(hours / 24)}天"


def get_ci_emoji(ci_status: str) -> str:
    """Get emoji for CI status."""
    emojis = {
        "SUCCESS": "✅",
        "FAILURE": "❌",
        "PENDING": "⏳",
        "RUNNING": "🔄",
        None: "⚪"
    }
    return emojis.get(ci_status, "❓")


def format_pr_entry(
    pr: Dict[str, Any],
    category: str,
    changes: Dict[str, Any] = None,
    advantages: List[str] = None,
    improvements: List[str] = None,
    encouragement: str = None,
    show_score: bool = True
) -> str:
    """Format a single PR entry."""

    lines = []

    # Header
    emoji_map = {
        "new": "✨",
        "progress": "✅",
        "unchanged": "📌",
        "needs_attention": "⚠️",
        "ready": "🎉"
    }
    emoji = emoji_map.get(category, "📦")

    # Quality score display
    score = pr.get("quality_score", 0)
    score_emoji = ""
    if score >= 80:
        score_emoji = "🏆"
    elif score >= 60:
        score_emoji = "⭐"
    elif score >= 40:
        score_emoji = "👍"
    else:
        score_emoji = "💪"

    if show_score:
        lines.append(f"{emoji} PR #{pr['number']}: {pr['title']} {score_emoji} {score:.0f}/100")
    else:
        lines.append(f"{emoji} PR #{pr['number']}: {pr['title']}")

    # Basic info
    author = pr["author"]["login"]

    # Status line (combines waiting + review status)
    ci_status = pr.get("ci_status")
    review_decision = pr.get("reviewDecision")

    # Determine who needs to act
    if ci_status == "FAILURE" or review_decision == "CHANGES_REQUESTED":
        # Contributor needs to fix
        lines.append(f"👤 @{author} | ⏳ 等待贡献者修改")
    elif review_decision == "APPROVED" and ci_status == "SUCCESS":
        # Admin needs to merge
        lines.append(f"👤 @{author} | ⏳ 等待管理员合并")
    else:
        # Waiting for review
        lines.append(f"👤 @{author} | ⏳ 等待审核中")

    # Show skill-specific advantages and improvements (immediately after author)
    pr_advantages = pr.get("advantages", [])
    pr_improvements = pr.get("improvements", [])

    if pr_advantages:
        lines.append(f"✨ {pr_advantages[0]}")
        if len(pr_advantages) > 1:
            lines.append(f"✨ {pr_advantages[1]}")

    if pr_improvements:
        lines.append(f"🔧 {pr_improvements[0]}")
        if len(pr_improvements) > 1:
            lines.append(f"🔧 {pr_improvements[1]}")

    # Highlight changes for progress category
    if category == "progress" and changes:
        if changes.get("ci_changed"):
            lines.append(f"✅ CI 从失败变为通过 ✨")
        if changes.get("new_approvals"):
            lines.append(f"✅ 收到新 approval 🎉")

    # Link
    lines.append(f"🔗 {pr['url']}")

    return "\n".join(lines)


def format_section(title: str, prs: List[Dict[str, Any]], **kwargs) -> str:
    """Format a section with multiple PRs."""
    if not prs:
        return ""

    separator = "━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    lines = [
        separator,
        f"{title}",
        separator,
        ""
    ]

    for i, pr in enumerate(prs):
        lines.append(format_pr_entry(pr, **kwargs))

        # Add separator between PRs (except last)
        if i < len(prs) - 1:
            lines.append("")
            lines.append("─────────────────────────────")
            lines.append("")

    lines.append("")  # Empty line after section

    return "\n".join(lines)


def format_statistics(summary: Dict[str, int]) -> str:
    """Format statistics section."""
    separator = "━━━━━━━━━━━━━━━━━━━━━━━━━━━"

    active_count = (
        summary.get("new", 0) +
        summary.get("progress", 0) +
        summary.get("unchanged", 0) +
        summary.get("needs_attention", 0) +
        summary.get("ready", 0)
    )

    lines = [
        separator,
        "📊 今日统计",
        separator,
        f"• 总活跃 PR: {active_count} 个",
        f"• 新增: {summary.get('new', 0)} | 有进展: {summary.get('progress', 0)} | 无变化: {summary.get('unchanged', 0)} | 待处理: {summary.get('needs_attention', 0)} | 就绪: {summary.get('ready', 0)}",
        ""
    ]

    # Calculate average waiting time
    # (Would need PR data to calculate this)

    # Encouraging closing
    if active_count > 0:
        lines.append("💪 团队给力！继续保持这个节奏 🚀")

    return "\n".join(lines)


def generate_report(
    prs_json: str,
    changes_json: str,
    history_json: str = None
) -> str:
    """Generate complete PR status report."""

    # Load data
    prs_data = load_json(prs_json)
    changes_data = load_json(changes_json)

    prs = {str(p["number"]): p for p in prs_data["prs"]}
    categories = changes_data["categories"]
    changes = changes_data["changes"]
    summary = changes_data["summary"]
    repo = prs_data["repo"]

    # Build report
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    lines = [
        f"🔄 PR 状态日报 | {now} | {repo}",
        "",
        ""
    ]

    # Sections in priority order
    section_order = [
        ("new", "✨ 新增待审核"),
        ("progress", "📌 待处理更新"),
        ("unchanged", "⏸️ 暂无变化"),
        ("needs_attention", "⚠️ 需要作者关注"),
        ("ready", "✅ 已就绪待合并")
    ]

    for category_key, section_title in section_order:
        pr_numbers = categories.get(category_key, [])

        if not pr_numbers:
            continue

        # For progress category, split into "has progress" and "unchanged" subsections
        if category_key == "progress":
            separator = "━━━━━━━━━━━━━━━━━━━━━━━━━━━"
            lines.append(separator)
            lines.append(section_title)
            lines.append(separator)
            lines.append("")

            # Add subsections
            has_progress_count = len(pr_numbers)
            lines.append(f"✅ 有进展 ({has_progress_count})")
            lines.append("")

            for pr_num in pr_numbers:
                pr = prs[pr_num]
                pr_changes = changes.get(pr_num, {})
                lines.append(format_pr_entry(pr, category_key, pr_changes))
                lines.append("")
                lines.append("─────────────────────────────")
                lines.append("")

            continue

        # For other categories, just list PRs
        category_prs = [prs[num] for num in pr_numbers]

        for pr_num in pr_numbers:
            pr = prs[pr_num]
            pr_changes = changes.get(pr_num, {})

            # Analyze PR for encouragement
            # (In real implementation, would call analyze_pr.analyze_pr_quality)
            advantages = []
            improvements = []
            encouragement = "👍"  # Default

            lines.append(format_pr_entry(
                pr,
                category_key,
                pr_changes,
                advantages,
                improvements,
                encouragement
            ))
            lines.append("")
            lines.append("─────────────────────────────")
            lines.append("")

    # Add statistics
    lines.append(format_statistics(summary))

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Generate PR status report")
    parser.add_argument("--prs", required=True, help="PRs JSON file (from fetch_prs.py)")
    parser.add_argument("--changes", required=True, help="Changes JSON file (from compare_states.py)")
    parser.add_argument("--history", help="Historical state file (for additional context)")
    parser.add_argument("--output", default="report.md", help="Output markdown file")
    parser.add_argument("--print", action="store_true", help="Print report to stdout")

    args = parser.parse_args()

    # Generate report
    report = generate_report(args.prs, args.changes, args.history)

    # Save report
    with open(args.output, "w", encoding="utf-8") as f:
        f.write(report)

    print(f"Report saved to {args.output}", file=sys.stderr)

    if args.print:
        print("\n" + "="*50 + "\n")
        print(report)


if __name__ == "__main__":
    main()
