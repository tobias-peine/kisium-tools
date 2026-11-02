#!/usr/bin/env python3
"""Spielt Design und Code-Injection nach kisium.de.

Baut den Head-Block aus design/google-verify.txt + design/nerd.css zusammen,
damit die Verifizierungszeile beim nächsten CSS-Update nicht verloren geht.

    GHOST_SESSION="s:..." python3 deploy.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ghost_admin import put_settings, session

HERE = os.path.dirname(os.path.abspath(__file__))


def read(name):
    with open(os.path.join(HERE, "design", name), encoding="utf-8") as f:
        return f.read().strip()


def main():
    head = read("google-verify.txt") + "\n<style>\n" + read("nerd.css") + "\n</style>"
    foot = read("terminal-chrome.html")
    out = put_settings(session(), [
        ("codeinjection_head", head),
        ("codeinjection_foot", foot),
    ])
    print(f"Head: {len(out['codeinjection_head'])} Zeichen")
    print(f"Foot: {len(out['codeinjection_foot'])} Zeichen")
    print("Verifizierung enthalten:", "google-site-verification" in out["codeinjection_head"])


if __name__ == "__main__":
    main()
