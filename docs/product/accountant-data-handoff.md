# Accountant data handoff and sensitive-source documents

Status: **Slovakia + Hungary product boundary adopted 2026-07-31; researched
design baseline — not implementation authorization or legal advice**

This note answers a narrow question: when Jober or CorvinumEU supports an
employer whose payroll is handled by an accountant, what information derived
from identity papers, children's birth certificates, medical-fitness papers,
and similar records should reach that accountant?

This handoff supports two separate employment/payroll jurisdictions: Slovakia
(`SK`) and Hungary (`HU`). Each has its own approved fields, declarations,
evidence rules, retention decisions, and export path. Posting, mixed-
jurisdiction, and unresolved cross-border tax/social-insurance cases remain
outside the product boundary. An office, nationality, home address, or UI
language does not itself decide the applicable law. In particular, Jober's
Győr office must not automatically select Hungary, and no Hungarian field or
rule may silently inherit its Slovak counterpart.

## Decision in one sentence

After resolving the employment to `SK` or `HU`, send the accountant that
jurisdiction's allowlisted **structured payroll facts**, plus
the **specific evidence required for a tax claim only when that claim is
made**; do not send a general worker file, an identity-card scan, or medical
examination details.

This does not change the platform document boundary. Jober and CorvinumEU do
not store the excluded scans merely so they can forward them. If an original
or copy must be made available to the employer's accountant, it travels through
the employer's separately approved evidence channel and custody process. The
platform records, at most, the minimum verification/status metadata.

## Controller and accountant roles

The employing company determines why employee data is processed and is
normally the controller. The EDPB gives payroll accounting as a direct example
of a processor relationship: an external payroll company follows the
employer's instructions about recipients, amounts, deadlines, reporting, and
retention. The role is functional, however; a provider may be an independent
controller for a separate activity it determines itself.

Before any production handoff, each client must therefore have:

- the correct employing legal entity recorded and the payroll jurisdiction
  explicitly confirmed as `SK` or `HU`; an absent, uncertain, mixed, posted, or
  other jurisdiction must block the handoff;
- the accountant's role and exact services documented;
- an Article 28 data-processing agreement where the accountant acts as a
  processor, including instructions, confidentiality, security,
  subprocessors, incident handling, return/deletion, and audit assistance;
- an approved field list, evidence list, purpose, cadence, transport, access
  list, and retention rule for each handoff.

Employee consent is not a shortcut for normal statutory payroll processing or
for collecting extra records. The legal basis and, for health data, the
special-category condition must be documented for the actual purpose.

## Shared handoff matrix

“Accountant” below means the person or company actually performing the
employer's payroll/tax task. It does not mean every finance or bookkeeping
user.

