---
name: pr-reminder
description: GitHub PR 状态监控与智能提醒工具，用于生成群聊友好的 PR 进展报告。在以下场景使用此 skill：需要定期检查 PR 状态、提醒贡献者处理审核意见或 CI 失败、提醒管理员合并已通过的 PR、生成团队 PR 进展日报、查看哪些 PR 长时间未处理。特别适合在团队群聊中分享 PR 状态，支持增量展示（区分新增/有变化/无变化的 PR）并包含鼓励性评价和改进建议。
compatibility: Requires GitHub CLI (gh) to be installed and authenticated
---

# PR Reminder - 智能 PR 状态监控与提醒

本 skill 帮你快速生成群聊友好的 PR 状态报告。它会自动获取 PR 数据、计算质量评分、对比历史变化，并输出格式化的报告。

## 使用方式

当用户要求生成 PR 状态报告时，按以下步骤执行：

### 1. 确定仓库
- 如果用户指定了仓库（如 "AgenticAIPlan/AgenticAISkills"），使用该仓库
- 如果未指定，使用当前 git 仓库（`git remote -v` 检测）

### 2. 执行完整流程

按顺序执行以下三个脚本，然后输出报告：

```bash
# 步骤 1: 获取 PR 数据（含评分）
python3 <skill-path>/scripts/fetch_prs.py --repo <仓库> --output /tmp/prs-$$-data.json

# 步骤 2: 对比历史状态
python3 <skill-path>/scripts/compare_states.py \
  --current /tmp/prs-$$-data.json \
  --history .pr-reminder-state.json \
  --output /tmp/prs-$$-changes.json \
  --update-history

# 步骤 3: 生成最终报告
python3 <skill-path>/scripts/format_report.py \
  --prs /tmp/prs-$$-data.json \
  --changes /tmp/prs-$$-changes.json \
  --output /tmp/prs-$$-report.md

# 步骤 4: 输出报告内容
cat /tmp/prs-$$-report.md

# 步骤 5: 清理临时文件
rm -f /tmp/prs-$$-*
```

**重要**：
- 使用 `$$` 确保临时文件唯一性，避免并发冲突
- 必须执行 `--update-history` 来保存状态供下次对比
- **最终输出必须是 Markdown 报告的内容**，直接用 `cat` 显示
- 不要只输出文件路径，要输出文件内容

## 输出格式说明

生成的报告会包含以下部分（按优先级排序）：

1. **✨ 新增待审核** - 首次出现的 PR，完整展示
2. **📌 待处理更新** → **✅ 有进展** - 有状态变化的 PR，高亮变化点
3. **⚠️ 需要作者关注** - CI 失败或有 review 建议的 PR
4. **🎉 已就绪待合并** - 已通过审核的 PR
5. **📊 今日统计** - 底部统计汇总

每个 PR 包含：
- 质量评分（0-100分，带 emoji 等级：🏆⭐👍💪）
- 作者和创建时间
- 代码变更规模（+行数/-行数，文件数）
- CI 状态
- 审核状态
- 鼓励性评语
- GitHub 链接

## PR 质量评分标准

- **CI 状态** (30分): SUCCESS=30, PENDING=15, FAILURE=0
- **代码规模** (20分): 200-800行最佳，过小或过大扣分
- **修改聚焦** (15分): 文件数越少分数越高
- **审核情况** (15分): approvals 越多分数越高
- **文档完整** (10分): 有描述+标签
- **时效性** (10分): 越新分数越高

## 特殊处理

### 过滤条件
- 超过 48 小时无变化的 PR 自动隐藏
- 无变化的 PR 使用最简洁展示
- 支持只显示特定状态的 PR（如 "只看 CI 失败的 PR"）

### 状态持久化
- 使用 `.pr-reminder-state.json` 保存历史
- 首次运行自动创建
- 每次运行自动更新
- 自动清理 7 天前的历史

## 示例输出

```
🔄 PR 状态日报 | 2025-04-16 15:18 | owner/repo

✨ PR #46: feat: add international-lead-research skill ⭐ 77/100
👤 作者: @VioYau
⏱️ 创建: 3天前
📊 变更: +345/-0 (1个文件)
🔧 CI: ✅ 通过
👥 等待审核
💬 👍
🔗 https://github.com/owner/repo/pull/46

━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 今日统计
━━━━━━━━━━━━━━━━━━━━━━━━━━━
• 总活跃 PR: 27 个
• 新增: 27 | 有进展: 0 | 无变化: 0 | 待处理: 0 | 就绪: 0

💪 团队给力！继续保持这个节奏 🚀
```

## 脚本说明

- `fetch_prs.py`: 获取 PR 数据并计算质量评分
- `compare_states.py`: 对比历史状态，识别变化
- `format_report.py`: 生成群聊友好的 Markdown 报告

所有脚本都支持 `--help` 查看详细用法。
