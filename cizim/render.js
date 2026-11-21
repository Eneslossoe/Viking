// SVG -> PNG (Playwright/Chromium). Kullanım: node render.js isler.json
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const FONT_DIR = path.join(__dirname, 'fontlar');
const fontCss = `
@font-face { font-family: 'Cinzel'; font-weight: 700; src: url('file://${FONT_DIR}/Cinzel-Bold.ttf'); }
@font-face { font-family: 'Cinzel'; font-weight: 900; src: url('file://${FONT_DIR}/Cinzel-Black.ttf'); }
@font-face { font-family: 'Nunito'; font-weight: 800; src: url('file://${FONT_DIR}/Nunito-ExtraBold.ttf'); }
@font-face { font-family: 'Nunito'; font-weight: 900; src: url('file://${FONT_DIR}/Nunito-Black.ttf'); }
html, body { margin: 0; padding: 0; background: transparent; }
svg { display: block; }
`;

(async () => {
  const jobs = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
  const scale = parseFloat(process.env.RENDER_SCALE || '1.1');
  const browser = await chromium.launch();
  const ctx = await browser.newContext({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: scale });
  const page = await ctx.newPage();
  for (const job of jobs) {
    const svg = fs.readFileSync(job.svg, 'utf8');
    const w = job.w || 1920, h = job.h || 1080;
    if (w !== 1920 || h !== 1080) await page.setViewportSize({ width: w, height: h });
    const html = `<!doctype html><html><head><meta charset="utf-8"><style>${fontCss}</style></head><body>${svg}</body></html>`;
    const htmlPath = path.resolve(job.svg.replace(/\.svg$/, '.html'));
    fs.writeFileSync(htmlPath, html);
    await page.goto('file://' + htmlPath);
    await page.evaluate(() => document.fonts.ready);
    await page.screenshot({ path: job.png, clip: { x: 0, y: 0, width: w, height: h }, omitBackground: !!job.transparent });
    if (w !== 1920 || h !== 1080) await page.setViewportSize({ width: 1920, height: 1080 });
    fs.unlinkSync(htmlPath);
    process.stdout.write('.');
  }
  await browser.close();
  console.log(' ok', jobs.length);
})();
