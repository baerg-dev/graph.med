/* graph.med view page: render precomputed nodes, pan/zoom by touch, tap a node → sheet below.
   No dependencies. Data: the #graph-data JSON written by tools/build.py. */
(function () {
  "use strict";
  var data = JSON.parse(document.getElementById("graph-data").textContent);
  var svg = document.getElementById("graph");
  var sheet = document.getElementById("sheet");
  var hint = document.getElementById("hint");
  var home = sheet.innerHTML;
  var NS = "http://www.w3.org/2000/svg";
  var byId = {}, adj = {};
  data.nodes.forEach(function (n) { byId[n.id] = n; adj[n.id] = []; });
  data.links.forEach(function (l) {
    if (byId[l.from] && byId[l.to]) { adj[l.from].push(l.to); adj[l.to].push(l.from); }
  });

  function el(name, attrs, parent) {
    var e = document.createElementNS(NS, name);
    for (var k in attrs) e.setAttribute(k, attrs[k]);
    if (parent) parent.appendChild(e);
    return e;
  }

  var world = el("g", { id: "world" }, svg);
  var edges = el("g", { "class": "edges" }, world);
  var nodes = el("g", { "class": "nodes" }, world);
  var lines = {};
  data.links.forEach(function (l, i) {
    var a = byId[l.from], b = byId[l.to];
    if (!a || !b) return;
    var isStmt = a.type === "statement" && b.type === "statement";
    lines[i] = el("line", { x1: a.x, y1: a.y, x2: b.x, y2: b.y, "class": isStmt ? "statement-edge" : "" }, edges);
    lines[i].dataset.from = l.from; lines[i].dataset.to = l.to;
  });
  var groups = {};
  data.nodes.forEach(function (n) {
    var g = el("g", { "class": n.type + (n.contested ? " contested" : ""), transform: "translate(" + n.x + "," + n.y + ")" }, nodes);
    g.dataset.id = n.id;
    var r = n.type === "statement" ? 9 : 5.5;
    el("circle", { r: 22, "class": "hit" }, g);              /* finger-sized hit area */
    el("circle", { r: r }, g);
    if (n.type === "concept") {
      var t = el("text", { x: r + 3, y: 4 }, g);
      t.setAttribute("lang", n.lang);
      t.textContent = n.label.length > 32 ? n.label.slice(0, 30) + "…" : n.label;
    }
    groups[n.id] = g;
  });

  /* pan / zoom: one pointer pans, two pinch, wheel zooms; a short still press is a tap */
  var view = { x: 0, y: 0, k: 1 };
  var pointers = {}, pinch = null, press = null;
  function apply() { world.setAttribute("transform", "translate(" + view.x + "," + view.y + ") scale(" + view.k + ")"); }
  function toSvg(px, py) {
    var r = svg.getBoundingClientRect(), vb = svg.viewBox.baseVal;
    var s = Math.min(r.width / vb.width, r.height / vb.height);
    var ox = (r.width - vb.width * s) / 2, oy = (r.height - vb.height * s) / 2;
    return { x: (px - r.left - ox) / s, y: (py - r.top - oy) / s };
  }
  function zoomAt(f, cx, cy) {
    var k = Math.max(0.4, Math.min(8, view.k * f)); f = k / view.k;
    view.x = cx - (cx - view.x) * f; view.y = cy - (cy - view.y) * f; view.k = k; apply();
  }
  svg.addEventListener("pointerdown", function (e) {
    svg.setPointerCapture(e.pointerId);
    pointers[e.pointerId] = toSvg(e.clientX, e.clientY);
    var ids = Object.keys(pointers);
    if (ids.length === 1) press = { id: e.pointerId, x: e.clientX, y: e.clientY, t: Date.now(), target: e.target.closest("g[data-id]") };
    if (ids.length === 2) { press = null; var a = pointers[ids[0]], b = pointers[ids[1]]; pinch = { d: Math.hypot(a.x - b.x, a.y - b.y) }; }
  });
  svg.addEventListener("pointermove", function (e) {
    if (!(e.pointerId in pointers)) return;
    var p = toSvg(e.clientX, e.clientY), prev = pointers[e.pointerId];
    pointers[e.pointerId] = p;
    var ids = Object.keys(pointers);
    if (ids.length === 1) {
      view.x += p.x - prev.x; view.y += p.y - prev.y; apply();
      if (press && Math.hypot(e.clientX - press.x, e.clientY - press.y) > 8) press = null;
    } else if (ids.length === 2 && pinch) {
      var a = pointers[ids[0]], b = pointers[ids[1]], d = Math.hypot(a.x - b.x, a.y - b.y);
      zoomAt(d / pinch.d, (a.x + b.x) / 2, (a.y + b.y) / 2); pinch.d = d;
    }
  });
  function up(e) {
    delete pointers[e.pointerId];
    if (Object.keys(pointers).length < 2) pinch = null;
    if (press && press.id === e.pointerId && Date.now() - press.t < 500) {
      if (press.target) select(press.target.dataset.id, true); else select(null, true);
    }
    press = null;
  }
  svg.addEventListener("pointerup", up);
  svg.addEventListener("pointercancel", up);
  svg.addEventListener("wheel", function (e) { e.preventDefault(); var p = toSvg(e.clientX, e.clientY); zoomAt(e.deltaY < 0 ? 1.15 : 1 / 1.15, p.x, p.y); }, { passive: false });

  /* selection → the sheet below the graph */
  function select(id, push) {
    Object.keys(groups).forEach(function (k) { groups[k].classList.remove("selected", "near", "dim"); });
    Object.keys(lines).forEach(function (k) { lines[k].classList.remove("dim"); });
    if (!id || !byId[id]) {
      sheet.innerHTML = home; hint.hidden = false;
      if (push) history.replaceState(null, "", location.pathname);
      return;
    }
    var near = {}; adj[id].forEach(function (n) { near[n] = true; });
    Object.keys(groups).forEach(function (k) {
      if (k === id) groups[k].classList.add("selected");
      else if (near[k]) groups[k].classList.add("near");
      else groups[k].classList.add("dim");
    });
    Object.keys(lines).forEach(function (k) {
      var l = lines[k]; if (l.dataset.from !== id && l.dataset.to !== id) l.classList.add("dim");
    });
    sheet.innerHTML = byId[id].html;
    hint.hidden = true;
    if (push) history.replaceState(null, "", "#" + id);
    sheet.scrollIntoView({ behavior: "smooth", block: "start" });
  }
  sheet.addEventListener("click", function (e) {
    var a = e.target.closest("a.node-link");
    if (a && byId[a.dataset.node]) { e.preventDefault(); select(a.dataset.node, true); }
  });
  window.addEventListener("hashchange", function () { select(decodeURIComponent(location.hash.slice(1)), false); });
  if (location.hash.length > 1) select(decodeURIComponent(location.hash.slice(1)), false);
})();
