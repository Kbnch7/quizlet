export function InlineProjectLogo() {
  return (<!-- ruzlet-wordmark.svg -->
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 520 120" width="520" height="120" role="img" aria-labelledby="titleB descB">
  <title id="titleB">Ruzlet wordmark</title>
  <desc id="descB">Ruzlet — icon + wordmark. Colors use CSS variables from site theme.</desc>
  <defs>
    <style>
      .icon-bg { fill: var(--color-primary, #4b6ef5); }
      .icon-accent { fill: var(--color-accent, #8b5cf6); }
      .text { fill: var(--color-foreground, #0f172a); font-family: var(--font-sans, Roboto, sans-serif); font-weight: 700; }
      .text-sub { fill: var(--color-muted-foreground, #6b7280); font-weight: 500; }
    </style>
  </defs>

  <!-- icon at left (smaller, simplified) -->
  <g transform="translate(18,10)">
    <rect x="0" y="0" width="100" height="100" rx="16" class="icon-bg"/>
    <rect x="14" y="18" width="72" height="64" rx="8" class="icon-accent" transform="rotate(-6 50 50)"/>
    <rect x="18" y="22" width="64" height="56" rx="6" fill="white"/>
    <text x="34" y="74" font-size="56" class="text" fill="var(--color-primary-foreground, white)">R</text>
  </g>

  <!-- wordmark -->
  <g transform="translate(140,66)">
    <text class="text" x="0" y="0" font-size="44">Ruzlet</text>
    <text class="text-sub" x="0" y="32" font-size="14">learn • review • remember</text>
  </g>
</svg>
)
}