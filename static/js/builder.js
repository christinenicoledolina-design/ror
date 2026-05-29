/**
 * builder.js — BuildLab PC Builder frontend logic
 * Handles: drag-and-drop, slot management, templates, compatibility check, save/export build
 */

const CAT_COLOR = {
  CPU:"#1e0a3c", Motherboard:"#0a1e3c", GPU:"#0a1040", RAM:"#0a2e1a",
  Storage:"#2e1a0a", PSU:"#2e0a1a", Cooling:"#0a2030", Case:"#1a1a2e"
};
const CAT_TEXT = {
  CPU:"#a78bfa", Motherboard:"#78bffa", GPU:"#60a5fa", RAM:"#6ee7b7",
  Storage:"#fbbf24", PSU:"#f472b6", Cooling:"#67e8f9", Case:"#c4b5fd"
};
const ICONS = { CPU:"⚙", Motherboard:"🔌", GPU:"🖥", RAM:"🧩", Storage:"💾", PSU:"⚡", Cooling:"❄", Case:"📦" };

let draggingId  = null;
let draggingCat = null;
const selectedParts = {};

/* ── Add a component to a slot ───────────────────────── */
function addToSlot(id, name, brand, cat, price) {
  selectedParts[cat] = { id, name, brand, price };
  renderSlot(cat);
  updateProgress();
}

function removeFromSlot(cat) {
  delete selectedParts[cat];
  renderSlot(cat);
  updateProgress();
}

/* ── Render a single slot ─────────────────────────────── */
function renderSlot(cat) {
  const slot = document.getElementById("slot-" + cat);
  if (!slot) return;
  const p = selectedParts[cat];
  slot.classList.toggle("filled", !!p);
  slot.innerHTML = `
    <div class="slot-icon" style="${p ? `background:${CAT_COLOR[cat]};` : ""}">
      <span style="${p ? `color:${CAT_TEXT[cat]};` : ""}">${ICONS[cat] || "⚙"}</span>
    </div>
    <div class="slot-info" style="flex:1;min-width:0;">
      <div class="slot-cat" style="${p ? `color:${CAT_TEXT[cat]};` : ""}">${cat}</div>
      ${p
        ? `<div class="slot-name">${p.name}</div><div class="slot-brand">${p.brand}</div>`
        : `<div class="slot-empty-text">Click or drag a component here</div>`
      }
    </div>
    ${p ? `
      <span class="slot-price">&#8369;${p.price.toLocaleString()}</span>
      <button class="slot-remove" onclick="event.stopPropagation();removeFromSlot('${cat}')">&#x2715;</button>
      <span class="slot-check">&#10003;</span>
    ` : ""}
  `;
  slot.setAttribute("ondragover", `event.preventDefault();onDragOver(event,'${cat}')`);
  slot.setAttribute("ondragleave", "onDragLeave(event)");
  slot.setAttribute("ondrop", `onDrop(event,'${cat}')`);
}

/* ── Progress / Total ─────────────────────────────────── */
function updateProgress() {
  const filled = Object.keys(selectedParts).length;
  const total  = 8;
  const pct    = Math.round((filled / total) * 100);
  const sum    = Object.values(selectedParts).reduce((s, p) => s + p.price, 0);

  const bar   = document.getElementById("prog-bar");
  const label = document.getElementById("prog-label");
  const totEl = document.getElementById("build-total");

  if (bar)   { bar.style.width = pct + "%"; bar.style.background = filled === total ? "#22c55e" : "var(--primary)"; }
  if (label) label.textContent = `${filled}/8`;
  if (totEl) totEl.innerHTML   = `&#8369;${sum.toLocaleString()}`;
}

/* ── Filter by category ──────────────────────────────── */
let currentCat = "ALL";

function setCat(cat, el) {
  currentCat = cat;
  document.querySelectorAll(".cat-pills .filter-pill").forEach(b => b.classList.remove("active"));
  if (el) el.classList.add("active");
  filterComponents(document.getElementById("component-search")?.value || "");
}

function filterComponents(query) {
  const q = (query || "").toLowerCase();
  document.querySelectorAll(".component-card").forEach(card => {
    const matchCat  = currentCat === "ALL" || card.dataset.cat === currentCat;
    const matchName = !q || card.dataset.name.toLowerCase().includes(q);
    card.style.display = (matchCat && matchName) ? "" : "none";
  });
}

/* ── Drag & Drop ─────────────────────────────────────── */
function onDragStart(event, id, cat) {
  draggingId  = id;
  draggingCat = cat;
  event.dataTransfer.effectAllowed = "move";
}

function onDragOver(event, cat) {
  event.preventDefault();
  if (draggingCat !== cat) return;
  const slot = document.getElementById("slot-" + cat);
  if (slot) slot.classList.add("drag-over");
}

function onDragLeave(event) {
  event.currentTarget.classList.remove("drag-over");
}

