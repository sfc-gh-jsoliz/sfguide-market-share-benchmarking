"""Brand: tokens from docs/DESIGN.md, global CSS and small HTML helpers."""
import base64
import html

T = {
    "rail": "#241B17", "rail2": "#33271F", "railInk": "#F4EEE9", "railMuted": "#BFAFA4",
    "canvas": "#FAF7F3", "surface": "#FFFFFF", "surface2": "#F2ECE6", "line": "#E4DAD1",
    "ink": "#231C18", "ink2": "#4A3F38", "muted": "#6E6158",
    "brand": "#B0287F", "brandSoft": "#F8E3F0", "ochre": "#E0A33A", "ochreInk": "#7A4C05", "ochreSoft": "#FBEFD8",
    "market": "#5B6B7A", "gain": "#1D7A46", "gainSoft": "#E1F2E7", "loss": "#B3261E", "lossSoft": "#FBE5E2",
}
CAT_COLORS = {
    "Restaurants & Food Service": "#B0287F", "Food & Beverage Stores": "#1D7A46",
    "Health & Personal Care": "#2F6FA3", "Furniture & Home Furnishings": "#8A5A00",
    "Clothing & Accessories": "#6D4BA0", "Electronics & Appliances": "#B3261E",
}
SHORT = {
    "Restaurants & Food Service": "Restaurants", "Food & Beverage Stores": "Grocery",
    "Health & Personal Care": "Health", "Furniture & Home Furnishings": "Furniture",
    "Clothing & Accessories": "Apparel", "Electronics & Appliances": "Electronics",
}

LOGO = ('<svg viewBox="0 0 32 32" width="32" height="32" xmlns="http://www.w3.org/2000/svg">'
        '<rect width="32" height="32" rx="9" fill="#241B17" stroke="#4A3A30"/>'
        '<circle cx="15" cy="17" r="8.5" fill="none" stroke="#F4EEE9" stroke-width="2.2" stroke-opacity=".55"/>'
        '<path d="M17.2 14.8V6.4a8.5 8.5 0 0 1 8.4 8.4Z" fill="#D63FA3"/>'
        '<path d="M20 24.5l2.6-2.6 2 2 3-3.4" fill="none" stroke="#E0A33A" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>')
LOGO_IMG = ('<img alt="" width="32" height="32" src="data:image/svg+xml;base64,'
            + base64.b64encode(LOGO.encode()).decode() + '">')

