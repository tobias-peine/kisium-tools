#!/usr/bin/env python3
"""Spielt den formatierten Artikel per Ghost Admin API in den bestehenden Post ein.

Aufruf:
    GHOST_ADMIN_KEY="<id>:<secret>" python3 push_article.py --dry-run
    GHOST_ADMIN_KEY="<id>:<secret>" python3 push_article.py --apply
    GHOST_ADMIN_KEY="<id>:<secret>" python3 push_article.py --rollback <backup.html>

Der Key kommt aus der Umgebungsvariable und landet nie auf der Platte.
Vor dem Schreiben wird die aktuelle Fassung nach backups/ gesichert.
"""
import argparse
import base64
import hashlib
import hmac
import json
import os
import sys
import time
from pathlib import Path

import requests

HERE = Path(__file__).resolve().parent
SITE = os.environ.get("GHOST_URL", "https://kisium.de")
SLUG = "mein-weg-in-die-it"
NEW_HTML = HERE / "01-mein-weg-in-die-it.html"
BACKUPS = HERE / "backups"


def b64url(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode()


def make_token(admin_key: str) -> str:
    try:
        key_id, secret = admin_key.split(":")
        bytes.fromhex(secret)
    except ValueError:
        sys.exit("Key-Format falsch. Erwartet wird '<id>:<secret>' aus Ghost → "
                 "Einstellungen → Integrationen (secret = 64 Hex-Zeichen).")

    header = {"alg": "HS256", "typ": "JWT", "kid": key_id}
    now = int(time.time())
    payload = {"iat": now - 60, "exp": now + 240, "aud": "/admin/"}

    signing_input = ".".join(
        b64url(json.dumps(part, separators=(",", ":")).encode()) for part in (header, payload)
    )
    signature = hmac.new(bytes.fromhex(secret), signing_input.encode(), hashlib.sha256).digest()
    return f"{signing_input}.{b64url(signature)}"


class Ghost:
    def __init__(self, admin_key: str):
        self.base = f"{SITE.rstrip('/')}/ghost/api/admin"
        self.session = requests.Session()
        self.token = make_token(admin_key)
        self.session.headers.update(
            {"Authorization": f"Ghost {self.token}", "Accept-Version": "v6.0",
             "Content-Type": "application/json"}
        )

    def get_post(self):
        r = self.session.get(f"{self.base}/posts/", params={
            "filter": f"slug:{SLUG}", "formats": "html,lexical", "limit": 1})
        r.raise_for_status()
        posts = r.json().get("posts", [])
        if not posts:
            sys.exit(f"Kein Post mit Slug '{SLUG}' gefunden.")
        return posts[0]

    def update_html(self, post, html):
        body = {"posts": [{"html": html, "updated_at": post["updated_at"]}]}
        r = self.session.put(f"{self.base}/posts/{post['id']}/", params={"source": "html"},
                             data=json.dumps(body))
        if r.status_code >= 400:
            sys.exit(f"Update fehlgeschlagen ({r.status_code}): {r.text[:600]}")
        return r.json()["posts"][0]


def verify_live():
    """Prüft die ausgelieferte Seite – nicht die API-Antwort."""
    r = requests.get(f"{SITE.rstrip('/')}/{SLUG}/", timeout=30, headers={"Cache-Control": "no-cache"})
    html = r.text
    report = {
        "http": r.status_code,
        "h2": html.count("<h2"),
        "h3": html.count("<h3"),
        "ul": html.count("<ul"),
        "table": html.count("<table"),
        "strong": html.count("<strong"),
        "br": html.count("<br"),
        "literale_rauten": html.count("##"),
        "literale_sternchen": html.count("**"),
    }
    return report


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true", help="wirklich schreiben")
    ap.add_argument("--dry-run", action="store_true", help="nur zeigen, was passieren würde")
    ap.add_argument("--rollback", metavar="BACKUP", help="Backup-HTML wieder einspielen")
    args = ap.parse_args()

    key = os.environ.get("GHOST_ADMIN_KEY", "").strip()
    if not key:
        sys.exit("GHOST_ADMIN_KEY fehlt.")

    ghost = Ghost(key)
    post = ghost.get_post()
    print(f"Post: {post['title']}  (id={post['id']}, status={post['status']}, "
          f"updated={post['updated_at']})")

    BACKUPS.mkdir(exist_ok=True)
    stamp = time.strftime("%Y%m%d-%H%M%S")

    if args.rollback:
        html = Path(args.rollback).read_text(encoding="utf-8")
        ghost.update_html(post, html)
        print(f"Rollback eingespielt aus {args.rollback}")
        print(json.dumps(verify_live(), indent=2, ensure_ascii=False))
        return

    current = post.get("html") or ""
    backup_path = BACKUPS / f"{SLUG}-{stamp}.html"
    backup_path.write_text(current, encoding="utf-8")
    print(f"Sicherung der aktuellen Fassung: {backup_path} ({len(current)} Zeichen)")

    if not NEW_HTML.exists():
        sys.exit(f"{NEW_HTML} fehlt – erst das Markdown rendern.")
    new_html = NEW_HTML.read_text(encoding="utf-8")
    print(f"Neue Fassung: {len(new_html)} Zeichen")

    if args.dry_run or not args.apply:
        print("\n--dry-run: nichts geschrieben. Mit --apply ausführen.")
        return

    ghost.update_html(post, new_html)
    print("Update geschrieben, prüfe die Live-Seite …")
    time.sleep(2)
    print(json.dumps(verify_live(), indent=2, ensure_ascii=False))
    print(f"\nRollback falls nötig:\n  GHOST_ADMIN_KEY=… python3 {Path(__file__).name} "
          f"--rollback {backup_path}")


if __name__ == "__main__":
    main()
