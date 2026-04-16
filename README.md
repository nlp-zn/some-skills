# Some Skills

> A collection of AI skills for Claude Code

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Skill Count](https://img.shields.io/badge/Skills-1-blue.svg)](https://github.com/zhangnan27/some-skills)

A curated collection of reusable AI skills for Claude Code. Each skill is designed to solve specific business problems and improve productivity.

## 🚀 Skills

### [pr-reminder](./skills/pr-reminder/) - PR Status Monitor & Reminder

An intelligent GitHub PR monitoring tool that generates team-chat-friendly status reports with quality scoring.

**Features:**
- 📊 **Quality Scoring**: Automatically scores PRs (0-100) based on CI, code size, focus, reviews, documentation, and timeliness
- 🔄 **Change Detection**: Tracks PR state changes across sessions
- 💬 **Team-Chat Format**: Generates beautiful, emoji-rich reports perfect for Slack/WeChat
- ✨ **Business Value Analysis**: Extracts skill information and highlights business/user value
- 🔧 **Actionable Insights**: Provides improvement suggestions from user perspective
- ⚡ **Smart Sorting**: Ranks PRs by quality score to prioritize review

**Use Cases:**
- Daily PR status reports in team chats
- Reminding contributors about CI failures or review feedback
- Alerting admins to merge approved PRs
- Tracking PR progress over time

**Quick Start:**
```bash
cd skills/pr-reminder
./install.sh
```

Then in Claude Code:
```
请帮我生成今天的 PR 状态报告
```

## 📦 Installation

See [`.claude/INSTALL.md`](./.claude/INSTALL.md) for detailed installation instructions.

### Quick Install

Each skill can be installed independently using the provided install script:

```bash
cd skills/<skill-name>
./install.sh
```

Or manually create a symlink:

```bash
ln -s $(pwd)/skills/<skill-name> ~/.claude/skills/<skill-name>
```

## 🔧 Requirements

- Claude Code
- GitHub CLI (`gh`) - for PR monitoring skill
- Python 3.7+

## 📖 Documentation

Each skill includes comprehensive documentation:
- `README.md` - Quick start guide
- `SKILL.md` - Detailed skill documentation
- `QUICKSTART.md` - 5-minute setup guide
- `SUMMARY.md` - Project summary
- `references/` - Technical references

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](./CONTRIBUTING.md) for details.

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](./LICENSE) file for details.

## 🌟 Acknowledgments

- Inspired by [obra/superpowers](https://github.com/obra/superpowers)
- Built with [Claude Code](https://claude.ai/code)
- Powered by [Anthropic Claude](https://www.anthropic.com)

## 📮 Contact

Zhangnan27 - [@zhangnan27](https://github.com/zhangnan27)

---

Made with ❤️ by Zhangnan27
