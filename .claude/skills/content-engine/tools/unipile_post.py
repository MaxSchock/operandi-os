#!/usr/bin/env python3
"""
unipile_post.py — Cliente Unipile API para publicar en LinkedIn.

Alternativa a Upload-Post cuando el usuario ya tiene Unipile (multi-cuenta nativo).

Uso:
    # Listar cuentas LinkedIn conectadas
    python tools/unipile_post.py --list-accounts

    # Publicar solo texto
    python tools/unipile_post.py --account-id ABC123 --text "Hola mundo"

    # Publicar texto + imagen
    python tools/unipile_post.py --account-id ABC123 \
        --text "Texto del post" \
        --image _assets/imagen.png

    # Publicar como página de empresa LinkedIn (en lugar de perfil personal)
    python tools/unipile_post.py --account-id ABC123 \
        --text "..." --as-organization 12345678

Entorno:
    UNIPILE_API_KEY  — obligatoria. Sacar del dashboard Unipile.
    UNIPILE_BASE_URL — obligatoria. Formato: https://apiX.unipile.com:PORT

Endpoints (verificados contra developer.unipile.com/docs/posts-and-comments):
    GET   {BASE}/api/v1/accounts?limit=N        → lista cuentas conectadas
    POST  {BASE}/api/v1/posts                    → crea un post (201)

Header de autenticación: X-API-KEY: <key>
Content-Type al publicar: multipart/form-data (atadjuntos como ficheros binarios).
"""

from __future__ import annotations

import argparse
import json
import mimetypes
import os
import sys
import urllib.parse
import urllib.request
import urllib.error
import uuid
from pathlib import Path


class UnipileError(Exception):
    """Error al llamar a Unipile."""


def _base_url() -> str:
    url = os.environ.get("UNIPILE_BASE_URL", "").rstrip("/")
    if not url:
        raise UnipileError(
            "UNIPILE_BASE_URL no está definida. Formato esperado: https://apiX.unipile.com:PORT"
        )
    return url


def _api_key() -> str:
    key = os.environ.get("UNIPILE_API_KEY", "")
    if not key:
        raise UnipileError(
            "UNIPILE_API_KEY no está definida. Sácala del dashboard Unipile."
        )
    return key


def _build_multipart(fields: list[tuple[str, str]], files: list[tuple[str, Path]]) -> tuple[bytes, str]:
    """Construye multipart/form-data con stdlib.

    fields: lista de (nombre, valor). Permite repetir nombres.
    files:  lista de (nombre_campo, ruta).
    """
    boundary = f"----UnipileBoundary{uuid.uuid4().hex}"
    lines: list[bytes] = []

    for key, value in fields:
        lines.append(f"--{boundary}".encode())
        lines.append(f'Content-Disposition: form-data; name="{key}"'.encode())
        lines.append(b"")
        lines.append(str(value).encode("utf-8"))

    for key, file_path in files:
        mime = mimetypes.guess_type(str(file_path))[0] or "application/octet-stream"
        lines.append(f"--{boundary}".encode())
        lines.append(
            f'Content-Disposition: form-data; name="{key}"; filename="{file_path.name}"'.encode()
        )
        lines.append(f"Content-Type: {mime}".encode())
        lines.append(b"")
        lines.append(file_path.read_bytes())

    lines.append(f"--{boundary}--".encode())
    lines.append(b"")
    return b"\r\n".join(lines), f"multipart/form-data; boundary={boundary}"


def _http(method: str, url: str, *, headers: dict, body: bytes | None = None, timeout_s: int = 120) -> dict:
    req = urllib.request.Request(url, method=method, data=body, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=timeout_s) as resp:
            raw = resp.read().decode("utf-8")
            status = resp.status
    except urllib.error.HTTPError as e:
        try:
            err_body = e.read().decode("utf-8")
        except Exception:
            err_body = str(e)
        raise UnipileError(f"HTTP {e.code} — {err_body}") from e
    try:
        data = json.loads(raw) if raw else {}
    except json.JSONDecodeError:
        data = {"raw": raw}
    data["_http_status"] = status
    return data


