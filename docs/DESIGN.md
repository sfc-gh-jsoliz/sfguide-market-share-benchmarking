# Design: Market Share & Vertical Benchmarking (v2)

The app is titled with the pack's plain name, **Market Share & Vertical Benchmarking**. No coined product name.

## Audience and voice

Strategy, benchmarking and merchant-sales leaders at a payments processor or acquirer. They think in basis points, verticals (merchant categories) and "are we growing faster than the market". Voice: plain, numerate, a little editorial, like a strategy memo. Short labels ("Gaining share", "Growth gap"), numbers first, no hype.

## Logo mark (inline SVG)

A rounded espresso square holding a pie wedge (our slice of the market) lifted out of a ring, with a small upward tick.

```svg
<svg viewBox="0 0 32 32" width="30" height="30" aria-hidden="true">
  <rect width="32" height="32" rx="9" fill="#241B17"/>
  <circle cx="15" cy="17" r="8.5" fill="none" stroke="#F4EEE9" stroke-width="2.2" stroke-opacity=".55"/>
  <path d="M17.2 14.8V6.4a8.5 8.5 0 0 1 8.4 8.4Z" fill="#D63FA3"/>
  <path d="M20 24.5l2.6-2.6 2 2 3-3.4" fill="none" stroke="#E0A33A" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
</svg>
```

## Palette

| Token | Hex | Use |
|---|---|---|
| `rail` | `#241B17` | Left navigation rail, logo square, landing hero band (espresso) |
| `rail-2` | `#33271F` | Active rail item, hover on the rail |
| `rail-ink` | `#F4EEE9` | Text on the rail (14.7:1 on `rail`) |
| `rail-muted` | `#BFAFA4` | Secondary text on the rail (7.9:1) |
| `canvas` | `#FAF7F3` | Page background (warm chalk) |
| `surface` | `#FFFFFF` | Cards, tables, drawers |
| `surface-2` | `#F2ECE6` | Table heads, wells, skeletons |
| `line` | `#E4DAD1` | Hairlines and borders |
| `ink` | `#231C18` | Body text (15.7:1 on canvas) |
| `ink-2` | `#4A3F38` | Secondary text (9.5:1) |
| `muted` | `#6E6158` | Captions (5.6:1, passes AA) |
| `brand` | `#B0287F` | Fuchsia brand: primary buttons, focus rings, our-share series (6.1:1 on white) |
| `brand-soft` | `#F8E3F0` | Brand tint for pills and the selected row |
| `ochre` | `#E0A33A` | Accent on dark surfaces only (tick in the logo, rail active marker) |
| `ochre-ink` | `#7A4C05` | Ochre text on light surfaces, "Holding" pills (6.4:1 on `ochre-soft`) |
| `ochre-soft` | `#FBEFD8` | Sample-mode badge, Holding pill background |
| `market` | `#5B6B7A` | Market series in charts (slate, neutral, so our book reads as the subject) |
| `gain` | `#1D7A46` | Gaining share (5.3:1 on white; 4.6:1 on `gain-soft`) |
| `gain-soft` | `#E1F2E7` | Gaining pill background |
| `loss` | `#B3261E` | Losing share (6.5:1 on white) |
| `loss-soft` | `#FBE5E2` | Losing pill background |

Contrast was checked with a WCAG relative-luminance script for every text/background pair above; all pass AA (4.5:1) for body text.

Category colors (charts only, each with a text label, never color alone): Restaurants `#B0287F`, Grocery `#1D7A46`, Health `#2F6FA3`, Furniture `#8A5A00`, Apparel `#6D4BA0`, Electronics `#B3261E`.

## Typography

- System UI stack (`ui-sans-serif, system-ui, -apple-system, "Segoe UI", Roboto, sans-serif`) for everything, so the Streamlit in Snowflake paste-in path looks identical with no font files. No web fonts, no CDN.
- Numbers use `font-variant-numeric: tabular-nums`; KPI values are 800 weight with tight tracking (-0.03em), which gives the "memo with numbers" feel.
- Small caps-style eyebrows: 11 px, 700, letter-spacing 0.08em, uppercase.

