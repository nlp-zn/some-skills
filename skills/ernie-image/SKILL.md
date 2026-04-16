---
name: ernie-image
description: 使用百度 AI Studio 的 OpenAI 兼容接口调用 ERNIE-Image 与 ERNIE-Image-Turbo，生成海报、封面、信息图、中文带字图和可复现的多版本出图；当用户提到 ERNIE Image、ERNIE-Image-Turbo、百度文生图、AI Studio 生图、poster、cover、infographic、thumbnail、seed、ratio、use_pe、Smart Optimize，或想把短 prompt 扩成更好的出图提示词时，都应优先使用这个 skill，即使用户没有明确说“写 API 调用”。
compatibility: Requires Python 3, the openai package, and an AI Studio Access Token supplied via AISTUDIO_API_KEY, AISTUDIO_ACCESS_TOKEN, --api-key, --env-file, or the user config file
---

# ERNIE Image

用百度 AI Studio 的 OpenAI 兼容接口调用 `ERNIE-Image` / `ERNIE-Image-Turbo`，并把输出保存为可直接继续使用的图片文件。

如果用户想把这个模型“玩到位”，除了本文件，也要按需阅读 [playbook.md](./references/playbook.md) 和 [archetypes.json](./references/archetypes.json)。前者整理探索到定稿的流程和参数策略，后者提供可复用的原型骨架和扩写模板。

## 默认工作方式

优先把这件事当作“交付一张能直接使用的图”，而不是“随便试一张图”。

执行时遵循这个顺序：

0. 先确认鉴权是否已经准备好；第一次使用时，不要跳过这一步。
1. 先判断用途，再决定比例和尺寸。
2. 短 prompt 先归类成一个原型，再扩写。
3. 先用默认参数跑通，再调高级参数。
4. 先出 1 到 4 个版本做选择，再决定是否继续精调。
5. 优先用脚本 `scripts/ernie_image.py`，不要每次都重新手写一套调用代码。

## 首次使用先做鉴权检查

这是开源 skill，默认要把“用户去哪里拿 token”明确说出来，而不是假设对方已经配好了环境。

首次使用时，按这个顺序引导：

1. 让用户访问 `https://aistudio.baidu.com/account/accessToken`
2. 在 AI Studio 控制台创建或复制自己的 Access Token
3. 用下面任一方式提供给当前环境

### 方式 1：环境变量

```bash
export AISTUDIO_API_KEY="your_access_token"
```

也兼容：

```bash
export AISTUDIO_ACCESS_TOKEN="your_access_token"
```

### 方式 2：命令行参数

```bash
python3 <skill-path>/scripts/ernie_image.py \
  --api-key "your_access_token" \
  --prompt "一只可爱的猫咪坐在窗台上"
```

### 方式 3：本地 env 文件

```bash
cat > .aistudio.env <<'EOF'
AISTUDIO_API_KEY=your_access_token
EOF
```

然后：

```bash
python3 <skill-path>/scripts/ernie_image.py \
  --env-file .aistudio.env \
  --prompt "一只可爱的猫咪坐在窗台上"
```

### 方式 4：让脚本自己打印 setup 指引

```bash
python3 <skill-path>/scripts/ernie_image.py --print-setup
```

### 方式 5：保存到用户级 config，后面直接复用

```bash
python3 <skill-path>/scripts/ernie_image.py \
  --api-key "your_access_token" \
  --save-config
```

默认会保存到：

```bash
~/.config/codex/ernie-image/config.json
```

也可以先查看实际路径：

```bash
python3 <skill-path>/scripts/ernie_image.py --print-config-path
```

如果 agent 发现 token 缺失，不要直接反复重试 API。应该先告诉用户去上面的页面拿 token，再继续后续调用。

## 模型选择

- 默认用 `ERNIE-Image-Turbo`
  适合快速迭代、批量出图、网页封面、社媒图、海报草案、提示词调优。
- 只有当用户明确要求满血版、最高保真、或特别强调最终质量时，才切到 `ERNIE-Image`
- 如果用户没有说清楚，默认解释为“先用 Turbo 快速产出结果”

这样做的原因是：官方介绍里 Turbo 是更适合实际生产使用的高效率版本，也是 AI Studio 体验页主推的快速体验模型。

AI Studio 体验页里的模型心智也值得借用：

- `Flagship`
  细节更丰富，适合最终高质量交付。
- `Speed`
  更适合快速验证创意。
