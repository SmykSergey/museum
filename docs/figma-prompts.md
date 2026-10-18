# Промты для Figma AI

Промты для генерации дизайна страниц, которых пока нет на сайте.
Каждый блок — отдельный промт: скопировать целиком и вставить в Figma AI
(Figma Make / First Draft / любой аналогичный инструмент).

## Как пользоваться

1. Начать новый файл Figma, вставить **блок 0** (дизайн-система) — он задаёт стиль.
2. Затем вставить промт нужной страницы (блоки 1–5) — отдельным сообщением.
3. Для киоска (блоки 6–8) — **отдельный файл**, там другая сетка и другие правила.
4. Готовые макеты присылать: ссылка на Figma-файл или PNG-экспорт экранов
   1440px и 375px. По ним я сверстаю страницы в Django.

---

## 0. Дизайн-система (вставлять первым, один раз)

```
You are designing new pages for the website of the Odesa Museum of Local History
(Одеський історико-краєзнавчий музей, Ukraine). The site is in Ukrainian.

The design must look like a natural continuation of the existing pages: same palette,
same fonts, same components. Do not invent a new style.

COLORS
- Page background: #ece6da (warm cream)
- Header background: #e7e1d4, with a 40px decorative strip below it
  (repeatable ornament pattern, repeat-x)
- Card background: rgba(255,255,255,0.78) with 1px rgba(43,38,32,0.08) border
- Primary accent (buttons, active states, links): #731C1E (deep museum red)
- Accent hover: #5c1414
- Secondary accent (titles on hero pages, thin rules): #b2945e (antique gold)
- Text primary: #2b2620 / #2B2B2B
- Text secondary: #6b6355, #8a8172
- Band / filter bar background: #E1D7C8 or rgba(222,216,204,0.55)

TYPOGRAPHY
- "Open Sans" — section headings and UI labels. H1 page titles: 700, clamp(30–52px).
  Section H2: 700, 48–64px. Body text: 400, 17–20px, line-height 1.6–1.7.
- "Cormorant Infant" — navigation, quotes, elegant serif accents, 20px.
- "Inter" — small meta text, dates, breadcrumbs, 13–16px.

LAYOUT
- Content container: max-width 1500px, horizontal padding 40px (24px tablet, 16px mobile).
- Card grid: 2 columns desktop, 1 column below 1000px. Gap 26–40px.
- Border radius: 16px for cards, 7px for buttons, 30px for pill buttons/search.
- Shadows: very soft, only on interactive elements (0 4px 14px rgba(43,38,32,0.06)).

COMPONENTS ALREADY IN THE SYSTEM (reuse them, do not redesign)
- Site header: logo (70px) + title on the left; nav on the right:
  "Про музей" (with dropdown: Про музей / Запобігання корупції / Державні закупівлі),
  "Події", "Локації", "Відвідувачам", "Герої не вмирають", "Бібліотека", language
  switcher "УКР ⌄".
- Page header block: light band #e7e1d4 with page title on the left and breadcrumbs
  ("Головна / ...") on the right.
- Card: photo on the left (38% width, 1:1) + text column (date, title, 2-line summary,
  red pill button "Детальніше").
- Primary button: #731C1E, white text, radius 7px, padding 12px 24px, 18px.
- Pill / secondary button: transparent, 1px border rgba(43,43,43,0.35), radius 999px.
- Pagination: centred, "← Попередня", "Сторінка 1 з 3", "Наступна →".
- Empty state: centred muted text in a soft white panel.
- Footer strip on hero pages: "Пам'ятаємо кожного, хто віддав життя за Україну".

ACCESSIBILITY
- Minimum body font 16px. Contrast ≥ 4.5:1.
- All interactive elements ≥ 44px tall.

Deliver responsive layout for 1440px desktop, 768px tablet and 375px mobile.
All copy must be in Ukrainian.
```

---

## 1. Страница «Відвідувачам» (для посетителей)

Сейчас пункт меню есть, а страницы нет — ведёт в никуда.

