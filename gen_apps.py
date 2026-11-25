# -*- coding: utf-8 -*-
"""產生每支 App 自己的介紹頁（四種語言），輸出到各 App 的公開 repo。

**為什麼要有這一頁**（2026-11-25）：推廣時只想貼一個連結。貼兩個商店連結很亂，
貼總網頁又要對方自己找是哪一支。所以每支 App 一頁：**最上面就是雙平台下載**，
下面才是介紹。總網頁只放在推廣帳號的個人簡介裡。

**一個連結通吃四種語言**：預設頁（index.html）是英文——那也是 App Store 的
「支援 URL」，審查員打開要看得懂——但瀏覽器語言是中、日、韓的人會被自動帶到
自己的語言。切換列上的 English 連到 `./?en`，帶著那個參數就不會再被帶走。

**資料只有一份**：名稱、標語、三個重點、商店連結、隱私權政策都直接 import
gen_hub.py 的 APPS，商店上架、換連結時只改那裡。介紹內文則是各 App 的
**商店完整說明**，從各自的私有 repo 讀進來——商店文案改了，重跑這支就跟上。
某個語言沒有完整說明（運動習慣只寫了中、英文）時改放三個重點。

**鬧鐘不在這裡產生**：它有自己更完整的介紹頁（更新紀錄、班別圖示），由
botanoalarm 私有 repo 的 tool/landing_page.py 產生。

**不要手改產生出來的 HTML**，下次跑就會被蓋掉。

    python3 gen_apps.py <私有 repo 的上層目錄> <公開 repo 的上層目錄>
    例：python3 gen_apps.py ~/code ../pub
"""

import html
import io
import os
import re
import sys

from gen_hub import APPS, LANG_ATTR, LANG_NAME, PLAY_URL

SITE = "https://botanodev.github.io"

OUT = {"en": "index.html", "zh": "index-zh.html", "ja": "index-ja.html", "ko": "index-ko.html"}

UI = {
    "en": {"soon": "Coming soon", "privacy": "Privacy policy", "more": "More apps by Botano",
           "highlights": "Highlights",
           "foot": 'Questions or suggestions: "Settings &rarr; Feedback" in the app, or '
                   '<a href="mailto:botanodev@gmail.com">botanodev@gmail.com</a>.'},
    "zh": {"soon": "即將推出", "privacy": "隱私權政策", "more": "Botano 的其他 App",
           "highlights": "重點",
           "foot": '有問題或建議，可以在 App 裡的「設定 → 意見與支援」寄給我，或寄到 '
                   '<a href="mailto:botanodev@gmail.com">botanodev@gmail.com</a>。'},
    "ja": {"soon": "近日公開", "privacy": "プライバシーポリシー", "more": "Botano のほかのアプリ",
           "highlights": "ポイント",
           "foot": 'ご質問・ご要望はアプリの「設定 → 意見とサポート」から、またはメール '
                   '<a href="mailto:botanodev@gmail.com">botanodev@gmail.com</a> まで。'},
    "ko": {"soon": "출시 예정", "privacy": "개인정보 처리방침", "more": "Botano의 다른 앱",
           "highlights": "주요 기능",
           "foot": '문의나 제안은 앱의 "설정 → 의견 및 지원"에서, 또는 '
                   '<a href="mailto:botanodev@gmail.com">botanodev@gmail.com</a>으로 보내 주세요.'},
}

# 「Android / iPhone」放在商店名稱上面，讓人一眼知道該按哪一個
PLATFORM = {
    "en": ("Android", "iPhone"), "zh": ("Android", "iPhone"),
    "ja": ("Android", "iPhone"), "ko": ("Android", "iPhone"),
}


# ---------------------------------------------------------------- 讀商店文案

def _read(path):
    return io.open(path, encoding="utf-8").read()


def _md_full(text, section_re, heading_re):
    """在 section_re 那一節之後，找 heading_re 標題底下的第一個 ``` 區塊。"""
    m = re.search(section_re, text, re.M)
    if not m:
        return None
    h = re.compile(heading_re, re.M).search(text, m.end())
    if not h:
        return None
    b = re.compile(r"^```[^\n]*\n(.*?)^```", re.M | re.S).search(text, h.end())
    return b.group(1).strip() if b else None


def _tag_full(text, tag):
    m = re.search(r"<%s>\n(.*?)\n</%s>" % (tag, tag), text, re.S)
    return m.group(1).strip() if m else None


