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
        "details": "詳細介紹",
        "privacy": "隱私權政策",
        "foot": ('有問題或建議，可以在各個 App 裡的「設定 → 意見與支援」寄給我，'
                 '或寄到 <a href="mailto:botanodev@gmail.com">botanodev@gmail.com</a>。'),
    },
    "en": {
        "desc": "Botano apps and store links.",
        "tagline": "Small tools, made by one person.",
        "apps": "APPS",
        "soon": "Coming soon",
        "details": "Details",
        "privacy": "Privacy policy",
        "foot": ('Questions or suggestions are welcome through "Settings &rarr; Feedback" '
                 'in any of the apps, or by email to '
                 '<a href="mailto:botanodev@gmail.com">botanodev@gmail.com</a>.'),
    },
    "ja": {
        "desc": "Botano のアプリとストアのリンク。",
        "tagline": "ひとりで作っている小さなツール。",
        "apps": "アプリ",
        "soon": "近日公開",
        "details": "詳しく見る",
        "privacy": "プライバシーポリシー",
        "foot": ('ご質問・ご要望は各アプリの「設定 → 意見とサポート」から、'
                 'またはメール <a href="mailto:botanodev@gmail.com">botanodev@gmail.com</a> '
                 'までお送りください。'),
    },
    "ko": {
        "desc": "Botano 앱과 스토어 링크.",
        "tagline": "혼자 만드는 작은 도구들.",
        "apps": "앱",
        "soon": "출시 예정",
        "details": "자세히 보기",
        "privacy": "개인정보 처리방침",
        "foot": ('문의나 제안은 각 앱의 "설정 → 의견 및 지원"에서, '
                 '또는 <a href="mailto:botanodev@gmail.com">botanodev@gmail.com</a> '
                 '으로 보내 주세요.'),
    },
}