function onDrop(event, cat) {
  event.preventDefault();
  const slot = document.getElementById("slot-" + cat);
  if (slot) slot.classList.remove("drag-over");
  if (draggingCat !== cat || !draggingId) return;

  const card = document.querySelector(`.component-card[data-id="${draggingId}"]`);
  if (!card) return;
  const name  = card.querySelector(".cc-name")?.textContent  || "";
  const priceText = card.querySelector(".cc-price")?.textContent || "0";
  const price = parseFloat(priceText.replace(/[^\d.]/g, "")) || 0;
  const brand = card.querySelector(".cc-brand")?.textContent || "";
  addToSlot(draggingId, name, brand, cat, price);
  draggingId = null; draggingCat = null;
}

/* ── Compatibility check ─────────────────────────────── */
function checkCompat() {
  const ids = Object.values(selectedParts).map(p => p.id);
  if (!ids.length) { alert("Add some parts first."); return; }
  fetch("/api/compatibility", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ component_ids: ids }),
  })
    .then(r => r.json())
    .then(data => {
      const el = document.getElementById("compat-result");
      if (!el) return;
      el.style.display = "block";
      el.className = "compat-banner " + (data.compatible ? "compat-ok" : "compat-fail");
      el.textContent = data.compatible ? "All parts are compatible!" : data.issues.join(" · ");
    })
    .catch(() => alert("Compatibility check failed."));
}

/* ── Save build ──────────────────────────────────────── */
function saveBuild() {
  const ids  = Object.values(selectedParts).map(p => p.id);
  const name = document.getElementById("build-name")?.textContent.trim() || "My Build";
  if (!ids.length) { alert("Add some parts first."); return; }
  fetch("/api/builds/save", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name, component_ids: ids }),
  })
    .then(r => r.json())
    .then(data => {
      if (data.error) { alert(data.error); return; }
      alert("Build saved! View it in My Builds.");
    })
    .catch(() => alert("Save failed."));
}

/* ── Export build (download as .txt) ─────────────────── */
function exportBuild() {
  const name  = document.getElementById("build-name")?.textContent.trim() || "My Build";
  const parts = Object.entries(selectedParts);
  if (!parts.length) { alert("Add some parts first."); return; }

  const sep   = "=".repeat(40);
  const lines = [`BuildLab — ${name}`, sep];
  let total   = 0;

  const ORDER = ["CPU","Motherboard","GPU","RAM","Storage","PSU","Cooling","Case"];
  ORDER.forEach(cat => {
    const p = selectedParts[cat];
    if (p) {
      lines.push(`${cat.padEnd(14)} ${p.name} (${p.brand})  —  P${p.price.toLocaleString()}`);
      total += p.price;
    } else {
      lines.push(`${cat.padEnd(14)} —`);
    }
  });

  lines.push(sep);
  lines.push(`${"TOTAL".padEnd(14)} P${total.toLocaleString()}`);

  const blob = new Blob([lines.join("\n")], { type: "text/plain" });
  const url  = URL.createObjectURL(blob);
  const a    = document.createElement("a");
  a.href     = url;
  a.download = name.replace(/\s+/g, "_") + ".txt";
  a.click();
  URL.revokeObjectURL(url);
}

/* ── Templates ───────────────────────────────────────── */
const TEMPLATES = {
  budget:  [4, 9, 13, 14, 19, 21, 23, 26],
  mid:     [1, 6, 11, 14, 17, 20, 25, 28],
  gaming:  [2, 7, 12, 15, 18, 20, 24, 27],
};

function loadTemplate(key) {
  const ids = TEMPLATES[key] || [];
  Object.keys(selectedParts).forEach(cat => delete selectedParts[cat]);
  ids.forEach(id => {
    const card = document.querySelector(`.component-card[data-id="${id}"]`);
    if (!card) return;
    const cat   = card.dataset.cat;
    const name  = card.querySelector(".cc-name")?.textContent  || "";
    const price = parseFloat(card.querySelector(".cc-price")?.textContent.replace(/[^0-9.]/g, "") || "0");
    const brand = card.querySelector(".cc-brand")?.textContent || "";
    selectedParts[cat] = { id, name, brand, price };
  });
  ["CPU","Motherboard","GPU","RAM","Storage","PSU","Cooling","Case"].forEach(renderSlot);
  updateProgress();
  const nameMap = { budget:"Budget Build", mid:"Mid-Range Build", gaming:"Gaming Build" };
  const nameEl  = document.getElementById("build-name");
  if (nameEl) nameEl.textContent = nameMap[key] || "My Build";
}

function clearBuild() {
  Object.keys(selectedParts).forEach(cat => delete selectedParts[cat]);
  ["CPU","Motherboard","GPU","RAM","Storage","PSU","Cooling","Case"].forEach(renderSlot);
  updateProgress();
}

/* ── Init ────────────────────────────────────────────── */
document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll(".component-card").forEach(card => {
    card.addEventListener("dragend", () => { draggingId = null; draggingCat = null; });
  });
});