def descriptions(code_dir, slug):
    """{語言: 完整說明純文字}。哪個語言沒有就不放。"""
    p = lambda *a: os.path.join(code_dir, slug, *a)
    out = {}
    if slug == "plantrecord":
        t = _read(p("store-listing.md"))
        for lang, sec in (("en", r"^## 〇、"), ("zh", r"^## 〇之三、"),
                          ("ja", r"^## 〇之四、"), ("ko", r"^## 〇之六、")):
            out[lang] = _md_full(t, sec, r"^### 完整說明")
    elif slug == "tripcart":
        t = _read(p("docs", "store", "listing.md"))
        for lang, tag in (("en", "en-US-full"), ("zh", "zh-TW-full"),
                          ("ja", "ja-JP-full"), ("ko", "ko-KR-full")):
            out[lang] = _tag_full(t, tag)
    elif slug == "plushcam":
        t = _read(p("doc", "store_listing.md"))
        heading = r"^### (完整說明|Full description|詳しい説明|자세한 설명)"
        for lang, sec in (("zh", r"^## 繁體中文"), ("en", r"^## English"),
                          ("ja", r"^## 日本語"), ("ko", r"^## 한국어")):
            out[lang] = _md_full(t, sec, heading)
    elif slug == "exercisehabit":
        t = _read(p("doc", "store_listing.md"))
        heading = r"^### (完整說明|Full description)"
        for lang, sec in (("zh", r"^## 繁體中文"), ("en", r"^## English")):
            out[lang] = _md_full(t, sec, heading)
    out = {k: v for k, v in out.items() if v}
    for lang, (a, b) in NEUTRAL.get(slug, {}).items():
        if lang in out:
            out[lang] = out[lang].replace(a, b)
    return out


# 商店文案是寫給 Play 的，這一頁兩個平台都連，所以把只講一邊的字換掉。
# 換不到（文案改寫過）不會報錯，產生後檢查會列出殘留的平台字樣。
NEUTRAL = {
    "tripcart": {
        "en": ("for Google Play purchases", "for in-app purchases"),
        "zh": ("透過 Google Play 購買", "App 內購買"),
        "ja": ("Google Play での購入", "アプリ内購入"),
        "ko": ("Google Play 구매", "앱 내 구매"),
    },
}


# ---------------------------------------------------------------- 純文字轉 HTML

_BULLET = re.compile(r"^\s*(?:[・•·]|- )\s*")
_NUM = re.compile(r"^\s*\d+[.．、)]\s*")
_CAPS = re.compile(r"^[A-Z0-9][A-Z0-9 ,'’&/:?!()\-–—]+$")
_END = tuple(u"。.!?！？:：、,，)）」")


def _heading(line):
    s = line.strip()
    if s.startswith(u"▍"):
        return s[1:].strip()
    if s.startswith(u"【") and s.endswith(u"】"):
        return s[1:-1].strip()
    if s.startswith(u"[") and s.endswith(u"]"):
        return s[1:-1].strip()
    if s.startswith(u"■"):
        return s[1:].strip()
    if len(s) > 3 and _CAPS.match(s) and any(c.isalpha() for c in s):
        return s.capitalize() if s.isupper() else s
    return None


def _short_title(line, lang):
    s = line.strip()
    limit = 16 if lang in ("zh", "ja", "ko") else 32
    return (len(s) <= limit and not s.endswith(_END)
            and not _BULLET.match(s) and not _NUM.match(s))


def _join(lines, lang):
    # 商店文案有些是手動折行的（植物紀錄的英文），段落內的行要接回去。
    # 中、日文接起來不加空白。
    sep = u"" if lang in ("zh", "ja") else u" "
    return sep.join(l.strip() for l in lines)


def to_html(text, lang):
    e = html.escape
    out = []
    for block in re.split(r"\n\s*\n", text.strip()):
        lines = [l for l in block.split("\n") if l.strip()]
        if len(lines) == 1 and _short_title(lines[0], lang):
            # 植物紀錄的寫法：小標題自成一段，前後都空行
            out.append(u"<h2>%s</h2>" % e(_heading(lines[0]) or lines[0].strip()))
            continue
        if lines and _heading(lines[0]):
            out.append(u"<h2>%s</h2>" % e(_heading(lines[0])))
            lines = lines[1:]
        i = 0
        while i < len(lines):
            if _BULLET.match(lines[i]) or _NUM.match(lines[i]):
                tag = "ol" if _NUM.match(lines[i]) else "ul"
                pat = _NUM if tag == "ol" else _BULLET
                items = []
                while i < len(lines) and pat.match(lines[i]):
                    items.append(u"<li>%s</li>" % e(pat.sub(u"", lines[i]).strip()))
                    i += 1
                out.append(u"<%s>%s</%s>" % (tag, u"".join(items), tag))
                continue
            para = []
            while i < len(lines) and not (_BULLET.match(lines[i]) or _NUM.match(lines[i])):
                para.append(lines[i])
                i += 1
            first = para[0].strip()
            if len(para) > 1 and _short_title(first, lang):
                # 「手持／像平常一樣……」這種小標題接說明的寫法
                out.append(u"<p><b>%s</b><br>%s</p>" % (e(first), e(_join(para[1:], lang))))
            else:
                out.append(u"<p>%s</p>" % e(_join(para, lang)))
    return u"\n".join(out)


