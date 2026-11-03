import "./style.css";
import { bat, ghost, moon, tombstone } from "./art";

type Video = {
  id: string; title: string; channel: string; crypt: string; why: string;
  n: number; from: number; to: number; alive: boolean; immortal: boolean;
};
type Hit = { id: string; title: string; channel: string; score: number };
type Grave = {
  id: string; title: string | null; n: number; from: number; to: number;
  status: "resurrected" | "archived" | "lost"; archive: string; reupload: Hit | null;
  epitaph: string; comment: string;
};
type View = "crypts" | "immortals" | "graveyard" | "origin";

const PAGE = 60;
const WATCHED_KEY = "hackirotube.watched";
const $ = <T extends HTMLElement>(sel: string) => document.querySelector<T>(sel)!;

let videos: Video[] = [];
let graves: Grave[] = [];
let view: View = "crypts";
let crypt: string | null = null;
let query = "";
let shown = PAGE;
const watched = new Set<string>(JSON.parse(localStorage.getItem(WATCHED_KEY) ?? "[]"));

const esc = (s: string) => s.replace(/[&<>"']/g, (c) => `&#${c.charCodeAt(0)};`);
const yt = (id: string) => `https://www.youtube.com/watch?v=${id}`;
const years = (a: number, b: number) => (a === b ? `${a}` : `${a}–${b}`);
const people = (n: number) => `${n} ${n === 1 ? "person" : "people"}`;
const matches = (title: string | null) => !query || (title ?? "").toLowerCase().includes(query);

function current(): (Video | Grave)[] {
  if (view === "graveyard") return graves.filter((g) => matches(g.title));
  if (view === "immortals")
    return videos.filter((v) => v.immortal && matches(v.title)).sort((a, b) => b.to - b.from - (a.to - a.from) || b.n - a.n);
  return videos.filter((v) => (!crypt || v.crypt === crypt) && matches(v.title));
}

function videoCard(v: Video): string {
  const seen = watched.has(v.id);
  return `<article class="card${seen ? " seen" : ""}" tabindex="-1" data-id="${v.id}">
    <a class="thumb" href="${yt(v.id)}" target="_blank" rel="noopener" tabindex="-1" aria-hidden="true">
      <img loading="lazy" src="https://i.ytimg.com/vi/${v.id}/mqdefault.jpg" alt="" width="320" height="180"></a>
    <h3><a class="open" href="${yt(v.id)}" target="_blank" rel="noopener">${esc(v.title)}</a></h3>
    <p class="meta">${esc(v.channel)} · recommended by ${people(v.n)} · ${years(v.from, v.to)}
      ${v.immortal ? '<span class="badge">Immortal</span>' : ""}</p>
    <p class="why">${esc(v.why)}</p>
    <button type="button" class="watch" aria-pressed="${seen}">${seen ? "Watched" : "Mark watched"}</button>
  </article>`;
}

const EPITAPH = { resurrected: "Possibly resurrected", archived: "Remains archived", lost: "Lost" };

function graveCard(g: Grave): string {
  const re = g.reupload;
  // A re-upload is a title match, not proof, so it is offered as a possibility.
  const primary = re ? yt(re.id) : g.archive;
  return `<article class="card grave ${g.status}" tabindex="-1" data-id="${g.id}">
    ${tombstone(g.status)}
    <h3><a class="open" href="${primary}" target="_blank" rel="noopener">${g.title ? esc(g.title) : "Name lost to time"}</a></h3>
    <p class="meta"><strong>${EPITAPH[g.status]}</strong> · mourned by ${people(g.n)} · recommended ${years(g.from, g.to)}</p>
    ${g.epitaph ? `<blockquote>${esc(g.epitaph)}…</blockquote>` : ""}
    <ul class="links">
      ${re ? `<li><a href="${yt(re.id)}" target="_blank" rel="noopener">Possible re-upload: ${esc(re.title)} (${esc(re.channel)})</a></li>` : ""}
      <li><a href="${g.archive}" target="_blank" rel="noopener">${g.status === "lost" ? "Search the Internet Archive" : "Archived page"}</a></li>
      <li><a href="https://news.ycombinator.com/item?id=${g.comment}" target="_blank" rel="noopener">Where HN mourned it</a></li>
    </ul>
  </article>`;
}

function renderCrypts() {
  const aside = $("#crypts");
  aside.hidden = view !== "crypts";
  if (aside.hidden) return;
  const counts = new Map<string, number>();
  for (const v of videos) counts.set(v.crypt, (counts.get(v.crypt) ?? 0) + 1);
  const rows = [...counts].sort((a, b) => b[1] - a[1]);
  const link = (name: string | null, n: number) =>
    `<li><a href="#/${name ? "crypt/" + encodeURIComponent(name) : ""}"${crypt === name ? ' aria-current="page"' : ""}>${esc(name ?? "All crypts")} <span>${n}</span></a></li>`;
  aside.innerHTML = `<h2>Crypts</h2><ul>${link(null, videos.length)}${rows.map(([c, n]) => link(c, n)).join("")}</ul>`;
}

function render() {
  const origin = view === "origin";
  $("#origin").hidden = !origin;
  $("#status").hidden = $("#list").hidden = origin;
  if (origin) {
    $("#more").hidden = true;
    markNav();
    renderCrypts();
    return;
  }
  const items = current();
  const list = $("#list");
  list.className = view === "graveyard" ? "graveyard" : "";
  list.innerHTML = items.length
    ? items.slice(0, shown).map((x) => ("crypt" in x ? videoCard(x) : graveCard(x))).join("")
    : `<div class="empty">${ghost("ghost lonely")}<p>Not even a ghost. Try another search.</p></div>`;
  $("#more").hidden = items.length <= shown;
  const label = view === "graveyard" ? "tombstones" : view === "immortals" ? "immortals" : crypt ? `in ${crypt}` : "videos";
  $("#status").textContent = items.length
    ? `${items.length.toLocaleString()} ${label}${query ? ` matching “${query}”` : ""}`
    : "Nothing stirs here.";
  markNav();
  renderCrypts();
}

function markNav() {
  document.querySelectorAll<HTMLAnchorElement>("nav a").forEach((a) =>
    a.dataset.view === view ? a.setAttribute("aria-current", "page") : a.removeAttribute("aria-current"));
}

function route() {
  const [, kind, arg] = location.hash.split("/");
  view = kind === "immortals" || kind === "graveyard" || kind === "origin" ? kind : "crypts";
  crypt = kind === "crypt" && arg ? decodeURIComponent(arg) : null;
  shown = PAGE;
  render();
}

function toggleWatched(card: HTMLElement) {
  const id = card.dataset.id!;
  if (card.classList.contains("grave")) return;
  watched.has(id) ? watched.delete(id) : watched.add(id);
  localStorage.setItem(WATCHED_KEY, JSON.stringify([...watched]));
  const seen = watched.has(id);
  card.classList.toggle("seen", seen);
  const btn = card.querySelector<HTMLButtonElement>(".watch")!;
  btn.setAttribute("aria-pressed", String(seen));
  btn.textContent = seen ? "Watched" : "Mark watched";
}

function exportView() {
  const blob = new Blob([JSON.stringify(current(), null, 1)], { type: "application/json" });
  const a = Object.assign(document.createElement("a"), {
    href: URL.createObjectURL(blob), download: `hackirotube-${crypt ?? view}.json`.replace(/[^\w.-]+/g, "-"),
  });
  a.click();
  URL.revokeObjectURL(a.href);
}

function move(step: number) {
  const cards = [...document.querySelectorAll<HTMLElement>("#list .card")];
  if (!cards.length) return;
  const at = cards.indexOf(document.activeElement?.closest(".card") as HTMLElement);
  const next = cards[Math.min(cards.length - 1, Math.max(0, at + step))];
  next.focus();
  next.scrollIntoView({ block: "nearest" });
}

document.addEventListener("keydown", (e) => {
  const help = $<HTMLDialogElement>("#help");
  if (e.target instanceof HTMLInputElement) {
    if (e.key === "Escape") e.target.blur();
    return;
  }
  if (e.ctrlKey || e.metaKey || e.altKey || help.open) return;
  const card = document.activeElement?.closest<HTMLElement>(".card");
  const keys: Record<string, () => void> = {
    j: () => move(1), k: () => move(-1),
    o: () => card?.querySelector<HTMLAnchorElement>("a.open")?.click(),
    Enter: () => document.activeElement === card && card?.querySelector<HTMLAnchorElement>("a.open")?.click(),
    w: () => card && toggleWatched(card),
    "/": () => $("#q").focus(),
    "1": () => (location.hash = "#/"), "2": () => (location.hash = "#/immortals"), "3": () => (location.hash = "#/graveyard"), "4": () => (location.hash = "#/origin"),
    x: exportView, "?": () => help.showModal(),
  };
  if (keys[e.key]) {
    e.preventDefault();
    keys[e.key]();
  }
});

$("#list").addEventListener("click", (e) => {
  const btn = (e.target as HTMLElement).closest(".watch");
  if (btn) toggleWatched(btn.closest<HTMLElement>(".card")!);
});
$("#more").addEventListener("click", () => {
  shown += PAGE;
  render();
  move(0);
});
$<HTMLInputElement>("#q").addEventListener("input", (e) => {
  query = (e.target as HTMLInputElement).value.trim().toLowerCase();
  shown = PAGE;
  render();
});
$("#export").addEventListener("click", exportView);
$(".sky").innerHTML = moon + bat("bat b1") + bat("bat b2") + bat("bat b3") + ghost("ghost mascot");
$("#help-btn").addEventListener("click", () => $<HTMLDialogElement>("#help").showModal());
window.addEventListener("hashchange", route);

fetch(`${import.meta.env.BASE_URL}catalog.json`)
  .then((r) => (r.ok ? r.json() : Promise.reject(new Error(`catalog.json: HTTP ${r.status}`))))
  .then((data: { videos: Video[]; graves: Grave[] }) => {
    videos = data.videos.sort((a, b) => b.n - a.n);
    graves = data.graves.sort((a, b) => b.n - a.n);
    document.querySelector('nav a[data-view="graveyard"]')!.insertAdjacentHTML("beforeend", ` <span>${graves.length}</span>`);
    const status = (s: Grave["status"]) => graves.filter((g) => g.status === s).length;
    const stats: Record<string, number> = {
      videos: videos.length, immortals: videos.filter((v) => v.immortal).length, graves: graves.length,
      resurrected: status("resurrected"), archived: status("archived"), lost: status("lost"),
    };
    document.querySelectorAll<HTMLElement>("#origin [data-stat]").forEach((el) => {
      const n = stats[el.dataset.stat!];
      if (n !== undefined) el.textContent = n.toLocaleString();
    });
    route();
  })
  .catch((err) => ($("#status").textContent = `The catalog would not rise: ${err.message}. Run pipeline/publish.py.`));
