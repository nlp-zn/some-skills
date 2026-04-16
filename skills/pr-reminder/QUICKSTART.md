# PR Reminder Skill - 快速开始

## 5 分钟上手指南

### 步骤 1：安装（1 分钟）

```bash
cd pr-reminder
./install.sh
```

你会看到：
```
=== PR Reminder Skill 安装 ===
创建软链接...
✅ 安装成功！
```

### 步骤 2：验证（30 秒）

打开 Claude Code，输入：
```
请帮我生成今天的 PR 状态报告
```

### 步骤 3：查看报告（30 秒）

报告会包含：
- ✨ 新增的 PR（完整信息）
- ⭐ 有进展的 PR（高亮变化）
- 📌 持续等待的 PR（简洁提醒）
- ⚠️ 需要关注的 PR（改进建议）
- 🎉 就待合并的 PR（呼吁管理员）
- 📊 统计汇总

### 步骤 4：理解评分（2 分钟）

每个 PR 都有质量评分（0-100分）：

- 🏆 **80-100分**: 优秀 - 高质量 PR，值得优先审核
- ⭐ **60-79分**: 良好 - 质量不错，可以审核
- 👍 **40-59分**: 一般 - 基本达标，但有待改进
- 💪 **0-39分**: 需改进 - 建议优化后再提交

**评分标准**：
- CI 状态: 30分（通过=30，失败=0）
- 代码规模: 20分（200-800行最佳）
- 修改聚焦: 15分（文件数越少越高）
- 审核情况: 15分（approval越多越高）
- 文档完整: 10分（有描述+标签）
- 时效性: 10分（越新越高）

### 步骤 5：持续使用（10 秒）

每次想了解 PR 状态时，只需说：
```
检查一下 PR 状态
```

或
```
看看有哪些 PR 卡住了
```

## 高级用法

### 只看特定状态的 PR

```
有哪些 PR 已经通过审核了？
```
→ 只展示已 APPROVED 的 PR

```
PR 有没有失败的 CI？
```
→ 只展示 CI 失败的 PR

### 手动运行脚本

```bash
# 获取 PR 数据
python scripts/fetch_prs.py --repo owner/repo --output prs.json

# 对比状态
python scripts/compare_states.py --current prs.json --history .pr-reminder-state.json --output changes.json --update-history

# 生成报告
python scripts/format_report.py --prs prs.json --changes changes.json --output report.md
```

### 自定义配置

**修改评分权重**：编辑 `scripts/analyze_pr.py` 中的 `calculate_pr_score` 函数

**修改鼓励语**：编辑 `scripts/format_report.py` 中的 `encouragement_templates`

**调整分组规则**：编辑 `scripts/compare_states.py` 中的 `categorize_pr` 函数

## 常见问题

**Q: 首次运行会显示什么？**
A: 所有 PR 都会被标记为"新增"，并创建新的状态文件。

**Q: 如何避免刷屏？**
A: Skill 会自动过滤超过48小时无变化的 PR，且对无变化的 PR 使用最简洁的展示方式。

**Q: 支持多仓库吗？**
A: 支持！状态文件自动支持多个仓库，相互独立。

**Q: 如何只看高分 PR？**
A: PR 已经按质量分数从高到低排序，前面的就是高分 PR。

## 卸载

```bash
cd pr-reminder
./uninstall.sh
```

## 获取帮助

- 查看详细文档: [README.md](README.md)
- 评分系统说明: [references/scoring-system.md](references/scoring-system.md)
- GitHub CLI 参考: [references/gh-api-reference.md](references/gh-api-reference.md)
- 完成总结: [SUMMARY.md](SUMMARY.md)

## 示例输出

```
🔄 PR 状态日报 | 2025-04-16 15:18 | AgenticAIPlan/AgenticAISkills

✨ PR #46: feat: add international-lead-research skill ⭐ 77/100
👤 作者: @VioYau
⏱️ 创建: 3天前
📊 变更: +345/-0 (1个文件)
🔧 CI: ✅ 通过
👥 等待审核
💬 👍

✨ PR #57: feat: add wecom-group-invite skill ⭐ 75/100
👤 作者: @2867297362mjb-sketch
⏱️ 创建: 5小时前
📊 变更: +67/-0 (2个文件)
🔧 CI: ✅ 通过
👥 等待审核
💬 👍

━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 今日统计
━━━━━━━━━━━━━━━━━━━━━━━━━━━
• 总活跃 PR: 27 个
• 新增: 27 | 有进展: 0 | 无变化: 0 | 待处理: 0 | 就绪: 0

💪 团队给力！继续保持这个节奏 🚀
```

---

**开始使用 PR Reminder，让 PR 管理更高效！** 🚀
