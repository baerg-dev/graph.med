/* graph.med view page: one decision tree — which patient group? → which condition? →
   recommendation → aim — drawn by Cytoscape.js with the dagre layout (self-hosted, see
   assets/vendor/LICENSES.md). Nodes size to their text, edges carry the answers, nothing
   overlaps. Tap a node for its details in the section below. Data: the #graph-data JSON
   written by tools/build.py. */
(function () {
  "use strict";
  var data = JSON.parse(document.getElementById("graph-data").textContent);
  var sheet = document.getElementById("sheet"), hint = document.getElementById("hint");
  var home = sheet.innerHTML;
  var css = function (name) { return getComputedStyle(document.documentElement).getPropertyValue(name).trim(); };
  var GRADE = { A: "--gA", B: "--gB", "0": "--g0", EK: "--gEK", mixed: "--line" };
  if (typeof cytoscapeDagre === "function") cytoscape.use(cytoscapeDagre);

  var elements = [];
  data.nodes.forEach(function (n) {
    elements.push({ data: { id: n.id, ref: n.ref || "", type: n.type, label: n.label || "", lang: n.lang || "",
      no: n.no || "", fill: n.grade ? css(GRADE[n.grade] || "--line") : css("--bg"),
      against: n.against ? 1 : 0, contested: n.contested ? 1 : 0 } });
  });
  data.edges.forEach(function (e, i) {
    elements.push({ data: { id: "e" + i, source: e.from, target: e.to, kind: e.kind, label: e.label || "", ref: e.ref || "" } });
  });

  var cy = cytoscape({
    container: document.getElementById("graph"),
    elements: elements,
    minZoom: 0.04, maxZoom: 4, wheelSensitivity: 0.3,
    boxSelectionEnabled: false, autounselectify: true,
    style: [
      { selector: "node", style: {
          "shape": "round-rectangle", "background-color": "data(fill)", "border-width": 1.5, "border-color": css("--mute"),
          "label": "data(label)", "color": css("--fg"), "font-family": "system-ui, sans-serif", "font-size": 12,
          "text-wrap": "wrap", "text-max-width": 200, "text-valign": "center", "text-halign": "center",
          "width": "label", "height": "label", "padding": 10 } },
      { selector: "node[type = 'root']", style: { "font-weight": 700, "text-max-width": 260, "border-color": css("--fg") } },
      { selector: "node[type = 'question']", style: { "shape": "diamond", "padding": 26, "border-color": css("--fg"), "font-weight": 600 } },
      { selector: "node[type = 'junction']", style: { "shape": "ellipse", "width": 12, "height": 12, "padding": 0, "background-color": css("--mute"), "border-width": 0 } },
      { selector: "node[type = 'statement']", style: { "color": "#111", "border-color": "rgba(0,0,0,0)", "text-max-width": 220 } },
      { selector: "node[type = 'statement'][against = 1]", style: { "border-width": 3, "border-color": css("--contested") } },
      { selector: "node[type = 'statement'][contested = 1]", style: { "border-width": 3, "border-color": css("--contested"), "border-style": "dashed" } },
      { selector: "node[type = 'aim']", style: { "shape": "tag", "font-size": 11, "color": css("--mute"), "border-style": "dashed" } },
      { selector: "edge", style: {
          "curve-style": "bezier", "width": 1.5, "line-color": css("--edge"),
          "target-arrow-shape": "triangle", "target-arrow-color": css("--edge"), "arrow-scale": 0.9,
          "label": "data(label)", "font-size": 10, "color": css("--fg"), "text-wrap": "wrap", "text-max-width": 150,
          "text-background-color": css("--bg"), "text-background-opacity": 1, "text-background-padding": 2, "text-background-shape": "round-rectangle" } },
      { selector: "edge[kind = 'answer']", style: { "line-color": css("--fg"), "target-arrow-color": css("--fg"), "font-weight": 600 } },
      { selector: "edge[kind = 'aim']", style: { "line-style": "dashed", "target-arrow-shape": "none" } },
      { selector: "edge[kind = 'relation']", style: { "line-style": "dotted", "line-color": css("--statement"), "target-arrow-color": css("--statement") } },
      { selector: ".dim", style: { "opacity": 0.12 } },
      { selector: ".picked", style: { "border-width": 3, "border-color": css("--fg"), "line-color": css("--fg"), "width": 3 } }
    ],
    layout: { name: "dagre", rankDir: "TB", nodeSep: 24, rankSep: 70, edgeSep: 12, ranker: "network-simplex" }
  });

  /* selection: what leads to the node and what follows it stays; the rest fades; the sheet fills */
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
    cy.animate({ fit: { eles: eles.closedNeighborhood(), padding: 40 }, duration: 250 });
    sheet.scrollIntoView({ behavior: "smooth", block: "start" });
  }
  cy.on("tap", "node, edge", function (evt) {
    var ref = evt.target.data("ref"); if (!ref) return;
    select(cy.elements("[ref = '" + ref + "']"), ref, true);
  });
  cy.on("tap", function (evt) { if (evt.target === cy) select(null, null, true); });
  document.getElementById("fit").addEventListener("click", function () { cy.animate({ fit: { padding: 20 }, duration: 250 }); });

  function open(ref, push) {
    var eles = ref ? cy.elements("[ref = '" + ref + "']") : null;
    if (eles && eles.nonempty()) select(eles, ref, push); else { select(null, null, false); cy.fit(20); }
  }
  sheet.addEventListener("click", function (e) {
    var a = e.target.closest("a.node-link");
    if (a && cy.elements("[ref = '" + a.dataset.node + "']").nonempty()) { e.preventDefault(); open(a.dataset.node, true); window.scrollTo({ top: 0, behavior: "smooth" }); }
  });
  window.addEventListener("hashchange", function () { open(decodeURIComponent(location.hash.slice(1)), false); });
  cy.ready(function () { open(decodeURIComponent(location.hash.slice(1)), false); });
})();
