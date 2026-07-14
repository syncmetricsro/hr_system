window.JoberShell = {
  version: "phase-0",
};

/* Destructive-action confirmation (2026-07-11): any form or submit button
   with data-confirm="message" must pass the modal before submitting. */
(function () {
  var pending = null;
  var confirmedForms = new WeakSet();

  function getDialog() {
    return document.getElementById("confirm-dialog");
  }

  function clearPending() {
    pending = null;
    var message = document.getElementById("confirm-dialog-message");
    if (message) message.textContent = "";
  }

  document.addEventListener("submit", function (event) {
    var form = event.target;
    var submitter = event.submitter || null;
    var message =
      (submitter && submitter.dataset && submitter.dataset.confirm) ||
      (form.dataset && form.dataset.confirm);
    if (!message) return;
    if (confirmedForms.has(form)) {
      confirmedForms.delete(form);
      return;
    }

    var dialog = getDialog();
    if (!dialog || typeof dialog.showModal !== "function") {
      // Older browsers still require an explicit confirmation instead of
      // silently allowing a high-impact action.
      if (!window.confirm(message)) event.preventDefault();
      return;
    }

    event.preventDefault();
    pending = { form: form, submitter: submitter };
    document.getElementById("confirm-dialog-message").textContent = message;
    if (!dialog.open) dialog.showModal();
  }, true);

  document.addEventListener("click", function (event) {
    var dialog = getDialog();
    if (!dialog) return;
    if (event.target.closest("[data-confirm-agree]")) {
      var submission = pending;
      pending = null;
      dialog.close();
      if (submission) {
        confirmedForms.add(submission.form);
        if (submission.submitter) submission.form.requestSubmit(submission.submitter);
        else submission.form.requestSubmit();
        // If native validation prevented the second submit event, do not let
        // a later attempt bypass confirmation.
        confirmedForms.delete(submission.form);
      }
    } else if (event.target.closest("[data-confirm-cancel]")) {
      dialog.close();
    }
  });

  var dialog = getDialog();
  if (dialog) dialog.addEventListener("close", clearPending);
})();

/* Contextual tooltips. Explicit data-tooltip values and existing destructive
   data-confirm explanations are discovered through delegation so htmx swaps
   require no reinitialization. Touch input is never intercepted. */