CSS = """
<style>
@property --n{syntax:"<integer>";initial-value:0;inherits:false}
:root{--rail:#241B17;--rail2:#33271F;--railInk:#F4EEE9;--railMuted:#BFAFA4;--canvas:#FAF7F3;--surface:#fff;--surface2:#F2ECE6;--line:#E4DAD1;--ink:#231C18;--ink2:#4A3F38;--muted:#6E6158;--brand:#B0287F;--brandSoft:#F8E3F0;--ochre:#E0A33A;--ochreInk:#7A4C05;--ochreSoft:#FBEFD8;--market:#5B6B7A;--gain:#1D7A46;--gainSoft:#E1F2E7;--loss:#B3261E;--lossSoft:#FBE5E2;
 --sans:ui-sans-serif,system-ui,-apple-system,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif}
html{overflow-x:clip}
html,body,.stApp,.stMarkdown,button,input,textarea,select{font-family:var(--sans)}
[data-testid="stHeader"]{background:transparent}
[data-testid="stToolbar"],[data-testid="stDecoration"],#MainMenu,footer{display:none}
.stApp{background:var(--canvas);color:var(--ink)}
.block-container,[data-testid="stMainBlockContainer"]{max-width:1180px;padding-top:1.6rem!important;padding-left:1.4rem;padding-right:1.4rem}
/* left rail */
[data-testid="stSidebar"]{background:var(--rail);border-right:0}
[data-testid="stSidebar"]>div:first-child{background:var(--rail)}
[data-testid="stSidebar"] *{color:var(--railInk)}
[data-testid="stSidebarHeader"]{height:.5rem;min-height:.5rem;padding:0}
[data-testid="stSidebarCollapseButton"] svg,[data-testid="stSidebarCollapseButton"] span{color:var(--railMuted)!important}
.ms-brand{display:flex;gap:.65rem;align-items:center;padding:.2rem 0 1rem;border-bottom:1px solid #3B2E26;margin-bottom:.8rem}
.ms-brand b{display:block;font-size:.98rem;line-height:1.2;font-weight:750;letter-spacing:-.01em}
.ms-brand span{display:block;font-size:.72rem;color:var(--railMuted)!important;margin-top:.15rem}
.ms-eyebrow{font-size:.66rem;font-weight:700;letter-spacing:.09em;text-transform:uppercase;color:var(--railMuted)!important;margin:.6rem 0 .35rem}
.st-key-nav [role="radiogroup"]{gap:.15rem!important}
.st-key-nav label[data-baseweb="radio"]{margin:0!important;padding:.55rem .7rem;border-radius:9px;width:100%;cursor:pointer;border-left:3px solid transparent;transition:background .15s}
.st-key-nav label[data-baseweb="radio"]>div:first-child{display:none}
.st-key-nav label[data-baseweb="radio"] p{font-size:.92rem;font-weight:550;color:var(--railMuted)!important}
.st-key-nav label[data-baseweb="radio"]:hover{background:var(--rail2)}
.st-key-nav label[data-baseweb="radio"]:has(input:checked){background:var(--rail2);border-left-color:var(--ochre)}
.st-key-nav label[data-baseweb="radio"]:has(input:checked) p{color:var(--railInk)!important;font-weight:700}
.st-key-modes [data-testid="stButtonGroup"] button{background:transparent;border-color:#4A3A30;min-height:2rem;font-size:.82rem}
.st-key-modes [data-testid="stButtonGroup"] button p{color:var(--railInk)!important}
.st-key-modes [data-testid="stButtonGroup"] button[kind$="Active"]{background:var(--ochre);border-color:var(--ochre)}
.st-key-modes [data-testid="stButtonGroup"] button[kind$="Active"] p{color:var(--rail)!important;font-weight:700}
.ms-who{margin-top:1rem;padding:.7rem;border:1px solid #3B2E26;border-radius:10px;font-size:.78rem}
.ms-who b{display:block;font-size:.84rem}
.ms-who span{color:var(--railMuted)!important}
.ms-env{display:inline-flex;align-items:center;gap:.35rem;font-size:.72rem;font-weight:700;border-radius:999px;padding:.18rem .6rem;margin-top:.5rem}
.ms-env.sample{background:var(--ochreSoft);color:var(--ochreInk)!important}
.ms-env.live{background:#1E3B2B;color:#BFF0D2!important}
.ms-env i{width:7px;height:7px;border-radius:50%;background:currentColor;display:inline-block}
/* heading row */
.ms-h{display:flex;align-items:flex-end;justify-content:space-between;gap:1rem;flex-wrap:wrap;margin:0 0 1.1rem}
.ms-h .eb{font-size:.68rem;font-weight:700;letter-spacing:.09em;text-transform:uppercase;color:var(--brand);margin:0 0 .25rem}
.ms-h h1{font-size:1.75rem;line-height:1.15;margin:0;color:var(--ink);font-weight:800;letter-spacing:-.025em;padding:0}
.ms-h p{margin:.3rem 0 0;color:var(--muted);font-size:.92rem;max-width:64ch}
.ms-cap{display:inline-flex;gap:.35rem;align-items:center;font-size:.72rem;font-weight:600;color:var(--brand);background:var(--brandSoft);border-radius:6px;padding:.22rem .55rem;max-width:100%;flex-wrap:wrap}
.ms-cap.sample{color:var(--ochreInk);background:var(--ochreSoft)}
/* cards */
.ms-card,[class*="st-key-card"]{background:var(--surface);border:1px solid var(--line);border-radius:14px;min-width:0}
[class*="st-key-card"]{padding:1rem 1.1rem .7rem;animation:msIn .18s ease-out both}
.ms-card{padding:1rem 1.1rem}
.ms-card-h{font-weight:750;font-size:1rem;color:var(--ink);margin:0 0 .1rem}
.ms-card-s{font-size:.8rem;color:var(--muted);margin:0 0 .6rem}
@keyframes msIn{from{opacity:0;transform:translateY(6px)}to{opacity:1;transform:none}}
/* kpis */
.ms-kpis{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:.8rem;margin-bottom:1rem}
.ms-kpi{background:var(--surface);border:1px solid var(--line);border-radius:14px;padding:.9rem 1rem .85rem;position:relative;overflow:hidden;animation:msIn .2s ease-out both;transition:transform .15s,border-color .15s;min-width:0}
.ms-kpi:hover{transform:translateY(-1px);border-color:#D2C3B6}
.ms-kpi:nth-child(2){animation-delay:.04s}.ms-kpi:nth-child(3){animation-delay:.08s}.ms-kpi:nth-child(4){animation-delay:.12s}
.ms-kpi .k{font-size:.68rem;color:var(--muted);font-weight:700;letter-spacing:.07em;text-transform:uppercase}
.ms-kpi .v{font-size:1.85rem;font-weight:800;color:var(--ink);margin:.3rem 0 .15rem;font-variant-numeric:tabular-nums;letter-spacing:-.03em;line-height:1.05}
.ms-kpi .v small{font-size:.85rem;font-weight:700;color:var(--muted);margin-left:.2rem;letter-spacing:0}
.ms-kpi .cnt{animation:msCount .8s ease-out forwards;counter-reset:n var(--n)}
.ms-kpi .cnt::after{content:counter(n)}
@keyframes msCount{from{--n:0}}
.ms-kpi .d{font-size:.78rem;color:var(--muted)}
.ms-kpi svg{position:absolute;right:.8rem;top:.8rem}
.up{color:var(--gain);font-weight:700}.down{color:var(--loss);font-weight:700}.flat{color:var(--ochreInk);font-weight:700}
/* pills */
.ms-pill{display:inline-flex;align-items:center;gap:.3rem;font-size:.72rem;font-weight:700;border-radius:999px;padding:.16rem .58rem;white-space:nowrap}
.ms-pill.Gaining,.ms-pill.ok{background:var(--gainSoft);color:var(--gain)}
.ms-pill.Losing,.ms-pill.warn{background:var(--lossSoft);color:var(--loss)}
.ms-pill.Holding{background:var(--ochreSoft);color:var(--ochreInk)}
.ms-pill.brand{background:var(--brandSoft);color:var(--brand)}
/* ranked list */
.ms-rank{list-style:none;margin:0;padding:0}
.ms-rank li{display:grid;grid-template-columns:minmax(0,1fr) auto;gap:.3rem .8rem;align-items:center;padding:.55rem 0;border-bottom:1px solid #EFE7E0;font-size:.88rem}
.ms-rank li:last-child{border-bottom:0}
.ms-rank .nm{font-weight:650;min-width:0}
.ms-rank .bar{grid-column:1/-1;height:7px;border-radius:4px;background:var(--surface2);position:relative;overflow:hidden}
.ms-rank .bar i{position:absolute;top:0;bottom:0;border-radius:4px;animation:msGrow .7s ease-out both}
.ms-rank .bar b{position:absolute;left:50%;top:-2px;bottom:-2px;width:1px;background:#CDBFB3}
@keyframes msGrow{from{transform:scaleX(0)}to{transform:scaleX(1)}}
.ms-rank .n{font-weight:750;font-variant-numeric:tabular-nums}
/* insight */
.ms-insight{border-left:3px solid var(--brand);background:var(--surface);border-radius:0 12px 12px 0;padding:.75rem .95rem;font-size:.9rem;color:var(--ink2);margin:0 0 1rem;border-top:1px solid var(--line);border-right:1px solid var(--line);border-bottom:1px solid var(--line)}
.ms-insight b{color:var(--ink)}
/* skeleton */
.ms-skel{border-radius:12px;background:linear-gradient(90deg,#F2ECE6 25%,#FBF8F5 37%,#F2ECE6 63%);background-size:400% 100%;animation:msSh 1.3s ease infinite}
@keyframes msSh{0%{background-position:100% 50%}100%{background-position:0 50%}}
/* ai */
.ms-steps{list-style:none;padding:0;margin:.2rem 0 .6rem}
.ms-steps li{display:flex;gap:.55rem;align-items:flex-start;font-size:.86rem;padding:.3rem 0;color:var(--muted)}
.ms-steps li.done{color:var(--ink2)}.ms-steps li.now{color:var(--ink);font-weight:600}
.ms-steps .ic{width:16px;height:16px;border-radius:50%;flex:none;margin-top:2px;border:2px solid var(--line)}
.ms-steps li.done .ic{background:var(--brand);border-color:var(--brand);box-shadow:inset 0 0 0 3px #fff}
.ms-steps li.now .ic{border-color:var(--brand);border-top-color:transparent;animation:msSpin .8s linear infinite}
@keyframes msSpin{to{transform:rotate(360deg)}}
.ms-label{display:inline-flex;align-items:center;gap:.3rem;font-size:.7rem;font-weight:700;letter-spacing:.04em;text-transform:uppercase;border-radius:6px;padding:.2rem .5rem;background:var(--ochreSoft);color:var(--ochreInk)}
.ms-label.live{background:var(--gainSoft);color:var(--gain)}
.ms-src{font-size:.8rem;color:var(--muted);border-top:1px dashed var(--line);margin-top:.7rem;padding-top:.55rem}
.ms-src code{font-size:.75rem;background:var(--surface2);border-radius:4px;padding:.05rem .3rem;color:var(--ink2)}
[class*="st-key-note_body"] h1,[class*="st-key-card_answer"] h1{font-size:1.3rem!important;line-height:1.3!important;padding:.3rem 0!important}
[class*="st-key-note_body"] h2,[class*="st-key-card_answer"] h2{font-size:1.05rem!important;padding:.6rem 0 .2rem!important}
[data-testid="stMarkdownContainer"] table{font-size:.84rem;display:block;overflow-x:auto;max-width:100%}
[data-testid="stMarkdownContainer"] th{background:var(--surface2)}
.ms-empty{text-align:center;padding:2.2rem 1rem;color:var(--muted);font-size:.9rem}
.ms-empty b{display:block;color:var(--ink);font-size:1rem;margin-bottom:.25rem}
.ms-quad{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:.6rem}
.ms-quad div{border:1px solid var(--line);border-radius:12px;padding:.7rem .8rem;background:var(--surface);min-width:0}
.ms-quad h4{margin:0 0 .2rem;font-size:.8rem;font-weight:750}
.ms-quad p{margin:0;font-size:.82rem;color:var(--ink2)}
/* buttons and widgets */
.stButton>button[kind="primary"]{background:var(--brand);border-color:var(--brand);color:#fff;font-weight:700}
.stButton>button[kind="primary"]:hover{background:#921F69;border-color:#921F69;color:#fff}
.stButton>button{border-radius:9px}
[data-testid="stDataFrame"]{border-radius:12px}
@media (max-width:760px){
 .ms-kpis{grid-template-columns:repeat(2,minmax(0,1fr))}
 .ms-kpi .v{font-size:1.4rem}
 .ms-kpi svg{display:none}
 .ms-h h1{font-size:1.4rem}
 .ms-quad{grid-template-columns:1fr}
}
@media (prefers-reduced-motion:reduce){*{animation:none!important;transition:none!important}}
</style>
"""


