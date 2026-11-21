/* Market Share & Vertical Benchmarking: hosted no-account example (Sample mode only).
   Computes share, YoY growth, growth gap and status from the bundled seeded rows with the
   same rules as the Snowflake views, and replays AI responses captured from Live runs. */
(function () {
  "use strict";
  var D = window.MSB;
  var COLORS = {"Restaurants & Food Service": "#B0287F", "Food & Beverage Stores": "#1D7A46", "Health & Personal Care": "#2F6FA3",
    "Furniture & Home Furnishings": "#8A5A00", "Clothing & Accessories": "#6D4BA0", "Electronics & Appliances": "#B3261E"};
  var SHORT = {"Restaurants & Food Service": "Restaurants", "Food & Beverage Stores": "Grocery", "Health & Personal Care": "Health",
    "Furniture & Home Furnishings": "Furniture", "Clothing & Accessories": "Apparel", "Electronics & Appliances": "Electronics"};
  var SCOPES = [["ALL", "Whole book"], ["RESTAURANTS", "Restaurants & Food Service"], ["GROCERY", "Food & Beverage Stores"],
    ["HEALTH", "Health & Personal Care"], ["FURNITURE", "Furniture & Home Furnishings"], ["APPAREL", "Clothing & Accessories"],
    ["ELECTRONICS", "Electronics & Appliances"]];
  var MON = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
  var MONL = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var main = $("#main"), tip = $("#tip");

  function esc(s) { return String(s).replace(/[&<>"']/g, function (c) { return {"&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"}[c]; }); }
  function r2(x) { if (x === null || isNaN(x)) return null; var s = x < 0 ? -1 : 1; return s * Math.round(Math.abs(x) * 100 + 1e-9) / 100; }
  function sgn(x, d, u) { return (x >= 0 ? "+" : "−") + Math.abs(x).toFixed(d) + (u || ""); }
  function usd(x) { return Math.abs(x) >= 1e9 ? "$" + (x / 1e9).toFixed(2) + "B" : "$" + (x / 1e6).toFixed(1) + "M"; }
  function mlabel(s) { var p = s.split("-"); return MON[+p[1] - 1] + " " + p[0].slice(2); }
  function mlong(s) { var p = s.split("-"); return MONL[+p[1] - 1] + " " + p[0]; }
  function arrow(x, t, flat) { if (Math.abs(x) <= (flat || 0)) return '<span class="flat">● ' + esc(t) + "</span>"; return x > 0 ? '<span class="up">▲ ' + esc(t) + "</span>" : '<span class="down">▼ ' + esc(t) + "</span>"; }
  function pill(s) { return '<span class="pill ' + esc(s) + '">' + esc(s) + "</span>"; }
  function verdict(s) { return s === "verified" ? '<span class="pill ok">✓ Verified</span>' : '<span class="pill warn">! Needs review</span>'; }
  function wait(ms) { return new Promise(function (r) { setTimeout(r, ms); }); }

  /* ------------------------------------------------------------------ data (mirrors the views) */
  var names = {}; D.categories.forEach(function (c) { names[c.category_code] = c.category_name; });
  var mkt = {}; D.market.forEach(function (m) { mkt[m.category_code + m.month_end] = m.market_sales_usd; });
  var bench = {};
  D.book.forEach(function (b) {
    (bench[b.category_code] = bench[b.category_code] || []).push({
      code: b.category_code, name: names[b.category_code], month: b.month_end, vol: b.processed_volume_usd,
      mkt: mkt[b.category_code + b.month_end], txn: b.txn_count, merchants: b.active_merchants});
  });
  var months = [];
  Object.keys(bench).forEach(function (code) {
    var g = bench[code].sort(function (a, b) { return a.month < b.month ? -1 : 1; });
    g.forEach(function (r, i) {
      r.bps = r2(r.vol / r.mkt * 10000);
      if (i >= 12) {
        r.byoy = r2((r.vol / g[i - 12].vol - 1) * 100); r.myoy = r2((r.mkt / g[i - 12].mkt - 1) * 100); r.gap = r2(r.byoy - r.myoy);
      } else { r.byoy = r.myoy = r.gap = null; }
    });
    if (!months.length) months = g.map(function (r) { return r.month; });
  });
  function avg(a) { return a.reduce(function (s, x) { return s + x; }, 0) / a.length; }
  var summ = Object.keys(bench).map(function (code) {
    var g = bench[code], last = g[g.length - 1];
    var start = r2(avg(g.slice(0, 3).map(function (r) { return r.bps; }))), now = r2(avg(g.slice(-3).map(function (r) { return r.bps; })));
    var pct = r2((now / start - 1) * 100);
    return {code: code, name: last.name, start: start, now: now, change: r2(now - start), pct: pct, vol: last.vol, mkt: last.mkt,
      byoy: last.byoy, myoy: last.myoy, gap: last.gap, merchants: last.merchants, latest: last.month,
      status: pct >= 3 ? "Gaining" : (pct <= -3 ? "Losing" : "Holding")};
  }).sort(function (a, b) { return b.change - a.change; });
  var port = months.map(function (m, i) {
    var v = 0, k = 0; Object.keys(bench).forEach(function (c) { v += bench[c][i].vol; k += bench[c][i].mkt; });
    return {month: m, vol: v, mkt: k, bps: v / k * 10000};
  });

  /* ------------------------------------------------------------------ tooltip */
  function showTip(e, html) { tip.innerHTML = html; tip.classList.add("on"); var x = e.clientX + 14, y = e.clientY + 14; var w = tip.offsetWidth, h = tip.offsetHeight; if (x + w > innerWidth - 8) x = e.clientX - w - 14; if (y + h > innerHeight - 8) y = e.clientY - h - 14; tip.style.left = x + "px"; tip.style.top = y + "px"; }
  function hideTip() { tip.classList.remove("on"); }
  function bindTips(root) {
    root.querySelectorAll("[data-tip]").forEach(function (el) {
      el.addEventListener("mousemove", function (e) { showTip(e, el.getAttribute("data-tip")); });
      el.addEventListener("mouseleave", hideTip);
      el.addEventListener("click", function (e) { showTip(e, el.getAttribute("data-tip")); });
    });
  }

  /* ------------------------------------------------------------------ charts */
  function ticks(lo, hi, n) {
    var span = hi - lo, step = Math.pow(10, Math.floor(Math.log10(span / n))), err = span / n / step;
    step *= err >= 7.5 ? 10 : err >= 3.5 ? 5 : err >= 1.5 ? 2 : 1;
    var out = []; for (var v = Math.ceil(lo / step) * step; v <= hi + 1e-9; v += step) out.push(+v.toFixed(6)); return out;
  }
  /* series: [{name, color, dash, values:[y...]}], x labels = months */
  function lineChart(series, opt) {
    var W = opt.w || 640, H = opt.h || 240, L = 48, R = 14, T = 12, B = 26, xs = opt.x;
    var all = []; series.forEach(function (s) { s.values.forEach(function (v) { if (v !== null) all.push(v); }); });
    var lo = Math.min.apply(null, all), hi = Math.max.apply(null, all), pad = (hi - lo) * 0.08 || 1;
    if (opt.zero) { lo = Math.min(lo, 0); hi = Math.max(hi, 0); }
    lo -= pad; hi += pad;
    var X = function (i) { return L + i * (W - L - R) / (xs.length - 1); }, Y = function (v) { return T + (hi - v) / (hi - lo) * (H - T - B); };
    var s = '<svg class="chart" viewBox="0 0 ' + W + " " + H + '" role="img" aria-label="' + esc(opt.aria) + '">';
    ticks(lo, hi, 4).forEach(function (t) { s += '<line class="grid" x1="' + L + '" x2="' + (W - R) + '" y1="' + Y(t) + '" y2="' + Y(t) + '"/><text x="' + (L - 6) + '" y="' + (Y(t) + 4) + '" text-anchor="end">' + (opt.fmt ? opt.fmt(t) : t) + "</text>"; });
    if (opt.zero) s += '<line x1="' + L + '" x2="' + (W - R) + '" y1="' + Y(0) + '" y2="' + Y(0) + '" stroke="#BFAFA4"/>';
    xs.forEach(function (m, i) { if (i % (opt.every || 3) === 0) s += '<text x="' + X(i) + '" y="' + (H - 6) + '" text-anchor="middle">' + mlabel(m) + "</text>"; });
    series.forEach(function (se) {
      var d = "", len = 0, prev = null;
      se.values.forEach(function (v, i) { if (v === null) { prev = null; return; } var px = X(i), py = Y(v); d += (prev ? "L" : "M") + px.toFixed(1) + "," + py.toFixed(1); if (prev) len += Math.hypot(px - prev[0], py - prev[1]); prev = [px, py]; });
      s += '<path class="ln' + (se.dash ? " dash" : "") + '" d="' + d + '" stroke="' + se.color + '" stroke-width="' + (se.w || 2.2) + '" style="--len:' + Math.ceil(len) + '"/>';
    });
    var step = (W - L - R) / (xs.length - 1);
    xs.forEach(function (m, i) {
      var rows = series.filter(function (se) { return se.values[i] !== null; }).map(function (se) { return '<span style="color:' + se.color + '">●</span> ' + esc(se.name) + ": " + (opt.tipfmt ? opt.tipfmt(se.values[i], se, i) : se.values[i]); }).join("<br>");
      if (rows) s += '<rect class="hit" x="' + (X(i) - step / 2) + '" y="' + T + '" width="' + step + '" height="' + (H - T - B) + '" data-tip="' + esc("<b>" + mlong(m) + "</b>" + rows) + '"/>';
    });
    s += "</svg>";
    var leg = series.length > 1 ? '<div class="legend">' + series.map(function (se) { return '<span><i class="' + (se.dash ? "dash" : "") + '" style="background:' + se.color + '"></i>' + esc(se.name) + "</span>"; }).join("") + "</div>" : "";
    return s + leg;
  }
  function ribbon() {
    var W = 640, H = 340, L = 150, R = 150, T = 30, B = 20;
    var vals = []; summ.forEach(function (r) { vals.push(r.start, r.now); });
    var lo = Math.min.apply(null, vals) - 6, hi = Math.max.apply(null, vals) + 6;
    var Y = function (v) { return T + (hi - v) / (hi - lo) * (H - T - B); };
    var s = '<svg class="chart" viewBox="0 0 ' + W + " " + H + '" role="img" aria-label="Slope chart of share in basis points per vertical, Jul to Sep 2024 against Apr to Jun 2026">';
    s += '<text class="lab" x="' + L + '" y="16" text-anchor="middle">Jul–Sep 2024</text><text class="lab" x="' + (W - R) + '" y="16" text-anchor="middle">Apr–Jun 2026</text>';
    s += '<line x1="' + L + '" x2="' + L + '" y1="' + T + '" y2="' + (H - B) + '" stroke="#E4DAD1"/><line x1="' + (W - R) + '" x2="' + (W - R) + '" y1="' + T + '" y2="' + (H - B) + '" stroke="#E4DAD1"/>';
    var placedL = [], placedR = [];
    function slot(arr, y) { var yy = y; arr.forEach(function (p) { if (Math.abs(p - yy) < 13) yy = p + 13; }); arr.push(yy); return yy; }
    summ.slice().sort(function (a, b) { return b.now - a.now; }).forEach(function (r) {
      var c = COLORS[r.name], y1 = Y(r.start), y2 = Y(r.now), wv = r.status === "Gaining" ? 3.4 : 2;
      var t = "<b>" + esc(r.name) + "</b>Share " + r.start.toFixed(1) + " → " + r.now.toFixed(1) + " bps<br>Change " + sgn(r.change, 1, " bps") + " · " + r.status;
      s += '<g data-tip="' + esc(t) + '"><line x1="' + L + '" y1="' + y1 + '" x2="' + (W - R) + '" y2="' + y2 + '" stroke="' + c + '" stroke-width="' + wv + '"' + (r.status === "Losing" ? ' stroke-dasharray="6 4"' : "") + ' stroke-linecap="round"/>';
      s += '<line x1="' + L + '" y1="' + y1 + '" x2="' + (W - R) + '" y2="' + y2 + '" stroke="transparent" stroke-width="14"/>';
      s += '<circle cx="' + L + '" cy="' + y1 + '" r="4.5" fill="' + c + '"/><circle cx="' + (W - R) + '" cy="' + y2 + '" r="5" fill="' + c + '"/></g>';
      var ly = slot(placedR, y2), ry = slot(placedL, y1);
      s += '<text class="lab" x="' + (W - R + 10) + '" y="' + (ly + 4) + '" style="fill:' + c + '">' + esc(SHORT[r.name]) + " " + r.now.toFixed(0) + "</text>";
      s += '<text x="' + (L - 10) + '" y="' + (ry + 4) + '" text-anchor="end">' + esc(SHORT[r.name]) + " " + r.start.toFixed(0) + "</text>";
    });
    return s + "</svg>";
  }
  function gapBars() {
    var rows = summ.slice().sort(function (a, b) { return b.gap - a.gap; });
    var W = 640, rh = 40, H = rows.length * rh + 34, L = 100, R = 40, mid = L + (W - L - R) / 2, sc = (W - L - R) / 2 / 9;
    var s = '<svg class="chart" viewBox="0 0 ' + W + " " + H + '" role="img" aria-label="Diverging bars of growth gap in percentage points by vertical">';
    [-8, -4, 0, 4, 8].forEach(function (t) { s += '<line class="grid" x1="' + (mid + t * sc) + '" x2="' + (mid + t * sc) + '" y1="6" y2="' + (H - 24) + '"/><text x="' + (mid + t * sc) + '" y="' + (H - 8) + '" text-anchor="middle">' + (t > 0 ? "+" : "") + t + "</text>"; });
    s += '<line x1="' + mid + '" x2="' + mid + '" y1="4" y2="' + (H - 22) + '" stroke="#BFAFA4"/>';
    rows.forEach(function (r, i) {
      var y = 10 + i * rh, w = Math.abs(r.gap) * sc, x = r.gap >= 0 ? mid : mid - w, c = r.gap >= 0 ? "#1D7A46" : "#B3261E";
      var t = "<b>" + esc(r.name) + "</b>Book YoY " + sgn(r.byoy, 2, "%") + "<br>Market YoY " + sgn(r.myoy, 2, "%") + "<br>Gap " + sgn(r.gap, 2, " pp");
      s += '<g data-tip="' + esc(t) + '"><rect x="' + x.toFixed(1) + '" y="' + y + '" width="' + w.toFixed(1) + '" height="24" rx="4" fill="' + c + '"/>';
      s += '<rect x="' + L + '" y="' + (y - 6) + '" width="' + (W - L - R) + '" height="36" fill="transparent"/></g>';
      s += '<text class="lab" x="' + (L - 10) + '" y="' + (y + 16) + '" text-anchor="end">' + esc(SHORT[r.name]) + "</text>";
      s += '<text class="lab" x="' + (r.gap >= 0 ? x + w + 6 : x - 6) + '" y="' + (y + 16) + '" text-anchor="' + (r.gap >= 0 ? "start" : "end") + '">' + sgn(r.gap, 1) + "</text>";
    });
    return s + '</svg><div class="legend"><span><i style="background:#1D7A46"></i>Outgrowing the market</span><span><i style="background:#B3261E"></i>Lagging the market</span></div>';
  }
  function spark(vals, color) {
    var w = 78, h = 26, lo = Math.min.apply(null, vals), hi = Math.max.apply(null, vals), rg = hi - lo || 1;
    var pts = vals.map(function (v, i) { return (i * w / (vals.length - 1)).toFixed(1) + "," + (h - 2 - (v - lo) / rg * (h - 4)).toFixed(1); }).join(" ");
    return '<svg width="' + w + '" height="' + h + '" viewBox="0 0 ' + w + " " + h + '" aria-hidden="true"><polyline fill="none" stroke="' + color + '" stroke-width="1.8" stroke-linejoin="round" points="' + pts + '"/></svg>';
  }
  function counter(el) {
    var to = +el.getAttribute("data-to"), d = +(el.getAttribute("data-d") || 0), t0 = performance.now();
    if (matchMedia("(prefers-reduced-motion: reduce)").matches) { el.textContent = to.toFixed(d); return; }
    (function f(t) { var p = Math.min(1, (t - t0) / 700); el.textContent = (to * (1 - Math.pow(1 - p, 3))).toFixed(d); if (p < 1) requestAnimationFrame(f); })(t0);
  }
  function head(eb, title, sub, cap) {
    return '<div class="h"><div><p class="eb">' + esc(eb) + "</p><h1>" + esc(title) + "</h1><p>" + esc(sub) + '</p></div><span class="cap">Sample data · ' + esc(cap) + "</span></div>";
  }

  /* ------------------------------------------------------------------ screens */
  function overview() {
    var n3 = avg(port.slice(-3).map(function (p) { return p.bps; })), s3 = avg(port.slice(0, 3).map(function (p) { return p.bps; }));
    var now = port[port.length - 1], yr = port[port.length - 13], yoy = now.vol / yr.vol - 1;
    var gaining = summ.filter(function (r) { return r.status === "Gaining"; }).length;
    var wide = summ.slice().sort(function (a, b) { return Math.abs(b.gap) - Math.abs(a.gap); })[0];
    var top = summ[0], bot = summ[summ.length - 1], m = Math.max.apply(null, summ.map(function (r) { return Math.abs(r.change); }));
    var h = head("Overview", "Where are we winning share?", "Our processed volume by merchant vertical against market retail sales, as share in basis points (100 bps = 1%).", "MARKET_SHARE_VERTICAL_SUMMARY view");
    h += '<div class="kpis">' +
      '<div class="kpi"><div class="k">Book share of market</div><div class="v"><span data-to="' + n3.toFixed(1) + '" data-d="1">0</span><small>bps</small></div><div class="d">' + arrow(n3 - s3, sgn(n3 - s3, 1, " bps") + " vs Jul–Sep 2024") + "</div>" + spark(port.map(function (p) { return p.bps; }), "#B0287F") + "</div>" +
      '<div class="kpi"><div class="k">Processed · ' + mlabel(now.month).replace(" ", " 20") + '</div><div class="v">' + usd(now.vol) + '</div><div class="d">' + arrow(yoy, sgn(yoy * 100, 1, "%") + " year over year") + "</div>" + spark(port.map(function (p) { return p.vol; }), "#5B6B7A") + "</div>" +
      '<div class="kpi"><div class="k">Verticals gaining share</div><div class="v"><span data-to="' + gaining + '">0</span><small>of ' + summ.length + '</small></div><div class="d">' + summ.filter(function (r) { return r.status === "Holding"; }).length + " holding · " + summ.filter(function (r) { return r.status === "Losing"; }).length + " losing</div></div>" +
      '<div class="kpi"><div class="k">Widest growth gap</div><div class="v">' + sgn(wide.gap, 1) + '<small>pp</small></div><div class="d">' + esc(SHORT[wide.name]) + ": book " + sgn(wide.byoy, 1, "%") + " vs market " + sgn(wide.myoy, 1, "%") + "</div></div></div>";
    h += '<div class="insight"><b>' + esc(top.name) + "</b> added the most share (" + sgn(top.change, 1, " bps") + ", growing " + sgn(top.byoy, 1, "%") + " against a market at " + sgn(top.myoy, 1, "%") + "). <b>" + esc(bot.name) + "</b> gave back " + Math.abs(bot.change).toFixed(1) + " bps: our book fell " + Math.abs(bot.byoy).toFixed(1) + "% while the market grew " + sgn(bot.myoy, 1, "%") + ".</div>";
    h += '<div class="grid2"><section class="card"><h2>Share ribbon</h2><p class="sub">Share of each vertical\'s market, first quarter of the window vs the latest (3-month averages). Thick = gaining, dashed = losing. Hover a line for figures.</p>' + ribbon() + "</section>";
    h += '<section class="card"><h2>Gainers and losers</h2><p class="sub">Change in share, bps, Jul–Sep 2024 to Apr–Jun 2026</p><ul class="rank">' + summ.map(function (r) {
      var w = Math.abs(r.change) / m * 50, left = r.change >= 0 ? 50 : 50 - w;
      return '<li><span class="nm">' + esc(r.name) + " " + pill(r.status) + '</span><span class="n ' + (r.change >= 0 ? "up" : "down") + '">' + sgn(r.change, 1) + '</span><span class="bar"><b></b><i style="left:' + left.toFixed(1) + "%;width:" + w.toFixed(1) + "%;background:" + (r.change >= 0 ? "#1D7A46" : "#B3261E") + '"></i></span></li>';
    }).join("") + '</ul><p class="sub" style="margin-top:.7rem">Gaining at +3% share change or more, losing at −3% or less. Latest month ' + mlong(summ[0].latest) + ".</p></section></div>";
    h += '<section class="card"><h2>Book share of market, monthly</h2><p class="sub">All six verticals combined</p>' + lineChart([{name: "Book share", color: "#B0287F", values: port.map(function (p) { return +p.bps.toFixed(2); })}], {x: months, w: 1100, h: 230, aria: "Line chart of total book share in basis points by month", tipfmt: function (v) { return v.toFixed(1) + " bps"; }}) + "</section>";
    main.innerHTML = h;
    main.querySelectorAll("[data-to]").forEach(counter);
  }

  var vState = {sort: "change", dir: -1, status: {Gaining: true, Holding: true, Losing: true}, q: ""};
  var COLS = [["name", "Vertical"], ["status", "Status"], ["now", "Share now (bps)"], ["change", "Change (bps)"], ["vol", "Processed, latest"], ["mkt", "Market, latest"], ["byoy", "Book YoY"], ["myoy", "Market YoY"], ["gap", "Growth gap"]];
  function verticals() {
    var h = head("Verticals", "Share by merchant vertical", "Sort and filter the verticals, then select a row to open its share history, growth and monthly figures.", "MARKET_SHARE_BENCHMARK view");
    h += '<div class="tools" role="group" aria-label="Filter by status">' + ["Gaining", "Holding", "Losing"].map(function (s) { return '<button type="button" class="chip" data-st="' + s + '" aria-pressed="' + vState.status[s] + '">' + s + "</button>"; }).join("") +
      '<input class="search" type="search" placeholder="Search verticals, e.g. grocery" aria-label="Search verticals" value="' + esc(vState.q) + '"></div><div id="vt"></div>' +
      '<p class="sub" style="margin-top:.6rem">Share now is the Apr–Jun 2026 average; change is against Jul–Sep 2024. Select a column header to sort.</p>';
    main.innerHTML = h;
    main.querySelectorAll("[data-st]").forEach(function (b) { b.onclick = function () { vState.status[b.dataset.st] = !vState.status[b.dataset.st]; b.setAttribute("aria-pressed", vState.status[b.dataset.st]); table(); }; });
    $(".search", main).oninput = function (e) { vState.q = e.target.value; table(); };
    table();
  }
  function table() {
    var rows = summ.filter(function (r) { return vState.status[r.status] && (!vState.q || r.name.toLowerCase().indexOf(vState.q.toLowerCase()) >= 0 || SHORT[r.name].toLowerCase().indexOf(vState.q.toLowerCase()) >= 0); });
    rows.sort(function (a, b) { var x = a[vState.sort], y = b[vState.sort]; return (x < y ? -1 : x > y ? 1 : 0) * vState.dir; });
    var el = $("#vt");
    if (!rows.length) { el.innerHTML = '<div class="card empty"><b>No verticals match</b>Clear the search or turn a status filter back on.</div>'; return; }
    var h = '<div class="tw"><table><thead><tr>' + COLS.map(function (c) { var s = vState.sort === c[0] ? (vState.dir > 0 ? "ascending" : "descending") : "none"; return '<th aria-sort="' + s + '"><button type="button" data-k="' + c[0] + '">' + c[1] + "</button></th>"; }).join("") + "</tr></thead><tbody>";
    rows.forEach(function (r) {
      h += '<tr tabindex="0" data-c="' + r.code + '"><td><b>' + esc(r.name) + "</b></td><td>" + pill(r.status) + "</td><td>" + r.now.toFixed(1) + '<span class="sbar"><i style="width:' + (r.now / 260 * 100).toFixed(0) + '%"></i></span></td><td class="' + (r.change >= 0 ? "up" : "down") + '">' + sgn(r.change, 1) + "</td><td>" + usd(r.vol) + "</td><td>" + usd(r.mkt) + "</td><td>" + sgn(r.byoy, 1, "%") + "</td><td>" + sgn(r.myoy, 1, "%") + '</td><td class="' + (r.gap >= 0 ? "up" : "down") + '">' + sgn(r.gap, 1, " pp") + "</td></tr>";
    });
    el.innerHTML = h + "</tbody></table></div>";
    el.querySelectorAll("th button").forEach(function (b) { b.onclick = function () { var k = b.dataset.k; if (vState.sort === k) vState.dir *= -1; else { vState.sort = k; vState.dir = k === "name" || k === "status" ? 1 : -1; } table(); }; });
    el.querySelectorAll("tbody tr").forEach(function (tr) { tr.onclick = function () { openDrawer(tr.dataset.c); }; tr.onkeydown = function (e) { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); openDrawer(tr.dataset.c); } }; });
  }
  function openDrawer(code) {
    var r = summ.filter(function (x) { return x.code === code; })[0], g = bench[code], c = COLORS[r.name];
    var h = '<button class="x" type="button" aria-label="Close">Close ✕</button><p class="sub" style="margin:0">Vertical</p><h2 id="dwh">' + esc(r.name) + " " + pill(r.status) + "</h2>" +
      '<p class="sub">Share ' + r.start.toFixed(1) + " → " + r.now.toFixed(1) + " bps (" + sgn(r.change, 1, " bps") + ", " + sgn(r.pct, 1, "%") + ") · latest growth gap " + sgn(r.gap, 1, " pp") + " · " + r.merchants + " active merchants</p>" +
      '<section class="card"><h2>Share of market, monthly</h2>' + lineChart([{name: "Share", color: c, values: g.map(function (x) { return x.bps; })}], {x: months, h: 200, aria: "Share in basis points by month for " + r.name, tipfmt: function (v) { return v.toFixed(2) + " bps"; }}) + "</section>" +
      '<section class="card"><h2>Our volume vs the market, indexed</h2><p class="sub">Jul 2024 = 100</p>' + lineChart([
        {name: "Our processed volume", color: c, values: g.map(function (x) { return +(x.vol / g[0].vol * 100).toFixed(2); })},
        {name: "Market retail sales", color: "#5B6B7A", dash: true, values: g.map(function (x) { return +(x.mkt / g[0].mkt * 100).toFixed(2); })}],
        {x: months, h: 200, aria: "Indexed growth of processed volume and market sales for " + r.name, tipfmt: function (v, se, i) { return v.toFixed(1) + " (" + usd(se.name.indexOf("Market") === 0 ? g[i].mkt : g[i].vol) + ")"; }}) + "</section>" +
      '<section class="card"><h2>Monthly figures</h2><div class="tw"><table><thead><tr><th>Month</th><th>Processed</th><th>Market</th><th>Share (bps)</th><th>Book YoY</th><th>Market YoY</th><th>Gap</th></tr></thead><tbody>' +
      g.slice().reverse().map(function (x) { return "<tr><td>" + mlong(x.month) + "</td><td>" + usd(x.vol) + "</td><td>" + usd(x.mkt) + "</td><td>" + x.bps.toFixed(2) + "</td><td>" + (x.byoy === null ? "n/d" : sgn(x.byoy, 2, "%")) + "</td><td>" + (x.myoy === null ? "n/d" : sgn(x.myoy, 2, "%")) + "</td><td>" + (x.gap === null ? "n/d" : sgn(x.gap, 2, " pp")) + "</td></tr>"; }).join("") + "</tbody></table></div></section>";
    var dw = $("#drawer"); dw.innerHTML = h; dw.classList.add("on"); $("#scrim").classList.add("on"); dw.setAttribute("aria-hidden", "false");
    bindTips(dw); $(".x", dw).onclick = closeDrawer; $(".x", dw).focus();
    main.querySelectorAll("tbody tr").forEach(function (tr) { tr.classList.toggle("sel", tr.dataset.c === code); });
  }
  function closeDrawer() { var dw = $("#drawer"); dw.classList.remove("on"); $("#scrim").classList.remove("on"); dw.setAttribute("aria-hidden", "true"); hideTip(); }

  function growth() {
    var latest = summ[0].latest;
    function names(f) { var n = summ.filter(f).map(function (r) { return SHORT[r.name]; }); return n.length ? n.join(", ") : "None"; }
    var h = head("Growth gap", "Are we growing faster than the market?", "Year-over-year growth of our processed volume minus the market's, in percentage points. Positive means we take share.", "growth_gap_pp in MARKET_SHARE_BENCHMARK");
    h += '<div class="grid2"><section class="card"><h2>Growth gap by vertical</h2><p class="sub">' + mlong(latest) + " vs the same month a year earlier</p>" + gapBars() + "</section>";
    h += '<section class="card"><h2>Read-out</h2><p class="sub">Where each vertical sits, from our growth and the market\'s</p><div class="quad">' +
      '<div><h3 class="up">Outgrowing a growing market</h3><p>' + names(function (r) { return r.byoy > 0 && r.myoy > 0.5 && r.gap > 0; }) + "</p></div>" +
      '<div><h3 class="flat">Growing, but slower than the market</h3><p>' + names(function (r) { return r.byoy > 0 && r.gap <= 0; }) + "</p></div>" +
      '<div><h3 class="up">Growing in a flat or shrinking market</h3><p>' + names(function (r) { return r.byoy > 0 && r.myoy <= 0.5 && r.gap > 0; }) + "</p></div>" +
      '<div><h3 class="down">Shrinking while the market grows</h3><p>' + names(function (r) { return r.byoy <= 0 && r.myoy > 0; }) + "</p></div></div></section></div>";
    var ms = months.slice(12);
    h += '<section class="card"><h2>Growth gap over time</h2><p class="sub">Monthly, from July 2025 (the first month with a year-earlier comparison). Hover for each month.</p>' +
      lineChart(summ.map(function (r) { return {name: r.name, color: COLORS[r.name], values: bench[r.code].slice(12).map(function (x) { return x.gap; })}; }),
        {x: ms, w: 1100, h: 300, zero: true, every: 1, aria: "Growth gap in percentage points by month for each vertical", fmt: function (t) { return (t > 0 ? "+" : "") + t; }, tipfmt: function (v) { return sgn(v, 2, " pp"); }}) + "</section>";
    main.innerHTML = h;
  }

  /* ------------------------------------------------------------------ AI (replayed) */
  function md(text) {
    var lines = text.split("\n"), out = "", list = null, i = 0;
    function inline(s) { return esc(s).replace(/\*\*(.+?)\*\*/g, "<b>$1</b>").replace(/`([^`]+)`/g, "<code>$1</code>").replace(/(^|[\s(])_(.+?)_(?=[\s).,]|$)/g, "$1<i>$2</i>"); }
    function close() { if (list) { out += "</" + list + ">"; list = null; } }
    while (i < lines.length) {
      var l = lines[i];
      if (/^\s*\|/.test(l)) {
        close(); var rows = []; while (i < lines.length && /^\s*\|/.test(lines[i])) { rows.push(lines[i]); i++; }
        var cells = rows.filter(function (r) { return !/^\s*\|[\s:|-]+\|\s*$/.test(r); }).map(function (r) { return r.trim().replace(/^\||\|$/g, "").split("|").map(function (c) { return c.trim(); }); });
        out += '<div class="tw"><table><thead><tr>' + cells[0].map(function (c) { return "<th>" + inline(c) + "</th>"; }).join("") + "</tr></thead><tbody>" + cells.slice(1).map(function (r) { return "<tr>" + r.map(function (c) { return "<td>" + inline(c) + "</td>"; }).join("") + "</tr>"; }).join("") + "</tbody></table></div>";
        continue;
      }
      var m;
      if ((m = /^(#{1,3})\s+(.*)/.exec(l))) { close(); out += "<h" + m[1].length + ">" + inline(m[2]) + "</h" + m[1].length + ">"; }
      else if ((m = /^\s*[-*•]\s+(.*)/.exec(l))) { if (list !== "ul") { close(); out += "<ul>"; list = "ul"; } out += "<li>" + inline(m[1]) + "</li>"; }
      else if ((m = /^\s*\d+\.\s+(.*)/.exec(l))) { if (list !== "ol") { close(); out += "<ol>"; list = "ol"; } out += "<li>" + inline(m[1]) + "</li>"; }
      else if (l.trim()) { close(); out += "<p>" + inline(l) + "</p>"; }
      else close();
      i++;
    }
    close(); return out;
  }
  async function stream(el, text) {
    if (matchMedia("(prefers-reduced-motion: reduce)").matches) { el.innerHTML = md(text); return; }
    el.classList.add("caret");
    for (var i = 60; i < text.length + 60; i += 60) { el.innerHTML = md(text.slice(0, i)); await wait(24); }
    el.classList.remove("caret"); el.innerHTML = md(text);
  }
  async function staged(el, steps) {
    var total = 4000 + Math.random() * 4000;
    for (var i = 0; i <= steps.length; i++) {
      el.innerHTML = '<ul class="steps">' + steps.map(function (s, j) { return '<li class="' + (j < i ? "done" : j === i ? "now" : "") + '"><span class="ic"></span><span>' + esc(s) + "</span></li>"; }).join("") + "</ul>";
      if (i < steps.length) await wait(total / steps.length);
    }
  }
  function noteSteps(scope) {
    var n = scope === "ALL" ? "6 verticals" : "1 vertical";
    return ["Building the fact pack: " + n + " from MARKET_SHARE_VERTICAL_SUMMARY (Jul 2024 to Jun 2026)", "Drafting the note with AI_COMPLETE (claude-sonnet-4-5) under the data rules",
      "Fact-checking every figure against the fact pack with a second AI_COMPLETE pass", "Saving the note and verdict to MARKET_SHARE_REPORTS"];
  }
  function noteBody(n) {
    var fp = n.fact_pack || {verticals: []};
    var src = '<div class="src">Sources: fact pack from <code>' + esc(fp.source || "") + "</code>, " + esc(fp.window || "") + '. These are the only figures the model may use.</div><div class="tw" style="margin-top:.5rem"><table><thead><tr><th>Vertical</th><th>Share start</th><th>Share now</th><th>Change</th><th>Growth gap</th><th>Status</th></tr></thead><tbody>' +
      fp.verticals.map(function (v) { return "<tr><td>" + esc(v.vertical) + "</td><td>" + esc(v.share_start_display) + "</td><td>" + esc(v.share_now_display) + "</td><td>" + esc(v.share_change_display) + "</td><td>" + esc(v.growth_gap_display) + "</td><td>" + pill(v.status) + "</td></tr>"; }).join("") + "</tbody></table></div>";
    var flags = (n.edits || []).length ? '<div class="flag"><b>Verifier flagged:</b><ul>' + n.edits.map(function (e) { return "<li>" + esc(e) + "</li>"; }).join("") + "</ul></div>"
      : '<p class="sub" style="margin-top:.6rem">Verifier: every figure matches the fact pack; ' + (n.residual_hedges || 0) + " hedge words.</p>";
    return {flags: flags, src: src};
  }
  var lastNote = null;
  function notes() {
    var h = head("Share notes", "A share note you can defend", "AI_COMPLETE drafts a one-page note from a fact pack under strict data rules; a second AI_COMPLETE pass checks every figure and marks it Verified or Needs review.", "Cortex AI_COMPLETE · draft + verifier");
    h += '<section class="card"><div class="row"><label>Scope<select id="scope">' + SCOPES.map(function (s) { return '<option value="' + s[0] + '">' + esc(s[1]) + "</option>"; }).join("") + '</select></label><button class="btn primary" id="go" type="button">Write share note</button></div><div id="prog"></div><div id="out"><div class="empty"><b>No note yet</b>Pick the whole book or one vertical and write a note. This example replays a response captured from a Live run.</div></div></section>';
    h += '<h2 style="font-size:1rem;margin:1.3rem 0 .2rem">Saved notes</h2><p class="sub">Sample gallery: notes captured from Live runs, labeled as sample AI responses. One came back Needs review: the verifier caught a claim the facts don\'t support.</p><div class="gallery">' +
      SCOPES.map(function (s) { var n = D.ai.notes[s[0]]; if (!n) return ""; var t = (n.markdown.split("\n")[0] || "").replace(/^#\s*/, ""); return '<article class="card" tabindex="0" role="button" data-s="' + s[0] + '">' + verdict(n.status) + "<h3>" + esc(t) + '</h3><p class="sub" style="margin:0">' + esc(s[1]) + " · " + (n.edits || []).length + " flagged · " + (n.latency_ms / 1000).toFixed(1) + " s live</p></article>"; }).join("") + "</div>";
    main.innerHTML = h;
    $("#go").onclick = function () { run($("#scope").value, true); };
    main.querySelectorAll(".gallery .card").forEach(function (c) { var f = function () { $("#scope").value = c.dataset.s; run(c.dataset.s, false); $("#out").scrollIntoView({behavior: "smooth", block: "start"}); }; c.onclick = f; c.onkeydown = function (e) { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); f(); } }; });
    if (lastNote) run(lastNote, false);
  }
  async function run(scope, animate) {
    var n = D.ai.notes[scope], out = $("#out"), prog = $("#prog"), go = $("#go");
    if (!n) { out.innerHTML = '<div class="empty"><b>No captured sample</b>Run this scope in Live mode.</div>'; return; }
    lastNote = scope;
    if (animate) { go.disabled = true; out.innerHTML = ""; await staged(prog, noteSteps(scope)); go.disabled = false; } else prog.innerHTML = "";
    var b = noteBody(n);
    out.innerHTML = '<div class="meta"><span class="label">Sample AI response</span>' + verdict(n.status) + "<span>" + esc(n.model) + " · " + (n.latency_ms / 1000).toFixed(1) + ' s measured live</span></div><div class="md" id="md"></div><div id="after"></div>';
    if (animate) await stream($("#md"), n.markdown); else $("#md").innerHTML = md(n.markdown);
    $("#after").innerHTML = b.flags + b.src;
  }

  var ASK_STEPS = ["Sending the question to the Market Share Agent (DATA_AGENT_RUN)", "Cortex Analyst writes SQL over the MARKET_SHARE_SV semantic view",
    "Running the SQL on SNOWPACK_MARKET_SHARE_WH", "Composing the answer from the result set"];
  var lastQ = null;
  function ask() {
    var qs = Object.keys(D.ai.ask);
    var h = head("Ask an analyst", "Ask the benchmark in plain English", "The Market Share Agent uses Cortex Analyst over the MARKET_SHARE_SV semantic view: it writes SQL, runs it and answers from the result.", "Cortex Agent · Cortex Analyst · semantic view");
    h += '<section class="card"><p class="sub">Suggested questions. This example answers them with responses captured from Live runs; in Live mode you can ask your own.</p><div class="qs">' +
      qs.map(function (q, i) { return '<button type="button" class="chip" data-q="' + i + '" aria-pressed="false">' + esc(q) + "</button>"; }).join("") + '</div><div id="aprog"></div><div id="aout"><div class="empty"><b>Pick a question</b>The answer shows the SQL Cortex Analyst wrote and the rows it returned.</div></div></section>';
    main.innerHTML = h;
    main.querySelectorAll("[data-q]").forEach(function (b) { b.onclick = function () { answer(qs[+b.dataset.q], true); }; });
    if (lastQ) answer(lastQ, false);
  }
  async function answer(q, animate) {
    var a = D.ai.ask[q], out = $("#aout"), busy = main.querySelectorAll("[data-q]");
    lastQ = q;
    busy.forEach(function (b) { b.setAttribute("aria-pressed", b.textContent === q); });
    if (animate) { busy.forEach(function (b) { b.disabled = true; }); out.innerHTML = ""; await staged($("#aprog"), ASK_STEPS); busy.forEach(function (b) { b.disabled = false; }); } else $("#aprog").innerHTML = "";
    var t = a.table, tbl = t && t.rows && t.rows.length ? '<div class="src">Source: result set from Cortex Analyst over <code>MARKET_SHARE_SV</code></div><div class="tw" style="margin-top:.5rem"><table><thead><tr>' + t.columns.map(function (c) { return "<th>" + esc(c) + "</th>"; }).join("") + "</tr></thead><tbody>" + t.rows.map(function (r) { return "<tr>" + r.map(function (c) { return "<td>" + esc(c === null ? "" : c) + "</td>"; }).join("") + "</tr>"; }).join("") + "</tbody></table></div>" : "";
    out.innerHTML = '<div class="meta"><span class="label">Sample AI response</span><span>' + (a.latency_ms / 1000).toFixed(1) + ' s measured live</span></div><h2 style="font-size:1rem;margin:.2rem 0">' + esc(q) + '</h2><div class="md" id="amd"></div><div id="aafter"></div>';
    if (animate) await stream($("#amd"), a.text); else $("#amd").innerHTML = md(a.text);
    $("#aafter").innerHTML = tbl + (a.sql ? "<details><summary>SQL generated by Cortex Analyst</summary><pre>" + esc(a.sql) + "</pre></details>" : "");
  }

  /* ------------------------------------------------------------------ router */
  var VIEWS = {overview: overview, verticals: verticals, growth: growth, notes: notes, ask: ask};
  function route() {
    var v = (location.hash || "#overview").slice(1); if (!VIEWS[v]) v = "overview";
    document.querySelectorAll("#nav a").forEach(function (a) { var on = a.dataset.v === v; a.classList.toggle("on", on); if (on) a.setAttribute("aria-current", "page"); else a.removeAttribute("aria-current"); });
    closeDrawer(); hideTip();
    VIEWS[v](); bindTips(main); window.scrollTo(0, 0);
  }
  document.body.insertAdjacentHTML("beforeend", '<div class="scrim" id="scrim"></div><aside class="drawer" id="drawer" role="dialog" aria-modal="true" aria-labelledby="dwh" aria-hidden="true"></aside>');
  $("#scrim").onclick = closeDrawer;
  document.addEventListener("keydown", function (e) { if (e.key === "Escape") closeDrawer(); });
  document.addEventListener("scroll", hideTip, {passive: true});
  $("#liveBtn").onclick = function () { $("#liveDlg").showModal(); };
  window.addEventListener("hashchange", route);
  route();
})();
