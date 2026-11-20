# -*- coding: utf-8 -*-
"""產生 Botano 首頁的四個語言版本。

版面只有一份，文字集中在下面的表格裡——改版面只要改這支腳本，
不必在四個 HTML 之間同步。輸出到 botanodev.github.io 的根目錄。

    python gen_hub.py <輸出目錄>
"""

import io
import os
import sys

# **預設是英文**：直接開 botanodev.github.io 的人可能來自任何地方，
# 而英文是最多人至少讀得懂的那一種。中文另外一頁，切換列四種都在。
# 順序就是切換列上的順序。
OUT = {
    "en": "index.html",
    "zh": "index-zh.html",
    "ja": "index-ja.html",
    "ko": "index-ko.html",
}

LANG_ATTR = {"zh": "zh-Hant", "en": "en", "ja": "ja", "ko": "ko"}

# 語言切換列上各語言自己的名字（永遠用該語言自稱，不翻譯）。
LANG_NAME = {"zh": "中文", "en": "English", "ja": "日本語", "ko": "한국어"}

UI = {
    "zh": {
        "desc": "Botano 的 App 與商店連結。",
        "tagline": "一個人做的小工具。",
        "apps": "APP",
        "soon": "即將推出",
        "more": "說明",
        "foot": ('有問題或建議，可以在各個 App 裡的「設定 → 意見與支援」寄給我，'
                 '或寄到 <a href="mailto:botanodev@gmail.com">botanodev@gmail.com</a>。'),
    },
    "en": {
        "desc": "Botano apps and store links.",
        "tagline": "Small tools, made by one person.",
        "apps": "APPS",
        "soon": "Coming soon",
        "more": "Details",
        "foot": ('Questions or suggestions are welcome through "Settings &rarr; Feedback" '
                 'in any of the apps, or by email to '
                 '<a href="mailto:botanodev@gmail.com">botanodev@gmail.com</a>.'),
    },
    "ja": {
        "desc": "Botano のアプリとストアのリンク。",
        "tagline": "ひとりで作っている小さなツール。",
        "apps": "アプリ",
        "soon": "近日公開",
        "more": "詳細",
        "foot": ('ご質問・ご要望は各アプリの「設定 → 意見とサポート」から、'
                 'またはメール <a href="mailto:botanodev@gmail.com">botanodev@gmail.com</a> '
                 'までお送りください。'),
    },
    "ko": {
        "desc": "Botano 앱과 스토어 링크.",
        "tagline": "혼자 만드는 작은 도구들.",
        "apps": "앱",
        "soon": "출시 예정",
        "more": "자세히",
        "foot": ('문의나 제안은 각 앱의 "설정 → 의견 및 지원"에서, '
                 '또는 <a href="mailto:botanodev@gmail.com">botanodev@gmail.com</a> '
                 '으로 보내 주세요.'),
    },
}