def esc(s):
    return html.escape(str(s))


def usd(x, d=1):
    x = float(x)
    if abs(x) >= 1e9:
        return f"${x / 1e9:.{d + 1}f}B"
    if abs(x) >= 1e6:
        return f"${x / 1e6:.{d}f}M"
    return f"${x:,.0f}"


def signed(x, d=1, unit=""):
    return f"{x:+.{d}f}{unit}"


def arrow(x, text, flat=0.0):
    if abs(x) <= flat:
        return f'<span class="flat">● {esc(text)}</span>'
    cls, a = ("up", "▲") if x > 0 else ("down", "▼")
    return f'<span class="{cls}">{a} {esc(text)}</span>'


def spark(values, color="#B0287F", w=78, h=26):
    lo, hi = min(values), max(values)
    rng = (hi - lo) or 1
    pts = " ".join(f"{i * w / (len(values) - 1):.1f},{h - 2 - (v - lo) / rng * (h - 4):.1f}" for i, v in enumerate(values))
    return (f'<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}" aria-hidden="true">'
            f'<polyline fill="none" stroke="{color}" stroke-width="1.8" stroke-linejoin="round" points="{pts}"/></svg>')


def kpi(label, value_html, delta_html, values=None, color="#B0287F"):
    s = spark(values, color) if values else ""
    return f'<div class="ms-kpi"><div class="k">{esc(label)}</div><div class="v">{value_html}</div><div class="d">{delta_html}</div>{s}</div>'


