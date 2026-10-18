/**
 * Раздел «Герої не вмирають».
 *
 * Список героев рендерится на сервере (Django-шаблон), поэтому скрипт только
 * улучшает готовую страницу:
 *   - мгновенный фильтр карточек прямо в DOM (без запросов к серверу);
 *   - запоминание позиции скролла и строки поиска при переходе к герою;
 *   - лайтбокс для фото на странице героя;
 *   - выпадающий переключатель языка.
 *
 * Без JavaScript страница продолжает работать: поиск отправляется формой,
 * алфавитная линейка — обычные якорные ссылки.
 */
(function () {
  "use strict";

  var SCROLL_KEY = "geroiListScrollY";
  var SEARCH_KEY = "geroiListSearch";

  /* ---------- память о позиции в списке ---------- */

  function saveListPosition(scrollY, searchText) {
    try {
      sessionStorage.setItem(SCROLL_KEY, String(scrollY));
      sessionStorage.setItem(SEARCH_KEY, searchText || "");
    } catch (e) { /* sessionStorage недоступен — просто игнорируем */ }
  }

  function readListPosition() {
    try {
      var y = sessionStorage.getItem(SCROLL_KEY);
      var q = sessionStorage.getItem(SEARCH_KEY);
      return { y: y !== null ? parseInt(y, 10) || 0 : null, q: q || "" };
    } catch (e) {
      return { y: null, q: "" };
    }
  }

  /* ---------- поиск ---------- */

  function setupSearch() {
    var input = document.getElementById("searchInput");
    var clear = document.getElementById("searchClear");
    var sections = document.getElementById("heroSections");
    var statusMsg = document.getElementById("statusMsg");
    var alphabetBar = document.getElementById("alphabetBar");
    if (!input || !sections) return;

    var sectionsList = Array.prototype.slice.call(
      sections.querySelectorAll(".letter-section")
    );

    // Заранее собираем карточки каждой секции с их поисковым текстом
    var index = sectionsList.map(function (section) {
      return {
        section: section,
        cards: Array.prototype.slice.call(section.querySelectorAll(".hero-card")).map(function (card) {
          var nameEl = card.querySelector(".name");
          return {
            card: card,
            haystack: (nameEl ? nameEl.textContent : "").trim().toLowerCase(),
          };
        }),
      };
    });

    function applyFilter(rawQuery) {
      var query = (rawQuery || "").trim().toLowerCase();
      var anyVisible = false;
      var letterHasResults = {};

      index.forEach(function (entry) {
        var visible = 0;
        entry.cards.forEach(function (item) {
          var match = !query || item.haystack.indexOf(query) !== -1;
          item.card.hidden = !match;
          if (match) visible += 1;
        });
        entry.section.hidden = visible === 0;
        if (visible > 0) {
          anyVisible = true;
          letterHasResults[entry.section.dataset.letter] = true;
        }
      });

      if (statusMsg) {
        statusMsg.hidden = anyVisible;
        if (!anyVisible) {
          statusMsg.textContent = "Нічого не знайдено. Спробуйте інше прізвище.";
        }
      }

      if (alphabetBar) {
        Array.prototype.forEach.call(alphabetBar.children, function (link) {
          link.classList.toggle("disabled", !letterHasResults[link.dataset.letter]);
        });
      }
    }

    input.addEventListener("input", function () {
      applyFilter(input.value);
      saveListPosition(window.scrollY, input.value);
    });

    if (clear) {
      clear.addEventListener("click", function (e) {
        e.preventDefault();
        input.value = "";
        applyFilter("");
        input.focus();
        saveListPosition(0, "");
      });
    }

    // Клик по карточке — запоминаем место, чтобы вернуться сюда же
    sections.addEventListener("click", function (e) {
      if (e.target.closest(".hero-card")) {
        saveListPosition(window.scrollY, input.value);
      }
    });

    var saveTimer = null;
    window.addEventListener("scroll", function () {
      if (saveTimer) return;
      saveTimer = setTimeout(function () {
        saveListPosition(window.scrollY, input.value);
        saveTimer = null;
      }, 200);
    });
    window.addEventListener("pagehide", function () {
      saveListPosition(window.scrollY, input.value);
    });

    // Строка поиска берётся из адреса (серверный поиск) либо из sessionStorage
    var saved = readListPosition();
    if (!input.value && saved.q) input.value = saved.q;
    if (input.value) applyFilter(input.value);

    if (saved.y && !input.value) {
      window.requestAnimationFrame(function () {
        window.scrollTo(0, saved.y);
      });
    }
  }

  /* ---------- лайтбокс ---------- */

  function setupLightbox() {
    var lightbox = document.getElementById("lightbox");
    if (!lightbox) return;

    var lightboxImg = document.getElementById("lightboxImg");
    var closeBtn = document.getElementById("lightboxClose");

    function open(src, alt) {
      lightboxImg.src = src;
      lightboxImg.alt = alt || "";
      lightbox.hidden = false;
      document.body.classList.add("lightbox-locked");
    }

    function close() {
      lightbox.hidden = true;
      lightboxImg.src = "";
      document.body.classList.remove("lightbox-locked");
    }

    document.addEventListener("click", function (e) {
      var img = e.target.closest(".photo-frame img, .gallery-item img");
      if (!img || !img.src) return;
      e.preventDefault();
      open(img.src, img.alt);
    });

    if (closeBtn) closeBtn.addEventListener("click", close);
    lightbox.addEventListener("click", function (e) {
      if (e.target === lightbox) close();
    });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && !lightbox.hidden) close();
    });
  }

  /* ---------- переключатель языка ---------- */

  function setupLangSwitch() {
    var wrap = document.getElementById("langSwitch");
    if (!wrap) return;

    var trigger = wrap.querySelector(".lang-current");
    if (!trigger) return;

    trigger.addEventListener("click", function (e) {
      e.preventDefault();
      e.stopPropagation();
      wrap.classList.toggle("open");
    });

    document.addEventListener("click", function (e) {
      if (!wrap.contains(e.target)) wrap.classList.remove("open");
    });
  }

  document.addEventListener("DOMContentLoaded", function () {
    setupLangSwitch();
    setupLightbox();
    setupSearch();
  });
})();