(function () {
  var tooltip = document.getElementById("app-tooltip");
  if (!tooltip) return;

  var showTimer = null;
  var hideTimer = null;
  var activeTarget = null;
  var focusTarget = null;
  var describedTarget = null;
  var originalDescription = null;
  var pointerOverTooltip = false;
  var suppressFocusUntil = 0;

  function tooltipTarget(node) {
    if (!node || !node.closest) return null;
    var explicit = node.closest("[data-tooltip]");
    if (explicit) return explicit.matches(":disabled") ? null : explicit;

    var confirmed = node.closest("button[data-confirm], input[data-confirm], [role='button'][data-confirm]");
    if (confirmed) return confirmed.matches(":disabled") ? null : confirmed;

    var submitter = node.closest("button[type='submit'], input[type='submit'], button:not([type])");
    if (submitter && submitter.form && submitter.form.dataset.confirm) {
      return submitter.matches(":disabled") ? null : submitter;
    }
    return null;
  }

  function tooltipMessage(target) {
    if (!target) return "";
    return (
      target.dataset.tooltip ||
      target.dataset.confirm ||
      (target.form && target.form.dataset.confirm) ||
      ""
    ).trim();
  }

  function restoreDescription() {
    if (!describedTarget) return;
    if (originalDescription === null) describedTarget.removeAttribute("aria-describedby");
    else describedTarget.setAttribute("aria-describedby", originalDescription);
    describedTarget = null;
    originalDescription = null;
  }

  function describe(target) {
    restoreDescription();
    describedTarget = target;
    originalDescription = target.getAttribute("aria-describedby");
    var ids = originalDescription ? originalDescription.split(/\s+/) : [];
    if (ids.indexOf(tooltip.id) === -1) ids.push(tooltip.id);
    target.setAttribute("aria-describedby", ids.join(" ").trim());
  }

  function positionTooltip() {
    if (!activeTarget || tooltip.hidden || !activeTarget.isConnected) return;
    var targetBox = activeTarget.getBoundingClientRect();
    var tooltipBox = tooltip.getBoundingClientRect();
    var gap = 10;
    var edge = 8;
    var side = "top";
    var top = targetBox.top - tooltipBox.height - gap;

    if (top < edge) {
      side = "bottom";
      top = targetBox.bottom + gap;
    }
    top = Math.max(edge, Math.min(top, window.innerHeight - tooltipBox.height - edge));

    var targetCenter = targetBox.left + targetBox.width / 2;
    var left = targetCenter - tooltipBox.width / 2;
    left = Math.max(edge, Math.min(left, window.innerWidth - tooltipBox.width - edge));
    var arrow = Math.max(12, Math.min(targetCenter - left, tooltipBox.width - 12));

    tooltip.dataset.side = side;
    tooltip.style.left = Math.round(left) + "px";
    tooltip.style.top = Math.round(top) + "px";
    tooltip.style.setProperty("--tooltip-arrow-x", Math.round(arrow) + "px");
  }

  function show(target) {
    var message = tooltipMessage(target);
    if (!message || !target.isConnected) return;
    window.clearTimeout(hideTimer);
    if (activeTarget !== target) restoreDescription();
    activeTarget = target;
    tooltip.textContent = message;
    tooltip.hidden = false;
    describe(target);
    positionTooltip();
    window.requestAnimationFrame(function () {
      if (activeTarget === target) tooltip.classList.add("is-visible");
    });
  }

  function hide(immediate) {
    window.clearTimeout(showTimer);
    window.clearTimeout(hideTimer);
    if (!activeTarget && tooltip.hidden) return;
    var closingTarget = activeTarget;
    activeTarget = null;
    tooltip.classList.remove("is-visible");
    restoreDescription();
    var finish = function () {
      if (!activeTarget && closingTarget !== activeTarget) {
        tooltip.hidden = true;
        tooltip.textContent = "";
      }
    };
    if (immediate) finish();
    else hideTimer = window.setTimeout(finish, 120);
  }

  function scheduleShow(target, delay) {
    window.clearTimeout(showTimer);
    window.clearTimeout(hideTimer);
    if (activeTarget === target) return;
    showTimer = window.setTimeout(function () { show(target); }, delay);
  }

  document.addEventListener("pointerdown", function (event) {
    if (event.pointerType === "touch") suppressFocusUntil = Date.now() + 1000;
  }, true);

  document.addEventListener("pointerover", function (event) {
    if (event.pointerType === "touch") return;
    if (tooltip.contains(event.target)) {
      pointerOverTooltip = true;
      window.clearTimeout(hideTimer);
      return;
    }
    var target = tooltipTarget(event.target);
    if (target) scheduleShow(target, 450);
  });

  document.addEventListener("pointerout", function (event) {
    if (tooltip.contains(event.target)) {
      pointerOverTooltip = tooltip.contains(event.relatedTarget);
      if (!pointerOverTooltip && !focusTarget) hide(false);
      return;
    }
    var target = tooltipTarget(event.target);
    if (!target || target.contains(event.relatedTarget)) return;
    if (tooltip.contains(event.relatedTarget)) {
      pointerOverTooltip = true;
      return;
    }
    window.clearTimeout(showTimer);
    if (focusTarget !== target && !pointerOverTooltip) hide(false);
  });

  document.addEventListener("focusin", function (event) {
    var target = tooltipTarget(event.target);
    if (!target || Date.now() < suppressFocusUntil) return;
    focusTarget = target;
    scheduleShow(target, 0);
  });

  document.addEventListener("focusout", function (event) {
    var target = tooltipTarget(event.target);
    if (focusTarget === target) focusTarget = null;
    if (!pointerOverTooltip) hide(false);
  });

  document.addEventListener("keydown", function (event) {
    if (event.key === "Escape") hide(true);
  });
  document.addEventListener("click", function () { hide(true); }, true);
  document.addEventListener("htmx:beforeSwap", function () { hide(true); });
  window.addEventListener("scroll", function () { hide(true); }, true);
  window.addEventListener("resize", function () { hide(true); });
})();
