---
name: prompt-writer
description: "Use this skill when the user wants to craft, revise, debug, or optimize a prompt for an AI agent or LLM. Trigger for writing system prompts, task prompts, skill prompts, or agent instructions; improving prompts that are too verbose, unreliable, or off-target; converting workflows or rules into reusable prompts; creating prompt templates for teams; building evaluation prompts; or fixing prompts that make agents over-research, hallucinate, ignore constraints, or behave unpredictably. Also use for requests like 'rewrite my system prompt', 'debug this prompt', 'make the agent do X instead of Y', 'prompt template for', or prompts for Codex, Claude, GPT, or local coding agents. Chinese: 写 prompt, 优化提示词, 改 system prompt, agent 规则, 转成 skill."
---

# Prompt Writer

Turn fuzzy requests, broken prompts, and messy notes into production-ready prompts that are easier to run, test, and iterate.

Read only the relevant reference note when the target is model-specific:

- OpenAI, Codex, or GPT-family agents: [openai-prompting-notes.md](./references/openai-prompting-notes.md)
- Claude-family agents: [claude-prompting-notes.md](./references/claude-prompting-notes.md)

Do not blindly rewrite prompts from scratch if the user already has one. First identify what is working, what is failing, and what the prompt is actually trying to control.

## What this skill should deliver

Default output:

1. A short diagnosis of the prompt problem
2. One polished prompt that the user can paste directly into their system prompt, task prompt, skill, or harness
3. Two or three realistic test prompts
4. A short note on what to tweak next if the prompt still misses

If the user explicitly wants "just give me the prompt", keep everything except the final prompt minimal.

## Default workflow

### 1. Identify the prompt type

First decide what you are writing:

- `system prompt`
- `task prompt`
- `skill prompt`
- `agent harness prompt`
- `evaluation prompt`
- `prompt revision` for an existing prompt

This matters because the right level of stability is different in each case. Stable behavioral rules belong in a system prompt or skill. One-off deliverable details belong in the task prompt.

### 2. Extract the real objective before drafting

Gather the following from the conversation before asking for more input:

- the target model or agent, if known
- the job to be done
- the available tools and files
- the constraints and no-go zones
- the desired output format
- the main failure modes
- whether the user wants speed, depth, or a balance

If some details are missing, make reasonable assumptions unless the prompt would become dangerously misleading.

### 3. Decide whether prompting is actually the bottleneck

Do not pretend prompt changes can fix everything.

If the real issue is one of these, say so briefly and then still give the best prompt you can:

- wrong model choice
- missing tools or missing context
- missing examples or source material
- missing evals
- instructions that belong in code, not prose

Prompting can improve behavior, but it is not a substitute for capability, context, or verification.

### 4. Match the structure to the target model

For OpenAI or Codex prompts:

- be explicit about scope, output shape, verbosity, and stopping rules
- state tool-use expectations clearly
- define the research bar and citation requirements when research is involved
- add concise constraints instead of long philosophical prose
- include metaprompting hooks when the user is iterating on agent behavior

For Claude prompts:

- prefer very clear and direct instructions
- use XML tags when the prompt mixes instructions, context, examples, and inputs
- use examples when format adherence matters
- make tool-use instructions action-oriented
- add a self-check when accuracy matters

For generic prompts:

- keep the structure simple and copy-pasteable
- separate role, task, context, workflow, and output contract
- avoid model-specific syntax unless the target is known

### 5. Write the smallest prompt that still controls the behavior

Do not bloat the prompt.

Prefer:

- concrete constraints over generic advice
- one explicit output contract over repeated wording
- a few good examples over many weak ones
- ordered steps when order matters
- placeholders with clear names such as `{{repo_name}}` or `{{user_goal}}`

Avoid:

- vague instructions like "be smart" or "do your best"
- contradictory goals like "be extremely thorough" and "be very fast" without a tradeoff rule
- repeating the same rule in multiple places
- style instructions that fight the actual task
- long persona blocks when the user mainly wants reliable execution

### 6. Pressure-test the prompt before you hand it over

Always draft a few realistic tests. Good tests should cover:

- a normal request
- an edge case or ambiguity
- a case that previously failed

If the user is building something important, recommend an eval loop rather than endless prompt vibes.

## Prompt building checklist

Before finalizing, make sure the prompt answers these questions:

1. What is the model supposed to do?
2. What inputs can it rely on?
3. What should it not do?
4. What tools may it use?
5. What should the output look like?
6. When should it ask, escalate, or stop?
7. How will we know the prompt is better than the previous one?

If any answer is unclear, the prompt will likely drift.

## Output templates

### Template A: System or agent prompt