```
Design the page "Відвідувачам" (Visitor information) for the museum website,
using the design system above.

PURPOSE
A visitor opens this page to plan a visit: when to come, how much a ticket costs,
how to get there, what rules apply, how to book a group tour.

PAGE STRUCTURE (top to bottom)
1. Page header block with H1 "Відвідувачам" and breadcrumbs "Головна / Відвідувачам".
2. Quick facts row — 3–4 compact cards in one line, each with a small line icon
   (clock, ticket, location pin, phone), a short label and a value:
   "Графік роботи" — "Пн–Пт: 10:00–18:00, Сб: 10:00–17:00, Нд: вихідний";
   "Квитки" — "від 30 ₴";
   "Адреса" — "вул. Гаванна, 4";
   "Телефон" — "+38 (048) 000-00-00".
3. Section "Графік роботи" — a clean two-column table (day / hours) for each of the
   4 museum locations, each location as a separate card with the location name as a link.
4. Section "Ціни на квитки" — a price table with rows: "Дорослий квиток",
   "Студентський", "Школярі", "Екскурсійне обслуговування (група до 25 осіб)",
   "Вхід для учасників бойових дій". Columns: "Категорія", "Ціна", "Примітка".
   Add a small note line under the table: "Оплата карткою або готівкою".
5. Section "Як дістатися" — a two-column block: on the left a short text
   ("Музей розташований у центрі Одеси, за 5 хвилин від Соборної площі") plus a list
   of transport ("Трамвай 3, 12; тролейбус 5 — зупинка «Гаванна»"), on the right
   an embedded map placeholder (16:9 grey block with a pin, rounded 12px).
6. Section "Правила відвідування" — a numbered list of 5–6 rules
   (не торкатися експонатів, фотозйомка без спалаху, великі сумки — у камеру
   зберігання, діти до 12 років — у супроводі дорослих).
7. Section "Екскурсії та групи" — a highlighted panel (soft white card) with text,
   a bulleted list of tour types and a primary red button "Замовити екскурсію".
8. Section "Доступність" — short block with 3 items: пандус і ліфт, тактильні копії
   експонатів, екскурсії для людей з порушеннями слуху (з перекладачем).
9. Section "Контакти" — repeat the existing contacts block from the home page:
   social icons row (Facebook, Instagram, Telegram), then venue cards with schedule
   and address.

STATES
- Provide the page with an empty-contact-phone edge case (value "—").

Do not add new navigation items. Keep the header and footer exactly as described
in the design system.
```

---

## 2. Страница «Запобігання корупції»

Пункт есть в выпадающем меню, страницы нет.

```
Design the page "Запобігання корупції" (Corruption prevention) for the museum website,
using the design system above. This is an official information page: it must look
calm, documentary and trustworthy — closer to a government site than to a poster.

PAGE STRUCTURE
1. Page header block with H1 "Запобігання корупції" and breadcrumbs
   "Головна / Про музей / Запобігання корупції".
2. Short intro paragraph (2–3 lines) explaining the museum's anti-corruption policy.
3. Document archive — the core of the page. A year filter (pill buttons:
   "Усі роки", "2026", "2025", "2024") above a list of documents.
   Each document row: date in a fixed 190px column, document title, an arrow icon.
   Rows are separated by 1px hairlines; hover tints the row slightly and moves
   the arrow 4px right. Show 5 example rows:
   "12.01.2026 — Антикорупційна програма музею на 2026 рік"
   "20.02.2026 — Звіт за результатами оцінки корупційних ризиків"
   "15.03.2025 — Порядок повідомлення про корупційні правопорушення"
   "04.06.2025 — План заходів із запобігання корупції"
   "18.11.2024 — Декларація доброчесності музею".
4. Section "Повідомити про корупцію" — a soft highlighted card with two columns:
   left — text explaining how to report, right — contact channels as icon rows:
   телефон (гаряча лінія), електронна пошта, поштова адреса, особистий прийом.
   Add a secondary outline button "Завантажити форму повідомлення".
5. Section "Уповноважена особа" — small card with a photo placeholder (1:1, 200px),
   name, position, working hours and e-mail.
6. Section "Корисні посилання" — a 2-column list of external links to
   НАЗК, НАБУ, САП, Рахункова палата (as text links with an external-link icon).

STATES
- Empty state for a year with no documents: "За цей рік документів немає."
- Hover and focus states for document rows and links.

Do not use photographs or bright colours here. Keep it typographic and restrained.
```

---

## 3. Страница «Експозиція» (список усіх експонатів)

Сейчас экспонаты видны только блоком на странице «Про музей» — нужна отдельная страница.

