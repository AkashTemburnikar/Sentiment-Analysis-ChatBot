// ==============================
// AI-Adaptive UI with Bandit +
// Working Open & Favorite
// ==============================

// ----- Data -----
const VARIANTS = [
  { id: "A", classes: ["dense", "small-cards"], theme: "dark",  description: "Dense + Small Cards + Dark" },
  { id: "B", classes: ["spacious","small-cards"], theme: "light", description: "Spacious + Small Cards + Light" },
  { id: "C", classes: ["dense","large-cards"],    theme: "dark",  description: "Dense + Large Cards + Dark" },
  { id: "D", classes: ["spacious","large-cards"], theme: "light", description: "Spacious + Large Cards + Light" },
];

const SAMPLE = [
  { id: 1, title: "Keyboard Shortcuts", text: "Boost productivity by learning essential shortcuts.", url: "https://support.microsoft.com/en-us/windows/keyboard-shortcuts-2bee0b6b-4765-4d3e-31af-8e9aeb0f6ada" },
  { id: 2, title: "Focus Mode",         text: "Hide distractions automatically when your intent is deep work.", url: "https://www.notion.so/product" },
  { id: 3, title: "Adaptive Layouts",   text: "Interfaces that change density and spacing based on your behavior.", url: "https://material.io/design/layout/understanding-layout" },
  { id: 4, title: "Personalized Themes",text: "Let the system learn your preferred theme under different contexts.", url: "https://developer.mozilla.org/docs/Web/CSS/@media/prefers-color-scheme" },
  { id: 5, title: "Smart Recos",        text: "Surface the most relevant items for the moment.", url: "https://dl.acm.org/doi/10.1145/1772690.1772758" }
];

// ----- Persistence helpers -----
const LS_POLICY_KEY = "banditPolicy_v1";
const LS_FAVS_KEY   = "favorites_v1";

const Policy = {
  load() {
    try { return JSON.parse(localStorage.getItem(LS_POLICY_KEY)) ?? { q:{}, n:{}, epsilon: 0.15 }; }
    catch { return { q:{}, n:{}, epsilon: 0.15 }; }
  },
  save(p) { localStorage.setItem(LS_POLICY_KEY, JSON.stringify(p)); },
  reset() { localStorage.removeItem(LS_POLICY_KEY); }
};
const Favorites = {
  load() { try { return new Set(JSON.parse(localStorage.getItem(LS_FAVS_KEY)) ?? []); } catch { return new Set(); } },
  save(set) { localStorage.setItem(LS_FAVS_KEY, JSON.stringify([...set])); }
};

// ----- Contextual bandit -----
function context() {
  const hour = new Date().getHours();
  const width = window.innerWidth;
  const prefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
  const hourBucket = hour < 8 ? "morning" : hour < 16 ? "day" : "evening";
  const widthBucket = width < 600 ? "narrow" : width < 1200 ? "medium" : "wide";
  return { hourBucket, widthBucket, prefersDark };
}
function k(variantId, ctx) { return `${variantId}|${ctx.hourBucket}|${ctx.widthBucket}|${ctx.prefersDark ? "D" : "L"}`; }

function selectVariant(policy, ctx) {
  // explore
  if (Math.random() < policy.epsilon) return VARIANTS[Math.floor(Math.random() * VARIANTS.length)];
  // exploit
  let best = VARIANTS[0], bestQ = -Infinity;
  for (const v of VARIANTS) {
    const qv = policy.q[k(v.id, ctx)] ?? 0;
    if (qv > bestQ) { bestQ = qv; best = v; }
  }
  return best;
}
function updatePolicy(policy, variant, ctx, reward) {
  const key = k(variant.id, ctx);
  const n = (policy.n[key] ?? 0) + 1;
  const q = policy.q[key] ?? 0;
  policy.q[key] = q + (reward - q) / n; // incremental mean
  policy.n[key] = n;
  Policy.save(policy);
}

// ----- Rendering -----
const cardsEl = () => document.getElementById("cards");
const containerEl = () => document.getElementById("container");
const variantLabelEl = () => document.getElementById("variantLabel");

