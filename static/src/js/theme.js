/* Shared client theme controller. It runs synchronously in <head> before CSS
   loads so a stored preference never flashes the client default first. */
(function () {
  "use strict";

  var root = document.documentElement;
  var defaultTheme = root.dataset.themeDefault === "dark" ? "dark" : "light";
  var storageKey = root.dataset.themeStorageKey || "platform-theme";
  var valid = { light: true, dark: true, system: true };
  var media = window.matchMedia("(prefers-color-scheme: dark)");
  var preference = defaultTheme;

  function readPreference() {
    try {
      var stored = window.localStorage.getItem(storageKey);
      return valid[stored] ? stored : defaultTheme;
    } catch (_error) {
      return defaultTheme;
    }
  }

  function resolvedTheme(value) {
    return value === "system" ? (media.matches ? "dark" : "light") : value;
  }

  function syncControls() {
    document.querySelectorAll("[data-theme-select]").forEach(function (select) {
      select.value = preference;
    });
  }

  function applyTheme(value) {
    preference = valid[value] ? value : defaultTheme;
    var resolved = resolvedTheme(preference);
    root.classList.remove("theme-light", "theme-dark");
    root.classList.add("theme-" + resolved);
    root.dataset.themePreference = preference;
    root.dataset.themeResolved = resolved;
    root.style.colorScheme = resolved;
    syncControls();
    document.dispatchEvent(new CustomEvent("themechange", {
      detail: { preference: preference, resolved: resolved }
    }));
  }

  function storePreference(value) {
    try {
      window.localStorage.setItem(storageKey, value);
    } catch (_error) {
      // The active page still changes theme when storage is blocked.
    }
  }

  applyTheme(readPreference());

  document.addEventListener("DOMContentLoaded", syncControls);
  document.addEventListener("change", function (event) {
    if (!event.target.matches("[data-theme-select]")) return;
    var value = event.target.value;
    if (!valid[value]) return;
    storePreference(value);
    applyTheme(value);
  });

  function handleSystemChange() {
    if (preference === "system") applyTheme("system");
  }
  if (media.addEventListener) media.addEventListener("change", handleSystemChange);
  else if (media.addListener) media.addListener(handleSystemChange);

  window.addEventListener("storage", function (event) {
    if (event.key !== storageKey) return;
    applyTheme(valid[event.newValue] ? event.newValue : defaultTheme);
  });
})();
