(function () {
  "use strict";

  document.querySelectorAll(".pub-list").forEach(function (list) {
    var count = list.querySelectorAll(".pub-item").length;
    var section = list.closest("details") || list.previousElementSibling;
    var target = section && section.querySelector("[data-pub-count]");
    if (target) {
      target.textContent = count + " " + (count === 1 ? "paper" : "papers");
    }
  });
})();
