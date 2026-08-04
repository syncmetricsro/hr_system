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
  var tooltipHeading = tooltip.querySelector("[data-tooltip-heading]");
  var tooltipBody = tooltip.querySelector("[data-tooltip-body]");
  if (!tooltipHeading || !tooltipBody) return;

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

  function tooltipHeadingMessage(target) {
    if (!target) return "";
    return (target.dataset.tooltipHeading || "").trim();
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
    var heading = tooltipHeadingMessage(target);
    window.clearTimeout(hideTimer);
    if (activeTarget !== target) restoreDescription();
    activeTarget = target;
    tooltipHeading.textContent = heading;
    tooltipHeading.hidden = !heading;
    tooltipBody.textContent = message;
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
        tooltipHeading.textContent = "";
        tooltipHeading.hidden = true;
        tooltipBody.textContent = "";
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
    if (!focusTarget && !pointerOverTooltip) hide(false);
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
  window.addEventListener("scroll", function () {
    if (!focusTarget) {
      hide(true);
      return;
    }
    window.requestAnimationFrame(function () {
      if (!focusTarget) return;
      if (activeTarget === focusTarget) positionTooltip();
      else show(focusTarget);
    });
  }, true);
  window.addEventListener("resize", function () { hide(true); });
})();

// Period filter (J7): show only the inputs for the selected granularity.
// Progressive enhancement - without this every group stays visible and the
// form still submits correctly, because the server reads only the inputs
// belonging to the chosen `period`.
(function () {
  var forms = document.querySelectorAll("[data-period-filter]");
  if (!forms.length) return;

  forms.forEach(function (form) {
    var select = form.querySelector("[data-period-select]");
    var groups = form.querySelectorAll("[data-period-group]");
    if (!select || !groups.length) return;

    function sync() {
      groups.forEach(function (group) {
        group.hidden = group.getAttribute("data-period-group") !== select.value;
      });
    }

    // Changing the year above the checkbox grid reloads it for that year;
    // ticks are per-year, so this submits rather than filtering client-side.
    var monthsYear = form.querySelector("[data-period-months-year]");
    if (monthsYear) {
      monthsYear.addEventListener("change", function () { form.submit(); });
    }

    select.addEventListener("change", sync);
    sync();
  });
})();

// Worker status rail (J8): remember the collapsed state per browser, and start
// collapsed on narrow viewports so the rail never covers the page on arrival.
(function () {
  var rail = document.querySelector("[data-worker-rail]");
  if (!rail) return;
  var toggle = rail.querySelector("[data-worker-rail-toggle]");
  if (!toggle) return;

  var KEY = "jober-worker-rail-collapsed";
  var stored = null;
  try { stored = window.localStorage.getItem(KEY); } catch (err) { stored = null; }

  // Collapsed by default, deliberately. Expanded, the rail reserves a 20rem
  // gutter so it never covers page content - but CorvinumEU centres its main
  // column at 1280px beside a 280px sidebar, so there is no width to give away
  // without narrowing every page for a client that did not ask for the rail.
  // Opt-in keeps it one click away without imposing that cost.
  var collapsed = stored === null ? true : stored === "true";

  function apply() {
    rail.setAttribute("data-collapsed", collapsed ? "true" : "false");
    toggle.setAttribute("aria-expanded", collapsed ? "false" : "true");
  }

  // Fetch when the rail is actually opened, not on htmx's `revealed`.
  // `revealed` fires unpredictably for an element that starts hidden, and the
  // resulting swap dismisses any open tooltip (app.js hides on
  // htmx:beforeSwap) - which made an unrelated tooltip test flake in CI while
  // passing locally. An explicit event is deterministic.
  var fetched = false;
  toggle.addEventListener("click", function () {
    collapsed = !collapsed;
    try { window.localStorage.setItem(KEY, String(collapsed)); } catch (err) { /* private mode */ }
    apply();
    if (!collapsed && !fetched) {
      fetched = true;
      rail.querySelector("[hx-get]").dispatchEvent(
        new CustomEvent("workerRailOpened", { bubbles: false })
      );
    }
  });

  apply();
})();

/* Double-submit guard (2026-08-04).

   Reported against certificate upload: the file POST is slow enough to press
   the button twice, and `Certificate` carries no uniqueness constraint, so the
   second press genuinely creates a second row. Applies to every POST form
   rather than that one page, because the ledger entry, payslip and wage forms
   all create rows the same way and are exposed to the same double-click.

   Deliberately narrow about what it touches:
   * GET forms are search and filter controls - re-submitting one is harmless.
   * htmx owns its own submissions, so anything with hx-post/hx-get is skipped.
   * a submission another listener already prevented (the confirm dialog) is
     left alone; the real submit arrives later and is guarded then. */
(function () {
  var BUSY = "data-busy";

  function submitButtons(form) {
    return form.querySelectorAll(
      "button[type='submit'], input[type='submit'], button:not([type])"
    );
  }

  document.addEventListener("submit", function (event) {
    if (event.defaultPrevented) return;

    var form = event.target;
    if (!form || form.tagName !== "FORM") return;
    if ((form.getAttribute("method") || "get").toLowerCase() !== "post") return;
    if (form.hasAttribute("hx-post") || form.hasAttribute("hx-get")) return;
    if (form.hasAttribute("data-no-busy")) return;

    if (form.getAttribute(BUSY) === "true") {
      // Already in flight. Swallow the repeat rather than let it through.
      event.preventDefault();
      return;
    }
    form.setAttribute(BUSY, "true");
    form.setAttribute("aria-busy", "true");

    var buttons = submitButtons(form);
    var submitter = event.submitter;

    /* The submitter's own name/value is dropped from the request once it is
       disabled - which would post an approval with no `decision=approve` in
       it - so carry it as a hidden input first. */
    if (submitter && submitter.name) {
      var carried = document.createElement("input");
      carried.type = "hidden";
      carried.name = submitter.name;
      carried.value = submitter.value;
      form.appendChild(carried);
    }

    /* Applied synchronously, not on a timer: once the form starts navigating
       the browser may never run a queued timeout, which is exactly the window
       the second press lands in. */
    for (var i = 0; i < buttons.length; i += 1) {
      var button = buttons[i];
      if (button === submitter || buttons.length === 1) {
        button.classList.add("is-busy");
        var busyLabel = button.getAttribute("data-busy-label");
        if (busyLabel) {
          button.setAttribute("data-idle-label", button.textContent.trim());
          button.textContent = busyLabel;
        }
      }
      button.disabled = true;
    }
  });
})();
