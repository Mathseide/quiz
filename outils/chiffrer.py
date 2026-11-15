#!/usr/bin/env python3
"""Chiffre une page de quiz avec un mot de passe (AES-GCM, clé PBKDF2-SHA256).

Usage : python3 chiffrer.py source.html sortie.html MOTDEPASSE "Titre affiché"
La page produite ne contient que le texte chiffré : sans le mot de passe, ni les
questions ni les réponses ne sont lisibles. Le déchiffrement se fait dans le
navigateur de l'élève (Web Crypto). Pour retrouver la source :
python3 chiffrer.py --dechiffrer page.html source.html MOTDEPASSE
"""
import base64, html, os, re, sys
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes

ITER = 250000

def cle(mdp, sel):
    return PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=sel, iterations=ITER).derive(mdp.encode())

def chiffrer(texte, mdp):
    sel, iv = os.urandom(16), os.urandom(12)
    return base64.b64encode(sel + iv + AESGCM(cle(mdp, sel)).encrypt(iv, texte.encode(), None)).decode()

def dechiffrer(b64, mdp):
    d = base64.b64decode(b64)
    return AESGCM(cle(mdp, d[:16])).decrypt(d[16:28], d[28:], None).decode()

PAGE = """<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1">
<meta name="robots" content="noindex">
<title>__TITRE__</title>
<style>
  body { margin:0; font-family:-apple-system, "Segoe UI", Helvetica, Arial, sans-serif; background:#f2f4f7; color:#1a1a1a; }
  .wrap { max-width:520px; margin:12vh auto 0; padding:0 18px; }
  .carte { background:#fff; border-radius:14px; padding:26px; box-shadow:0 2px 8px rgba(0,0,0,.06); }
  h1 { color:#1f4e79; font-size:1.5rem; margin:0 0 8px; }
  p { color:#555; }
  input { width:100%; box-sizing:border-box; font-size:1.3rem; padding:14px; border:2px solid #ccd3dc; border-radius:10px; margin-top:8px; }
  input:focus { outline:none; border-color:#1f4e79; }
  button { margin-top:16px; width:100%; font-size:1.2rem; padding:14px; border:none; border-radius:10px; background:#1f4e79; color:#fff; }
  .err { color:#c62828; min-height:1.4em; margin-top:10px; }
</style>
</head>
<body>
<div class="wrap"><div class="carte">
  <h1>🔒 __TITRE__</h1>
  <p>Ce quiz est protégé. Tape le code donné par ton professeur.</p>
  <form id="f"><input id="mdp" type="text" autocomplete="off" autocapitalize="none" autocorrect="off" spellcheck="false" placeholder="Code du quiz">
  <button id="ok" type="submit">Ouvrir le quiz</button></form>
  <div class="err" id="err"></div>
</div></div>
<script>
const DONNEES = "__DONNEES__";
const ITER = __ITER__;
const CLE_SESSION = "code|" + location.pathname;
async function ouvrir(mdp){
  const d = Uint8Array.from(atob(DONNEES), c => c.charCodeAt(0));
  const base = await crypto.subtle.importKey("raw", new TextEncoder().encode(mdp), "PBKDF2", false, ["deriveKey"]);
  const k = await crypto.subtle.deriveKey({ name:"PBKDF2", salt:d.slice(0,16), iterations:ITER, hash:"SHA-256" },
                                          base, { name:"AES-GCM", length:256 }, false, ["decrypt"]);
  const clair = await crypto.subtle.decrypt({ name:"AES-GCM", iv:d.slice(16,28) }, k, d.slice(28));
  try { sessionStorage.setItem(CLE_SESSION, mdp); } catch(e) {}
  const html = new TextDecoder().decode(clair);
  document.open(); document.write(html); document.close();
}
document.getElementById("f").onsubmit = async e => {
  e.preventDefault();
  const mdp = document.getElementById("mdp").value.trim().toLowerCase();
  document.getElementById("err").textContent = "Vérification…";
  document.getElementById("ok").disabled = true;
  try { await ouvrir(mdp); }
  catch(err) { document.getElementById("err").textContent = "Code incorrect."; document.getElementById("ok").disabled = false; }
};
(async () => { let m = null; try { m = sessionStorage.getItem(CLE_SESSION); } catch(e) {}
  if (m) { try { await ouvrir(m); } catch(e) {} } })();
</script>
</body>
</html>
"""

if __name__ == "__main__":
    if sys.argv[1] == "--dechiffrer":
        page, sortie, mdp = sys.argv[2:5]
        b64 = re.search(r'const DONNEES = "([^"]+)"', open(page, encoding="utf-8").read()).group(1)
        open(sortie, "w", encoding="utf-8").write(dechiffrer(b64, mdp))
    else:
        src, sortie, mdp, titre = sys.argv[1:5]
        page = (PAGE.replace("__TITRE__", html.escape(titre)).replace("__ITER__", str(ITER))
                    .replace("__DONNEES__", chiffrer(open(src, encoding="utf-8").read(), mdp.strip().lower())))
        open(sortie, "w", encoding="utf-8").write(page)