let policy = Policy.load();
let favorites = Favorites.load();
let sessionStart = Date.now();
let currentVariant = null;
let currentCtx = null;

function renderCards() {
  const el = cardsEl();
  el.innerHTML = "";
  for (const item of SAMPLE) {
    const fav = favorites.has(item.id);
    const node = document.createElement("article");
    node.className = "card";
    node.setAttribute("data-id", item.id);
    node.innerHTML = `
      <h3>${item.title}</h3>
      <p>${item.text}</p>
      <div class="actions">
        <button class="action primary" data-action="open">Open</button>
        <button class="action ${fav ? "active":""}" data-action="fav">${fav ? "Favorited" : "Favorite"}</button>
        <button class="action" data-action="dismiss">Dismiss</button>
      </div>
    `;
    el.appendChild(node);
  }
}

function applyVariant(variant) {
  document.body.classList.remove("light"); // reset theme
  if (variant.theme === "light") document.body.classList.add("light");
  const cont = containerEl();
  cont.classList.remove("dense","spacious","small-cards","large-cards");
  for (const c of variant.classes) cont.classList.add(c);
  variantLabelEl().textContent = `${variant.id} — ${variant.description}`;
}

// ----- Rewards & actions -----
function baseReward(action) {
  switch (action) {
    case "open": return 1.0;
    case "fav": return 2.0;
    case "dismiss": return -1.0;
    default: return 0;
  }
}
function dwellBonus() {
  const seconds = (Date.now() - sessionStart) / 1000;
  return Math.max(0, Math.min(1, seconds / 30)); // up to +1 over first 30s
}

function handleOpen(item) {
  // show modal and count reward
  const modal = document.getElementById("modal");
  document.getElementById("modalTitle").textContent = item.title;
  document.getElementById("modalBody").textContent  = item.text;
  const link = document.getElementById("modalLink");
  link.href = item.url;
  modal.classList.add("show");
  modal.setAttribute("aria-hidden", "false");
}
function closeModal() {
  const modal = document.getElementById("modal");
  modal.classList.remove("show");
  modal.setAttribute("aria-hidden", "true");
}

function syncFavoriteButton(btn, isFav) {
  btn.classList.toggle("active", isFav);
  btn.textContent = isFav ? "Favorited" : "Favorite";
}

// ----- Event wiring -----
function attachHandlers() {
  // Card actions (event delegation)
  cardsEl().addEventListener("click", (e) => {
    const btn = e.target.closest("button[data-action]");
    if (!btn) return;
    e.preventDefault();

    const card = btn.closest(".card");
    const id = Number(card?.getAttribute("data-id"));
    const item = SAMPLE.find(x => x.id === id);
    const act = btn.getAttribute("data-action");

    // Visual behaviors
    if (act === "open") {
      handleOpen(item);
    } else if (act === "fav") {
      const newFav = !favorites.has(id);
      if (newFav) favorites.add(id); else favorites.delete(id);
      Favorites.save(favorites);
      syncFavoriteButton(btn, newFav);
    } else if (act === "dismiss") {
      card.remove();
    }

    // Reward update
    const reward = baseReward(act) + dwellBonus();
    updatePolicy(policy, currentVariant, currentCtx, reward);
  });

  // Modal close controls
  document.getElementById("modal").addEventListener("click", (e) => {
    if (e.target.matches("[data-close]")) {
      e.preventDefault();
      closeModal();
    }
  });
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") closeModal();
  });

  // Sidebar controls
  document.getElementById("resetPolicyBtn").addEventListener("click", () => {
    Policy.reset(); policy = Policy.load();
    alert("Policy reset. The system will explore again.");
  });
  document.getElementById("toggleThemeBtn").addEventListener("click", () => {
    document.body.classList.toggle("light");
  });

  // Re-evaluate context on resize
  window.addEventListener("resize", () => {
    currentCtx = context();
    currentVariant = selectVariant(policy, currentCtx);
    applyVariant(currentVariant);
  });
}

// ----- Init -----
function main() {
  currentCtx = context();
  currentVariant = selectVariant(policy, currentCtx);
  applyVariant(currentVariant);
  renderCards();
  attachHandlers();
}
window.addEventListener("load", main);