const puppeteer = require('puppeteer');
const fs = require('fs');
const OUT = 'd:/tmp/test_screenshots';

(async () => {
  const browser = await puppeteer.launch({
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox'],
    ignoreHTTPSErrors: true
  });
  const ctx = await browser.createBrowserContext();
  const pg = await ctx.newPage();
  await pg.setViewport({ width: 1400, height: 900 });

  await pg.goto('https://testbill.smit34.ru/admin/login/', { waitUntil: 'domcontentloaded', timeout: 30000 });
  await pg.screenshot({ path: OUT + '/00a_login_page.png' });
  console.log('[OK] login page screenshot');

  // Wrong password
  await pg.type('[name=username]', 'uspeshnyy');
  await pg.type('[name=password]', 'WRONGPASS123');
  await pg.click('[type=submit]');
  await pg.waitForNavigation({ waitUntil: 'domcontentloaded', timeout: 10000 }).catch(() => {});
  await pg.screenshot({ path: OUT + '/00b_login_wrong_pass.png' });
  const errEl = await pg.$('.alert, .error, [class*=error], .alert-danger');
  const errText = errEl ? await errEl.evaluate(e => e.innerText) : '';
  console.log('[OK] wrong pass screenshot, error:', errText.substring(0, 100));

  // Correct login
  await pg.evaluate(() => {
    document.querySelector('[name=username]').value = '';
    document.querySelector('[name=password]').value = '';
  });
  await pg.type('[name=username]', 'uspeshnyy');
  await pg.type('[name=password]', 'Qqqqq!1111');
  await Promise.all([
    pg.click('[type=submit]'),
    pg.waitForNavigation({ waitUntil: 'networkidle2', timeout: 20000 })
  ]);
  console.log('After login URL:', pg.url());
  await pg.screenshot({ path: OUT + '/01_dashboard_after_login.png' });
  console.log('[OK] dashboard after login screenshot');

  await browser.close();
  console.log('Done');
})();
