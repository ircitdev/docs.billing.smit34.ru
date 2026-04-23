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

  await pg.goto('https://testbill.smit34.ru/admin/login/', { waitUntil: 'networkidle2', timeout: 30000 });
  await pg.screenshot({ path: OUT + '/00a_login_page.png' });
  console.log('[OK] login page screenshot');

  // Get all buttons and submit inputs
  const buttons = await pg.$$eval('button, input[type=submit], [type=submit]', els =>
    els.map(e => ({ tag: e.tagName, type: e.type, text: e.textContent.trim(), id: e.id, class: e.className.substring(0,50) }))
  );
  console.log('Buttons:', JSON.stringify(buttons));

  // Wrong password via form submit
  await pg.type('[name=username]', 'uspeshnyy');
  await pg.type('[name=password]', 'WRONGPASS123');
  // Submit via Enter key
  await pg.keyboard.press('Enter');
  await pg.waitForNavigation({ waitUntil: 'domcontentloaded', timeout: 10000 }).catch(() => {});
  await pg.screenshot({ path: OUT + '/00b_login_wrong_pass.png' });
  console.log('[OK] wrong pass screenshot');
  const bodyText = await pg.$eval('body', e => e.innerText);
  console.log('Body has error?', bodyText.includes('Пожалуйста') || bodyText.includes('error') || bodyText.toLowerCase().includes('неверн'));

  // Correct login
  await pg.evaluate(() => {
    document.querySelector('[name=username]').value = '';
    document.querySelector('[name=password]').value = '';
  });
  await pg.type('[name=username]', 'uspeshnyy');
  await pg.type('[name=password]', 'Qqqqq!1111');
  await pg.keyboard.press('Enter');
  await pg.waitForNavigation({ waitUntil: 'networkidle2', timeout: 20000 }).catch(e => console.log('nav error:', e.message));
  console.log('After login URL:', pg.url());
  await pg.screenshot({ path: OUT + '/01_dashboard_new.png' });
  console.log('[OK] dashboard screenshot');

  await browser.close();
})();
