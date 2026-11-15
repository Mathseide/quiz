#!/usr/bin/env python3
"""Construit le site « Maths à l'EIDE » à partir de outils/catalogue.json.

Usage (depuis la racine du dépôt) : python3 outils/construire.py

Chaque document du catalogue a un code « classe-type-aammjj » :
  - type Aide  → page « Supports et aides » de la classe (liste permanente)
  - type DM    → page « Travail maison » du mois correspondant
  - type Quiz  → page « Quiz » du mois correspondant (fichier chiffré)
Champs : code, titre, fichier (chemin depuis la racine du site), masque (facultatif).
Les QR codes sont générés en SVG par outils/qrcode/svg.js (Node).
"""
import html, json, os, re, shutil, subprocess, sys

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CAT = json.load(open(os.path.join(RACINE, "outils", "catalogue.json"), encoding="utf-8"))
SITE = CAT["site"]
ADR = SITE["adresse"].rstrip("/") + "/"
MOIS_FR = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août",
           "septembre", "octobre", "novembre", "décembre"]
TYPES = {"aide": "aides", "dm": "dm", "quiz": "quiz"}
SECTIONS = [("aides", "Supports et aides", "📘"), ("dm", "Travail maison", "🏠"), ("quiz", "Quiz", "🔒")]
COULEURS = ["#2563eb", "#0d9488", "#7c3aed", "#ea580c", "#be123c", "#4d7c0f", "#0369a1"]

e = lambda s: html.escape(str(s))
_qr = {}
def qr(url):
    if url not in _qr:
        _qr[url] = subprocess.run(["node", os.path.join(RACINE, "outils", "qrcode", "svg.js"), url],
                                  capture_output=True, text=True, check=True).stdout
    return _qr[url]

def dossier(classe): return "classes/" + classe.lower() + "/"
def nom_mois(m): a, n = m.split("-"); return f"{MOIS_FR[int(n) - 1]} {a}"
def nom_mois_maj(m): s = nom_mois(m); return s[0].upper() + s[1:]
def nb(n): return "Aucun document" if n == 0 else f"{n} document{'s' if n > 1 else ''}"

# ---------- lecture du catalogue ----------
docs = []
for d in CAT["documents"]:
    if d.get("masque"): continue
    m = re.fullmatch(r"(.+)-(Aide|DM|Quiz)-(\d{2})(\d{2})(\d{2})", d["code"], re.I)
    if not m: sys.exit(f"Code invalide : {d['code']} (attendu classe-type-aammjj)")
    classe = next((c for c in CAT["classes"] if c.lower() == m.group(1).lower()), None)
    if not classe: sys.exit(f"Classe inconnue dans {d['code']}")
    aa, mm, jj = m.group(3), m.group(4), m.group(5)
    docs.append({**d, "classe": classe, "type": TYPES[m.group(2).lower()],
                 "mois": f"20{aa}-{mm}", "date": f"{jj}/{mm}/20{aa}", "tri": f"{aa}{mm}{jj}"})

# ---------- gabarit ----------
def page(chemin, titre, fil, contenu, classe=None, section=None, qr_page=True):
    prof = chemin.count("/")
    r = "../" * prof
    url = ADR + (chemin[:-len("index.html")] if chemin.endswith("index.html") else chemin)
    nav = ""
    if classe:
        i = CAT["classes"].index(classe)
        nav = '<nav class="onglets">' + "".join(
            f'<a href="{r}{dossier(classe)}{s}/" class="{"actif" if s == section else ""}">{ic} {e(t)}</a>'
            for s, t, ic in SECTIONS) + "</nav>"
    filtxt = " › ".join(f'<a href="{r}{h}">{e(t)}</a>' if h is not None else f"<span>{e(t)}</span>" for t, h in fil)
    coul = COULEURS[CAT["classes"].index(classe) % len(COULEURS)] if classe else "#1f4e79"
    bloc_qr = (f'<div class="qr-page"><button class="qr" data-titre="{e(titre)}" data-url="{e(url)}" aria-label="Agrandir le QR code">{qr(url)}</button>'
               f'<span>QR code de cette page</span></div>') if qr_page else ""
    out = f"""<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(titre)} — {e(SITE["titre"])}</title>
<link rel="stylesheet" href="{r}assets/site.css">
</head>
<body style="--accent:{coul}">
<header class="entete"><div class="contenu">
  <a class="marque" href="{r}">∑ {e(SITE["titre"])}</a>
</div></header>
<main class="contenu">
  <div class="fil">{filtxt}</div>
  <div class="titre-page"><h1>{e(titre)}</h1>{bloc_qr}</div>
  {nav}
  {contenu}
</main>
<footer class="contenu pied">{e(SITE["titre"])}</footer>
<div id="zoom" hidden><div class="zoom-carte"><div id="zoom-qr"></div><p id="zoom-titre"></p><p id="zoom-url"></p><button id="zoom-fermer">Fermer</button></div></div>
<script src="{r}assets/site.js"></script>
</body>
</html>
"""
    p = os.path.join(RACINE, chemin)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, "w", encoding="utf-8").write(out)

