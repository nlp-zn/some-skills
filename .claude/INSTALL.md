# Installation for Claude Code

This document explains how to install skills from this repository in Claude Code.

## Quick Installation

### Install All Skills

To install all skills at once, run the installation script for each skill:

```bash
# Install pr-reminder
cd skills/pr-reminder
./install.sh
```

### Install Individual Skills

Each skill has its own `install.sh` script:

```bash
cd skills/<skill-name>
./install.sh
```

This creates a symlink from the skill directory to `~/.claude/skills/`.

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

Claude will automatically trigger the appropriate skill.

## Uninstallation

To uninstall a skill, use the provided uninstall script:

```bash
cd skills/<skill-name>
./uninstall.sh
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

If you get permission errors, the install script may not be executable:

```bash
chmod +x skills/<skill-name>/install.sh
```

### State Files

Some skills (like pr-reminder) create state files in your working directory. These are normal and help with change detection across sessions.

## Next Steps

- Read the skill's README for detailed usage instructions
- Check QUICKSTART.md for a 5-minute setup guide
- See CONTRIBUTING.md if you want to add new skills
