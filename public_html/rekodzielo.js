/* Godek — Pracownia Skórzana: galeria lightbox (Vanilla JS) */
(function () {
  "use strict";

  const lb = document.getElementById("lightbox");
  const lbImg = document.getElementById("lightbox-img");
  const lbCounter = document.getElementById("lightbox-counter");
  const btnClose = lb.querySelector(".lightbox__close");
  const btnPrev = lb.querySelector(".lightbox__prev");
  const btnNext = lb.querySelector(".lightbox__next");

  let photos = [];   // ścieżki bieżącej galerii
  let index = 0;
  let title = "";

  const pad = (n) => String(n).padStart(2, "0");

  function openGallery(cat, count, label) {
    photos = [];
    for (let i = 1; i <= count; i++) {
      photos.push(`img/skora/${cat}/${pad(i)}.webp`);
    }
    title = label || cat;
    index = 0;
    show();
    lb.classList.add("is-open");
    lb.setAttribute("aria-hidden", "false");
    document.body.style.overflow = "hidden";
    btnClose.focus();
  }

  function show() {
    lbImg.src = photos[index];
    lbImg.alt = `${title} — zdjęcie ${index + 1} z ${photos.length}`;
    lbCounter.textContent = `${index + 1} / ${photos.length}`;
  }

  function move(step) {
    index = (index + step + photos.length) % photos.length;
    show();
  }

  function close() {
    lb.classList.remove("is-open");
    lb.setAttribute("aria-hidden", "true");
    lbImg.src = "";
    document.body.style.overflow = "";
  }

  // Podpięcie kafelków z galerią (mają data-cat)
  document.querySelectorAll(".card[data-cat]").forEach((card) => {
    const cat = card.dataset.cat;
    const count = parseInt(card.dataset.count, 10) || 0;
    const label = card.querySelector("h2")?.textContent || cat;
    const activate = () => count > 0 && openGallery(cat, count, label);
    card.addEventListener("click", activate);
    card.addEventListener("keydown", (e) => {
      if (e.key === "Enter" || e.key === " ") { e.preventDefault(); activate(); }
    });
  });

  // Sterowanie lightboxem
  btnClose.addEventListener("click", close);
  btnPrev.addEventListener("click", () => move(-1));
  btnNext.addEventListener("click", () => move(1));
  lb.addEventListener("click", (e) => { if (e.target === lb) close(); });

  document.addEventListener("keydown", (e) => {
    if (!lb.classList.contains("is-open")) return;
    if (e.key === "Escape") close();
    else if (e.key === "ArrowLeft") move(-1);
    else if (e.key === "ArrowRight") move(1);
  });
})();
