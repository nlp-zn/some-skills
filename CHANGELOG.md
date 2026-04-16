# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

#### pr-reminder v1.0.0
- Intelligent GitHub PR monitoring and status reporting
- **Quality Scoring System**: Automatically scores PRs (0-100) based on:
  - CI status (30 points)
  - Code size (20 points)
  - Focus (15 points)
  - Reviews (15 points)
  - Documentation (10 points)
  - Timeliness (10 points)
- **Change Detection**: Tracks PR state changes across sessions
- **Business Value Analysis**: Extracts skill information and highlights:
  - Core capability value (automation, analysis, generation, etc.)
  - User benefits (efficiency, quality, satisfaction)
- **Smart Status Display**: Clear indication of next action:
  - "等待贡献者修改" - Contributor needs to fix
  - "等待审核中" - Waiting for reviewers
  - "等待管理员合并" - Admin needs to merge
- **Team-Chat Format**: Beautiful, emoji-rich reports perfect for team messaging
- **Actionable Insights**: User-perspective improvement suggestions
- **Quality-Based Ranking**: PRs sorted by score for prioritized review

### Installation Scripts
- `install.sh` - Quick symlink-based installation
- `uninstall.sh` - Clean removal

### Documentation
- Comprehensive README with features and quick start
- QUICKSTART.md - 5-minute setup guide
- SUMMARY.md - Complete project summary
- CONTRIBUTING.md - Contribution guidelines
- Scoring system documentation
- GitHub CLI reference

### Technical Features
- State persistence across sessions (`.pr-reminder-state.json`)
- Multi-repository support
- Automatic cleanup of old history (7 days)
- Smart filtering (hides PRs unchanged >48 hours)
- Concurrent-safe temporary file handling

#### ernie-image v1.0.0
- Added ERNIE-Image / ERNIE-Image-Turbo skill
- Added AI Studio auth onboarding via environment variable, CLI flag, env file, and user-level config
- Added prompt playbook, presets, evals, and runtime stability improvements for serial image generation

### Changed
- Updated repo documentation for a multi-skill layout
- Standardized guidance for eval workspaces, local config, and root-level installation

## [1.0.0] - 2025-04-16

### Added
- Initial project structure
- First skill: pr-reminder
- MIT License
- Contribution guidelines
- Git repository initialization

---

## Format Summary

- **Added**: New features
- **Changed**: Changes to existing functionality
- **Deprecated**: Soon-to-be removed features
- **Removed**: Removed features
- **Fixed**: Bug fixes
- **Security**: Security vulnerability fixes