Use this when the user wants a reusable prompt for an agent, skill, or harness.

```text
You are [role].

Your job:
- [primary responsibility]

Context:
- [relevant environment, repo, domain, or users]

Working rules:
1. [ordered rule]
2. [ordered rule]
3. [ordered rule]

Tool use:
- [when to use tools]
- [when not to use tools]

Output contract:
- [default response shape]
- [format requirements]

Escalation:
- [when to ask]
- [when to make a reasonable assumption]

Quality bar:
- [verification or self-check rule]
```

### Template B: Task prompt

Use this when the user wants a one-off prompt for a single run.

```text
Goal: [what to produce]

Context:
- [facts the model should rely on]

Constraints:
- [scope limits]
- [format limits]
- [time or cost tradeoffs]

Instructions:
1. [step]
2. [step]
3. [step]

Output:
- [exact format]
- [must include / must exclude]
```

### Template C: Claude-style structured prompt

Use this when Claude is the clear target and the task is complex enough to benefit from tagged sections.

```xml
<role>You are [role].</role>
<goal>[what success looks like]</goal>
<context>
[relevant context]
</context>
<instructions>
1. [step]
2. [step]
3. [step]
</instructions>
<output_format>
[required shape]
</output_format>
<quality_checks>
[self-check or verification rule]
</quality_checks>
```

## Revision workflow for existing prompts

When the user already has a prompt:

1. Read the current prompt carefully.
2. Name the failure modes in plain language.
3. Preserve any instruction that is still doing useful work.
4. Remove duplication and contradictions.
5. Tighten the output contract.
6. Add examples only if they solve a real formatting or reasoning problem.
7. Return a revised prompt plus a short changelog.

Do not claim that a rewrite is better unless you can explain why.

## Metaprompting loop

When the user is tuning agent behavior over time, use a simple improvement loop:

1. keep the current prompt
2. identify one recurring failure mode
3. make one targeted change
4. run a few realistic tests
5. keep or discard the change based on observed behavior

Prefer small prompt edits over total rewrites unless the prompt is fundamentally confused.

## Style rules for this skill

- Write prompts that are ready to paste.
- Keep your own explanation shorter than the prompt unless the user asks for depth.
- Use section headings inside the prompt only when they improve scanability.
- Prefer numbered steps when completeness matters.
- Prefer bullets when the prompt is mainly declarative.
- If the prompt is for coding or research agents, make verification expectations explicit.
- If the prompt is for long-running agents, include persistence and stopping rules.

## Examples

Use these examples as patterns, not as rigid templates.

### Example 1: Chinese prompt rewrite for a coding agent

Input:

`把这个很口语化的提示词改成可复用的 system prompt，目标是让 agent 做长任务时更稳、更会自检，而且别动不动就停下来问我。`

Good output shape:

- First diagnose the real control problem: long-running reliability, self-checking, and over-escalation.
- Then write one paste-ready `system prompt`.
- End with 2 to 3 test prompts and one likely next tweak.

The final prompt should usually include:

- a rule for when to keep going versus when to ask
- a verification or self-check rule
- a concise-update rule
- a bias toward reasonable assumptions when risk is low

### Example 2: Workflow to reusable skill prompt

Input:

`Turn this workflow into a reusable skill prompt: when someone asks for demand research, search real user feedback across Reddit, GitHub, and X, summarize repeated pain points, separate evidence from inference, and end with 3 product opportunities.`

Good output shape:

- Identify that this is a reusable `skill prompt`, not a one-off task prompt.
- Add trigger conditions so the skill knows when to activate.
- Convert the rough workflow into a stable sequence of steps.
- Define a report structure that keeps evidence and inference separate.

The final prompt should usually include:

- trigger language such as "Use this skill when..."
- source quality rules
- a section that is explicitly evidence-only
- a final section with concrete opportunities or recommendations

### Example 3: Claude-friendly structured rewrite

Input:

`Rewrite this Claude prompt so it is easier to follow: "Analyze this repo deeply, maybe use tools, probably search the web if needed, and tell me what to do."`

Good output shape:

- Briefly explain that the prompt is underspecified.
- Return one Claude-oriented prompt with tagged structure.
- Make tool expectations and output shape explicit.

The rewritten prompt should usually include:

- `<role>` and `<goal>`
- a `<context>` block that explains when tools or web research are appropriate
- an ordered `<instructions>` block
- an `<output_format>` block
- a `<quality_checks>` block

## Exit criteria

The skill is done when the user has:

- one prompt they can actually use now
- clear assumptions
- a few test prompts to validate behavior

If the prompt still feels speculative, say what is missing instead of pretending it is production-ready.