# play：None 表示還沒公開（顯示「即將推出」而不是連結）。
# ios ：None 表示還沒上架，拿到 App Store ID 之後換成網址。
#       Play 只在封閉測試時也放 None——測試頁一般人打不開。
APPS = [
    {
        "play": "com.botano.alarm",
        "ios": None,
        "more": "/botanoalarm/",
        "name": {
            "zh": ("班表鬧鐘", "Botano Shift Work Alarm"),
            "en": ("Botano Shift Work Alarm", ""),
            "ja": ("シフト勤務アラーム", "Botano Shift Work Alarm"),
            "ko": ("교대근무 알람", "Botano Shift Work Alarm"),
        },
        "line": {
            "zh": "排班族的行事曆鬧鐘。在行事曆上標好班別，鬧鐘自己跟著班表響。",
            "en": "A calendar-driven alarm for shift workers. Mark your shifts once; "
                  "the alarms follow.",
            "ja": "シフト勤務のためのカレンダー連動アラーム。シフトを登録すれば、"
                  "あとはアラームが合わせてくれます。",
            "ko": "교대 근무자를 위한 캘린더 연동 알람. 근무표만 표시해 두면 "
                  "알람이 알아서 따라갑니다.",
        },
    },
    {
        "play": "com.botano.plantrecord",
        "ios": None,
        "more": "/plantrecord/",
        "name": {
            "zh": ("植物成長紀錄", "Plant Growth Journal"),
            "en": ("Plant Growth Journal", ""),
            "ja": ("植物の成長記録", "Plant Growth Journal"),
            "ko": ("식물 성장 기록", "Plant Growth Journal"),
        },
        "line": {
            "zh": "幫植物拍照記錄成長，匯出成一張可以分享的直式長圖。",
            "en": "Photograph your plants over time and export one tall, shareable image.",
            "ja": "植物の写真を撮りためて、縦長の一枚の画像にまとめて共有できます。",
            "ko": "식물 사진을 기록해 공유할 수 있는 세로로 긴 이미지로 내보냅니다.",
        },
    },
    {
        "play": "com.botano.tripcart",
        "ios": None,
        "more": "/tripcart/",
        "name": {
            "zh": ("出國購物計算機", "TripCart"),
            "en": ("TripCart", ""),
            "ja": ("海外ショッピング計算機", "TripCart"),
            "ko": ("해외 쇼핑 계산기", "TripCart"),
        },
        "line": {
            "zh": "在店裡就算清楚這家店要付多少本國貨幣，結帳後自動成為旅程帳本的一筆。",
            "en": "Work out what a shop really costs in your own currency, "
                  "then keep it as a trip expense.",
            "ja": "お店でその場で自国通貨の支払額を計算し、会計後はそのまま"
                  "旅の家計簿に残ります。",
            "ko": "매장에서 자국 통화로 얼마인지 바로 계산하고, 결제 후에는 "
                  "여행 가계부에 그대로 남습니다.",
        },
    },
    {
        "play": None,
        "ios": "https://apps.apple.com/app/id6835796281",
        "more": "/plushcam/",
        "name": {
            "zh": ("玩偶拍照", "PlushCam"),
            "en": ("PlushCam", ""),
            "ja": ("ぬい撮りカメラ", "PlushCam"),
            "ko": ("인형 사진", "PlushCam"),
        },
        "line": {
            "zh": "把玩偶拍一次、去背存起來，之後就能放進任何照片裡。玩偶不用帶出門，也能一起合照。",
            "en": "Photograph your plushie once, and it can join any photo you take, "
                  "even on days it stays home.",
            "ja": "ぬいを一度撮って切り抜いておけば、どんな写真にも一緒に写れます。"
                  "連れて行けない日も、ぬい撮り。",
            "ko": "인형을 한 번 찍어 배경을 지워 두면 어떤 사진에도 함께 담을 수 있습니다. "
                  "데려가지 못한 날에도 함께 찍어요.",
        },
    },
    {
        "play": "com.botano.exercisehabit",
        "ios": None,
        "more": "/exercisehabit/",
        "name": {
            "zh": ("運動習慣養成", "Exercise Habit"),
            "en": ("Exercise Habit", ""),
            "ja": ("運動習慣づくり", "Exercise Habit"),
            "ko": ("운동 습관 만들기", "Exercise Habit"),
        },
        "line": {
            "zh": "給討厭運動、容易忘記的人。每天的最低限度不到一分鐘，生病那天也做得到。",
            "en": "For people who dislike exercise and forget to start. "
                  "The daily minimum takes under a minute.",
            "ja": "運動が嫌いで忘れがちな人のために。毎日の最低ラインは一分もかかりません。",
            "ko": "운동을 싫어하고 자주 잊는 사람을 위해. 하루 최소량은 1분도 걸리지 않습니다.",
        },
    },
]

