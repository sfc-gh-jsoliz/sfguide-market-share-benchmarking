# Self-review (v2 rebuild, November 2026)

Every item in the Snow Packs v2 self-check and every CONTRIBUTING Must and Should, checked on this branch.

## Self-check before you call it done
| Item | Result |
|---|---|
| Fresh clone runs in Sample (mock) mode | Pass: cloned `v2-rebuild`, every screen renders with Streamlit AppTest, no exceptions |
| Setup, Live mode, cleanup in a clean role | Pass: `sql/setup.sql` run twice; all screens, a share note and an agent question run in Live mode; `sql/cleanup.sql` leaves no database, warehouse or role (SHOW checks); cleanup also re-runs on an empty account |
| Grep files and git history for secrets, account identifiers, user names | Pass: tracked files, every added line in the pushed history, and every blob for local paths |
| Pages URL and `/try/` signed out, phone width | Pass on the fork's Pages preview (branch `v2-rebuild`, `/docs`): no horizontal scroll at 390 px or 1440 px, no console errors; every JS/CSS/SVG from `/try/index.html` returns 200; `docs/.nojekyll` served |
| Dark mode | Skipped: the design is light only (see `docs/DESIGN.md`) |
| Story beats visible in a screenshot | Pass: Restaurants gaining and Electronics losing (Overview, Growth gap), Holding verticals (Verticals), verified and flagged notes (Share notes) |

## v2 requirements
| Item | Result |
|---|---|
| `docs/DESIGN.md` before UI, plain name, no coined product name | Pass |
| Distinct from at least 5 live packs | Pass: 13 named in DESIGN.md; espresso + fuchsia, left rail, slope-chart hero |
| Branded shell, logo, role chip, Sample/Live badge | Pass (Streamlit and `/try/`) |
| KPI tiles with trends, charts with tooltips and legends, sortable/filterable tables, status pills, detail panel, empty/loading/error states | Pass |
| Motion: transitions, skeletons, hover, count-up | Pass; off under reduced motion |
| WCAG AA contrast | Pass: every token pair measured with a script (lowest 4.6:1) |
| AI: 4-8 s staged steps, streaming reveal, sources, "Sample AI response" | Pass |
| Seeded deterministic generator, stories in `data/README.md` | Pass: byte-identical reruns; Live equals Sample on every column |
| Only claim what ran live; preview labels | Pass: the Census overlay and the in-Snowflake Streamlit deploy are marked not verified; no Preview features used |
| Key-pair auth only | Pass |
| App screenshots in `docs/images/`, 2-8 catalog cards 960x600 JPG under 100 KB | Pass: 5 screenshots, 5 cards (73-80 KB) in `docs/catalog/` |

## CONTRIBUTING Musts
| Must | Result |
|---|---|
| Business problem first; one industry and function | Pass (Payments, Strategy) |
| Public repo `sfguide-<topic>`, Apache 2.0 `LICENSE` | Pass (unchanged) |
| GitHub Pages enabled, `.nojekyll` | Pass on the fork; the owner switches his Pages to `/docs` after merge (V2-CHANGES.md) |
| Landing: problem and outcome first, screenshots of the running app with captions naming the capability and matching alt text | Pass |
| Capability named per step; only tested capabilities claimed | Pass |
| Visible disclaimer; repo and docs links (all docs links return 200) | Pass |
| No Snowflake logo files; no internal sales motions | Pass |
| End-user app with a real workflow | Pass |
| No-account mode; simulated AI labeled | Pass |
| Live mode on Snowflake with synthetic data | Pass |
| Synthetic data; dedicated database and XSMALL warehouse; nothing existing changed | Pass |
| Cleanup removes everything | Pass |
| No credentials, account identifiers or internal hostnames in code, screenshots or history; user names redacted | Pass |
| No customer names, deals or internal programs; GA features | Pass |
| README: prerequisites, run steps, objects table, cost and time, limitations, Customize with Cortex Code, owner and review date, license and disclaimer | Pass |
| Outcomes as possibilities; synthetic results qualified | Pass |

## CONTRIBUTING Shoulds
| Should | Result |
|---|---|
| Several screenshots; prerequisites, time and cost near the top | Pass |
| Phone width | Pass |
| Dark mode | Skipped (design choice) |
| No trackers or CDN | Pass |
| Sample/Live switch, setup steps when no connection, no silent fallback | Pass |
| Realistic AI delays and truthful steps | Pass |
| Capability badges in the UI | Pass |
| Least-privilege role | Pass (`MARKET_SHARE_ROLE`) |
| Edition notes | Pass |
| Template repository, topics | Skipped: the owner's repo setting (V2-CHANGES.md) |
| Notebook re-run | Skipped: only its prerequisite text changed; the notebook was not re-executed in this build |
