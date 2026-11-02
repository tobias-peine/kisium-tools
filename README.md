# kisium-tools

Werkzeuge, mit denen ich [kisium.de](https://kisium.de) betreibe – meinen Blog über den
Quereinstieg in die IT.

Alle Skripte greifen über die Ghost-Admin-API oder SMTP zu. **Zugangsdaten kommen
ausschließlich aus Umgebungsvariablen** und stehen nicht im Code.

## Inhalt

| Datei | Zweck |
| --- | --- |
| `ghost_admin.py` | Session-Helfer für die Ghost-Admin-API (Cookie aus `GHOST_SESSION`) |
| `push_article.py` | Artikel als HTML in einen Ghost-Post schreiben, mit Backup und Rollback |
| `deploy.py` | CSS und Code-Injection ins Theme deployen |
| `cover.py` | Titelbilder erzeugen: große Zahl, Kicker, Wortmarke – einheitlich per Skript |
| `smtp_test.py` | Prüft SMTP-Zugangsdaten in vier Schritten: Verbindung, STARTTLS, Login, Versand |

## Beispiel

```bash
export GHOST_SESSION="s:..."        # Cookie ghost-admin-api-session
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

```
python3 -m pip install requests pillow
```