def counter(number, suffix="", prefix=""):
    return f'{esc(prefix)}<span class="cnt" style="--n:{int(number)}"></span><small>{esc(suffix)}</small>'


def header(eyebrow, title, sub, cap, sample=False):
    c = "ms-cap sample" if sample else "ms-cap"
    return (f'<div class="ms-h"><div><p class="eb">{esc(eyebrow)}</p><h1>{esc(title)}</h1><p>{esc(sub)}</p></div>'
            f'<span class="{c}">{cap}</span></div>')


def pill(status):
    return f'<span class="ms-pill {esc(status)}">{esc(status)}</span>'


def verdict(status):
    if status == "verified":
        return '<span class="ms-pill ok">✓ Verified</span>'
    return '<span class="ms-pill warn">! Needs review</span>'


def skeleton(rows=((4, 104), (1, 320))):
    out = []
    for n, h in rows:
        cells = "".join(f'<div class="ms-skel" style="height:{h}px"></div>' for _ in range(n))
        out.append(f'<div style="display:grid;grid-template-columns:repeat({n},minmax(0,1fr));gap:.8rem;margin-bottom:.9rem">{cells}</div>')
    return "".join(out)


def steps_html(steps, current, finished=False):
    items = []
    for i, s in enumerate(steps):
        cls = "done" if (i < current or finished) else ("now" if i == current else "")
        items.append(f'<li class="{cls}"><span class="ic"></span><span>{esc(s)}</span></li>')
    return f'<ul class="ms-steps">{"".join(items)}</ul>'


def md_safe(text):
    """Model markdown for st.markdown: dollar signs are not LaTeX."""
    return (text or "").replace("$", "\\$")
