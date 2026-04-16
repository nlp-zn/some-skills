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
# Ensure you have Python 3.7+
python3 --version

# Install GitHub CLI (required for pr-reminder)
brew install gh
gh auth login
```

## 📁 Project Structure

```
some-skills/
├── pr-reminder/              # PR monitoring skill
│   ├── SKILL.md             # Main skill file
│   ├── README.md            # User documentation
│   ├── QUICKSTART.md        # Quick start guide
│   ├── SUMMARY.md           # Project summary
│   ├── scripts/             # Python scripts
│   ├── references/          # Technical references
│   ├── assets/              # Resource files
│   ├── install.sh           # Installation script
│   └── uninstall.sh         # Uninstallation script
├── LICENSE
├── README.md
└── CONTRIBUTING.md
```

## 🔧 Development Workflow

### Adding a New Skill

1. **Create a new directory** for your skill:
   ```bash
   mkdir your-skill-name
   cd your-skill-name
   ```

2. **Create required files**:
   - `SKILL.md` - Main skill definition with frontmatter
   - `README.md` - User-facing documentation
   - `install.sh` - Installation script (make executable)
   - `uninstall.sh` - Uninstallation script (make executable)

3. **Follow the skill structure**:
   ```
   your-skill/
   ├── SKILL.md              # Required: skill metadata and instructions
   ├── README.md             # Required: user documentation
   ├── scripts/              # Optional: executable scripts
   ├── references/           # Optional: reference docs
   └── assets/               # Optional: templates, configs
   ```

4. **SKILL.md format**:
   ```yaml
   ---
   name: your-skill-name
   description: A clear, concise description of when to use this skill
   compatibility: Any required tools or dependencies
   ---

   # Your Skill Name

   Detailed instructions for using this skill...
   ```

### Making Changes

1. **Create a branch** for your work:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** and test thoroughly:
   ```bash
   # Test your skill locally
   cd your-skill
   ./install.sh
   ```

3. **Commit your changes**:
   ```bash
   git add .
   git commit -m "feat: add your-skill-name for doing X"
   ```

4. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
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

## 🧪 Testing

Before submitting a PR:

1. **Test installation**:
   ```bash
   cd your-skill
   ./install.sh
   ```

2. **Test the skill** in Claude Code:
   - Trigger the skill with appropriate prompts
   - Verify expected behavior
   - Test edge cases

3. **Test uninstallation**:
   ```bash
   ./uninstall.sh
   ```

## 📖 Documentation

Good documentation is essential:

- **README.md**: Clear description, features, installation, usage
- **SKILL.md**: Proper frontmatter, detailed instructions
- **Comments**: Explain complex logic in code
- **Examples**: Provide real-world usage examples

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