- `Lite`
  更轻量灵活，适合创意探索。

把这个经验映射到本 skill：

1. 先用 `Turbo` 探索方向
2. 用 `Turbo + seed` 锁版
3. 最终需要更高质量时再切满血版

基于 AI Studio 公开示例页的实际观察，还要记住一个细节：

- 公开详情页最稳定暴露的是 `提示词 + 比例 + 像素尺寸`
- `做同款` 最明显的行为，是把案例 prompt 直接回填到创作框
- 公开详情里并不会像 prompt 那样明确强调“这是哪一个模型生成的”

因此在没有更强证据时，把“同款复刻”默认理解为：

1. 先复用 prompt 结构
2. 默认继续用当前最顺手的 `ERNIE-Image-Turbo`
3. 只有用户明确要求满血版时再切 `ERNIE-Image`

## 为什么 ERNIE Image 值得单独用 skill

根据官方资料，这个模型的核心价值不只是“出图”，而是更贴近真实交付：

- ERNIE-Image 是满血版，官方介绍中通常使用约 50 步推理。
- ERNIE-Image-Turbo 是蒸馏版，官方介绍中强调 8 步左右即可快速出图，更适合生产环境迭代。
- ERNIE-Image 基于单流 DiT 架构，并配有轻量 Prompt Enhancer，特别适合把较短、较口语化的需求扩展成更完整的画面描述。
- 星河社区和 AI Studio 的公开体验都在强调海报、封面、结构化画面、带文字内容这类更接近真实发布场景的任务。

## 尺寸与用途

先选比例，再映射到像素尺寸。如果运行时支持 `ratio`，优先传 `ratio`；如果只需要 `size`，再映射成最接近的像素组合。

- `1:1` -> `1024x1024`
- `4:3` -> `2048x1536`
- `16:9` -> `2048x1152`
- `3:4` -> `1536x2048`
- `9:16` -> `1152x2048`

常用 preset 仍然适合做快捷选择：

- `square`
- `avatar`
- `article`
- `poster`
- `story`
- `wallpaper`

如果用户直接说“横版封面”“竖版海报”“方图”，先把比例和用途定下来，再调别的参数。

## Prompt Expansion

官方示例和 AI Studio 体验页都更适合“真实需求描述”而不是纯形容词堆叠。默认按这个顺序组织 prompt：

`用途 -> 场景 -> 主体 -> 构图 -> 留白 -> 文字区 -> 风格气质 -> 干净程度`

短 prompt 要先被扩写，而不是原样丢给模型。默认策略是：

1. 先把用户意图归到一个原型
2. 参考 [archetypes.json](./references/archetypes.json) 里的对应骨架
3. 用用户原话补齐关键内容
4. 短 prompt 默认保留 `use_pe=true`

示例：

`来一张科技感海报`

应该扩成：

`科技新品发布海报，竖版，中心是未来感设备主体，主色偏银灰与电蓝，上方预留标题区域，下方预留中文 slogan 区，整体干净克制，适合产品发布宣传图，不要拥挤。`

如果用户已经给了完整需求，就保留核心内容，只补缺失的版式信息，不要过度改写原意。

## Archetypes

机器可复用的原型骨架放在 [archetypes.json](./references/archetypes.json)。agent 可以直接读这个文件；脚本内置的自动扩写也遵循同一类分类心智。这里保留一层人类可读的分类：

- `cover_poster`
  公众号封面、专栏头图、宣传海报。先保留标题区和主体区。
- `infographic`
  教程图、对比图、知识图谱。先保留模块、标签和说明区。
- `engineering_markup`
  产品拆解、结构示意、工程说明图。先保证主体清晰，再叠标注。
- `viral_thumbnail`
  视频封面、社媒主图、高点击率缩略图。先做强对比和大标题。
- `historical_knowledge`
  朝代服饰、制度演变、时间轴图谱。先把顺序和注释讲清楚。
- `character_ip`
  角色、IP、吉祥物。先锁定身份块，再换场景和动作。

对短需求的判断，不是“这句话还不够长”，而是“这句话还没选画法”。先选原型，再扩写。

## 参数策略

只在确实需要时再调这些参数：

- `ratio`
  先选比例，再映射尺寸；如果 runtime 已经支持 `ratio`，优先直接传。
- `n`
  默认 `1`。做封面、海报、宣传图时，优先尝试 `2` 到 `4`，把单次生成变成选择题。