# play：None 表示還沒公開（顯示「即將推出」而不是連結）。
# ios ：None 表示還沒上架，拿到 App Store ID 之後換成網址。
#       Play 只在封閉測試時也放 None——測試頁一般人打不開。
# privacy：(中文版, 英文版)。各 App 的檔名不一致（鬧鐘的 privacy.html 是中文、
#       PlushCam 的是英文），所以逐一寫明，不要用規則拼。
#       以前這格是「說明」連到各 App 的根目錄，但只有鬧鐘那頁是真的介紹，
#       其他都只有隱私權與信箱，所以統一改成隱私權政策（2026-11-20）。
APPS = [
    {
        "play": "com.botano.alarm",
        "ios": "https://apps.apple.com/app/id6837208588",
        "privacy": ("/botanoalarm/privacy.html", "/botanoalarm/privacy-en.html"),
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
        "points": {
            "zh": ["早班、中班、晚班、休假四種班別，每顆鬧鐘只在自己的班別響",
                   "一個班別設了好幾顆鬧鐘時，「跳過整天」一次跳掉當天剩下的",
                   "台灣的國定假日與補班日自動標好，其他地區也會顯示節日名稱"],
            "en": ["Morning, afternoon, night or off: each alarm rings only on its own shift",
                   "“Skip whole day” silences the rest of a day’s alarms in one tap",
                   "Taiwan’s public holidays and make-up workdays are marked for you; "
                   "other regions show holiday names"],
            "ja": ["早番・中番・夜勤・休みの4種類。アラームは自分のシフトの日だけ鳴ります",
                   "「一日スキップ」で、その日の残りのアラームをまとめて止められます",
                   "台湾の祝日と振替出勤日は自動で反映。ほかの地域でも祝日名を表示します"],
            "ko": ["오전·오후·야간·휴무 네 가지 근무. 알람은 해당 근무일에만 울립니다",
                   "‘하루 건너뛰기’로 그날 남은 알람을 한 번에 끌 수 있습니다",
                   "대만의 공휴일과 대체 근무일은 자동으로 표시되고, 다른 지역도 공휴일 이름을 보여 줍니다"],
        },
    },
    {
        "play": "com.botano.plantrecord",
        "ios": "https://apps.apple.com/app/id6836677754",
        "privacy": ("/plantrecord/privacy-zh.html", "/plantrecord/privacy-en.html"),
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
        "points": {
            "zh": ["每張照片自動記下日期，同一株植物的變化排在一起看",
                   "一鍵做成長圖或組圖，預覽免費，做好可以直接分享",
                   "不用註冊，照片只存在你的手機裡"],
            "en": ["Every photo is dated, so one plant’s changes line up side by side",
                   "Turn them into a tall image or a grid in one tap; previews are free",
                   "No sign-up, and your photos stay on your phone"],
            "ja": ["写真には日付が自動で付き、同じ株の変化を並べて見られます",
                   "縦長の画像やグリッドをワンタップで作成。プレビューは無料です",
                   "登録不要。写真はスマホの中だけに保存されます"],
            "ko": ["사진마다 날짜가 자동으로 기록되어 한 식물의 변화를 나란히 볼 수 있습니다",
                   "세로로 긴 이미지나 그리드를 한 번에 만들 수 있고, 미리보기는 무료입니다",
                   "가입이 필요 없고, 사진은 휴대폰에만 저장됩니다"],
        },
    },
    {
        "play": "com.botano.tripcart",
        "ios": None,
        "privacy": ("/tripcart/privacy-zh.html", "/tripcart/privacy-en.html"),
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
        "points": {
            "zh": ["算進信用卡的海外手續費與回饋，在店裡就知道實際大約要付多少",
                   "旅程帳本依日期分組，有預算與圖表，可以匯出 CSV 與 PDF",
                   "日本退稅：每件商品標記 10% 或 8%，出境前列出要領的退稅"],
            "en": ["Counts your card’s foreign transaction fee and rewards, "
                   "so you see the real cost while still in the shop",
                   "A trip ledger by day, with a budget, charts and CSV/PDF export",
                   "Japan tax refund: mark items 10% or 8% and get a checklist before you fly home"],
            "ja": ["カードの海外事務手数料とポイント還元まで含めて、実際の支払額の目安をその場で表示",
                   "日付ごとの旅の家計簿。予算とグラフ、CSV・PDF 書き出しに対応",
                   "日本の免税：商品ごとに 10%・8% を記録し、出国前に受け取る免税をまとめて確認"],
            "ko": ["카드 해외 결제 수수료와 적립까지 반영해, 매장에서 실제 결제 금액을 바로 확인",
                   "날짜별 여행 가계부에 예산과 차트, CSV·PDF 내보내기까지",
                   "일본 택스리펀드: 상품마다 10%·8%를 표시하고, 출국 전에 받을 환급을 한눈에"],
        },
    },
    {
        "play": None,
        "ios": "https://apps.apple.com/app/id6835796281",
        "privacy": ("/plushcam/privacy-zh.html", "/plushcam/privacy.html"),
        "name": {
            "zh": ("玩偶拍照", "PlushCam"),
            "en": ("PlushCam", ""),
            "ja": ("ぬい撮りカメラ", "PlushCam"),
            "ko": ("인형 사진", "PlushCam"),
        },
        "line": {
            # 2026-11-22 開發者補的概念：台灣很多人把娃娃當寶貝，會裝進透明娃包掛著出門。
            # 重點是「捨不得弄髒、弄丟，但又想一起拍照」，不是「懶得帶」。
            "zh": "太寶貝的娃娃捨不得帶出門？怕弄髒、怕弄丟，就算裝進透明娃包也還是擔心。"
                  "在家把它拍一次，娃娃安心留在家，照片裡一樣有它。",
            "en": "Too precious to take outside? Afraid it gets dirty or lost, even in a clear "
                  "pouch? Photograph your plushie once at home; it stays safe there, "
                  "and still joins every photo you take.",
            "ja": "大切なぬいを汚したくない、なくしたくない。透明なぬいポーチに入れても心配。"
                  "でも一緒に写真は撮りたい。家で一度撮っておけば、ぬいはお留守番のまま、"
                  "どの写真にも一緒に写れます。",
            "ko": "소중한 인형이 더러워지거나 잃어버릴까 봐, 투명 인형 파우치에 넣어도 걱정되나요? "
                  "집에서 한 번 찍어 두면 인형은 집에서 안전하게, "
                  "사진 속에는 언제나 함께할 수 있어요.",
        },
        "points": {
            "zh": ["在素色背景前拍一次，App 自動去背；想要更多角度可以補拍側面與背面",
                   "現場拍有「手持」與「完整入鏡」兩種構圖，完整入鏡會加上淡淡的影子",
                   "以前拍好的風景照，也能事後把玩偶放進去"],
            "en": ["Shoot it once on a plain background and the app cuts it out; "
                   "add side and back views if you like",
                   "Two framings on location: hand-held, or standing in the scene with a soft shadow",
                   "Add your plushie to photos you took earlier, too"],
            "ja": ["無地の背景で一度撮れば自動で切り抜き。横や後ろの角度も追加できます",
                   "撮影時は「手持ち」と「全身」の2つの構図。全身にはやわらかな影が付きます",
                   "前に撮った風景写真にも、あとからぬいを入れられます"],
            "ko": ["단색 배경에서 한 번 찍으면 자동으로 배경을 지웁니다. 옆모습과 뒷모습도 추가할 수 있어요",
                   "현장 촬영은 ‘손에 든 구도’와 ‘전신 구도’ 두 가지. 전신에는 은은한 그림자가 생깁니다",
                   "예전에 찍은 풍경 사진에도 나중에 인형을 넣을 수 있습니다"],
        },
    },
    {
        "play": "com.botano.exercisehabit",
        "ios": "https://apps.apple.com/app/id6837182764",
        "privacy": ("/exercisehabit/privacy-zh.html", "/exercisehabit/privacy-en.html"),
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
        "points": {
            "zh": ["回答 4 個問題，30 秒挑出適合你的範本，從最容易的階段開始",
                   "每天兩個選項：慢慢變難的今日目標，和不到一分鐘的維持運動",
                   "持續 14 天、完成目標 10 次就建議升一階；做不動時也可以退回"],
            "en": ["Answer 4 questions and get a habit that fits you, starting at the easiest level",
                   "Two options every day: a goal that slowly grows, and a minimum that takes under a minute",
                   "After 14 days and 10 goals the app suggests the next level, and you can always step back"],
            "ja": ["4つの質問に答えるだけで、自分に合った習慣をいちばんやさしい段階から",
                   "毎日2つの選択肢：少しずつ上がる今日の目標と、1分かからない最低ライン",
                   "14日続けて目標を10回達成すると次の段階を提案。きついときは戻ることもできます"],
            "ko": ["4가지 질문에 답하면 나에게 맞는 습관을 가장 쉬운 단계부터 시작합니다",
                   "매일 두 가지 선택: 조금씩 어려워지는 오늘의 목표와 1분도 안 걸리는 최소량",
                   "14일 동안 목표를 10번 달성하면 다음 단계를 제안하고, 힘들 때는 한 단계 내려갈 수도 있습니다"],
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
  .app b a.name { color: var(--ink); text-decoration: none; }
  .app b a.name:hover { text-decoration: underline; }
  .app .en { color: var(--muted); font-weight: 400; font-size: .95rem; }
  .app > p { margin: 4px 0 10px; color: var(--muted); font-size: .95rem; }
  .app .points {
    margin: 0 0 14px; padding-left: 1.2em;
    color: var(--ink); font-size: .9rem; line-height: 1.6;
  }
  .app .points li { margin-bottom: 4px; }
  .app .points li::marker { color: var(--green); }

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
  .stores .detail { background: var(--brand); color: #fff; }
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
    # 名稱連到該 App 自己的介紹頁（gen_apps.py 產生，2026-11-25 起每支都有）。
    slug = app["privacy"][0].strip("/").split("/")[0]
    page = {"en": "", "zh": "index-zh.html"}.get(lang, "index-%s.html" % lang)
    if slug == "botanoalarm" and lang != "zh":
        page = "?en"  # 鬧鐘只有中、英兩版，日、韓文總網頁點進去看英文
    elif lang == "en":
        page = "?en"
    detail_href = u"/%s/%s" % (slug, page)
    title = u'<a class="name" href="%s">%s</a>' % (detail_href, title)

    # 「詳細介紹」放第一顆，跟著總網頁目前的語言：中文總網頁點進去是中文、
    # 英文點進去是英文（2026-11-25 開發者要求，原本連乾淨網址、依瀏覽器語言帶，
    # 會出現在中文總網頁點進去卻看到英文的情況）。
    # 推廣要貼的乾淨網址是 https://botanodev.github.io/<app>/，那一頁仍會依瀏覽器語言帶。
    chips = [u'<a class="detail" href="%s">%s</a>' % (detail_href, ui["details"])]
    if app["play"]:
        chips.append(u'<a href="%s">Google Play</a>' % (PLAY_URL % app["play"]))
    else:
        chips.append(u"<span>Google Play &middot; %s</span>" % ui["soon"])
    if app["ios"]:
        chips.append(u'<a href="%s">App Store</a>' % app["ios"])
    else:
        chips.append(u"<span>App Store &middot; %s</span>" % ui["soon"])
    # 隱私權政策只有中、英兩版：中文頁連中文，其他語言連英文
    zh_url, en_url = app["privacy"]
    chips.append(u'<a class="more" href="%s">%s</a>'
                 % (zh_url if lang == "zh" else en_url, ui["privacy"]))

    # 特色：一行標語之外再三點，讓沒裝過的人知道它具體能做什麼（2026-11-22 加）
    points = u"\n".join(u"      <li>%s</li>" % p for p in app["points"][lang])

    return (u'  <div class="app">\n'
            u'    <b>%s</b>\n'
            u'    <p>%s</p>\n'
            u'    <ul class="points">\n%s\n    </ul>\n'
            u'    <div class="stores">\n      %s\n    </div>\n'
            u'  </div>\n') % (title, app["line"][lang], points, u"\n      ".join(chips))


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
