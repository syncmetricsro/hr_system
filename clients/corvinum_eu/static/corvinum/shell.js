/* CorvinumEU shell: sidebar slide/collapse (ported from the peopleops
   prototype's shell.js — first-party code, no dependencies). Desktop toggles
   a collapsed icon rail (persisted); mobile toggles off-canvas + scrim. */

(function () {
  var body = document.body;
  var mq = window.matchMedia("(min-width: 1024px)");

  if (mq.matches && localStorage.getItem("pop-rail") === "1") {
    body.classList.add("rail");
  }

  document.querySelectorAll("[data-nav-toggle]").forEach(function (btn) {
    btn.addEventListener("click", function () {
      if (mq.matches) {
        body.classList.toggle("rail");
        localStorage.setItem("pop-rail", body.classList.contains("rail") ? "1" : "0");
      } else {
        body.classList.toggle("nav-open");
      }
    });
  });

  var scrim = document.querySelector(".scrim");
  if (scrim) {
    scrim.addEventListener("click", function () {
      body.classList.remove("nav-open");
    });
  }
})();