- `use_pe`
  短 prompt、口语化描述、信息密度不高时默认开启；只有当用户明确想要“原样更忠实的提示词”时才考虑关闭。
- `seed`
  做版本复现、团队协作、A/B 对比时再固定。做多版本探索时，若 runtime 支持 `seed_mode`，优先用 `fixed` / `incremental` / `random` 区分意图。
- `num_inference_steps`
  先用模型默认值；用户明确想要更细致控制或特别提到 Turbo 的 8 步推理时再设。
- `guidance_scale`
  只有当用户明确需要“更贴 prompt”或“更自由发挥”时再调。
- `negative_prompt`
  当模型反复出现不想要的内容时再加，例如拥挤背景、过多小物件、低可读性文字。
- `style`
  用于快速扫风格，例如 `Photographic`、`Anime`、`Cinematic`、`Digital Art`。
- `sampler_index`
  进阶用户调采样器时再动，默认不要过早参与。

AI Studio 页面里把 `seed` 叫做 `Style Seed`。可以把它理解为“创意锁定器”：

- 同 prompt + 同 seed：尽量复现
- 同 seed + 小改 prompt：做稳定 A/B
- 新 seed：重新找构图
- `fixed`：锁住一个方向
- `incremental`：做一组轻微变化的版本
- `random`：用来重新找构图或风格

不要一上来把所有参数都扫一遍。推荐顺序始终是：

1. 跑默认值
2. 调 `ratio` / `size`
3. 调 `n`
4. 选 `seed` / `seed_mode`
5. 最后再动 `negative_prompt` / `style` / `steps` / `guidance_scale`

## 官方参数地图

这个 skill 同时兼容两套说法：

- AI Studio 文档侧：
  `negative_prompt` / `ratio` / `size` / `n` / `steps` / `style` / `sampler_index` / `seed` / `cfg_scale`
- 官方公众号玩法侧：
  `use_pe` / `seed` / `seed_mode` / `num_inference_steps` / `guidance_scale`

脚本里已经兼容这些常见字段和别名，优先用用户更熟悉的那套说法即可。

## 使用脚本

优先使用：

```bash
python3 <skill-path>/scripts/ernie_image.py \
  --prompt "一只可爱的猫咪坐在窗台上" \
  --model ERNIE-Image-Turbo \
  --ratio 1:1 \
  --size 1024x1024 \
  --n 1
```

如果 runtime 已经支持 `ratio`，先传 `ratio` 再映射到具体 `size`。如果只支持 `size`，就直接用最接近的像素组合。

### 先预览 URL

```bash
python3 <skill-path>/scripts/ernie_image.py \
  --prompt "一只可爱的猫咪坐在窗台上" \
  --ratio 1:1 \
  --response-format url
```

### 一次生成多版

```bash
python3 <skill-path>/scripts/ernie_image.py \
  --prompt "未来感城市夜景，横版16:9，左侧留标题留白，适合作为AI专栏封面图" \
  --preset article \
  --ratio 16:9 \
  --n 4
```

如果是 `response_format=url` 且 `n>1`，脚本现在默认会走 `--batch-mode auto`，自动改成更稳的串行单图请求，再把 4 个 URL 汇总回来。这样做是为了避免 AI Studio 在“多图 URL 预览”场景里偶发长时间挂起。

### 固定 seed 做可复现版本

```bash
python3 <skill-path>/scripts/ernie_image.py \
  --prompt "极简科技风产品海报，银灰主色，中心主体，留出中文标题区" \
  --seed 42 \
  --use-pe true \
  --num-inference-steps 8 \
  --guidance-scale 1.0
```

### 海报玩法：一次扫 4 张

```bash
python3 <skill-path>/scripts/ernie_image.py \
  --prompt "极简科技新品海报，竖版，中心是银灰色智能设备主体，上方留主标题区域，下方留 slogan 区域，高对比，适合作为产品发布海报" \
  --preset poster \
  --ratio 9:16 \
  --n 4 \
  --response-format url
```

### 风格玩法：快速扫 style

```bash
python3 <skill-path>/scripts/ernie_image.py \
  --prompt "未来机器人站在霓虹城市街头，电影感构图" \
  --style Cinematic \
  --preset wallpaper
```

### 做同款玩法：锁 seed 再改一个变量