# ---------------------------------------------------------------- 版面

CSS = """  :root {
    --bg: #F5F7F4; --ink: #1A1D18; --muted: #4A5147; --hair: #DCE0D8;
    --brand: #5273A8; --green: #4C7A3F; --card: #FFFFFF;
    --btn: #1A1D18; --btnink: #FFFFFF;
  }
  @media (prefers-color-scheme: dark) {
    :root {
      --bg: #101410; --ink: #E2E5DC; --muted: #B3BCAC; --hair: #2B322A;
      --green: #9DD48B; --card: #171B16;
      --btn: #E2E5DC; --btnink: #101410;
    }
  }
  * { box-sizing: border-box; }
  body {
    margin: 0; background: var(--bg); color: var(--ink);
    font-family: system-ui, "Noto Sans TC", "Noto Sans JP", "Noto Sans KR", sans-serif;
    line-height: 1.75; -webkit-font-smoothing: antialiased;
  }
  header { background: var(--brand); color: #fff; padding: 20px 20px 36px; }
  header .inner, .wrap { max-width: 40rem; margin: 0 auto; }
  header .bar {
    display: flex; justify-content: space-between; align-items: center;
    gap: 10px; flex-wrap: wrap; margin-bottom: 28px; font-size: .9rem;
  }
  header .bar a { color: #DCE4F2; text-decoration: none; }
  header .bar strong { color: #fff; }
  header .bar nav { display: flex; gap: 12px; flex-wrap: wrap; }
  header .app { display: flex; gap: 16px; align-items: center; }
  header img {
    width: 76px; height: 76px; border-radius: 18px; flex: none;
    box-shadow: 0 2px 10px rgba(0,0,0,.18);
  }
  header h1 { margin: 0; font-size: 1.6rem; line-height: 1.3; letter-spacing: -.01em; }
  header h1 small { display: block; font-size: .9rem; font-weight: 400; color: #DCE4F2; }
  header .line { margin: 18px 0 0; color: #EEF2F9; font-size: 1.02rem; }

  .stores {
    display: grid; grid-template-columns: 1fr 1fr; gap: 10px;
    margin: -22px 0 8px; position: relative;
  }
  .stores a, .stores span {
    display: block; padding: 11px 14px; text-decoration: none;
    border-radius: 12px; line-height: 1.25; text-align: center;
  }
  .stores a { background: var(--btn); color: var(--btnink); box-shadow: 0 2px 8px rgba(0,0,0,.15); }
  .stores span { background: var(--card); color: var(--muted); border: 1px solid var(--hair); }
  .stores small { display: block; font-size: .75rem; opacity: .75; }
  .stores b { font-size: 1.05rem; white-space: nowrap; }

  .wrap { padding: 0 20px 64px; }
  .desc { margin-top: 28px; }
  .desc h2 { font-size: 1.08rem; margin: 36px 0 10px; }
  .desc p { margin: 0 0 14px; }
  .desc ul, .desc ol { margin: 0 0 14px; padding-left: 1.3em; }
  .desc li { margin-bottom: 6px; }
  .desc li::marker { color: var(--green); }

  footer {
    margin-top: 44px; padding-top: 18px; border-top: 1px solid var(--hair);
    color: var(--muted); font-size: .92rem;
  }
  footer a { color: var(--green); }
  footer p { margin: 0 0 10px; }
"""

# 瀏覽器語言自動帶到對應語言的頁面（只放在英文的預設頁）。
# 網址帶 ?en 表示使用者自己選了英文，不再帶走。
REDIRECT = u"""<script>
(function () {
  if (/[?&]en\\b/.test(location.search)) return;
  var langs = navigator.languages || [navigator.language || ""];
  for (var i = 0; i < langs.length; i++) {
    var l = (langs[i] || "").toLowerCase();
    if (l.indexOf("en") === 0) return;
    var to = { zh: "index-zh.html", ja: "index-ja.html", ko: "index-ko.html" }[l.slice(0, 2)];
    if (to) { location.replace(to + location.hash); return; }
  }
})();
</script>"""


def _href(code):
    return u"./?en" if code == "en" else OUT[code]


