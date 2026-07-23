(() => {
  "use strict";

  const brand = {
    wordmark: "Jober",
    subtitle: "Workforce folders"
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
      "Role": "Rola",
      "Role switch": "Prepínač roly",
      "Recruiter": "Náborár",
      "Manager": "Manažér",
      "Coordinator": "Koordinátor",
      "Observer": "Pozorovateľ",
      "Decisions captured": "Zachytené rozhodnutia",
      "Start guided demo": "Spustiť sprievodcu",
      "Start": "Štart",
      "Back": "Späť",
      "Next": "Ďalej",
      "Can approve hires, verify documents, demote, blacklist, and run field actions.": "Môže schvaľovať prijatia, overovať dokumenty, meniť statusy, pridávať na čiernu listinu a robiť terénne akcie.",
      "Can create people, schedule tests, assign shifts, send pickup notices, and update document metadata.": "Môže vytvárať ľudí, plánovať skúšky, priraďovať zmeny, posielať pokyny na vyzdvihnutie a aktualizovať metadáta dokumentov.",
      "Can manage transport, accommodation, and equipment logistics.": "Môže spravovať dopravu, ubytovanie a výstroj.",
      "Read-only view. Action buttons are disabled for meeting review.": "Režim iba na čítanie. Akčné tlačidlá sú vypnuté pre kontrolu na stretnutí.",
      "Operations": "Prevádzka",
      "People": "Ľudia",
      "Compliance": "Súlad",
      "Logistics": "Logistika",
      "Accounting": "Účtovníctvo",
      "Reports": "Reporty",
      "Board": "Panel",
      "Demand": "Dopyt",
      "Shifts": "Zmeny",
      "SMS pickup": "SMS vyzdvihnutie",
      "Second shift": "Druhá zmena",
      "Field mode": "Terénny režim",
      "Roster scan": "Kontrola zoznamu",
      "Approvals": "Schválenia",
      "Documents": "Dokumenty",
      "Sick leave": "PN",
      "Accommodation": "Ubytovanie",
      "Equipment": "Výstroj",
      "Pohoda": "Pohoda",
      "Review": "Kontrola",
      "Sign in": "Prihlásiť sa",
      "Manager dashboard": "Manažérsky prehľad",
      "Demand decision": "Rozhodnutie o dopyte",
      "Risk check": "Kontrola rizika",
      "Work test approval": "Schválenie pracovnej skúšky",
      "Shift + transport": "Zmena + doprava",
      "Pickup SMS": "SMS na vyzdvihnutie",
      "Certificate stop": "Zastavenie certifikátu",
      "Manager field view": "Terénny pohľad manažéra",
      "Daily control board": "Denný riadiaci panel",
      "Demand intake": "Príjem dopytu",
      "Worker file scan": "Kontrola karty pracovníka",
      "Trial shift decision": "Rozhodnutie po skúšobnej zmene",
      "Dispatch plan": "Dispečerský plán",
      "Pickup message": "Správa o vyzdvihnutí",
      "Second dispatch slot": "Druhý dispečerský slot",
      "Leave dates set inactive": "Dátumy absencie nastavia neaktívne",
      "Certificate expiry stop": "Zastavenie pri expirácii certifikátu",
      "Pohoda snapshot": "Snímka Pohoda",
      "Decision review": "Kontrola rozhodnutí",
      "Recorded": "Zaznamenané",
      "Observer read-only": "Pozorovateľ iba číta",
      "Awaiting choice": "Čaká na výber",
      "No choice recorded yet.": "Zatiaľ nie je zaznamenaný výber.",
      "Close": "Zavrieť",
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
      "Role": "Szerep",
      "Role switch": "Szerepváltó",
      "Recruiter": "Toborzó",
      "Manager": "Vezető",
      "Coordinator": "Koordinátor",
      "Observer": "Megfigyelő",
      "Decisions captured": "Rögzített döntések",
      "Start guided demo": "Vezetett demó indítása",
      "Start": "Indítás",
      "Back": "Vissza",
      "Next": "Tovább",
      "Can approve hires, verify documents, demote, blacklist, and run field actions.": "Jóváhagyhat felvételeket, ellenőrizhet dokumentumokat, módosíthat státuszt, tiltólistázhat és terepi műveleteket végezhet.",
      "Can create people, schedule tests, assign shifts, send pickup notices, and update document metadata.": "Létrehozhat dolgozókat, teszteket ütemezhet, műszakokat oszthat be, felvételi értesítést küldhet és dokumentummetaadatokat frissíthet.",
      "Can manage transport, accommodation, and equipment logistics.": "Szállítási, szállás- és felszerelési logisztikát kezelhet.",
      "Read-only view. Action buttons are disabled for meeting review.": "Csak olvasható nézet. A műveleti gombok ki vannak kapcsolva a megbeszéléshez.",
      "Operations": "Műveletek",
      "People": "Dolgozók",
      "Compliance": "Megfelelőség",
      "Logistics": "Logisztika",
      "Accounting": "Könyvelés",
      "Reports": "Jelentések",
      "Board": "Panel",
      "Demand": "Igény",
      "Shifts": "Műszakok",
      "SMS pickup": "Felvételi SMS",
      "Second shift": "Második műszak",
      "Field mode": "Terepi mód",
      "Roster scan": "Névsor ellenőrzése",
      "Approvals": "Jóváhagyások",
      "Documents": "Dokumentumok",
      "Sick leave": "Betegszabadság",
      "Accommodation": "Szállás",
      "Equipment": "Felszerelés",
      "Pohoda": "Pohoda",
      "Review": "Áttekintés",
      "Sign in": "Bejelentkezés",
      "Manager dashboard": "Vezetői áttekintés",
      "Demand decision": "Igénydöntés",
      "Risk check": "Kockázatellenőrzés",
      "Work test approval": "Próbanap jóváhagyása",
      "Shift + transport": "Műszak + szállítás",
      "Pickup SMS": "Felvételi SMS",
      "Certificate stop": "Tanúsítvány stop",
      "Manager field view": "Vezetői terepi nézet",
      "Daily control board": "Napi irányítópanel",
      "Demand intake": "Igényfelvétel",
      "Worker file scan": "Dolgozói karton ellenőrzése",
      "Trial shift decision": "Próbanapi döntés",
      "Dispatch plan": "Diszpécserterv",
      "Pickup message": "Felvételi üzenet",
      "Second dispatch slot": "Második beosztási slot",
      "Leave dates set inactive": "Távolléti dátumok inaktívra állítanak",
      "Certificate expiry stop": "Tanúsítvány lejárati stop",
      "Pohoda snapshot": "Pohoda pillanatkép",
      "Decision review": "Döntések áttekintése",
      "Recorded": "Rögzítve",
      "Observer read-only": "Megfigyelő csak olvas",
      "Awaiting choice": "Választásra vár",
      "No choice recorded yet.": "Még nincs rögzített választás.",
      "Close": "Bezárás",
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

  Object.assign(translations.sk, {
    "English": "Angličtina",
    "Slovak": "Slovenčina",
    "Hungarian": "Maďarčina",
    "Workforce folders": "Pracovné priečinky",
    "workforce folders": "pracovné priečinky",
    "Go to dashboard": "Prejsť na prehľad",
    "Presenter avatar": "Avatar prezentujúceho",
    "Current role": "Aktuálna rola",
    "Guided demo progress": "Priebeh sprievodcu",
    "Operational route preview": "Náhľad prevádzkovej trasy",
    "Phone frame": "Rám telefónu",
    "Action unavailable for current role.": "Akcia nie je dostupná pre aktuálnu rolu.",
    "Presenter entry": "Vstup prezentujúceho",
    "Auth facade": "Ukážkové prihlásenie",
    "A static meeting prototype for dispatch, people files, compliance, logistics, and accounting signals.": "Statický prototyp na stretnutie pre dispečing, karty ľudí, súlad, logistiku a účtovné signály.",
    "Cosmetic sign in": "Ukážkové prihlásenie",
    "Open the live demo": "Otvoriť živé demo",
    "Email": "E-mail",
    "Password": "Heslo",
    "Privileged roles would use 2FA here. This demo does not authenticate or send anything.": "Privilegované roly by tu použili 2FA. Toto demo neoveruje identitu ani nič neposiela.",
    "Request": "Požiadavka",
    "Pickup": "Vyzdvihnutie",
    "Gate": "Brána",
    "Cert": "Certifikát",
    "Workers to Nitra": "Pracovníci do Nitry",
    "Bus 2, Nitra depot": "Autobus 2, depo Nitra",
    "Blacklist review": "Kontrola čiernej listiny",
    "Forklift expiry": "Expirácia VZV",
    "workers": "pracovníkov",
    "The meeting starts from dispatch pressure: who is working, what is expiring, and what needs a manager decision.": "Stretnutie začína dispečerským tlakom: kto pracuje, čo expiruje a čo potrebuje rozhodnutie manažéra.",
    "Working now": "Práve pracujú",
    "Olha is active on Worksite A.": "Olha je aktívna na pracovisku A.",
    "Docs expiring": "Dokumenty expirujú",
    "Forklift and work permit alerts.": "Upozornenia na VZV a pracovné povolenie.",
    "Blacklist queue": "Front čiernej listiny",
    "One returnee needs review.": "Jeden navrátilec potrebuje kontrolu.",
    "Hire approvals": "Schválenia prijatia",
    "Tran waits for manager approval.": "Tran čaká na schválenie manažérom.",
    "Today's manifest": "Dnešný manifest",
    "Recent audit": "Nedávny audit",
    "Help us confirm how demand enters the board before recruiters fill the work.": "Pomôžte nám potvrdiť, ako sa dopyt dostane na panel pred obsadením práce náborármi.",
    "Partner": "Partner",
    "Need": "Potreba",
    "Next move": "Ďalší krok",
    "Whichever model the team picks, the demo continues into the same shift and transport flow.": "Nech si tím vyberie ktorýkoľvek model, demo pokračuje do rovnakého toku zmien a dopravy.",
    "Continue to risk check": "Pokračovať na kontrolu rizika",
    "Add person": "Pridať osobu",
    "Name or identifier": "Meno alebo identifikátor",
    "Initial status": "Počiatočný status",
    "Recruit, activation gated": "Kandidát, aktivácia blokovaná",
    "People roster": "Zoznam ľudí",
    "The headline moment: the recruiter starts adding a returnee and the blacklist gate catches it before activation.": "Hlavný moment: náborár začne pridávať navrátilca a brána čiernej listiny ho zachytí pred aktiváciou.",
    "Ready for live check.": "Pripravené na živú kontrolu.",
    "Type a name or identifier to compare against duplicate and blacklist records.": "Zadajte meno alebo identifikátor na porovnanie s duplicitami a čiernou listinou.",
    "Blacklist match found: Bohdan Marchenko": "Zhoda na čiernej listine: Bohdan Marchenko",
    "Category: repeated no-show. Activation is blocked until a manager reviews the record.": "Kategória: opakovaná neúčasť. Aktivácia je blokovaná, kým manažér neskontroluje záznam.",
    "Saved with review flag": "Uložené s príznakom kontroly",
    "Save as recruit with review flag": "Uložiť ako kandidáta s príznakom kontroly",
    "Possible duplicate.": "Možná duplicita.",
    "Olha Tkachenko already exists as a hired worker. Review before creating another profile.": "Olha Tkachenko už existuje ako prijatá pracovníčka. Pred vytvorením ďalšieho profilu ju skontrolujte.",
    "No blacklist or duplicate match.": "Bez zhody na čiernej listine alebo v duplicitách.",
    "The person can be saved as Recruit and moved into work test scheduling.": "Osobu možno uložiť ako kandidáta a presunúť do plánovania pracovnej skúšky.",
    "Recruiters can recommend a candidate. Managers make the hire decision and the audit trail records it.": "Náborári môžu odporučiť kandidáta. Manažéri rozhodnú o prijatí a auditná stopa to zaznamená.",
    "Work test": "Pracovná skúška",
    "Scheduled for 17 Jun 2026": "Naplánované na 17 Jun 2026",
    "Not scheduled": "Nenaplánované",
    "Recommendation": "Odporúčanie",
    "Recommend hire": "Odporučiť prijatie",
    "Ready to recommend": "Pripravené na odporúčanie",
    "Recruiter note": "Poznámka náborára",
    "Arrived on time, understood safety briefing, suitable for warehouse picker.": "Prišiel načas, porozumel bezpečnostnej inštruktáži, vhodný pre skladový výber.",
    "Manager decision": "Rozhodnutie manažéra",
    "Approved as hired": "Schválené ako prijaté",
    "Pending": "Čaká",
    "Test scheduled": "Skúška naplánovaná",
    "Schedule work test": "Naplánovať pracovnú skúšku",
    "Recommended": "Odporúčané",
    "Hire approved": "Prijatie schválené",
    "Approve hire": "Schváliť prijatie",
    "Audit entry": "Auditný záznam",
    "Hire approved.": "Prijatie schválené.",
    "Tran Van Minh changed from Recruit to Hired and the approval is in the audit log.": "Tran Van Minh sa zmenil z kandidáta na prijatého a schválenie je v audite.",
    "Manager approval required.": "Vyžaduje sa schválenie manažérom.",
    "Switch to Manager to approve the hire. Recruiter and Observer cannot complete this step.": "Pre schválenie prijatia prepnite na Manažéra. Náborár ani Pozorovateľ tento krok nemôžu dokončiť.",
    "Olha is hired. The assignment ties the dated shift to a worksite, position, bus, pickup point, and time.": "Olha je prijatá. Priradenie spája dátumovanú zmenu s pracoviskom, pozíciou, autobusom, miestom vyzdvihnutia a časom.",
    "Once hired, a worker is directly shift-eligible. The assignment ties the dated shift to a worksite, vehicle, pickup point, and time.": "Po prijatí je pracovník priamo spôsobilý na zmenu. Priradenie spája dátumovanú zmenu s pracoviskom, vozidlom, miestom vyzdvihnutia a časom.",
    "Transport logistics view: assigned worksite, dated shift, vehicle, pickup point, and time.": "Logistický pohľad dopravy: priradené pracovisko, dátumovaná zmena, vozidlo, miesto vyzdvihnutia a čas.",
    "Worker header": "Hlavička pracovníka",
    "Transport assignment": "Priradenie dopravy",
    "Position": "Pozícia",
    "Transport group": "Dopravná skupina",
    "Bus 2 capacity": "Kapacita autobusu 2",
    "Vehicle capacity": "Kapacita vozidla",
    "Driver Tomas V., pickup Nitra depot, 06:15.": "Vodič Tomas V., vyzdvihnutie depo Nitra, 06:15.",
    "Capacity enforced.": "Kapacita vynútená.",
    "Bus 2 is full after Olha. A future assignment would be blocked.": "Autobus 2 je po Olhe plný. Ďalšie priradenie by bolo blokované.",
    "Shift table": "Tabuľka zmien",
    "Assigned to shift": "Priradené na zmenu",
    "Assign to shift": "Priradiť na zmenu",
    "8 / 9 booked": "8 / 9 rezervované",
    "9 / 9 full": "9 / 9 plné",
    "The demo composes the message and records a fake sent state. No SMS is actually sent.": "Demo zostaví správu a zaznamená falošný stav odoslania. Žiadna SMS sa skutočne neposiela.",
    "Primary channel: SMS, because many workers do not reliably use email.": "Primárny kanál: SMS, pretože mnohí pracovníci nepoužívajú e-mail spoľahlivo.",
    "Olha, your pickup is Bus 2 at 06:15 from Nitra depot for Worksite A - Nitra warehouse. Reply by SMS if you cannot travel.": "Olha, vyzdvihnutie je autobusom 2 o 06:15 z depa Nitra na Pracovisko A - sklad Nitra. Ak nemôžete cestovať, odpovedzte SMS.",
    "Sent": "Odoslané",
    "Send pickup notice": "Odoslať pokyn na vyzdvihnutie",
    "Sent confirmation shown.": "Zobrazené potvrdenie odoslania.",
    "This is a demo receipt only. No message left the browser.": "Toto je iba demo potvrdenie. Žiadna správa neopustila prehliadač.",
    "Transport context": "Kontext dopravy",
    "The model supports one worker holding multiple dated shifts with different worksites and transport groups.": "Model podporuje jedného pracovníka s viacerými dátumovanými zmenami na rôznych pracoviskách a v rôznych dopravných skupinách.",
    "Second shift added": "Druhá zmena pridaná",
    "Add second shift": "Pridať druhú zmenu",
    "Olha's dated shifts": "Dátumované zmeny Olhy",
    "The leave record stores dates only. No medical detail is captured in this prototype.": "Záznam PN ukladá iba dátumy. V prototype sa nezachytáva žiadny zdravotný detail.",
    "Dates only leave entry": "Záznam PN iba s dátumami",
    "Leave type": "Typ absencie",
    "From": "Od",
    "To": "Do",
    "No medical detail stored.": "Žiadny zdravotný detail sa neukladá.",
    "The operational effect is enough: availability flips inactive and shifts in the window are cancelled.": "Stačí prevádzkový dopad: dostupnosť sa prepne na neaktívnu a zmeny v okne sa zrušia.",
    "Sick leave recorded": "PN zaznamenaná",
    "Record sick leave dates": "Zaznamenať dátumy PN",
    "Worker state": "Stav pracovníka",
    "Availability changed to inactive.": "Dostupnosť zmenená na neaktívnu.",
    "Both dated shifts in the sick-leave window show cancelled.": "Obe dátumované zmeny v okne PN sa zobrazujú ako zrušené.",
    "Affected shifts": "Dotknuté zmeny",
    "Farrukh is hired and available, but the required forklift certificate is inside the expiry warning window.": "Farrukh je prijatý a dostupný, ale požadovaný certifikát na VZV je v expiračnom varovnom okne.",
    "Forklift certificate expires in 12 days.": "Certifikát na VZV expiruje o 12 dní.",
    "Expiry date: 25 Jun 2026. Forklift operator shifts require a valid certificate.": "Dátum expirácie: 25 Jun 2026. Zmeny operátora VZV vyžadujú platný certifikát.",
    "Try assign forklift shift": "Skúsiť priradiť zmenu VZV",
    "Assignment stopped.": "Priradenie zastavené.",
    "Forklift operator requires a valid forklift certificate. Pick another worker or update the certificate record.": "Operátor VZV vyžaduje platný certifikát. Vyberte iného pracovníka alebo aktualizujte záznam certifikátu.",
    "Certificate metadata": "Metadáta certifikátu",
    "Type": "Typ",
    "Issue date": "Dátum vydania",
    "Expiry date": "Dátum expirácie",
    "Validity": "Platnosť",
    "Valid until warning window": "Platný do varovného okna",
    "Document queue": "Front dokumentov",
    "Document": "Dokument",
    "State": "Stav",
    "Forklift certificate": "Certifikát na VZV",
    "Work permit": "Pracovné povolenie",
    "Expires soon": "Čoskoro expiruje",
    "18 days left": "Zostáva 18 dní",
    "A coordinator can check today's workers, document state, and quick actions from a phone-sized screen.": "Koordinátor môže z obrazovky veľkosti telefónu skontrolovať dnešných pracovníkov, stav dokumentov a rýchle akcie.",
    "A manager can check today's workers, document state, and quick actions from a phone-sized screen.": "Manažér môže z obrazovky veľkosti telefónu skontrolovať dnešných pracovníkov, stav dokumentov a rýchle akcie.",
    "Search workers": "Hľadať pracovníkov",
    "Call": "Volať",
    "Message": "Správa",
    "Marked": "Označené",
    "No-show": "Neúčasť",
    "Room occupancy and worker-room assignment. Costs stay out of this demo.": "Obsadenosť izieb a priradenie pracovníkov k izbám. Náklady zostávajú mimo dema.",
    "Room": "Izba",
    "Occupancy": "Obsadenosť",
    "Workers": "Pracovníci",
    "Action": "Akcia",
    "Assign worker": "Priradiť pracovníka",
    "Gear and sizes": "Výstroj a veľkosti",
    "Issued gear sits beside worker sizes so inventory can be prepared before the shift.": "Vydaná výstroj je pri veľkostiach pracovníkov, aby sa inventár pripravil pred zmenou.",
    "Issued gear": "Vydaná výstroj",
    "Worker sizes": "Veľkosti pracovníkov",
    "Item": "Položka",
    "Size": "Veľkosť",
    "Helmet": "Prilba",
    "Boots": "Topánky",
    "Vest": "Vesta",
    "Gloves": "Rukavice",
    "Issued": "Vydané",
    "Prepared": "Pripravené",
    "Returned": "Vrátené",
    "Standard": "Štandard",
    "Read-only accounting sync status for the demo. No connection is attempted.": "Stav účtovnej synchronizácie iba na čítanie pre demo. Neprebieha žiadne pripojenie.",
    "Demo data - connected via Pohoda mServer (XML)": "Demo dáta - pripojené cez Pohoda mServer (XML)",
    "Placeholder figures only. This browser does not call Pohoda.": "Iba zástupné údaje. Tento prehliadač nevolá Pohodu.",
    "Open invoices": "Otvorené faktúry",
    "Ready payroll rows": "Pripravené mzdové riadky",
    "Last XML import": "Posledný XML import",
    "Sync warnings": "Upozornenia synchronizácie",
    "Mocked": "Ukážkové",
    "Use this screen after the walkthrough to read captured decisions and operational signals.": "Túto obrazovku použite po prechode na čítanie zachytených rozhodnutí a prevádzkových signálov.",
    "Decisions": "Rozhodnutia",
    "Operational report": "Prevádzkový report",
    "Open manager field view": "Otvoriť terénny pohľad manažéra",
    "Ukraine": "Ukrajina",
    "Uzbekistan": "Uzbekistan",
    "Vietnam": "Vietnam",
    "Worksite A - Nitra warehouse": "Pracovisko A - sklad Nitra",
    "Worksite B - Trnava site": "Pracovisko B - areál Trnava",
    "Worksite A": "Pracovisko A",
    "General laborer": "Pomocný pracovník",
    "Bus 2, Nitra depot, 06:15": "Autobus 2, depo Nitra, 06:15",
    "Bus 1, Trnava station, 10:40": "Autobus 1, stanica Trnava, 10:40",
    "Bus 2, 06:15, Nitra depot": "Autobus 2, 06:15, depo Nitra",
    "Bus 1, 10:40, Trnava station": "Autobus 1, 10:40, stanica Trnava",
    "Own transport": "Vlastná doprava",
    "Work permit expires in 18 days": "Pracovné povolenie expiruje o 18 dní",
    "Forklift cert expires 25 Jun 2026": "Certifikát na VZV expiruje 25 Jun 2026",
    "Residence card valid": "Pobytová karta platná",
    "Profile archived": "Profil archivovaný",
    "Hired after work test": "Prijatý po pracovnej skúške",
    "Room 12": "Izba 12",
    "Room 14": "Izba 14",
    "Room 18": "Izba 18",
    "3/4 beds": "3/4 lôžka",
    "2/4 beds": "2/4 lôžka",
    "4/4 beds": "4/4 lôžka",
    "Full": "Plné",
    "None": "Žiadne",
    "Not recorded": "Nezaznamenané",
    "Pending issue": "Čaká na vydanie",
    "Vest, helmet, gloves": "Vesta, prilba, rukavice",
    "Helmet, boots": "Prilba, topánky",
    "Vest, gloves": "Vesta, rukavice",
    "Shirt M / trousers 40 / boots 39": "Tričko M / nohavice 40 / topánky 39",
    "Shirt L / trousers 42 / boots 43": "Tričko L / nohavice 42 / topánky 43",
    "Shirt S / trousers 38 / boots 40": "Tričko S / nohavice 38 / topánky 40",
    "Shirt S / trousers 36 / boots 38": "Tričko S / nohavice 36 / topánky 38",
    "Shirt XL / trousers 46 / boots 44": "Tričko XL / nohavice 46 / topánky 44",
    "Dashboard opened for today's staffing picture.": "Prehľad otvorený pre dnešný obraz obsadenia.",
    "Forklift certificate alert queued for Farrukh Yusupov.": "Upozornenie na certifikát VZV pre Farrukha Yusupova zaradené do frontu.",
    "Blacklist review queue contains one returnee.": "Front kontroly čiernej listiny obsahuje jedného navrátilca.",
    "Demand model: option A recorded.": "Model dopytu: možnosť A zaznamenaná.",
    "Demand model: option B recorded.": "Model dopytu: možnosť B zaznamenaná.",
    "Transport capacity: option A recorded.": "Kapacita dopravy: možnosť A zaznamenaná.",
    "Transport capacity: option B recorded.": "Kapacita dopravy: možnosť B zaznamenaná.",
    "Certificate storage: option A recorded.": "Ukladanie certifikátov: možnosť A zaznamenaná.",
    "Certificate storage: option B recorded.": "Ukladanie certifikátov: možnosť B zaznamenaná.",
    "Bohdan Marchenko saved as Recruit with manager review flag. Activation remains blocked.": "Bohdan Marchenko uložený ako kandidát s príznakom manažérskej kontroly. Aktivácia zostáva blokovaná.",
    "Work test scheduled for Tran Van Minh.": "Pracovná skúška pre Tran Van Minh naplánovaná.",
    "Recruiter recommended Tran Van Minh for hire.": "Náborár odporučil Tran Van Minh na prijatie.",
    "Manager approved Tran Van Minh. Hire status changed from Recruit to Hired.": "Manažér schválil Tran Van Minh. Status prijatia sa zmenil z kandidáta na prijatého.",
    "Olha Tkachenko assigned to Worksite A with Bus 2 pickup.": "Olha Tkachenko priradená na Pracovisko A s vyzdvihnutím autobusom 2.",
    "Pickup notice marked sent for Olha Tkachenko. Demo only, no SMS sent.": "Pokyn na vyzdvihnutie pre Olhu Tkachenko označený ako odoslaný. Iba demo, SMS sa neodoslala.",
    "Second same-day shift added for Olha Tkachenko at Worksite B.": "Druhá zmena v ten istý deň pridaná pre Olhu Tkachenko na Pracovisku B.",
    "Sick leave dates recorded for Olha Tkachenko. Availability changed to Inactive.": "Dátumy PN pre Olhu Tkachenko zaznamenané. Dostupnosť zmenená na neaktívnu.",
    "Forklift assignment stopped for Farrukh Yusupov because required certificate is expiring.": "Priradenie VZV pre Farrukha Yusupova zastavené, pretože požadovaný certifikát expiruje.",
    "Manager marked a field no-show from the mobile view.": "Manažér označil terénnu neúčasť z mobilného pohľadu."
  });

  Object.assign(translations.hu, {
    "English": "Angol",
    "Slovak": "Szlovák",
    "Hungarian": "Magyar",
    "Workforce folders": "Munkaerő mappák",
    "workforce folders": "munkaerő mappák",
    "Go to dashboard": "Ugrás az áttekintésre",
    "Presenter avatar": "Prezentáló avatárja",
    "Current role": "Aktuális szerep",
    "Guided demo progress": "Vezetett demó előrehaladása",
    "Operational route preview": "Műveleti útvonal előnézet",
    "Phone frame": "Telefonkeret",
    "Action unavailable for current role.": "A művelet nem elérhető az aktuális szerepben.",
    "Presenter entry": "Prezentálói belépés",
    "Auth facade": "Belépési minta",
    "A static meeting prototype for dispatch, people files, compliance, logistics, and accounting signals.": "Statikus tárgyalási prototípus diszpécserhez, dolgozói kartonokhoz, megfelelőséghez, logisztikához és könyvelési jelekhez.",
    "Cosmetic sign in": "Minta bejelentkezés",
    "Open the live demo": "Élő demó megnyitása",
    "Email": "E-mail",
    "Password": "Jelszó",
    "Privileged roles would use 2FA here. This demo does not authenticate or send anything.": "A kiemelt szerepek itt 2FA-t használnának. Ez a demó nem hitelesít és nem küld semmit.",
    "Request": "Igény",
    "Pickup": "Felvétel",
    "Gate": "Kapu",
    "Cert": "Tanúsítvány",
    "Workers to Nitra": "Dolgozók Nyitrára",
    "Bus 2, Nitra depot": "2-es busz, nyitrai depó",
    "Blacklist review": "Tiltólista ellenőrzés",
    "Forklift expiry": "Targonca lejárat",
    "workers": "dolgozó",
    "The meeting starts from dispatch pressure: who is working, what is expiring, and what needs a manager decision.": "A megbeszélés a diszpécseri nyomásból indul: ki dolgozik, mi jár le, és mi igényel vezetői döntést.",
    "Working now": "Most dolgoznak",
    "Olha is active on Worksite A.": "Olha aktív az A munkaterületen.",
    "Docs expiring": "Lejáró dokumentumok",
    "Forklift and work permit alerts.": "Targonca és munkavállalási engedély riasztások.",
    "Blacklist queue": "Tiltólista sor",
    "One returnee needs review.": "Egy visszatérőt ellenőrizni kell.",
    "Hire approvals": "Felvételi jóváhagyások",
    "Tran waits for manager approval.": "Tran vezetői jóváhagyásra vár.",
    "Today's manifest": "Mai manifest",
    "Recent audit": "Friss audit",
    "Help us confirm how demand enters the board before recruiters fill the work.": "Segítsen megerősíteni, hogyan kerül az igény a panelre, mielőtt a toborzók betöltik a munkát.",
    "Partner": "Partner",
    "Need": "Igény",
    "Next move": "Következő lépés",
    "Whichever model the team picks, the demo continues into the same shift and transport flow.": "Bármelyik modellt választja a csapat, a demó ugyanabba a műszak- és szállítási folyamatba lép tovább.",
    "Continue to risk check": "Tovább a kockázatellenőrzéshez",
    "Add person": "Személy hozzáadása",
    "Name or identifier": "Név vagy azonosító",
    "Initial status": "Kezdő státusz",
    "Recruit, activation gated": "Jelölt, aktiválás blokkolva",
    "People roster": "Dolgozói névsor",
    "The headline moment: the recruiter starts adding a returnee and the blacklist gate catches it before activation.": "A fő pillanat: a toborzó visszatérőt kezd rögzíteni, és a tiltólista kapu még aktiválás előtt megfogja.",
    "Ready for live check.": "Kész az élő ellenőrzésre.",
    "Type a name or identifier to compare against duplicate and blacklist records.": "Adjon meg nevet vagy azonosítót a duplikátumokkal és a tiltólistával való összevetéshez.",
    "Blacklist match found: Bohdan Marchenko": "Tiltólista egyezés: Bohdan Marchenko",
    "Category: repeated no-show. Activation is blocked until a manager reviews the record.": "Kategória: ismételt meg nem jelenés. Az aktiválás vezetői ellenőrzésig blokkolt.",
    "Saved with review flag": "Ellenőrzési jelzéssel mentve",
    "Save as recruit with review flag": "Mentés jelöltként ellenőrzési jelzéssel",
    "Possible duplicate.": "Lehetséges duplikátum.",
    "Olha Tkachenko already exists as a hired worker. Review before creating another profile.": "Olha Tkachenko már felvett dolgozóként létezik. Új profil előtt ellenőrizze.",
    "No blacklist or duplicate match.": "Nincs tiltólista- vagy duplikátumegyezés.",
    "The person can be saved as Recruit and moved into work test scheduling.": "A személy jelöltként menthető és átvihető a próbanap ütemezésébe.",
    "Recruiters can recommend a candidate. Managers make the hire decision and the audit trail records it.": "A toborzók ajánlhatnak jelöltet. A vezetők hozzák meg a felvételi döntést, az auditnapló pedig rögzíti.",
    "Work test": "Próbanap",
    "Scheduled for 17 Jun 2026": "Ütemezve: 17 Jun 2026",
    "Not scheduled": "Nincs ütemezve",
    "Recommendation": "Ajánlás",
    "Recommend hire": "Felvétel ajánlása",
    "Ready to recommend": "Ajánlásra kész",
    "Recruiter note": "Toborzói megjegyzés",
    "Arrived on time, understood safety briefing, suitable for warehouse picker.": "Időben érkezett, megértette a biztonsági eligazítást, alkalmas raktári komissiózónak.",
    "Manager decision": "Vezetői döntés",
    "Approved as hired": "Felvettként jóváhagyva",
    "Pending": "Függőben",
    "Test scheduled": "Teszt ütemezve",
    "Schedule work test": "Próbanap ütemezése",
    "Recommended": "Ajánlva",
    "Hire approved": "Felvétel jóváhagyva",
    "Approve hire": "Felvétel jóváhagyása",
    "Audit entry": "Auditbejegyzés",
    "Hire approved.": "Felvétel jóváhagyva.",
    "Tran Van Minh changed from Recruit to Hired and the approval is in the audit log.": "Tran Van Minh jelöltből felvett státuszba került, a jóváhagyás az auditnaplóban van.",
    "Manager approval required.": "Vezetői jóváhagyás szükséges.",
    "Switch to Manager to approve the hire. Recruiter and Observer cannot complete this step.": "A felvétel jóváhagyásához váltson Vezető szerepre. Toborzó és Megfigyelő nem fejezheti be ezt a lépést.",
    "Olha is hired. The assignment ties the dated shift to a worksite, position, bus, pickup point, and time.": "Olha felvéve. A kiosztás összeköti a dátumozott műszakot a munkaterülettel, pozícióval, busszal, felvételi ponttal és idővel.",
    "Once hired, a worker is directly shift-eligible. The assignment ties the dated shift to a worksite, vehicle, pickup point, and time.": "Felvétel után a dolgozó közvetlenül beosztható műszakra. A kiosztás összeköti a dátumozott műszakot a munkaterülettel, járművel, felvételi ponttal és idővel.",
    "Transport logistics view: assigned worksite, dated shift, vehicle, pickup point, and time.": "Szállítási logisztikai nézet: hozzárendelt munkaterület, dátumozott műszak, jármű, felvételi pont és idő.",
    "Worker header": "Dolgozói fejléc",
    "Transport assignment": "Szállítási beosztás",
    "Position": "Pozíció",
    "Transport group": "Szállítási csoport",
    "Bus 2 capacity": "2-es busz kapacitása",
    "Vehicle capacity": "Jármű kapacitása",
    "Driver Tomas V., pickup Nitra depot, 06:15.": "Sofőr Tomas V., felvétel nyitrai depó, 06:15.",
    "Capacity enforced.": "Kapacitás betartva.",
    "Bus 2 is full after Olha. A future assignment would be blocked.": "Olha után a 2-es busz megtelt. Egy későbbi kiosztás blokkolva lenne.",
    "Shift table": "Műszaktábla",
    "Assigned to shift": "Műszakra beosztva",
    "Assign to shift": "Műszakra osztás",
    "8 / 9 booked": "8 / 9 foglalt",
    "9 / 9 full": "9 / 9 tele",
    "The demo composes the message and records a fake sent state. No SMS is actually sent.": "A demó összeállítja az üzenetet és minta elküldött állapotot rögzít. Valódi SMS nem megy ki.",
    "Primary channel: SMS, because many workers do not reliably use email.": "Elsődleges csatorna: SMS, mert sok dolgozó nem használja megbízhatóan az e-mailt.",
    "Olha, your pickup is Bus 2 at 06:15 from Nitra depot for Worksite A - Nitra warehouse. Reply by SMS if you cannot travel.": "Olha, a felvétel a 2-es busszal 06:15-kor indul a nyitrai depóból az A munkaterület - nyitrai raktár felé. Válaszoljon SMS-ben, ha nem tud utazni.",
    "Sent": "Elküldve",
    "Send pickup notice": "Felvételi értesítés küldése",
    "Sent confirmation shown.": "Elküldési visszaigazolás megjelenítve.",
    "This is a demo receipt only. No message left the browser.": "Ez csak demó visszaigazolás. Nem hagyta el üzenet a böngészőt.",
    "Transport context": "Szállítási kontextus",
    "The model supports one worker holding multiple dated shifts with different worksites and transport groups.": "A modell támogatja, hogy egy dolgozónak több dátumozott műszaka legyen eltérő munkaterületekkel és szállítási csoportokkal.",
    "Second shift added": "Második műszak hozzáadva",
    "Add second shift": "Második műszak hozzáadása",
    "Olha's dated shifts": "Olha dátumozott műszakai",
    "The leave record stores dates only. No medical detail is captured in this prototype.": "A távolléti rekord csak dátumokat tárol. A prototípus nem rögzít egészségügyi részletet.",
    "Dates only leave entry": "Csak dátumos távolléti bejegyzés",
    "Leave type": "Távollét típusa",
    "From": "Ettől",
    "To": "Eddig",
    "No medical detail stored.": "Nincs egészségügyi részlet tárolva.",
    "The operational effect is enough: availability flips inactive and shifts in the window are cancelled.": "Az üzemi hatás elég: az elérhetőség inaktívra vált, és az adott időszak műszakai törlődnek.",
    "Sick leave recorded": "Betegszabadság rögzítve",
    "Record sick leave dates": "Betegszabadság dátumainak rögzítése",
    "Worker state": "Dolgozó állapota",
    "Availability changed to inactive.": "Az elérhetőség inaktívra változott.",
    "Both dated shifts in the sick-leave window show cancelled.": "A betegszabadság időszakában mindkét dátumozott műszak töröltként jelenik meg.",
    "Affected shifts": "Érintett műszakok",
    "Farrukh is hired and available, but the required forklift certificate is inside the expiry warning window.": "Farrukh felvett és elérhető, de a szükséges targoncatanúsítvány a lejárati figyelmeztetési időszakon belül van.",
    "Forklift certificate expires in 12 days.": "A targoncatanúsítvány 12 nap múlva lejár.",
    "Expiry date: 25 Jun 2026. Forklift operator shifts require a valid certificate.": "Lejárati dátum: 25 Jun 2026. A targoncavezetői műszakokhoz érvényes tanúsítvány szükséges.",
    "Try assign forklift shift": "Targoncás műszak próbabeosztása",
    "Assignment stopped.": "Kiosztás leállítva.",
    "Forklift operator requires a valid forklift certificate. Pick another worker or update the certificate record.": "A targoncavezetőhöz érvényes targoncatanúsítvány kell. Válasszon másik dolgozót vagy frissítse a tanúsítvány rekordját.",
    "Certificate metadata": "Tanúsítvány-metaadatok",
    "Type": "Típus",
    "Issue date": "Kiadási dátum",
    "Expiry date": "Lejárati dátum",
    "Validity": "Érvényesség",
    "Valid until warning window": "Érvényes a figyelmeztetési időszakig",
    "Document queue": "Dokumentumsor",
    "Document": "Dokumentum",
    "State": "Állapot",
    "Forklift certificate": "Targoncatanúsítvány",
    "Work permit": "Munkavállalási engedély",
    "Expires soon": "Hamarosan lejár",
    "18 days left": "18 nap van hátra",
    "A coordinator can check today's workers, document state, and quick actions from a phone-sized screen.": "A koordinátor telefonméretű képernyőről ellenőrizheti a mai dolgozókat, dokumentumállapotot és gyors műveleteket.",
    "A manager can check today's workers, document state, and quick actions from a phone-sized screen.": "A vezető telefonméretű képernyőről ellenőrizheti a mai dolgozókat, dokumentumállapotot és gyors műveleteket.",
    "Search workers": "Dolgozók keresése",
    "Call": "Hívás",
    "Message": "Üzenet",
    "Marked": "Megjelölve",
    "No-show": "Nem jelent meg",
    "Room occupancy and worker-room assignment. Costs stay out of this demo.": "Szobafoglaltság és dolgozó-szoba kiosztás. A költségek kívül maradnak a demón.",
    "Room": "Szoba",
    "Occupancy": "Foglaltság",
    "Workers": "Dolgozók",
    "Action": "Művelet",
    "Assign worker": "Dolgozó hozzárendelése",
    "Gear and sizes": "Felszerelés és méretek",
    "Issued gear sits beside worker sizes so inventory can be prepared before the shift.": "A kiadott felszerelés a dolgozói méretek mellett van, hogy a készlet műszak előtt előkészíthető legyen.",
    "Issued gear": "Kiadott felszerelés",
    "Worker sizes": "Dolgozói méretek",
    "Item": "Tétel",
    "Size": "Méret",
    "Helmet": "Sisak",
    "Boots": "Bakancs",
    "Vest": "Mellény",
    "Gloves": "Kesztyű",
    "Issued": "Kiadva",
    "Prepared": "Előkészítve",
    "Returned": "Visszaadva",
    "Standard": "Standard",
    "Read-only accounting sync status for the demo. No connection is attempted.": "Csak olvasható könyvelési szinkronállapot a demóhoz. Kapcsolódás nem történik.",
    "Demo data - connected via Pohoda mServer (XML)": "Demóadat - Pohoda mServeren (XML) keresztül kapcsolva",
    "Placeholder figures only. This browser does not call Pohoda.": "Csak helyőrző számok. Ez a böngésző nem hívja meg a Pohodát.",
    "Open invoices": "Nyitott számlák",
    "Ready payroll rows": "Kész bérsorok",
    "Last XML import": "Utolsó XML import",
    "Sync warnings": "Szinkron figyelmeztetések",
    "Mocked": "Minta",
    "Use this screen after the walkthrough to read captured decisions and operational signals.": "Ezt a képernyőt a bejárás után használja a rögzített döntések és üzemi jelek áttekintésére.",
    "Decisions": "Döntések",
    "Operational report": "Üzemi jelentés",
    "Open manager field view": "Vezetői terepi nézet megnyitása",
    "Ukraine": "Ukrajna",
    "Uzbekistan": "Üzbegisztán",
    "Vietnam": "Vietnám",
    "Worksite A - Nitra warehouse": "A munkaterület - nyitrai raktár",
    "Worksite B - Trnava site": "B munkaterület - nagyszombati telephely",
    "Worksite A": "A munkaterület",
    "General laborer": "Általános munkás",
    "Bus 2, Nitra depot, 06:15": "2-es busz, nyitrai depó, 06:15",
    "Bus 1, Trnava station, 10:40": "1-es busz, nagyszombati állomás, 10:40",
    "Bus 2, 06:15, Nitra depot": "2-es busz, 06:15, nyitrai depó",
    "Bus 1, 10:40, Trnava station": "1-es busz, 10:40, nagyszombati állomás",
    "Own transport": "Saját közlekedés",
    "Work permit expires in 18 days": "Munkavállalási engedély 18 nap múlva lejár",
    "Forklift cert expires 25 Jun 2026": "Targoncaigazolvány lejár: 25 Jun 2026",
    "Residence card valid": "Tartózkodási kártya érvényes",
    "Profile archived": "Profil archiválva",
    "Hired after work test": "Próbanap után felvéve",
    "Room 12": "12-es szoba",
    "Room 14": "14-es szoba",
    "Room 18": "18-as szoba",
    "3/4 beds": "3/4 ágy",
    "2/4 beds": "2/4 ágy",
    "4/4 beds": "4/4 ágy",
    "Full": "Tele",
    "None": "Nincs",
    "Not recorded": "Nincs rögzítve",
    "Pending issue": "Kiadásra vár",
    "Vest, helmet, gloves": "Mellény, sisak, kesztyű",
    "Helmet, boots": "Sisak, bakancs",
    "Vest, gloves": "Mellény, kesztyű",
    "Shirt M / trousers 40 / boots 39": "Póló M / nadrág 40 / bakancs 39",
    "Shirt L / trousers 42 / boots 43": "Póló L / nadrág 42 / bakancs 43",
    "Shirt S / trousers 38 / boots 40": "Póló S / nadrág 38 / bakancs 40",
    "Shirt S / trousers 36 / boots 38": "Póló S / nadrág 36 / bakancs 38",
    "Shirt XL / trousers 46 / boots 44": "Póló XL / nadrág 46 / bakancs 44",
    "Dashboard opened for today's staffing picture.": "Megnyílt az áttekintés a mai létszámképhez.",
    "Forklift certificate alert queued for Farrukh Yusupov.": "Targoncatanúsítvány-figyelmeztetés sorba állítva Farrukh Yusupovhoz.",
    "Blacklist review queue contains one returnee.": "A tiltólista ellenőrzési sora egy visszatérőt tartalmaz.",
    "Demand model: option A recorded.": "Igénymodell: A opció rögzítve.",
    "Demand model: option B recorded.": "Igénymodell: B opció rögzítve.",
    "Transport capacity: option A recorded.": "Szállítási kapacitás: A opció rögzítve.",
    "Transport capacity: option B recorded.": "Szállítási kapacitás: B opció rögzítve.",
    "Certificate storage: option A recorded.": "Tanúsítványtárolás: A opció rögzítve.",
    "Certificate storage: option B recorded.": "Tanúsítványtárolás: B opció rögzítve.",
    "Bohdan Marchenko saved as Recruit with manager review flag. Activation remains blocked.": "Bohdan Marchenko jelöltként mentve vezetői ellenőrzési jelzéssel. Az aktiválás blokkolva marad.",
    "Work test scheduled for Tran Van Minh.": "Próbanap ütemezve Tran Van Minh számára.",
    "Recruiter recommended Tran Van Minh for hire.": "A toborzó felvételre ajánlotta Tran Van Minht.",
    "Manager approved Tran Van Minh. Hire status changed from Recruit to Hired.": "A vezető jóváhagyta Tran Van Minht. A felvételi státusz jelöltről felvettre változott.",
    "Olha Tkachenko assigned to Worksite A with Bus 2 pickup.": "Olha Tkachenko az A munkaterületre beosztva 2-es buszos felvétellel.",
    "Pickup notice marked sent for Olha Tkachenko. Demo only, no SMS sent.": "Olha Tkachenko felvételi értesítése elküldöttként jelölve. Csak demó, SMS nem ment ki.",
    "Second same-day shift added for Olha Tkachenko at Worksite B.": "Második aznapi műszak hozzáadva Olha Tkachenko számára a B munkaterületen.",
    "Sick leave dates recorded for Olha Tkachenko. Availability changed to Inactive.": "Olha Tkachenko betegszabadság-dátumai rögzítve. Az elérhetőség inaktívra váltott.",
    "Forklift assignment stopped for Farrukh Yusupov because required certificate is expiring.": "Farrukh Yusupov targoncás beosztása leállítva, mert a szükséges tanúsítvány lejáróban van.",
    "Manager marked a field no-show from the mobile view.": "A vezető a mobil nézetből terepi meg nem jelenést jelölt."
  });

  const recruiterPermissions = new Set([
    "createPerson",
    "scheduleTest",
    "recommendHire",
    "assignShift",
    "sendSms",
    "recordSickLeave",
    "uploadDocs"
  ]);

  const tabGroups = [
    {
      id: "operations",
      label: "Operations",
      defaultView: "dashboard",
      views: [
        { label: "Board", view: "dashboard" },
        { label: "Demand", view: "requests" },
        { label: "Shifts", view: "shifts" },
        { label: "SMS pickup", view: "sms" },
        { label: "Second shift", view: "second-shift" },
        { label: "Field mode", view: "field" }
      ]
    },
    {
      id: "people",
      label: "People",
      defaultView: "people",
      views: [
        { label: "Roster scan", view: "people" },
        { label: "Approvals", view: "approvals" }
      ]
    },
    {
      id: "compliance",
      label: "Compliance",
      defaultView: "documents",
      views: [
        { label: "Documents", view: "documents" },
        { label: "Sick leave", view: "sick-leave" }
      ]
    },
    {
      id: "logistics",
      label: "Logistics",
      defaultView: "accommodation",
      views: [
        { label: "Accommodation", view: "accommodation" },
        { label: "Equipment", view: "equipment" }
      ]
    },
    {
      id: "accounting",
      label: "Accounting",
      defaultView: "pohoda",
      views: [
        { label: "Pohoda", view: "pohoda" }
      ]
    },
    {
      id: "reports",
      label: "Reports",
      defaultView: "reports",
      views: [
        { label: "Review", view: "reports" }
      ]
    }
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
    { id: "field", label: "Manager field view", view: "field", meta: "Mobile" }
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
  const coordinatorViews = new Set(["shifts", "sms", "second-shift", "accommodation", "equipment"]);
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

  function localizeTree(scope) {
    if (state.language === "en") {
      return;
    }
    const dictionary = translations[state.language] || {};
    const textNodes = [];
    const walker = document.createTreeWalker(scope, NodeFilter.SHOW_TEXT);
    while (walker.nextNode()) {
      textNodes.push(walker.currentNode);
    }
    textNodes.forEach((node) => {
      const original = node.nodeValue;
      const trimmed = original.trim();
      if (trimmed && dictionary[trimmed]) {
        node.nodeValue = original.replace(trimmed, dictionary[trimmed]);
      }
    });
    scope.querySelectorAll("[data-label], [aria-label], [title]").forEach((node) => {
      ["data-label", "aria-label", "title"].forEach((attribute) => {
        const value = node.getAttribute(attribute);
        if (value && dictionary[value]) {
          node.setAttribute(attribute, dictionary[value]);
        }
      });
    });
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

  function isViewAllowed(view) {
    return !isCoordinator() || coordinatorViews.has(view);
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

  function visibleTabGroups() {
    if (!isCoordinator()) {
      return tabGroups;
    }
    return tabGroups
      .map((group) => {
        const views = group.views.filter((item) => coordinatorViews.has(item.view));
        if (!views.length) {
          return null;
        }
        return { ...group, defaultView: views[0].view, views };
      })
      .filter(Boolean);
  }

  function visibleTourSteps() {
    return tourSteps.filter((step) => !isCoordinator() || step.view === "login" || coordinatorViews.has(step.view));
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
    const title = disabled ? t("Action unavailable for current role.") : "";
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
    return `
      <header class="topbar">
        <button class="brand ghost-button" data-action="go-step" data-step="1" aria-label="Go to dashboard">
          <span class="brand-mark" aria-hidden="true">
            <img src="assets/logo.png" alt="Jober" class="brand-logo-img">
          </span>
          <span class="brand-text">
            <span class="brand-name">${escapeHtml(brand.wordmark)}</span>
            <span class="brand-subtitle">${escapeHtml(brand.subtitle)}</span>
          </span>
        </button>
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
          <button class="toolbar-button compact-button" data-action="toggle-decisions">${escapeHtml(t("Decisions captured"))}</button>
          <button class="toolbar-button compact-button" data-action="start-demo">${escapeHtml(t("Start"))}</button>
          <span class="avatar" aria-label="Presenter avatar">${state.role.slice(0, 2).toUpperCase()}</span>
        </div>
        ${renderRoleSwitch("mobile-role-control")}
        ${renderLanguageSwitch("mobile-language-control")}
      </header>
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

  function activeGroup() {
    const groups = visibleTabGroups();
    return groups.find((group) => group.views.some((item) => item.view === state.view)) || groups[0];
  }

  function renderFolderTabs() {
    const groups = visibleTabGroups();
    const currentGroup = activeGroup();
    return `
      <nav class="folder-tabs" aria-label="Jober folders">
        ${groups.map((group) => `
          <button class="folder-tab ${currentGroup.id === group.id ? "is-active" : ""}" data-action="nav" data-view="${group.defaultView}" aria-pressed="${currentGroup.id === group.id}">
            ${escapeHtml(t(group.label))}
          </button>
        `).join("")}
      </nav>
      <nav class="sub-tabs" aria-label="${escapeHtml(currentGroup.label)} sections">
        ${currentGroup.views.map((item) => `
          <button class="sub-tab ${state.view === item.view ? "is-active" : ""}" data-action="nav" data-view="${item.view}" aria-pressed="${state.view === item.view}">
            ${escapeHtml(t(item.label))}
          </button>
        `).join("")}
      </nav>
    `;
  }

  function renderStepBar() {
    const steps = visibleTourSteps();
    const visibleIndex = Math.max(0, currentVisibleStepIndex());
    return `
      <section class="step-bar" aria-label="Guided demo progress">
        <div class="step-track">
          ${steps.map((step) => {
            const index = tourSteps.indexOf(step);
            const done = index < state.currentStep;
            const current = index === state.currentStep;
            return `
              <button class="step-dot ${done ? "is-done" : ""} ${current ? "is-current" : ""}" data-action="go-step" data-step="${index}" aria-current="${current ? "step" : "false"}" title="${escapeHtml(step.label)}">
                <span>${steps.indexOf(step) + 1}</span>
                <strong>${escapeHtml(t(step.label))}</strong>
              </button>
            `;
          }).join("")}
        </div>
        <div class="step-actions">
          <button class="toolbar-button" data-action="prev-step" ${visibleIndex <= 0 ? "disabled" : ""}>${escapeHtml(t("Back"))}</button>
          <button class="toolbar-button" data-action="next-step" ${nextIsDisabled() ? "disabled" : ""}>${escapeHtml(t("Next"))}</button>
        </div>
      </section>
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
      return t("Can manage transport, accommodation, and equipment logistics.");
    }
    return t("Read-only view. Action buttons are disabled for meeting review.");
  }

  function renderRoleNotice() {
    return `
      <section class="role-strip" aria-label="Current role">
        <strong>${escapeHtml(t(state.role))}</strong>
        <span>${escapeHtml(roleDescription())}</span>
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
    return `
      ${renderTopbar()}
      <main class="login-stage">
        <section class="login-visual" aria-label="Operational route preview">
          <div>
            <p class="eyebrow">Presenter entry</p>
            <h1 class="login-title">${escapeHtml(brand.wordmark)} ${escapeHtml(t("workforce folders"))}</h1>
            <p class="page-lede">A static meeting prototype for dispatch, people files, compliance, logistics, and accounting signals.</p>
          </div>
          <div class="login-hero-wrap">
            <img src="assets/hero.png" alt="Jober Workforce Folders" class="login-hero-img">
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
              <input type="email" value="manager@example.test" aria-label="Email">
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
      <div class="folder-shell">
        ${renderFolderTabs()}
        ${renderStepBar()}
        ${renderRoleNotice()}
        <main class="main-content" id="main-content">
          ${renderCurrentView()}
        </main>
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
        ${renderPageHeader("Operations", "Daily control board", "The meeting starts from dispatch pressure: who is working, what is expiring, and what needs a manager decision.")}
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
        ${renderPageHeader("Decision 1", "Demand intake", "Help us confirm how demand enters the board before recruiters fill the work.")}
        <section class="section">
          <div class="three-up">
            <div><p class="field-label">Partner</p><strong>${escapeHtml(request.name)}</strong></div>
            <div><p class="field-label">Need</p><strong>${request.workersNeeded} ${escapeHtml(t("workers"))}</strong></div>
            <div><p class="field-label">Worksite</p><strong>${escapeHtml(request.worksite)}</strong></div>
          </div>
        </section>
        ${renderDecision("demand")}
        <section class="section">
          <h2 class="section-title">Next move</h2>
          <p class="muted">Whichever model the team picks, the demo continues into the same shift and transport flow.</p>
          <button class="primary-button" data-action="next-step" ${state.decisionChoices.demand ? "" : "disabled"}>Continue to risk check</button>
        </section>
      </section>
    `;
  }

  function renderPeople() {
    return `
      <section class="page">
        ${renderPageHeader("People", "Worker file scan", "The headline moment: the recruiter starts adding a returnee and the blacklist gate catches it before activation.")}
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
        ${renderPageHeader("People", "Trial shift decision", "Recruiters can recommend a candidate. Managers make the hire decision and the audit trail records it.")}
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
        ${renderPageHeader("Operations", "Dispatch plan", isCoordinator() ? "Transport logistics view: assigned worksite, dated shift, vehicle, pickup point, and time." : "Once hired, a worker is directly shift-eligible. The assignment ties the dated shift to a worksite, vehicle, pickup point, and time.")}
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
        ${renderPageHeader("Operations", "Pickup message", "The demo composes the message and records a fake sent state. No SMS is actually sent.")}
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
        ${renderPageHeader("Operations", "Second dispatch slot", "The model supports one worker holding multiple dated shifts with different worksites and transport groups.")}
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
        ${renderPageHeader("Compliance", "Leave dates set inactive", "The leave record stores dates only. No medical detail is captured in this prototype.")}
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
        ${renderPageHeader("Compliance", "Certificate expiry stop", "Farrukh is hired and available, but the required forklift certificate is inside the expiry warning window.")}
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
        ${renderPageHeader("Operations", "Field mode", "A manager can check today's workers, document state, and quick actions from a phone-sized screen.")}
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

  function renderAccommodation() {
    return `
      <section class="page">
        ${renderPageHeader("Logistics", "Accommodation board", "Room occupancy and worker-room assignment. Costs stay out of this demo.")}
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
    return `
      <section class="page">
        ${renderPageHeader("Logistics", "Gear and sizes", "Issued gear sits beside worker sizes so inventory can be prepared before the shift.")}
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
    return `
      <section class="page">
        ${renderPageHeader("Accounting", "Pohoda snapshot", "Read-only accounting sync status for the demo. No connection is attempted.")}
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
          <p class="metric-label">${escapeHtml(t(label))}</p>
          <p class="metric-note">${escapeHtml(t(note))}</p>
        </span>
      </div>
    `;
  }

  function renderReports() {
    return `
      <section class="page">
        ${renderPageHeader("Reports", "Decision review", "Use this screen after the walkthrough to read captured decisions and operational signals.")}
        <div class="split">
          <section class="section">
            <h2 class="section-title">Decisions</h2>
            <div class="decision-summary">
              ${Object.entries(decisions).map(([key, decision]) => {
                const choiceKey = state.decisionChoices[key];
                const choice = choiceKey ? decision.options[choiceKey] : null;
                return `<div class="decision-summary-item"><strong>${escapeHtml(t(decision.title))}</strong><p>${choice ? `${escapeHtml(choiceKey)} - ${escapeHtml(t(choice.label))}` : escapeHtml(t("Pending"))}</p></div>`;
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
    return `<p><strong>${escapeHtml(t(label))}:</strong> <span class="mono">${escapeHtml(value)}</span></p>`;
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
          <li class="audit-item"><span class="audit-time">${escapeHtml(item.time)}</span><span>${escapeHtml(t(item.text))}</span></li>
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
        localizeTree(preview);
      }
    }
  }

  function render() {
    normalizeRoleView();
    root.innerHTML = state.view === "login" ? renderLogin() : renderShell();
    localizeTree(root);
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
