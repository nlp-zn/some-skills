# PR Reminder Skill - 完成总结

## 项目概述

成功创建了一个智能的 GitHub PR 状态监控与提醒 skill，用于生成群聊友好的 PR 进展报告。

## 核心功能

### 1. 多维度 PR 状态检查 ✅
- Review 状态（APPROVED, CHANGES_REQUESTED, REVIEW_REQUIRED）
- CI 检查状态（SUCCESS, FAILURE, PENDING）
- 更新时间和创建时间
- 标签和作者信息
- 代码变更规模（行数、文件数）

### 2. 智能 PR 质量评分系统 ✨
- **评分维度**：
  - CI 状态 (30分)
  - 代码规模 (20分)
  - 修改聚焦度 (15分)
  - 审核情况 (15分)
  - 文档完整性 (10分)
  - 时效性 (10分)
- **评分等级**：
  - 🏆 80-100分: 优秀
  - ⭐ 60-79分: 良好
  - 👍 40-59分: 一般
  - 💪 0-39分: 需改进
- **智能排序**：高质量 PR 优先展示

### 3. 智能变化感知 ✅
- 对比历史状态，自动识别：
  - 新增 PR
  - 有进展的 PR（CI 变化、审核状态变化、新增 approval）
  - 无变化的 PR
  - 需要关注的 PR（CI 失败、有建议待处理）
  - 就待合并的 PR

### 4. 差异化展示 📊
- **新增 PR**：完整介绍（作者、时间、规模、CI、reviewers）
- **有进展 PR**：简洁信息 + 高亮变化点
- **无变化 PR**：最简洁提醒 + 等待时长
- **需关注 PR**：标明问题 + 改进建议
- **就待合并 PR**：呼吁管理员 + 肯定语

### 5. 群聊友好格式 💬
- 使用 emoji 增强可读性
- 分层展示（分组标题 + 分隔线）
- 鼓励性语言和积极反馈
- 统计汇总（底部数据）
- 适合在微信群、Slack 等分享

### 6. 频次控制 🔄
- 跨会话状态持久化（JSON 文件）
- 自动过滤超过 48 小时无变化的 PR
- 避免重复刷屏
- 支持多仓库独立管理

## 文件结构

```
pr-reminder/
├── SKILL.md                    # Skill 主文件（触发条件、工作流程）
├── README.md                   # 使用说明
├── SUMMARY.md                  # 本文件
├── install.sh                  # 安装脚本（软链接）
├── uninstall.sh                # 卸载脚本
├── pr-reminder.skill           # 打包的 skill 文件（26KB）
├── scripts/
│   ├── fetch_prs.py           # 获取 PR 数据 + 评分
│   ├── compare_states.py      # 对比历史状态
│   ├── analyze_pr.py          # PR 质量分析和评分
│   └── format_report.py       # 生成群聊友好报告
├── references/
│   ├── gh-api-reference.md    # GitHub CLI API 参考
│   └── scoring-system.md      # 评分系统详细说明
└── assets/
    └── state-schema.json      # 状态文件结构示例
```

## 测试结果

### 测试仓库
- [AgenticAIPlan/AgenticAISkills](https://github.com/AgenticAIPlan/AgenticAISkills)
- 27 个 open PR

### 测试场景 1：首次运行
- ✅ 成功获取 27 个 PR
- ✅ 所有 PR 标记为"新增"
- ✅ 正确计算质量评分（最高 77 分）
- ✅ 按评分从高到低排序
- ✅ 生成群聊友好报告

### 评分示例（Top 10）
1. PR #46: 77/100 - feat: add international-lead-research skill ⭐
2. PR #57: 75/100 - feat: add wecom-group-invite skill ⭐
3. PR #55: 75/100 - feat: add drama-agent skill ⭐
4. PR #52: 73/100 - feat: add paddleocr-ondevice-integration-navigator skill ⭐
5. PR #44: 72/100 - feat: add quarterly-eval skill ⭐

## 使用方式

### 安装
```bash
# 方式 1：使用安装脚本（推荐）
cd pr-reminder
./install.sh

# 方式 2：手动创建软链接
ln -s $(pwd)/pr-reminder ~/.claude/skills/pr-reminder
```

### 在 Claude Code 中使用
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
```bash
# 获取 PR 数据
python pr-reminder/scripts/fetch_prs.py --repo owner/repo --output prs.json

# 对比状态
python pr-reminder/scripts/compare_states.py --current prs.json --history .pr-reminder-state.json --output changes.json --update-history

# 生成报告
python pr-reminder/scripts/format_report.py --prs prs.json --changes changes.json --output report.md
```

## 技术栈

- **语言**: Python 3.7+
- **依赖**: GitHub CLI (gh)
- **数据格式**: JSON
- **输出格式**: Markdown（群聊友好）

## 关键设计决策

### 1. 评分系统设计
- CI 状态权重最高（30%），因为质量最重要
- 代码规模有最佳区间（200-800行），避免过小或过大
- 鼓励聚焦（文件数越少分数越高）
- 考虑时效性（新 PR 优先）

### 2. 频次控制策略
- 48 小时无变化的 PR 自动隐藏
- 无变化 PR 使用最简洁展示
- 有变化 PR 高亮进展
- 避免重复刷屏

### 3. 群聊展示优化
- emoji 分组和分层
- 鼓励性语言（"团队给力！继续保持这个节奏 🚀"）
- 统计汇总（整体数据）
- 链接可点击

### 4. 软链接安装方式
- 源代码保留在 git 仓库
- 软链接到 `~/.claude/skills/`
- 方便迭代和更新
- 支持多人协作

## 后续优化方向

1. **交互式配置**：支持自定义评分权重
2. **多平台通知**：直接发送到微信/Slack/DingTalk
3. **PR 趋势分析**：追踪 PR 质量变化趋势
4. **自动评论**：直接在 PR 上添加鼓励性评论
5. **团队统计**：贡献者排名、审核效率统计
6. **定时任务**：自动定时生成并发送报告

## 许可证

MIT

## 相关资源

- [GitHub CLI 文档](https://cli.github.com/manual/)
- [AgenticAIPlan/AgenticAISkills](https://github.com/AgenticAIPlan/AgenticAISkills)
- [Skill Creator](https://github.com/anthropics/claude-code-skill-creator)

---

**创建时间**: 2025-04-16
**版本**: 1.0.0
**作者**: zhangnan27
**状态**: ✅ 完成并测试通过
