// Hand-drawn inline SVG cartoons. All decorative (aria-hidden); meaning is always also given in text.

const ghostBody = (fill = "#f3ecff") => `
  <path d="M32 4C17 4 8 15 8 30v34l8-6 8 6 8-6 8 6 8-6 8 6V30C56 15 47 4 32 4z" fill="${fill}"/>
  <ellipse cx="24" cy="30" rx="4" ry="6" fill="#19161d"/><ellipse cx="40" cy="30" rx="4" ry="6" fill="#19161d"/>
  <circle cx="25.5" cy="27.5" r="1.4" fill="#fff"/><circle cx="41.5" cy="27.5" r="1.4" fill="#fff"/>
  <ellipse cx="32" cy="44" rx="4" ry="3.2" fill="#19161d"/>
  <ellipse cx="17" cy="38" rx="3.5" ry="2" fill="#ff80b5" opacity=".55"/><ellipse cx="47" cy="38" rx="3.5" ry="2" fill="#ff80b5" opacity=".55"/>`;

export const ghost = (cls = "ghost") =>
  `<svg class="${cls}" viewBox="0 0 64 68" aria-hidden="true" focusable="false">${ghostBody()}</svg>`;

export const bat = (cls = "bat") => `<svg class="${cls}" viewBox="0 0 64 30" aria-hidden="true" focusable="false">
  <path d="M32 9c1.5-3 4.5-3 6 0 4-5 13-8 24-5-5 2-7 7-7 13-3-3-7-3-9 0-2-2-5-3-7-1-1 2-3 3-4 3s-3-1-4-3c-2-2-5-1-7 1-2-3-6-3-9 0 0-6-2-11-7-13 11-3 20 0 24 5 1.5-3 4.5-3 6 0z" fill="#7138cc"/>
  <circle cx="29.5" cy="11" r="1" fill="#ffcf99"/><circle cx="34.5" cy="11" r="1" fill="#ffcf99"/></svg>`;

export const moon = `<svg class="moon" viewBox="0 0 80 80" aria-hidden="true" focusable="false">
  <circle cx="40" cy="40" r="34" fill="#e2d3fe"/><circle cx="28" cy="30" r="6" fill="#cbb8f0"/>
  <circle cx="50" cy="48" r="9" fill="#cbb8f0"/><circle cx="48" cy="22" r="4" fill="#cbb8f0"/></svg>`;

const stone = (cracked: boolean) => `
  <path d="M14 86V36C14 20 26 9 40 9s26 11 26 27v50z" fill="#3a3442" stroke="#5f5670" stroke-width="2"/>
  <text x="40" y="48" text-anchor="middle" font-family="Georgia, serif" font-weight="700" font-size="15" fill="#c9c2d6">RIP</text>
  <path d="M26 58h28M26 66h20" stroke="#5f5670" stroke-width="3" stroke-linecap="round"/>
  ${cracked ? '<path d="M40 9l-4 12 6 7-5 10" fill="none" stroke="#19161d" stroke-width="2"/>' : ""}
  <path d="M4 88c6-6 10-6 14-2 4-6 9-6 12 0 5-5 9-5 13 0 4-6 9-6 13 0 4-5 9-5 12 0 3-4 6-4 8 2z" fill="#2e5a44"/>`;

// resurrected: a ghost rises from the stone; lost: the stone is cracked; archived: just the stone.
export const tombstone = (status: "resurrected" | "archived" | "lost") =>
  `<svg class="stone-art" viewBox="${status === "resurrected" ? "0 -34 80 124" : "0 0 80 90"}" aria-hidden="true" focusable="false">
    ${status === "resurrected" ? `<g class="rising"><g transform="translate(18 -32) scale(.7)">${ghostBody("#d9fbe8")}</g></g>` : ""}
    ${stone(status === "lost")}
  </svg>`;
