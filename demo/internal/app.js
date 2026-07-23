(() => {
  "use strict";

  const DEFAULT_CLIENT = "corvinum";

  const themes = {
    corvinum: {
      label: "CorvinumEU",
      wordmark: "CorvinumEU",
      subtitle: "Shared HR operations"
    },
    jober: {
      label: "Jober",
      wordmark: "Jober",
      subtitle: "Licensed workforce modules"
    }
  };

  const roles = ["Recruiter", "Manager", "Coordinator", "Observer"];

  const languages = [
    { id: "en", label: "EN", name: "English" },
    { id: "sk", label: "SK", name: "Slovak" },
    { id: "hu", label: "HU", name: "Hungarian" }
  ];

  const translations = {
    sk: {
      "Language": "Jazyk",
      "Language switch": "Prepínač jazyka",
      "Client": "Klient",
      "Client switch": "Prepínač klienta",
      "Role": "Rola",
      "Role switch": "Prepínač roly",
      "Recruiter": "Náborár",
      "Manager": "Manažér",
      "Coordinator": "Koordinátor",
      "Observer": "Pozorovateľ",
      "Decisions captured": "Zachytené rozhodnutia",
      "Start guided demo": "Spustiť sprievodcu",
      "Back": "Späť",
      "Next": "Ďalej",
      "Menu": "Menu",
      "Close": "Zavrieť",
      "Workspace": "Pracovisko",
      "Core workspace": "Hlavné pracovisko",
      "Permission model": "Model oprávnení",
      "Can approve hires, verify documents, demote, blacklist, and run field actions.": "Môže schvaľovať prijatia, overovať dokumenty, meniť statusy, pridávať na čiernu listinu a robiť terénne akcie.",
      "Can create people, schedule tests, assign shifts, send pickup notices, and update document metadata.": "Môže vytvárať ľudí, plánovať skúšky, priraďovať zmeny, posielať pokyny na vyzdvihnutie a aktualizovať metadáta dokumentov.",
      "Can manage logistics only.": "Môže spravovať iba logistiku.",
      "Read-only view. Action buttons are disabled for meeting review.": "Režim iba na čítanie. Akčné tlačidlá sú vypnuté pre kontrolu na stretnutí.",
      "Live manifest": "Živý manifest",
      "Twelve-stop worker journey.": "Dvanásťkroková cesta pracovníka.",
      "Logistics-only journey.": "Iba logistická cesta.",
      "Dashboard": "Prehľad",
      "People": "Ľudia",
      "Staffing requests": "Požiadavky na obsadenie",
      "Shifts & transport": "Zmeny a doprava",
      "Documents": "Dokumenty",
      "Approvals": "Schválenia",
      "Reports": "Reporty",
      "Accommodation": "Ubytovanie",
      "Equipment": "Výstroj",
      "Pohoda dashboard": "Prehľad Pohoda",
      "Sign in": "Prihlásiť sa",
      "Manager dashboard": "Manažérsky prehľad",
      "Demand decision": "Rozhodnutie o dopyte",
      "Risk check": "Kontrola rizika",
      "Work test approval": "Schválenie pracovnej skúšky",
      "Shift + transport": "Zmena + doprava",
      "Pickup SMS": "SMS na vyzdvihnutie",
      "Second shift": "Druhá zmena",
      "Sick leave": "PN",
      "Certificate stop": "Zastavenie certifikátu",
      "Manager field view": "Terénny pohľad manažéra",
      "Become Jober": "Prepnúť na Jober",
      "Today": "Dnes",
      "Decision 1": "Rozhodnutie 1",
      "Decision 2": "Rozhodnutie 2",
      "Decision 3": "Rozhodnutie 3",
      "Mobile": "Mobil",
      "Recorded": "Zaznamenané",
      "Observer read-only": "Pozorovateľ iba číta",
      "Awaiting choice": "Čaká na výber",
      "No choice recorded yet.": "Zatiaľ nie je zaznamenaný výber.",
      "Help us confirm how you actually work": "Pomôžte nám potvrdiť, ako naozaj pracujete",
      "Person": "Osoba",
      "Country": "Krajina",
      "Status": "Status",
      "Document state": "Stav dokumentu",
      "Contact": "Kontakt",
      "Worker": "Pracovník",
      "Worksite": "Pracovisko",
      "Shift": "Zmena",
      "Transport": "Doprava",
      "Demand model": "Model dopytu",
      "How does a partner request become work?": "Ako sa požiadavka partnera zmení na prácu?",
      "Order-driven": "Podľa objednávky",
      "The partner request exists as an order record. Recruiters fill it by assigning workers to shifts.": "Požiadavka partnera existuje ako objednávka. Náborári ju plnia priraďovaním pracovníkov na zmeny.",
      "Shift-driven": "Podľa zmien",
      "Recruiters create dated shifts directly. There is no separate order object.": "Náborári vytvárajú dátumované zmeny priamo. Samostatná objednávka neexistuje.",
      "Transport capacity": "Kapacita dopravy",
      "What happens when the bus is full?": "Čo sa stane, keď je autobus plný?",
      "Enforce capacity": "Vynútiť kapacitu",
      "Block new assignments once the bus reaches capacity.": "Blokovať nové priradenia, keď autobus dosiahne kapacitu.",
      "Client decision: enforce capacity": "Rozhodnutie klienta: vynútiť kapacitu",
      "Vehicle-specific capacity is enforced. A full vehicle blocks new assignments.": "Kapacita sa vynucuje podľa konkrétneho vozidla. Plné vozidlo blokuje nové priradenia.",
      "Transport logistics view: assigned worksite, dated shift, vehicle, pickup point, and time.": "Logistický pohľad dopravy: priradené pracovisko, dátumovaná zmena, vozidlo, miesto vyzdvihnutia a čas.",
      "Certificate storage": "Ukladanie certifikátov",
      "What should be stored for certificates?": "Čo sa má ukladať pri certifikátoch?",
      "Dates only": "Iba dátumy",
      "Store certificate type, issue date, expiry date, and valid/invalid status. No file is retained.": "Uložiť typ certifikátu, dátum vydania, dátum expirácie a stav platný/neplatný. Súbor sa neuchováva.",
      "Client decision: metadata only": "Rozhodnutie klienta: iba metadáta",
      "Certificate records store type, issue date, expiry date, and valid/invalid status. No file is retained.": "Záznamy certifikátov ukladajú typ, dátum vydania, dátum expirácie a stav platný/neplatný. Súbor sa neuchováva.",
      "Hired": "Prijatý",
      "Recruit": "Kandidát",
      "Archived": "Archivovaný",
      "Blacklisted": "Na čiernej listine",
      "Working": "Pracuje",
      "Available": "Dostupný",
      "Inactive": "Neaktívny",
      "Draft": "Návrh",
      "Planned": "Plánované",
      "Assigned": "Priradené",
      "Cancelled": "Zrušené"
    },
    hu: {
      "Language": "Nyelv",
      "Language switch": "Nyelvváltó",
      "Client": "Ügyfél",
      "Client switch": "Ügyfélváltó",
      "Role": "Szerep",
      "Role switch": "Szerepváltó",
      "Recruiter": "Toborzó",
      "Manager": "Vezető",
      "Coordinator": "Koordinátor",
      "Observer": "Megfigyelő",
      "Decisions captured": "Rögzített döntések",
      "Start guided demo": "Vezetett demó indítása",
      "Back": "Vissza",
      "Next": "Tovább",
      "Menu": "Menü",
      "Close": "Bezárás",
      "Workspace": "Munkaterület",
      "Core workspace": "Fő munkaterület",
      "Permission model": "Jogosultsági modell",
      "Can approve hires, verify documents, demote, blacklist, and run field actions.": "Jóváhagyhat felvételeket, ellenőrizhet dokumentumokat, módosíthat státuszt, tiltólistázhat és terepi műveleteket végezhet.",
      "Can create people, schedule tests, assign shifts, send pickup notices, and update document metadata.": "Létrehozhat dolgozókat, teszteket ütemezhet, műszakokat oszthat be, felvételi értesítést küldhet és dokumentummetaadatokat frissíthet.",
      "Can manage logistics only.": "Csak logisztikát kezelhet.",
      "Read-only view. Action buttons are disabled for meeting review.": "Csak olvasható nézet. A műveleti gombok ki vannak kapcsolva a megbeszéléshez.",
      "Live manifest": "Élő manifest",
      "Twelve-stop worker journey.": "Tizenkét lépéses dolgozói út.",
      "Logistics-only journey.": "Csak logisztikai út.",
      "Dashboard": "Áttekintés",
      "People": "Dolgozók",
      "Staffing requests": "Munkaerőigények",
      "Shifts & transport": "Műszakok és szállítás",
      "Documents": "Dokumentumok",
      "Approvals": "Jóváhagyások",
      "Reports": "Jelentések",
      "Accommodation": "Szállás",
      "Equipment": "Felszerelés",
      "Pohoda dashboard": "Pohoda áttekintés",
      "Sign in": "Bejelentkezés",
      "Manager dashboard": "Vezetői áttekintés",
      "Demand decision": "Igénydöntés",
      "Risk check": "Kockázatellenőrzés",
      "Work test approval": "Próbanap jóváhagyása",
      "Shift + transport": "Műszak + szállítás",
      "Pickup SMS": "Felvételi SMS",
      "Second shift": "Második műszak",
      "Sick leave": "Betegszabadság",
      "Certificate stop": "Tanúsítvány stop",
      "Manager field view": "Vezetői terepi nézet",
      "Become Jober": "Váltás Joberre",
      "Today": "Ma",
      "Decision 1": "1. döntés",
      "Decision 2": "2. döntés",
      "Decision 3": "3. döntés",
      "Mobile": "Mobil",
      "Recorded": "Rögzítve",
      "Observer read-only": "Megfigyelő csak olvas",
      "Awaiting choice": "Választásra vár",
      "No choice recorded yet.": "Még nincs rögzített választás.",
      "Help us confirm how you actually work": "Segítsen megerősíteni, hogyan dolgoznak valójában",
      "Person": "Személy",
      "Country": "Ország",
      "Status": "Státusz",
      "Document state": "Dokumentumállapot",
      "Contact": "Kapcsolat",
      "Worker": "Dolgozó",
      "Worksite": "Munkaterület",
      "Shift": "Műszak",
      "Transport": "Szállítás",
      "Demand model": "Igénymodell",
      "How does a partner request become work?": "Hogyan lesz a partneri igényből munka?",
      "Order-driven": "Megrendelés-alapú",
      "The partner request exists as an order record. Recruiters fill it by assigning workers to shifts.": "A partneri igény megrendelésként létezik. A toborzók dolgozókat osztanak műszakokra.",
      "Shift-driven": "Műszak-alapú",
      "Recruiters create dated shifts directly. There is no separate order object.": "A toborzók közvetlenül dátumozott műszakokat hoznak létre. Nincs külön megrendelésobjektum.",
      "Transport capacity": "Szállítási kapacitás",
      "What happens when the bus is full?": "Mi történik, ha a busz megtelt?",
      "Enforce capacity": "Kapacitás betartása",
      "Block new assignments once the bus reaches capacity.": "Új beosztások blokkolása, ha a busz eléri a kapacitást.",
      "Client decision: enforce capacity": "Ügyféldöntés: kapacitás betartása",
      "Vehicle-specific capacity is enforced. A full vehicle blocks new assignments.": "A kapacitás járművenként érvényesül. A megtelt jármű blokkolja az új beosztásokat.",
      "Transport logistics view: assigned worksite, dated shift, vehicle, pickup point, and time.": "Szállítási logisztikai nézet: hozzárendelt munkaterület, dátumozott műszak, jármű, felvételi pont és idő.",
      "Certificate storage": "Tanúsítványtárolás",
      "What should be stored for certificates?": "Mit kell tárolni a tanúsítványoknál?",
      "Dates only": "Csak dátumok",
      "Store certificate type, issue date, expiry date, and valid/invalid status. No file is retained.": "A tanúsítvány típusának, kiadási dátumának, lejárati dátumának és érvényes/érvénytelen státuszának tárolása. Fájl nem marad meg.",
      "Client decision: metadata only": "Ügyféldöntés: csak metaadatok",
      "Certificate records store type, issue date, expiry date, and valid/invalid status. No file is retained.": "A tanúsítványrekordok típust, kiadási dátumot, lejárati dátumot és érvényes/érvénytelen státuszt tárolnak. Fájl nem marad meg.",
      "Hired": "Felvéve",
      "Recruit": "Jelölt",
      "Archived": "Archivált",
      "Blacklisted": "Tiltólistás",
      "Working": "Dolgozik",
      "Available": "Elérhető",
      "Inactive": "Inaktív",
      "Draft": "Vázlat",
      "Planned": "Tervezett",
      "Assigned": "Beosztva",
      "Cancelled": "Törölve"
    }
  };

  const recruiterPermissions = new Set([
    "createPerson",
    "scheduleTest",
    "recommendHire",
    "assignShift",
    "sendSms",
    "recordSickLeave",
    "uploadDocs"
  ]);

  const navItems = [
    { id: "dashboard", label: "Dashboard", icon: "D", view: "dashboard" },
    { id: "people", label: "People", icon: "P", view: "people" },
    { id: "requests", label: "Staffing requests", icon: "R", view: "requests" },
    { id: "shifts", label: "Shifts & transport", icon: "S", view: "shifts" },
    { id: "documents", label: "Documents", icon: "C", view: "documents" },
    { id: "approvals", label: "Approvals", icon: "A", view: "approvals" },
    { id: "reports", label: "Reports", icon: "T", view: "reports" },
    { id: "accommodation", label: "Accommodation", icon: "H", view: "accommodation", joberOnly: true },
    { id: "equipment", label: "Equipment", icon: "E", view: "equipment", joberOnly: true },
    { id: "pohoda", label: "Pohoda dashboard", icon: "X", view: "pohoda", joberOnly: true }
  ];

  const tourSteps = [
    { id: "login", label: "Sign in", view: "login", meta: "Auth facade" },
    { id: "dashboard", label: "Manager dashboard", view: "dashboard", meta: "Today" },
    { id: "demand", label: "Demand decision", view: "requests", meta: "Decision 1" },
    { id: "risk", label: "Risk check", view: "people", meta: "Blacklist gate" },
    { id: "approval", label: "Work test approval", view: "approvals", meta: "Role switch" },
    { id: "transport", label: "Shift + transport", view: "shifts", meta: "Decision 2" },
    { id: "sms", label: "Pickup SMS", view: "sms", meta: "Fake send" },
    { id: "second-shift", label: "Second shift", view: "second-shift", meta: "Same day" },
    { id: "sick", label: "Sick leave", view: "sick-leave", meta: "Dates only" },
    { id: "cert", label: "Certificate stop", view: "documents", meta: "Decision 3" },
    { id: "field", label: "Manager field view", view: "field", meta: "Mobile" },
    { id: "jober", label: "Become Jober", view: "jober-finale", meta: "Modules" }
  ];

  const decisions = {
    demand: {
      title: "Demand model",
      question: "How does a partner request become work?",
      options: {
        A: {
          label: "Order-driven",
          body: "The partner request exists as an order record. Recruiters fill it by assigning workers to shifts."
        },
        B: {
          label: "Shift-driven",
          body: "Recruiters create dated shifts directly. There is no separate order object."
        }
      }
    },
    transport: {
      title: "Transport capacity",
      question: "What happens when the bus is full?",
      options: {
        A: {
          label: "Enforce capacity",
          body: "Block new assignments once the bus reaches capacity."
        }
      }
    },
    cert: {
      title: "Certificate storage",
      question: "What should be stored for certificates?",
      options: {
        B: {
          label: "Dates only",
          body: "Store certificate type, issue date, expiry date, and valid/invalid status. No file is retained."
        }
      }
    }
  };

  const mockData = {
    partner: {
      name: "Stavby Nitra s.r.o.",
      requestId: "REQ-2026-0616-A",
      workersNeeded: 12,
      worksite: "Worksite A - Nitra warehouse",
      date: "Tuesday, 16 Jun 2026",
      position: "General laborer"
    },
    worksites: [
      { id: "nitra", label: "Worksite A - Nitra warehouse", address: "Logisticka 14, Nitra" },
      { id: "trnava", label: "Worksite B - Trnava site", address: "Priemyselna 8, Trnava" }
    ],
    positions: [
      { label: "General laborer", requiredCert: "None" },
      { label: "Warehouse picker", requiredCert: "None" },
      { label: "Forklift operator", requiredCert: "Forklift certificate" }
    ],
    buses: [
      { id: "bus1", label: "Bus 1", capacity: 15, booked: 11, driver: "Marek H.", pickup: "Trnava station", time: "10:40" },
      { id: "bus2", label: "Bus 2", capacity: 9, booked: 8, driver: "Tomas V.", pickup: "Nitra depot", time: "06:15" }
    ],
    people: [
      {
        id: "olha",
        name: "Olha Tkachenko",
        scriptName: "Ольга Ткаченко",
        country: "Ukraine",
        phone: "+421 900 222 014",
        hireStatus: "Hired",
        availability: "Working",
        document: "Work permit expires in 18 days",
        room: "Room 12",
        sizes: "Shirt M / trousers 40 / boots 39",
        equipment: "Vest, helmet, gloves"
      },
      {
        id: "bohdan",
        name: "Bohdan Marchenko",
        scriptName: "Богдан Марченко",
        country: "Ukraine",
        phone: "+421 900 441 118",
        hireStatus: "Blacklisted",
        availability: "Inactive",
        document: "Archived",
        room: "None",
        sizes: "Not recorded",
        equipment: "Returned",
        blacklistReason: "Repeated no-show"
      },
      {
        id: "farrukh",
        name: "Farrukh Yusupov",
        scriptName: "Фаррух Юсупов",
        country: "Uzbekistan",
        phone: "+421 900 873 331",
        hireStatus: "Hired",
        availability: "Available",
        document: "Forklift cert expires 25 Jun 2026",
        room: "Room 14",
        sizes: "Shirt L / trousers 42 / boots 43",
        equipment: "Helmet, boots",
        certificate: {
          type: "Forklift certificate",
          expires: "25 Jun 2026",
          daysLeft: 12
        }
      },
      {
        id: "tran",
        name: "Tran Van Minh",
        scriptName: "Tran Van Minh",
        country: "Vietnam",
        phone: "+421 900 730 822",
        hireStatus: "Recruit",
        availability: "Available",
        document: "Test scheduled",
        room: "None",
        sizes: "Shirt S / trousers 38 / boots 40",
        equipment: "Pending issue"
      },
      {
        id: "dilnoza",
        name: "Dilnoza Karimova",
        scriptName: "Дилноза Каримова",
        country: "Uzbekistan",
        phone: "+421 900 611 203",
        hireStatus: "Hired",
        availability: "Available",
        document: "Residence card valid",
        room: "Room 12",
        sizes: "Shirt S / trousers 36 / boots 38",
        equipment: "Vest, gloves"
      },
      {
        id: "mykola",
        name: "Mykola Hrytsenko",
        scriptName: "Микола Гриценко",
        country: "Ukraine",
        phone: "+421 900 511 290",
        hireStatus: "Archived",
        availability: "Inactive",
        document: "Profile archived",
        room: "None",
        sizes: "Shirt XL / trousers 46 / boots 44",
        equipment: "Returned"
      }
    ],
    rooms: [
      { room: "Room 12", occupancy: "3/4 beds", workers: "Olha Tkachenko, Dilnoza Karimova, Milan K." },
      { room: "Room 14", occupancy: "2/4 beds", workers: "Farrukh Yusupov, Azizbek R." },
      { room: "Room 18", occupancy: "4/4 beds", workers: "Full" }
    ],
    equipment: [
      { worker: "Olha Tkachenko", item: "Helmet", status: "Issued", size: "Standard" },
      { worker: "Farrukh Yusupov", item: "Boots", status: "Issued", size: "43" },
      { worker: "Tran Van Minh", item: "Vest", status: "Prepared", size: "S" },
      { worker: "Mykola Hrytsenko", item: "Gloves", status: "Returned", size: "L" }
    ]
  };

  const state = {
    signedIn: false,
    client: DEFAULT_CLIENT,
    language: "en",
    role: "Manager",
    view: "login",
    currentStep: 0,
    navOpen: false,
    manifestOpen: false,
    decisionsOpen: false,
    decisionChoices: {
      demand: null,
      transport: "A",
      cert: "B"
    },
    riskInput: "Bohdan Marchenko",
    bohdanFlagSaved: false,
    testScheduled: true,
    testRecommended: false,
    tranApproved: false,
    shiftAssigned: false,
    smsSent: false,
    secondShiftAdded: false,
    sickLeaveRecorded: false,
    certAssignmentTried: false,
    noShowMarked: false,
    auditLog: [
      { time: "08:05", text: "Dashboard opened for today's staffing picture." },
      { time: "08:18", text: "Forklift certificate alert queued for Farrukh Yusupov." },
      { time: "08:27", text: "Blacklist review queue contains one returnee." }
    ]
  };

  const root = document.getElementById("app");
  const coordinatorCoreViews = new Set(["shifts", "sms", "second-shift"]);
  const coordinatorJoberViews = new Set(["accommodation", "equipment"]);
  const coordinatorPermissions = new Set(["assignShift", "sendSms"]);
  const lockedDecisions = {
    transport: "A",
    cert: "B"
  };

  function t(value) {
    return translations[state.language]?.[value] || value;
  }

  function escapeHtml(value) {
    return String(value)
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#39;");
  }

  function getPerson(id) {
    return mockData.people.find((person) => person.id === id);
  }

  function setPerson(id, changes) {
    const target = getPerson(id);
    if (target) {
      Object.assign(target, changes);
    }
  }

  function nowTime() {
    return new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
  }

  function addAudit(text) {
    state.auditLog.unshift({ time: nowTime(), text });
  }

  function isCoordinator() {
    return state.role === "Coordinator";
  }

  function coordinatorDefaultView() {
    return "shifts";
  }

  function isCoordinatorJoberView(view) {
    return coordinatorJoberViews.has(view);
  }

  function isViewAllowed(view) {
    if (!isCoordinator()) {
      return true;
    }
    return coordinatorCoreViews.has(view) || (state.client === "jober" && isCoordinatorJoberView(view));
  }

  function normalizeRoleView() {
    if (state.view === "login") {
      return;
    }
    if (!isViewAllowed(state.view)) {
      state.view = coordinatorDefaultView();
    }
    const stepIndex = tourSteps.findIndex((step) => step.view === state.view);
    if (stepIndex >= 0) {
      state.currentStep = stepIndex;
    }
  }

  function visibleNavItems() {
    return navItems.filter((item) => {
      if (item.joberOnly && state.client !== "jober") {
        return false;
      }
      return isViewAllowed(item.view);
    });
  }

  function visibleTourSteps() {
    return tourSteps.filter((step) => !isCoordinator() || step.view === "login" || isViewAllowed(step.view));
  }

  function currentVisibleStepIndex() {
    return visibleTourSteps().findIndex((step) => step.view === state.view);
  }

  function can(permission) {
    if (state.role === "Observer") {
      return false;
    }
    if (state.role === "Manager") {
      return true;
    }
    if (isCoordinator()) {
      return coordinatorPermissions.has(permission);
    }
    return recruiterPermissions.has(permission);
  }

  function actionButton(permission, action, label, className = "primary-button", extra = "") {
    const disabled = permission && !can(permission);
    const displayLabel = t(label);
    const title = disabled ? `Current role cannot ${displayLabel.toLowerCase()}.` : "";
    return `
      <button class="${className}" data-action="${action}" ${extra} ${disabled ? "disabled" : ""} title="${escapeHtml(title)}">
        ${escapeHtml(displayLabel)}
      </button>
    `;
  }

  function statusBadges(person) {
    return `
      <span class="badge hire-${person.hireStatus.toLowerCase()}">${escapeHtml(t(person.hireStatus))}</span>
      <span class="badge availability-${person.availability.toLowerCase()}">${escapeHtml(t(person.availability))}</span>
    `;
  }

  function renderTopbar() {
    const theme = themes[state.client];
    const canOpenNav = state.view !== "login";
    return `
      <header class="topbar">
        <button class="brand ghost-button" data-action="go-step" data-step="1" aria-label="Go to dashboard">
          <span class="brand-mark" aria-hidden="true">
            <img src="assets/${state.client === "jober" ? "jober-logo.png" : "corvinum-logo.png"}" alt="${escapeHtml(theme.wordmark)}" class="brand-logo-img">
          </span>
          <span class="brand-text">
            <span class="brand-name">${escapeHtml(theme.wordmark)}</span>
            <span class="brand-subtitle">${escapeHtml(theme.subtitle)}</span>
          </span>
        </button>
        ${renderClientSwitch("desktop-control")}
        ${renderRoleSwitch("desktop-control")}
        ${renderLanguageSwitch("desktop-control")}
        <div class="topbar-group topbar-demo desktop-control">
          <button class="toolbar-button" data-action="toggle-decisions">${escapeHtml(t("Decisions captured"))}</button>
          <button class="toolbar-button" data-action="start-demo">${escapeHtml(t("Start guided demo"))}</button>
          <button class="toolbar-button" data-action="prev-step" ${state.currentStep === 0 ? "disabled" : ""}>${escapeHtml(t("Back"))}</button>
          <button class="toolbar-button" data-action="next-step" ${nextIsDisabled() ? "disabled" : ""}>${escapeHtml(t("Next"))}</button>
          <span class="avatar" aria-label="Presenter avatar">${state.role.slice(0, 2).toUpperCase()}</span>
        </div>
        <div class="mobile-top-actions">
          ${canOpenNav ? `<button class="toolbar-button icon-button" data-action="toggle-nav" aria-expanded="${state.navOpen}" aria-controls="mobile-nav">${escapeHtml(t("Menu"))}</button>` : ""}
          <button class="toolbar-button compact-button" data-action="toggle-decisions">${escapeHtml(t("Decisions captured"))}</button>
          <span class="avatar" aria-label="Presenter avatar">${state.role.slice(0, 2).toUpperCase()}</span>
        </div>
      </header>
    `;
  }

  function renderClientSwitch(extraClass = "") {
    return `
      <div class="topbar-group ${extraClass}" aria-label="${escapeHtml(t("Client switch"))}">
        <span class="control-label">${escapeHtml(t("Client"))}</span>
        <span class="segmented">
          ${Object.entries(themes).map(([id, item]) => `
            <button class="segmented-button ${state.client === id ? "is-active" : ""}" data-action="set-client" data-client="${id}" aria-pressed="${state.client === id}">
              ${escapeHtml(item.label)}
            </button>
          `).join("")}
        </span>
      </div>
    `;
  }

  function renderRoleSwitch(extraClass = "") {
    return `
      <div class="topbar-group ${extraClass}" aria-label="${escapeHtml(t("Role switch"))}">
        <span class="control-label">${escapeHtml(t("Role"))}</span>
        <span class="segmented">
          ${roles.map((role) => `
            <button class="segmented-button ${state.role === role ? "is-active" : ""}" data-action="set-role" data-role="${role}" aria-pressed="${state.role === role}">
              ${escapeHtml(t(role))}
            </button>
          `).join("")}
        </span>
      </div>
    `;
  }

  function renderLanguageSwitch(extraClass = "") {
    return `
      <div class="topbar-group ${extraClass}" aria-label="${escapeHtml(t("Language switch"))}">
        <span class="control-label">${escapeHtml(t("Language"))}</span>
        <span class="segmented">
          ${languages.map((language) => `
            <button class="segmented-button ${state.language === language.id ? "is-active" : ""}" data-action="set-language" data-language="${language.id}" aria-pressed="${state.language === language.id}" title="${escapeHtml(language.name)}">
              ${escapeHtml(language.label)}
            </button>
          `).join("")}
        </span>
      </div>
    `;
  }

  function nextIsDisabled() {
    const steps = visibleTourSteps();
    const visibleIndex = currentVisibleStepIndex();
    if (visibleIndex < 0 || visibleIndex === steps.length - 1) {
      return true;
    }
    const step = tourSteps[state.currentStep];
    if (step.id === "demand") {
      return !state.decisionChoices.demand;
    }
    return false;
  }

  function renderSidebar() {
    const visibleItems = visibleNavItems();
    return `
      <div class="nav-backdrop ${state.navOpen ? "is-open" : ""}" data-action="close-nav" aria-hidden="true"></div>
      <aside class="sidebar ${state.navOpen ? "is-open" : ""}" id="mobile-nav">
        <div class="drawer-header nav-drawer-header">
          <strong>${escapeHtml(t("Workspace"))}</strong>
          <button class="ghost-button" data-action="close-nav">${escapeHtml(t("Close"))}</button>
        </div>
        <div class="drawer-controls">
          ${renderClientSwitch("drawer-control")}
          ${renderRoleSwitch("drawer-control")}
          ${renderLanguageSwitch("drawer-control")}
          <button class="secondary-button" data-action="start-demo">${escapeHtml(t("Start guided demo"))}</button>
        </div>
        <div class="nav-section-label">${escapeHtml(t("Core workspace"))}</div>
        <nav class="nav-list" aria-label="Primary">
          ${visibleItems.map((item) => `
            <button class="nav-button ${state.view === item.view ? "is-active" : ""}" data-action="nav" data-view="${item.view}">
              <span class="nav-icon" aria-hidden="true">${escapeHtml(item.icon)}</span>
              <span>${escapeHtml(t(item.label))}</span>
            </button>
          `).join("")}
        </nav>
        <div class="nav-section-label">${escapeHtml(t("Permission model"))}</div>
        <div class="callout">
          <strong>${escapeHtml(t(state.role))}</strong>
          <p class="muted">${escapeHtml(roleDescription())}</p>
        </div>
      </aside>
    `;
  }

  function roleDescription() {
    if (state.role === "Manager") {
      return t("Can approve hires, verify documents, demote, blacklist, and run field actions.");
    }
    if (state.role === "Recruiter") {
      return t("Can create people, schedule tests, assign shifts, send pickup notices, and update document metadata.");
    }
    if (isCoordinator()) {
      return t("Can manage logistics only.");
    }
    return t("Read-only view. Action buttons are disabled for meeting review.");
  }

  function renderManifestRail() {
    const steps = visibleTourSteps();
    return `
      <aside class="manifest-rail" aria-label="Guided demo manifest">
        <h2 class="rail-title">${escapeHtml(t("Live manifest"))}</h2>
        <p class="rail-subtitle">${escapeHtml(t(isCoordinator() ? "Logistics-only journey." : "Twelve-stop worker journey."))}</p>
        <div class="rail-steps">
          ${steps.map((step) => {
            const index = tourSteps.indexOf(step);
            const done = index < state.currentStep;
            const current = index === state.currentStep;
            return `
              <button class="rail-step ${done ? "is-done" : ""} ${current ? "is-current" : ""}" data-action="go-step" data-step="${index}" aria-current="${current ? "step" : "false"}">
                <span class="rail-index">${String(index + 1).padStart(2, "0")}</span>
                <span class="rail-copy">
                  <span class="rail-label">${escapeHtml(t(step.label))}</span>
                  <span class="rail-meta">${escapeHtml(t(step.meta))}</span>
                </span>
              </button>
            `;
          }).join("")}
        </div>
      </aside>
    `;
  }

  function renderMobileManifest() {
    const steps = visibleTourSteps();
    const current = tourSteps[state.currentStep];
    const visibleIndex = Math.max(0, currentVisibleStepIndex());
    return `
      <section class="mobile-manifest ${state.manifestOpen ? "is-open" : ""}" aria-label="Guided demo progress">
        <div class="mobile-manifest-top">
          <button class="manifest-toggle" data-action="toggle-manifest" aria-expanded="${state.manifestOpen}">
            <span class="rail-index">${String(state.currentStep + 1).padStart(2, "0")}</span>
            <span class="rail-copy">
              <span class="rail-label">${escapeHtml(t(current.label))}</span>
              <span class="rail-meta">${escapeHtml(t(current.meta))} · ${visibleIndex + 1} / ${steps.length}</span>
            </span>
            <span class="manifest-caret" aria-hidden="true">${state.manifestOpen ? escapeHtml(t("Close")) : escapeHtml(t("Menu"))}</span>
          </button>
          <div class="mobile-tour-actions">
            <button class="toolbar-button" data-action="prev-step" ${state.currentStep === 0 ? "disabled" : ""}>${escapeHtml(t("Back"))}</button>
            <button class="toolbar-button" data-action="next-step" ${nextIsDisabled() ? "disabled" : ""}>${escapeHtml(t("Next"))}</button>
          </div>
        </div>
        <div class="mobile-rail-steps">
          ${steps.map((step) => {
            const index = tourSteps.indexOf(step);
            const done = index < state.currentStep;
            const currentStep = index === state.currentStep;
            return `
              <button class="rail-step ${done ? "is-done" : ""} ${currentStep ? "is-current" : ""}" data-action="go-step" data-step="${index}" aria-current="${currentStep ? "step" : "false"}">
                <span class="rail-index">${String(index + 1).padStart(2, "0")}</span>
                <span class="rail-copy">
                  <span class="rail-label">${escapeHtml(t(step.label))}</span>
                  <span class="rail-meta">${escapeHtml(t(step.meta))}</span>
                </span>
              </button>
            `;
          }).join("")}
        </div>
      </section>
    `;
  }

  function renderDecisionDrawer() {
    if (!state.decisionsOpen) {
      return "";
    }
    return `
      <aside class="decision-drawer" aria-label="Decisions captured">
        <div class="drawer-header">
          <h2>${escapeHtml(t("Decisions captured"))}</h2>
          <button class="ghost-button" data-action="toggle-decisions">${escapeHtml(t("Close"))}</button>
        </div>
        <div class="decision-summary">
          ${Object.entries(decisions).map(([key, decision]) => {
            const choiceKey = state.decisionChoices[key];
            const choice = choiceKey ? decision.options[choiceKey] : null;
            return `
              <div class="decision-summary-item">
                <strong>${escapeHtml(t(decision.title))}</strong>
                <p>${choice ? `${escapeHtml(choiceKey)} - ${escapeHtml(t(choice.label))}` : escapeHtml(t("No choice recorded yet."))}</p>
              </div>
            `;
          }).join("")}
        </div>
      </aside>
    `;
  }

  function renderPageHeader(kicker, title, lede, actionHtml = "") {
    return `
      <header class="page-header">
        <div>
          <p class="page-kicker">${escapeHtml(t(kicker))}</p>
          <h1 class="page-title">${escapeHtml(t(title))}</h1>
          ${lede ? `<p class="page-lede">${escapeHtml(t(lede))}</p>` : ""}
        </div>
        <div class="inline-actions">${actionHtml}</div>
      </header>
    `;
  }

  function renderLogin() {
    const theme = themes[state.client];
    return `
      ${renderTopbar()}
      <main class="login-stage">
        <section class="login-visual" aria-label="Operational route preview">
          <div>
            <p class="eyebrow">Presenter entry</p>
            <h1 class="login-title">${escapeHtml(theme.wordmark)} ${escapeHtml(t("workforce control"))}</h1>
            <p class="page-lede">A static meeting prototype for staffing requests, people, shifts, transport, documents, and risk gates.</p>
          </div>
          <div class="login-route">
            <div class="route-block"><span class="muted">Request</span><strong>12</strong><span>Workers to Nitra</span></div>
            <div class="route-block"><span class="muted">Pickup</span><strong>06:15</strong><span>Bus 2, Nitra depot</span></div>
            <div class="route-block"><span class="muted">Gate</span><strong>1</strong><span>Blacklist review</span></div>
            <div class="route-block"><span class="muted">Cert</span><strong>12d</strong><span>Forklift expiry</span></div>
          </div>
        </section>
        <section class="login-panel">
          <p class="eyebrow">Cosmetic sign in</p>
          <h2 class="section-title">Open the live demo</h2>
          <div class="stack">
            <label class="field">
              <span>Email</span>
              <input type="email" value="manager@corvinum.example" aria-label="Email">
            </label>
            <label class="field">
              <span>Password</span>
              <input type="password" value="demo-only" aria-label="Password">
            </label>
            <div class="info-strip">Privileged roles would use 2FA here. This demo does not authenticate or send anything.</div>
            <button class="primary-button" data-action="sign-in">${escapeHtml(t("Sign in"))}</button>
          </div>
        </section>
      </main>
      ${renderDecisionDrawer()}
    `;
  }

  function renderShell() {
    return `
      ${renderTopbar()}
      <div class="app-layout">
        ${renderSidebar()}
        ${renderMobileManifest()}
        <main class="main-content" id="main-content">
          ${renderCurrentView()}
        </main>
        ${renderManifestRail()}
      </div>
      ${renderDecisionDrawer()}
    `;
  }

  function renderCurrentView() {
    switch (state.view) {
      case "dashboard":
        return renderDashboard();
      case "people":
        return renderPeople();
      case "requests":
        return renderRequests();
      case "shifts":
        return renderShifts();
      case "sms":
        return renderSms();
      case "second-shift":
        return renderSecondShift();
      case "sick-leave":
        return renderSickLeave();
      case "documents":
        return renderDocuments();
      case "approvals":
        return renderApprovals();
      case "reports":
        return renderReports();
      case "field":
        return renderFieldView();
      case "jober-finale":
        return renderJoberFinale();
      case "accommodation":
        return renderAccommodation();
      case "equipment":
        return renderEquipment();
      case "pohoda":
        return renderPohoda();
      default:
        return renderDashboard();
    }
  }

  function renderDashboard() {
    const working = mockData.people.filter((person) => person.availability === "Working").length;
    const expiring = 2;
    const blacklist = mockData.people.filter((person) => person.hireStatus === "Blacklisted").length;
    const pending = getPerson("tran").hireStatus === "Recruit" ? 1 : 0;

    return `
      <section class="page">
        ${renderPageHeader("Today", "Manager dashboard", "The meeting starts from the operational picture: who is working, what is expiring, and what needs a manager decision.")}
        <div class="metric-grid">
          ${metricCard("Working now", working, "Olha is active on Worksite A.", "shifts")}
          ${metricCard("Docs expiring", expiring, "Forklift and work permit alerts.", "documents")}
          ${metricCard("Blacklist queue", blacklist, "One returnee needs review.", "people")}
          ${metricCard("Hire approvals", pending, "Tran waits for manager approval.", "approvals")}
        </div>
        <div class="split">
          <section class="section">
            <h2 class="section-title">Today's manifest</h2>
            ${renderShiftTable()}
          </section>
          <section class="section">
            <h2 class="section-title">Recent audit</h2>
            ${renderAudit()}
          </section>
        </div>
      </section>
    `;
  }

  function metricCard(label, value, note, view) {
    return `
      <button class="metric-card" data-action="nav" data-view="${view}">
        <span class="metric-value">${escapeHtml(value)}</span>
        <span>
          <p class="metric-label">${escapeHtml(t(label))}</p>
          <p class="metric-note">${escapeHtml(t(note))}</p>
        </span>
      </button>
    `;
  }

  function renderRequests() {
    const request = mockData.partner;
    return `
      <section class="page">
        ${renderPageHeader("Decision 1", "Staffing request", "Help us confirm how this request enters the system before recruiters fill the work.")}
        <section class="section">
          <div class="three-up">
            <div><p class="field-label">Partner</p><strong>${escapeHtml(request.name)}</strong></div>
            <div><p class="field-label">Need</p><strong>${request.workersNeeded} workers</strong></div>
            <div><p class="field-label">Worksite</p><strong>${escapeHtml(request.worksite)}</strong></div>
          </div>
        </section>
        ${renderDecision("demand")}
        <section class="section">
          <h2 class="section-title">Next in the story</h2>
          <p class="muted">Whichever model the client picks, the demo continues into the same shift and transport flow.</p>
          <button class="primary-button" data-action="next-step" ${state.decisionChoices.demand ? "" : "disabled"}>Continue to risk check</button>
        </section>
      </section>
    `;
  }

  function renderPeople() {
    return `
      <section class="page">
        ${renderPageHeader("People", "Roster and live risk check", "The headline moment: the recruiter starts adding a returnee and the blacklist gate catches it before activation.")}
        <section class="section">
          <h2 class="section-title">Add person</h2>
          <div class="split">
            <div class="stack">
              <label class="field">
                <span>Name or identifier</span>
                <input data-input="risk" value="${escapeHtml(state.riskInput)}" autocomplete="off" aria-describedby="risk-result">
              </label>
              <div class="form-grid">
                <div class="field">
                  <span class="field-label">Country</span>
                  <span class="field-value">Ukraine</span>
                </div>
                <div class="field">
                  <span class="field-label">Initial status</span>
                  <span class="field-value">Recruit, activation gated</span>
                </div>
              </div>
            </div>
            <div id="risk-result">${riskResultHtml()}</div>
          </div>
        </section>
        <section class="section">
          <h2 class="section-title">People roster</h2>
          ${renderPeopleTable()}
        </section>
      </section>
    `;
  }

  function riskResultHtml() {
    const input = state.riskInput.trim().toLowerCase();
    const matchesBohdan = input.includes("bohdan") || input.includes("marchenko") || input.includes("богдан");
    const matchesOlha = input.includes("olha") || input.includes("tkachenko") || input.includes("ольга");

    if (!input) {
      return `<div class="info-strip"><strong>Ready for live check.</strong><p class="muted">Type a name or identifier to compare against duplicate and blacklist records.</p></div>`;
    }

    if (matchesBohdan) {
      return `
        <div class="hard-stop">
          <strong>Blacklist match found: Bohdan Marchenko</strong>
          <p>Category: repeated no-show. Activation is blocked until a manager reviews the record.</p>
          <div class="badge-row">${statusBadges(getPerson("bohdan"))}</div>
          <div class="inline-actions">
            ${actionButton("createPerson", "save-risk", state.bohdanFlagSaved ? "Saved with review flag" : "Save as recruit with review flag", state.bohdanFlagSaved ? "secondary-button" : "primary-button", state.bohdanFlagSaved ? "disabled" : "")}
          </div>
        </div>
      `;
    }

    if (matchesOlha) {
      return `<div class="warning"><strong>Possible duplicate.</strong><p>Olha Tkachenko already exists as a hired worker. Review before creating another profile.</p></div>`;
    }

    return `<div class="success"><strong>No blacklist or duplicate match.</strong><p>The person can be saved as Recruit and moved into work test scheduling.</p></div>`;
  }

  function renderApprovals() {
    const tran = getPerson("tran");
    return `
      <section class="page">
        ${renderPageHeader("Approval gate", "Work test and hire approval", "Recruiters can recommend a candidate. Managers make the hire decision and the audit trail records it.")}
        <div class="split">
          <section class="section">
            <h2 class="section-title">Tran Van Minh</h2>
            <div class="badge-row">${statusBadges(tran)}</div>
            <div class="form-grid">
              <div class="field">
                <span class="field-label">Work test</span>
                <span class="field-value">${state.testScheduled ? "Scheduled for 17 Jun 2026" : "Not scheduled"}</span>
              </div>
              <div class="field">
                <span class="field-label">Recommendation</span>
                <span class="field-value">${state.testRecommended ? "Recommend hire" : "Ready to recommend"}</span>
              </div>
              <label class="field">
                <span>Recruiter note</span>
                <textarea>Arrived on time, understood safety briefing, suitable for warehouse picker.</textarea>
              </label>
              <div class="field">
                <span class="field-label">Manager decision</span>
                <span class="field-value">${state.tranApproved ? "Approved as hired" : "Pending"}</span>
              </div>
            </div>
            <div class="inline-actions">
              ${actionButton("scheduleTest", "schedule-test", state.testScheduled ? "Test scheduled" : "Schedule work test", "secondary-button", state.testScheduled ? "disabled" : "")}
              ${actionButton("recommendHire", "recommend-hire", state.testRecommended ? "Recommended" : "Recommend hire", "secondary-button", state.testRecommended ? "disabled" : "")}
              ${actionButton("approveHire", "approve-hire", state.tranApproved ? "Hire approved" : "Approve hire", "primary-button", state.tranApproved ? "disabled" : "")}
            </div>
          </section>
          <section class="section">
            <h2 class="section-title">Audit entry</h2>
            ${state.tranApproved ? `<div class="success"><strong>Hire approved.</strong><p>Tran Van Minh changed from Recruit to Hired and the approval is in the audit log.</p></div>` : `<div class="info-strip"><strong>Manager approval required.</strong><p>Switch to Manager to approve the hire. Recruiter and Observer cannot complete this step.</p></div>`}
            ${renderAudit()}
          </section>
        </div>
      </section>
    `;
  }

  function renderShifts() {
    const olha = getPerson("olha");
    const busText = transportCapacityText();
    return `
      <section class="page">
        ${renderPageHeader("Decision 2", "Assign shift and transport", isCoordinator() ? "Transport logistics view: assigned worksite, dated shift, vehicle, pickup point, and time." : "Once hired, a worker is directly shift-eligible. The assignment ties the dated shift to a worksite, vehicle, pickup point, and time.")}
        <section class="section">
          <div class="split">
            <div class="stack">
              <h2 class="section-title">${isCoordinator() ? "Transport assignment" : "Worker header"}</h2>
              <div class="person-name">
                <span>${escapeHtml(olha.name)}</span>
                ${isCoordinator() ? "" : `<span class="script-name">${escapeHtml(olha.scriptName)}</span>`}
              </div>
              ${isCoordinator() ? "" : `<div class="badge-row">${statusBadges(olha)}</div>`}
              <div class="form-grid">
                <div class="field"><span class="field-label">Worksite</span><span class="field-value">Worksite A - Nitra warehouse</span></div>
                <div class="field"><span class="field-label">Shift</span><span class="field-value">16 Jun 2026, 07:00-15:00</span></div>
                <div class="field"><span class="field-label">Transport group</span><span class="field-value">Bus 2, Nitra depot, 06:15</span></div>
              </div>
              <div class="inline-actions">
                ${actionButton("assignShift", "assign-shift", state.shiftAssigned ? "Assigned to shift" : "Assign to shift", "primary-button", state.shiftAssigned ? "disabled" : "")}
              </div>
            </div>
            <div class="stack">
              <h2 class="section-title">Vehicle capacity</h2>
              <div class="capacity-meter">
                <div class="meter-track"><div class="meter-fill" style="--meter-width: ${state.shiftAssigned ? "100%" : "89%"}"></div></div>
                <strong class="mono">${escapeHtml(busText)}</strong>
                <p class="muted">Driver Tomas V., pickup Nitra depot, 06:15.</p>
              </div>
              <div class="success"><strong>Client decision: enforce capacity</strong><p>Vehicle-specific capacity is enforced. A full vehicle blocks new assignments.</p></div>
              ${state.shiftAssigned ? `<div class="hard-stop"><strong>Capacity enforced.</strong><p>Bus 2 is full after Olha. A future assignment would be blocked.</p></div>` : ""}
            </div>
          </div>
        </section>
        <section class="section">
          <h2 class="section-title">Shift table</h2>
          ${renderShiftTable()}
        </section>
      </section>
    `;
  }

  function transportCapacityText() {
    if (state.shiftAssigned) {
      return "9 / 9 full";
    }
    return "8 / 9 booked";
  }

  function renderSms() {
    const olha = getPerson("olha");
    const message = "Olha, your pickup is Bus 2 at 06:15 from Nitra depot for Worksite A - Nitra warehouse. Reply by SMS if you cannot travel.";
    return `
      <section class="page">
        ${renderPageHeader("SMS channel", "Pickup notice", "The demo composes the message and records a fake sent state. No SMS is actually sent.")}
        <div class="split">
          <section class="section">
            <h2 class="section-title">${escapeHtml(olha.name)}</h2>
            ${isCoordinator() ? "" : `<div class="badge-row">${statusBadges(olha)}</div>`}
            <p class="muted">Primary channel: SMS, because many workers do not reliably use email.</p>
            <div class="message-box">${escapeHtml(message)}</div>
            <div class="inline-actions">
              ${actionButton("sendSms", "send-sms", state.smsSent ? "Sent" : "Send pickup notice", state.smsSent ? "secondary-button" : "primary-button", state.smsSent ? "disabled" : "")}
            </div>
            ${state.smsSent ? `<div class="success"><strong>Sent confirmation shown.</strong><p>This is a demo receipt only. No message left the browser.</p></div>` : ""}
          </section>
          <section class="section">
            <h2 class="section-title">Transport context</h2>
            ${renderShiftTable("olha-only")}
          </section>
        </div>
      </section>
    `;
  }

  function renderSecondShift() {
    return `
      <section class="page">
        ${renderPageHeader("Same worker, same day", "Add second shift", "The model supports one worker holding multiple dated shifts with different worksites and transport groups.")}
        <section class="section">
          <div class="form-grid">
            <div class="field"><span class="field-label">Worker</span><span class="field-value">Olha Tkachenko</span></div>
            <div class="field"><span class="field-label">Worksite</span><span class="field-value">Worksite B - Trnava site</span></div>
            <div class="field"><span class="field-label">Shift</span><span class="field-value">16 Jun 2026, 17:30-21:30</span></div>
            <div class="field"><span class="field-label">Transport</span><span class="field-value">Bus 1, Trnava station, 10:40</span></div>
          </div>
          <div class="inline-actions">
            ${actionButton("assignShift", "add-second-shift", state.secondShiftAdded ? "Second shift added" : "Add second shift", state.secondShiftAdded ? "secondary-button" : "primary-button", state.secondShiftAdded ? "disabled" : "")}
          </div>
        </section>
        <section class="section">
          <h2 class="section-title">Olha's dated shifts</h2>
          ${renderShiftTable("olha-only")}
        </section>
      </section>
    `;
  }

  function renderSickLeave() {
    const olha = getPerson("olha");
    return `
      <section class="page">
        ${renderPageHeader("Availability", "Sick leave sets inactive", "The leave record stores dates only. No medical detail is captured in this prototype.")}
        <div class="split">
          <section class="section">
            <h2 class="section-title">Dates only leave entry</h2>
            <div class="form-grid">
              <div class="field"><span class="field-label">Worker</span><span class="field-value">Olha Tkachenko</span></div>
              <div class="field"><span class="field-label">Leave type</span><span class="field-value">Sick leave</span></div>
              <div class="field"><span class="field-label">From</span><span class="field-value">16 Jun 2026</span></div>
              <div class="field"><span class="field-label">To</span><span class="field-value">17 Jun 2026</span></div>
            </div>
            <div class="warning"><strong>No medical detail stored.</strong><p>The operational effect is enough: availability flips inactive and shifts in the window are cancelled.</p></div>
            <div class="inline-actions">
              ${actionButton("recordSickLeave", "record-sick-leave", state.sickLeaveRecorded ? "Sick leave recorded" : "Record sick leave dates", state.sickLeaveRecorded ? "secondary-button" : "primary-button", state.sickLeaveRecorded ? "disabled" : "")}
            </div>
          </section>
          <section class="section">
            <h2 class="section-title">Worker state</h2>
            <div class="person-name">
              <span>${escapeHtml(olha.name)}</span>
              <span class="script-name">${escapeHtml(olha.scriptName)}</span>
            </div>
            <div class="badge-row">${statusBadges(olha)}</div>
            ${state.sickLeaveRecorded ? `<div class="success"><strong>Availability changed to inactive.</strong><p>Both dated shifts in the sick-leave window show cancelled.</p></div>` : ""}
          </section>
        </div>
        <section class="section">
          <h2 class="section-title">Affected shifts</h2>
          ${renderShiftTable("olha-only")}
        </section>
      </section>
    `;
  }

  function renderDocuments() {
    const farrukh = getPerson("farrukh");
    return `
      <section class="page">
        ${renderPageHeader("Decision 3", "Certificate expiry hard-stop", "Farrukh is hired and available, but the required forklift certificate is inside the expiry warning window.")}
        <div class="split">
          <section class="section">
            <h2 class="section-title">${escapeHtml(farrukh.name)}</h2>
            <div class="person-name">
              <span>${escapeHtml(farrukh.name)}</span>
              <span class="script-name">${escapeHtml(farrukh.scriptName)}</span>
            </div>
            <div class="badge-row">${statusBadges(farrukh)}</div>
            <div class="warning">
              <strong>Forklift certificate expires in ${farrukh.certificate.daysLeft} days.</strong>
              <p>Expiry date: ${escapeHtml(farrukh.certificate.expires)}. Forklift operator shifts require a valid certificate.</p>
            </div>
            <div class="inline-actions">
              ${actionButton("assignShift", "try-forklift", "Try assign forklift shift", "danger-button")}
            </div>
            ${state.certAssignmentTried ? `<div class="hard-stop"><strong>Assignment stopped.</strong><p>Forklift operator requires a valid forklift certificate. Pick another worker or update the certificate record.</p></div>` : ""}
          </section>
          <section class="section">
            <h2 class="section-title">Certificate metadata</h2>
            <div class="success"><strong>Client decision: metadata only</strong><p>Certificate records store type, issue date, expiry date, and valid/invalid status. No file is retained.</p></div>
            <table class="data-table">
              <thead><tr><th>Worker</th><th>Type</th><th>Issue date</th><th>Expiry date</th><th>Validity</th></tr></thead>
              <tbody>
                <tr>
                  <td data-label="Worker">Farrukh Yusupov</td>
                  <td data-label="Type">Forklift certificate</td>
                  <td data-label="Issue date">25 Jun 2024</td>
                  <td data-label="Expiry date">25 Jun 2026</td>
                  <td data-label="Validity"><span class="badge availability-inactive">Expires soon</span></td>
                </tr>
                <tr>
                  <td data-label="Worker">Olha Tkachenko</td>
                  <td data-label="Type">Work permit</td>
                  <td data-label="Issue date">08 Jul 2025</td>
                  <td data-label="Expiry date">02 Jul 2026</td>
                  <td data-label="Validity"><span class="badge availability-available">Valid until warning window</span></td>
                </tr>
              </tbody>
            </table>
          </section>
        </div>
      </section>
    `;
  }

  function renderFieldView() {
    const todayWorkers = [getPerson("olha"), getPerson("dilnoza"), getPerson("farrukh")];
    return `
      <section class="page">
        ${renderPageHeader("Mobile manager", "Field view", "A manager can check today's workers, document state, and quick actions from a phone-sized screen.")}
        <div class="phone-wrap">
          <div class="phone" aria-label="Phone frame">
            <div class="phone-screen">
              <div class="phone-top"><strong>Today</strong><span>Worksite A</span></div>
              <label class="field">
                <span>Search workers</span>
                <input value="Olha" aria-label="Search workers">
              </label>
              <div class="phone-list">
                ${todayWorkers.map((person) => `
                  <div class="phone-worker">
                    <div class="person-name">
                      <span>${escapeHtml(person.name)}</span>
                      <span class="script-name">${escapeHtml(person.scriptName)}</span>
                    </div>
                    <div class="badge-row">${statusBadges(person)}</div>
                    <span class="muted">${escapeHtml(person.document)}</span>
                    <div class="phone-actions">
                      <button ${state.role === "Observer" ? "disabled" : ""}>Call</button>
                      <button ${state.role === "Observer" ? "disabled" : ""}>Message</button>
                      <button data-action="mark-no-show" ${state.role !== "Manager" || state.noShowMarked ? "disabled" : ""}>${state.noShowMarked && person.id === "olha" ? "Marked" : "No-show"}</button>
                    </div>
                  </div>
                `).join("")}
              </div>
            </div>
          </div>
        </div>
      </section>
    `;
  }

  function renderJoberFinale() {
    const isJober = state.client === "jober";
    return `
      <section class="page">
        ${renderPageHeader("Finale", "Become Jober", "The same core app changes identity and enables licensed modules from one client switch.")}
        <section class="section">
          <div class="split">
            <div>
              <h2 class="section-title">${isJober ? "Jober modules are live" : "CorvinumEU core is active"}</h2>
              <p class="muted">${isJober ? "Accommodation, equipment, and Pohoda dashboard are now visible in the nav." : "Flip the client switch to reveal the fuller Jober configuration."}</p>
              <div class="inline-actions">
                <button class="primary-button" data-action="become-jober">${isJober ? "Jober active" : "Flip to Jober"}</button>
              </div>
            </div>
            <div class="${isJober ? "success" : "info-strip"}">
              <strong>One app, different client skin.</strong>
              <p>Layout and behavior stay shared. Brand, palette, and licensed modules change.</p>
            </div>
          </div>
        </section>
        ${isJober ? `
          <div class="three-up">
            ${modulePreview("Accommodation", "Rooms, occupancy, and worker assignment.", "accommodation")}
            ${modulePreview("Equipment", "Issued gear, returns, and worker sizes.", "equipment")}
            ${modulePreview("Pohoda dashboard", "Read-only demo figures via Pohoda mServer XML.", "pohoda")}
          </div>
        ` : ""}
      </section>
    `;
  }

  function modulePreview(title, body, view) {
    return `
      <section class="section">
        <h2 class="section-title">${escapeHtml(title)}</h2>
        <p class="muted">${escapeHtml(body)}</p>
        <button class="secondary-button" data-action="nav" data-view="${view}">Open ${escapeHtml(title)}</button>
      </section>
    `;
  }

  function renderAccommodation() {
    if (state.client !== "jober") {
      return renderModuleHidden("Accommodation");
    }
    return `
      <section class="page">
        ${renderPageHeader("Jober module", "Accommodation", "Room occupancy and worker-room assignment. Costs stay out of this demo.")}
        <section class="section">
          <table class="data-table">
            <thead><tr><th>Room</th><th>Occupancy</th><th>Workers</th><th>Action</th></tr></thead>
            <tbody>
              ${mockData.rooms.map((room) => `
                <tr>
                  <td data-label="Room"><strong>${escapeHtml(room.room)}</strong></td>
                  <td data-label="Occupancy" class="mono">${escapeHtml(room.occupancy)}</td>
                  <td data-label="Workers">${escapeHtml(room.workers)}</td>
                  <td data-label="Action"><button class="secondary-button" ${state.role === "Observer" ? "disabled" : ""}>Assign worker</button></td>
                </tr>
              `).join("")}
            </tbody>
          </table>
        </section>
      </section>
    `;
  }

  function renderEquipment() {
    if (state.client !== "jober") {
      return renderModuleHidden("Equipment");
    }
    return `
      <section class="page">
        ${renderPageHeader("Jober module", "Equipment", "Issued gear is visible beside worker sizes so inventory can be prepared before the shift.")}
        <div class="${isCoordinator() ? "stack" : "split"}">
          <section class="section">
            <h2 class="section-title">Issued gear</h2>
            <table class="data-table">
              <thead><tr><th>Worker</th><th>Item</th><th>Status</th><th>Size</th></tr></thead>
              <tbody>
                ${mockData.equipment.map((item) => `
                  <tr>
                    <td data-label="Worker">${escapeHtml(item.worker)}</td>
                    <td data-label="Item">${escapeHtml(item.item)}</td>
                    <td data-label="Status">${escapeHtml(item.status)}</td>
                    <td data-label="Size" class="mono">${escapeHtml(item.size)}</td>
                  </tr>
                `).join("")}
              </tbody>
            </table>
          </section>
          ${isCoordinator() ? "" : `<section class="section">
            <h2 class="section-title">Worker sizes</h2>
            ${mockData.people.filter((person) => person.hireStatus !== "Archived").map((person) => `
              <p><strong>${escapeHtml(person.name)}</strong><br><span class="muted">${escapeHtml(person.sizes)}</span></p>
            `).join("")}
          </section>`}
        </div>
      </section>
    `;
  }

  function renderPohoda() {
    if (state.client !== "jober") {
      return renderModuleHidden("Pohoda dashboard");
    }
    return `
      <section class="page">
        ${renderPageHeader("Jober module", "Pohoda dashboard", "Read-only accounting sync status for the demo. No connection is attempted.")}
        <div class="info-strip"><strong>Demo data - connected via Pohoda mServer (XML)</strong><p>Placeholder figures only. This browser does not call Pohoda.</p></div>
        <div class="metric-grid">
          ${plainMetric("Open invoices", "18", "Mocked")}
          ${plainMetric("Ready payroll rows", "42", "Mocked")}
          ${plainMetric("Last XML import", "08:45", "Mocked")}
          ${plainMetric("Sync warnings", "3", "Mocked")}
        </div>
      </section>
    `;
  }

  function plainMetric(label, value, note) {
    return `
      <div class="metric-card">
        <span class="metric-value">${escapeHtml(value)}</span>
        <span>
          <p class="metric-label">${escapeHtml(label)}</p>
          <p class="metric-note">${escapeHtml(note)}</p>
        </span>
      </div>
    `;
  }

  function renderModuleHidden(moduleName) {
    return `
      <section class="page">
        ${renderPageHeader("Module hidden", moduleName, "This module appears only after switching the client to Jober.")}
        <section class="section">
          <button class="primary-button" data-action="become-jober">Flip to Jober</button>
        </section>
      </section>
    `;
  }

  function renderReports() {
    return `
      <section class="page">
        ${renderPageHeader("Reports", "Meeting review", "Use this screen after the walkthrough to read captured decisions and operational signals.")}
        <div class="split">
          <section class="section">
            <h2 class="section-title">Decisions</h2>
            <div class="decision-summary">
              ${Object.entries(decisions).map(([key, decision]) => {
                const choiceKey = state.decisionChoices[key];
                const choice = choiceKey ? decision.options[choiceKey] : null;
                return `<div class="decision-summary-item"><strong>${escapeHtml(decision.title)}</strong><p>${choice ? `${escapeHtml(choiceKey)} - ${escapeHtml(choice.label)}` : "Pending"}</p></div>`;
              }).join("")}
            </div>
          </section>
          <section class="section">
            <h2 class="section-title">Operational report</h2>
            ${plainReportRow("Working now", mockData.people.filter((person) => person.availability === "Working").length)}
            ${plainReportRow("Available", mockData.people.filter((person) => person.availability === "Available").length)}
            ${plainReportRow("Inactive", mockData.people.filter((person) => person.availability === "Inactive").length)}
            <div class="inline-actions">
              <button class="secondary-button" data-action="nav" data-view="field">Open manager field view</button>
            </div>
          </section>
        </div>
      </section>
    `;
  }

  function plainReportRow(label, value) {
    return `<p><strong>${escapeHtml(label)}:</strong> <span class="mono">${escapeHtml(value)}</span></p>`;
  }

  function renderDecision(decisionKey) {
    const decision = decisions[decisionKey];
    const selected = state.decisionChoices[decisionKey];
    return `
      <section class="section">
        <p class="eyebrow">${escapeHtml(t("Help us confirm how you actually work"))}</p>
        <h2 class="section-title">${escapeHtml(t(decision.question))}</h2>
        <div class="decision-grid">
          ${Object.entries(decision.options).map(([choiceKey, option]) => `
            <button class="decision-option ${selected === choiceKey ? "is-selected" : ""}" data-action="choose-decision" data-decision="${decisionKey}" data-choice="${choiceKey}" ${state.role === "Observer" ? "disabled" : ""}>
              <span class="choice-marker">${escapeHtml(choiceKey)}</span>
              <strong>${escapeHtml(t(option.label))}</strong>
              <span>${escapeHtml(t(option.body))}</span>
              <span class="muted">${selected === choiceKey ? escapeHtml(t("Recorded")) : state.role === "Observer" ? escapeHtml(t("Observer read-only")) : escapeHtml(t("Awaiting choice"))}</span>
            </button>
          `).join("")}
        </div>
      </section>
    `;
  }

  function renderPeopleTable() {
    return `
      <table class="data-table">
        <thead>
          <tr><th>${escapeHtml(t("Person"))}</th><th>${escapeHtml(t("Country"))}</th><th>${escapeHtml(t("Status"))}</th><th>${escapeHtml(t("Document state"))}</th><th>${escapeHtml(t("Contact"))}</th></tr>
        </thead>
        <tbody>
          ${mockData.people.map((person) => `
            <tr>
              <td data-label="Person"><span class="person-name"><span>${escapeHtml(person.name)}</span><span class="script-name">${escapeHtml(person.scriptName)}</span></span></td>
              <td data-label="Country">${escapeHtml(person.country)}</td>
              <td data-label="Status"><span class="badge-row">${statusBadges(person)}</span></td>
              <td data-label="Document state">${escapeHtml(person.document)}</td>
              <td data-label="Contact" class="mono">${escapeHtml(person.phone)}</td>
            </tr>
          `).join("")}
        </tbody>
      </table>
    `;
  }

  function renderShiftTable(filter = "all") {
    const rows = [];
    if (state.shiftAssigned || filter === "all") {
      rows.push({
        worker: "Olha Tkachenko",
        worksite: "Worksite A - Nitra warehouse",
        shift: "16 Jun, 07:00-15:00",
        transport: "Bus 2, 06:15, Nitra depot",
        status: state.sickLeaveRecorded ? "Cancelled" : state.shiftAssigned ? "Assigned" : "Draft"
      });
    }
    if (state.secondShiftAdded || filter === "all") {
      rows.push({
        worker: "Olha Tkachenko",
        worksite: "Worksite B - Trnava site",
        shift: "16 Jun, 17:30-21:30",
        transport: "Bus 1, 10:40, Trnava station",
        status: state.sickLeaveRecorded ? "Cancelled" : state.secondShiftAdded ? "Assigned" : "Planned"
      });
    }
    if (filter === "all") {
      rows.push({
        worker: "Dilnoza Karimova",
        worksite: "Worksite A - Nitra warehouse",
        shift: "16 Jun, 07:00-15:00",
        transport: "Bus 2, 06:15, Nitra depot",
        status: "Assigned"
      });
      rows.push({
        worker: "Farrukh Yusupov",
        worksite: "Worksite B - Trnava site",
        shift: "17 Jun, 08:00-16:00",
        transport: "Own transport",
        status: "Available"
      });
    }

    const showStatus = !isCoordinator();
    return `
      <table class="data-table">
        <thead><tr><th>${escapeHtml(t("Worker"))}</th><th>${escapeHtml(t("Worksite"))}</th><th>${escapeHtml(t("Shift"))}</th><th>${escapeHtml(t("Transport"))}</th>${showStatus ? `<th>${escapeHtml(t("Status"))}</th>` : ""}</tr></thead>
        <tbody>
          ${rows.map((row) => `
            <tr>
              <td data-label="Worker">${escapeHtml(row.worker)}</td>
              <td data-label="Worksite">${escapeHtml(row.worksite)}</td>
              <td data-label="Shift" class="mono">${escapeHtml(row.shift)}</td>
              <td data-label="Transport">${escapeHtml(row.transport)}</td>
              ${showStatus ? `<td data-label="Status"><span class="badge ${row.status === "Cancelled" ? "availability-inactive" : "availability-working"}">${escapeHtml(t(row.status))}</span></td>` : ""}
            </tr>
          `).join("")}
        </tbody>
      </table>
    `;
  }

  function renderAudit() {
    return `
      <ul class="audit-list">
        ${state.auditLog.slice(0, 6).map((item) => `
          <li class="audit-item"><span class="audit-time">${escapeHtml(item.time)}</span><span>${escapeHtml(item.text)}</span></li>
        `).join("")}
      </ul>
    `;
  }

  function goToStep(index) {
    const nextIndex = Math.max(0, Math.min(tourSteps.length - 1, Number(index)));
    const step = tourSteps[nextIndex];
    if (step.view !== "login" && !isViewAllowed(step.view)) {
      const fallbackIndex = tourSteps.findIndex((item) => item.view === coordinatorDefaultView());
      state.currentStep = fallbackIndex;
      state.view = coordinatorDefaultView();
      state.signedIn = true;
      render();
      return;
    }
    state.currentStep = nextIndex;
    state.view = step.view;
    state.signedIn = step.view !== "login";
    if (step.id === "approval" && state.role === "Observer") {
      state.role = "Recruiter";
    }
    render();
  }

  function setClient(client) {
    state.client = client in themes ? client : DEFAULT_CLIENT;
    document.documentElement.dataset.theme = state.client;
    if (state.client !== "jober" && ["accommodation", "equipment", "pohoda"].includes(state.view)) {
      state.view = "dashboard";
    }
    normalizeRoleView();
  }

  function chooseDecision(decisionKey, choiceKey) {
    if (lockedDecisions[decisionKey]) {
      return;
    }
    if (!decisions[decisionKey] || !decisions[decisionKey].options[choiceKey]) {
      return;
    }
    state.decisionChoices[decisionKey] = choiceKey;
    addAudit(`${decisions[decisionKey].title}: option ${choiceKey} recorded.`);
  }

  function handleAction(action, target) {
    switch (action) {
      case "sign-in":
        state.signedIn = true;
        state.role = "Manager";
        state.navOpen = false;
        state.manifestOpen = false;
        goToStep(1);
        return;
      case "start-demo":
        state.navOpen = false;
        state.manifestOpen = false;
        goToStep(0);
        return;
      case "prev-step":
        state.manifestOpen = false;
        if (isCoordinator()) {
          const steps = visibleTourSteps();
          const previous = steps[Math.max(0, currentVisibleStepIndex() - 1)];
          goToStep(tourSteps.indexOf(previous));
          return;
        }
        goToStep(state.currentStep - 1);
        return;
      case "next-step":
        state.manifestOpen = false;
        if (isCoordinator()) {
          const steps = visibleTourSteps();
          const next = steps[Math.min(steps.length - 1, currentVisibleStepIndex() + 1)];
          goToStep(tourSteps.indexOf(next));
          return;
        }
        goToStep(state.currentStep + 1);
        return;
      case "go-step":
        state.navOpen = false;
        state.manifestOpen = false;
        goToStep(target.dataset.step);
        return;
      case "nav":
        if (!isViewAllowed(target.dataset.view)) {
          return;
        }
        state.signedIn = true;
        state.view = target.dataset.view;
        state.navOpen = false;
        render();
        return;
      case "toggle-nav":
        state.navOpen = !state.navOpen;
        render();
        return;
      case "close-nav":
        state.navOpen = false;
        render();
        return;
      case "toggle-manifest":
        state.manifestOpen = !state.manifestOpen;
        render();
        return;
      case "set-client":
        setClient(target.dataset.client);
        render();
        return;
      case "set-role":
        if (roles.includes(target.dataset.role)) {
          state.role = target.dataset.role;
          normalizeRoleView();
        }
        render();
        return;
      case "set-language":
        if (languages.some((language) => language.id === target.dataset.language)) {
          state.language = target.dataset.language;
        }
        render();
        return;
      case "toggle-decisions":
        state.decisionsOpen = !state.decisionsOpen;
        render();
        return;
      case "choose-decision":
        chooseDecision(target.dataset.decision, target.dataset.choice);
        render();
        return;
      case "save-risk":
        if (!can("createPerson")) {
          return;
        }
        state.bohdanFlagSaved = true;
        addAudit("Bohdan Marchenko saved as Recruit with manager review flag. Activation remains blocked.");
        render();
        return;
      case "schedule-test":
        if (!can("scheduleTest")) {
          return;
        }
        state.testScheduled = true;
        addAudit("Work test scheduled for Tran Van Minh.");
        render();
        return;
      case "recommend-hire":
        if (!can("recommendHire")) {
          return;
        }
        state.testRecommended = true;
        addAudit("Recruiter recommended Tran Van Minh for hire.");
        render();
        return;
      case "approve-hire":
        if (!can("approveHire")) {
          return;
        }
        state.testRecommended = true;
        state.tranApproved = true;
        setPerson("tran", { hireStatus: "Hired", availability: "Available", document: "Hired after work test" });
        addAudit("Manager approved Tran Van Minh. Hire status changed from Recruit to Hired.");
        render();
        return;
      case "assign-shift":
        if (!can("assignShift")) {
          return;
        }
        state.shiftAssigned = true;
        setPerson("olha", { availability: "Working" });
        addAudit("Olha Tkachenko assigned to Worksite A with Bus 2 pickup.");
        render();
        return;
      case "send-sms":
        if (!can("sendSms")) {
          return;
        }
        state.smsSent = true;
        addAudit("Pickup notice marked sent for Olha Tkachenko. Demo only, no SMS sent.");
        render();
        return;
      case "add-second-shift":
        if (!can("assignShift")) {
          return;
        }
        state.secondShiftAdded = true;
        addAudit("Second same-day shift added for Olha Tkachenko at Worksite B.");
        render();
        return;
      case "record-sick-leave":
        if (!can("recordSickLeave")) {
          return;
        }
        state.sickLeaveRecorded = true;
        setPerson("olha", { availability: "Inactive" });
        addAudit("Sick leave dates recorded for Olha Tkachenko. Availability changed to Inactive.");
        render();
        return;
      case "try-forklift":
        if (!can("assignShift")) {
          return;
        }
        state.certAssignmentTried = true;
        addAudit("Forklift assignment stopped for Farrukh Yusupov because required certificate is expiring.");
        render();
        return;
      case "mark-no-show":
        if (state.role !== "Manager") {
          return;
        }
        state.noShowMarked = true;
        addAudit("Manager marked a field no-show from the mobile view.");
        render();
        return;
      case "become-jober":
        setClient("jober");
        state.view = "jober-finale";
        state.currentStep = 11;
        state.signedIn = true;
        addAudit("Client switched to Jober. Licensed modules are visible.");
        render();
        return;
      default:
        return;
    }
  }

  function handleInput(target) {
    if (target.dataset.input === "risk") {
      state.riskInput = target.value;
      const preview = document.getElementById("risk-result");
      if (preview) {
        preview.innerHTML = riskResultHtml();
      }
    }
  }

  function render() {
    normalizeRoleView();
    document.documentElement.dataset.theme = state.client;
    root.innerHTML = state.view === "login" ? renderLogin() : renderShell();
  }

  document.addEventListener("click", (event) => {
    const target = event.target.closest("[data-action]");
    if (!target) {
      return;
    }
    event.preventDefault();
    handleAction(target.dataset.action, target);
  });

  document.addEventListener("input", (event) => {
    const target = event.target.closest("[data-input]");
    if (!target) {
      return;
    }
    handleInput(target);
  });

  render();
})();
