# Contributing to Some Skills

Thank you for your interest in contributing! This document provides guidelines for contributing to this repository.

## 🎯 Types of Contributions

We welcome the following types of contributions:

- **New Skills**: Add completely new skills to the collection
- **Bug Fixes**: Fix bugs in existing skills
- **Enhancements**: Improve functionality or user experience
- **Documentation**: Improve or add documentation
- **Examples**: Add usage examples or test cases

## 🚀 Getting Started

### 1. Fork the Repository

Click the "Fork" button in the top right corner of the repository page.

### 2. Clone Your Fork

```bash
git clone https://github.com/YOUR_USERNAME/some-skills.git
cd some-skills
```

### 3. Install Dependencies

```bash
# Ensure you have Python 3
python3 --version

# Install extra dependencies only for the skill you are working on
```

## 📁 Project Structure

```
some-skills/
├── skills/
│   ├── <skill-name>/
│   │   ├── SKILL.md         # Required: main skill definition
│   │   ├── scripts/         # Optional helper scripts
│   │   ├── references/      # Optional supporting docs
│   │   ├── evals/           # Optional eval definitions
│   │   └── assets/          # Optional templates/examples
│   └── <skill-name>-workspace/
│       └── ...              # Local eval outputs, screenshots, benchmarks
├── LICENSE
├── README.md
├── CONTRIBUTING.md
├── install.sh
└── .claude/INSTALL.md
```

## 🔧 Development Workflow

### Adding a New Skill

1. **Create a new directory** for your skill:
   ```bash
   mkdir -p skills/your-skill-name
   cd skills/your-skill-name
   ```

2. **Create the required file**:
   - `SKILL.md` - Main skill definition and usage guidance

3. **Add optional directories only if they help**:
   ```
   your-skill/
   ├── SKILL.md              # Required
   ├── scripts/              # Optional
   ├── references/           # Optional
   ├── evals/                # Optional
   └── assets/               # Optional
   ```

4. **Document skill-specific requirements inside the skill**, not only in repo docs:
   - auth or token setup
   - expected env vars or config locations
   - helper scripts and examples
   - model or provider caveats

5. **Keep local eval outputs outside the skill directory**:
   ```bash
   mkdir -p skills/your-skill-workspace
   ```
   Use the sibling workspace for screenshots, generated media, benchmark results, and experiment notes. These directories are gitignored on purpose.

6. **Never commit secrets**:
   - use environment variables
   - or use user-level config such as `~/.config/<tool-or-skill>/...`
   - if local `.env` files are needed for testing, keep them ignored

### Making Changes

1. **Create a branch** for your work:
   ```bash
   git checkout -b codex/your-feature-name
   ```

2. **Make your changes** and test thoroughly:
   ```bash
   # Install the skill from the repo root
   ./install.sh your-skill-name
   ```

3. **Commit your changes**:
   ```bash
   git add .
   git commit -m "feat: add your-skill-name for doing X"
   ```

4. **Push to your fork**:
   ```bash
   git push origin codex/your-feature-name
   ```

5. **Create a Pull Request** on GitHub.

## 📝 Commit Message Guidelines

Follow conventional commit format:

```
<type>: <description>

[optional body]

[optional footer]
```

**Types:**
- `feat`: New skill or feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples:**
```
feat: add pr-reminder skill for GitHub PR monitoring

- Implements quality scoring system
- Generates team-chat-friendly reports
- Tracks PR state changes across sessions
```

## ✅ Code Style

### Python Scripts
- Follow PEP 8 guidelines
- Use type hints where appropriate
- Add docstrings to functions
- Keep functions focused and modular

### Skill Files
- Use clear, concise language
- Provide context for instructions
- Include examples where helpful
- Use progressive disclosure (simple first, detailed later)
- Default to reusable patterns that will still make sense after more skills are added

## 🧪 Testing

Before submitting a PR:

1. **Test installation**:
   ```bash
   ./install.sh your-skill-name
   ```

2. **Test the skill** in Claude Code:
   - Trigger the skill with appropriate prompts
   - Verify expected behavior
   - Test edge cases
   - If the skill integrates with an external provider, verify the auth onboarding path too

3. **Check repo-level docs if behavior changed**:
   - update `README.md` if a new skill was added
   - update `.claude/INSTALL.md` if install or setup flow changed
   - update `CHANGELOG.md` when the change is user-visible

## 📖 Documentation

Good documentation is essential:

- **README.md**: Repo catalog and shared conventions
- **SKILL.md**: Skill entry point and usage guidance
- **Comments**: Explain complex logic in code
- **Examples**: Provide real-world usage examples
- **references/**: Keep supporting material close to the skill when it improves outcomes

## 🤝 Code Review Process

1. All submissions require review
2. Address review feedback promptly
3. Keep PRs focused and minimal
4. Update documentation as needed

## 🎨 Style Guidelines

### Skill Descriptions
- Be specific about when to use the skill
- Include both what it does and when to trigger it
- Use "pushy" descriptions to improve triggering accuracy
- Prefer descriptions that still make sense when the repo contains many unrelated skills

### User-Facing Text
- Use clear, friendly language
- Avoid jargon when possible
- Provide context for technical terms
- Use encouraging, positive language

## 📧 Questions?

Feel free to open an issue for:
- Bug reports
- Feature requests
- Documentation improvements
- General questions

## ⭐ Recognition

Contributors will be acknowledged in the skill documentation and project README.

Thank you for contributing! 🎉
