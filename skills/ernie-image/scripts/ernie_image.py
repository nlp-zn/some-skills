#!/usr/bin/env python3
"""Generate images with ERNIE-Image via AI Studio's OpenAI-compatible API."""

from __future__ import annotations

import argparse
import base64
import copy
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


DEFAULT_BASE_URL = "https://aistudio.baidu.com/llm/lmapi/v3"
DEFAULT_MODEL = "ERNIE-Image-Turbo"
DEFAULT_SIZE = "1024x1024"
TOKEN_ENV_VARS = ("AISTUDIO_API_KEY", "AISTUDIO_ACCESS_TOKEN")
DEFAULT_CONFIG_PATH = Path.home() / ".config" / "codex" / "ernie-image" / "config.json"
PRESET_SIZES = {
    "square": "1024x1024",
    "avatar": "1536x1536",
    "article": "2048x1536",
    "poster": "1536x2048",
    "story": "1152x2048",
    "wallpaper": "2048x1152",
}


def build_setup_instructions() -> str:
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
        "  python3 scripts/ernie_image.py --env-file .aistudio.env --prompt '一只可爱的猫咪坐在窗台上'",
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
    return "\n".join(lines)


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
    parser.add_argument("--use-pe", type=parse_bool, help="Whether to enable prompt enhancement.")
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


def resolve_outdir(path_arg: str | None) -> Path:
    if path_arg:
        outdir = Path(path_arg).expanduser().resolve()
    else:
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        outdir = Path.cwd() / f"ernie-image-output-{stamp}"
    outdir.mkdir(parents=True, exist_ok=True)
    return outdir


def resolve_size(args: argparse.Namespace) -> str:
    if args.size != DEFAULT_SIZE:
        return args.size
    if args.preset:
        return PRESET_SIZES[args.preset]
    return args.size


def build_extra_body(args: argparse.Namespace) -> dict[str, Any]:
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
    if args.use_pe is not None:
        extra_body["use_pe"] = args.use_pe
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


def derive_serial_extra_body(base_extra_body: dict[str, Any], base_seed: int | None, index: int) -> dict[str, Any]:
    serial_extra_body = copy.deepcopy(base_extra_body)
    if base_seed is not None:
        serial_extra_body["seed"] = base_seed + index - 1
    return serial_extra_body


def run_batch_request(
    *,
    client: Any,
    request_payload: dict[str, Any],
    outdir: Path,
    args: argparse.Namespace,
    resolved_size: str,
    extra_body: dict[str, Any],
    batch_mode: str,
) -> dict[str, Any]:
    result = client.images.generate(**request_payload)

    summary: dict[str, Any] = {
        "model": args.model,
        "size": resolved_size,
        "preset": args.preset,
        "n": args.n,
        "response_format": args.response_format,
        "prompt": args.prompt,
        "outdir": str(outdir),
        "extra_body": extra_body,
        "batch_mode": batch_mode,
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
) -> dict[str, Any]:
    variant_root = outdir / "variants"
    variant_root.mkdir(parents=True, exist_ok=True)

    combined_summary: dict[str, Any] = {
        "model": args.model,
        "size": resolved_size,
        "preset": args.preset,
        "n": args.n,
        "response_format": args.response_format,
        "prompt": args.prompt,
        "outdir": str(outdir),
        "extra_body": extra_body,
        "batch_mode": "serial",
        "files": [],
        "urls": [],
        "serial_strategy": {
            "reason": "auto-url-preview" if args.batch_mode == "auto" else "explicit-serial",
            "seed_mode": "incremental" if args.seed is not None else "random-per-call",
            "seeds_used": [],
        },
    }

    for index in range(1, args.n + 1):
        variant_outdir = variant_root / f"variant_{index:02d}"
        variant_outdir.mkdir(parents=True, exist_ok=True)
        variant_extra_body = derive_serial_extra_body(extra_body, args.seed, index)
        variant_request = build_request_payload(
            model=args.model,
            prompt=args.prompt,
            n=1,
            response_format=args.response_format,
            size=resolved_size,
            extra_body=variant_extra_body,
        )
        variant_result = client.images.generate(**variant_request)

        variant_summary: dict[str, Any] = {
            "model": args.model,
            "size": resolved_size,
            "preset": args.preset,
            "n": 1,
            "response_format": args.response_format,
            "prompt": args.prompt,
            "outdir": str(variant_outdir),
            "extra_body": variant_extra_body,
            "batch_mode": "serial",
            "files": [],
            "urls": [],
        }

        if "seed" in variant_extra_body:
            combined_summary["serial_strategy"]["seeds_used"].append(variant_extra_body["seed"])

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

    if not args.prompt and not args.save_config:
        parser.error("--prompt is required unless --print-setup, --list-presets, --print-config-path, or --save-config is used.")

    if not 1 <= args.n <= 4:
        parser.error("--n must be between 1 and 4 for this workflow.")

    outdir = resolve_outdir(args.outdir)
    resolved_size = resolve_size(args)
    extra_body = build_extra_body(args)
    effective_batch_mode = resolve_batch_mode(args)

    request_payload = build_request_payload(
        model=args.model,
        prompt=args.prompt,
        n=args.n,
        response_format=args.response_format,
        size=resolved_size,
        extra_body=extra_body,
    )
    request_payload["batch_mode"] = effective_batch_mode

    dump_metadata(outdir, request_payload)

    if args.dry_run:
        print(
            json.dumps(
                {
                    "dry_run": True,
                    "payload": request_payload,
                    "outdir": str(outdir),
                    "effective_batch_mode": effective_batch_mode,
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
            "You can also run: python3 scripts/ernie_image.py --print-setup"
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
    if effective_batch_mode == "serial":
        summary = run_serial_requests(
            client=client,
            args=args,
            outdir=outdir,
            resolved_size=resolved_size,
            extra_body=extra_body,
        )
    else:
        summary = run_batch_request(
            client=client,
            request_payload=build_request_payload(
                model=args.model,
                prompt=args.prompt,
                n=args.n,
                response_format=args.response_format,
                size=resolved_size,
                extra_body=extra_body,
            ),
            outdir=outdir,
            args=args,
            resolved_size=resolved_size,
            extra_body=extra_body,
            batch_mode=effective_batch_mode,
        )

    (outdir / "result.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
