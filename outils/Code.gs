/**
 * Script Google Apps Script — reçoit les résultats des quiz,
 * envoie un mail de correction et range les notes dans le Google Sheet.
 *
 * Après toute modification de ce code :
 *   Déployer > Gérer les déploiements > crayon > Version : Nouvelle version > Déployer
 *   (l'URL /exec reste la même).
 */

const EMAIL_ENSEIGNANT = "maths.eide@gmail.com";

// Test : sélectionnez « testEnvoi » en haut de l'éditeur puis cliquez sur Exécuter.
function testEnvoi() {
  doPost({ postData: { contents: JSON.stringify({
    quiz: "Test d'installation", candidat: "0000", prenom: "Test",
    objet: "Test d'installation — 0000 Test — 5/10 — RETARD 3 min",
    corps: "Ceci est un test.", note: 5, noteSur: 10, nbJustes: 1,
    debut: "09/11/2026 20:03:10", remise: "09/11/2026 20:15:42", dureeUtilisee: "12 min 32 s",
    retardMin: 3, retard: "en retard de 3 min 10 s (début officiel 20:00:00)", finPar: "remis par l'élève",
    details: [
      { num: 1, enonce: "1 + 1 = ?", reponseEleve: "2", correction: "2", juste: true, points: 5, bareme: 5 },
      { num: 2, enonce: "2 × 3 = ?", reponseEleve: "5", correction: "6", juste: false, points: 0, bareme: 5 }
    ]
  }) } });
}

function doPost(e) {
  const d = JSON.parse(e.postData.contents);
  const recu = new Date();   // heure de réception par Google (fait foi)
  const recuTxt = Utilities.formatDate(recu, "Europe/Paris", "dd/MM/yyyy HH:mm:ss");
  const enRetard = (d.retardMin || 0) >= 1;

  // 1) Mail de correction
  let html = `<h2>${esc(d.quiz)}</h2>
    <p><b>N° de candidat :</b> ${esc(d.candidat)}<br><b>Prénom :</b> ${esc(d.prenom)}</p>
    <p><b>Début :</b> ${esc(d.debut || "—")}
       — <span style="color:${enRetard ? "#c62828" : "#2e7d32"};font-weight:bold">${esc(d.retard || "—")}</span><br>
    <b>Remise :</b> ${esc(d.remise || "—")} (${esc(d.finPar || "—")}, durée ${esc(d.dureeUtilisee || "—")})<br>
    <b>Reçu par le serveur :</b> ${recuTxt}</p>
    <h3>Note : ${String(d.note).replace(".", ",")} / ${d.noteSur}
    (${d.nbJustes} / ${d.details.length} justes)</h3>
    <table border="1" cellpadding="6" style="border-collapse:collapse;font-family:Arial">
    <tr style="background:#1f4e79;color:#fff"><th>N°</th><th>Question</th><th>Réponse de l'élève</th><th>Correction</th><th>Points</th></tr>`;
  d.details.forEach(q => {
    html += `<tr style="background:${q.juste ? "#e8f5e9" : "#fdecea"}">
      <td>${q.num}</td><td>${esc(q.enonce)}</td><td>${esc(q.reponseEleve)}</td>
      <td>${esc(q.correction)}</td><td>${q.points} / ${q.bareme}</td></tr>`;
  });
  html += "</table>";

  MailApp.sendEmail({ to: EMAIL_ENSEIGNANT, subject: d.objet,
                      body: d.corps + "\nReçu par le serveur : " + recuTxt, htmlBody: html });

  // 2) Une ligne par élève dans le Google Sheet (un onglet par quiz)
  const ss = classeurResultats();
  const nomOnglet = d.quiz.substring(0, 90);
  let sh = ss.getSheetByName(nomOnglet);
  if (!sh) {
    sh = ss.insertSheet(nomOnglet);
    sh.appendRow(["Reçu le", "N° candidat", "Prénom", "Note", "Sur", "Justes",
                  "Début", "Retard (min)", "Remise", "Durée", "Fin"]
      .concat(d.details.map(q => "Q" + q.num)));
    sh.setFrozenRows(1);
  }
  sh.appendRow([recu, d.candidat, d.prenom, d.note, d.noteSur, d.nbJustes,
                d.debut || "", d.retardMin || 0, d.remise || "", d.dureeUtilisee || "", d.finPar || ""]
    .concat(d.details.map(q => q.juste ? "✔ " + q.reponseEleve : "✘ " + q.reponseEleve)));
  if (enRetard) sh.getRange(sh.getLastRow(), 8).setBackground("#fdecea");

  return ContentService.createTextOutput("ok");
}

function esc(s) {
  return String(s).replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
}

// Trouve le Google Sheet des résultats : celui auquel le script est attaché,
// sinon un classeur « Résultats quiz » créé automatiquement dans le Drive.
function classeurResultats() {
  const actif = SpreadsheetApp.getActiveSpreadsheet();
  if (actif) return actif;
  const props = PropertiesService.getScriptProperties();
  const id = props.getProperty("ID_CLASSEUR");
  if (id) {
    try { return SpreadsheetApp.openById(id); } catch (e) { /* supprimé : on en recrée un */ }
  }
  const ss = SpreadsheetApp.create("Résultats quiz");
  props.setProperty("ID_CLASSEUR", ss.getId());
  return ss;
}

// Diagnostic : exécutez « ouEstLeClasseur », le lien du classeur s'affiche dans le journal.
function ouEstLeClasseur() {
  const ss = classeurResultats();
  Logger.log("Classeur : " + ss.getName() + " → " + ss.getUrl());
}
