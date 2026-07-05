# godek.eu

Osobista strona (Maker's Bento Box) — HTML + CSS + Vanilla JS.
Hosting: MyDevil (serwer s61), domena **godek.eu**.

## Struktura

```
public_html/        ← pliki strony (to trafia na serwer)
  index.html
  style.css
  script.js
deploy.py           ← ręczny deploy przez SSH/SFTP (czyta hasło z .env)
.env                ← dane logowania SSH (NIE trafia do repo)
.env.example        ← wzorzec .env (bez hasła)
.github/workflows/  ← automatyczny deploy po git push
```

## Jak to działa

**Edytujesz stronę → `git push` → GitHub automatycznie wgrywa ją na serwer.**

1. Zmieniasz pliki w folderze `public_html/`
2. `git add . && git commit -m "opis zmian" && git push`
3. GitHub Actions (zakładka **Actions** w repo) wgrywa `public_html/` na MyDevil

## Konfiguracja GitHub (jednorazowo)

W repo na GitHubie: **Settings → Secrets and variables → Actions → New repository secret**
dodaj trzy sekrety:

| Nazwa | Wartość |
|-------|---------|
| `SSH_HOST` | `s61.mydevil.net` |
| `SSH_USER` | `Pluszek` |
| `SSH_PASS` | hasło do MyDevil |

## Deploy ręczny (bez GitHuba)

```bash
pip install -r requirements.txt   # jednorazowo
python deploy.py list             # podgląd serwera
python deploy.py                  # wgraj stronę
python deploy.py clean deploy     # wyczyść serwer i wgraj od nowa
```
