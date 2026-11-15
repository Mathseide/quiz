// Agrandit un QR code au toucher (pratique pour le projeter en classe)
const zoom = document.getElementById("zoom");
document.querySelectorAll("button.qr").forEach(b => b.addEventListener("click", () => {
  document.getElementById("zoom-qr").innerHTML = b.innerHTML;
  document.getElementById("zoom-titre").textContent = b.dataset.titre;
  document.getElementById("zoom-url").textContent = b.dataset.url;
  zoom.hidden = false;
}));
document.getElementById("zoom-fermer").onclick = () => zoom.hidden = true;
zoom.addEventListener("click", ev => { if (ev.target === zoom) zoom.hidden = true; });
document.addEventListener("keydown", ev => { if (ev.key === "Escape") zoom.hidden = true; });
