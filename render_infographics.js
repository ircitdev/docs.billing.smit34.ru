const puppeteer = require('puppeteer');
const OUT = 'd:/tmp/mailserver_shots';
const items = [
  ['infographic_mailserv.html', 'info_architecture.png'],
  ['infographic_mailserv_domains.html', 'info_domains.png'],
];
(async () => {
  const browser = await puppeteer.launch({ headless: true, args: ['--no-sandbox'] });
  for (const [src, out] of items) {
    const page = await browser.newPage();
    await page.setViewport({ width: 1280, height: 900, deviceScaleFactor: 2 });
    await page.goto('file:///' + __dirname.replace(/\\/g,'/') + '/' + src, { waitUntil: 'networkidle0' });
    await new Promise(r => setTimeout(r, 400));
    await page.screenshot({ path: OUT + '/' + out, fullPage: true });
    console.log('[OK] ' + out);
    await page.close();
  }
  await browser.close();
})();