## Layout model

- **Left rail** (232 px, espresso) with the logo, the app name, five sections and, at the bottom, the user/role chip and the Sample/Live environment badge. Below 900 px the rail becomes a top bar with a horizontally scrolling section strip.
- Content column max 1180 px. Each screen opens with a heading row: title, one-line purpose, and a capability badge naming the Snowflake object behind it (for example "MARKET_SHARE_BENCHMARK view").
- Density: medium. Cards with 14 px radius, 1 px hairline, no heavy shadows; one soft shadow on drawers only.

## Screens

1. **Overview**: four KPI tiles with sparklines (book share in bps, processed volume, verticals gaining share, widest growth gap), the share ribbon, a ranked gainers/losers list, and an editorial insight line.
2. **Verticals**: sortable, filterable table with status pills (Gaining, Holding, Losing) and an inline share bar; clicking a row opens a detail drawer with processed vs market, share over 24 months, and the month table.
3. **Growth gap**: our year-over-year growth against the market's, per vertical, as a diverging bar chart plus a quadrant read-out.
4. **Share notes**: generate a grounded note (AI_COMPLETE draft + AI_COMPLETE verifier) for the whole book or one vertical, with staged steps, streaming reveal, the fact pack as sources, and a gallery of saved notes with Verified / Needs review badges.
5. **Ask an analyst**: questions to the Cortex Agent over the semantic view, with the generated SQL and the result table as sources.

## Chart style

- **Share ribbon** (signature chart): a slope chart from the first month (Jul 2024) to the latest (Jun 2026), one line per vertical, in bps, labels at both ends, gainers in category color and thicker, losers dashed. Nobody else in the catalog uses a slope chart as the hero.
- Line charts: our share in brand fuchsia, market in slate, 2 px lines, no area fills, light dotted grid on y only, tooltips with month and formatted value, legends at the bottom.
- Diverging bars for growth gap, centered on zero, gain green right, loss red left.

## Motion

- 180 ms fade-up on cards, staggered 40 ms for KPI tiles; animated count-up on KPI values; skeleton shimmer while Live queries run; spinner ring on the current AI step; text reveal for AI output at roughly 60 characters per frame. All disabled under `prefers-reduced-motion`.

## Dark mode

Not in this design. The landing page and app are light only; the rail and hero give the dark contrast. Listed as a skipped Should.

## Landing page (`docs/index.html`)

Same tokens and logo. Espresso hero band with a problem-first headline ("Your book is growing. Is it growing faster than the market?"), the share ribbon drawn as inline SVG from the synthetic data, then the four-step how-it-works strip, captioned screenshots, the capability table, setup, cost, and the disclaimer. No scripts from a CDN.

## How this differs from live packs

Looked at the landing pages and Try apps of: Auto Finance Portfolio Analytics (navy, lime and teal, top bar), Workforce Intelligence (violet and coral on deep plum), Cross-Border & FX v2 (pine and saffron, top bar, Space Grotesk), Dispute Intelligence v2 (deep teal masthead, mint), Macro Stress Testing v2 (sand and burnt orange), Verified Bank Research v2 (stone and gold shield), Complaints Intelligence (burgundy on stone), Continuous Control Testing (ink and vermilion, Plex), Governed Context Layer (graphite night with lime), Loan File Review (cobalt and yellow blueprint), Market Data Discovery (glacier, navy and pink contours), Trade Reporting Validation (amber on near-black), Client Account Views (amber dial on dark).

What this pack avoids:
- No navy, teal, pine, violet, cobalt, burgundy or lime as the base: espresso plus fuchsia is new to the catalog.
- No top-bar shell (most Payments v2 rebuilds use one): this one uses a left rail.
- No KPI-grid-first hero on the landing page: the hero is the share ribbon slope chart.
- No web-font display face shared with another pack: system stack with heavy tabular numerals.
