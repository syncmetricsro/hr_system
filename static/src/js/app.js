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