def list_accounts(*, limit: int = 50, provider: str | None = "LINKEDIN") -> list[dict]:
    """Lista cuentas conectadas en Unipile (filtradas por provider).

    Returns:
        Lista de dicts con keys mínimos: id, name, type, status.
        Filtrada a provider 'LINKEDIN' por defecto. Pasa provider=None para todas.
    """
    headers = {
        "X-API-KEY": _api_key(),
        "accept": "application/json",
    }
    url = f"{_base_url()}/api/v1/accounts?limit={limit}"
    data = _http("GET", url, headers=headers)
    items = data.get("items", data) if isinstance(data, dict) else data
    if not isinstance(items, list):
        raise UnipileError(f"Respuesta inesperada de /accounts: {data!r}")

    out: list[dict] = []
    for a in items:
        t = a.get("type") or a.get("provider")
        if provider and t != provider:
            continue
        out.append({
            "id": a.get("id"),
            "type": t,
            "status": a.get("current_status") or a.get("status"),
            "name": (
                a.get("name")
                or a.get("username")
                or a.get("user_name")
                or (a.get("connection_params") or {}).get("email")
            ),
        })
    return out


def publish_post(
    *,
    account_id: str,
    text: str,
    image_path: Path | None = None,
    as_organization: str | None = None,
    external_link: str | None = None,
    repost_id: str | None = None,
) -> dict:
    """Publica un post en LinkedIn vía Unipile.

    Args:
        account_id: id de la cuenta LinkedIn en Unipile.
        text: cuerpo del post. Soporta mentions LinkedIn vía {{index}}.
        image_path: imagen a adjuntar (opcional). Una sola imagen.
        as_organization: id de página de empresa LinkedIn — publica como página, no como perfil.
        external_link: URL externa (debe aparecer también dentro de text).
        repost_id: id de un post LinkedIn a republicar (text puede ir vacío).

    Returns:
        dict con la respuesta de Unipile (incluye _http_status).
    """
    if not account_id:
        raise UnipileError("account_id es obligatorio.")
    if not text and not repost_id:
        raise UnipileError("Se requiere 'text' o 'repost_id'.")

    fields: list[tuple[str, str]] = [
        ("account_id", account_id),
        ("text", text or ""),
    ]
    if as_organization:
        fields.append(("as_organization", as_organization))
    if external_link:
        if external_link not in text:
            raise UnipileError(
                "external_link debe aparecer también dentro del cuerpo de 'text' (regla Unipile/LinkedIn)."
            )
        fields.append(("external_link", external_link))
    if repost_id:
        fields.append(("repost", repost_id))

    files: list[tuple[str, Path]] = []
    if image_path is not None:
        if not image_path.exists():
            raise UnipileError(f"Imagen no encontrada: {image_path}")
        files.append(("attachments", image_path))

    body, content_type = _build_multipart(fields, files)
    headers = {
        "X-API-KEY": _api_key(),
        "Content-Type": content_type,
        "accept": "application/json",
    }
    url = f"{_base_url()}/api/v1/posts"
    return _http("POST", url, headers=headers, body=body)


def main() -> int:
    parser = argparse.ArgumentParser(description="Publica un post en LinkedIn vía Unipile.")
    parser.add_argument("--list-accounts", action="store_true",
                        help="Lista las cuentas LinkedIn conectadas y sale.")
    parser.add_argument("--account-id", default=None,
                        help="ID de la cuenta LinkedIn en Unipile.")
    parser.add_argument("--text", default=None, help="Cuerpo del post.")
    parser.add_argument("--image", default=None, help="Ruta a imagen a adjuntar (opcional).")
    parser.add_argument("--as-organization", default=None,
                        help="ID de página de empresa LinkedIn (publica como página).")
    parser.add_argument("--external-link", default=None,
                        help="URL externa (debe aparecer también dentro del texto).")
    parser.add_argument("--repost", default=None,
                        help="ID de un post LinkedIn a republicar.")
    parser.add_argument("--dry-run", action="store_true",
                        help="No publica. Muestra lo que se enviaría.")
    args = parser.parse_args()

    try:
        if args.list_accounts:
            accounts = list_accounts()
            print(json.dumps(accounts, indent=2, ensure_ascii=False))
            return 0

        if not args.account_id:
            print("[unipile_post] error: --account-id es obligatorio (o usa --list-accounts).", file=sys.stderr)
            return 2

        if args.dry_run:
            preview = {
                "would_post_to": args.account_id,
                "text_chars": len(args.text or ""),
                "text_preview": (args.text or "")[:200],
                "image": args.image,
                "as_organization": args.as_organization,
                "external_link": args.external_link,
                "repost": args.repost,
            }
            print(json.dumps(preview, indent=2, ensure_ascii=False))
            return 0

        result = publish_post(
            account_id=args.account_id,
            text=args.text or "",
            image_path=Path(args.image) if args.image else None,
            as_organization=args.as_organization,
            external_link=args.external_link,
            repost_id=args.repost,
        )
    except UnipileError as e:
        print(f"[unipile_post] error: {e}", file=sys.stderr)
        return 1

    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
