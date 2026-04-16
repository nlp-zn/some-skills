# Installation for Claude Code

This document explains how to install skills from this repository in Claude Code.

## Quick Installation

Install individual skills from the repo root:

```bash
./install.sh pr-reminder
./install.sh ernie-image
```

The root installer only lists directories that contain a `SKILL.md`, so local eval workspaces such as `ernie-image-workspace/` are ignored automatically.

This creates a symlink from `skills/<skill-name>/` to `~/.claude/skills/<skill-name>`.

## Manual Installation

If you prefer manual installation, create a symlink:

```bash
# Navigate to the repository
cd /path/to/some-skills

# Create symlink for the skill
ln -s $(pwd)/skills/<skill-name> ~/.claude/skills/<skill-name>
```

## Verification

To verify the installation, check that the skill is available:

```bash
ls -la ~/.claude/skills/
```

You should see the skill listed as a symlink:

```
lrwxr-xr-x  1 user  staff  /path/to/some-skills/skills/pr-reminder
```

## Using Skills in Claude Code

Once installed, you can use the skill in Claude Code by simply describing what you want:

```
请帮我生成今天的 PR 状态报告
```

Or for ERNIE Image:

```
画一张科技感海报
```

Claude will automatically trigger the appropriate skill.

## Uninstallation

To uninstall a skill, use the root uninstall script:

```bash
./uninstall.sh <skill-name>
```

Or manually remove the symlink:

```bash
rm ~/.claude/skills/<skill-name>
```

## Troubleshooting

### Skill Not Triggering

1. **Check installation**: Verify the symlink exists
2. **Check SKILL.md**: Ensure the description is clear and specific
3. **Restart Claude Code**: Sometimes a restart is needed

### Permission Errors

If you get permission errors, the repo install script may not be executable:

```bash
chmod +x install.sh uninstall.sh
```

### Local State and Config

Some skills create local state or user-level config:

- `pr-reminder` may write local state snapshots for change detection
- `ernie-image` can use environment variables or a user-level config file for API access

Keep generated outputs, screenshots, and benchmarks in a sibling `*-workspace/` directory instead of committing them into the skill itself.

## Next Steps

- Read the skill's `SKILL.md` for detailed usage instructions
- Check the skill's `references/` or `evals/` folders if present
- See `CONTRIBUTING.md` if you want to add new skills
