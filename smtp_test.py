#!/usr/bin/env python3
"""Prüft die Brevo-SMTP-Zugangsdaten und schickt eine Testmail.

    BREVO_USER="9xxxxx@smtp-brevo.com" BREVO_KEY="xsmtpsib-..." \
        python3 smtp_test.py deine@adresse.de

Prüft in dieser Reihenfolge: Verbindung, STARTTLS, Anmeldung, Versand.
Damit sieht man genau, woran es hängt, statt nur "geht nicht".
"""
import os
import smtplib
import ssl
import sys
from email.message import EmailMessage

HOST = "smtp-relay.brevo.com"
PORT = 587
ABSENDER = "newsletter@kisium.de"


def main():
    user = os.environ.get("BREVO_USER", "").strip()
    key = os.environ.get("BREVO_KEY", "").strip()
    if not user or not key:
        sys.exit("BREVO_USER und BREVO_KEY setzen.")
    if len(sys.argv) < 2:
        sys.exit("Empfängeradresse fehlt: python3 smtp_test.py <adresse>")
    empf = sys.argv[1]

    print(f"1. Verbindung zu {HOST}:{PORT} …")
    with smtplib.SMTP(HOST, PORT, timeout=25) as s:
        s.ehlo()
        print("   ok:", s.ehlo_resp.decode(errors="ignore").split("\n")[0])

        print("2. STARTTLS …")
        s.starttls(context=ssl.create_default_context())
        s.ehlo()
        print("   ok, verschlüsselt")

        print(f"3. Anmeldung als {user} …")
        try:
            s.login(user, key)
            print("   ok, Zugangsdaten stimmen")
        except smtplib.SMTPAuthenticationError as e:
            sys.exit(f"   FEHLER bei der Anmeldung: {e.smtp_code} {e.smtp_error.decode(errors='ignore')}")

        msg = EmailMessage()
        msg["From"] = f"Kisium <{ABSENDER}>"
        msg["To"] = empf
        msg["Subject"] = "Testmail von kisium.de"
        msg.set_content(
            "Wenn du das liest, funktioniert der Mailversand über Brevo.\n\n"
            "Als Nächstes trage ich die Zugangsdaten in die Ghost-Konfiguration ein, "
            "danach funktionieren Anmeldung und Bestätigungsmails.\n"
        )

        print(f"4. Versand an {empf} …")
        try:
            s.send_message(msg)
            print("   ok, Mail ist raus")
        except smtplib.SMTPDataError as e:
            sys.exit(f"   FEHLER beim Versand: {e.smtp_code} {e.smtp_error.decode(errors='ignore')}\n"
                     f"   Häufige Ursache: Absender {ABSENDER} ist in Brevo nicht verifiziert.")


if __name__ == "__main__":
    main()