| Source or event | Minimum information for the payroll accountant | Evidence that may be required | What must not be in the routine handoff |
|---|---|---|---|
| Worker onboarding / identity verification | Internal employee ID, employing entity, explicit `SK`/`HU` jurisdiction, and only the fields in that jurisdiction's approved schedule below; payment method and IBAN only when payroll pays by bank | Normally a verified source, employment documents, and the applicable registration/declaration—not an ID image | ID-card/passport scan; portrait; signature; machine-readable zone; a document number or other fields that the accountant has not tied to a named legal filing |
| Child/family tax benefit | **Only when the worker claims it:** the identifiers, eligibility, period/change, amount/head-count choice, declaration, and co-claimant facts required by the applicable Slovak or Hungarian process | Only the evidence required for the particular claim under that jurisdiction; the two countries' evidence rules must not be merged | Records about children for whom no claim is made; an unrestricted family file; unrelated facts visible on a civil-status document |
| Spouse/partner allowance or related tax claim | Only the spouse/partner claim facts and amounts required by the selected jurisdiction's current process | Only the particular supporting records required for that claim | A standing copy of the entire family-document set “just in case” |
| Medical fitness for work | **Nothing in the ordinary payroll export.** At most, a separate HR/OHS status can say that a fitness opinion was verified, its conclusion/status, issue/validity dates, and whether an operational restriction must be handled | The statutory fitness opinion belongs in the employer's restricted occupational-health/personnel custody. If an accountant is separately contracted to administer that record, it needs a distinct purpose, instruction, access group, and retention path | Diagnosis, examination result, clinical report, medication, medical history, or a health-certificate scan in payroll. The examination provider's invoice may go to bookkeeping, but not the clinical record |
| Disability, pension, or another status that changes tax/levy treatment | Only the official status, effective dates, applicable payroll code, and reference needed to apply the treatment | The precise official decision/confirmation required for that treatment, if current rules require the employer to retain it | Diagnosis or broader medical/social file; assumptions inferred from appearance or notes |
| Residence/work authorization for a foreign worker in supported national payroll | Only identifiers and status data demonstrably required for the employer's applicable Slovak or Hungarian registration, tax, payroll, or social-insurance task | Permit or residence evidence stays with the responsible HR/legal process unless the accountant has a named filing or custody duty | Routine passport/residence-card scans or a complete immigration file; posted/mixed/cross-border cases are unsupported |
| Forklift, crane, or welding licence | Normally nothing; these are operational qualification records | Only if a separately identified accounting event needs invoice/expense data | Certificate image in a payroll export |
| Bank/payment evidence | Account-holder name, IBAN, payment method, and an effective date when needed to pay wages | A controlled verification process if the employer requires one | Bank-card image, online-banking screenshot, account balance, or bank statement |

### Slovakia: identity and child-claim schedule

For Slovak payroll, the employer's tax payroll record includes names,
surnames, and birth numbers of people for whom the employee claims the spouse
allowance or child tax bonus. The employee claims the child bonus through the
signed declaration/annual-settlement process. The Financial Administration's
2026 guidance identifies a birth certificate as proof and lists additional
documents for particular relationships or older children.

That means a birth certificate can be legitimate **claim evidence**. It does
not mean every employee's children's certificates should be collected, placed
in PeopleOps, or sent every month. The evidence is relevant only if the worker
makes the claim and only to the employer function processing it. The client and
accountant must confirm whether their compliant process requires a copy, an
extract, controlled inspection, or another official/electronic confirmation.

Recommended platform metadata for the Slovak path, if this capability is later
approved:

- benefit/claim type and tax jurisdiction (`SK`);
- claimant worker and the minimum dependant identifiers required by the
  payroll record;
- effective-from/to or claimed months;
- declaration received date and current/cancelled state;
- evidence type, verified status, verifier, verification time, and external
  custodian/reference;
- date a change was reported and the handoff batch/receipt identifier.

It must not include a birth-certificate upload field.

### Why the ID image is not a payroll input

The accountant needs reliable identifiers to register and pay the employee.
For Slovak tax records that includes the employee's name, birth number, and
permanent address; Social Insurance has a separate EČC path for a foreign
worker without a Slovak birth number. These are structured data needs. The
research found no general Slovak rule requiring a payroll accountant to retain
a scan of every national ID card or passport.

The ID may be inspected by an authorized person to establish the correct
facts. Only fields tied to a documented employment, tax, insurance, or
right-to-work purpose should then be recorded. Slovak law specifically limits
use of a generally applicable identifier such as the birth number to cases
where its use is necessary for the processing purpose; it should consequently
be restricted, masked in ordinary views/exports where possible, and never used
as a convenient universal application key.

### Hungary: identity and family-benefit schedule

Hungary's current NAV `08E` process is a structured registration, not an ID-
image requirement. Depending on the event and whether NAV must create an
identifier, its fields include:

- employee tax identification number (`adóazonosító jel`) and social-security
  number (`TAJ`);
- current and birth name;
- mother's birth name;
- place and date of birth;
- citizenship and address where the particular registration/identifier process
  requires them;
- employment relationship code, start/end, FEOR occupation code, weekly hours,
  and the relationship sequence number introduced for relationships beginning
  in 2026.

