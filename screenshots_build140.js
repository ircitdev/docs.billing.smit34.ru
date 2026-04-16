const puppeteer = require('puppeteer');
const path = require('path');

const BASE = 'https://testbill.smit34.ru';
const OUT = path.join(__dirname, 'img', 'v140');
const LOGIN = { username: 'uspeshnyy', password: 'Qqqqq!1111' };

const PAGES = [
    // Audit
    { name: 'audit_operations.png', url: '/admin/reports/AuditOperations/', wait: 3000, w: 1400, h: 900 },
    // Reports library
    { name: 'reports_library.png', url: '/admin/reports/AdminCustomReports/?tab=all', wait: 2000, w: 1400, h: 800 },
    // Report execution with history
    { name: 'report_execute.png', url: '/admin/reports/AdminCustomReports/136/executesql/', wait: 2000, w: 1400, h: 800 },
    // Server logs
    { name: 'server_logs.png', url: '/admin/reports/dev/?tab=logs&log=error.log', wait: 2000, w: 1400, h: 900 },
    // Dev reports
    { name: 'dev_reports.png', url: '/admin/reports/dev/?tab=reports', wait: 2000, w: 1400, h: 800 },
    // Profile
    { name: 'profile.png', url: '/admin/settings/profile/', wait: 1500, w: 1400, h: 900 },
    // Staff management
    { name: 'staff_list.png', url: '/admin/settings/staff/', wait: 1500, w: 1400, h: 800 },
    // Settings - integrations sidebar
    { name: 'settings_integrations.png', url: '/admin/settings/integrations/?tab=claude', wait: 1500, w: 1400, h: 800 },
    // Dictionary - pools with tabs
    { name: 'dict_pools.png', url: '/admin/dictionary/IpPull/', wait: 1500, w: 1400, h: 700 },
    // Dictionary - statuses with tabs
    { name: 'dict_statuses.png', url: '/admin/dictionary/Status/', wait: 1500, w: 1400, h: 700 },
    // Settings - mass actions with tabs
    { name: 'settings_mass_actions.png', url: '/admin/settings/unblock/', wait: 1500, w: 1400, h: 700 },
    // Menu sidebar - reports section
    { name: 'menu_reports.png', url: '/admin/reports/dev/?tab=logs', wait: 1500, w: 400, h: 600, clip: { x: 0, y: 60, width: 280, height: 500 } },
];

(async () => {
    const fs = require('fs');
    if (!fs.existsSync(OUT)) fs.mkdirSync(OUT, { recursive: true });

    const browser = await puppeteer.launch({ headless: 'new', args: ['--no-sandbox'] });
    const page = await browser.newPage();

    // Login
    await page.goto(`${BASE}/admin/login/`, { waitUntil: 'networkidle2' });
    await page.type('input[name="username"]', LOGIN.username);
    await page.type('input[name="password"]', LOGIN.password);
    await page.evaluate(() => document.querySelector('form').submit());
    await page.waitForNavigation({ waitUntil: 'networkidle2' });
    console.log('Logged in');

    for (const p of PAGES) {
        try {
            await page.setViewport({ width: p.w || 1400, height: p.h || 900 });
            await page.goto(`${BASE}${p.url}`, { waitUntil: 'networkidle2', timeout: 15000 });
            if (p.wait) await new Promise(r => setTimeout(r, p.wait));
            const opts = { path: path.join(OUT, p.name), type: 'png' };
            if (p.clip) opts.clip = p.clip;
            else opts.fullPage = false;
            await page.screenshot(opts);
            console.log(`✓ ${p.name}`);
        } catch (e) {
            console.log(`✗ ${p.name}: ${e.message}`);
        }
    }

    await browser.close();
    console.log(`\nDone. Screenshots in ${OUT}`);
})();
