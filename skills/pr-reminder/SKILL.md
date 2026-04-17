---
name: pr-reminder
description: 固定监控 GitHub 仓库 AgenticAIPlan/AgenticAISkills 的未合入 PR，并生成群聊友好的质量排行榜报告。在以下场景使用此 skill：需要查看当前所有 open PR、按质量分排序筛出最值得优先推进的 PR、提醒贡献者处理 CI 或 review 问题、快速了解仓库当前合并阻塞点。
compatibility: Requires GitHub CLI (gh) to be installed and authenticated
---

# PR Reminder - AgenticAISkills PR 全量巡检

本 skill 固定查看 `AgenticAIPlan/AgenticAISkills` 的未合入 PR。它会自动获取当前 open PR、计算质量评分，并输出全量统计 + 质量 Top 10 的 Markdown 报告。

## 使用方式

当用户要求生成 PR 状态报告时，按以下步骤执行：

### 1. 固定仓库
- 始终查看 `AgenticAIPlan/AgenticAISkills`
- 不需要根据当前 git 仓库自动检测
- 不需要让用户额外指定 repo，除非明确要求调试别的仓库

### 2. 执行完整流程

按顺序执行以下两个脚本，然后输出报告：

```bash
# 步骤 1: 获取 PR 数据（含评分）
python3 <skill-path>/scripts/fetch_prs.py \
  --output /tmp/prs-$$-data.json

# 步骤 2: 生成最终报告（全量统计 + Top 10）
python3 <skill-path>/scripts/format_report.py \
  --prs /tmp/prs-$$-data.json \
  --top 10 \
  --output /tmp/prs-$$-report.md

# 步骤 3: 输出报告内容
cat /tmp/prs-$$-report.md

# 步骤 4: 清理临时文件
rm -f /tmp/prs-$$-*
```

**重要**：
- 使用 `$$` 确保临时文件唯一性，避免并发冲突
- **最终输出必须是 Markdown 报告的内容**，直接用 `cat` 显示
- 不要只输出文件路径，要输出文件内容
- 当前版本**不做每日增量变化对比**

## 输出格式说明

生成的报告会包含以下部分（按优先级排序）：

1. **📊 全量统计** - 当前所有未合入 PR 的整体概览
2. **🏆 质量 Top 10** - 按质量分排序展示最值得优先推进的 PR

每个 PR 包含：
- 质量评分（0-100分，带 emoji 等级：🏆⭐👍💪）
- 作者、创建时间、当前流程状态
- 代码变更规模（+行数/-行数，文件数）
- CI 状态与审核状态
- 业务价值亮点和改进建议
- GitHub 链接

## PR 质量评分标准

- **CI 状态** (30分): SUCCESS=30, PENDING=15, FAILURE=0
- **代码规模** (20分): 200-800行最佳，过小或过大扣分
- **修改聚焦** (15分): 文件数越少分数越高
- **审核情况** (15分): approvals 越多分数越高
- **文档完整** (10分): 有描述+标签
- **时效性** (10分): 越新分数越高

## 特殊处理

### 报告策略
- 始终看全量 open PR，不做历史增量过滤
- 统计覆盖全部未合入 PR，但正文只展开质量 Top 10
- 适合在群里快速同步“现在最值得推进的 10 个 PR”

### reviewer 建议
- 不会再对刚创建、仍在正常等待审核的 PR 立刻提示“请求 reviewer”
- 只有 PR 已经闲置一段时间、没有 reviewer request、也没有 review 记录时，才会给出该建议

## 示例输出

```
🔄 PR 全量巡检 | 2025-04-16 15:18 | AgenticAIPlan/AgenticAISkills

━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 全量统计
━━━━━━━━━━━━━━━━━━━━━━━━━━━
• 未合入 PR: 33 个
• 展示范围: 质量 Top 10
• 等待审核: 18 | 待作者处理: 12 | 待合并: 2 | Draft: 1

━━━━━━━━━━━━━━━━━━━━━━━━━━━
🏆 质量 Top 10
━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. PR #64: feat(skill): add ernie-image-monitor 舆情监测业务 Skill ⭐ 77/100
👤 @wanghuanai273-byte | ⏱️ 创建 1天前 | 🧭 等待审核中
📊 变更: +220/-18 | 4 个文件
🔧 CI: ✅ 通过 | 👥 审核: 已请求 2 位 reviewer
✨ 数据驱动决策，提供深度洞察和情报支持
🔗 https://github.com/AgenticAIPlan/AgenticAISkills/pull/64
```

## 脚本说明

- `fetch_prs.py`: 获取 PR 数据并计算质量评分
- `format_report.py`: 生成群聊友好的全量排行榜 Markdown 报告

所有脚本都支持 `--help` 查看详细用法。