The exact subset must come from the current event/form version. The platform
must not collect every conditional `08E` field for every employee simply
because the form can contain it. The source identity document may be inspected
by an authorized person, but the accountant handoff contains the required
structured values rather than a card/passport scan.

For the 2026 Hungarian family tax allowance (`családi kedvezmény`), the employee
gives the employer/payer an advance-tax declaration. The current declaration
uses the claimant's name and tax identifier and, for each dependant, name, tax
identifier, dependant-status code, change date/months, and the chosen amount or
number of qualifying dependants. Joint claims require the other claimant's
specified identifiers and declaration details; the form also addresses whether
a similar foreign benefit is claimed.

The researched Hungarian process does **not** establish a routine need for the
payroll accountant to receive or retain every child's birth-certificate scan.
The signed/electronic declaration is the normal payroll input. Evidence is
conditional on the actual basis—for example an official entitlement decision,
public document supporting a qualifying relationship, pregnancy confirmation,
or disability/family-allowance confirmation. The client accountant must name
the rule and exact evidence before it is transferred. Jober/CorvinumEU retain
only claim/declaration and evidence-verification metadata, not the source scan.

Recommended Hungarian metadata, if later approved:

- benefit/claim type and jurisdiction (`HU`);
- employee and dependant tax identifiers required by the declaration;
- dependant-status code and effective change date/months;
- joint-claim/co-claimant status and the minimum required identifiers;
- requested amount or qualifying-dependant count and whether the contribution
  allowance is declined;
- declaration version, submitted/received date, current/replaced state, and
  external NAV/ONYA or employer reference;
- evidence type/status, verifier/time, and external custodian/reference where
  evidence is actually required.

It must not include a Hungarian birth-certificate or identity-document upload
field.

### Why medical details stop before payroll

Under the current Slovak public-health law, the examining doctor records the
examination results in medical documentation and gives the employer a medical
fitness opinion. The opinion identifies the worker and assessed work and gives
the fitness conclusion; it is not a licence for the employer or accountant to
receive examination results. The National Labour Inspectorate likewise
distinguishes the work-fitness result from medical examination results.

The statutory employer record and its retention belong to a restricted
occupational-health/personnel process. In particular, current law specifies a
20-year employer retention rule for fitness opinions of employees who perform
risk-category work; the applicable work category and any other retention rule
must be confirmed rather than applying 20 years to every worker by default.

If the accountant books the cost of an examination, send ordinary accounting
facts—supplier, invoice, date, amount, cost centre and, only if necessary, an
internal worker reference. Do not attach the opinion or report to the invoice.

Hungary follows the same routing boundary even though its legal form is
different. The current occupational-fitness decree communicates whether the
person is suitable, temporarily unsuitable, or unsuitable for the assessed
work, plus necessary restrictions. The reason for unsuitability may be given
to the employer only with the examined person's written consent. This fitness
opinion is an employer/occupational-health record, not an ordinary payroll
accountant input; diagnoses and examination results remain excluded.

## Three deliberately separate routes

1. **Recurring payroll data:** a jurisdiction-specific allowlisted structured
   export for the named employing entity and `SK` or `HU` payroll period. It
   contains no scans.
2. **Conditional tax evidence:** a task-specific package or controlled view
   only after the employee makes a claim. Evidence is transferred outside the
   base platform and logged by manifest/receipt, not duplicated in PeopleOps.
3. **Restricted HR/OHS evidence:** fitness opinions, immigration/right-to-work
   evidence, and similar employer records. They never enter the normal
   accountant export. Access by an accountant requires a separate documented
   personnel-administration duty.

There must be no “export all documents,” ZIP of a worker profile, or role that
quietly gives a general bookkeeper access to all three routes.

## Transfer and logging controls

When a handoff is implemented:

- generate it server-side from the selected `SK` or `HU` client/field
  allowlist; free-text notes and attachments are excluded by construction;