def page(app, slug, lang, desc_html):
    ui = UI[lang]
    e = html.escape
    name, sub = app["name"][lang]
    en_name = app["name"]["en"][0]
    nav = u"\n        ".join(
        u"<strong>%s</strong>" % LANG_NAME[c] if c == lang
        else u'<a href="%s">%s</a>' % (_href(c), LANG_NAME[c])
        for c in OUT)

    android, iphone = PLATFORM[lang]
    stores = []
    if app["play"]:
        stores.append(u'<a href="%s"><small>%s</small><b>Google Play</b></a>'
                      % (PLAY_URL % app["play"], android))
    else:
        stores.append(u"<span><small>%s</small><b>Google Play</b><br><small>%s</small></span>"
                      % (android, ui["soon"]))
    if app["ios"]:
        stores.append(u'<a href="%s"><small>%s</small><b>App Store</b></a>' % (app["ios"], iphone))
    else:
        stores.append(u"<span><small>%s</small><b>App Store</b><br><small>%s</small></span>"
                      % (iphone, ui["soon"]))

    if not desc_html:
        desc_html = u"<h2>%s</h2>\n<ul>%s</ul>" % (
            ui["highlights"], u"".join(u"<li>%s</li>" % p for p in app["points"][lang]))

    zh_priv, en_priv = app["privacy"]
    alts = u"\n".join(
        [u'<link rel="alternate" hreflang="%s" href="%s/%s/%s">'
         % (LANG_ATTR[c], SITE, slug, "" if OUT[c] == "index.html" else OUT[c]) for c in OUT]
        + [u'<link rel="alternate" hreflang="x-default" href="%s/%s/">' % (SITE, slug)])
    url = u"%s/%s/%s" % (SITE, slug, "" if OUT[lang] == "index.html" else OUT[lang])
    title = name if lang == "en" else u"%s %s" % (name, en_name)
    hub = u"/" if lang == "en" else u"/index-%s.html" % lang

    return u"""<!doctype html>
<html lang="%(lang_attr)s">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>%(title)s</title>
<meta name="description" content="%(line_attr)s">
<meta property="og:type" content="website">
<meta property="og:title" content="%(title)s">
<meta property="og:description" content="%(line_attr)s">
<meta property="og:image" content="%(site)s/%(slug)s/icon.png">
<meta property="og:url" content="%(url)s">
<meta name="twitter:card" content="summary">
<link rel="icon" href="icon.png">
%(alts)s
%(redirect)s
<style>
%(css)s</style>
</head>
<body>

<header>
  <div class="inner">
    <div class="bar">
      <a href="%(hub)s">&larr; Botano</a>
      <nav>
        %(nav)s
      </nav>
    </div>
    <div class="app">
      <img src="icon.png" alt="" width="76" height="76">
      <h1>%(name)s%(sub)s</h1>
    </div>
    <p class="line">%(line)s</p>
  </div>
</header>

<div class="wrap">
  <div class="stores">
    %(stores)s
  </div>

  <div class="desc">
%(desc)s
  </div>

  <footer>
    <p>%(foot)s</p>
    <p><a href="%(priv_main)s">%(privacy)s</a> &middot; <a href="%(priv_alt)s">%(privacy_alt)s</a></p>
    <p><a href="%(hub)s">%(more)s</a></p>
  </footer>
</div>
</body>
</html>
""" % {
        "lang_attr": LANG_ATTR[lang], "title": e(title), "line_attr": e(app["line"][lang]),
        "site": SITE, "slug": slug, "url": url, "alts": alts,
        "redirect": REDIRECT if lang == "en" else u"",
        "css": CSS, "hub": hub, "nav": nav, "name": name,
        "sub": u"<small>%s</small>" % sub if sub else u"",
        "line": app["line"][lang], "stores": u"\n    ".join(stores), "desc": desc_html,
        "foot": ui["foot"],
        # 隱私權政策只有中、英兩版
        "priv_main": zh_priv if lang == "zh" else en_priv,
        "privacy": ui["privacy"],
        "priv_alt": en_priv if lang == "zh" else zh_priv,
        "privacy_alt": u"English" if lang == "zh" else u"繁體中文",
        "more": ui["more"],
    }


def main():
    code_dir, pub_dir = sys.argv[1], sys.argv[2]
    for app in APPS:
        slug = app["privacy"][0].strip("/").split("/")[0]
        if slug == "botanoalarm":
            continue  # 見檔頭
        descs = descriptions(code_dir, slug)
        for lang, filename in OUT.items():
            body = to_html(descs[lang], lang) if lang in descs else u""
            path = os.path.join(pub_dir, slug, filename)
            io.open(path, "w", encoding="utf-8", newline="\n").write(page(app, slug, lang, body))
        print("%-14s 完整說明：%s" % (slug, " ".join(sorted(descs)) or "（無）"))


if __name__ == "__main__":
    main()
