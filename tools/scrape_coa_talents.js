// Scrape every talent tooltip from ascensionsidekick.com.
//
//   node tools/scrape_coa_talents.js <specs.json> <outdir>
//
// The site is a React SPA, so a plain HTTP fetch returns an empty shell and
// everything has to be rendered. The talent data is NOT in the page text -
// the builder grid renders only point counts like "3/3" - but every node's
// tooltip is already present in the DOM as span.btooltip, so no hovering is
// needed. A first version did hover each node and diff document.innerText,
// which sliced names mid-word ("ncreased armor penetration") because the
// tooltip replaces rather than appends. Read the element instead.
//
// Each tooltip carries name, level/type, full description, point cost and the
// tier requirement, e.g.
//
//   Strength of the Black Empire | Level 40 Passive | Dreadnought now sheds
//   your mortal form, transforming you into a void monstrosity, reducing your
//   damage taken by -10% | Free | Requires 16 points in this tree (level 40)
//
// AE = class-tree points, TE = spec-tree points. Each spec page carries both
// trees, so the class tree repeats across that class's spec pages.
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const SPECS_FILE = process.argv[2] || '/tmp/coa/_specs.json';
const OUTDIR = process.argv[3] || '/tmp/coa_talents';
const BASE = 'https://ascensionsidekick.com';
const CONCURRENCY = 5;

async function pool(items, n, fn) {
  const queue = [...items];
  await Promise.all(Array.from({ length: n }, async () => {
    while (queue.length) await fn(queue.shift());
  }));
}

(async () => {
  const specs = JSON.parse(fs.readFileSync(SPECS_FILE, 'utf8'));
  fs.mkdirSync(OUTDIR, { recursive: true });
  const browser = await chromium.launch();
  const ctx = await browser.newContext();
  let ok = 0, empty = 0;

  await pool(specs, CONCURRENCY, async (specPath) => {
    const page = await ctx.newPage();
    let tips = [];
    // Retry: the grid is rendered client-side and sometimes needs longer.
    for (let attempt = 0; attempt < 3 && tips.length === 0; attempt++) {
      try {
        await page.goto(BASE + specPath, { waitUntil: 'domcontentloaded', timeout: 60000 });
      } catch (e) { /* fall through to the wait + read */ }
      await page.waitForTimeout(4000 + attempt * 3000);
      tips = await page.evaluate(() =>
        [...document.querySelectorAll('span.btooltip, div.bld-tip')]
          .map(e => (e.innerText || '').trim())
          .filter(t => t.length > 15));
    }
    const name = specPath.slice(1).replace(/\//g, '__') + '.json';
    fs.writeFileSync(path.join(OUTDIR, name),
      JSON.stringify({ path: specPath, tooltips: tips }, null, 1));
    if (tips.length) ok++; else empty++;
    console.log(`${specPath}  ${tips.length} tooltips`);
    await page.close();
  });

  await browser.close();
  console.log(`DONE  ${ok} pages with tooltips, ${empty} empty`);
})();
