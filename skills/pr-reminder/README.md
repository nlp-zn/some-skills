# PR Reminder - 智能 PR 状态监控与提醒

一个帮助你监控 GitHub PR 状态变化，并生成适合在群聊中分享的友好报告的 skill。

## 功能特性

- ✅ **多维度状态检查**：检查 review 状态、CI 检查、更新时间、标签等
- ✅ **智能变化感知**：对比历史记录，自动识别新增、有进展、无变化的 PR
- ✅ **差异化展示**：新增 PR 完整介绍、有变化 PR 高亮进展、无变化 PR 简洁提醒
- ✅ **PR 质量评分**：基于 CI、代码规模、聚焦度、审核情况等维度打分（0-100分）
- ✅ **智能排序**：高质量 PR 优先展示，帮助识别值得优先审核的 PR
- ✅ **PR 质量分析**：自动分析代码规模、CI 状态、review 情况，给出优势总结和改进建议
- ✅ **鼓励性反馈**：使用积极正向的语言，肯定贡献者的努力
- ✅ **频次控制**：跨会话记录历史，避免重复展示相同内容

## 安装

### 方法 1：使用 .skill 文件（推荐）

```bash
# 复制 skill 文件到 skills 目录
cp pr-reminder.skill ~/.claude/skills/

# 或者创建软链接
ln -s $(pwd)/pr-reminder ~/.claude/skills/pr-reminder
```

### 方法 2：直接使用目录

```bash
# 创建软链接到 skill 目录
ln -s $(pwd)/pr-reminder ~/.claude/skills/pr-reminder
```

## 前置要求

- 安装 GitHub CLI (gh)
- 已完成 gh 认证 (`gh auth login`)
- Python 3.7+

## 使用方法

### 基本用法

在 Claude Code 中使用自然语言触发：

```
请帮我生成今天的 PR 状态报告
```

```
检查一下有哪些 PR 需要提醒
```

```
看看 pending 的 PR 进展如何
```

### 手动使用脚本

你也可以直接使用提供的 Python 脚本：

#### 1. 获取 PR 数据

```bash
python pr-reminder/scripts/fetch_prs.py \
  --repo owner/repo \
  --output prs.json \
  --pretty
```

#### 2. 对比状态（可选）

```bash
python pr-reminder/scripts/compare_states.py \
  --current prs.json \
  --history .pr-reminder-state.json \
  --output changes.json \
  --update-history
```

#### 3. 生成报告

```bash
python pr-reminder/scripts/format_report.py \
  --prs prs.json \
  --changes changes.json \
  --output report.md
```

## 工作原理

1. **获取 PR**：使用 `gh pr list` 获取所有 open PR
2. **加载历史**：读取状态文件（`~/.pr-reminder-state.json`）
3. **状态对比**：识别新增、变化、无变化的 PR
4. **智能分组**：
   - 新增 PR → 完整介绍
   - 有进展 PR → 高亮变化点
   - 无变化 PR → 简洁标记（超过48小时）
   - 需关注 PR → 优先提醒
   - 就待合并 → 呼吁管理员
5. **生成报告**：应用鼓励性话术和 PR 分析
6. **保存状态**：更新历史快照

## 输出示例

```markdown
🔄 PR 状态日报 | 2025-04-16 14:30 | owner/repo

✨ 新增待审核 (2)
━━━━━━━━━━━━━━━━━━━━━━━━━━━

📦 PR #42: 实现用户认证功能
👤 作者: @zhangnan27
⏱️ 创建: 2小时前
📊 变更: +450/-120 (5个文件)
✅ CI: 通过中...
👥 等待: @reviewer1, @reviewer2
💬 这个功能很实用！认证逻辑清晰，代码结构良好。

🔗 https://github.com/owner/repo/pull/42

━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 今日统计
━━━━━━━━━━━━━━━━━━━━━━━━━━━
• 总活跃 PR: 7 个
• 新增: 2 | 有进展: 2 | 无变化: 1 | 待处理: 1 | 就绪: 1

💪 团队给力！继续保持这个节奏 🚀
```

## 目录结构

```
pr-reminder/
├── SKILL.md                    # Skill 主文件
├── README.md                   # 本文件
├── scripts/
│   ├── fetch_prs.py           # 获取 PR 数据
│   ├── compare_states.py      # 对比历史状态
│   ├── analyze_pr.py          # 分析 PR 质量
│   └── format_report.py       # 生成报告
├── references/
│   └── gh-api-reference.md    # GitHub CLI API 参考
└── assets/
    └── state-schema.json      # 状态文件结构示例
```

## 配置

### 状态文件位置

默认使用工作目录中的 `.pr-reminder-state.json`，如果不存在则尝试 `~/.pr-reminder-state.json`。

可以通过环境变量自定义：

```bash
export PR_REMINDER_STATE_FILE="/path/to/custom/state.json"
```

### 自定义鼓励语

编辑 `scripts/format_report.py` 中的 `encouragement_templates` 字典。

### 调整分组规则

修改 SKILL.md 中的分类逻辑，或直接编辑 `compare_states.py`。

## 常见问题

### Q: 首次运行会显示什么？

A: 首次运行时，所有 PR 都会被标记为"新增"，并创建新的状态文件。

### Q: 如何避免刷屏？

A: Skill 会自动过滤超过48小时无变化的 PR，且对无变化的 PR 使用最简洁的展示方式。

### Q: 支持多仓库吗？

A: 支持！状态文件自动支持多个仓库，相互独立。

### Q: 如何只看特定状态的 PR？

A: 可以在提示中指定，例如："有哪些 PR 已经通过审核了？"

## 测试

在真实仓库上测试过：

- ✅ 成功获取 27 个 PR
- ✅ 正确识别新增 PR
- ✅ 生成群聊友好的报告格式
- ✅ CI 状态正确提取和显示

## 贡献

欢迎提交 Issue 和 Pull Request！

## 许可证

MIT

## 相关资源

- [GitHub CLI 文档](https://cli.github.com/manual/)
- [Skill Creator](https://github.com/anthropics/claude-code-skill-creator)
- [AgenticAIPlan/AgenticAISkills](https://github.com/AgenticAIPlan/AgenticAISkills)
