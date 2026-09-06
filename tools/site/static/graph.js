/* graph.med view page: one decision tree — which patient group? → which condition? →
   recommendation → aim — drawn left to right by Cytoscape.js with the dagre layout
   (self-hosted, see assets/vendor/LICENSES.md). Folded by default: tap an answer to
   unfold that patient group. Tap a box for its details in the section beside or below
   the graph. Data: the #graph-data JSON written by tools/build.py. */
(function () {
  "use strict";
  var hint = document.getElementById("hint"), sheet = document.getElementById("sheet");
  var home = sheet.innerHTML;
  function fail(msg) { hint.hidden = false; hint.textContent = "The graph could not be drawn: " + msg; }
  try { draw(); } catch (e) { fail(e && e.message ? e.message : String(e)); throw e; }

  function draw() {
  var data = JSON.parse(document.getElementById("graph-data").textContent);
  var css = function (name) { return getComputedStyle(document.documentElement).getPropertyValue(name).trim(); };
  var GRADE = { A: "--gA", B: "--gB", "0": "--g0", EK: "--gEK", mixed: "--line" };
  if (typeof cytoscape !== "function") throw new Error("library missing");
  if (typeof cytoscapeDagre === "function") cytoscape.use(cytoscapeDagre);

  var elements = [];
  data.nodes.forEach(function (n) {
    elements.push({ data: { id: n.id, ref: n.ref || "", type: n.type, label: n.label || "", group: n.group || "",
      fill: n.grade ? css(GRADE[n.grade] || "--line") : css("--bg"), against: n.against ? 1 : 0, contested: n.contested ? 1 : 0 } });
  });
  data.edges.forEach(function (e, i) {
    elements.push({ data: { id: "e" + i, source: e.from, target: e.to, kind: e.kind, label: e.label || "", ref: e.ref || "" } });
  });

  var cy = cytoscape({
    container: document.getElementById("graph"),
    elements: elements,
    minZoom: 0.1, maxZoom: 4,
    boxSelectionEnabled: false, autounselectify: true,
    style: [
      { selector: "node", style: {
          "shape": "round-rectangle", "background-color": "data(fill)", "border-width": 1.5, "border-color": css("--mute"),
          "label": "data(label)", "color": css("--fg"), "font-family": "system-ui, sans-serif", "font-size": 12,
          "text-wrap": "wrap", "text-max-width": 210, "text-valign": "center", "text-halign": "center",
          "width": 240, "height": "label", "padding": 10 } },
      { selector: "node[type = 'root']", style: { "font-weight": 700, "border-color": css("--fg") } },
      { selector: "node[type = 'question']", style: { "shape": "diamond", "width": 200, "height": 120, "padding": 0, "text-max-width": 110, "border-color": css("--fg"), "font-weight": 600 } },
      { selector: "node[type = 'junction']", style: { "shape": "ellipse", "width": 30, "height": 30, "padding": 0, "font-size": 11, "font-weight": 700,
          "background-color": css("--bg"), "border-color": css("--fg"), "border-width": 2, "text-max-width": 30 } },
      { selector: "node[type = 'junction'].open", style: { "background-color": css("--fg"), "color": css("--bg") } },
      { selector: "node[type = 'statement']", style: { "color": "#111", "border-color": "rgba(0,0,0,0)", "text-halign": "center" } },
      { selector: "node[type = 'statement'][against = 1]", style: { "border-width": 3, "border-color": css("--contested") } },
      { selector: "node[type = 'statement'][contested = 1]", style: { "border-width": 3, "border-color": css("--contested"), "border-style": "dashed" } },
      { selector: "node[type = 'aim']", style: { "width": 180, "text-max-width": 160, "font-size": 11, "color": css("--mute"), "border-style": "dashed" } },
      { selector: "edge", style: {
          "curve-style": "bezier", "width": 1.5, "line-color": css("--edge"),
          "target-arrow-shape": "triangle", "target-arrow-color": css("--edge"), "arrow-scale": 0.9,
          "label": "data(label)", "font-size": 11, "color": css("--fg"), "text-wrap": "wrap", "text-max-width": 170,
          "text-background-color": css("--bg"), "text-background-opacity": 1, "text-background-padding": 3, "text-background-shape": "round-rectangle" } },
      { selector: "edge[kind = 'answer']", style: { "line-color": css("--fg"), "target-arrow-color": css("--fg"), "font-weight": 600 } },
      { selector: "edge[kind = 'aim']", style: { "line-style": "dashed", "target-arrow-shape": "none" } },
      { selector: "edge[kind = 'relation']", style: { "line-style": "dotted", "line-color": css("--statement"), "target-arrow-color": css("--statement") } },
      { selector: ".folded", style: { "display": "none" } },
      { selector: ".dim", style: { "opacity": 0.12 } },
      { selector: ".picked", style: { "border-width": 3, "border-color": css("--fg"), "line-color": css("--fg"), "width": 3 } }
    ],
    layout: { name: "preset" }
  });

  /* folding: the root, the first question and its answers are always shown; a patient
     group's subtree only while its junction is open */
  var junctions = cy.nodes("[type = 'junction']"), open = {};
  var always = cy.nodes("[type = 'root'], [type = 'question']").filter(function (n) { return n.id() === "q:population" || n.data("type") === "root"; })
               .union(junctions).union(junctions.connectedEdges()).union(cy.nodes("[type = 'root']").connectedEdges());
  function relayout(fitTo) {
    var shown = always;
    junctions.forEach(function (j) { if (open[j.id()]) shown = shown.union(j.successors()); });
    cy.elements().addClass("folded"); shown.removeClass("folded");
    junctions.forEach(function (j) { j.toggleClass("open", !!open[j.id()]); });
    var lay = shown.layout({ name: "dagre", rankDir: "LR", nodeSep: 14, rankSep: 90, edgeSep: 10, align: "UL", animate: true, animationDuration: 250, fit: false });
    lay.one("layoutstop", function () { if (fitTo) cy.animate({ fit: { eles: fitTo.not(".folded"), padding: 30 }, duration: 250 }); });
    lay.run();
  }
  function toggle(j, force) {
    open[j.id()] = force === undefined ? !open[j.id()] : force;
    relayout(open[j.id()] ? j.union(j.successors()) : j.closedNeighborhood());
  }

  /* selection: what leads to the element and what follows it stays; the rest fades; the sheet fills */
  function select(eles, ref, push) {
    cy.elements().removeClass("dim picked");
    if (!eles || eles.empty()) {
      sheet.innerHTML = home; hint.hidden = false;
      if (push) history.replaceState(null, "", location.pathname);
      return;
    }
    var keep = eles.union(eles.predecessors()).union(eles.successors());
    cy.elements().not(keep).addClass("dim");
    eles.addClass("picked");
    sheet.innerHTML = data.html[ref] || home; hint.hidden = !data.html[ref];
    if (push) history.replaceState(null, "", "#" + ref);
    if (window.innerWidth < 900) sheet.scrollIntoView({ behavior: "smooth", block: "start" });
  }
  cy.on("tap", "node, edge", function (evt) {
    var t = evt.target, ref = t.data("ref");
    var j = t.isNode() && t.data("type") === "junction" ? t : (t.isEdge() && t.data("kind") === "answer" && t.target().data("type") === "junction" ? t.target() : null);
    if (j) { toggle(j); }
    if (!ref) return;
    var eles = cy.elements("[ref = '" + ref + "']");
    select(eles, ref, true);
    if (!j) cy.animate({ fit: { eles: eles.closedNeighborhood().not(".folded"), padding: 40 }, duration: 250 });
  });
  cy.on("tap", function (evt) { if (evt.target === cy) select(null, null, true); });
  document.getElementById("fit").addEventListener("click", function () { cy.animate({ fit: { eles: cy.elements().not(".folded"), padding: 20 }, duration: 250 }); });
  window.addEventListener("resize", function () { cy.resize(); });

  function open_(ref, push) {
    var eles = ref ? cy.elements("[ref = '" + ref + "']") : cy.collection();
    if (eles.empty()) { relayout(cy.elements()); return; }
    var groups = eles.union(eles.predecessors()).filter("[type = 'junction']");
    groups.forEach(function (j) { open[j.id()] = true; });
    relayout(eles.closedNeighborhood());
    select(eles, ref, push);
  }
  sheet.addEventListener("click", function (e) {
    var a = e.target.closest("a.node-link");
    if (a && cy.elements("[ref = '" + a.dataset.node + "']").nonempty()) { e.preventDefault(); open_(a.dataset.node, true); if (window.innerWidth < 900) window.scrollTo({ top: 0, behavior: "smooth" }); }
  });
  window.addEventListener("hashchange", function () { open_(decodeURIComponent(location.hash.slice(1)), false); });
  cy.ready(function () { open_(decodeURIComponent(location.hash.slice(1)), false); });
  window.graphmed = { cy: cy, open: open_, toggle: toggle, isOpen: function (id) { return !!open[id]; } };   /* for the console and tests */
  }
})();
