/* Runs inside zenika/alpine-chrome:with-puppeteer (tools/screenshot.py copies it in): open the
   built view page at file:///site/<view>/, wait for the graph to lay out, run the requested
   actions through window.graphmed (the hooks tools/site/static/graph.js exposes), capture. */
const puppeteer = require("/usr/src/app/node_modules/puppeteer");
const spec = JSON.parse(process.argv[2]);
const sleep = ms => new Promise(r => setTimeout(r, ms));
(async () => {
  const browser = await puppeteer.launch({ executablePath: "/usr/bin/chromium-browser", args: ["--no-sandbox", "--disable-gpu", "--hide-scrollbars"] });
  const page = await browser.newPage();
  const errors = [];
  page.on("pageerror", e => errors.push(String(e)));
  page.on("console", m => { if (m.type() === "error") errors.push(m.text()); });
  await page.setViewport({ width: spec.width, height: spec.height, deviceScaleFactor: spec.phone ? 2 : 1, isMobile: !!spec.phone, hasTouch: !!spec.phone });
  await page.goto(`file:///site/${spec.view}/index.html`, { waitUntil: "load" });
  await page.waitForFunction(() => window.graphmed && window.graphmed.cy.nodes().not(".folded").length > 0, { timeout: 20000 });
  await sleep(900);
  for (const [action, value] of spec.actions) {
    if (action === "wait") { await sleep(Number(value) || 500); continue; }
    await page.evaluate((action, value) => {
      const g = window.graphmed;
      if (action === "toggle") g.toggle(g.cy.getElementById("j:" + value));
      else if (action === "open") g.open(value, false);
      else if (action === "section") g.section(value);
      else if (action === "search") g.search(value);
      else if (action === "facet") g.search(document.getElementById("search").value, value);
      else if (action === "chapters") document.getElementById("chapters-toggle").click();
      else throw new Error("unknown action " + action);
    }, action, value);
    await sleep(900);
  }
  await page.screenshot({ path: "/tmp/shot.png" });
  const shown = await page.evaluate(() => window.graphmed.cy.elements().not(".folded").length);
  console.log(`${shown} elements shown` + (errors.length ? `; page errors: ${errors.join(" | ")}` : ""));
  await browser.close();
})().catch(e => { console.error("screenshot failed: " + e.message); process.exit(1); });
