#!/usr/bin/env python3
"""Débloque un quiz : le remplace par une version d'entraînement en accès libre.

Usage (depuis la racine du dépôt) :
  python3 outils/debloquer.py CODE-DU-CATALOGUE MOTDEPASSE [CODE2 MOTDEPASSE2 ...]
  ex. python3 outils/debloquer.py S5ma6FRA-Quiz-261120 piano21

Pour chaque quiz : déchiffre la page, reprend ses questions dans le modèle actuel
(outils/modele-quiz.html), passe en mode entraînement (sans code, sans chronomètre,
rien n'est envoyé, note + corrigé à la fin), retire la liste des élèves à temps
majoré, marque le document « libre » dans le catalogue puis reconstruit le site.
"""
import json, os, re, subprocess, sys
RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RACINE, "outils"))
from chiffrer import dechiffrer

DEBUT = re.compile(r"/\* =+\n   CONFIGURATION[^\n]*\n   =+ \*/\n")
FIN = "/* ===================================================================== */"
FORCER = """
/* ---- version débloquée : entraînement en accès libre ---- */
Object.assign(CONFIG, { entrainement:true, dureeMinutes:0, debut:"", dernierDepart:"", fin:"",
  urlAppsScript:"", afficherNoteEleve:true, afficherCorrigeEleve:true, tempsMajore:[] });
"""

def section(html):
    m = DEBUT.search(html)
    if not m: raise SystemExit("Section CONFIGURATION introuvable")
    j = html.index(FIN, m.end())
    return m.end(), j

cat_p = os.path.join(RACINE, "outils", "catalogue.json")
cat = json.load(open(cat_p, encoding="utf-8"))
modele = open(os.path.join(RACINE, "outils", "modele-quiz.html"), encoding="utf-8").read()
args = sys.argv[1:]
for code, mdp in zip(args[::2], args[1::2]):
    doc = next(d for d in cat["documents"] if d["code"] == code)
    chemin = os.path.join(RACINE, doc["fichier"])
    page = open(chemin, encoding="utf-8").read()
    m = re.search(r'const DONNEES = "([^"]+)"', page)
    source = dechiffrer(m.group(1), mdp.strip().lower()) if m else page
    a, b = section(source)
    config = re.sub(r"^\s*tempsMajore\s*:.*\n", "", source[a:b], flags=re.M)
    config = re.sub(r"\n/\* ---- version débloquée.*?\}\);\n", "\n", config, flags=re.S)
    ma, mb = section(modele)
    page = modele[:ma] + config + FORCER + modele[mb:]
    page = page.replace("<title>Quiz</title>", "<title>Entraînement</title>", 1)
    open(chemin, "w", encoding="utf-8").write(page)
    doc["libre"] = True
    print("Débloqué :", code, "→", doc["fichier"])
json.dump(cat, open(cat_p, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
open(cat_p, "a").write("\n")
subprocess.run([sys.executable, os.path.join(RACINE, "outils", "construire.py")], check=True)
