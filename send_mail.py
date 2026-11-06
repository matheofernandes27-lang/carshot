#!/usr/bin/env python3
"""Envoie un email via SMTP SSL (ssl0.ovh.net:465) depuis contact@boldkoi.com.

Usage:
    python3 send_mail.py <destinataire> <sujet> <fichier_corps.txt>

Identifiants lus depuis .env (EMAIL_USER, EMAIL_PASS), jamais en dur dans le code.
"""

import argparse
import smtplib
import ssl
import sys
from email.message import EmailMessage
from pathlib import Path

SMTP_HOST = "ssl0.ovh.net"
SMTP_PORT = 465


def load_env(path: Path) -> dict:
    env = {}
    if not path.exists():
        return env
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        env[key.strip()] = value.strip().strip('"').strip("'")
    return env


def main() -> int:
    parser = argparse.ArgumentParser(description="Envoie un email via SMTP SSL.")
    parser.add_argument("destinataire", help="Adresse email du destinataire")
    parser.add_argument("sujet", help="Sujet de l'email")
    parser.add_argument("fichier_corps", help="Chemin du fichier texte contenant le corps du message")
    args = parser.parse_args()

    env = load_env(Path(__file__).resolve().parent / ".env")
    user = env.get("EMAIL_USER")
    password = env.get("EMAIL_PASS")

    if not user or not password:
        print("Erreur : EMAIL_USER et EMAIL_PASS doivent être définis dans .env", file=sys.stderr)
        return 1

    corps_path = Path(args.fichier_corps)
    try:
        corps = corps_path.read_text(encoding="utf-8")
    except OSError as e:
        print(f"Erreur de lecture du fichier corps : {e}", file=sys.stderr)
        return 1

    msg = EmailMessage()
    msg["From"] = user
    msg["To"] = args.destinataire
    msg["Subject"] = args.sujet
    msg.set_content(corps)

    context = ssl.create_default_context()
    try:
        with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, context=context, timeout=15) as server:
            server.login(user, password)
            server.send_message(msg)
    except Exception as e:
        print(f"Erreur lors de l'envoi : {type(e).__name__}: {e}", file=sys.stderr)
        return 1

    print(f"Email envoyé avec succès à {args.destinataire}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
