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
  console.log('URL:', pg.url());

  // Get all inputs
  const inputs = await pg.$$eval('input', els => els.map(e => ({ id: e.id, name: e.name, type: e.type })));
  console.log('Inputs:', JSON.stringify(inputs));

  // Get page title
  const title = await pg.title();
  console.log('Title:', title);

  await pg.screenshot({ path: OUT + '/00a_login_real.png' });

  if (inputs.length > 0) {
    const unameInput = inputs.find(i => i.name === 'username' || i.type === 'text' || i.name === 'login');
    console.log('Username input:', unameInput);
  }

  await browser.close();
})();
