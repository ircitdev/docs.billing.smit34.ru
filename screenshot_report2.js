const puppeteer = require('puppeteer');
const BASE = 'https://testbill.smit34.ru';
const OUT = 'd:/tmp/mailserver_shots';
const FILE = 'Отчёты/2026-06-18_Отчёт_Модуль_Почтовый_сервер_mailserv.md';
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
  const url = BASE + '/admin/reports/dev/?tab=reports&file=' + encodeURIComponent(FILE);
  await page.goto(url, { waitUntil: 'networkidle2', timeout: 30000 });
  await new Promise(r => setTimeout(r, 4500)); // дать markdown + картинкам GCS прогрузиться
  await page.screenshot({ path: OUT + '/07_report_in_billing.png', fullPage: false });
  // проверка содержимого
  const info = await page.evaluate(() => ({
    hasHero: !!document.querySelector('img[src*="info_architecture"]'),
    imgCount: document.querySelectorAll('img[src*="mailserv_v1225"]').length,
    h1: (document.querySelector('h1') || {}).textContent || ''
  }));
  console.log('[OK] 07_report_in_billing.png', JSON.stringify(info));
  await browser.close();
})();
