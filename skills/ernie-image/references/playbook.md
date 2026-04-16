# ERNIE Image Playbook

## What This Model Is Good At

Use ERNIE-Image and ERNIE-Image-Turbo for outputs that need to be publishable, editable, and production-adjacent:

- Article covers
- Poster and flyer drafts
- Social promo graphics
- Robot / mascot / IP concepts
- Text-bearing Chinese covers
- Structured compositions with explicit white space

The official materials emphasize that ERNIE Image is not only for "pretty one-off images", but for content that can be shipped, revised, and reused.

For prompt expansion, keep the machine-friendly archetype data in [archetypes.json](./archetypes.json). This playbook explains how to use it; the JSON file carries the repeatable skeletons.

The AI Studio product framing is also useful:

- `Flagship`: richer detail, better for high-quality final work
- `Speed`: fast generation, best for quick idea validation
- `Lite`: lightweight and flexible, useful for broader creative exploration

Map that mindset into the skill:

- explore with `Turbo`
- lock direction with `Turbo + seed`
- finish with the highest quality model the user wants

## Best Workflow: Explore -> Lock -> Finish

### 1. Explore quickly

Use this when direction is still fuzzy:

- `model=ERNIE-Image-Turbo`
- `response_format=url`
- `n=4`
- short but specific prompt
- `use_pe=true`
- choose `ratio` first, then map to the closest size

Goal: find the right direction cheaply.

### 2. Lock composition

Once one direction is close:

- reduce to `n=1` or `n=2`
- add exact layout constraints
- add explicit "left blank area", "top title space", "bottom slogan area"
- set `seed` for reproducibility

Goal: convert "nice image" into "usable deliverable."

### 3. Finish for delivery

When the concept is approved:

- switch to `b64_json`
- use final output size
- keep the winning `seed`
- increase `steps` or `num_inference_steps` only if needed
- add a short `negative_prompt` to remove recurring flaws

Goal: stable output and local files for downstream use.

## Prompt Rescue and Archetypes

Many users will only say something like `来一张科技感海报`. Do not pass that through untouched.

Use the machine-friendly skeleton in [archetypes.json](./archetypes.json) as the canonical reference, then expand with:

`用途 + 场景 + 主体 + 构图 + 留白 + 文字区 + 风格气质 + 干净程度`

If the original ask is short or vague, keep `use_pe=true` by default. That matches AI Studio's `Smart Optimize` behavior and usually produces a better first draft.

Examples:

- `来一张科技感海报`
  Expand to a poster brief with a clear subject, one title zone, one slogan zone, and explicit whitespace.
- `帮我做一个讲 AI 工作流的图`
  Expand to an infographic brief with modules, labels, and a Chinese title.
- `给我一个硬核一点的产品图`
  Expand to an engineering markup or exploded-view brief.

The core idea is simple:

1. classify the request
2. expand the prompt
3. preserve the layout brief
4. only then decide whether to sweep `style`, `seed`, or `negative_prompt`

When the task is structured, write the prompt like a designer brief, not like a caption.

## What `做同款` Seems To Preserve

Observed from the public page:

- detail pages consistently expose prompt, ratio, and pixel size
- the remix flow clearly reuses the prompt text
- the page still foregrounds `ERNIE-Image-Turbo` as the current creation model

Inference:

- the public "make one like this" workflow is mainly a prompt-structure reuse pattern
- for skill design, it is safer to preserve the prompt skeleton first, and only switch models if the user explicitly asks for a higher-quality final pass

This is why the skill should default to:

1. reuse the composition skeleton
2. keep `Turbo` for iteration
3. lock `seed` when comparing revisions

## Text Rendering Tricks

If the image contains text:

- Keep on-image text short
- Ask for one title, not three paragraphs
- Ask for a large quiet area around the text
- Explicitly mention language when necessary: `中文海报字`
- Prefer high contrast and uncluttered background behind the text

Bad:

`画面里放很多中文说明文字，内容丰富`

Better:

`左上角放简短中文标题“AI工作流”，大字，高对比，标题区域背景干净，不要被主体遮挡`

## White Space Tricks

ERNIE Image is more controllable when white space is described as a design requirement, not an afterthought.

Good patterns:

- `左侧留出标题区域`
- `上方留品牌 logo 区`
- `底部预留中文 slogan 位置`
- `整体不要拥挤，构图平衡`

## Seed-Based Refinement

Use a fixed `seed` when:

- comparing prompt variants
- reviewing with teammates
- generating version A / B / C from the same base
- iterating on text placement or white space

Change one thing at a time:

1. keep `seed` fixed
2. change only layout wording, or only style wording, or only the text block
3. compare

AI Studio labels this as `Style Seed`. Treat it as a creative lock:

- same seed + same prompt -> stable reproduction
- same seed + one prompt change -> cleaner A/B comparison
- new seed -> fresh composition search
- `fixed` is the default choice when you want reproducibility
- `incremental` is the right choice when you want a controlled sweep
- `random` is the right choice when you want to search for a new composition

## Parameter Strategy

### Core

- `ratio`: choose for destination first when the runtime supports it
- `size`: choose the closest pixel fallback when `ratio` is unavailable
- `n`: use `2-4` for exploration, `1-2` for refinement
- `response_format=url`: preview quickly
- `response_format=b64_json`: final save

### Creative control

- `use_pe=true`: good for short, natural-language prompts; default it on unless the user wants literal wording
- `negative_prompt`: useful when outputs repeat known defects
- `style`: useful for fast visual sweeps such as `Photographic`, `Anime`, `Cinematic`, `Digital Art`

### Precision control

- `seed`: lock a direction
- `seed_mode`: `fixed`, `incremental`, or `random` depending on whether you want reproducibility, a sweep, or fresh search
- `steps` / `num_inference_steps`: increase only after the concept is already right
- `cfg_scale` / `guidance_scale`: raise when the model drifts away from the prompt; lower when it feels too rigid
- `sampler_index`: advanced users only; use to explore rendering behavior after the concept is stable

## Three Reliable Play Modes

### Mode A: Poster sprint

- `preset=poster`
- `ratio=9:16` or `16:9`, depending on the destination
- `n=4`
- `response_format=url`
- prompt includes text area + focal product

### Mode B: Cover lock

- `preset=article`
- `ratio=16:9`
- `seed` fixed
- `n=2`
- text short and explicit

### Mode C: Wallpaper polish

- `preset=wallpaper`
- `ratio=16:9` or `9:16`
- no text
- strong atmosphere + clean subject hierarchy
- optional style sweep across 2-3 runs

### Mode D: Make-one-like-this

The AI Studio gallery exposes a `做同款 / Remake` behavior. Recreate that pattern inside the skill:

1. identify the winning image category
2. preserve the core composition block
3. keep the same `seed` if consistency matters
4. only change one of:
   - topic
   - subject identity
   - style
   - text block

This is often better than writing a brand-new prompt from scratch.

### Mode E: Gallery archetype rescue

Use this when the user gives a very short request.

1. classify the request as cover, infographic, engineering markup, thumbnail, historical card, or character
2. expand the request into the matching gallery-style structure
3. keep `use_pe=true`
4. only after that decide whether to add style sweeps or seed locking

Examples:

- `来一张科技感海报`
  Turn it into a poster brief with focal subject, title zone, and clean negative space.
- `帮我做一个讲 AI 工作流的图`
  Turn it into an infographic brief with modules, labels, and Chinese title.
- `给我一个硬核产品图`
  Turn it into an engineering markup or exploded-view brief.

## Common Failure Modes

### Too many adjectives

If the result feels muddy, remove decorative adjectives and specify layout instead.

### No destination in mind

If the user says "make a good image", decide whether this is for square, article, poster, or wallpaper before generating.

### Text area not preserved

If text is getting crowded out, explicitly ask for:

- one side blank
- minimal foreground clutter
- balanced composition

### Over-tuning too early

Do not start with every advanced parameter turned on. Explore first, then lock.