def tableau(liste, prof, avec_date=True, vide="Rien pour le moment."):
    if not liste: return f'<p class="vide">{e(vide)}</p>'
    r = "../" * prof
    lignes = ""
    for d in sorted(liste, key=lambda d: d["tri"], reverse=True):
        url = ADR + d["fichier"]
        cadenas = " 🔒" if d["type"] == "quiz" else ""
        lignes += f"""<tr>
  <td><a class="doc" href="{r}{e(d["fichier"])}">{e(d["titre"])}{cadenas}</a><div class="code">{e(d["code"])}</div></td>
  {f'<td class="date">{d["date"]}</td>' if avec_date else ""}
  <td class="cqr"><button class="qr" data-titre="{e(d["titre"])}" data-url="{e(url)}" aria-label="Agrandir le QR code">{qr(url)}</button></td>
</tr>"""
    tete = "<th>Sujet</th>" + ("<th>Date</th>" if avec_date else "") + "<th>QR code</th>"
    return f'<table class="docs"><thead><tr>{tete}</tr></thead><tbody>{lignes}</tbody></table>'

# ---------- nettoyage des pages générées ----------
shutil.rmtree(os.path.join(RACINE, "classes"), ignore_errors=True)

# ---------- accueil ----------
cartes = ""
for i, c in enumerate(CAT["classes"]):
    n = sum(1 for d in docs if d["classe"] == c)
    cartes += f'<a class="carte-classe" style="--accent:{COULEURS[i % len(COULEURS)]}" href="{dossier(c)}"><span class="nom">{e(c)}</span><span class="info">{nb(n)}</span></a>'
page("index.html", SITE["titre"], [("Accueil", None)],
     f'<p class="intro">Choisis ta classe.</p><div class="grille">{cartes}</div>')

# ---------- pages de classe ----------
for c in CAT["classes"]:
    base = dossier(c)
    dc = [d for d in docs if d["classe"] == c]
    menu = "".join(
        f'<a class="carte-section" href="{s}/"><span class="ic">{ic}</span><span class="nom">{e(t)}</span>'
        f'<span class="info">{nb(sum(1 for d in dc if d["type"] == s))}</span></a>'
        for s, t, ic in SECTIONS)
    page(base + "index.html", c, [("Accueil", ""), (c, None)], f'<div class="grille">{menu}</div>', classe=c)

    # Supports et aides (liste permanente)
    page(base + "aides/index.html", f"{c} — Supports et aides",
         [("Accueil", ""), (c, base), ("Supports et aides", None)],
         tableau([d for d in dc if d["type"] == "aides"], 3, avec_date=False, vide="Aucune aide pour le moment."),
         classe=c, section="aides")

    # Travail maison et Quiz : une page par mois
    for s, t, ic in SECTIONS[1:]:
        ds = [d for d in dc if d["type"] == s]
        mois = "".join(
            f'<a class="carte-mois" href="{m}.html"><span class="nom">{e(nom_mois_maj(m))}</span>'
            f'<span class="info">{nb(sum(1 for d in ds if d["mois"] == m))}</span></a>'
            for m in CAT["mois"])
        page(base + f"{s}/index.html", f"{c} — {t}", [("Accueil", ""), (c, base), (t, None)],
             f'<div class="grille mois">{mois}</div>', classe=c, section=s)
        for k, m in enumerate(CAT["mois"]):
            prec = f'<a href="{CAT["mois"][k-1]}.html">← {e(nom_mois(CAT["mois"][k-1]))}</a>' if k > 0 else "<span></span>"
            suiv = f'<a href="{CAT["mois"][k+1]}.html">{e(nom_mois(CAT["mois"][k+1]))} →</a>' if k < len(CAT["mois"]) - 1 else "<span></span>"
            page(base + f"{s}/{m}.html", f"{c} — {t} — {nom_mois_maj(m)}",
                 [("Accueil", ""), (c, base), (t, base + f"{s}/"), (nom_mois_maj(m), None)],
                 tableau([d for d in ds if d["mois"] == m], 3, vide="Aucun document pour ce mois.")
                 + f'<div class="pagemois">{prec}{suiv}</div>', classe=c, section=s, qr_page=False)

hors = [d["code"] for d in docs if d["type"] != "aides" and d["mois"] not in CAT["mois"]]
if hors: print("Attention, mois hors calendrier :", ", ".join(hors))
print(f"Site construit : {len(docs)} document(s), {len(CAT['classes'])} classes.")
