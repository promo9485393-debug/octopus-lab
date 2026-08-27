// Общий служебный код всех страниц. Каждая страница грузит ТОЛЬКО свои данные:
// колонка весит 131 КБ, и тянуть её на страницу стратегий незачем.

const fmt = (v, d = 1) => v == null ? "н/д" : (v > 0 ? "+" : "") + v.toFixed(d);
const cls = v => v == null ? "" : (v > 0 ? "pos" : v < 0 ? "neg" : "");
const esc = s => String(s ?? "").replace(/[&<>"]/g, c =>
  ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));

// Ошибку показываем текстом, а не молчанием: пустой блок читается как «проблем нет»,
// хотя означает «данные не загрузились».
function fail(id, what) {
  const el = document.getElementById(id);
  if (el) el.innerHTML = '<div class="err">Не удалось загрузить ' + esc(what) +
    '. Это отсутствие данных, а не подтверждение, что всё в порядке.</div>';
}

function spark(curve) {
  if (!curve || curve.length < 2) return "";
  const n = curve.length, lo = Math.min(...curve), hi = Math.max(...curve);
  const W = 260, H = 42, P = 3;
  const X = i => P + i * (W - 2 * P) / (n - 1);
  const Y = v => H - P - (v - lo) / (hi - lo || 1) * (H - 2 * P);
  const line = curve.map((v, i) => (i ? "L" : "M") + X(i).toFixed(1) + " " + Y(v).toFixed(1)).join(" ");
  const col = curve[n - 1] >= curve[0] ? "var(--ok)" : "var(--bad)";
  return `<svg class="spark" viewBox="0 0 ${W} ${H}" preserveAspectRatio="none" aria-hidden="true">
    <path d="${line} L${X(n - 1).toFixed(1)} ${H - P} L${P} ${H - P} Z" fill="${col}" opacity=".10"/>
    <path d="${line}" fill="none" stroke="${col}" stroke-width="1.6" stroke-linejoin="round"/></svg>`;
}

const STATE_LABEL = {
  confirmed: "край подтверждён", timing_only: "только тайминг",
  selection_only: "только отбор", not_confirmed: "не подтверждён",
  unprofitable: "убыточна", overfit: "подгонка"
};

function nullRow(n) {
  if (!n || n.error) return "";
  return `<div class="nullrow"><span class="${n.passed ? "pass" : "fail"}">${n.passed ? "✔" : "✕"}</span>
    <span style="flex:1">${esc(n.what)}</span>
    <b class="${n.passed ? "pass" : "fail"}">${n.beat}/${n.n}</b></div>`;
}

// подсветка текущего раздела в навигации
document.addEventListener("DOMContentLoaded", () => {
  const here = location.pathname.split("/").pop() || "index.html";
  document.querySelectorAll("nav a").forEach(a => {
    if (a.getAttribute("href") === here) a.classList.add("active");
  });
});
