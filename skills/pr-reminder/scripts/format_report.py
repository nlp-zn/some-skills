#!/usr/bin/env python3
"""
Generate a full open-PR leaderboard report for AgenticAISkills.
"""
import argparse
import json
import sys
from datetime import datetime
from typing import Any, Dict, List


def load_json(filepath: str) -> Any:
    """Load JSON data from a file."""
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def parse_time(timestamp: str) -> datetime:
    """Parse GitHub timestamps."""
    return datetime.fromisoformat(timestamp.replace("Z", "+00:00"))


def format_duration(timestamp: str) -> str:
    """Format timestamp as human-readable duration."""
    dt = parse_time(timestamp)
    now = datetime.now(dt.tzinfo)
    diff = now - dt
    hours = diff.total_seconds() / 3600

    if hours < 1:
        return f"{int(diff.total_seconds() / 60)}分钟前"
    if hours < 24:
        return f"{int(hours)}小时前"
    return f"{int(hours / 24)}天前"


def get_score_emoji(score: float) -> str:
    """Map a numeric quality score to a badge."""
    if score >= 80:
        return "🏆"
    if score >= 60:
        return "⭐"
    if score >= 40:
        return "👍"
    return "💪"


def get_ci_summary(pr: Dict[str, Any]) -> str:
    """Return a concise CI summary."""
    ci_status = pr.get("ci_status")
    mapping = {
        "SUCCESS": "✅ 通过",
        "FAILURE": "❌ 失败",
        "PENDING": "⏳ 进行中",
        None: "⚪ 未配置"
    }
    return mapping.get(ci_status, "❓ 未知")


def get_review_summary(pr: Dict[str, Any]) -> str:
    """Return a concise review summary."""
    review_decision = pr.get("reviewDecision")
    latest_reviews = pr.get("latestReviews", [])
    approvals = sum(1 for review in latest_reviews if review.get("state") == "APPROVED")
    requested = len(pr.get("reviewRequests", []))

    if review_decision == "CHANGES_REQUESTED":
        return "请求修改"
    if review_decision == "APPROVED":
        return f"已批准 {max(approvals, 1)} 人"
    if approvals > 0:
        return f"已批准 {approvals} 人"
    if requested > 0:
        return f"已请求 {requested} 位 reviewer"
    return "待分配 reviewer"


def get_action_status(pr: Dict[str, Any]) -> str:
    """Return the main workflow status for the PR."""
    ci_status = pr.get("ci_status")
    review_decision = pr.get("reviewDecision")
    has_reviewers = bool(pr.get("reviewRequests")) or bool(pr.get("latestReviews"))

    if pr.get("isDraft", False):
        return "Draft，待作者完善"
    if ci_status == "FAILURE" or review_decision == "CHANGES_REQUESTED":
        return "等待贡献者修改"
    if review_decision == "APPROVED" and ci_status == "SUCCESS":
        return "等待管理员合并"
    if not has_reviewers:
        return "待分配 reviewer"
    return "等待审核中"


def build_summary(prs: List[Dict[str, Any]]) -> Dict[str, int]:
    """Aggregate high-level report counts."""
    summary = {
        "total_open": len(prs),
        "awaiting_review": 0,
        "needs_author": 0,
        "ready_to_merge": 0,
        "draft": 0,
        "ci_success": 0,
        "ci_pending": 0,
        "ci_failure": 0,
        "ci_unknown": 0,
    }

    for pr in prs:
        ci_status = pr.get("ci_status")
        review_decision = pr.get("reviewDecision")

        if pr.get("isDraft", False):
            summary["draft"] += 1
        elif ci_status == "FAILURE" or review_decision == "CHANGES_REQUESTED":
            summary["needs_author"] += 1
        elif review_decision == "APPROVED" and ci_status == "SUCCESS":
            summary["ready_to_merge"] += 1
        else:
            summary["awaiting_review"] += 1

        if ci_status == "SUCCESS":
            summary["ci_success"] += 1
        elif ci_status == "PENDING":
            summary["ci_pending"] += 1
        elif ci_status == "FAILURE":
            summary["ci_failure"] += 1
        else:
            summary["ci_unknown"] += 1

    return summary


