const puppeteer = require('puppeteer');
const path = require('path');
const fs = require('fs');

const BASE = 'https://testbill.smit34.ru';
const OUT = 'd:/tmp/test_screenshots';
if (!fs.existsSync(OUT)) fs.mkdirSync(OUT, { recursive: true });

const results = {};

async function tryScreenshot(page, filename, label) {
  try {
    await page.screenshot({ path: OUT + '/' + filename, fullPage: false });
    results[label] = { status: 'ok', file: filename };
    console.log('[OK] ' + label + ' -> ' + filename);
  } catch (e) {
    results[label] = { status: 'error', error: e.message };
    console.log('[ERR] ' + label + ': ' + e.message);
  }
}

(async () => {
  const browser = await puppeteer.launch({
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--ignore-certificate-errors']
  });
  const page = await browser.newPage();
  await page.setViewport({ width: 1400, height: 900 });

  // Ignore certificate errors
  await page.setBypassCSP(true);

  // ---- 1. Страница входа ----
  console.log('Navigating to login...');
  try {
    await page.goto(BASE + '/admin/login/', { waitUntil: 'networkidle2', timeout: 30000 });
    await tryScreenshot(page, '00_login_page.png', 'login_page');

    // Неверный пароль тест
    await page.type('#id_username', 'uspeshnyy');
    await page.type('#id_password', 'WRONG_PASSWORD');
    await Promise.all([
      page.click('[type=submit]'),
      page.waitForNavigation({ timeout: 10000 }).catch(() => {})
    ]);
    await tryScreenshot(page, '00b_login_wrong_pass.png', 'login_wrong_pass');

    const errorVisible = await page.$('.alert-danger, .errornote, .errorlist') !== null;
    results['login_wrong_pass'].error_shown = errorVisible;
    console.log('  Wrong pass error shown:', errorVisible);

    // Очищаем поля и вводим правильный пароль
    await page.evaluate(() => { document.getElementById('id_username').value = ''; document.getElementById('id_password').value = ''; });
    await page.type('#id_username', 'uspeshnyy');
    await page.type('#id_password', 'Qqqqq!1111');
    await Promise.all([
      page.click('[type=submit]'),
      page.waitForNavigation({ waitUntil: 'networkidle2', timeout: 15000 })
    ]);
    console.log('Current URL after login:', page.url());
    results['login'] = { status: page.url().includes('/admin/') ? 'ok' : 'error', url: page.url() };
    await tryScreenshot(page, '01_dashboard.png', 'dashboard');
  } catch (e) {
    results['login'] = { status: 'error', error: e.message };
    console.log('[ERR] Login: ' + e.message);
  }

  // ---- 2. Список абонентов (папка) ----
  try {
    await page.goto(BASE + '/admin/Abonents/9001/', { waitUntil: 'networkidle2', timeout: 20000 });
    await page.waitForSelector('.content-wrapper', { timeout: 10000 });
    await tryScreenshot(page, '02_abonents_folder.png', 'abonents_folder');
    results['abonents_folder'].note = 'Root folder loaded';
  } catch (e) {
    results['abonents_folder'] = { status: 'error', error: e.message };
    console.log('[ERR] Abonents folder: ' + e.message);
  }

  // ---- 3. Глобальный поиск абонентов ----
  try {
    await page.goto(BASE + '/admin/Abonents/search/', { waitUntil: 'networkidle2', timeout: 20000 });
    await page.waitForSelector('body', { timeout: 10000 });
    await tryScreenshot(page, '03_abonents_search.png', 'abonents_search');

    // Попробуем чип должников
    await page.goto(BASE + '/admin/Abonents/search/?chip=debtors', { waitUntil: 'networkidle2', timeout: 20000 });
    await tryScreenshot(page, '03b_abonents_debtors.png', 'abonents_debtors');

    // Count abonents in search
    const count = await page.$eval('.badge, .stats-badge, [data-total]', el => el.textContent).catch(() => 'N/A');
    results['abonents_search'].debtors_chip = 'tested';
  } catch (e) {
    results['abonents_search'] = { status: 'error', error: e.message };
    console.log('[ERR] Abonents search: ' + e.message);
  }

  // ---- 4. FinanceOperations список ----
  try {
    await page.goto(BASE + '/admin/Abonents/FinanceOperations/', { waitUntil: 'networkidle2', timeout: 20000 });
    await page.waitForSelector('body', { timeout: 10000 });
    await tryScreenshot(page, '04_finops_list.png', 'finops_list');
    results['finops_list'].note = 'FinanceOperations list loaded';
  } catch (e) {
    results['finops_list'] = { status: 'error', error: e.message };
    console.log('[ERR] FinOps list: ' + e.message);
  }

  // ---- 5. Настройки ----
  try {
    await page.goto(BASE + '/admin/settings/VpnConst/', { waitUntil: 'networkidle2', timeout: 20000 });
    await page.waitForSelector('body', { timeout: 10000 });
    await tryScreenshot(page, '05_settings.png', 'settings');
  } catch (e) {
    results['settings'] = { status: 'error', error: e.message };
    console.log('[ERR] Settings: ' + e.message);
  }

  // ---- 6. Карточка абонента #3296 ----
  try {
    await page.goto(BASE + '/admin/Abonents/3296/', { waitUntil: 'networkidle2', timeout: 20000 });
    await page.waitForSelector('.nav-tabs, .content-wrapper', { timeout: 10000 });
    await tryScreenshot(page, '06_abonent_card.png', 'abonent_card');
    results['abonent_card'].note = 'Abonent 3296 card';
  } catch (e) {
    results['abonent_card'] = { status: 'error', error: e.message };
    console.log('[ERR] Abonent card: ' + e.message);
  }

  // ---- 7. Вкладка Операции абонента ----
  try {
    await page.goto(BASE + '/admin/Abonents/3296/?tab=fin_ops', { waitUntil: 'networkidle2', timeout: 20000 });
    await page.waitForSelector('.content-wrapper', { timeout: 10000 });
    await tryScreenshot(page, '07_abonent_operations.png', 'abonent_operations');
  } catch (e) {
    results['abonent_operations'] = { status: 'error', error: e.message };
    console.log('[ERR] Abonent operations: ' + e.message);
  }

  // ---- 8. Вкладка Услуги абонента ----
  try {
    await page.goto(BASE + '/admin/Abonents/3296/?tab=usluga', { waitUntil: 'networkidle2', timeout: 20000 });
    await page.waitForSelector('.content-wrapper', { timeout: 10000 });
    await tryScreenshot(page, '08_abonent_uslugi.png', 'abonent_uslugi');
  } catch (e) {
    results['abonent_uslugi'] = { status: 'error', error: e.message };
    console.log('[ERR] Abonent uslugi: ' + e.message);
  }

  // ---- 9. Мастер создания абонента ----
  try {
    await page.goto(BASE + '/admin/Abonents/9001/?action=wizard', { waitUntil: 'networkidle2', timeout: 20000 }).catch(() => {});
    // Try the wizard button approach
    await page.goto(BASE + '/admin/Abonents/9001/', { waitUntil: 'networkidle2', timeout: 20000 });
    const wizardBtn = await page.$('.btn-wizard, [href*="wizard"], button[data-action="wizard"]');
    if (wizardBtn) {
      await wizardBtn.click();
      await page.waitForSelector('.modal, .wizard-form, form', { timeout: 5000 }).catch(() => {});
    }
    await tryScreenshot(page, '09_abonent_wizard.png', 'abonent_wizard');
  } catch (e) {
    results['abonent_wizard'] = { status: 'error', error: e.message };
    console.log('[ERR] Abonent wizard: ' + e.message);
  }

  // ---- 10. Users modal (Учётные записи) ----
  try {
    await page.goto(BASE + '/admin/Abonents/3296/', { waitUntil: 'networkidle2', timeout: 20000 });
    await page.waitForSelector('.content-wrapper', { timeout: 10000 });
    // Try clicking users edit button
    const editBtn = await page.$('.btn-usr-edit, .btn-edit-user, [data-target="#modal-usr"]');
    if (editBtn) {
      await editBtn.click();
      await page.waitForSelector('#modal-usr', { timeout: 5000 }).catch(() => {});
    }
    await tryScreenshot(page, '10_users_modal.png', 'users_modal');
  } catch (e) {
    results['users_modal'] = { status: 'error', error: e.message };
    console.log('[ERR] Users modal: ' + e.message);
  }

  // ---- 11. PayLog (FinanceOperations report) ----
  try {
    await page.goto(BASE + '/admin/reports/PayLog/', { waitUntil: 'networkidle2', timeout: 20000 });
    await page.waitForSelector('body', { timeout: 10000 });
    await tryScreenshot(page, '11_paylog.png', 'paylog');
  } catch (e) {
    results['paylog'] = { status: 'error', error: e.message };
    console.log('[ERR] PayLog: ' + e.message);
  }

  // ---- 12. Dashboard Reports ----
  try {
    await page.goto(BASE + '/admin/reports/dashboard/', { waitUntil: 'networkidle2', timeout: 20000 });
    await page.waitForSelector('body', { timeout: 10000 });
    await tryScreenshot(page, '12_reports_dashboard.png', 'reports_dashboard');
  } catch (e) {
    results['reports_dashboard'] = { status: 'error', error: e.message };
    console.log('[ERR] Reports dashboard: ' + e.message);
  }

  // ---- 13. Settings Payment ----
  try {
    await page.goto(BASE + '/admin/settings/payment/', { waitUntil: 'networkidle2', timeout: 20000 });
    await page.waitForSelector('body', { timeout: 10000 });
    await tryScreenshot(page, '13_settings_payment.png', 'settings_payment');
  } catch (e) {
    results['settings_payment'] = { status: 'error', error: e.message };
    console.log('[ERR] Settings payment: ' + e.message);
  }

  // ---- 14. IP Пулы ----
  try {
    await page.goto(BASE + '/admin/dictionary/IpPull/', { waitUntil: 'networkidle2', timeout: 20000 });
    await page.waitForSelector('body', { timeout: 10000 });
    await tryScreenshot(page, '14_ip_pools.png', 'ip_pools');
  } catch (e) {
    results['ip_pools'] = { status: 'error', error: e.message };
    console.log('[ERR] IP pools: ' + e.message);
  }

  // ---- 15. Тарифы ----
  try {
    await page.goto(BASE + '/admin/dictionary/Tarif/', { waitUntil: 'networkidle2', timeout: 20000 });
    await page.waitForSelector('body', { timeout: 10000 });
    await tryScreenshot(page, '15_tariffs.png', 'tariffs');
  } catch (e) {
    results['tariffs'] = { status: 'error', error: e.message };
    console.log('[ERR] Tariffs: ' + e.message);
  }

  await browser.close();

  console.log('\n=== RESULTS ===');
  console.log(JSON.stringify(results, null, 2));

  // Write results JSON
  fs.writeFileSync(OUT + '/results.json', JSON.stringify(results, null, 2));
  console.log('Done. Screenshots in ' + OUT);
})();