- require an explicit employing entity, period, purpose, and recipient;
- show an exact preview and require an authorized confirmation;
- use the accountant's controlled portal, managed SFTP, or another approved
  encrypted channel; ordinary email attachments, Telegram, Messenger, and
  public/shared-drive links are not approved evidence transport;
- encrypt temporary exports, expire them quickly, and remove them after
  receipt according to the approved procedure;
- audit who exported what **categories**, for which purpose/period and
  recipient, plus receipt/deletion status; do not copy raw identifiers or
  health facts into audit messages;
- isolate each employing entity and client, apply least privilege and MFA, and
  test that an accountant cannot request another office/client/entity;
- document retention separately for the payroll record, claim evidence,
  medical-fitness opinion, and transfer artefact. “Keep everything with the
  worker forever” is not a retention rule.

## Two-country enforcement boundary

The jurisdiction is not inferred at export time. Every employment included in
an accountant handoff must already resolve to an approved employing entity and
one explicit jurisdiction, `SK` or `HU`. The export service selects that
jurisdiction's versioned allowlist and declaration/evidence rules. It must
never combine the two schedules in one employment record or silently fall back
from one to the other.

If jurisdiction is missing, disputed, outside `SK`/`HU`, posted, mixed, or
cross-border, the system must refuse the handoff and direct the case to a human
legal/payroll process outside Jober and CorvinumEU.

The Győr office can remain an operational office for ordinary Jober scoping.
Its name or location does not automatically choose the Hungarian schedule. A
worker associated with Győr may use `HU`, `SK`, or neither only according to the
responsible payroll owner's documented employment-level determination. The
same rule applies to Slovak office labels: they do not override a confirmed
Hungarian jurisdiction.

Adding any third jurisdiction is a separately scoped product and legal project.
It requires its own official-source field/evidence matrix, retention rules,
processor instructions, tests, and an explicit new decision; it is not an
unreviewed configuration toggle.

## Decisions required before design or code

The business owner, client, accountant/payroll owner, and privacy/legal reviewer
must answer:

1. Which legal entity employs each population, and can the payroll owner assign
   each employment exactly one supported jurisdiction (`SK` or `HU`)? A third,
   mixed, posted, cross-border, or uncertain answer is out of scope.
2. Is the recipient a payroll processor, an independent accountant, or both for
   different activities? Is the required Article 28 agreement in place?
3. Which exact current Slovak or Hungarian forms/filings does the accountant
   submit, and which source fields does each require?
4. Who is the legal custodian of each original/copy, particularly child-claim
   evidence and medical-fitness opinions?
5. Does the accountant require evidence access or only verified structured
   facts? For each document, what rule creates that need?
6. What are the jurisdiction- and purpose-specific retention/deletion rules?
7. What secure transfer system and recipient accounts will be used?
8. Who handles worker corrections, claim cancellation, expiry, employment
   termination, and proof that the accountant received/deleted a package?

Until these are answered, no accountant export, family-benefit schema, evidence
upload, or production personal-data flow is approved. Fictional data only under
the repository's real-data gate.

## Primary sources checked

Slovakia:

- Financial Administration, [2026 employer/payroll tax information](https://www.financnasprava.sk/sk/podnikatelia/dane/dan-z-prijmov/zamestnavatelia/info-dp-zamestnavatel) — required payroll-record fields and the signed declaration route.
- Financial Administration, [proof for the 2026 annual settlement](https://podpora.financnasprava.sk/874663-Preukazovanie-n%C3%A1rokov-pri-vykonan%C3%AD-ro%C4%8Dn%C3%A9ho-z%C3%BA%C4%8Dtovania) and [2026 guidance PDF](https://www.financnasprava.sk/_img/pfsedit/Dokumenty_PFS/Zverejnovanie_dok/Aktualne/DP/Zavis_cinnost/2026/2026.01.07_002_ZC_2026_IM.pdf) — conditional birth, marriage, care, and school/benefit evidence.
- Social Insurance Agency, [registering an employee](https://www.socpoist.sk/kto-som/zamestnavatel/prihlasenie-odhlasenie/prihlasit-do-socialnej-poistovne-zamestnanca) and [employer FAQ](https://www.socpoist.sk/faq-zamestnavatel) — RLFO and the EČC path for foreign workers without a Slovak birth number.
- Všeobecná zdravotná poisťovňa, [2026 employer notification duty](https://www.vszp.sk/showdoc.do?docid=147&forceBrowserDetector=blind) — employee public-health-insurance reporting.
- Slov-Lex, [Act No. 355/2007 Coll., §30f and related employer duties](https://www.slov-lex.sk/ezbierky/pravne-predpisy/SK/ZZ/2007/355/) — content/custody of the fitness opinion and risk-work retention.
- National Labour Inspectorate, [employer access to fitness result rather than examination results](https://www.ip.gov.sk/koronavirus-informacie/zamestnavatel-ockovanie-zamestnancov-z-pohladu-pracovneho-prava.html).
- Slov-Lex, [Act No. 18/2018 Coll. on personal-data protection](https://www.slov-lex.sk/ezbierky/pravne-predpisy/SK/ZZ/2018/18/) — purpose limitation/minimisation and necessary use of general identifiers.

EU/data protection:

- EUR-Lex, [GDPR](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX%3A32016R0679) — Articles 5, 9, 28, and 32.
- Slovak Data Protection Office/EDPB, [Guidelines 07/2020 on controller and processor concepts](https://dataprotection.gov.sk/files/metod-edpb/usmernenia_k_pojmom_prevadzkovatel_a_sprostredkovatel_podla_vseobecneho_nariadenia_o_ochrane_udajov.pdf) — payroll accountant example.
- Slovak Data Protection Office, [Article 28 standard controller–processor clauses](https://dataprotection.gov.sk/sk/aktuality/standardne-zmluvne-dolozky-medzi-prevadzkovatelmi-sprostredkovatelmi-sprostredkovatelska-zmluva.html).

Hungary:

- NAV, [current 08E employee registration page](https://nav.gov.hu/nyomtatvanyok/letoltesek/nyomtatvanykitolto_programok/nyomtatvanykitolto_programok_nav/08E) and [2026 form/change explanation](https://nav.gov.hu/nyomtatvanyok/letoltesek_egyeb/nyomtatvanytervezetek/Megjelent_a_biztositotti_jogviszonyok_bejelentesere_szolgalo_08E_jelu_2026._evtol_alkalmazando_urlap_tervezet) — structured insured-person and employment-relationship registration fields.
- NAV, [2026 family tax allowance](https://nav.gov.hu/ado/szja/szja-kedvezmenyek/csaladi-kedvezmeny), [2026 declaration guidance](https://nav.gov.hu/pfile/file?path=%2Fado%2Fszja%2Fadoeloleg-nyilatkozatok%2F2026%2FCsaladi_kedvezmeny.pdf1), and [2026 tax-base allowance guide](https://nav.gov.hu/pfile/file?path=%2Fugyfeliranytu%2Fnezzen-utana%2Finf_fuz%2F2026%2F73.-Szja-adoalap-kedvezmenyek-2026.-01.-16) — dependant identifiers, eligibility/status, co-claiming, period, and declaration route.
- National Legislation Database, [Decree 33/1998 (VI. 24.) NM](https://njt.hu/jogszabaly/1998-33-20-3D) — occupational-fitness conclusion, restrictions, and disclosure boundary.
- Hungarian National Authority for Data Protection and Freedom of Information, [workplace data-processing guidance](https://www.naih.hu/files/2016_11_15_Tajekoztato_munkahelyi_adatkezelesek.pdf) and [qualification-copy opinion](https://naih.hu/adatvedelmi-allasfoglalasok/file/657-az-iso-9001-2015-minosegiranyitasi-rendszerszabvanynak-valo-megfeleles-igenye-nem-jogositja-fel-a-szervezetet-a-munkavallalok-vegzettseget-igazolo-dokumentumok-masolatanak-elkeszitesere-megorzesere) — purpose/necessity and minimisation of employee-document copies.
