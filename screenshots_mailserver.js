const puppeteer = require('puppeteer');
const fs = require('fs');

const BASE = 'https://testbill.smit34.ru';   // DNS → rbill 193.232.2.128
const OUT = 'd:/tmp/mailserver_shots';
if (!fs.existsSync(OUT)) fs.mkdirSync(OUT, { recursive: true });

const results = {};

async function shot(page, file, label, opts = {}) {
  try {
    await page.screenshot({ path: OUT + '/' + file, fullPage: !!opts.full });
    results[label] = { status: 'ok', file };
    console.log('[OK] ' + label + ' -> ' + file);
  } catch (e) {
    results[label] = { status: 'error', error: e.message };
    console.log('[ERR] ' + label + ': ' + e.message);
  }
}

async function go(page, url, waitSel) {
  await page.goto(url, { waitUntil: 'networkidle2', timeout: 35000 });
  if (waitSel) await page.waitForSelector(waitSel, { timeout: 12000 }).catch(() => {});
  // дать догрузиться AJAX вкладкам
  await new Promise(r => setTimeout(r, 1800));
}

(async () => {
  const browser = await puppeteer.launch({
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--ignore-certificate-errors']
  });
  const page = await browser.newPage();
  await page.setViewport({ width: 1480, height: 940 });
  await page.setBypassCSP(true);

  // ---- Логин ----
  try {
    await go(page, BASE + '/admin/login/', '[name=username]');
    await page.type('[name=username]', 'uspeshnyy');
    await page.type('[name=password]', 'Qqqqq!1111');
    await Promise.all([
      page.click('button.btn-large.btn-success[type=submit]'),
      page.waitForNavigation({ waitUntil: 'networkidle2', timeout: 20000 })
    ]);
    results['login'] = { status: page.url().includes('/admin/') ? 'ok' : 'error', url: page.url() };
    console.log('login url:', page.url());
  } catch (e) {
    results['login'] = { status: 'error', error: e.message };
    console.log('[ERR] login: ' + e.message);
  }

  const tabs = [
    ['overview',       '01_overview.png',       'Обзор'],
    ['mailboxes',      '02_mailboxes.png',      'Ящики'],
    ['domain-admins',  '03_domain_admins.png',  'Админы доменов'],
    ['domains',        '04_domains.png',        'Домены'],
    ['login-branding', '05_login_branding.png', 'Страница входа'],
  ];

  for (const [slug, file, label] of tabs) {
    try {
      await go(page, BASE + '/admin/settings/mailserver/' + slug + '/', '.content-wrapper');
      await shot(page, file, 'mailserver_' + slug);
    } catch (e) {
      results['mailserver_' + slug] = { status: 'error', error: e.message };
      console.log('[ERR] ' + slug + ': ' + e.message);
    }
  }

  // полностраничный обзор для документации
  try {
    await go(page, BASE + '/admin/settings/mailserver/overview/', '.content-wrapper');
    await shot(page, '01b_overview_full.png', 'mailserver_overview_full', { full: true });
  } catch (e) { console.log('[ERR] overview full: ' + e.message); }

  // ---- DNS раздел ----
  try {
    await go(page, BASE + '/admin/settings/dns/', '.content-wrapper');
    await shot(page, '06_dns.png', 'dns_access');
    await shot(page, '06b_dns_full.png', 'dns_full', { full: true });
  } catch (e) {
    results['dns'] = { status: 'error', error: e.message };
    console.log('[ERR] dns: ' + e.message);
  }

  await browser.close();
  fs.writeFileSync(OUT + '/results.json', JSON.stringify(results, null, 2));
  console.log('\n=== RESULTS ===');
  console.log(JSON.stringify(results, null, 2));
  console.log('Done -> ' + OUT);
})();
