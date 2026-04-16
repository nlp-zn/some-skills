#!/usr/bin/env python3
"""
Analyze PR quality and generate advantages/improvements summary.
"""
import argparse
import json
import sys
from datetime import datetime
from typing import Dict, List, Tuple, Any


def calculate_pr_score(pr: Dict[str, Any]) -> float:
    """
    Calculate PR quality score (0-100).

    Scoring criteria:
    - CI status: 30 points (SUCCESS=30, FAILURE=0, PENDING=15)
    - Code size: 20 points (reasonable size gets more points)
    - Focus: 15 points (fewer files is better)
    - Reviews: 15 points (more approvals is better)
    - Documentation: 10 points
    - Timeliness: 10 points (newer is better)

    Args:
        pr: PR object from gh CLI

    Returns:
        Score from 0 to 100
    """
    score = 0.0

    additions = pr.get("additions", 0)
    deletions = pr.get("deletions", 0)
    changed_files = pr.get("changedFiles", 0)
    ci_status = pr.get("ci_status")
    latest_reviews = pr.get("latestReviews", [])
    labels = [l["name"] for l in pr.get("labels", [])]
    created_at = datetime.fromisoformat(pr["createdAt"].replace("Z", "+00:00"))
    has_description = bool(pr.get("body", "").strip())
    days_old = (datetime.now(created_at.tzinfo) - created_at).days

    # CI status (30 points)
    if ci_status == "SUCCESS":
        score += 30
    elif ci_status == "PENDING":
        score += 15
    # FAILURE gets 0

    # Code size (20 points) - sweet spot 200-800 lines
    total_changes = additions + deletions
    if 200 <= total_changes <= 800:
        score += 20
    elif total_changes < 200:
        score += 15  # Small but ok
    elif total_changes <= 1500:
        score += 10  # Large but manageable
    else:
        score += 5   # Too large

    # Focus (15 points) - fewer files is better
    if changed_files <= 3:
        score += 15
    elif changed_files <= 5:
        score += 12
    elif changed_files <= 10:
        score += 8
    else:
        score += 4

    # Reviews (15 points) - more approvals is better
    approved_count = sum(1 for r in latest_reviews if r.get("state") == "APPROVED")
    if approved_count >= 2:
        score += 15
    elif approved_count == 1:
        score += 10
    # No reviews gets 0

    # Documentation (10 points)
    if has_description:
        score += 5
    if "documentation" in labels:
        score += 5

    # Timeliness (10 points) - newer is better
    if days_old <= 1:
        score += 10
    elif days_old <= 3:
        score += 7
    elif days_old <= 7:
        score += 4
    else:
        score += 2

    return min(score, 100.0)  # Cap at 100


def extract_skill_info(pr: Dict[str, Any]) -> Dict[str, str]:
    """
    Extract skill information from PR body.

    Returns:
        Dict with 'skill_name', 'business_scenario', 'skill_path' if found
    """
    body = pr.get("body", "")
    if not body:
        return {}

    skill_info = {}

    # Extract key information from PR body
    lines = body.split('\n')
    for line in lines:
        line = line.strip()
        if line.startswith("- Skill 名称:") or line.startswith("Skill 名称:"):
            skill_info['name'] = line.split(":", 1)[1].strip()
        elif line.startswith("- 业务场景:") or line.startswith("业务场景:"):
            skill_info['scenario'] = line.split(":", 1)[1].strip()
        elif line.startswith("- Skill 路径:") or line.startswith("Skill 路径:"):
            skill_info['path'] = line.split(":", 1)[1].strip()

    return skill_info


def generate_skill_advantages(pr: Dict[str, Any], skill_info: Dict[str, str]) -> List[str]:
    """
    Generate skill business value and user value advantages.
    """
    advantages = []

    # Get business scenario
    scenario = skill_info.get('scenario', '')
    skill_name = skill_info.get('name', '')

    if not scenario:
        # Generic advantages if no skill info
        advantages.append("实用型 skill，解决实际问题")
        return advantages

    # Analyze business scenario and extract value propositions
    scenario_lower = scenario.lower()

    # Value Proposition 1: Core capability
    if "自动化" in scenario or "自动" in scenario:
        advantages.append("自动化重复性工作，解放人力专注高价值活动")
    elif "分析" in scenario or "调研" in scenario:
        advantages.append("数据驱动决策，提供深度洞察和情报支持")
    elif "生成" in scenario or "创作" in scenario or "写作" in scenario:
        advantages.append("AI 辅助创作，大幅提升内容生产效率")
    elif "管理" in scenario or "协作" in scenario:
        advantages.append("优化团队协作流程，降低沟通成本")
    elif "对话" in scenario or "客服" in scenario or "回复" in scenario:
        advantages.append("7x24小时智能响应，即时服务用户")
    elif "推荐" in scenario or "搜索" in scenario:
        advantages.append("精准匹配需求，提升发现效率")
    elif "文档" in scenario or "整理" in scenario:
        advantages.append("结构化知识管理，快速定位关键信息")
    else:
        advantages.append("场景化 AI 能力，直接赋能业务")

    # Value Proposition 2: User benefit
    if "企业" in scenario or "b端" in scenario:
        advantages.append("面向企业场景，助力业务数字化转型")
    elif "社群" in scenario or "用户" in scenario:
        advantages.append("提升用户服务体验，增强满意度")
    elif "效率" in scenario or "快速" in scenario:
        advantages.append("显著提升操作效率，节省时间成本")
    elif "质量" in scenario:
        advantages.append("标准化输出质量，降低人为误差")

    # If only one advantage, add a second one
    if len(advantages) == 1:
        advantages.append("即插即用，快速集成到现有工作流")

    return advantages[:2]  # Max 2 advantages


