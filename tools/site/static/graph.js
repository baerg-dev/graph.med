/* graph.med view page: one decision graph per chapter — patient group (diamond) → condition
   (hexagon) → recommendation (box, coloured by grade) → aim (tag) — laid out top-down by the
   build. Pan and pinch inside the viewport; tap a node for its details in the section below.
   No dependencies, no layout in the browser. Data: the #graph-data JSON from tools/build.py. */
(function () {
  "use strict";
  var data = JSON.parse(document.getElementById("graph-data").textContent);
  var svg = document.getElementById("graph"), sheet = document.getElementById("sheet");
  var hint = document.getElementById("hint"), nav = document.getElementById("chapters");
  var home = sheet.innerHTML, NS = "http://www.w3.org/2000/svg";
  var chapter = null, selected = null, nodes = {}, out = {}, inn = {}, groups = {}, paths = [];
  var view = { x: 0, y: 0, k: 1 }, world, anim = null;

  function el(name, attrs, parent) {
    var e = document.createElementNS(NS, name);
    for (var k in attrs) e.setAttribute(k, attrs[k]);
    if (parent) parent.appendChild(e);
    return e;
  }
  function shape(n, g) {   /* the node's form by type; size from the build */
    var w = n.w, h = n.h;
    if (n.type === "population") return el("polygon", { points: "0," + (-h / 2) + " " + (w / 2) + ",0 0," + (h / 2) + " " + (-w / 2) + ",0" }, g);
    if (n.type === "condition") { var q = w / 2 - 14; return el("polygon", { points: (-q) + "," + (-h / 2) + " " + q + "," + (-h / 2) + " " + (w / 2) + ",0 " + q + "," + (h / 2) + " " + (-q) + "," + (h / 2) + " " + (-w / 2) + ",0" }, g); }
    if (n.type === "outcome") return el("polygon", { points: (-w / 2) + "," + (-h / 2) + " " + (w / 2 - 12) + "," + (-h / 2) + " " + (w / 2) + ",0 " + (w / 2 - 12) + "," + (h / 2) + " " + (-w / 2) + "," + (h / 2) }, g);
    return el("rect", { x: -w / 2, y: -h / 2, width: w, height: h, rx: 8 }, g);
  }

  /* chapter chips */
  data.chapters.forEach(function (c, i) {
    var b = document.createElement("button");
    b.type = "button"; b.textContent = c.label + " · " + c.count; b.dataset.i = i;
    b.addEventListener("click", function () { show(i, true); });
    nav.appendChild(b);
  });

  function show(i, push) {
    chapter = data.chapters[i];
    Array.prototype.forEach.call(nav.children, function (b, j) { b.classList.toggle("on", j === i); });
    svg.textContent = ""; nodes = {}; out = {}; inn = {}; groups = {}; paths = [];
    world = el("g", {}, svg);
    var edges = el("g", { "class": "edges" }, world), boxes = el("g", { "class": "nodes" }, world);
    chapter.nodes.forEach(function (n) { nodes[n.id] = n; out[n.id] = []; inn[n.id] = []; });
    chapter.edges.forEach(function (e) {
      var a = nodes[e.from], b = nodes[e.to]; if (!a || !b) return;
      out[e.from].push(e.to); inn[e.to].push(e.from);
      var y0 = a.y + a.h / 2, y1 = b.y - b.h / 2, m = (y0 + y1) / 2;
      var p = el("path", { d: "M" + a.x + "," + y0 + " C" + a.x + "," + m + " " + b.x + "," + m + " " + b.x + "," + y1, "class": "edge " + e.kind }, edges);
      p.dataset.from = e.from; p.dataset.to = e.to; paths.push(p);
    });
    chapter.nodes.forEach(function (n) {
      var cls = "node " + n.type + (n.grade ? " g-" + n.grade : "") + (n.against ? " against" : "") + (n.contested ? " contested" : "");
      var g = el("g", { transform: "translate(" + n.x + "," + n.y + ")", "class": cls }, boxes);
      g.dataset.id = n.id;
      shape(n, g);
      var t = el("text", { "text-anchor": "middle", y: -((n.lines.length - 1) * 7) + 4 }, g);
      if (n.lang) t.setAttribute("lang", n.lang);
      n.lines.forEach(function (line, k) { var s = el("tspan", { x: 0, dy: k ? 14 : 0 }, t); s.textContent = line; });
      if (n.no) el("text", { "class": "no", x: -n.w / 2 + 6, y: -n.h / 2 + 11 }, g).textContent = n.no;
      groups[n.id] = g;
    });
    if (push) history.replaceState(null, "", "#chapter=" + chapter.chapter);
    select(null, false);
    fit(false);
  }

  /* selection: the node, its ancestors and descendants stay; the rest fades; the sheet fills */
  function reach(id, dir) { var seen = {}; (function go(x) { if (seen[x]) return; seen[x] = true; dir[x].forEach(go); })(id); return seen; }
  function select(id, push) {
    selected = id;
    var keep = null;
    if (id && nodes[id]) { keep = reach(id, out); var up = reach(id, inn); for (var k in up) keep[k] = true; }
    for (var nid in groups) {
      groups[nid].classList.toggle("dim", !!keep && !keep[nid]);
      groups[nid].classList.toggle("selected", nid === id);
    }
    paths.forEach(function (p) { p.classList.toggle("dim", !!keep && !(keep[p.dataset.from] && keep[p.dataset.to])); });
    if (keep) {
      sheet.innerHTML = data.html[nodes[id].ref] || ""; hint.hidden = true;
      if (push) history.replaceState(null, "", "#" + nodes[id].ref);
      sheet.scrollIntoView({ behavior: "smooth", block: "start" });
    } else {
      sheet.innerHTML = home; hint.hidden = false;
      if (push) history.replaceState(null, "", "#chapter=" + chapter.chapter);
    }
  }

  /* pan / zoom / fit */
  function apply() { world.setAttribute("transform", "translate(" + view.x + "," + view.y + ") scale(" + view.k + ")"); }
  function bounds(list) {
    var x0 = Infinity, y0 = Infinity, x1 = -Infinity, y1 = -Infinity;
    list.forEach(function (n) { x0 = Math.min(x0, n.x - n.w / 2); x1 = Math.max(x1, n.x + n.w / 2); y0 = Math.min(y0, n.y - n.h / 2); y1 = Math.max(y1, n.y + n.h / 2); });
    return { x0: x0, y0: y0, x1: x1, y1: y1 };
  }
  function fit(animated, list) {
    var r = svg.getBoundingClientRect(), b = bounds(list || chapter.nodes), pad = 24;
    var k = Math.min(2, (r.width - 2 * pad) / (b.x1 - b.x0), (r.height - 2 * pad) / (b.y1 - b.y0));
    var target = { k: k, x: (r.width - (b.x1 - b.x0) * k) / 2 - b.x0 * k, y: (r.height - (b.y1 - b.y0) * k) / 2 - b.y0 * k };
    if (animated) animate(target); else { view = target; apply(); }
  }
  function animate(target) {
    var from = { x: view.x, y: view.y, k: view.k }, t0 = performance.now();
    cancelAnimationFrame(anim);
    (function step(now) {
      var u = Math.min(1, (now - t0) / 260), e = 1 - Math.pow(1 - u, 3);
      view.x = from.x + (target.x - from.x) * e; view.y = from.y + (target.y - from.y) * e; view.k = from.k + (target.k - from.k) * e;
      apply(); if (u < 1) anim = requestAnimationFrame(step);
    })(t0);
  }
  var pointers = {}, pinch = null, press = null;
  function local(px, py) { var r = svg.getBoundingClientRect(); return { x: px - r.left, y: py - r.top }; }
  function zoomAt(f, cx, cy) {
    var k = Math.max(0.15, Math.min(4, view.k * f)); f = k / view.k;
    view.x = cx - (cx - view.x) * f; view.y = cy - (cy - view.y) * f; view.k = k; apply();
  }
  svg.addEventListener("pointerdown", function (e) {
    svg.setPointerCapture(e.pointerId); cancelAnimationFrame(anim);
    pointers[e.pointerId] = local(e.clientX, e.clientY);
    var ids = Object.keys(pointers);
    if (ids.length === 1) press = { id: e.pointerId, x: e.clientX, y: e.clientY, target: e.target };
    if (ids.length === 2) { press = null; var a = pointers[ids[0]], b = pointers[ids[1]]; pinch = { d: Math.hypot(a.x - b.x, a.y - b.y) }; }
  });
  svg.addEventListener("pointermove", function (e) {
    if (!(e.pointerId in pointers)) return;
    var p = local(e.clientX, e.clientY), prev = pointers[e.pointerId]; pointers[e.pointerId] = p;
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
    if (press && press.id === e.pointerId) {
      var g = press.target.closest && press.target.closest("g.node");
      if (g) { select(g.dataset.id, true); var n = nodes[g.dataset.id]; if (view.k < 0.8) fit(true, [n].concat(out[n.id].concat(inn[n.id]).map(function (i) { return nodes[i]; }))); }
      else select(null, true);
    }
    press = null;
  }
  svg.addEventListener("pointerup", up); svg.addEventListener("pointercancel", up);
  svg.addEventListener("wheel", function (e) { e.preventDefault(); var p = local(e.clientX, e.clientY); zoomAt(e.deltaY < 0 ? 1.15 : 1 / 1.15, p.x, p.y); }, { passive: false });
  document.getElementById("fit").addEventListener("click", function () { fit(true); });
  window.addEventListener("resize", function () { fit(false); });

  /* links in the sheet and deep links: #<entity id> or #chapter=<n> */
  function locate(ref) {
    for (var i = 0; i < data.chapters.length; i++) {
      var hit = data.chapters[i].nodes.filter(function (n) { return n.ref === ref; })[0];
      if (hit) return { i: i, id: hit.id };
    }
    return null;
  }
  function open(hash, push) {
    var m = /^chapter=(.+)$/.exec(hash);
    if (m) { var i = data.chapters.map(function (c) { return c.chapter; }).indexOf(m[1]); show(i < 0 ? 0 : i, push); return; }
    var at = locate(hash);
    if (!at) { show(0, push); return; }
    if (chapter !== data.chapters[at.i]) show(at.i, false);
    select(at.id, push);
    var n = nodes[at.id]; fit(true, [n].concat(out[n.id].concat(inn[n.id]).map(function (i) { return nodes[i]; })));
  }
  sheet.addEventListener("click", function (e) {
    var a = e.target.closest("a.node-link");
    if (a && locate(a.dataset.node)) { e.preventDefault(); open(a.dataset.node, true); window.scrollTo({ top: 0, behavior: "smooth" }); }
  });
  window.addEventListener("hashchange", function () { open(decodeURIComponent(location.hash.slice(1)), false); });
  open(decodeURIComponent(location.hash.slice(1)), false);
})();