```bash
python3 <skill-path>/scripts/ernie_image.py \
  --prompt "未来感城市夜景，左侧标题留白，右侧机器人 IP，适合作为 AI 专栏封面" \
  --preset article \
  --seed 42 \
  --style Cinematic
```

然后只改一个变量，例如 `style` 从 `Cinematic` 改成 `Photographic`，而不是整段 prompt 全改。

### 精修玩法：先 dry run 看 payload

```bash
python3 <skill-path>/scripts/ernie_image.py \
  --prompt "AI 专栏封面，左侧标题留白，右侧机器人 IP" \
  --preset article \
  --seed 42 \
  --use-pe true \
  --dry-run
```

### 控制多图请求策略

```bash
python3 <skill-path>/scripts/ernie_image.py \
  --prompt "AI 技术专栏封面，左侧留标题留白，右侧机器人 IP" \
  --preset article \
  --n 4 \
  --response-format url \
  --batch-mode auto
```

- `auto`
  默认值；多图 URL 预览时自动走串行单图请求。
- `batch`
  强制一次性批量请求。
- `serial`
  强制逐张请求；如果传了 `seed`，会按 `seed, seed+1, seed+2...` 递增，避免多张完全重复。

## 环境准备

如果当前环境还没准备好，按这个顺序处理：

1. 先执行下面的 setup 帮助，确认当前用户知道 token 要去哪里拿：

```bash
python3 <skill-path>/scripts/ernie_image.py --print-setup
```

2. 让用户到 `https://aistudio.baidu.com/account/accessToken` 获取 Access Token
3. 设置环境变量：

```bash
export AISTUDIO_API_KEY="your_access_token"
```

4. 安装依赖：

```bash
pip install openai
```

如果这个环境会反复用这个 skill，更推荐在拿到 token 后执行一次：

```bash
python3 <skill-path>/scripts/ernie_image.py \
  --api-key "your_access_token" \
  --save-config
```

这样后面再次运行时，就不需要每次都显式传 `--api-key` 或 `--env-file`。

如果当前终端有代理环境，且出现 SOCKS 相关错误，先尝试针对单次命令临时取消代理变量再运行。

## 输出要求

完成任务时：

- 如果是 `b64_json`，把图片实际落盘到目录中，不要只停留在内存里。
- 如果是 `url`，输出 URL，同时写入 `urls.json` 方便后续继续处理。
- 明确告诉用户生成结果保存在哪个目录。
- 如果用了 `seed`、`size`、`n` 或其他关键参数，顺手在结果里说明，方便复现。

## 你该怎么响应用户

- 用户要“先看看效果”：优先 `response_format=url`
- 用户要“拿去交付”或“入库”：优先 `response_format=b64_json`
- 用户要“出几版让我挑”：把 `n` 开到 `2` 到 `4`
- 用户只给了很短的一句话：默认保留 `use_pe=true`
- 用户给的是海报/封面/宣传图任务：主动帮他补齐尺寸、留白、文字位置、构图信息
- 如果当前环境缺少 token：先给出 `https://aistudio.baidu.com/account/accessToken` 和 `--print-setup` 路径，不要盲目继续请求
- 用户说“想多试几版”“先找方向”：优先走 `Turbo + url + n=4`
- 用户说“先锁版式再细化”：固定 `seed`
- 用户说“这张图老是太乱”：引导他加 `negative_prompt` 和留白描述
- 用户说“我要试几种视觉方向”：优先扫 `style`，而不是一开始改一堆别的参数
- 用户只给一句很短的需求：主动做 prompt 补全，并默认保留 `use_pe=true`
- 用户说“按这个风格再来一个”或“做同款”：保留核心构图块，尽量锁 `seed`，一次只改一个变量
- 用户明确说这个环境会长期复用：优先建议 `--save-config`，把 token 存到用户级 config，不要存进 repo

## 参考事实

这个 skill 的默认策略基于以下公开信息：

- ERNIE-Image 是满血版本；官方介绍中提到通常使用约 50 步推理。
- ERNIE-Image-Turbo 是蒸馏版本；官方介绍中提到通常只需 8 步推理，更强调速度与生产可用性。
- AI Studio 体验页强调文生图、多风格视觉内容创作，并支持在网页端免费体验。
- 官方正文给出的 API 写法是 OpenAI 兼容的 `client.images.generate(...)` 风格。
- AI Studio 文档中公开了 `negative_prompt`、`steps`、`style`、`sampler_index`、`seed`、`cfg_scale` 等图像参数。