```
Design the page "Експозиція" (Exhibition) — a catalogue of the museum's exhibits —
using the design system above.

PURPOSE
The visitor browses the collection and opens an exhibit card for details.
The current site shows a short exhibit block on the About page; this is the full page.

PAGE STRUCTURE
1. Page header block with H1 "Експозиція" and breadcrumbs "Головна / Про музей / Експозиція".
2. Intro paragraph (2 lines) about the collection and how the items are arranged.
3. Filter bar (full-bleed band, like the procurement page search band):
   a text search field "Пошук за назвою" on the left,
   and pill buttons "Усі", "Зброя", "Археологія", "Нумізматика", "Живопис"
   on the right. The active pill is filled #731C1E with white text.
4. Exhibit grid — 3 columns on desktop, 2 on tablet, 1 on mobile.
   Each exhibit card: large photo on top (4:3, object-fit cover, rounded 12px),
   below — a gold uppercase kicker (collection name, 13px, letter-spacing 0.08em),
   the exhibit title in Open Sans 700 (22px), 2 lines of description,
   and a text link "Детальніше →" in museum red.
   Show 6 cards, using these titles:
   "Шолом типу «Моріон», XVII століття" (Зброя)
   "Амфора з розписом, IV ст. до н. е." (Археологія)
   "Одеський карбованець, 1918 рік" (Нумізматика)
   "Портрет невідомої, олія, XIX ст." (Живопис)
   "Козацька шабля, XVIII століття" (Зброя)
   "Мармуровий бюст, античність" (Археологія)
5. Pagination at the bottom (see design system).
6. A closing band with a secondary button "Повернутися на сторінку «Про музей»".

STATES
- Empty search result: "Нічого не знайдено. Спробуйте іншу назву."
- Card hover: photo scales 1.03 inside the frame, title turns #731C1E.
```

---

## 4. Раздел «Герої не вмирають» — період 2014–2021 (АТО/ООС)

На сайте сейчас только период 2022+. В киоске период выбирается отдельным экраном.

```
Design the page "Герої не вмирають" for the period 2014–2021 (АТО/ООС), using the
design system above. This page must look like a sibling of the existing 2022+ page,
which already exists on the site:
- cream background #ece6da with a faint marble texture image behind,
- gold H1 "Герої не вмирають! Одещина" (Inter 400, 56px),
- a pill search field "Введіть прізвище",
- a sticky alphabet bar on #E1D7C8 with letter links А–Я,
- hero cards in 2 columns: photo (3:4) + name, branch, dates, on rgba(255,255,255,0.78),
- a footer line "Пам'ятаємо кожного, хто віддав життя за Україну".

WHAT IS NEW — the period switcher
Add a period switch directly under the H1, before the search field:
two large pill tabs side by side, centred:
  "2014–2021 · АТО / ООС"   (active on this page)
  "2022 – .... · Повномасштабне вторгнення"
The active tab is filled #731C1E with white text; the inactive one is a transparent
pill with a 1px border. Show a short counter inside each tab:
"2014–2021 · АТО / ООС — 84" and "2022+ — 500".
Under the tabs, one line of muted explanatory text (15px, #6b6355):
"Оберіть період, щоб переглянути список героїв."

CONTENT
Show the same list layout as the 2022+ page, but with 6 example cards for 2014–2021
and the group heading "А" above them. Use placeholder names of the same style:
"Агапій Олександр Петрович", "Андрієць Ігор Вікторович", "Антіпов Дмитро Олегович",
"Атуков Віктор Миколайович", "Бацюк Андрій Сергійович", "Бароліс Олександр Іванович".
Each card must also show a small muted branch label ("Збройні Сили України",
"Добровольчі формування" etc.) in the same place where the 2022+ page shows it.

STATES
- Empty period: "За цей період записів ще немає."
- Search with no results: "Нічого не знайдено. Спробуйте інше прізвище."
- Active letter in the alphabet bar highlighted.

Deliver desktop 1440 and mobile 375. On mobile the tabs stack vertically and the
alphabet bar scrolls horizontally.
```

---

## 5. Страница 404 (необязательно, но пригодится)

```
Design a friendly 404 page for the museum website, using the design system above.

CONTENT
- Centered composition on the cream background.
- A thin gold rule above the title.
- Large title "Сторінку не знайдено" (Open Sans 700, 52px).
- One line of text: "Можливо, сторінка переїхала або адресу введено з помилкою."
- Two buttons side by side: primary red "На головну" and secondary outline
  "Герої не вмирають".
- Below, a short list "Можливо, ви шукали:" with 3 text links:
  "Новини", "Події", "Локації".
- Keep the site header and footer.
```

---

# Киоск (сенсорний стіл) — отдельный файл Figma

Правила для киоска, отличные от сайта:

```
KIOSK DESIGN CONSTRAINTS
- Fixed canvas 1280 × 1024 px. No responsiveness, no scrolling gestures.
- The table has a touch screen WITHOUT swipe support. Every scrollable area must
  have large arrow buttons (≥ 64 px) that scroll by a fixed step.
- Minimum touch target 64 × 64 px, body text ≥ 20 px, headings ≥ 40 px.
- Visual language: dark, memorial, respectful — NOT the cream website palette.
  Background #1b1b1b with a blurred military/stone photo overlay at 60–70% opacity.
  Gold accent #b2945e for headings and frames, white text #f2efe9.
  Serif font (Segoe UI / Georgia) for headings, sans for UI.
- No hover states — only "pressed" (scale 0.97) and "active" (gold border).
```

