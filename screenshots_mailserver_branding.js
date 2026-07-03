const puppeteer = require('puppeteer');
const fs = require('fs');
const BASE = 'https://testbill.smit34.ru';
const OUT = 'd:/tmp/mailserver_shots';

async function go(page, url, sel) {
  await page.goto(url, { waitUntil: 'networkidle2', timeout: 35000 });
  if (sel) await page.waitForSelector(sel, { timeout: 12000 }).catch(() => {});
  await new Promise(r => setTimeout(r, 1800));
}

(async () => {
  const browser = await puppeteer.launch({
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--ignore-certificate-errors']
  });
  const page = await browser.newPage();
  await page.setViewport({ width: 1480, height: 1100 });
  await page.setBypassCSP(true);

  await go(page, BASE + '/admin/login/', '[name=username]');
  await page.type('[name=username]', 'uspeshnyy');
  await page.type('[name=password]', 'Qqqqq!1111');
  await Promise.all([
    page.click('button.btn-large.btn-success[type=submit]'),
    page.waitForNavigation({ waitUntil: 'networkidle2', timeout: 20000 })
  ]);

  // login-branding → клик по первому домену в списке
  await go(page, BASE + '/admin/settings/mailserver/login-branding/', '.content-wrapper');
  // кликнуть первую строку домена входа
  const clicked = await page.evaluate(() => {
    const cand = document.querySelector('[data-brand-domain], .ms-brand-item, .list-group-item, [data-domain]');
    if (cand) { cand.click(); return cand.textContent.trim().slice(0, 40); }
    // fallback: первая строка, содержащая mail.
    const rows = [...document.querySelectorAll('a,div,li')].filter(e => /mail\./.test(e.textContent) && e.offsetParent);
    if (rows[0]) { rows[0].click(); return rows[0].textContent.trim().slice(0, 40); }
    return null;
  });
  console.log('clicked domain row:', clicked);
  await new Promise(r => setTimeout(r, 2000));
  await page.screenshot({ path: OUT + '/05b_branding_form.png', fullPage: true });
  console.log('[OK] 05b_branding_form.png');

  // проверка: текст комментария НЕ виден
  const leaked = await page.evaluate(() =>
    document.body.innerText.includes('Поле загрузки ассета') ||
    document.body.innerText.includes('field (имя поля'));
  console.log('comment leaked on page:', leaked);

  await browser.close();
})();