def sort_prs(prs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Sort PRs by quality score, then by recency."""
    return sorted(
        prs,
        key=lambda pr: (pr.get("quality_score", 0), pr.get("createdAt", "")),
        reverse=True,
    )


def format_pr_entry(pr: Dict[str, Any]) -> str:
    """Format a single PR entry in the leaderboard."""
    score = pr.get("quality_score", 0.0)
    score_emoji = get_score_emoji(score)
    additions = pr.get("additions", 0)
    deletions = pr.get("deletions", 0)
    changed_files = pr.get("changedFiles", 0)

    lines = [
        f"PR #{pr['number']}: {pr['title']} {score_emoji} {score:.0f}/100",
        f"👤 @{pr['author']['login']} | ⏱️ 创建 {format_duration(pr['createdAt'])} | 🧭 {get_action_status(pr)}",
        f"📊 变更: +{additions}/-{deletions} | {changed_files} 个文件",
        f"🔧 CI: {get_ci_summary(pr)} | 👥 审核: {get_review_summary(pr)}",
    ]

    for advantage in pr.get("advantages", [])[:2]:
        lines.append(f"✨ {advantage}")

    for improvement in pr.get("improvements", [])[:2]:
        lines.append(f"🔧 {improvement}")

    lines.append(f"🔗 {pr['url']}")
    return "\n".join(lines)


def format_statistics(summary: Dict[str, int], shown: int) -> str:
    """Format the top-level summary section."""
    separator = "━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    total = summary["total_open"]
    hidden = max(total - shown, 0)
    lines = [
        separator,
        "📊 全量统计",
        separator,
        f"• 未合入 PR: {total} 个",
        f"• 展示范围: 质量 Top {shown}" if total else "• 展示范围: 无可展示 PR",
        f"• 等待审核: {summary['awaiting_review']} | 待作者处理: {summary['needs_author']} | 待合并: {summary['ready_to_merge']} | Draft: {summary['draft']}",
        f"• CI 通过: {summary['ci_success']} | CI 进行中: {summary['ci_pending']} | CI 失败: {summary['ci_failure']} | 无 CI: {summary['ci_unknown']}",
    ]

    if hidden > 0:
        lines.append(f"• 其余 {hidden} 个 PR 未展开，仍计入全量统计")

    return "\n".join(lines)


def generate_report(prs_json: str, top_n: int = 10) -> str:
    """Generate the final Markdown report."""
    prs_data = load_json(prs_json)
    repo = prs_data["repo"]
    prs = sort_prs(prs_data["prs"])
    summary = build_summary(prs)
    top_prs = prs[:top_n]
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    separator = "━━━━━━━━━━━━━━━━━━━━━━━━━━━"

    lines = [
        f"🔄 PR 全量巡检 | {now} | {repo}",
        "",
        format_statistics(summary, len(top_prs)),
        "",
        separator,
        f"🏆 质量 Top {len(top_prs)}",
        separator,
        "",
    ]

    if not top_prs:
        lines.append("当前没有未合入的 PR。")
    else:
        for index, pr in enumerate(top_prs, start=1):
            lines.append(f"{index}. {format_pr_entry(pr)}")
            if index < len(top_prs):
                lines.append("")
                lines.append("─────────────────────────────")
                lines.append("")

    if summary["total_open"] > 0:
        lines.extend([
            "",
            "💪 以上按质量分排序，方便优先看最值得推进的 PR。"
        ])

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Generate a full PR leaderboard report")
    parser.add_argument("--prs", required=True, help="PRs JSON file (from fetch_prs.py)")
    parser.add_argument("--output", default="report.md", help="Output markdown file")
    parser.add_argument("--top", type=int, default=10, help="Number of PRs to show in the leaderboard")
    parser.add_argument("--print", action="store_true", help="Print report to stdout")

    args = parser.parse_args()

    report = generate_report(args.prs, args.top)

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(report)

    print(f"Report saved to {args.output}", file=sys.stderr)

    if args.print:
        print("\n" + "=" * 50 + "\n")
        print(report)


if __name__ == "__main__":
    main()