### 6. Экран «Портал» — выбор периода

```
Design a kiosk screen 1280×1024 for the museum memorial table.

TOP: museum logo (white version, 90px) on the left, title
"Одеський історико-краєзнавчий музей" in 22px white, a gold 1px line under the block.

CENTER: H1 "Меморіал Героїв" (gold #b2945e, 64px, serif, letter-spacing 0.02em).
Under it one line: "Оберіть період" (white, 24px).

Two large choice cards side by side, each 520 × 300 px, radius 16px,
background rgba(255,255,255,0.06) with 2px gold border on hover/press:
  LEFT:  "2014 – 2021" (48px white) + "АТО / ООС" (24px #b2945e) + counter "84 герої"
  RIGHT: "2022 – ...." (48px white) + "Повномасштабне вторгнення" (24px #b2945e)
         + counter "500 героїв"
Each card has a faint photo of a soldier silhouette on the right side, masked with
a gradient so text stays readable.

BOTTOM: centered line "ПАМ'ЯТАЄМО КОЖНОГО" (18px, letter-spacing 0.3em, #b2945e).

Deliver also the pressed state of both cards.
```

### 7. Экран «Вибір роду військ» + карта районів

```
Design a kiosk screen 1280×1024: choosing a military branch, with an alphabet filter
and a district map.

TOP BAR (height 80px): back arrow "←" (64×64) on the left,
H1 "Герої не вмирають! Одещина" centered in gold serif 40px.

LEFT COLUMN (width 420px, full height under the top bar):
- Search field "Введіть прізвище" (height 64, radius 999, dark with light border).
- Alphabet grid: 6 columns × 6 rows of letter buttons, each 60×60, letter 24px,
  letters А Б В Г Ґ Д Е Є Ж З И І Ї Й К Л М Н О П Р С Т У Ф Х Ц Ч Ш Щ Ь Ю Я.
  Unavailable letters are dimmed (30% opacity) and disabled.
- Below: 6 branch buttons stacked, height 64, full width, left-aligned text:
  "Збройні Сили України", "Державна прикордонна служба України",
  "Національна гвардія України", "Міністерство внутрішніх справ України",
  "Служба безпеки України", "Державна служба з надзвичайних ситуацій".
  Active branch has a 2px gold border and a small gold chevron on the right.

RIGHT AREA (860 × 900): an interactive map of Odesa oblast districts.
Show 7 district shapes in muted dark grey with 1px gold outlines and district names
inside in 18px. One district is highlighted (gold fill at 25% opacity) to show the
selected state. Above the map a hint line: "Торкніться району, щоб побачити героїв".
Under the map a compact result strip: "Обрано: Одеський район · 89 героїв"
with a gold "Показати" button 220×64.

No hover states — define default, pressed (scale 0.97) and selected (gold border) states.
```

### 8. Карточка героя в киоске

```
Design a kiosk hero card screen 1280×1024.

TOP BAR (80px): back arrow "←" (64×64), centered breadcrumb text
"Збройні Сили України · 2022+".

LEFT COLUMN (460px wide):
- Main photo in a 400×520 frame with 2px gold border, object-fit cover.
- Under the photo: a thumbnail strip of 5 thumbnails 72×72 (4 photos + 1 square
  map thumbnail labelled "Мапа району"). The active thumbnail has a gold border.
- Two big arrow buttons (72×72) on the sides of the strip for scrolling thumbnails.

RIGHT COLUMN (760px wide):
- Name: "Андрусенко Віталій Миколайович" (serif, 44px, white).
- Under it a gold line and a subtitle: "Державна прикордонна служба України · 18.05.1986 – 10.10.2024".
- Biography block: 5–6 paragraphs in 22px white on rgba(255,255,255,0.05),
  line-height 1.6, inside a fixed-height scroll area (700px) with a visible
  scrollbar track replaced by two large arrow buttons "↑ ↓" (72×72) pinned to the
  right edge of the block.

BOTTOM: a thin footer line "ПАМ'ЯТАЄМО КОЖНОГО".

Deliver also the state when the map thumbnail is selected (the main frame shows the
district map instead of the photo).
```

---

## Что прислать обратно

- Ссылку на Figma-файл (или PNG-экспорт каждого экрана в 1440px и 375px).
- Отдельно, если менялись: цвета, шрифты, отступы, радиусы — списком.
- Для новых компонентов (например, переключатель периода, карточка-тариф) —
  экспорт с отступами и состояниями (default / hover / active / disabled).

По этим макетам страницы будут свёрстаны в Django 1:1 с текущим стилем сайта.
