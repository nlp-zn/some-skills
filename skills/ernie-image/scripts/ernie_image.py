#!/usr/bin/env python3
"""Generate images with ERNIE-Image via AI Studio's OpenAI-compatible API."""

from __future__ import annotations

import argparse
import base64
import copy
import json
import os
import shlex
from functools import lru_cache
import re
import secrets
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


DEFAULT_BASE_URL = "https://aistudio.baidu.com/llm/lmapi/v3"
DEFAULT_MODEL = "ERNIE-Image-Turbo"
DEFAULT_SIZE = "1024x1024"
TOKEN_ENV_VARS = ("AISTUDIO_API_KEY", "AISTUDIO_ACCESS_TOKEN")
DEFAULT_CONFIG_PATH = Path.home() / ".config" / "codex" / "ernie-image" / "config.json"
SCRIPT_PATH = Path(__file__).resolve()
ARCHETYPE_REFERENCE_PATH = SCRIPT_PATH.parent.parent / "references" / "archetypes.json"
PRESET_SIZES = {
    "square": "1024x1024",
    "avatar": "1536x1536",
    "article": "2048x1536",
    "poster": "1536x2048",
    "story": "1152x2048",
    "wallpaper": "2048x1152",
}
RATIO_SIZES = {
    "1:1": "1024x1024",
    "4:3": "2048x1536",
    "3:4": "1536x2048",
    "16:9": "2048x1152",
    "9:16": "1152x2048",
    "3:2": "1536x1024",
    "2:3": "1024x1536",
}
ARCHETYPE_CHOICES = (
    "auto",
    "image",
    "portrait",
    "poster",
    "cover_poster",
    "infographic",
    "engineering_markup",
    "historical_knowledge",
    "character_ip",
    "thumbnail",
    "viral_thumbnail",
    "wallpaper",
    "product",
    "logo",
    "scene",
)
SHORT_PROMPT_CHAR_LIMIT = 28
SHORT_PROMPT_WORD_LIMIT = 6


def build_setup_instructions() -> str:
    script_path = shlex.quote(str(SCRIPT_PATH))
    lines = [
        "AI Studio ERNIE Image setup",
        "",
        "1. Open the Access Token page:",
        "   https://aistudio.baidu.com/account/accessToken",
        "2. Create or copy your Access Token.",
        "3. Provide it using one of these methods:",
        "",
        "Environment variable:",
        '  export AISTUDIO_API_KEY="your_access_token"',
        "",
        "Alternative environment variable:",
        '  export AISTUDIO_ACCESS_TOKEN="your_access_token"',
        "",
        "Direct CLI argument:",
        '  --api-key "your_access_token"',
        "",
        "Env file:",
        "  echo 'AISTUDIO_API_KEY=your_access_token' > .aistudio.env",
        f"  python3 {script_path} --env-file .aistudio.env --prompt '一只可爱的猫咪坐在窗台上'",
        "",
        "Optional user config:",
        f"  python3 {script_path} --api-key \"your_access_token\" --save-config",
        "",
        "Then run the generator again.",
    ]
    return "\n".join(lines)


def build_preset_guide() -> str:
    lines = ["Available presets", ""]
    for name, size in PRESET_SIZES.items():
        lines.append(f"- {name}: {size}")
    lines.append("")
    lines.append("You can still override a preset by passing --size explicitly.")
    lines.append("")
    lines.append("Aspect ratios")
    lines.append("")
    for ratio, size in RATIO_SIZES.items():
        lines.append(f"- {ratio}: {size}")
    lines.append("")
    lines.append("You can still override a ratio by passing --size explicitly.")
    return "\n".join(lines)


def normalize_prompt(prompt: str) -> str:
    return " ".join(prompt.strip().split())


def canonicalize_archetype(archetype: str) -> str:
    mapping = {
        "cover_poster": "poster",
        "viral_thumbnail": "thumbnail",
        "character_ip": "portrait",
    }
    return mapping.get(archetype, archetype)


