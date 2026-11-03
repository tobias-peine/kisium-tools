# kisium-tools

Werkzeuge, mit denen ich [kisium.de](https://kisium.de) betreibe – meinen Blog über den
Quereinstieg in die IT.

Alle Skripte greifen über die Ghost-Admin-API oder SMTP zu. **Zugangsdaten kommen
ausschließlich aus Umgebungsvariablen** und stehen nicht im Code.

## Inhalt

| Datei | Zweck |
| --- | --- |
| `ghost_admin.py` | Session-Helfer für die Ghost-Admin-API (Cookie aus `GHOST_SESSION`, Host optional aus `GHOST_URL`) |
| `push_article.py` | Artikel als HTML in einen Ghost-Post schreiben, mit Backup und Rollback |
| `deploy.py` | CSS und Code-Injection ins Theme deployen |
| `cover.py` | Titelbilder erzeugen: große Zahl, Kicker, Wortmarke – einheitlich per Skript |
| `smtp_test.py` | Prüft SMTP-Zugangsdaten in vier Schritten: Verbindung, STARTTLS, Login, Versand |
| `design/` | `nerd.css`, `terminal-chrome.html`, `google-verify.txt` für `deploy.py` |
| `01-mein-weg-in-die-it.html` | Artikel-HTML für `push_article.py` |

## Beispiel

```bash
export GHOST_SESSION="s:..."        # Cookie ghost-admin-api-session
# export GHOST_URL="https://kisium.de"   # optional, Default ist kisium.de
mkdir -p bilder
python3 deploy.py

python3 cover.py --nummer 06 --farbe "#8a2f52" \
                 --kicker "MEIN WEG · TEIL 6" --out bilder/06-cover.jpg
```

## Warum das existiert

Zwei Dinge, die ich dabei gelernt habe:

1. **Backups vor dem Schreiben.** `push_article.py` sichert den aktuellen Stand, bevor es
   überschreibt. Ein Artikel, der beim Formatieren kaputtgeht, ist ohne Backup verloren.
2. **Cover per Skript, nicht per Hand.** Zwölf von Hand gebaute Bilder driften optisch
   auseinander. Ein Skript liefert immer dasselbe Raster.

## Voraussetzungen

```bash
python3 -m pip install -r requirements.txt
```

Getestet mit Python 3.12 unter Linux. `cover.py` nutzt die DejaVu-Fonts unter
`/usr/share/fonts/truetype/dejavu/`; auf anderen Systemen müssen die Pfade im Skript
angepasst werden.

`deploy.py` liest die Dateien aus `design/`, `push_article.py` liest
`01-mein-weg-in-die-it.html`. Beide liegen im Repo.
