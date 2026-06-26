# الشمري (Al-Shammari v2.0) – أداة فحص ثغرات شاملة

أداة فحص واستغلال ثغرات تطبيقات الويب. متعددة المنصات (Windows / macOS / Linux / Termux)، بدون اعتماديات خارجية.

---

## الجديد في v2.0

| الميزة | التفاصيل |
|---|---|
| **محرك التخفي (Stealth Engine)** | تدوير بصمة متصفح، تأخير متكيّف، كشف WAF وتفادي الحظر تلقائياً |
| **مكتبة الـ Payloads** | من 200+ إلى 700+ payload منظم حسب الفئة وقاعدة البيانات |
| **فحص NoSQL** | MongoDB, JavaScript Injection, Redis, Cassandra |
| **فحص SSTI** | 14 محرك قوالب: Jinja2, Twig, FreeMarker, Velocity, Mako, Smarty, Thymeleaf, EJS, Nunjucks, PugJS, Tornado, ERB |
| **فحص Command Injection** | Unix + Windows + WAF bypass |
| **فحص XXE** | File read, Out-of-Band, Billion Laughs |
| **فحص GraphQL** | SQLi داخل استعلامات GraphQL |
| **فحص JWT** | تزوير none algorithm، path traversal في kid |
| **فحص LFI** | قراءة ملفات مع PHP wrappers |
| **فحص Database-Specific** | MSSQL, PostgreSQL, Oracle مخصص |
| **تحقق إحصائي** | Boolean verification + Time-based مع baseline متعدد العينات |
| **استخراج بيانات** | سحب تلقائي لـ emails, tokens, usernames بعد الاستغلال |
| **فحص IDOR** | 90+ اسم باراميتر + ترميزات Base64/hex |
| **كشف XSS متقدم** | تحليل سياق الانعكاس (script, attribute, event handler, HTML body) + تحقق متعدد |
| **استغلال متكامل** | Union extraction، stacked queries، OOB data exfiltration |
| **وضع CLI كامل** | تشغيل بكل الخيارات من سطر الأوامر بدون menu |

---

## المزايا العامة

- فحص SQL Injection (14 فئة)
- فحص XSS (10+ فئة)
- فحص IDOR مع fuzzing
- فحص Auth Bypass
- فحص NoSQL Injection
- فحص SSTI (Server-Side Template Injection)
- فحص Command Injection
- فحص XXE
- فحص GraphQL
- فحص JWT
- فحص LFI
- بصمة الهدف (WAF, CMS, Database)
- دعم البروكسيات والكوكيز
- محرك تخفي متكامل (Stealth)
- تشغيل من سطر الأوامر أو من قائمة تفاعلية

---

## المتطلبات

- بايثون `3.6+`

## التشغيل

### الوضع التفاعلي
```sh
python3 FQsql.py --menu
```

### فحص شامل تلقائي
```sh
python3 FQsql.py -u "http://target.com/page.php?id=1" --type auto
```

### فحص SQL Injection
```sh
python3 FQsql.py -u "http://target.com/page.php?id=1" --type sqli
```

### فحص XSS
```sh
python3 FQsql.py -u "http://target.com/search?q=test" --type xss
```

### فحص IDOR
```sh
python3 FQsql.py -u "http://target.com/api/user/1" --type idor
```

### فحص Auth Bypass
```sh
python3 FQsql.py -u "http://target.com/login" --type auth
```

### فحص إضافي (NoSQL + SSTI + CMDi + XXE)
```sh
python3 FQsql.py -u "http://target.com/page" --type extra
```

### بصمة الهدف
```sh
python3 FQsql.py -u "http://target.com" --type fp
```

### فحص جماعي من ملف
```sh
python3 FQsql.py -f urls.txt
```

### فحص مخصص (Custom Payload)
```sh
python3 FQsql.py -u "http://target.com" --payload "' OR 1=1 --" --method POST --param username
```

---

## خيارات سطر الأوامر

| الخيار | الوصف |
|---|---|
| `-u, --url` | رابط الهدف |
| `-p, --payload` | Payload مخصص |
| `-m, --method` | HTTP method (افتراضي GET) |
| `-P, --param` | اسم الباراميتر المستهدف |
| `-t, --type` | نوع الفحص: auto, sqli, xss, idor, auth, extra, fp |
| `-f, --file` | ملف روابط للفحص الجماعي |
| `--proxy` | بروكسي (http://ip:port) |
| `--proxy-file` | ملف بروكسيات |
| `--delay` | تأخير بين الطلبات (min-max بالثواني) |
| `--no-delay` | تعطيل التأخير |
| `--cookies` | كوكيز (key=value;key2=value2) |
| `--fingerprint` | بصمة المتصفح: chrome_win, chrome_mac, firefox_linux, safari_mac... |
| `--menu` | تشغيل القائمة التفاعلية |

---

## الإحصائيات

| الفئة | عدد الـ Payloads |
|---|---|
| SQL Injection | 250+ |
| XSS | 120+ |
| NoSQL | 40+ |
| SSTI | 45+ |
| Command Injection | 60+ |
| XXE | 15+ |
| **المجموع** | **530+** |

---

## تنبيه

الاستخدام يكون على الأنظمة أو التطبيقات المصرح لك بفحصها فقط.
