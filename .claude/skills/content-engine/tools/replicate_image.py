#!/usr/bin/env python3
"""
replicate_image.py — Inferencia de imagen vía Replicate con LoRAs entrenados por cliente.

Diseñado para modelos entrenados con ostris/flux-dev-lora-trainer (la firma
de inputs viene de ahí: prompt, aspect_ratio, lora_scale, etc.).

Uso:
    # Generación básica
    python tools/replicate_image.py \
        --model maxschock/ingolf \
        --prompt "INGOLF in a modern boardroom presenting to executives, ..." \
        --aspect-ratio 4:5 \
        --output _assets/ingolf-test.png

    # Con LoRA scale custom (más débil para escenas complejas)
    python tools/replicate_image.py --model maxschock/ingolf \
        --prompt "..." --lora-scale 0.85 --output _assets/o.png

    # Modo rápido (fp8 quantized)
    python tools/replicate_image.py --model maxschock/ingolf \
        --prompt "..." --go-fast --output _assets/o.png

Entorno:
    REPLICATE_API_TOKEN — obligatoria. https://replicate.com/account/api-tokens

Endpoints (verificados):
    POST  /v1/models/{owner}/{name}/predictions   → crea prediction (usa latest version)
    GET   /v1/predictions/{id}                    → estado/output

Auth: Authorization: Bearer <token>

El cliente usa el header `Prefer: wait=60` para que Replicate devuelva el
resultado en la misma respuesta cuando la inferencia tarda <60s. Si no, polea
hasta completar o timeout configurable.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.request
import urllib.error
from pathlib import Path

API_BASE = "https://api.replicate.com/v1"


class ReplicateError(Exception):
    """Error al llamar a Replicate."""


def _api_token() -> str:
    token = os.environ.get("REPLICATE_API_TOKEN", "")
    if not token:
        raise ReplicateError(
            "REPLICATE_API_TOKEN no está definida. Sácala en https://replicate.com/account/api-tokens"
        )
    return token


def _http(method: str, url: str, *, body: dict | None = None, extra_headers: dict | None = None, timeout_s: int = 120) -> dict:
    headers = {
        "Authorization": f"Bearer {_api_token()}",
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": "content-engine/0.3.0 (iamasters-os; +https://github.com/iamasters-academy/content-engine)",
    }
    if extra_headers:
        headers.update(extra_headers)

    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(url, method=method, data=data, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=timeout_s) as resp:
            raw = resp.read().decode("utf-8")
    except urllib.error.HTTPError as e:
        try:
            err_body = e.read().decode("utf-8")
        except Exception:
            err_body = str(e)
        raise ReplicateError(f"HTTP {e.code} — {err_body}") from e
    try:
        return json.loads(raw) if raw else {}
    except json.JSONDecodeError:
        return {"raw": raw}


def get_latest_version(model_slug: str) -> str:
    """Obtiene el version id de la latest version del modelo."""
    data = _http("GET", f"{API_BASE}/models/{model_slug}")
    lv = data.get("latest_version") or {}
    vid = lv.get("id")
    if not vid:
        raise ReplicateError(f"No se encontró latest_version para {model_slug}.")
    return vid


def create_prediction(model_slug: str, input_params: dict, *, wait_inline_s: int = 60, version: str | None = None) -> dict:
    """Crea una prediction. Usa /predictions con version explícito (compatible
    con modelos entrenados, no solo modelos públicos oficiales).

    Si Replicate la completa en <wait_inline_s s, devuelve el resultado en la
    misma respuesta. Si no, devuelve estado intermedio (starting/processing).
    """
    if version is None:
        version = get_latest_version(model_slug)
    url = f"{API_BASE}/predictions"
    extra = {"Prefer": f"wait={wait_inline_s}"} if wait_inline_s > 0 else {}
    body = {"version": version, "input": input_params}
    return _http("POST", url, body=body, extra_headers=extra, timeout_s=wait_inline_s + 30)


def get_prediction(prediction_id: str) -> dict:
    url = f"{API_BASE}/predictions/{prediction_id}"
    return _http("GET", url)


def wait_for_completion(prediction_id: str, *, timeout_s: int = 180, poll_s: float = 2.0) -> dict:
    deadline = time.time() + timeout_s
    last: dict = {}
    while time.time() < deadline:
        last = get_prediction(prediction_id)
        status = last.get("status", "")
        if status == "succeeded":
            return last
        if status in {"failed", "canceled"}:
            err = last.get("error") or "(sin detalle)"
            raise ReplicateError(f"Prediction {prediction_id} {status}: {err}")
        time.sleep(poll_s)
    raise ReplicateError(f"Timeout esperando prediction {prediction_id} (>{timeout_s}s). Último estado: {last.get('status')}")


def download_url(url: str, output_path: Path) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req, timeout=60) as resp:
        data = resp.read()
    output_path.write_bytes(data)
    return output_path


def generate(
    *,
    model_slug: str,
    prompt: str,
    aspect_ratio: str = "4:5",
    output_format: str = "png",
    lora_scale: float = 1.0,
    num_inference_steps: int = 28,
    guidance_scale: float = 3.0,
    output_quality: int = 100,
    num_outputs: int = 1,
    seed: int | None = None,
    go_fast: bool = False,
    extra_lora: str | None = None,
    extra_lora_scale: float = 1.0,
    output_path: Path | None = None,
    timeout_s: int = 180,
) -> dict:
    """Lanza una generación y devuelve dict con prediction + paths locales.

    Returns:
        {
          "prediction_id": str,
          "status": "succeeded",
          "output_urls": [str, ...],
          "output_paths": [Path, ...]   # si output_path se pasó
        }
    """
    if not prompt:
        raise ReplicateError("prompt es obligatorio.")

    inputs: dict = {
        "prompt": prompt,
        "aspect_ratio": aspect_ratio,
        "output_format": output_format,
        "lora_scale": lora_scale,
        "num_inference_steps": num_inference_steps,
        "guidance_scale": guidance_scale,
        "output_quality": output_quality,
        "num_outputs": num_outputs,
        "go_fast": go_fast,
    }
    if seed is not None:
        inputs["seed"] = seed
    if extra_lora:
        inputs["extra_lora"] = extra_lora
        inputs["extra_lora_scale"] = extra_lora_scale

    pred = create_prediction(model_slug, inputs)
    status = pred.get("status", "")
    if status != "succeeded":
        # No completó inline — polea.
        pred = wait_for_completion(pred["id"], timeout_s=timeout_s)

    output = pred.get("output") or []
    if isinstance(output, str):
        output = [output]

    result: dict = {
        "prediction_id": pred.get("id"),
        "status": pred.get("status"),
        "output_urls": output,
        "output_paths": [],
        "metrics": pred.get("metrics") or {},
    }

    if output_path is not None and output:
        if len(output) == 1:
            paths = [download_url(output[0], output_path)]
        else:
            stem = output_path.stem
            paths = []
            for i, url in enumerate(output):
                p = output_path.with_name(f"{stem}-{i}{output_path.suffix}")
                paths.append(download_url(url, p))
        result["output_paths"] = [str(p) for p in paths]

    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Genera imágenes vía Replicate con LoRA por cliente.")
    parser.add_argument("--model", required=True,
                        help="Slug del modelo Replicate. Ej: maxschock/ingolf")
    parser.add_argument("--prompt", required=True, help="Prompt en inglés. Incluye trigger_word del LoRA.")
    parser.add_argument("--aspect-ratio", default="4:5",
                        help="1:1 | 4:5 | 5:4 | 16:9 | 9:16 | 21:9 | 9:21 | 3:2 | 2:3 | custom")
    parser.add_argument("--output-format", default="png", choices=["png", "jpg", "webp"])
    parser.add_argument("--lora-scale", type=float, default=1.0,
                        help="Fuerza del LoRA. 1.0 default. Bajar a 0.85 si la cara satura la escena.")
    parser.add_argument("--steps", type=int, default=28, dest="num_inference_steps")
    parser.add_argument("--guidance", type=float, default=3.0, dest="guidance_scale")
    parser.add_argument("--quality", type=int, default=100, dest="output_quality")
    parser.add_argument("--num-outputs", type=int, default=1)
    parser.add_argument("--seed", type=int, default=None)
    parser.add_argument("--go-fast", action="store_true", help="fp8 quantized, más rápido y barato.")
    parser.add_argument("--extra-lora", default=None,
                        help="LoRA adicional. Formato <owner>/<name> o URL HuggingFace.")
    parser.add_argument("--extra-lora-scale", type=float, default=1.0)
    parser.add_argument("--output", default=None, help="Ruta local para descargar la imagen.")
    parser.add_argument("--timeout", type=int, default=180)
    args = parser.parse_args()

    try:
        result = generate(
            model_slug=args.model,
            prompt=args.prompt,
            aspect_ratio=args.aspect_ratio,
            output_format=args.output_format,
            lora_scale=args.lora_scale,
            num_inference_steps=args.num_inference_steps,
            guidance_scale=args.guidance_scale,
            output_quality=args.output_quality,
            num_outputs=args.num_outputs,
            seed=args.seed,
            go_fast=args.go_fast,
            extra_lora=args.extra_lora,
            extra_lora_scale=args.extra_lora_scale,
            output_path=Path(args.output) if args.output else None,
            timeout_s=args.timeout,
        )
    except ReplicateError as e:
        print(f"[replicate_image] error: {e}", file=sys.stderr)
        return 1

    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
