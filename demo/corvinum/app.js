(() => {
  "use strict";

  const brand = {
    wordmark: "CorvinumEU",
    subtitle: "HR operations"
  };

  const roles = ["Recruiter", "Manager", "Observer"];

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
      "Observer": "Pozorovateľ",
      "Decisions captured": "Zachytené rozhodnutia",
      "Start guided demo": "Spustiť sprievodcu",
      "Start": "Štart",
      "Back": "Späť",
      "Next": "Ďalej",
      "Menu": "Menu",
      "Close": "Zavrieť",
      "Workspace": "Pracovisko",
      "Core workspace": "Hlavné pracovisko",
      "Permission model": "Model oprávnení",
      "Can approve hires, verify documents, demote, blacklist, and run field actions.": "Môže schvaľovať prijatia, overovať dokumenty, meniť statusy, pridávať na čiernu listinu a robiť terénne akcie.",
      "Can create people, schedule tests, assign shifts, send pickup notices, and upload documents.": "Môže vytvárať ľudí, plánovať skúšky, priraďovať zmeny, posielať pokyny na vyzdvihnutie a nahrávať dokumenty.",
      "Read-only view. Action buttons are disabled for meeting review.": "Režim iba na čítanie. Akčné tlačidlá sú vypnuté pre kontrolu na stretnutí.",
      "Live manifest": "Živý manifest",
      "Eleven-stop worker journey.": "Jedenásťkroková cesta pracovníka.",
      "Dashboard": "Prehľad",
      "People": "Ľudia",
      "Staffing requests": "Požiadavky na obsadenie",
      "Shifts & transport": "Zmeny a doprava",
      "Documents": "Dokumenty",
      "Approvals": "Schválenia",
      "Reports": "Reporty",
      "Sign in": "Prihlásiť sa",
      "Auth facade": "Ukážkové prihlásenie",
      "Manager dashboard": "Manažérsky prehľad",
      "Today": "Dnes",
      "Demand decision": "Rozhodnutie o dopyte",
      "Decision 1": "Rozhodnutie 1",
      "Risk check": "Kontrola rizika",
      "Blacklist gate": "Brána čiernej listiny",
      "Work test approval": "Schválenie pracovnej skúšky",
      "Role switch": "Prepínač roly",
      "Shift + transport": "Zmena + doprava",
      "Decision 2": "Rozhodnutie 2",
      "Pickup SMS": "SMS na vyzdvihnutie",
      "Fake send": "Falošné odoslanie",
      "Second shift": "Druhá zmena",
      "Same day": "Ten istý deň",
      "Sick leave": "PN",
      "Dates only": "Iba dátumy",
      "Certificate stop": "Zastavenie certifikátu",
      "Decision 3": "Rozhodnutie 3",
      "Manager field view": "Terénny pohľad manažéra",
      "Mobile": "Mobil",
      "Presenter entry": "Vstup prezentujúceho",
      "workforce control": "riadenie pracovnej sily",
      "A static meeting prototype for staffing requests, people, shifts, transport, documents, and risk gates.": "Statický prototyp na stretnutie pre požiadavky, ľudí, zmeny, dopravu, dokumenty a rizikové brány.",
      "Cosmetic sign in": "Ukážkové prihlásenie",
      "Open the live demo": "Otvoriť živé demo",
      "Email": "E-mail",
      "Password": "Heslo",
      "Privileged roles would use 2FA here. This demo does not authenticate or send anything.": "Privilegované roly by tu použili 2FA. Toto demo neoveruje identitu ani nič neposiela.",
      "The meeting starts from the operational picture: who is working, what is expiring, and what needs a manager decision.": "Stretnutie začína prevádzkovým obrazom: kto pracuje, čo expiruje a čo potrebuje rozhodnutie manažéra.",
      "Working now": "Práve pracujú",
      "Olha is active on Worksite A.": "Olha je aktívna na pracovisku A.",
      "Docs expiring": "Dokumenty expirujú",
      "Forklift and work permit alerts.": "Upozornenia na vysokozdvižný vozík a pracovné povolenie.",
      "Blacklist queue": "Front čiernej listiny",
      "One returnee needs review.": "Jeden navrátilec potrebuje kontrolu.",
      "Hire approvals": "Schválenia prijatia",
      "Tran waits for manager approval.": "Tran čaká na schválenie manažérom.",
      "Today's manifest": "Dnešný manifest",
      "Recent audit": "Nedávny audit",
      "Staffing request": "Požiadavka na obsadenie",
      "Help us confirm how this request enters the system before recruiters fill the work.": "Pomôžte nám potvrdiť, ako sa požiadavka dostane do systému pred obsadením práce.",
      "Partner": "Partner",
      "Need": "Potreba",
      "Worksite": "Pracovisko",
      "Next in the story": "Ďalší krok príbehu",
      "Whichever model the client picks, the demo continues into the same shift and transport flow.": "Nech si tím vyberie ktorýkoľvek model, demo pokračuje do rovnakého toku zmien a dopravy.",
      "Continue to risk check": "Pokračovať na kontrolu rizika",
      "Roster and live risk check": "Zoznam a živá kontrola rizika",
      "The headline moment: the recruiter starts adding a returnee and the blacklist gate catches it before activation.": "Hlavný moment: náborár začne pridávať navrátilca a brána čiernej listiny ho zachytí pred aktiváciou.",
      "Add person": "Pridať osobu",
      "Name or identifier": "Meno alebo identifikátor",
      "Country": "Krajina",
      "Initial status": "Počiatočný status",
      "Recruit, activation gated": "Kandidát, aktivácia blokovaná",
      "People roster": "Zoznam ľudí",
      "Person": "Osoba",
      "Status": "Status",
      "Document state": "Stav dokumentu",
      "Contact": "Kontakt",
      "Worker": "Pracovník",
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
      "Record only": "Iba zaznamenať",
      "Allow the assignment and record that transport is over capacity.": "Povoliť priradenie a zaznamenať prekročenie kapacity.",
      "Certificate storage": "Ukladanie certifikátov",
      "What should be stored for certificates?": "Čo sa má ukladať pri certifikátoch?",
      "Store the file": "Uložiť súbor",
      "Upload and keep the certificate document alongside type and expiry.": "Nahrať a ponechať dokument certifikátu spolu s typom a expiráciou.",
      "Dates only": "Iba dátumy",
      "Store certificate type and expiry date, with no file retained.": "Uložiť typ certifikátu a dátum expirácie bez uchovania súboru.",
      "Help us confirm how you actually work": "Pomôžte nám potvrdiť, ako naozaj pracujete",
      "Recorded": "Zaznamenané",
      "Observer read-only": "Pozorovateľ iba číta",
      "Awaiting choice": "Čaká na výber",
      "No choice recorded yet.": "Zatiaľ nie je zaznamenaný výber.",
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
      "Observer": "Megfigyelő",
      "Decisions captured": "Rögzített döntések",
      "Start guided demo": "Vezetett demó indítása",
      "Start": "Indítás",
      "Back": "Vissza",
      "Next": "Tovább",
      "Menu": "Menü",
      "Close": "Bezárás",
      "Workspace": "Munkaterület",
      "Core workspace": "Fő munkaterület",
      "Permission model": "Jogosultsági modell",
      "Can approve hires, verify documents, demote, blacklist, and run field actions.": "Jóváhagyhat felvételeket, ellenőrizhet dokumentumokat, módosíthat státuszt, tiltólistázhat és terepi műveleteket végezhet.",
      "Can create people, schedule tests, assign shifts, send pickup notices, and upload documents.": "Létrehozhat dolgozókat, teszteket ütemezhet, műszakokat oszthat be, felvételi értesítést küldhet és dokumentumokat tölthet fel.",
      "Read-only view. Action buttons are disabled for meeting review.": "Csak olvasható nézet. A műveleti gombok ki vannak kapcsolva a megbeszéléshez.",
      "Live manifest": "Élő manifest",
      "Eleven-stop worker journey.": "Tizenegy lépéses dolgozói út.",
      "Dashboard": "Áttekintés",
      "People": "Dolgozók",
      "Staffing requests": "Munkaerőigények",
      "Shifts & transport": "Műszakok és szállítás",
      "Documents": "Dokumentumok",
      "Approvals": "Jóváhagyások",
      "Reports": "Jelentések",
      "Sign in": "Bejelentkezés",
      "Auth facade": "Belépési minta",
      "Manager dashboard": "Vezetői áttekintés",
      "Today": "Ma",
      "Demand decision": "Igénydöntés",
      "Decision 1": "1. döntés",
      "Risk check": "Kockázatellenőrzés",
      "Blacklist gate": "Tiltólista kapu",
      "Work test approval": "Próbanap jóváhagyása",
      "Role switch": "Szerepváltó",
      "Shift + transport": "Műszak + szállítás",
      "Decision 2": "2. döntés",
      "Pickup SMS": "Felvételi SMS",
      "Fake send": "Minta küldés",
      "Second shift": "Második műszak",
      "Same day": "Ugyanaz a nap",
      "Sick leave": "Betegszabadság",
      "Dates only": "Csak dátumok",
      "Certificate stop": "Tanúsítvány stop",
      "Decision 3": "3. döntés",
      "Manager field view": "Vezetői terepi nézet",
      "Mobile": "Mobil",
      "Presenter entry": "Prezentálói belépés",
      "workforce control": "munkaerő-irányítás",
      "A static meeting prototype for staffing requests, people, shifts, transport, documents, and risk gates.": "Statikus tárgyalási prototípus munkaerőigényekhez, dolgozókhoz, műszakokhoz, szállításhoz, dokumentumokhoz és kockázati kapukhoz.",
      "Cosmetic sign in": "Minta bejelentkezés",
      "Open the live demo": "Élő demó megnyitása",
      "Email": "E-mail",
      "Password": "Jelszó",
      "Privileged roles would use 2FA here. This demo does not authenticate or send anything.": "A kiemelt szerepek itt 2FA-t használnának. Ez a demó nem hitelesít és nem küld semmit.",
      "The meeting starts from the operational picture: who is working, what is expiring, and what needs a manager decision.": "A megbeszélés az üzemi képpel indul: ki dolgozik, mi jár le, és mi igényel vezetői döntést.",
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
      "Staffing request": "Munkaerőigény",
      "Help us confirm how this request enters the system before recruiters fill the work.": "Segítsen megerősíteni, hogyan kerül az igény a rendszerbe, mielőtt a toborzók betöltik a munkát.",
      "Partner": "Partner",
      "Need": "Igény",
      "Worksite": "Munkaterület",
      "Next in the story": "Következő lépés",
      "Whichever model the client picks, the demo continues into the same shift and transport flow.": "Bármelyik modellt választja a csapat, a demó ugyanabba a műszak- és szállítási folyamatba lép tovább.",
      "Continue to risk check": "Tovább a kockázatellenőrzéshez",
      "Roster and live risk check": "Névsor és élő kockázatellenőrzés",
      "The headline moment: the recruiter starts adding a returnee and the blacklist gate catches it before activation.": "A fő pillanat: a toborzó visszatérőt kezd rögzíteni, és a tiltólista kapu még aktiválás előtt megfogja.",
      "Add person": "Személy hozzáadása",
      "Name or identifier": "Név vagy azonosító",
      "Country": "Ország",
      "Initial status": "Kezdő státusz",
      "Recruit, activation gated": "Jelölt, aktiválás blokkolva",
      "People roster": "Dolgozói névsor",
      "Person": "Személy",
      "Status": "Státusz",
      "Document state": "Dokumentumállapot",
      "Contact": "Kapcsolat",
      "Worker": "Dolgozó",
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
      "Record only": "Csak rögzítés",
      "Allow the assignment and record that transport is over capacity.": "A beosztás engedélyezése és a kapacitástúllépés rögzítése.",
      "Certificate storage": "Tanúsítványtárolás",
      "What should be stored for certificates?": "Mit kell tárolni a tanúsítványoknál?",
      "Store the file": "Fájl tárolása",
      "Upload and keep the certificate document alongside type and expiry.": "A tanúsítvány dokumentumának feltöltése és megőrzése típussal és lejárattal együtt.",
      "Dates only": "Csak dátumok",
      "Store certificate type and expiry date, with no file retained.": "A tanúsítvány típusának és lejáratának tárolása fájl nélkül.",
      "Help us confirm how you actually work": "Segítsen megerősíteni, hogyan dolgoznak valójában",
      "Recorded": "Rögzítve",
      "Observer read-only": "Megfigyelő csak olvas",
      "Awaiting choice": "Választásra vár",
      "No choice recorded yet.": "Még nincs rögzített választás.",
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
    "HR operations": "HR prevádzka",
    "Go to dashboard": "Prejsť na prehľad",
    "Presenter avatar": "Avatar prezentujúceho",
    "Guided demo manifest": "Manifest sprievodcu",
    "Guided demo progress": "Priebeh sprievodcu",
    "Operational route preview": "Náhľad prevádzkovej trasy",
    "Primary": "Primárne",
    "Phone frame": "Rám telefónu",
    "Action unavailable for current role.": "Akcia nie je dostupná pre aktuálnu rolu.",
    "Current role": "Aktuálna rola",
    "Request": "Požiadavka",
    "Pickup": "Vyzdvihnutie",
    "Gate": "Brána",
    "Cert": "Certifikát",
    "Workers to Nitra": "Pracovníci do Nitry",
    "Bus 2, Nitra depot": "Autobus 2, depo Nitra",
    "Blacklist review": "Kontrola čiernej listiny",
    "Forklift expiry": "Expirácia VZV",
    "workers": "pracovníkov",
    "Today's manifest": "Dnešný manifest",
    "Recent audit": "Nedávny audit",
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
    "Approval gate": "Schvaľovacia brána",
    "Work test and hire approval": "Pracovná skúška a schválenie prijatia",
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
    "Assign shift and transport": "Priradiť zmenu a dopravu",
    "Olha is hired. The assignment ties the dated shift to a worksite, position, bus, pickup point, and time.": "Olha je prijatá. Priradenie spája dátumovanú zmenu s pracoviskom, pozíciou, autobusom, miestom vyzdvihnutia a časom.",
    "Worker header": "Hlavička pracovníka",
    "Position": "Pozícia",
    "Transport group": "Dopravná skupina",
    "Bus 2 capacity": "Kapacita autobusu 2",
    "Driver Tomas V., pickup Nitra depot, 06:15.": "Vodič Tomas V., vyzdvihnutie depo Nitra, 06:15.",
    "Capacity enforced.": "Kapacita vynútená.",
    "Bus 2 is full after Olha. A future assignment would be blocked.": "Autobus 2 je po Olhe plný. Ďalšie priradenie by bolo blokované.",
    "Capacity recorded only.": "Kapacita iba zaznamenaná.",
    "The demo shows how an over-capacity transport row would be flagged, not blocked.": "Demo ukazuje, ako by sa riadok dopravy nad kapacitu označil, nie blokoval.",
    "Shift table": "Tabuľka zmien",
    "Assigned to shift": "Priradené na zmenu",
    "Assign to shift": "Priradiť na zmenu",
    "8 / 9 booked": "8 / 9 rezervované",
    "9 / 9 full": "9 / 9 plné",
    "10 / 9 recorded": "10 / 9 zaznamenané",
    "SMS channel": "SMS kanál",
    "Pickup notice": "Pokyn na vyzdvihnutie",
    "The demo composes the message and records a fake sent state. No SMS is actually sent.": "Demo zostaví správu a zaznamená falošný stav odoslania. Žiadna SMS sa skutočne neposiela.",
    "Primary channel: SMS, because many workers do not reliably use email.": "Primárny kanál: SMS, pretože mnohí pracovníci nepoužívajú e-mail spoľahlivo.",
    "Olha, your pickup is Bus 2 at 06:15 from Nitra depot for Worksite A - Nitra warehouse. Reply by SMS if you cannot travel.": "Olha, vyzdvihnutie je autobusom 2 o 06:15 z depa Nitra na Pracovisko A - sklad Nitra. Ak nemôžete cestovať, odpovedzte SMS.",
    "Sent": "Odoslané",
    "Send pickup notice": "Odoslať pokyn na vyzdvihnutie",
    "Sent confirmation shown.": "Zobrazené potvrdenie odoslania.",
    "This is a demo receipt only. No message left the browser.": "Toto je iba demo potvrdenie. Žiadna správa neopustila prehliadač.",
    "Transport context": "Kontext dopravy",
    "Same worker, same day": "Rovnaký pracovník, rovnaký deň",
    "Add second shift": "Pridať druhú zmenu",
    "The model supports one worker holding multiple dated shifts with different worksites and transport groups.": "Model podporuje jedného pracovníka s viacerými dátumovanými zmenami na rôznych pracoviskách a v rôznych dopravných skupinách.",
    "Second shift added": "Druhá zmena pridaná",
    "Olha's dated shifts": "Dátumované zmeny Olhy",
    "Availability": "Dostupnosť",
    "Sick leave sets inactive": "PN nastaví neaktívny stav",
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
    "Certificate expiry hard-stop": "Tvrdé zastavenie pri expirácii certifikátu",
    "Farrukh is hired and available, but the required forklift certificate is inside the expiry warning window.": "Farrukh je prijatý a dostupný, ale požadovaný certifikát na VZV je v expiračnom varovnom okne.",
    "Forklift certificate expires in 12 days.": "Certifikát na VZV expiruje o 12 dní.",
    "Expiry date: 25 Jun 2026. Forklift operator shifts require a valid certificate.": "Dátum expirácie: 25 Jun 2026. Zmeny operátora VZV vyžadujú platný certifikát.",
    "Try assign forklift shift": "Skúsiť priradiť zmenu VZV",
    "Assignment stopped.": "Priradenie zastavené.",
    "Forklift operator requires a valid forklift certificate. Pick another worker or update the certificate record.": "Operátor VZV vyžaduje platný certifikát. Vyberte iného pracovníka alebo aktualizujte záznam certifikátu.",
    "Document queue": "Front dokumentov",
    "Document": "Dokument",
    "State": "Stav",
    "Forklift certificate": "Certifikát na VZV",
    "Work permit": "Pracovné povolenie",
    "Expires soon": "Čoskoro expiruje",
    "18 days left": "Zostáva 18 dní",
    "Mobile manager": "Mobilný manažér",
    "Field view": "Terénny pohľad",
    "A coordinator can check today's workers, document state, and quick actions from a phone-sized screen.": "Koordinátor môže z obrazovky veľkosti telefónu skontrolovať dnešných pracovníkov, stav dokumentov a rýchle akcie.",
    "Search workers": "Hľadať pracovníkov",
    "Call": "Volať",
    "Message": "Správa",
    "Marked": "Označené",
    "No-show": "Neúčasť",
    "Meeting review": "Rekapitulácia stretnutia",
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
    "Contract ended": "Zmluva ukončená",
    "Hired after work test": "Prijatý po pracovnej skúške",
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
    "HR operations": "HR műveletek",
    "Go to dashboard": "Ugrás az áttekintésre",
    "Presenter avatar": "Prezentáló avatárja",
    "Guided demo manifest": "Vezetett demó manifest",
    "Guided demo progress": "Vezetett demó előrehaladása",
    "Operational route preview": "Műveleti útvonal előnézet",
    "Primary": "Elsődleges",
    "Phone frame": "Telefonkeret",
    "Action unavailable for current role.": "A művelet nem elérhető az aktuális szerepben.",
    "Current role": "Aktuális szerep",
    "Request": "Igény",
    "Pickup": "Felvétel",
    "Gate": "Kapu",
    "Cert": "Tanúsítvány",
    "Workers to Nitra": "Dolgozók Nyitrára",
    "Bus 2, Nitra depot": "2-es busz, nyitrai depó",
    "Blacklist review": "Tiltólista ellenőrzés",
    "Forklift expiry": "Targonca lejárat",
    "workers": "dolgozó",
    "Today's manifest": "Mai manifest",
    "Recent audit": "Friss audit",
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
    "Approval gate": "Jóváhagyási kapu",
    "Work test and hire approval": "Próbanap és felvételi jóváhagyás",
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
    "Assign shift and transport": "Műszak és szállítás kiosztása",
    "Olha is hired. The assignment ties the dated shift to a worksite, position, bus, pickup point, and time.": "Olha felvéve. A kiosztás összeköti a dátumozott műszakot a munkaterülettel, pozícióval, busszal, felvételi ponttal és idővel.",
    "Worker header": "Dolgozói fejléc",
    "Position": "Pozíció",
    "Transport group": "Szállítási csoport",
    "Bus 2 capacity": "2-es busz kapacitása",
    "Driver Tomas V., pickup Nitra depot, 06:15.": "Sofőr Tomas V., felvétel nyitrai depó, 06:15.",
    "Capacity enforced.": "Kapacitás betartva.",
    "Bus 2 is full after Olha. A future assignment would be blocked.": "Olha után a 2-es busz megtelt. Egy későbbi kiosztás blokkolva lenne.",
    "Capacity recorded only.": "Kapacitás csak rögzítve.",
    "The demo shows how an over-capacity transport row would be flagged, not blocked.": "A demó azt mutatja, hogyan lenne a kapacitáson felüli szállítási sor jelölve, nem blokkolva.",
    "Shift table": "Műszaktábla",
    "Assigned to shift": "Műszakra beosztva",
    "Assign to shift": "Műszakra osztás",
    "8 / 9 booked": "8 / 9 foglalt",
    "9 / 9 full": "9 / 9 tele",
    "10 / 9 recorded": "10 / 9 rögzítve",
    "SMS channel": "SMS csatorna",
    "Pickup notice": "Felvételi értesítés",
    "The demo composes the message and records a fake sent state. No SMS is actually sent.": "A demó összeállítja az üzenetet és minta elküldött állapotot rögzít. Valódi SMS nem megy ki.",
    "Primary channel: SMS, because many workers do not reliably use email.": "Elsődleges csatorna: SMS, mert sok dolgozó nem használja megbízhatóan az e-mailt.",
    "Olha, your pickup is Bus 2 at 06:15 from Nitra depot for Worksite A - Nitra warehouse. Reply by SMS if you cannot travel.": "Olha, a felvétel a 2-es busszal 06:15-kor indul a nyitrai depóból az A munkaterület - nyitrai raktár felé. Válaszoljon SMS-ben, ha nem tud utazni.",
    "Sent": "Elküldve",
    "Send pickup notice": "Felvételi értesítés küldése",
    "Sent confirmation shown.": "Elküldési visszaigazolás megjelenítve.",
    "This is a demo receipt only. No message left the browser.": "Ez csak demó visszaigazolás. Nem hagyta el üzenet a böngészőt.",
    "Transport context": "Szállítási kontextus",
    "Same worker, same day": "Ugyanaz a dolgozó, ugyanaz a nap",
    "Add second shift": "Második műszak hozzáadása",
    "The model supports one worker holding multiple dated shifts with different worksites and transport groups.": "A modell támogatja, hogy egy dolgozónak több dátumozott műszaka legyen eltérő munkaterületekkel és szállítási csoportokkal.",
    "Second shift added": "Második műszak hozzáadva",
    "Olha's dated shifts": "Olha dátumozott műszakai",
    "Availability": "Elérhetőség",
    "Sick leave sets inactive": "Betegszabadság inaktívra állít",
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
    "Certificate expiry hard-stop": "Tanúsítvány lejárati blokkolás",
    "Farrukh is hired and available, but the required forklift certificate is inside the expiry warning window.": "Farrukh felvett és elérhető, de a szükséges targoncatanúsítvány a lejárati figyelmeztetési időszakon belül van.",
    "Forklift certificate expires in 12 days.": "A targoncatanúsítvány 12 nap múlva lejár.",
    "Expiry date: 25 Jun 2026. Forklift operator shifts require a valid certificate.": "Lejárati dátum: 25 Jun 2026. A targoncavezetői műszakokhoz érvényes tanúsítvány szükséges.",
    "Try assign forklift shift": "Targoncás műszak próbabeosztása",
    "Assignment stopped.": "Kiosztás leállítva.",
    "Forklift operator requires a valid forklift certificate. Pick another worker or update the certificate record.": "A targoncavezetőhöz érvényes targoncatanúsítvány kell. Válasszon másik dolgozót vagy frissítse a tanúsítvány rekordját.",
    "Document queue": "Dokumentumsor",
    "Document": "Dokumentum",
    "State": "Állapot",
    "Forklift certificate": "Targoncatanúsítvány",
    "Work permit": "Munkavállalási engedély",
    "Expires soon": "Hamarosan lejár",
    "18 days left": "18 nap van hátra",
    "Mobile manager": "Mobil vezető",
    "Field view": "Terepi nézet",
    "A coordinator can check today's workers, document state, and quick actions from a phone-sized screen.": "A koordinátor telefonméretű képernyőről ellenőrizheti a mai dolgozókat, dokumentumállapotot és gyors műveleteket.",
    "Search workers": "Dolgozók keresése",
    "Call": "Hívás",
    "Message": "Üzenet",
    "Marked": "Megjelölve",
    "No-show": "Nem jelent meg",
    "Meeting review": "Megbeszélés áttekintése",
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
    "Contract ended": "Szerződés lezárva",
    "Hired after work test": "Próbanap után felvéve",
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

  const navItems = [
    { id: "dashboard", label: "Dashboard", icon: "D", view: "dashboard" },
    { id: "people", label: "People", icon: "P", view: "people" },
    { id: "requests", label: "Staffing requests", icon: "R", view: "requests" },
    { id: "shifts", label: "Shifts & transport", icon: "S", view: "shifts" },
    { id: "documents", label: "Documents", icon: "C", view: "documents" },
    { id: "approvals", label: "Approvals", icon: "A", view: "approvals" },
    { id: "reports", label: "Reports", icon: "T", view: "reports" }
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
        },
        B: {
          label: "Record only",
          body: "Allow the assignment and record that transport is over capacity."
        }
      }
    },
    cert: {
      title: "Certificate storage",
      question: "What should be stored for certificates?",
      options: {
        A: {
          label: "Store the file",
          body: "Upload and keep the certificate document alongside type and expiry."
        },
        B: {
          label: "Dates only",
          body: "Store certificate type and expiry date, with no file retained."
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
        documentNote: "Residency file reviewed"
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
        document: "Test scheduled"
      },
      {
        id: "dilnoza",
        name: "Dilnoza Karimova",
        scriptName: "Дилноза Каримова",
        country: "Uzbekistan",
        phone: "+421 900 611 203",
        hireStatus: "Hired",
        availability: "Available",
        document: "Residence card valid"
      },
      {
        id: "mykola",
        name: "Mykola Hrytsenko",
        scriptName: "Микола Гриценко",
        country: "Ukraine",
        phone: "+421 900 511 290",
        hireStatus: "Archived",
        availability: "Inactive",
        document: "Contract ended"
      }
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
      transport: null,
      cert: null
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

  function can(permission) {
    if (state.role === "Observer") {
      return false;
    }
    if (state.role === "Manager") {
      return true;
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
    const canOpenNav = state.view !== "login";
    return `
      <header class="topbar">
        <button class="brand ghost-button" data-action="go-step" data-step="1" aria-label="Go to dashboard">
          <span class="brand-mark" aria-hidden="true">
            <span></span><span></span><span></span><span></span><span></span><span></span><span></span><span></span><span></span>
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
          ${canOpenNav ? `<button class="toolbar-button icon-button" data-action="toggle-nav" aria-expanded="${state.navOpen}" aria-controls="mobile-nav">${escapeHtml(t("Menu"))}</button>` : ""}
          <button class="toolbar-button compact-button" data-action="toggle-decisions">${escapeHtml(t("Decisions captured"))}</button>
          <span class="avatar" aria-label="Presenter avatar">${state.role.slice(0, 2).toUpperCase()}</span>
        </div>
      </header>
    `;
  }

  function renderRoleSwitch(extraClass = "") {
    return `
      <div class="topbar-group ${extraClass}" aria-label="Role switch">
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
            <button class="segmented-button ${state.language === language.id ? "is-active" : ""}" data-action="set-language" data-language="${language.id}" aria-pressed="${state.language === language.id}" title="${escapeHtml(t(language.name))}">
              ${escapeHtml(language.label)}
            </button>
          `).join("")}
        </span>
      </div>
    `;
  }

  function nextIsDisabled() {
    if (state.currentStep === tourSteps.length - 1) {
      return true;
    }
    const step = tourSteps[state.currentStep];
    if (step.id === "demand") {
      return !state.decisionChoices.demand;
    }
    if (step.id === "transport") {
      return !state.decisionChoices.transport;
    }
    if (step.id === "cert") {
      return !state.decisionChoices.cert;
    }
    return false;
  }

  function renderSidebar() {
    return `
      <div class="nav-backdrop ${state.navOpen ? "is-open" : ""}" data-action="close-nav" aria-hidden="true"></div>
      <aside class="sidebar ${state.navOpen ? "is-open" : ""}" id="mobile-nav">
        <div class="drawer-header nav-drawer-header">
          <strong>${escapeHtml(t("Workspace"))}</strong>
          <button class="ghost-button" data-action="close-nav">${escapeHtml(t("Close"))}</button>
        </div>
        <div class="drawer-controls">
          ${renderRoleSwitch("drawer-control")}
          ${renderLanguageSwitch("drawer-control")}
          <button class="secondary-button" data-action="start-demo">${escapeHtml(t("Start guided demo"))}</button>
        </div>
        <div class="nav-section-label">${escapeHtml(t("Core workspace"))}</div>
        <nav class="nav-list" aria-label="Primary">
          ${navItems.map((item) => `
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
      return t("Can create people, schedule tests, assign shifts, send pickup notices, and upload documents.");
    }
    return t("Read-only view. Action buttons are disabled for meeting review.");
  }

  function renderManifestRail() {
    return `
      <aside class="manifest-rail" aria-label="Guided demo manifest">
        <h2 class="rail-title">${escapeHtml(t("Live manifest"))}</h2>
        <p class="rail-subtitle">${escapeHtml(t("Eleven-stop worker journey."))}</p>
        <div class="rail-steps">
          ${tourSteps.map((step, index) => {
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
    const current = tourSteps[state.currentStep];
    return `
      <section class="mobile-manifest ${state.manifestOpen ? "is-open" : ""}" aria-label="Guided demo progress">
        <div class="mobile-manifest-top">
          <button class="manifest-toggle" data-action="toggle-manifest" aria-expanded="${state.manifestOpen}">
            <span class="rail-index">${String(state.currentStep + 1).padStart(2, "0")}</span>
            <span class="rail-copy">
              <span class="rail-label">${escapeHtml(t(current.label))}</span>
              <span class="rail-meta">${escapeHtml(t(current.meta))} · ${state.currentStep + 1} / ${tourSteps.length}</span>
            </span>
            <span class="manifest-caret" aria-hidden="true">${state.manifestOpen ? escapeHtml(t("Close")) : escapeHtml(t("Menu"))}</span>
          </button>
          <div class="mobile-tour-actions">
            <button class="toolbar-button" data-action="prev-step" ${state.currentStep === 0 ? "disabled" : ""}>${escapeHtml(t("Back"))}</button>
            <button class="toolbar-button" data-action="next-step" ${nextIsDisabled() ? "disabled" : ""}>${escapeHtml(t("Next"))}</button>
          </div>
        </div>
        <div class="mobile-rail-steps">
          ${tourSteps.map((step, index) => {
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
    return `
      ${renderTopbar()}
      <main class="login-stage">
        <section class="login-visual" aria-label="Operational route preview">
          <div>
            <p class="eyebrow">${escapeHtml(t("Presenter entry"))}</p>
            <h1 class="login-title">${escapeHtml(brand.wordmark)} ${escapeHtml(t("workforce control"))}</h1>
            <p class="page-lede">${escapeHtml(t("A static meeting prototype for staffing requests, people, shifts, transport, documents, and risk gates."))}</p>
          </div>
          <div class="login-route">
            <div class="route-block"><span class="muted">Request</span><strong>12</strong><span>Workers to Nitra</span></div>
            <div class="route-block"><span class="muted">Pickup</span><strong>06:15</strong><span>Bus 2, Nitra depot</span></div>
            <div class="route-block"><span class="muted">Gate</span><strong>1</strong><span>Blacklist review</span></div>
            <div class="route-block"><span class="muted">Cert</span><strong>12d</strong><span>Forklift expiry</span></div>
          </div>
        </section>
        <section class="login-panel">
          <p class="eyebrow">${escapeHtml(t("Cosmetic sign in"))}</p>
          <h2 class="section-title">${escapeHtml(t("Open the live demo"))}</h2>
          <div class="stack">
            <label class="field">
              <span>${escapeHtml(t("Email"))}</span>
              <input type="email" value="manager@example.test" aria-label="Email">
            </label>
            <label class="field">
              <span>${escapeHtml(t("Password"))}</span>
              <input type="password" value="demo-only" aria-label="Password">
            </label>
            <div class="info-strip">${escapeHtml(t("Privileged roles would use 2FA here. This demo does not authenticate or send anything."))}</div>
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
            <div><p class="field-label">${escapeHtml(t("Partner"))}</p><strong>${escapeHtml(request.name)}</strong></div>
            <div><p class="field-label">${escapeHtml(t("Need"))}</p><strong>${request.workersNeeded} ${escapeHtml(t("workers"))}</strong></div>
            <div><p class="field-label">${escapeHtml(t("Worksite"))}</p><strong>${escapeHtml(request.worksite)}</strong></div>
          </div>
        </section>
        ${renderDecision("demand")}
        <section class="section">
          <h2 class="section-title">${escapeHtml(t("Next in the story"))}</h2>
          <p class="muted">${escapeHtml(t("Whichever model the client picks, the demo continues into the same shift and transport flow."))}</p>
          <button class="primary-button" data-action="next-step" ${state.decisionChoices.demand ? "" : "disabled"}>${escapeHtml(t("Continue to risk check"))}</button>
        </section>
      </section>
    `;
  }

  function renderPeople() {
    return `
      <section class="page">
        ${renderPageHeader("People", "Roster and live risk check", "The headline moment: the recruiter starts adding a returnee and the blacklist gate catches it before activation.")}
        <section class="section">
          <h2 class="section-title">${escapeHtml(t("Add person"))}</h2>
          <div class="split">
            <div class="stack">
              <label class="field">
                <span>${escapeHtml(t("Name or identifier"))}</span>
                <input data-input="risk" value="${escapeHtml(state.riskInput)}" autocomplete="off" aria-describedby="risk-result">
              </label>
              <div class="form-grid">
                <div class="field">
                  <span class="field-label">${escapeHtml(t("Country"))}</span>
                  <span class="field-value">Ukraine</span>
                </div>
                <div class="field">
                  <span class="field-label">${escapeHtml(t("Initial status"))}</span>
                  <span class="field-value">${escapeHtml(t("Recruit, activation gated"))}</span>
                </div>
              </div>
            </div>
            <div id="risk-result">${riskResultHtml()}</div>
          </div>
        </section>
        <section class="section">
          <h2 class="section-title">${escapeHtml(t("People roster"))}</h2>
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
        ${renderPageHeader("Decision 2", "Assign shift and transport", "Olha is hired. The assignment ties the dated shift to a worksite, position, bus, pickup point, and time.")}
        <section class="section">
          <div class="split">
            <div class="stack">
              <h2 class="section-title">Worker header</h2>
              <div class="person-name">
                <span>${escapeHtml(olha.name)}</span>
                <span class="script-name">${escapeHtml(olha.scriptName)}</span>
              </div>
              <div class="badge-row">${statusBadges(olha)}</div>
              <div class="form-grid">
                <div class="field"><span class="field-label">Worksite</span><span class="field-value">Worksite A - Nitra warehouse</span></div>
                <div class="field"><span class="field-label">Position</span><span class="field-value">General laborer</span></div>
                <div class="field"><span class="field-label">Shift</span><span class="field-value">16 Jun 2026, 07:00-15:00</span></div>
                <div class="field"><span class="field-label">Transport group</span><span class="field-value">Bus 2, Nitra depot, 06:15</span></div>
              </div>
              <div class="inline-actions">
                ${actionButton("assignShift", "assign-shift", state.shiftAssigned ? "Assigned to shift" : "Assign to shift", "primary-button", state.shiftAssigned ? "disabled" : "")}
              </div>
            </div>
            <div class="stack">
              <h2 class="section-title">Bus 2 capacity</h2>
              <div class="capacity-meter">
                <div class="meter-track"><div class="meter-fill" style="--meter-width: ${state.decisionChoices.transport === "B" ? "100%" : state.shiftAssigned ? "100%" : "89%"}"></div></div>
                <strong class="mono">${escapeHtml(busText)}</strong>
                <p class="muted">Driver Tomas V., pickup Nitra depot, 06:15.</p>
              </div>
              ${state.decisionChoices.transport === "A" ? `<div class="success"><strong>Capacity enforced.</strong><p>Bus 2 is full after Olha. A future assignment would be blocked.</p></div>` : ""}
              ${state.decisionChoices.transport === "B" ? `<div class="warning"><strong>Capacity recorded only.</strong><p>The demo shows how an over-capacity transport row would be flagged, not blocked.</p></div>` : ""}
            </div>
          </div>
        </section>
        ${renderDecision("transport")}
        <section class="section">
          <h2 class="section-title">Shift table</h2>
          ${renderShiftTable()}
        </section>
      </section>
    `;
  }

  function transportCapacityText() {
    if (state.decisionChoices.transport === "B") {
      return "10 / 9 recorded";
    }
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
            <div class="badge-row">${statusBadges(olha)}</div>
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
            <h2 class="section-title">Document queue</h2>
            <table class="data-table">
              <thead><tr><th>Worker</th><th>Document</th><th>State</th></tr></thead>
              <tbody>
                <tr>
                  <td data-label="Worker">Farrukh Yusupov</td>
                  <td data-label="Document">Forklift certificate</td>
                  <td data-label="State"><span class="badge availability-inactive">Expires soon</span></td>
                </tr>
                <tr>
                  <td data-label="Worker">Olha Tkachenko</td>
                  <td data-label="Document">Work permit</td>
                  <td data-label="State"><span class="badge availability-available">18 days left</span></td>
                </tr>
              </tbody>
            </table>
          </section>
        </div>
        ${renderDecision("cert")}
      </section>
    `;
  }

  function renderFieldView() {
    const todayWorkers = [getPerson("olha"), getPerson("dilnoza"), getPerson("farrukh")];
    return `
      <section class="page">
        ${renderPageHeader("Mobile manager", "Field view", "A coordinator can check today's workers, document state, and quick actions from a phone-sized screen.")}
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

    return `
      <table class="data-table">
        <thead><tr><th>${escapeHtml(t("Worker"))}</th><th>${escapeHtml(t("Worksite"))}</th><th>${escapeHtml(t("Shift"))}</th><th>${escapeHtml(t("Transport"))}</th><th>${escapeHtml(t("Status"))}</th></tr></thead>
        <tbody>
          ${rows.map((row) => `
            <tr>
              <td data-label="Worker">${escapeHtml(row.worker)}</td>
              <td data-label="Worksite">${escapeHtml(row.worksite)}</td>
              <td data-label="Shift" class="mono">${escapeHtml(row.shift)}</td>
              <td data-label="Transport">${escapeHtml(row.transport)}</td>
              <td data-label="Status"><span class="badge ${row.status === "Cancelled" ? "availability-inactive" : "availability-working"}">${escapeHtml(t(row.status))}</span></td>
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
    state.currentStep = nextIndex;
    state.view = step.view;
    state.signedIn = step.view !== "login";
    if (step.id === "approval" && state.role === "Observer") {
      state.role = "Recruiter";
    }
    render();
  }

  function chooseDecision(decisionKey, choiceKey) {
    if (!decisions[decisionKey] || !decisions[decisionKey].options[choiceKey]) {
      return;
    }
    state.decisionChoices[decisionKey] = choiceKey;
    addAudit(`${decisions[decisionKey].title}: option ${choiceKey} recorded.`);
    if (decisionKey === "transport" && choiceKey === "B") {
      state.shiftAssigned = true;
      setPerson("olha", { availability: "Working" });
    }
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
        goToStep(state.currentStep - 1);
        return;
      case "next-step":
        state.manifestOpen = false;
        goToStep(state.currentStep + 1);
        return;
      case "go-step":
        state.navOpen = false;
        state.manifestOpen = false;
        goToStep(target.dataset.step);
        return;
      case "nav":
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
