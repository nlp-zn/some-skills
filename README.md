# Some Skills

> A growing collection of reusable AI skills, organized for long-term expansion.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Skills](https://img.shields.io/badge/Skills-2-blue.svg)](https://github.com/nlp-zn/some-skills)

This repository stores production-ready skills under `skills/`, plus the shared conventions needed to keep new additions consistent as the collection grows.

## What Lives Here

Current skills:

| Skill | Purpose | Notes |
| --- | --- | --- |
| [`pr-reminder`](./skills/pr-reminder/) | GitHub PR monitoring and team-chat-friendly status reports | Uses GitHub data and local state snapshots |
| [`ernie-image`](./skills/ernie-image/) | ERNIE-Image / ERNIE-Image-Turbo text-to-image generation | Uses AI Studio access token and optional local config |

## Repository Conventions

All installable skills live under `skills/<skill-name>/` and must contain a `SKILL.md`.

Recommended layout:

```text
some-skills/
├── skills/
│   ├── <skill-name>/
│   │   ├── SKILL.md            # Required
│   │   ├── scripts/            # Optional helpers
│   │   ├── references/         # Optional supporting docs
│   │   ├── evals/              # Optional eval definitions
│   │   └── assets/             # Optional templates or examples
│   └── <skill-name>-workspace/ # Optional local eval outputs, gitignored
├── README.md
├── CONTRIBUTING.md
├── install.sh
└── .claude/INSTALL.md
```

Important repo-level rules:

- `SKILL.md` is the only required file for a skill directory.
- Eval and benchmark outputs should stay in a sibling `*-workspace/` directory and must not be committed.
- Secrets must never be stored in the repository. Prefer environment variables or user-level config under `~/.config/...`.
- Skill-specific dependencies belong in the skill docs, not in a repo-wide hard requirement list.

## Installation

Use the root installer to install any skill that contains a `SKILL.md`:

```bash
./install.sh pr-reminder
./install.sh ernie-image
```

This creates a symlink in `~/.claude/skills/`.

Manual install also works:

```bash
ln -s "$(pwd)/skills/<skill-name>" ~/.claude/skills/<skill-name>
```

See [`.claude/INSTALL.md`](./.claude/INSTALL.md) for more detail.

## Requirements

Shared baseline:

- Claude Code or a compatible skill runner
- `bash`
- `python3` for skills that ship helper scripts

Skill-specific dependencies vary:

- `pr-reminder` depends on GitHub access and its helper scripts
- `ernie-image` depends on an AI Studio access token

## Adding More Skills

When a new skill lands, the repo should stay coherent at three levels:

1. Add the skill under `skills/<skill-name>/`.
2. Update this README so the skill catalog stays discoverable.
3. Follow [CONTRIBUTING.md](./CONTRIBUTING.md) for shared structure, secret handling, and eval workspace rules.

## Contributing

Contributions are welcome. See [CONTRIBUTING.md](./CONTRIBUTING.md).

## License

This project is licensed under the MIT License. See [LICENSE](./LICENSE).
