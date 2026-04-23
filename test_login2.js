const puppeteer = require('puppeteer');
const fs = require('fs');
const OUT = 'd:/tmp/test_screenshots';

(async () => {
  const browser = await puppeteer.launch({
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--ignore-certificate-errors'],
    ignoreHTTPSErrors: true
  });

  // Fresh context (no cookies)
  const ctx = await browser.createBrowserContext();
  const pg = await ctx.newPage();
  await pg.setViewport({ width: 1400, height: 900 });

  // Go directly to login
  const resp = await pg.goto('https://testbill.smit34.ru/admin/login/', { waitUntil: 'domcontentloaded', timeout: 30000 });
  console.log('Login page status:', resp.status());
  console.log('Login page URL:', pg.url());

  // Check if #id_username exists
  const hasInput = await pg.$('#id_username');
  console.log('Has login input:', !!hasInput);

  await pg.screenshot({ path: OUT + '/00a_login_page.png' });

  if (hasInput) {
    await pg.type('#id_username', 'uspeshnyy');
    await pg.type('#id_password', 'WRONG_PASS_123');
    await pg.click('[type=submit]');
    await pg.waitForNavigation({ waitUntil: 'domcontentloaded', timeout: 10000 }).catch(() => {});
    await pg.screenshot({ path: OUT + '/00b_login_wrong_pass.png' });
    const body = await pg.$eval('body', el => el.innerText).catch(() => '');
    console.log('Error text:', body.substring(0, 200));

    // Login correct
    await pg.evaluate(() => {
      document.getElementById('id_username').value = '';
      document.getElementById('id_password').value = '';
    });
    await pg.type('#id_username', 'uspeshnyy');
    await pg.type('#id_password', 'Qqqqq!1111');
    await Promise.all([
      pg.click('[type=submit]'),
      pg.waitForNavigation({ waitUntil: 'networkidle2', timeout: 20000 })
    ]);
    console.log('After login URL:', pg.url());
    await pg.screenshot({ path: OUT + '/01_dashboard_new.png' });
  }

  await browser.close();
  console.log('Done');
})();