def generate_skill_improvements(pr: Dict[str, Any], skill_info: Dict[str, str]) -> List[str]:
    """
    Generate skill improvement suggestions from user/business perspective.
    """
    improvements = []

    ci_status = pr.get("ci_status")
    review_decision = pr.get("reviewDecision")
    additions = pr.get("additions", 0)
    changed_files = pr.get("changedFiles", 0)

    # Calculate age with proper timezone handling
    created_at = datetime.fromisoformat(pr["createdAt"].replace("Z", "+00:00"))
    if created_at.tzinfo is None:
        created_at = created_at.replace(tzinfo=None)
        days_old = (datetime.now() - created_at).days
    else:
        days_old = (datetime.now(created_at.tzinfo) - created_at).days

    # Priority 1: CI failures (blocks user usage)
    if ci_status == "FAILURE":
        improvements.append("需修复 CI 方可正常使用")

    # Priority 2: Review feedback (blocks PR merge)
    if review_decision == "CHANGES_REQUESTED":
        improvements.append("处理 review 建议后即可合并上线")

    # Priority 3: Completeness issues
    scenario = skill_info.get('scenario', '')
    if scenario and len(scenario) < 30:
        improvements.append("建议补充业务场景说明，明确使用价值")

    # Priority 4: Complexity affecting usability
    if changed_files > 10:
        improvements.append("功能较复杂，建议补充使用示例")

    # Priority 5: Stale PR
    if days_old > 7:
        improvements.append(f"等待 {days_old} 天，需跟进推进")

    # Priority 6: Missing reviewers
    if not pr.get("reviewRequests") and review_decision == "REVIEW_REQUIRED":
        improvements.append("建议请求 reviewer 加快审核")

    return improvements[:2]  # Max 2 improvements


def analyze_pr_quality(pr: Dict[str, Any]) -> Tuple[List[str], List[str]]:
    """
    Analyze PR and return (advantages, improvements).

    Args:
        pr: PR object from gh CLI

    Returns:
        Tuple of (advantages list, improvements list)
    """
    advantages = []
    improvements = []

    additions = pr.get("additions", 0)
    deletions = pr.get("deletions", 0)
    changed_files = pr.get("changedFiles", 0)
    ci_status = pr.get("ci_status")
    review_decision = pr.get("reviewDecision")
    latest_reviews = pr.get("latestReviews", [])
    labels = [l["name"] for l in pr.get("labels", [])]
    created_at = datetime.fromisoformat(pr["createdAt"].replace("Z", "+00:00"))
    has_description = bool(pr.get("body", "").strip())
    reviewers_requested = pr.get("reviewRequests", [])

    # ===== Check advantages =====

    # Reasonable code additions (not over-engineering)
    total_changes = additions + deletions
    if total_changes > 0 and deletions / total_changes < 0.3:
        advantages.append("代码增量合理，避免过度工程化")

    # Focused change scope
    if changed_files <= 5:
        advantages.append("修改范围聚焦，易于审查")

    # CI passing
    if ci_status == "SUCCESS":
        advantages.append("CI 全部通过，质量保证到位")

    # Good collaboration (multiple reviews)
    approved_count = sum(1 for r in latest_reviews if r.get("state") == "APPROVED")
    if approved_count >= 2:
        advantages.append(f"收到 {approved_count} 次 review，团队协作良好")

    # Manageable PR size
    if additions < 300:
        advantages.append("PR 规模适中，快速合并潜力高")

    # Includes documentation
    if "documentation" in labels:
        advantages.append("包含文档更新，维护性好")

    # Has descriptive title/body
    if has_description and len(pr.get("body", "")) > 50:
        advantages.append("PR 描述详细，变更说明清晰")

    # Draft status (shows careful preparation)
    if not pr.get("isDraft", False):
        advantages.append("标记为 ready，准备充分")

    # ===== Check improvements =====

    # CI failure
    if ci_status == "FAILURE":
        improvements.append("CI 检查失败需要修复")

    # Changes requested
    if review_decision == "CHANGES_REQUESTED":
        improvements.append("有 review 建议待处理")

    # Too many files
    if changed_files > 10:
        improvements.append("建议拆分成多个小 PR，便于审查")

    # Long time open
    days_open = (datetime.now(created_at.tzinfo) - created_at).days
    if days_open > 7:
        improvements.append(f"PR 已开放 {days_open} 天，考虑是否仍需要")

    # Missing description
    if not has_description:
        improvements.append("建议补充 PR 描述说明变更原因")

    # No reviewers requested
    if len(reviewers_requested) == 0 and review_decision not in ("APPROVED", "CHANGES_REQUESTED"):
        improvements.append("建议主动请求 reviewer")

    # Large PR
    if additions > 500:
        improvements.append("PR 规模较大，考虑是否可以拆分")

    # No reviews yet
    if not latest_reviews and days_open > 1:
        improvements.append("尚未收到 review，可以在群里提醒一下")

    return advantages, improvements


