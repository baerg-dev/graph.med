/* graph.med view page: an outline tree — source → chapters → statements → concepts — expanded
   step by step; pan and pinch inside the viewport; tap a shape to open it, a label for the sheet.
   Layout is the outline order: row = y, depth = x. No dependencies, no simulation.
   Data: the #graph-data JSON written by tools/build.py. */
(function () {
  "use strict";
  var data = JSON.parse(document.getElementById("graph-data").textContent);
  var svg = document.getElementById("graph"), sheet = document.getElementById("sheet");
  var hint = document.getElementById("hint"), home = sheet.innerHTML;
  var NS = "http://www.w3.org/2000/svg";
  var ROW = 30, INDENT = 26, PAD = 14;
  var nodes = data.nodes;

  /* the outline as instances: one per occurrence (a concept may sit under several statements) */
  var instances = [], byId = {};
  function walk(item, depth, parent, slot) {
    var inst = { key: instances.length, id: item.id, depth: depth, parent: parent, slot: slot || null,
                 children: [], open: false, node: nodes[item.id] };
    instances.push(inst); (byId[item.id] = byId[item.id] || []).push(inst);
    (item.children || []).forEach(function (c) { inst.children.push(walk(c, depth + 1, inst, c.slot)); });
    return inst;
  }
  var roots = data.tree.map(function (r) { return walk(r, 0, null); });
  roots.forEach(function (r) { r.open = true; });          /* start: the source and its chapters */

  function el(name, attrs, parent) {
    var e = document.createElementNS(NS, name);
    for (var k in attrs) e.setAttribute(k, attrs[k]);
    if (parent) parent.appendChild(e);
    return e;
  }
  var world = el("g", { id: "world" }, svg);
  var edges = el("g", { "class": "edges" }, world);
  var rels = el("g", { "class": "relations" }, world);
  var rows = el("g", { "class": "nodes" }, world);
  var selected = null, view = { x: 0, y: 0, k: 1 };

  function shape(type, g) {           /* node form by type */
    if (type === "source") return el("rect", { x: -9, y: -9, width: 18, height: 18, rx: 4 }, g);
    if (type === "chapter") return el("polygon", { points: "0,-10 9,-5 9,5 0,10 -9,5 -9,-5" }, g);
    if (type === "concept") return el("polygon", { points: "0,-8 8,0 0,8 -8,0" }, g);
    return el("circle", { r: 8 }, g);
  }
  function short(s, n) { return s.length > n ? s.slice(0, n - 1) + "…" : s; }

  var visible = [], drawn = {};
  function render() {
    edges.textContent = ""; rels.textContent = ""; rows.textContent = "";
    visible = []; drawn = {};
    (function collect(list) { list.forEach(function (i) { visible.push(i); if (i.open) collect(i.children); }); })(roots);
    visible.forEach(function (inst, row) {
      inst.x = PAD + inst.depth * INDENT; inst.y = PAD + row * ROW + ROW / 2;
      drawn[inst.id] = drawn[inst.id] || inst;
    });
    visible.forEach(function (inst) {
      if (inst.parent) {   /* elbow connector from the parent's shape down to this row */
        var p = inst.parent, cls = inst.slot ? "slot " + inst.slot : "contains";
        el("path", { d: "M" + p.x + "," + (p.y + 10) + "V" + inst.y + "H" + (inst.x - 10), "class": cls }, edges);
      }
      var n = inst.node, g = el("g", { transform: "translate(" + inst.x + "," + inst.y + ")",
        "class": "node " + n.type + (n.contested ? " contested" : "") + (inst.children.length ? (inst.open ? " open" : " closed") : " leaf")
                 + (selected === inst.id ? " selected" : "") }, rows);
      g.dataset.key = inst.key;
      el("circle", { r: 16, "class": "hit", "data-act": "toggle" }, g);
      shape(n.type, g);
      if (inst.children.length && n.type !== "source") el("text", { "class": "chev", x: 0, y: 4, "text-anchor": "middle" }, g).textContent = inst.open ? "−" : "+";
      var label = n.label; if (n.type === "chapter") label += " · " + n.count;
      var t = el("text", { x: 16, y: 4, "class": "label", "data-act": "select" }, g);
      if (n.lang) t.setAttribute("lang", n.lang);
      if (inst.slot) { var s = el("tspan", { "class": "slot-tag" }, t); s.textContent = inst.slot + " "; }
      el("tspan", {}, t).textContent = short(label, n.type === "statement" ? 60 : 44);
    });
    data.relations.forEach(function (r) {   /* dashed arcs on the right between related statements */
      var a = drawn[r.from], b = drawn[r.to]; if (!a || !b) return;
      var x = Math.max(a.x, b.x) + 30 + 8 * Math.abs(a.depth - b.depth), bend = x + 40;
      el("path", { d: "M" + x + "," + a.y + " C" + bend + "," + a.y + " " + bend + "," + b.y + " " + x + "," + b.y, "class": "relation " + r.kind }, rels)
        .appendChild(el("title", {})).textContent = r.kind;
    });
    var h = PAD * 2 + visible.length * ROW;
    svg.dataset.h = h;
  }

  /* pan / zoom inside the viewport; fit animates to the open rows */
  function apply() { world.setAttribute("transform", "translate(" + view.x + "," + view.y + ") scale(" + view.k + ")"); }
  function fit(rowsToFit) {
    var r = svg.getBoundingClientRect();
    var ys = rowsToFit.map(function (i) { return i.y; });
    var y0 = Math.min.apply(null, ys) - ROW, y1 = Math.max.apply(null, ys) + ROW;
    var k = Math.min(1.6, Math.max(0.5, (r.height - 2 * PAD) / (y1 - y0)));
    var target = { k: k, x: PAD, y: (r.height - (y1 - y0) * k) / 2 - y0 * k };
    if (target.y > PAD) target.y = PAD;
    animate(target);
  }
  var anim = null;
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
    var k = Math.max(0.4, Math.min(4, view.k * f)); f = k / view.k;
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
    if (press && press.id === e.pointerId) tap(press.target);
    press = null;
  }
  svg.addEventListener("pointerup", up); svg.addEventListener("pointercancel", up);
  svg.addEventListener("wheel", function (e) { e.preventDefault(); var p = local(e.clientX, e.clientY); zoomAt(e.deltaY < 0 ? 1.15 : 1 / 1.15, p.x, p.y); }, { passive: false });

  /* taps: shape toggles, label selects (and opens); background clears the selection */
  function tap(target) {
    var g = target.closest && target.closest("g.node");
    if (!g) { select(null, true); return; }
    var inst = instances[+g.dataset.key], act = target.getAttribute("data-act") || "toggle";
    if (act === "select") { select(inst.id, true, inst); return; }
    if (inst.children.length) { inst.open = !inst.open; render(); fit(inst.open ? [inst].concat(inst.children) : [inst]); }
    else select(inst.id, true, inst);
  }
  function select(id, push, inst) {
    selected = id;
    if (!id || !nodes[id]) {
      render(); sheet.innerHTML = home; hint.hidden = false;
      if (push) history.replaceState(null, "", location.pathname);
      return;
    }
    inst = inst || byId[id].filter(function (i) { return visible.indexOf(i) >= 0; })[0] || byId[id][0];
    for (var p = inst.parent; p; p = p.parent) p.open = true;   /* reveal the path to it */
    if (inst.children.length) inst.open = true;
    render();
    sheet.innerHTML = nodes[id].html; hint.hidden = true;
    if (push) history.replaceState(null, "", "#" + id);
    fit([inst].concat(inst.open ? inst.children : []));
    sheet.scrollIntoView({ behavior: "smooth", block: "start" });
  }
  sheet.addEventListener("click", function (e) {
    var a = e.target.closest("a.node-link");
    if (a && nodes[a.dataset.node]) { e.preventDefault(); select(a.dataset.node, true); window.scrollTo({ top: 0, behavior: "smooth" }); }
  });
  document.getElementById("fit").addEventListener("click", function () { fit(visible); });
  document.getElementById("reset").addEventListener("click", function () {
    instances.forEach(function (i) { i.open = false; }); roots.forEach(function (r) { r.open = true; }); select(null, true); fit(visible);
  });
  window.addEventListener("hashchange", function () { select(decodeURIComponent(location.hash.slice(1)), false); });
  window.addEventListener("resize", function () { fit(visible); });

  render();
  if (location.hash.length > 1 && nodes[decodeURIComponent(location.hash.slice(1))]) select(decodeURIComponent(location.hash.slice(1)), false);
  else fit(visible);
})();