CSS = """  :root {
    --bg: #F5F7F4; --ink: #1A1D18; --muted: #4A5147; --hair: #DCE0D8;
    --brand: #5273A8; --green: #4C7A3F; --card: #FFFFFF;
    --chip: #EDF1F7; --chipink: #3C5A86;
  }
  @media (prefers-color-scheme: dark) {
    :root {
      --bg: #101410; --ink: #E2E5DC; --muted: #B3BCAC; --hair: #2B322A;
      --green: #9DD48B; --card: #171B16;
      --chip: #1C2432; --chipink: #A8C2E6;
    }
  }
  * { box-sizing: border-box; }
  body {
    margin: 0; background: var(--bg); color: var(--ink);
    font-family: system-ui, "Noto Sans TC", "Noto Sans JP", "Noto Sans KR", sans-serif;
    line-height: 1.7; -webkit-font-smoothing: antialiased;
  }
  header { background: var(--brand); color: #fff; padding: 48px 20px 40px; }
  header .inner, .wrap { max-width: 40rem; margin: 0 auto; }
  header h1 { margin: 0 0 6px; font-size: 1.9rem; letter-spacing: -.01em; }
  header p { margin: 0; color: #DCE4F2; }
  header nav { margin-top: 18px; display: flex; flex-wrap: wrap; gap: 6px; }
  header nav a, header nav strong {
    font-size: .88rem; padding: 4px 11px; border-radius: 999px;
    text-decoration: none; border: 1px solid rgba(255,255,255,.35);
  }
  header nav a { color: #DCE4F2; }
  header nav strong { background: #fff; color: var(--brand); border-color: #fff; }

  .wrap { padding: 36px 20px 72px; }
  h2 { font-size: .95rem; letter-spacing: .08em; color: var(--muted);
       margin: 0 0 14px; font-weight: 700; }

  .app {
    background: var(--card); border: 1px solid var(--hair);
    padding: 18px; margin-bottom: 14px;
  }
  .app b { display: block; font-size: 1.1rem; }
  .app .en { color: var(--muted); font-weight: 400; font-size: .95rem; }
  .app > p { margin: 4px 0 14px; color: var(--muted); font-size: .95rem; }

  .stores { display: flex; flex-wrap: wrap; gap: 8px; align-items: center; }
  .stores a, .stores span {
    display: inline-block; padding: 7px 14px; font-size: .9rem;
    border: 1px solid var(--hair); border-radius: 999px;
  }
  .stores a {
    background: var(--chip); color: var(--chipink);
    text-decoration: none; font-weight: 700; border-color: transparent;
  }
  .stores span { color: var(--muted); }
  .stores .more {
    background: none; color: var(--green); font-weight: 400;
    border-color: var(--hair); padding: 7px 12px;
  }

  footer {
    margin-top: 40px; padding-top: 20px; border-top: 1px solid var(--hair);
    color: var(--muted); font-size: .92rem;
  }
  footer a { color: var(--green); }
"""

PLAY_URL = "https://play.google.com/store/apps/details?id=%s"


def href(code):
    """該語言的網址。預設語言用 `/`，不要用 `/index.html`。"""
    return u"/" if OUT[code] == "index.html" else u"/" + OUT[code]


def nav(lang):
    out = []
    for code in OUT:
        if code == lang:
            out.append(u"<strong>%s</strong>" % LANG_NAME[code])
        else:
            out.append(u'<a href="%s">%s</a>' % (href(code), LANG_NAME[code]))
    return u"\n      ".join(out)


def card(app, lang, ui):
    zh_name, sub = app["name"][lang]
    title = zh_name if not sub else u'%s <span class="en">%s</span>' % (zh_name, sub)

    chips = []
    if app["play"]:
        chips.append(u'<a href="%s">Google Play</a>' % (PLAY_URL % app["play"]))
    else:
        chips.append(u"<span>Google Play &middot; %s</span>" % ui["soon"])
    if app["ios"]:
        chips.append(u'<a href="%s">App Store</a>' % app["ios"])
    else:
        chips.append(u"<span>App Store &middot; %s</span>" % ui["soon"])
    if app["more"]:
        chips.append(u'<a class="more" href="%s">%s</a>' % (app["more"], ui["more"]))

    return (u'  <div class="app">\n'
            u'    <b>%s</b>\n'
            u'    <p>%s</p>\n'
            u'    <div class="stores">\n      %s\n    </div>\n'
            u'  </div>\n') % (title, app["line"][lang], u"\n      ".join(chips))


def page(lang):
    ui = UI[lang]
    cards = u"\n".join(card(a, lang, ui) for a in APPS)
    # hreflang 讓搜尋引擎知道這四頁是同一頁的不同語言；x-default 指向
    # 沒有對應語言時該送到哪一頁（＝英文那頁）。
    alts = u"\n".join(
        [u'<link rel="alternate" hreflang="%s" href="https://botanodev.github.io%s">'
         % (LANG_ATTR[c], href(c)) for c in OUT]
        + [u'<link rel="alternate" hreflang="x-default" '
           u'href="https://botanodev.github.io/">']
    )
    return u"""<!doctype html>
<html lang="%s">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Botano</title>
<meta name="description" content="%s">
%s
<style>
%s</style>
</head>
<body>

<header>
  <div class="inner">
    <h1>Botano</h1>
    <p>%s</p>
    <nav>
      %s
    </nav>
  </div>
</header>

<div class="wrap">
  <h2>%s</h2>

%s
  <footer>
    <p>%s</p>
  </footer>
</div>
</body>
</html>
""" % (LANG_ATTR[lang], ui["desc"], alts, CSS, ui["tagline"], nav(lang),
       ui["apps"], cards, ui["foot"])


def main():
    out_dir = sys.argv[1]
    for lang, filename in OUT.items():
        path = os.path.join(out_dir, filename)
        io.open(path, "w", encoding="utf-8", newline="\n").write(page(lang))
        print("wrote %s" % filename)


if __name__ == "__main__":
    main()