def generate_encouragement(category: str, pr: Dict[str, Any]) -> str:
    """Generate encouraging message based on PR category and state."""

    # Calculate waiting time
    created_at = datetime.fromisoformat(pr["createdAt"].replace("Z", "+00:00"))
    hours_open = (datetime.now(created_at.tzinfo) - created_at).total_seconds() / 3600

    encouragements = {
        "new": [
            "🌟 新 PR 来了！感谢贡献～",
            "💡 不错的想法，期待这个功能！",
            "👏 欢迎新贡献！"
        ],
        "progress": [
            "🎉 太棒了！有明显进展",
            "✨ 稳步推进，继续保持",
            "🚀 离合并又近了一步"
        ],
        "unchanged": [
            "💪 稍安勿躁，好 PR 值得等待",
            "⏳ reviewer 们正在路上",
            "🙏 耐心等待，质量第一"
        ],
        "needs_attention": [
            "💪 加油！处理一下就能合并了",
            "🔧 小修小补，马上就好",
            "🤝 有建议很正常，迭代改进就好"
        ],
        "ready": [
            "🌟 就绪！可以考虑合并啦",
            "✅ 完美！等待管理员合并",
            "🎊 恭喜通过审核！"
        ]
    }

    # Get appropriate messages
    messages = encouragements.get(category, encouragements["progress"])

    # Add context-specific messages
    if hours_open > 48:
        messages = [
            "🙏 感谢耐心等待，好饭不怕晚",
            "⏰ 重要的 PR 值得时间打磨",
            "💫 坚持！这个改进很有价值"
        ]

    # Return first message (could randomize in future)
    return messages[0]


def format_pr_summary(pr: Dict[str, Any], advantages: List[str], improvements: List[str], encouragement: str) -> str:
    """Format a text summary of PR analysis."""
    lines = [
        f"PR #{pr['number']}: {pr['title']}",
        f"鼓励: {encouragement}"
    ]

    if advantages:
        lines.append("优势:")
        for adv in advantages:
            lines.append(f"  • {adv}")

    if improvements:
        lines.append("改进建议:")
        for imp in improvements:
            lines.append(f"  • {imp}")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Analyze PR quality")
    parser.add_argument("--pr-number", type=int, required=True, help="PR number")
    parser.add_argument("--repo", help="Repository (owner/repo)")
    parser.add_argument("--prs-json", help="Path to PRs JSON file (alternative to pr-number)")
    parser.add_argument("--output", help="Output file (default: stdout)")

    args = parser.parse_args()

    # Load PR data
    if args.prs_json:
        with open(args.prs_json, "r", encoding="utf-8") as f:
            data = json.load(f)
            prs = data["prs"]
            pr = next((p for p in prs if p["number"] == args.pr_number), None)
            if not pr:
                print(f"PR #{args.pr_number} not found in {args.prs_json}", file=sys.stderr)
                sys.exit(1)
    else:
        # Would need to fetch from gh CLI - not implemented
        print("Error: Please provide --prs-json for now", file=sys.stderr)
        sys.exit(1)

    # Analyze
    advantages, improvements = analyze_pr_quality(pr)

    # Get category for encouragement (infer from PR state)
    if pr.get("reviewDecision") == "APPROVED" and pr.get("ci_status") == "SUCCESS":
        category = "ready"
    elif pr.get("ci_status") == "FAILURE" or pr.get("reviewDecision") == "CHANGES_REQUESTED":
        category = "needs_attention"
    else:
        category = "progress"

    encouragement = generate_encouragement(category, pr)

    # Prepare output
    result = {
        "pr_number": pr["number"],
        "title": pr["title"],
        "category": category,
        "advantages": advantages,
        "improvements": improvements,
        "encouragement": encouragement
    }

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print(f"Saved analysis to {args.output}", file=sys.stderr)
    else:
        print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
