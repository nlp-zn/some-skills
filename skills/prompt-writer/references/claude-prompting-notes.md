# Claude Prompting Notes

These notes are a compact synthesis of Anthropic's current prompting guidance checked on 2026-04-18. Treat the linked docs as the source of truth if you need to verify a detail.

## Primary sources

- Prompt engineering overview: https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/overview
- Prompting best practices: https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices

## What to carry into prompt writing

### 1. Clear and direct beats clever

Anthropic explicitly recommends clear, explicit instructions. If a minimally informed colleague would be confused by the prompt, Claude probably will be too.

Practical implication:

- say exactly what should be produced
- make format and constraint requirements literal
- do not rely on vague phrases like "handle this well"

### 2. Context improves results

Anthropic recommends adding context or motivation behind important instructions so Claude understands why they matter.

Practical implication:

- explain the purpose of a behavior when it changes prioritization
- use this sparingly, only where the why actually helps

### 3. Examples are one of the strongest levers

Anthropic recommends using a few relevant, diverse, structured examples when output format or reasoning style needs tighter control.

Practical implication:

- use examples when format adherence matters
- keep examples close to the real task
- prefer a few strong examples over many noisy ones

### 4. XML structure helps on complex prompts

Anthropic explicitly recommends XML tags when a prompt mixes instructions, context, examples, and user inputs.

Practical implication:

- use tags like `<instructions>`, `<context>`, `<examples>`, and `<input>`
- tag boundaries help reduce misreads in long prompts

### 5. Tool use should be stated as action, not suggestion

Anthropic notes that if you say "suggest changes", Claude may stop at suggestions even when you wanted implementation.

Practical implication:

- if the model should act, say so directly
- if a tool should be used, specify that expectation plainly

### 6. Add self-checks when correctness matters

Anthropic recommends asking Claude to verify its work against a criterion before finishing.

Practical implication:

- add a final quality check for coding, research, math, or structured extraction
- keep the check concrete rather than philosophical

### 7. Prompt engineering is not always the fix

Anthropic's overview explicitly says not every failure should be solved with prompt engineering. Some problems are better fixed by model choice, tooling, or eval design.

Practical implication:

- say when a better prompt alone is unlikely to solve the issue
- recommend capability or workflow fixes when appropriate

## Claude-oriented prompt heuristics

When writing prompts for Claude, this structure is usually reliable:

1. a short role sentence
2. a clear goal block
3. structured context
4. ordered instructions
5. output-format block
6. quality-check block

When the task is simple, stay plain. When the task is complex, switch to tagged structure instead of making the prose denser.
