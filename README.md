# Maths à l'EIDE

Site : https://mathseide.github.io/quiz/

## Organisation
- `outils/catalogue.json` : liste des classes, des mois et des documents.
  Chaque document : `code` (classe-type-aammjj, type = Aide, DM ou Quiz), `titre`, `fichier`, `masque` (facultatif).
- `python3 outils/construire.py` : régénère toutes les pages `classes/…` et l'accueil depuis le catalogue.
- Les **quiz sont chiffrés** (`outils/chiffrer.py`) : il faut leur code pour les ouvrir. Les codes ne sont jamais enregistrés ici.
- `outils/modele-quiz.html` : modèle de quiz / travail maison (configuration en haut du fichier).
- `outils/Code.gs` : script Google Apps Script qui reçoit les résultats (mail + tableur).
- `outils/qrcode/` : génération des QR codes (bibliothèque QRCode de Kazuhiko Arase, licence MIT).
- `outils/debloquer.py` : le lendemain de la date d'un quiz, le remplace par une version d'entraînement libre (sans code, sans chronomètre, rien n'est envoyé).
- Temps majoré (+25 %) : dans la configuration d'un quiz, `tempsMajore: ["numéro", …]` (ligne retirée automatiquement au déblocage ; la liste de référence n'est jamais publiée ici).
