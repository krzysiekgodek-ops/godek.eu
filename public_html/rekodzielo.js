/* Godek — Pracownia Skórzana: miniaturki + lightbox (Vanilla JS) */
(function () {
  "use strict";

  const lb = document.getElementById("lightbox");
  const lbImg = document.getElementById("lightbox-img");
  const lbCounter = document.getElementById("lightbox-counter");
  const btnClose = lb.querySelector(".lightbox__close");
  const btnPrev = lb.querySelector(".lightbox__prev");
  const btnNext = lb.querySelector(".lightbox__next");

  const pad = (n) => String(n).padStart(2, "0");

  let photos = [];   // pełne zdjęcia bieżącej kategorii
  let label = "";
  let index = 0;

  // --- Budowa miniaturek dla każdej kategorii ---
  document.querySelectorAll(".thumbs[data-cat]").forEach((grid) => {
    const cat = grid.dataset.cat;
    const count = parseInt(grid.dataset.count, 10) || 0;
    const lbl = grid.dataset.label || cat;
    for (let i = 1; i <= count; i++) {
      const btn = document.createElement("button");
      btn.type = "button";
      btn.className = "thumb";
      btn.setAttribute("aria-label", `${lbl} ${i} — powiększ`);
      const img = document.createElement("img");
      img.src = `img/skora/${cat}/t/${pad(i)}.webp`;
      img.alt = `${lbl} ${i}`;
      img.loading = "lazy";
      img.decoding = "async";
      btn.appendChild(img);
      btn.addEventListener("click", () => openGallery(cat, count, lbl, i - 1));
      grid.appendChild(btn);
    }
  });

  function openGallery(cat, count, lbl, start) {
    photos = [];
    for (let i = 1; i <= count; i++) photos.push(`img/skora/${cat}/${pad(i)}.webp`);
    label = lbl;
    index = start;
    show();
    lb.classList.add("is-open");
    lb.setAttribute("aria-hidden", "false");
    document.body.style.overflow = "hidden";
    btnClose.focus();
  }

  function show() {
    lbImg.src = photos[index];
    lbImg.alt = `${label} ${index + 1} z ${photos.length}`;
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