@lru_cache(maxsize=1)
def load_archetype_reference() -> dict[str, Any]:
    if not ARCHETYPE_REFERENCE_PATH.exists():
        return {}
    try:
        return json.loads(ARCHETYPE_REFERENCE_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def lookup_archetype_from_reference(prompt: str) -> str | None:
    lowered = normalize_prompt(prompt).lower()
    data = load_archetype_reference()
    for item in data.get("archetypes", []):
        archetype_id = item.get("id")
        aliases = item.get("aliases", [])
        if not archetype_id:
            continue
        lowered_aliases = [str(alias).lower() for alias in aliases]
        if any(alias in lowered for alias in lowered_aliases):
            return canonicalize_archetype(archetype_id)
    return None


def is_short_or_vague_prompt(prompt: str) -> bool:
    normalized = normalize_prompt(prompt)
    if not normalized:
        return True
    if len(normalized) <= SHORT_PROMPT_CHAR_LIMIT:
        return True
    word_count = len(re.findall(r"[A-Za-z0-9]+|[\u4e00-\u9fff]", normalized))
    if word_count <= SHORT_PROMPT_WORD_LIMIT and len(normalized) <= 80:
        return True
    vague_starters = (
        "画",
        "画个",
        "画一张",
        "来一张",
        "做一个",
        "做一张",
        "生成",
        "帮我画",
        "帮我做",
        "帮我生成",
        "给我",
        "a",
        "an",
        "make",
        "create",
        "generate",
        "draw",
    )
    lowered = normalized.lower()
    if lowered.startswith(vague_starters):
        return True
    generic_terms = (
        "猫",
        "狗",
        "人物",
        "人像",
        "海报",
        "封面",
        "信息图",
        "壁纸",
        "logo",
        "图标",
        "插画",
        "缩略图",
    )
    if any(term.lower() in lowered for term in generic_terms) and len(normalized) <= 60:
        return True
    if len(normalized) <= 45 and all(sep not in normalized for sep in (",", "，", "；", "、", ";", ":", "：")):
        return True
    return False


def infer_archetype(prompt: str) -> str:
    referenced = lookup_archetype_from_reference(prompt)
    if referenced:
        return referenced

    lowered = normalize_prompt(prompt).lower()
    keyword_groups = [
        ("infographic", ("信息图", "流程图", "结构图", "知识图谱", "infographic", "diagram", "flowchart")),
        ("poster", ("海报", "banner", "poster", "封面", "cover", "宣传图")),
        ("thumbnail", ("缩略图", "thumbnail", "video cover", "封面图")),
        ("engineering_markup", ("工程标注", "拆解图", "结构示意", "exploded view", "engineering markup")),
        ("historical_knowledge", ("历史图谱", "知识图谱", "时间轴", "history card", "knowledge card")),
        ("character_ip", ("角色", "吉祥物", "mascot", "character", "ip形象", "角色ip")),
        ("wallpaper", ("壁纸", "wallpaper", "桌面背景", "background")),
        ("logo", ("logo", "图标", "icon", "标志")),
        ("product", ("产品", "电商", "商品", "product", "packshot", "包装")),
        ("portrait", ("头像", "人像", "人物", "肖像", "portrait", "person", "cat", "dog", "pet", "猫", "狗", "宠物")),
        ("scene", ("漫画", "插画", "illustration", "anime", "卡通", "场景", "scene")),
    ]
    for archetype, keywords in keyword_groups:
        if any(keyword.lower() in lowered for keyword in keywords):
            return archetype
    return "image"


def infer_orientation(size: str) -> str:
    try:
        width_str, height_str = size.lower().split("x", 1)
        width = int(width_str)
        height = int(height_str)
    except (ValueError, TypeError):
        return "square"
    if width > height * 1.15:
        return "landscape"
    if height > width * 1.15:
        return "portrait"
    return "square"


def uses_cjk_language(prompt: str) -> bool:
    return bool(re.search(r"[\u4e00-\u9fff]", prompt))


def build_archetype_clauses(archetype: str, orientation: str, size: str, *, chinese: bool) -> list[str]:
    archetype = canonicalize_archetype(archetype)
    clauses: list[str] = []
    if chinese:
        orientation_clauses = {
            "landscape": "使用横向构图",
            "portrait": "使用竖向构图",
            "square": "使用平衡居中的构图",
        }
    else:
        orientation_clauses = {
            "landscape": "use a wide horizontal composition",
            "portrait": "use a tall vertical composition",
            "square": "use a balanced centered composition",
        }
    clauses.append(orientation_clauses.get(orientation, orientation_clauses["square"]))

    if archetype == "poster":
        clauses.extend(
            [
                "把它当作一张完成度高的商业海报来设计" if chinese else "treat it like a polished commercial poster",
                "为标题或主文案预留清晰留白" if chinese else "leave clear negative space for title copy",
                "让视觉层级一眼就能看懂" if chinese else "keep the visual hierarchy obvious at a glance",
            ]
        )
    elif archetype == "infographic":
        clauses.extend(
            [
                "把画面组织成清晰可读的分区" if chinese else "structure the image into readable sections",
                "使用标签、箭头、图标和明确的信息层级" if chinese else "use labels, arrows, icons, and clear information hierarchy",
                "保持版式干净、整齐、适合直接展示" if chinese else "keep the layout clean, organized, and presentation-ready",
            ]
        )
    elif archetype == "thumbnail":
        clauses.extend(
            [
                "让主体足够大，缩略图里一眼能看清" if chinese else "make the focal subject large and instantly readable",
                "使用高对比和简单背景" if chinese else "use high contrast and a simple background",
                "如果需要，给大标题预留空间" if chinese else "leave room for a bold headline block if needed",
            ]
        )
    elif archetype == "wallpaper":
        clauses.extend(
            [
                "让画面有电影感和空间感" if chinese else "make it feel cinematic and spacious",
                "背景保持氛围感但细节不要太吵" if chinese else "keep the background atmospheric with subtle detail",
            ]
        )
    elif archetype == "product":
        clauses.extend(
            [
                "使用棚拍光线和干净高级的背景" if chinese else "use studio lighting and a clean premium backdrop",
                "把主体展示清楚，材质细节要利落" if chinese else "show the subject clearly with crisp material detail",
            ]
        )
    elif archetype == "engineering_markup":
        clauses.extend(
            [
                "先把主体展示清楚，再叠加工程标注、箭头和说明" if chinese else "show the object clearly first, then layer engineering notes, arrows, and callouts",
                "让标注成为第二层信息，不要喧宾夺主" if chinese else "make annotations a second layer of information instead of overwhelming the subject",
            ]
        )
    elif archetype == "historical_knowledge":
        clauses.extend(
            [
                "把它当作教学型知识图谱来组织" if chinese else "treat it like an instructional knowledge card",
                "明确主体顺序、对比维度和注释区域" if chinese else "make subject order, comparison dimensions, and annotation zones explicit",
            ]
        )
    elif archetype == "logo":
        clauses.extend(
            [
                "保持极简和图标感" if chinese else "keep the design minimal and icon-like",
                "强调干净边缘、简单形状和高识别度" if chinese else "favor clean edges, simple shapes, and high legibility",
            ]
        )
    elif archetype == "portrait":
        clauses.extend(
            [
                "让主体显得亲切，构图清楚" if chinese else "make the subject feel friendly and clearly framed",
                "用柔和自然光突出脸部、毛发或主体细节" if chinese else "emphasize face, fur, or subject detail with soft natural lighting",
            ]
        )
    elif archetype == "scene":
        clauses.extend(
            [
                "让环境逻辑统一、视觉有吸引力" if chinese else "keep the environment coherent and visually engaging",
                "平衡主体、背景和叙事细节" if chinese else "balance the subject, background, and storytelling details",
            ]
        )
    else:
        clauses.extend(
            [
                "让画面干净、容易读懂" if chinese else "keep the composition clean and easy to read",
                "让主体一眼就能看明白" if chinese else "make the main subject obvious at a glance",
            ]
        )

    if size in {"2048x1536", "1536x2048", "2048x1152", "1152x2048"}:
        clauses.append("保留足够细节，保证最终成片质量" if chinese else "preserve enough detail for a high-quality final image")

    return clauses


def build_prompt_plan(
    *,
    prompt: str,
    size: str,
    explicit_archetype: str | None,
    style: str | None,
) -> dict[str, Any]:
    original_prompt = normalize_prompt(prompt)
    archetype = canonicalize_archetype(explicit_archetype or infer_archetype(original_prompt))
    short_or_vague = is_short_or_vague_prompt(original_prompt)
    should_expand = short_or_vague or archetype != "image" or bool(style)
    orientation = infer_orientation(size)
    chinese = uses_cjk_language(original_prompt)

    expanded_prompt = original_prompt
    prompt_clauses = [original_prompt]
    if should_expand:
        prompt_clauses.extend(build_archetype_clauses(archetype, orientation, size, chinese=chinese))
        if style:
            prompt_clauses.append(f"使用 {style} 风格" if chinese else f"use a {style} visual style")
        if archetype in {"poster", "thumbnail", "infographic"}:
            prompt_clauses.append("避免杂乱，保持版式有明确设计感，并让结果看起来可直接交付" if chinese else "avoid clutter, keep the layout deliberate, and make the result feel production-ready")
        joiner = "，" if chinese else ", "
        expanded_prompt = joiner.join(dict.fromkeys(prompt_clauses))

    effective_use_pe = should_expand
    return {
        "original_prompt": original_prompt,
        "expanded_prompt": expanded_prompt,
        "archetype": archetype,
        "orientation": orientation,
        "prompt_was_expanded": expanded_prompt != original_prompt,
        "should_expand": should_expand,
        "effective_use_pe": effective_use_pe,
    }


def load_env_file(env_file: str | None) -> dict[str, str]:
    if not env_file:
        return {}

    path = Path(env_file).expanduser().resolve()
    if not path.exists():
        raise SystemExit(f"Env file not found: {path}")

    loaded: dict[str, str] = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        loaded[key.strip()] = value.strip().strip("'").strip('"')
    return loaded


def resolve_config_path(config_path: str | None) -> Path:
    if config_path:
        return Path(config_path).expanduser().resolve()
    return DEFAULT_CONFIG_PATH


def load_config_file(config_path: Path) -> dict[str, Any]:
    if not config_path.exists():
        return {}
    try:
        return json.loads(config_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Invalid config JSON: {config_path}\n{exc}") from exc


def save_config_file(config_path: Path, config: dict[str, Any]) -> None:
    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text(
        json.dumps(config, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    try:
        os.chmod(config_path, 0o600)
    except OSError:
        pass


def resolve_api_key(args: argparse.Namespace) -> str | None:
    if args.api_key:
        return args.api_key

    env_values = load_env_file(args.env_file)
    for key in TOKEN_ENV_VARS:
        if env_values.get(key):
            return env_values[key]

    for key in TOKEN_ENV_VARS:
        if os.environ.get(key):
            return os.environ[key]

    config_path = resolve_config_path(args.config)
    config = load_config_file(config_path)
    for key in ("api_key", "aistudio_api_key", *TOKEN_ENV_VARS):
        if config.get(key):
            return config[key]

    return None


def parse_bool(value: str) -> bool:
    lowered = value.strip().lower()
    if lowered in {"1", "true", "yes", "y", "on"}:
        return True
    if lowered in {"0", "false", "no", "n", "off"}:
        return False
    raise argparse.ArgumentTypeError(f"Invalid boolean value: {value}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate images with ERNIE-Image / ERNIE-Image-Turbo."
    )
    parser.add_argument("--prompt", help="Prompt used for image generation.")
    parser.add_argument("--negative-prompt", help="Things the image should avoid.")
    parser.add_argument("--model", default=DEFAULT_MODEL, help="Model name.")
    parser.add_argument("--size", default=DEFAULT_SIZE, help="Image size, e.g. 1024x1024.")
    parser.add_argument(
        "--ratio",
        choices=tuple(RATIO_SIZES),
        help="Aspect ratio shortcut that maps to a size when --size is left at its default.",
    )
    parser.add_argument(
        "--preset",
        choices=tuple(PRESET_SIZES),
        help="Convenience preset for common output shapes. --size still wins if both are set.",
    )
    parser.add_argument("--n", type=int, default=1, help="Number of images to generate (1-4 recommended).")
    parser.add_argument(
        "--response-format",
        choices=("b64_json", "url"),
        default="b64_json",
        help="How the API should return image results.",
    )
    parser.add_argument(
        "--batch-mode",
        choices=("auto", "batch", "serial"),
        default="auto",
        help="How to issue multi-image requests. auto defaults to serial single-image calls for URL previews with n>1.",
    )
    parser.add_argument("--api-key", help="AI Studio access token. Defaults to AISTUDIO_API_KEY.")
    parser.add_argument("--env-file", help="Optional .env-style file containing AISTUDIO_API_KEY or AISTUDIO_ACCESS_TOKEN.")
    parser.add_argument(
        "--config",
        help=f"Optional config JSON path. Defaults to {DEFAULT_CONFIG_PATH}.",
    )
    parser.add_argument(
        "--save-config",
        action="store_true",
        help="Persist the resolved API key into the user config file for future runs.",
    )
    parser.add_argument(
        "--print-config-path",
        action="store_true",
        help="Print the default config path and exit.",
    )
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL, help="AI Studio OpenAI-compatible base URL.")
    parser.add_argument(
        "--request-timeout",
        type=float,
        default=180.0,
        help="HTTP request timeout in seconds for each API call.",
    )
    parser.add_argument("--outdir", help="Directory for generated outputs.")
    parser.add_argument("--seed", type=int, help="Optional fixed seed.")
    parser.add_argument(
        "--seed-mode",
        choices=("auto", "fixed", "incremental", "random"),
        default="auto",
        help="Seed strategy for serial multi-image runs. Auto keeps the old incremental behavior when a seed is provided.",
    )
    parser.add_argument("--use-pe", type=parse_bool, help="Override prompt enhancement. If omitted, the script auto-enables it for short or underspecified prompts.")
    parser.add_argument(
        "--archetype",
        choices=ARCHETYPE_CHOICES,
        default="auto",
        help="Prompt archetype used for built-in expansion. Auto infers poster, infographic, portrait, wallpaper, and similar structures.",
    )
    parser.add_argument("--style", help="Optional style name, for example Photographic, Anime, Cinematic.")
    parser.add_argument("--steps", type=int, help="Iteration steps. AI Studio docs suggest 10-50.")
    parser.add_argument("--sampler-index", help="Optional sampler name such as Euler a or DPM++ 2M.")
    parser.add_argument("--cfg-scale", type=float, help="Prompt adherence / cfg scale.")
    parser.add_argument("--num-inference-steps", type=int, help="Optional inference step count.")
    parser.add_argument("--guidance-scale", type=float, help="Optional guidance scale.")
    parser.add_argument(
        "--print-setup",
        action="store_true",
        help="Print setup instructions for obtaining and configuring the AI Studio Access Token.",
    )
    parser.add_argument(
        "--list-presets",
        action="store_true",
        help="Print the built-in size presets and exit.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the request payload without calling the API.",
    )
    return parser


def require_openai() -> Any:
    try:
        from openai import OpenAI
    except ImportError as exc:
        raise SystemExit(
            "Missing dependency: openai. Install it with `pip install openai`."
        ) from exc
    return OpenAI


def resolve_outdir(path_arg: str | None, *, create: bool = True) -> Path:
    if path_arg:
        outdir = Path(path_arg).expanduser().resolve()
    else:
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        outdir = Path.cwd() / f"ernie-image-output-{stamp}"
    if create:
        outdir.mkdir(parents=True, exist_ok=True)
    return outdir


def resolve_size(args: argparse.Namespace) -> str:
    if args.size != DEFAULT_SIZE:
        return args.size
    if args.preset:
        return PRESET_SIZES[args.preset]
    if args.ratio:
        return RATIO_SIZES[args.ratio]
    return args.size


def build_extra_body(args: argparse.Namespace, *, effective_use_pe: bool | None) -> dict[str, Any]:
    extra_body: dict[str, Any] = {}
    if args.negative_prompt:
        extra_body["negative_prompt"] = args.negative_prompt
    if args.style:
        extra_body["style"] = args.style
    if args.sampler_index:
        extra_body["sampler_index"] = args.sampler_index
    if args.seed is not None:
        extra_body["seed"] = args.seed
    if args.steps is not None:
        extra_body["steps"] = args.steps
    if args.cfg_scale is not None:
        extra_body["cfg_scale"] = args.cfg_scale
    if args.num_inference_steps is not None:
        if args.steps is not None and args.steps != args.num_inference_steps:
            raise SystemExit("--steps and --num-inference-steps disagree. Pass only one or use the same value.")
        extra_body["num_inference_steps"] = args.num_inference_steps
        extra_body.setdefault("steps", args.num_inference_steps)
    if args.guidance_scale is not None:
        if args.cfg_scale is not None and args.cfg_scale != args.guidance_scale:
            raise SystemExit("--cfg-scale and --guidance-scale disagree. Pass only one or use the same value.")
        extra_body["guidance_scale"] = args.guidance_scale
        extra_body.setdefault("cfg_scale", args.guidance_scale)
    if effective_use_pe is not None:
        extra_body["use_pe"] = effective_use_pe
    return extra_body


def dump_metadata(outdir: Path, payload: dict[str, Any]) -> None:
    (outdir / "request.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def resolve_batch_mode(args: argparse.Namespace) -> str:
    if args.batch_mode != "auto":
        return args.batch_mode
    if args.response_format == "url" and args.n > 1:
        return "serial"
    return "batch"


def resolve_seed_mode(args: argparse.Namespace, batch_mode: str) -> str:
    if args.seed_mode != "auto":
        return args.seed_mode
    if batch_mode == "serial" and args.n > 1:
        if args.seed is not None:
            return "incremental"
        return "random"
    if args.seed is not None:
        return "fixed"
    return "random"


def random_seed() -> int:
    return secrets.randbelow(2_000_000_000)


def resolve_serial_base_seed(base_seed: int | None, seed_mode: str) -> int | None:
    if seed_mode == "random":
        return None
    if base_seed is not None:
        return base_seed
    return random_seed()


def derive_serial_seed(base_seed: int, seed_mode: str, index: int) -> int:
    if seed_mode == "random":
        return random_seed()
    if seed_mode == "incremental":
        return base_seed + index - 1
    return base_seed


def build_request_payload(
    *,
    model: str,
    prompt: str,
    n: int,
    response_format: str,
    size: str,
    extra_body: dict[str, Any],
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "model": model,
        "prompt": prompt,
        "n": n,
        "response_format": response_format,
        "size": size,
    }
    if extra_body:
        payload["extra_body"] = extra_body
    return payload


def write_variant_artifacts(variant_outdir: Path, payload: dict[str, Any], summary: dict[str, Any]) -> None:
    dump_metadata(variant_outdir, payload)
    (variant_outdir / "result.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    if summary.get("urls"):
        (variant_outdir / "urls.json").write_text(
            json.dumps(summary["urls"], ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )


def run_batch_request(
    *,
    client: Any,
    request_payload: dict[str, Any],
    outdir: Path,
    args: argparse.Namespace,
    resolved_size: str,
    extra_body: dict[str, Any],
    batch_mode: str,
    prompt_plan: dict[str, Any],
    seed_mode: str,
) -> dict[str, Any]:
    result = client.images.generate(**request_payload)

    summary: dict[str, Any] = {
        "model": args.model,
        "size": resolved_size,
        "ratio": args.ratio,
        "preset": args.preset,
        "n": args.n,
        "response_format": args.response_format,
        "prompt": prompt_plan["original_prompt"],
        "expanded_prompt": request_payload["prompt"],
        "archetype": prompt_plan["archetype"],
        "prompt_was_expanded": prompt_plan["prompt_was_expanded"],
        "outdir": str(outdir),
        "extra_body": extra_body,
        "batch_mode": batch_mode,
        "seed_mode": seed_mode,
        "files": [],
        "urls": [],
    }

    if args.response_format == "b64_json":
        for index, item in enumerate(result.data, start=1):
            if not getattr(item, "b64_json", None):
                continue
            filename = f"image_{index:02d}.png"
            filepath = outdir / filename
            filepath.write_bytes(base64.b64decode(item.b64_json))
            summary["files"].append(str(filepath))
    else:
        for item in result.data:
            if getattr(item, "url", None):
                summary["urls"].append(item.url)
        (outdir / "urls.json").write_text(
            json.dumps(summary["urls"], ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    return summary


def run_serial_requests(
    *,
    client: Any,
    args: argparse.Namespace,
    outdir: Path,
    resolved_size: str,
    extra_body: dict[str, Any],
    prompt_plan: dict[str, Any],
    seed_mode: str,
) -> dict[str, Any]:
    variant_root = outdir / "variants"
    variant_root.mkdir(parents=True, exist_ok=True)
    serial_base_seed = resolve_serial_base_seed(args.seed, seed_mode)

    combined_summary: dict[str, Any] = {
        "model": args.model,
        "size": resolved_size,
        "ratio": args.ratio,
        "preset": args.preset,
        "n": args.n,
        "response_format": args.response_format,
        "prompt": prompt_plan["original_prompt"],
        "expanded_prompt": prompt_plan["expanded_prompt"],
        "archetype": prompt_plan["archetype"],
        "prompt_was_expanded": prompt_plan["prompt_was_expanded"],
        "outdir": str(outdir),
        "extra_body": extra_body,
        "batch_mode": "serial",
        "files": [],
        "urls": [],
        "serial_strategy": {
            "reason": "auto-url-preview" if args.batch_mode == "auto" else "explicit-serial",
            "seed_mode": seed_mode,
            "base_seed": serial_base_seed,
            "seeds_used": [],
        },
    }

    for index in range(1, args.n + 1):
        variant_outdir = variant_root / f"variant_{index:02d}"
        variant_outdir.mkdir(parents=True, exist_ok=True)
        variant_seed = derive_serial_seed(serial_base_seed if serial_base_seed is not None else random_seed(), seed_mode, index)
        variant_extra_body = copy.deepcopy(extra_body)
        variant_extra_body["seed"] = variant_seed
        variant_request = build_request_payload(
            model=args.model,
            prompt=prompt_plan["expanded_prompt"],
            n=1,
            response_format=args.response_format,
            size=resolved_size,
            extra_body=variant_extra_body,
        )
        variant_result = client.images.generate(**variant_request)

        variant_summary: dict[str, Any] = {
            "model": args.model,
            "size": resolved_size,
            "ratio": args.ratio,
            "preset": args.preset,
            "n": 1,
            "response_format": args.response_format,
            "prompt": prompt_plan["original_prompt"],
            "expanded_prompt": prompt_plan["expanded_prompt"],
            "archetype": prompt_plan["archetype"],
            "prompt_was_expanded": prompt_plan["prompt_was_expanded"],
            "outdir": str(variant_outdir),
            "extra_body": variant_extra_body,
            "batch_mode": "serial",
            "seed_mode": seed_mode,
            "files": [],
            "urls": [],
        }

        combined_summary["serial_strategy"]["seeds_used"].append(variant_seed)

        if args.response_format == "b64_json":
            item = variant_result.data[0]
            if getattr(item, "b64_json", None):
                filename = f"image_{index:02d}.png"
                filepath = outdir / filename
                filepath.write_bytes(base64.b64decode(item.b64_json))
                variant_summary["files"].append(str(filepath))
                combined_summary["files"].append(str(filepath))
        else:
            item = variant_result.data[0]
            if getattr(item, "url", None):
                variant_summary["urls"].append(item.url)
                combined_summary["urls"].append(item.url)

        write_variant_artifacts(variant_outdir, variant_request, variant_summary)

    if combined_summary["urls"]:
        (outdir / "urls.json").write_text(
            json.dumps(combined_summary["urls"], ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    return combined_summary


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if args.print_setup:
        print(build_setup_instructions())
        return 0

    if args.list_presets:
        print(build_preset_guide())
        return 0

    if args.print_config_path:
        config_path = resolve_config_path(args.config)
        exists = "exists" if config_path.exists() else "missing"
        print(f"{config_path} ({exists})")
        return 0

    config_path = resolve_config_path(args.config)
    config = load_config_file(config_path)
    if args.base_url == DEFAULT_BASE_URL and config.get("base_url"):
        args.base_url = config["base_url"]

    if not args.prompt:
        if args.save_config:
            api_key = resolve_api_key(args)
            if not api_key:
                raise SystemExit(
                    "Missing API key.\n\n"
                    f"{build_setup_instructions()}\n\n"
                    f"You can also run: python3 {shlex.quote(str(SCRIPT_PATH))} --print-setup"
                )
            existing = config
            existing["api_key"] = api_key
            existing["base_url"] = args.base_url
            existing["updated_at"] = datetime.now().isoformat(timespec="seconds")
            save_config_file(config_path, existing)
            print(f"Saved config: {config_path}")
            return 0
        parser.error("--prompt is required unless --print-setup, --list-presets, --print-config-path, or --save-config is used.")

    if not 1 <= args.n <= 4:
        parser.error("--n must be between 1 and 4 for this workflow.")

    resolved_size = resolve_size(args)
    effective_batch_mode = resolve_batch_mode(args)
    explicit_archetype = None if args.archetype == "auto" else args.archetype
    prompt_plan = build_prompt_plan(
        prompt=args.prompt,
        size=resolved_size,
        explicit_archetype=explicit_archetype,
        style=args.style,
    )
    effective_use_pe = args.use_pe if args.use_pe is not None else prompt_plan["effective_use_pe"]
    seed_mode = resolve_seed_mode(args, effective_batch_mode)
    extra_body = build_extra_body(args, effective_use_pe=effective_use_pe)

    request_payload = build_request_payload(
        model=args.model,
        prompt=prompt_plan["expanded_prompt"],
        n=args.n,
        response_format=args.response_format,
        size=resolved_size,
        extra_body=extra_body,
    )

    if args.dry_run:
        dry_run_outdir = resolve_outdir(args.outdir, create=False)
        print(
            json.dumps(
                {
                    "dry_run": True,
                    "payload": request_payload,
                    "outdir": str(dry_run_outdir),
                    "effective_batch_mode": effective_batch_mode,
                    "seed_mode": seed_mode,
                    "prompt_plan": prompt_plan,
                    "effective_use_pe": effective_use_pe,
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 0

    api_key = resolve_api_key(args)
    if not api_key:
        raise SystemExit(
            "Missing API key.\n\n"
            f"{build_setup_instructions()}\n\n"
            f"You can also run: python3 {shlex.quote(str(SCRIPT_PATH))} --print-setup"
        )

    if args.save_config:
        existing = config
        existing["api_key"] = api_key
        existing["base_url"] = args.base_url
        existing["updated_at"] = datetime.now().isoformat(timespec="seconds")
        save_config_file(config_path, existing)
        print(f"Saved config: {config_path}")
        if not args.prompt:
            return 0

    OpenAI = require_openai()
    try:
        client = OpenAI(api_key=api_key, base_url=args.base_url, timeout=args.request_timeout)
    except ImportError as exc:
        message = str(exc)
        if "socks proxy" in message.lower():
            raise SystemExit(
                "Detected SOCKS proxy environment, but socksio is not installed.\n"
                "For a quick one-off run, unset ALL_PROXY / HTTP_PROXY / HTTPS_PROXY for this command.\n"
                "Or install a client that includes SOCKS support."
            ) from exc
        raise
    outdir = resolve_outdir(args.outdir)
    dump_metadata(
        outdir,
        {
            "dry_run": False,
            "request": request_payload,
            "prompt_plan": prompt_plan,
            "effective_batch_mode": effective_batch_mode,
            "seed_mode": seed_mode,
        },
    )
    if effective_batch_mode == "serial":
        summary = run_serial_requests(
            client=client,
            args=args,
            outdir=outdir,
            resolved_size=resolved_size,
            extra_body=extra_body,
            prompt_plan=prompt_plan,
            seed_mode=seed_mode,
        )
    else:
        summary = run_batch_request(
            client=client,
            request_payload=request_payload,
            outdir=outdir,
            args=args,
            resolved_size=resolved_size,
            extra_body=extra_body,
            batch_mode=effective_batch_mode,
            prompt_plan=prompt_plan,
            seed_mode=seed_mode,
        )

    (outdir / "result.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
