#!/usr/bin/env python3
"""
Deploy strony godek.eu na MyDevil (serwer s61) przez SSH/SFTP.

Użycie:
    python deploy.py list            # pokaż, co jest teraz na serwerze
    python deploy.py clean           # skasuj zawartość public_html (pyta o potwierdzenie)
    python deploy.py                 # wgraj pliki strony (deploy)
    python deploy.py clean deploy    # skasuj starą stronę i wgraj nową

Hasło i dane logowania czytane są z pliku .env.
Wymaga biblioteki paramiko:  pip install paramiko
"""
import os
import sys
import stat
import posixpath

# Poprawne wyświetlanie polskich znaków w konsoli Windows
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

try:
    import paramiko
except ImportError:
    sys.exit("Brak biblioteki paramiko. Zainstaluj poleceniem:  pip install paramiko")

# Lokalny folder ze stroną (lustro serwera). Cała jego zawartość idzie na WWW.
SITE_DIR = "public_html"


# ----------------------------------------------------------------------
# Konfiguracja z .env
# ----------------------------------------------------------------------
def load_env(path=".env"):
    if not os.path.exists(path):
        sys.exit("Brak pliku .env. Skopiuj .env.example jako .env i uzupełnij hasło.")
    cfg = {}
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, val = line.split("=", 1)
            cfg[key.strip()] = val.strip().strip('"').strip("'")
    return cfg


CFG = load_env()
HOST = CFG.get("SSH_HOST", "s61.mydevil.net")
PORT = int(CFG.get("SSH_PORT", "22"))
USER = CFG.get("SSH_USER", "Pluszek")
PASS = CFG.get("SSH_PASS", "")
REMOTE = CFG.get("REMOTE_DIR", f"/usr/home/{USER}/domains/godek.eu/public_html")


# ----------------------------------------------------------------------
# Połączenie
# ----------------------------------------------------------------------
def connect():
    if not PASS:
        sys.exit("Uzupełnij SSH_PASS w pliku .env")
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    print(f"Łączę z {USER}@{HOST}:{PORT} ...")
    client.connect(HOST, port=PORT, username=USER, password=PASS, timeout=25)
    return client


def ensure_remote_dir(sftp, path):
    """Tworzy katalog zdalny (rekurencyjnie), jeśli nie istnieje."""
    parts = path.strip("/").split("/")
    cur = ""
    for p in parts:
        cur += "/" + p
        try:
            sftp.stat(cur)
        except IOError:
            sftp.mkdir(cur)


# ----------------------------------------------------------------------
# Tryby
# ----------------------------------------------------------------------
def cmd_list(sftp):
    print(f"\nZawartość {REMOTE}:")
    try:
        entries = sftp.listdir_attr(REMOTE)
    except IOError:
        print("  (katalog nie istnieje jeszcze na serwerze)")
        return
    if not entries:
        print("  (pusty)")
        return
    for e in sorted(entries, key=lambda x: x.filename):
        kind = "DIR " if stat.S_ISDIR(e.st_mode) else "file"
        print(f"  [{kind}] {e.filename}")


def remote_rmtree(sftp, path):
    """Rekurencyjnie usuwa zawartość katalogu path (sam katalog zostaje)."""
    for e in sftp.listdir_attr(path):
        full = posixpath.join(path, e.filename)
        if stat.S_ISDIR(e.st_mode):
            remote_rmtree(sftp, full)
            sftp.rmdir(full)
        else:
            sftp.remove(full)
        print(f"  usunięto: {full}")


def cmd_clean(client, sftp, auto_yes=False):
    try:
        entries = sftp.listdir(REMOTE)
    except IOError:
        print("Katalog docelowy nie istnieje — nie ma czego kasować.")
        return
    if not entries:
        print("Katalog docelowy jest już pusty.")
        return
    print(f"\nUWAGA: zaraz skasuję CAŁĄ zawartość {REMOTE}")
    print(f"Liczba elementów do usunięcia: {len(entries)}")
    if not auto_yes:
        answer = input("Wpisz TAK aby potwierdzić: ").strip()
        if answer != "TAK":
            print("Anulowano.")
            return
    # Szybkie czyszczenie jedną komendą przez SSH (pliki zwykłe + ukryte).
    # Zabezpieczenie: kasujemy tylko WEWNĄTRZ public_html.
    if REMOTE.rstrip("/").endswith("public_html"):
        cmd = f"rm -rf '{REMOTE}'/* '{REMOTE}'/.??*"
        print("Czyszczę serwer (rm -rf)...")
        _, stdout, stderr = client.exec_command(cmd)
        stdout.channel.recv_exit_status()  # czekaj na zakończenie
        err = stderr.read().decode(errors="ignore").strip()
        if err:
            print("  uwaga:", err)
        print("Wyczyszczono katalog docelowy.")
    else:
        # Ostrożniejszy fallback, gdyby ścieżka była nietypowa
        remote_rmtree(sftp, REMOTE)
        print("Wyczyszczono katalog docelowy.")


def upload_dir(sftp, local_dir, remote_dir):
    ensure_remote_dir(sftp, remote_dir)
    for name in os.listdir(local_dir):
        lpath = os.path.join(local_dir, name)
        rpath = posixpath.join(remote_dir, name)
        if os.path.isdir(lpath):
            upload_dir(sftp, lpath, rpath)
        else:
            sftp.put(lpath, rpath)
            print(f"  wgrano: {rpath}")


def cmd_deploy(sftp):
    if not os.path.isdir(SITE_DIR):
        sys.exit(f"Brak folderu '{SITE_DIR}' — nie ma czego wgrać.")
    ensure_remote_dir(sftp, REMOTE)
    print(f"\nWgrywam zawartość '{SITE_DIR}/' do {REMOTE}:")
    for name in sorted(os.listdir(SITE_DIR)):
        lpath = os.path.join(SITE_DIR, name)
        rpath = posixpath.join(REMOTE, name)
        if os.path.isdir(lpath):
            upload_dir(sftp, lpath, rpath)
        else:
            sftp.put(lpath, rpath)
            print(f"  wgrano: {name}")
    print("Deploy zakończony.")


# ----------------------------------------------------------------------
def main():
    args = [a.lower() for a in sys.argv[1:]]
    auto_yes = "-y" in args or "--yes" in args
    args = [a for a in args if a not in ("-y", "--yes")]

    # domyślnie: deploy
    do_list = "list" in args
    do_clean = "clean" in args
    do_deploy = "deploy" in args or not args

    client = connect()
    try:
        sftp = client.open_sftp()
        if do_list:
            cmd_list(sftp)
        if do_clean:
            cmd_clean(client, sftp, auto_yes=auto_yes)
        if do_deploy:
            cmd_deploy(sftp)
        sftp.close()
    finally:
        client.close()
        print("Rozłączono.")


if __name__ == "__main__":
    main()
