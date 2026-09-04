# -*- coding: ascii -*-
import base64, time
for p in ['/admin/settings/modules/', '/admin/settings/widgets/', '/admin/settings/messaging/',
          '/admin/settings/bank_statements/', '/admin/ai/dialer/']:
    js("location.href='https://rbill.smit34.ru%s'" % p)
    for _ in range(16):
        time.sleep(2)
        if js("location.pathname") == p and js("document.readyState") == 'complete':
            break
    time.sleep(3)
    raw = js("btoa(String.fromCharCode(...new TextEncoder().encode(document.body.innerText.replace(new RegExp(String.fromCharCode(92)+'s+','g'),' ').slice(120, 620))))")
    print('=== ' + p)
    print(base64.b64decode(raw).decode('utf-8'))
