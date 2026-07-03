const puppeteer = require('puppeteer');
const BASE = 'https://testbill.smit34.ru';
const OUT = 'd:/tmp/mailserver_shots';
(async () => {
  const browser = await puppeteer.launch({ headless: true, args: ['--no-sandbox','--ignore-certificate-errors'] });
  const page = await browser.newPage();
  await page.setViewport({ width: 1480, height: 1000 });
  await page.setBypassCSP(true);
  await page.goto(BASE + '/admin/login/', { waitUntil: 'networkidle2' });
  await page.waitForSelector('[name=username]', { timeout: 15000 });
  await page.type('[name=username]', 'uspeshnyy');
  await page.type('[name=password]', 'Qqqqq!1111');
  await Promise.all([
    page.click('button.btn-large.btn-success[type=submit]'),
    page.waitForNavigation({ waitUntil: 'networkidle2', timeout: 20000 })
  ]);
  // открыть раздел отчётов и кликнуть новый отчёт
  await page.goto(BASE + '/admin/reports/dev/', { waitUntil: 'networkidle2', timeout: 30000 });
  await new Promise(r => setTimeout(r, 2500));
  // первый файл в списке = наш отчёт (сортировка по дате, он новейший)
  const clicked = await page.evaluate(() => {
    const rows = [...document.querySelectorAll('*')].filter(e =>
      e.children.length === 0 && /^2026-06-18_/.test(e.textContent.trim()) && e.offsetParent);
    const t = rows[0];
    if (t) { (t.closest('li,a,tr,div') || t).click(); return t.textContent.trim().slice(0,60); }
    return null;
  });
  console.log('clicked:', clicked);
  await new Promise(r => setTimeout(r, 3500));
  await page.screenshot({ path: OUT + '/07_report_in_billing.png', fullPage: false });
  console.log('[OK] 07_report_in_billing.png');
  await browser.close();
})();
