# OpenAI Prompting Notes

These notes are a compact synthesis of official OpenAI prompting guidance checked on 2026-04-18. Treat the linked docs as the source of truth if you need to verify a detail.

## Primary sources

- Prompting overview: https://developers.openai.com/api/docs/guides/prompting
- Prompt optimizer: https://developers.openai.com/api/docs/guides/prompt-optimizer
- GPT-5.2 Prompting Guide: https://developers.openai.com/cookbook/examples/gpt-5/gpt-5-2_prompting_guide
- Codex Prompting Guide: https://developers.openai.com/cookbook/examples/gpt-5/codex_prompting_guide

## What to carry into prompt writing

### 1. Put stable behavior in stable places

OpenAI's docs separate long-lived prompt objects from one-off task messages. When turning a workflow into a reusable prompt, keep stable instructions in the reusable layer and keep task-specific details in the run-specific layer.

Practical implication:

- system prompt or skill: lasting behavior, defaults, tone, tool rules
- task prompt: the deliverable, inputs, and one-off constraints

### 2. Be explicit about output shape and verbosity

The GPT-5.2 guide strongly favors clear output-shape constraints. It also shows that modern models benefit from literal verbosity controls such as "3-6 sentences", "up to 5 bullets", or an exact schema.

Practical implication:

- tell the model how long the response should be
- specify whether prose, bullets, JSON, or another schema is required
- if the task must stay narrow, explicitly forbid extra features or styling

### 3. Scope drift is a real failure mode

The GPT-5.2 guide calls out unnecessary embellishment, especially in frontend and coding workflows. Prompts should say what not to add, not just what to do.

Practical implication:

- say "implement exactly and only what is requested" when overbuilding is risky
- define the simplest valid interpretation when ambiguity should not expand scope

### 4. Research tasks need a research bar

The GPT-5.2 guide recommends setting expectations for source coverage, contradiction resolution, and citation quality in the prompt.

Practical implication:

- define whether the model should stop after a quick answer or continue deeper
- say whether second-order leads should be followed
- require citations or source verification when needed

### 5. Tool use should be described directly

The Codex Prompting Guide and OpenAI agent-style prompts work best when tools, progress updates, and editing behavior are specified in straightforward operational language.

Practical implication:

- tell the model when to inspect before answering
- tell it when to act directly versus when to ask
- define update cadence if the agent is interactive

### 6. Reasoning and migration should be changed one variable at a time

The GPT-5.2 migration guidance recommends switching models first, pinning reasoning effort, running evals, and only then making targeted prompt changes.

Practical implication:

- do not change model, prompt, and evaluation criteria all at once
- when debugging a prompt, isolate one suspected failure mode at a time

### 7. Use metaprompting for targeted repairs

The Codex Prompting Guide explicitly recommends asking the model to propose instruction changes after a weak turn, especially for issues like slow starts, awkward updates, or overthinking.

Practical implication:

- after a bad run, ask what instruction change would reduce that exact failure mode
- keep the repair generalized, not tied to a single example

### 8. Use evals and human review, not vibes alone

The prompting overview says to rerun linked evals when publishing new versions. The prompt optimizer guide says optimized prompts still need manual review.

Practical implication:

- every prompt revision should have at least a small test set
- for important prompts, pair human review with graders or eval prompts

## OpenAI-oriented prompt heuristics

When writing prompts for OpenAI or Codex agents, prefer this order:

1. role or job
2. task objective
3. context and available inputs
4. workflow or tool rules
5. scope boundaries
6. output contract
7. verification or escalation rule

This order maps well to OpenAI's current guidance for coding and agentic systems.
