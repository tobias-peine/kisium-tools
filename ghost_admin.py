#!/usr/bin/env python3
"""Admin-Zugriff auf kisium.de über die Ghost-Admin-Session.

Die Session-Cookie kommt aus der Umgebungsvariable GHOST_SESSION
(nicht in die Datei schreiben, nicht committen). GHOST_URL überschreibt
den Host, Default ist https://kisium.de.
"""
import json
import os
import sys

import requests

SITE = os.environ.get("GHOST_URL", "https://kisium.de").rstrip("/")
DOMAIN = SITE.split("://", 1)[-1].split("/", 1)[0]


def session():
    cookie = os.environ.get("GHOST_SESSION", "").strip()
    if not cookie:
        sys.exit("GHOST_SESSION fehlt (Cookie ghost-admin-api-session).")
    s = requests.Session()
    s.cookies.set("ghost-admin-api-session", cookie, domain=DOMAIN, path="/")
    s.headers.update({
        "User-Agent": "Mozilla/5.0",
        "Origin": SITE,
        "Referer": f"{SITE}/ghost/",
        "Accept": "application/json",
        "Content-Type": "application/json",
    })
    return s


def put_settings(s, pairs):
    body = {"settings": [{"key": k, "value": v} for k, v in pairs]}
    r = s.put(f"{SITE}/ghost/api/admin/settings/", data=json.dumps(body))
    if r.status_code >= 400:
        sys.exit(f"Settings-Update fehlgeschlagen ({r.status_code}): {r.text[:400]}")
    return {x['key']: x['value'] for x in r.json()['settings']}


def put_theme_settings(s, pairs):
    body = {"custom_theme_settings": [{"key": k, "value": v} for k, v in pairs]}
    r = s.put(f"{SITE}/ghost/api/admin/custom_theme_settings/", data=json.dumps(body))
    if r.status_code >= 400:
        sys.exit(f"Theme-Settings fehlgeschlagen ({r.status_code}): {r.text[:400]}")
    return {x['key']: x['value'] for x in r.json()['custom_theme_settings']}


if __name__ == "__main__":
    s = session()
    r = s.get(f"{SITE}/ghost/api/admin/site/")
    print("Session ok:", r.status_code, r.json()["site"]["title"])
