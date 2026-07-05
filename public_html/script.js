/* Godek — minimalny Vanilla JS */
(function () {
  "use strict";

  const root = document.documentElement;
  const toggle = document.getElementById("theme-toggle");
  const STORAGE_KEY = "godek-theme";

  // Wczytaj zapisany wybór (jeśli jest); inaczej zostaje preferencja systemowa
  const saved = localStorage.getItem(STORAGE_KEY);
  if (saved === "light" || saved === "dark") {
    root.setAttribute("data-theme", saved);
  } else {
    root.removeAttribute("data-theme"); // atrybut "auto" nie nadpisuje @media
  }

  toggle?.addEventListener("click", function () {
    const systemDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
    const current = root.getAttribute("data-theme") || (systemDark ? "dark" : "light");
    const next = current === "dark" ? "light" : "dark";
    root.setAttribute("data-theme", next);
    localStorage.setItem(STORAGE_KEY, next);
  });

  // Aktualny rok w stopce
  const yearEl = document.getElementById("year");
  if (yearEl) yearEl.textContent = new Date().getFullYear();
})();
