const puppeteer = require('puppeteer');
const fs = require('fs');
const OUT = 'd:/tmp/test_screenshots';

(async () => {
  const browser = await puppeteer.launch({
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--ignore-certificate-errors']
  });
  const page = await browser.newPage();
  await page.setViewport({ width: 1400, height: 900 });

  // Use incognito to ensure clean session
  const ctx = await browser.createBrowserContext();
  const pg = await ctx.newPage();
  await pg.setViewport({ width: 1400, height: 900 });

  // Go to login page (fresh session)
  await pg.goto('https://testbill.smit34.ru/admin/login/?next=/admin/', { waitUntil: 'networkidle2', timeout: 30000 });
  await pg.screenshot({ path: OUT + '/00a_login_fresh.png' });
  console.log('Login page screenshot taken');

  // Test wrong password
  await pg.type('#id_username', 'uspeshnyy');
  await pg.type('#id_password', 'WRONGPASS');
  await Promise.all([
    pg.click('[type=submit]'),
    pg.waitForNavigation({ waitUntil: 'networkidle2', timeout: 15000 }).catch(() => {})
  ]);
  await pg.screenshot({ path: OUT + '/00b_login_wrong.png' });
  const errText = await pg.$eval('body', el => el.innerText).catch(() => '');
  console.log('Wrong pass error shown:', errText.includes('Пожалуйста') || errText.includes('неверн') || errText.includes('error') || errText.includes('Error'));

  // Clear and login correctly
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
  await pg.screenshot({ path: OUT + '/01_dashboard_after_login.png' });

  await browser.close();
  console.log('Done');
})();
