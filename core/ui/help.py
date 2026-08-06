"""Feature-aware, client-neutral registry for the in-app Help area.

Help is deliberately code-backed and translated with Django rather than stored
in the database.  Every authenticated role may read it; feature flags decide
which workflows exist for the running thin client.  Asset selection is driven
by ``HELP_ASSET_NAMESPACE`` so shared core never branches on client identity.
"""

from __future__ import annotations

import re
from copy import copy

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils.translation import gettext_lazy as _

_NAMESPACE = re.compile(r"^[a-z0-9_-]+$")


def _screen(slug: str, alt, first, second) -> dict:
    return {
        "file": f"{slug}.webp",
        "alt": alt,
        "callouts": (
            {"number": 1, "x": 18, "y": 22, "text": first},
            {"number": 2, "x": 78, "y": 22, "text": second},
        ),
    }


def _f(name, text, who=None, locks=None) -> dict:
    """One row of an article's field reference.

    Money and approval screens document every field they show, because "what
    does this box actually do" is the question a client asks in a demo and the
    one an office asks six months later. The wording here is deliberately the
    **same sentence** used in that field's `data-tooltip`, so the two cannot
    drift into disagreeing about the same control.
    """
    return {"name": name, "text": text, "who": who, "locks": locks}


HELP_GROUPS = [
    {
        "label": _("Start here"),
        "articles": [
            {
                "slug": "getting-started",
                "title": _("Getting started"),
                "summary": _(
                    "Learn the shell, roles, scope, statuses, and built-in guidance."
                ),
                "icon": "help",
                "purpose": _(
                    "Use this orientation before changing records so the navigation, status colors, office boundary, and permission model make sense."
                ),
                "role_note": _(
                    "Every authenticated role can read Help. Buttons and navigation entries still depend on your role and on the modules enabled for this client."
                ),
                "steps": (
                    _(
                        "Use the main navigation to move between workflows. The Jober top tabs and the Corvinum sidebar show only modules this client supports."
                    ),
                    _(
                        "Start from People when you need one worker. Search or filter the list, open the profile, and follow its next-step panel."
                    ),
                    _(
                        "Read status dots and alert colors consistently: blue is available, amber needs attention, green is working or valid, gray is inactive, and red is blocked or urgent."
                    ),
                    _(
                        "Hover with a mouse or tap with touch to open tooltips. Return to Help for the complete workflow and its safety boundaries."
                    ),
                ),
                "warning_title": _("Scope is enforced on the server"),
                "warning": _(
                    "A missing action normally means your role cannot perform it. A forbidden cross-office link is rejected by the server; changing a URL does not widen access."
                ),
                "screenshots": (
                    _screen(
                        "getting-started",
                        _(
                            "The client-specific application shell with its main navigation and account controls."
                        ),
                        _("Open a module from the client navigation."),
                        _(
                            "Account, language, theme, office, and role controls stay in the shell."
                        ),
                    ),
                ),
                "related": ("people", "reports", "audit"),
                "covers": ("help_index",),
            }
        ],
    },
    {
        "label": _("Workforce workflows"),
        "articles": [
            {
                "slug": "people",
                "title": _("People and intake"),
                "summary": _(
                    "Find, create, and maintain worker profiles, avatars, and lifecycle state."
                ),
                "icon": "people",
                "purpose": _(
                    "People is the operational home for a worker from first intake through assignment, inactivity, and any later return."
                ),
                "role_note": _(
                    "All roles may read profiles in their allowed office scope. Recruiters and Managers normally create or edit people; other actions have their own permission checks."
                ),
                "steps": (
                    _(
                        "Search by name and combine the status and inactive-reason filters to narrow the People list without changing any records."
                    ),
                    _(
                        "Choose Add person to record the minimum reliable intake details. Review spelling and duplicates before saving."
                    ),
                    _(
                        "Open the profile to manage operational details, the owning recruiter, project history, readiness, certificates, and other enabled panels."
                    ),
                    _(
                        "Upload a portrait only when it is useful. Accepted JPEG, PNG, or WebP files are cropped, resized to 512 by 512, stripped of metadata, and stored as WebP."
                    ),
                ),
                "warning_title": _("Personal-data gate"),
                "warning": _(
                    "Use fictional people until the real-data security gate is complete. Record only data needed for the workflow, and never use a real identity document as an avatar."
                ),
                "screenshots": (
                    _screen(
                        "people",
                        _(
                            "The People list with fictional workers, status filters, and profile links."
                        ),
                        _("Search and filters narrow the current office-scoped list."),
                        _(
                            "Each row opens the worker profile and shows the lifecycle state."
                        ),
                    ),
                ),
                "related": ("getting-started", "projects", "readiness"),
                "covers": ("people_list", "intake_start"),
            },
            {
                "slug": "projects",
                "title": _("Projects and assignments"),
                "summary": _(
                    "Create projects, place workers, review headcount, and record exits."
                ),
                "icon": "projects",
                "purpose": _(
                    "Projects connect workers to the site where they are expected to work and provide the source for active headcount reporting."
                ),
                "role_note": _(
                    "All roles can read allowed projects. Coordinators and Managers normally manage placements; project creation and editing require the configured project permission."
                ),
                "steps": (
                    _(
                        "Open Projects and choose an existing project, or create one with its office and responsible coordinators."
                    ),
                    _(
                        "Assign an available worker from the project or person workflow. Confirm the intended project before submitting."
                    ),
                    _(
                        "Review active assignments and readiness before asking for activation. Reports update from these assignment records."
                    ),
                    _(
                        "When work ends, use the exit workflow and record the real reason. The exit reconciles enabled resources and moves the person out of active work."
                    ),
                ),
                "warning_title": _("Assignments drive other modules"),
                "warning": _(
                    "Do not create a second active placement to correct the first. Use the supported exit and assignment actions so history, resources, status, and reports stay consistent."
                ),
                "screenshots": (
                    _screen(
                        "projects",
                        _(
                            "The Projects workspace with fictional projects and assignment information."
                        ),
                        _(
                            "Open a project to review its people and operational details."
                        ),
                        _("Use the project actions for assignment and maintenance."),
                    ),
                ),
                "related": ("people", "readiness", "reports"),
                "covers": ("project_list",),
            },
            {
                "slug": "readiness",
                "title": _("Trials, readiness and activation"),
                "summary": _(
                    "Record trial outcomes, complete readiness, and decide activation requests."
                ),
                "icon": "readiness",
                "purpose": _(
                    "This workflow moves a candidate from a trial or preparation stage into active work only after the required operational checks are complete."
                ),
                "role_note": _(
                    "Recruiters or Coordinators prepare the worker according to their permissions. Managers decide queued activation requests; reading this article is not role-restricted."
                ),
                "steps": (
                    _(
                        "Schedule a trial for the correct worker and project, then record the actual outcome instead of changing lifecycle status by hand."
                    ),
                    _(
                        "Complete each readiness requirement or mark it not applicable with a reason. Client-specific critical checklist items must also be complete where enabled."
                    ),
                    _(
                        "Submit the activation request only when the page reports readiness. The request captures the relevant readiness state for review."
                    ),
                    _(
                        "A Manager approves to start the assignment or rejects with a reason so the preparer knows what must be corrected."
                    ),
                ),
                "conditional_steps": (
                    {
                        "flag": "checklists",
                        "text": _(
                            "In checklist-enabled clients, tick every critical activation item on the worker profile; a critical open item blocks activation even when the ordinary pillars look complete."
                        ),
                    },
                ),
                "warning_title": _("Never bypass readiness"),
                "warning": _(
                    "Activation is a controlled state transition. Correct the underlying trial, readiness, or checklist record instead of forcing a status that contradicts it."
                ),
                "screenshots": (
                    _screen(
                        "readiness",
                        _(
                            "The activation queue with fictional workers awaiting a decision."
                        ),
                        _("The queue identifies the worker and requested project."),
                        _(
                            "Decision controls approve or return the request with a reason."
                        ),
                    ),
                ),
                "fields": (
                    _f(
                        _("Medical"),
                        _(
                            "The entry medical certificate is on file. Required - it cannot be marked not-applicable, and activation is refused without it."
                        ),
                        who=_("Coordinator or Manager"),
                    ),
                    _f(
                        _("Gear"),
                        _(
                            "The worker has the equipment the job needs. Required, like Medical, and cannot be marked not-applicable."
                        ),
                        who=_("Coordinator or Manager"),
                    ),
                    _f(
                        _("Accommodation"),
                        _(
                            "A bed is arranged, or genuinely not needed. Marking it not-applicable requires a written reason."
                        ),
                        who=_("Coordinator or Manager"),
                    ),
                    _f(
                        _("Transport"),
                        _(
                            "Travel to site is arranged, or not needed with a reason. Hidden entirely where the transport feature is switched off."
                        ),
                        who=_("Coordinator or Manager"),
                    ),
                    _f(
                        _("Entry medical date"),
                        _(
                            "The date the medical was carried out. It cannot be in the future; a future date is a typo, not a plan."
                        ),
                        who=_("Coordinator or Manager"),
                    ),
                    _f(
                        _("Request activation"),
                        _(
                            "Asks a manager to decide. It does not activate anyone, and the four pillars are re-checked at the moment of the decision in case one regressed in between."
                        ),
                        who=_("Coordinator or Manager"),
                    ),
                    _f(
                        _("Approve"),
                        _(
                            "Puts this worker to work: they move to Working on this project, the assignment starts today, and accommodation and equipment are committed."
                        ),
                        who=_("Manager"),
                        locks=_(
                            "Deciding your own request is allowed, and recorded as a self-approval."
                        ),
                    ),
                    _f(
                        _("Reject"),
                        _(
                            "Sends the request back with your reason. The worker stays in readiness and the coordinator can fix what you name and ask again. A reason is required."
                        ),
                        who=_("Manager"),
                    ),
                    _f(
                        _("Activate without a trial day"),
                        _(
                            "Opens readiness for a worker the office already knows, with no trial. It waives the trial only - all four pillars still apply before activation."
                        ),
                        who=_("Manager"),
                    ),
                ),
                "related": ("people", "projects", "compliance"),
                "covers": ("trials_queue", "activation_queue"),
            },
        ],
    },
    {
        "label": _("Safety and resources"),
        "articles": [
            {
                "slug": "compliance",
                "title": _("Certificates and compliance"),
                "summary": _(
                    "Store allowed occupational licences and manage expiry, renewal, and archive."
                ),
                "icon": "compliance",
                "flags": ("documents",),
                "purpose": _(
                    "Compliance keeps occupational certificate metadata and the permitted forklift, crane, and welding files visible before they expire."
                ),
                "role_note": _(
                    "Authorized Recruiters, Coordinators, and Managers can add certificates. Permanent file removal is Manager-only; private file delivery rechecks office and sensitive-data access."
                ),
                "steps": (
                    _(
                        "Open a worker and choose Add certificate. Select only Forklift, Crane, or Welding and enter the issuer, dates, and optional certificate number."
                    ),
                    _(
                        "Upload one PDF, one front image, or front and back images. Review both private links after saving a two-sided card."
                    ),
                    _(
                        "Use Edit to correct metadata or add a missing back image. Use Renew for a replacement certificate so the previous record remains in history."
                    ),
                    _(
                        "Archive a record that should no longer be active. Use Manager file removal only for an improper upload and provide the required reason."
                    ),
                ),
                "warning_title": _("Strict document-storage boundary"),
                "warning": _(
                    "Never upload passports, identity cards, birth or residence documents, financial records, medical reports, or health-certificate scans. Those are metadata-only or stay outside this platform. Files are sanitized but not individually encrypted by Django on disk; server storage and encrypted backups are part of the production gate. Use fictional certificates until that gate is complete."
                ),
                "screenshots": (
                    _screen(
                        "compliance",
                        _(
                            "The compliance workspace showing fictional occupational certificate alerts."
                        ),
                        _(
                            "Alerts identify the worker and the occupational requirement."
                        ),
                        _("Status and due date show which item needs attention first."),
                    ),
                ),
                "related": ("people", "readiness", "audit"),
                "covers": ("compliance_list",),
            },
            {
                "slug": "equipment",
                "title": _("Equipment"),
                "summary": _(
                    "Maintain the catalogue, issue items, and handle stock, returns, or reviews."
                ),
                "icon": "equipment",
                "flags": ("equipment",),
                "purpose": _(
                    "Equipment records what can be issued, what each worker holds, and how a missing or returned item is resolved under the client's policy."
                ),
                "role_note": _(
                    "All roles may read the enabled equipment views. Issuing, receiving, returning, adjusting stock, and deciding deductions each require their corresponding operational permission."
                ),
                "steps": (
                    _(
                        "Maintain catalogue names, sizes, and prices so an issue can be identified and valued consistently."
                    ),
                    _(
                        "Issue the correct item from the worker profile and verify the worker and office before submitting."
                    ),
                    _(
                        "If an item is not returned, flag it for review. A Manager records whether the cost is charged or waived instead of editing history."
                    ),
                ),
                "conditional_steps": (
                    {
                        "setting": "EQUIPMENT_STOCK_LEDGER_ENABLED",
                        "text": _(
                            "Where stock tracking is enabled, record goods receipts before issuing, use adjustments only with a reason, and reconcile the office-specific balance and receipt log."
                        ),
                    },
                    {
                        "flag": "equipment_returns",
                        "text": _(
                            "Where returns are enabled, use Return on the original issue so the item state changes through the recorded workflow and the catalogue remains accurate."
                        ),
                    },
                ),
                "warning_title": _("Follow the enabled issue policy"),
                "warning": _(
                    "Stock-ledger clients reduce office stock when issuing. Return-enabled clients record a return on the original issue. The Help page shows only the policy enabled for this client."
                ),
                "screenshots": (
                    _screen(
                        "equipment",
                        _(
                            "The client-specific equipment workspace with fictional catalogue or stock data."
                        ),
                        _(
                            "Catalogue or stock rows identify the item and current state."
                        ),
                        _(
                            "Available actions follow this client's stock and return policy."
                        ),
                    ),
                ),
                "related": ("people", "reports", "audit"),
                "covers": ("equipment_catalog", "equipment_reviews", "equipment_stock"),
            },
            {
                "slug": "accommodation",
                "title": _("Accommodation"),
                "summary": _(
                    "Manage buildings, rooms, assignments, rates, and monthly costs."
                ),
                "icon": "accommodation",
                "flags": ("accommodation",),
                "purpose": _(
                    "Accommodation connects office-owned buildings and rooms to the workers living there and to the rates used in operational cost views."
                ),
                "role_note": _(
                    "Readers see accommodation within their office scope. Coordinators and Managers normally manage rooms and placements; rate and cost actions require their specific permissions."
                ),
                "steps": (
                    _(
                        "Create the building in the correct office, then add rooms with a real capacity and the applicable rate."
                    ),
                    _(
                        "Assign a worker from the profile and confirm the room still has capacity. Record the assignment-specific rate only when it genuinely differs."
                    ),
                    _(
                        "Release the room when the worker leaves or moves; use a transfer workflow rather than overlapping active placements."
                    ),
                    _(
                        "Use Accommodation costs with the period controls to review occupancy, room rates, worker payments, and the office-scoped result."
                    ),
                ),
                "warning_title": _("Capacity and dates matter"),
                "warning": _(
                    "A stale room assignment makes both availability and cost reporting wrong. Record moves and releases on the date they actually happen."
                ),
                "screenshots": (
                    _screen(
                        "accommodation",
                        _(
                            "The accommodation workspace with fictional buildings, occupancy, and cost information."
                        ),
                        _("Building and room data define capacity and placement."),
                        _(
                            "Period controls and totals explain the accommodation cost view."
                        ),
                    ),
                ),
                "related": ("people", "projects", "reports"),
                "covers": ("accommodation_list",),
            },
            {
                "slug": "blacklist",
                "title": _("Blacklist"),
                "summary": _(
                    "Propose, review, match, and restrict serious re-entry cases."
                ),
                "icon": "blacklist",
                "flags": ("duplicate_blacklist",),
                "purpose": _(
                    "The blacklist is a controlled last-resort process for preventing a specifically reviewed person from being re-entered after a serious issue."
                ),
                "role_note": _(
                    "A Coordinator or Manager may propose a case. Only a Manager decides it; other authenticated roles may read Help even if they cannot open the review queue."
                ),
                "steps": (
                    _(
                        "Open the person's profile, propose a case, choose the approved category, and write a factual reason without unnecessary sensitive detail."
                    ),
                    _(
                        "A Manager reviews the proposal and its privacy-preserving identifiers, then approves or rejects with a recorded reason."
                    ),
                    _(
                        "Approved cases block activation and flag a matching future intake. The system does not merge people automatically."
                    ),
                    _(
                        "If a restriction must be removed, use the controlled removal action so the reason and actor remain in Audit."
                    ),
                ),
                "warning_title": _("High-impact restricted data"),
                "warning": _(
                    "Do not use the blacklist for ordinary performance notes or as an automatic consequence of an exit. Follow the approved legal basis, access, and retention policy before real data is admitted."
                ),
                "screenshots": (
                    _screen(
                        "blacklist",
                        _("The blacklist review queue with fictional proposed cases."),
                        _("The proposal shows the person, category, and review facts."),
                        _("A Manager records the decision through explicit controls."),
                    ),
                ),
                "related": ("people", "readiness", "audit"),
                "covers": ("blacklist_queue",),
            },
        ],
    },
    {
        "label": _("Reporting and pay"),
        "articles": [
            {
                "slug": "reports",
                "title": _("Reports and staff activity"),
                "summary": _(
                    "Use period filters, drill-downs, office scope, and activity reporting."
                ),
                "icon": "reports",
                "purpose": _(
                    "Reports summarizes current operational records, while Staff activity counts selected staff actions over a chosen reporting period."
                ),
                "role_note": _(
                    "Report visibility follows office scope and each report action. Staff activity is available only to roles with its reporting permission; Help remains readable to everyone."
                ),
                "steps": (
                    _(
                        "Set the reporting period first. Month, quarter, year, and custom controls change the rows and totals shown on the page."
                    ),
                    _(
                        "Open a metric card or linked row to drill down to the underlying People or Projects view instead of copying a headline number."
                    ),
                    _(
                        "Use Staff activity to compare recorded operational actions, including zero-activity colleagues where shown."
                    ),
                    _(
                        "Use Audit—not Staff activity—when you need to know who changed a specific record, what changed, and why."
                    ),
                ),
                "warning_title": _("Read totals in scope"),
                "warning": _(
                    "Operational totals include only records visible in your office scope. An Observer may see cross-office figures that another role cannot."
                ),
                "screenshots": (
                    _screen(
                        "reports",
                        _(
                            "The Reports workspace with fictional metrics, period controls, and drill-down links."
                        ),
                        _("Set the period before interpreting a metric."),
                        _("Linked cards and rows open the records behind the total."),
                    ),
                ),
                "related": ("projects", "audit", "finance", "ledger"),
                "covers": ("reports", "staff_activity"),
            },
            {
                "slug": "finance",
                "title": _("Finance"),
                "summary": _(
                    "Record monthly project revenue and cost lines, lock periods, and read results."
                ),
                "icon": "finance",
                "flags": ("profitability",),
                "purpose": _(
                    "Finance records project profitability from explicit monthly revenue and cost lines and derives every displayed total from those entries."
                ),
                "role_note": _(
                    "Authorized finance readers may inspect reports. Recording, locking, reopening, and export actions require their configured permissions, with Manager approval where specified."
                ),
                "steps": (
                    _(
                        "Create an active project, or edit an existing one, and keep Include this project in Finance enabled."
                    ),
                    _(
                        "Open Finance and choose the project under Enter a project year. The workbook reports are read-only."
                    ),
                    _(
                        "Type costs as negative amounts and revenues as positive amounts in the twelve-month grid. Never type a pre-calculated net value."
                    ),
                    _(
                        "Select Save year once. Review the monthly and yearly reports, then lock a month when its figures are final."
                    ),
                    _(
                        "Use Export Excel for a formula-free snapshot with the yearly project grid, twelve-month summary, office totals, and live charts."
                    ),
                ),
                "warning_title": _("Locked periods are deliberate"),
                "warning": _(
                    "The project-year grid uses the workbook signs: costs are negative and revenues are positive. Locking prevents ordinary edits, and every reopen is an audited exception."
                ),
                "screenshots": (
                    _screen(
                        "finance",
                        _(
                            "The Finance workspace with fictional monthly revenue, costs, and derived results."
                        ),
                        _("Period and project controls select the financial slice."),
                        _(
                            "Totals and charts are derived from the recorded line items."
                        ),
                    ),
                ),
                "related": ("projects", "reports", "audit"),
                "covers": ("finance_summary",),
            },
            {
                "slug": "feedback",
                "title": _("Feedback"),
                "summary": _(
                    "Create public links and QR flyers, then review anonymous submissions."
                ),
                "icon": "feedback",
                "flags": ("feedback",),
                "purpose": _(
                    "Feedback gives workers a public, account-free way to submit a message through a controlled link or printed QR flyer."
                ),
                "role_note": _(
                    "Managers create links and review the inbox. The submission form is public to anyone holding the token; Help itself remains authenticated."
                ),
                "steps": (
                    _(
                        "Create a clearly labelled feedback link and optionally connect it to the relevant project."
                    ),
                    _(
                        "Share the generated URL or download the one-page QR flyer for printing. Retire a distribution point by controlling where its token is published."
                    ),
                    _(
                        "A worker opens the public form, writes a message, and may add a rating without creating an account."
                    ),
                    _(
                        "Managers review the newest submissions in the inbox and handle them under the agreed retention and escalation process."
                    ),
                ),
                "warning_title": _("Public token, limited purpose"),
                "warning": _(
                    "Anyone with the link can submit. Do not ask workers to include identity documents, medical details, credentials, or other unnecessary sensitive information in free text."
                ),
                "screenshots": (
                    _screen(
                        "feedback",
                        _(
                            "The Feedback inbox with fictional submissions and link-management controls."
                        ),
                        _("Link and QR controls create the public entry point."),
                        _(
                            "The authenticated inbox is where Managers review submissions."
                        ),
                    ),
                ),
                "related": ("projects", "audit", "getting-started"),
                "covers": ("feedback_inbox",),
            },
            {
                "slug": "ledger",
                "title": _("Ledger"),
                "summary": _(
                    "Record advances, additions, deductions, reversals, and settlement cycles."
                ),
                "icon": "ledger",
                "flags": ("advances",),
                "purpose": _(
                    "The ledger records explicit pay additions and deductions, groups them into settlement cycles, and preserves corrections as history."
                ),
                "role_note": _(
                    "Authorized readers can inspect cycles. Entry, cancellation, reversal, settlement, and export each require the corresponding ledger or export permission."
                ),
                "steps": (
                    _(
                        "Record the person, optional project, entry type, category, positive amount, and a concise note."
                    ),
                    _(
                        "Review the current Thursday summary and select the intended 20th-to-20th cycle before including entries."
                    ),
                    _(
                        "Correct a mistake by cancelling or reversing the original entry with a reason; never overwrite financial history."
                    ),
                    _(
                        "After the external deduction process is complete, mark the included cycle settled and use the approved CSV export when needed."
                    ),
                ),
                "warning_title": _("Positive amounts, explicit pay effect"),
                "warning": _(
                    "The entry type controls whether an amount adds to or deducts from pay. This ledger records source adjustments; it does not calculate statutory payroll."
                ),
                "screenshots": (
                    _screen(
                        "ledger",
                        _(
                            "The ledger workspace with fictional entries, cycle controls, and settlement summaries."
                        ),
                        _(
                            "Entry controls record an explicit type, category, and amount."
                        ),
                        _(
                            "Cycle controls include, export, and settle the selected period."
                        ),
                    ),
                ),
                "fields": (
                    _f(
                        _("Person"),
                        _(
                            "The worker this money concerns. The entry appears on their pay overview and in their open balance."
                        ),
                        who=_("Coordinator or Manager"),
                    ),
                    _f(
                        _("Company / project"),
                        _(
                            "Optional. Attributes the amount to a partner company for reporting. It does not change what the worker is paid."
                        ),
                        who=_("Coordinator or Manager"),
                    ),
                    _f(
                        _("Entry type"),
                        _(
                            "Decides the direction: an advance or deduction reduces pay, an addition increases it. The amount stays positive either way."
                        ),
                        who=_("Coordinator or Manager"),
                    ),
                    _f(
                        _("Category"),
                        _(
                            "What the money was for - advance, clothing, footwear, equipment, medical, travel or other. Groups the cycle report; it does not affect the direction or the amount."
                        ),
                        who=_("Coordinator or Manager"),
                    ),
                    _f(
                        _("Amount (EUR)"),
                        _(
                            "Always a positive number. Never type a minus sign - the entry type decides whether this is added or subtracted."
                        ),
                        who=_("Coordinator or Manager"),
                        locks=_(
                            "Once the cycle is included; correct it with a reversal after that."
                        ),
                    ),
                    _f(
                        _("Entry date"),
                        _(
                            "The day the money changed hands. It decides which 21st-to-20th payroll cycle the entry settles in, and which calendar month it appears under on the pay overview. Leave blank for today; a date inside an already-settled cycle is refused."
                        ),
                        who=_("Coordinator or Manager"),
                        locks=_("Once the cycle containing that date is included."),
                    ),
                    _f(
                        _("Note"),
                        _(
                            "The reason, in words, for whoever reads this months from now. It is carried into the exports the accountant receives."
                        ),
                        who=_("Coordinator or Manager"),
                    ),
                ),
                "related": ("payslips", "gross-wages", "audit"),
                "covers": ("ledger_overview",),
            },
            {
                "slug": "payslips",
                "title": _("Payslips"),
                "summary": _(
                    "Record net payslip values and deliver encrypted PDFs safely."
                ),
                "icon": "payslips",
                "flags": ("payslips",),
                "purpose": _(
                    "Payslips stores the independently supplied net value and can email a freshly generated encrypted PDF to the worker."
                ),
                "role_note": _(
                    "Payslip amounts are restricted pay data. Only roles with payslip access can read them, and only authorized Managers can record or send them."
                ),
                "steps": (
                    _(
                        "Confirm the worker has the correct email address, then record the calendar month, positive net amount, optional issue date, and note."
                    ),
                    _(
                        "Review the recorded row before sending. Send encrypted PDF generates the attachment and a random one-time password."
                    ),
                    _(
                        "Tell the worker the password by phone or Messenger, never in the same email as the encrypted PDF."
                    ),
                    _(
                        "If you resend, a new password is generated and the earlier one is invalidated. The password is shown once and is not stored for later retrieval."
                    ),
                ),
                "warning_title": _("Never capture or copy the password into records"),
                "warning": _(
                    "Do not screenshot the success message, paste the password into notes, email it, or send it through the same channel as the PDF. The generated PDF is not stored by the application."
                ),
                "screenshots": (
                    _screen(
                        "payslips",
                        _(
                            "The payslip list with fictional net values and delivery states; no passwords are visible."
                        ),
                        _(
                            "The record form stores the independently supplied net value."
                        ),
                        _("Delivery state shows whether an encrypted PDF was sent."),
                    ),
                ),
                "fields": (
                    _f(
                        _("Person"),
                        _(
                            "Who the payslip belongs to. A worker with no email address is marked in the list, because the encrypted PDF cannot be delivered to them."
                        ),
                        who=_("Manager"),
                    ),
                    _f(
                        _("Pay month"),
                        _(
                            "The calendar month this payslip pays for, not the month it was issued in. One payslip per person per month."
                        ),
                        who=_("Manager"),
                    ),
                    _f(
                        _("Net amount (EUR)"),
                        _(
                            "The net figure printed on the payslip, as paid. It is shown beside the gross wage and the ledger deductions for the same month; the system does not calculate it."
                        ),
                        who=_("Manager"),
                    ),
                    _f(
                        _("Payslip date (optional)"),
                        _(
                            "The date printed on the document. Blank means the day it was recorded."
                        ),
                        who=_("Manager"),
                    ),
                    _f(
                        _("Note"),
                        _(
                            "Free text for the office. It is not included in the PDF sent to the worker."
                        ),
                        who=_("Manager"),
                    ),
                ),
                "related": ("gross-wages", "ledger", "audit"),
                "covers": ("payslip_list",),
            },
            {
                "slug": "gross-wages",
                "title": _("Gross wages"),
                "summary": _(
                    "Record independent monthly gross-wage source values without payroll calculation."
                ),
                "icon": "gross-wages",
                "flags": ("wage_ledger",),
                "purpose": _(
                    "Gross wages stores the supplied gross amount for a person and month beside, but independently from, the recorded net payslip."
                ),
                "role_note": _(
                    "Authorized pay-data readers may inspect the list. Recording a gross wage requires the wage-management permission."
                ),
                "steps": (
                    _(
                        "Choose the correct person and calendar month, then enter the externally supplied positive gross amount."
                    ),
                    _(
                        "Add a short source or reconciliation note when it helps another authorized reader understand the record."
                    ),
                    _(
                        "Compare gross and net only as independent source values. Investigate discrepancies through the payroll owner outside this application."
                    ),
                ),
                "warning_title": _("Not a payroll calculator"),
                "warning": _(
                    "The application does not derive tax, insurance, statutory deductions, or net pay from this amount and does not treat a gross-to-net difference as an automatic error."
                ),
                "screenshots": (
                    _screen(
                        "gross-wages",
                        _(
                            "The gross-wage workspace with fictional independent monthly source values."
                        ),
                        _(
                            "The form records a person, month, and positive gross amount."
                        ),
                        _("The table preserves who recorded each source value."),
                    ),
                ),
                "fields": (
                    _f(
                        _("Person"),
                        _(
                            "The worker who earned this wage. One gross figure per person per month."
                        ),
                        who=_("Manager"),
                    ),
                    _f(
                        _("Wage month"),
                        _(
                            "The calendar month the wage was earned in, not the month it was paid out."
                        ),
                        who=_("Manager"),
                    ),
                    _f(
                        _("Gross wage (EUR)"),
                        _(
                            "Gross, before anything is taken off. Ledger deductions are subtracted from this on the worker's pay overview; tax and levies are not calculated here."
                        ),
                        who=_("Manager"),
                    ),
                    _f(
                        _("Note"),
                        _(
                            "Where this figure came from - a contract, a timesheet, the accountant. It is what the next reader checks it against."
                        ),
                        who=_("Manager"),
                    ),
                ),
                "related": ("payslips", "ledger", "audit"),
                "covers": ("wage_list",),
            },
            {
                "slug": "audit",
                "title": _("Audit"),
                "summary": _(
                    "Trace sensitive actions, old and new values, actors, reasons, and retention."
                ),
                "icon": "audit",
                "purpose": _(
                    "Audit is the append-only trace for sensitive actions: who acted, what record changed, when it happened, and the reason or value snapshot available for that event."
                ),
                "role_note": _(
                    "Only roles with Audit access can open the log. Help explains it to every role because their own sensitive actions may create events."
                ),
                "steps": (
                    _(
                        "Open Audit and narrow the result by actor, worker, action, record type, or date range."
                    ),
                    _(
                        "Read the newest events first and use the record reference to connect an event to the operational workflow."
                    ),
                    _(
                        "Use old and new value snapshots where provided to understand the change; free-text reasons remain in the language originally entered."
                    ),
                    _(
                        "Use Staff activity for volume reporting. Audit is for traceability and investigation, not performance totals."
                    ),
                ),
                "warning_title": _("Append-only and restricted"),
                "warning": _(
                    "Ordinary users cannot edit or delete audit events. Retention follows the approved policy; do not copy restricted event details into a less protected system."
                ),
                "screenshots": (
                    _screen(
                        "audit",
                        _(
                            "The Audit page heading and filters, captured without event rows or log contents."
                        ),
                        _("Filters narrow the trace without changing stored events."),
                        _(
                            "Audit access and append-only behavior protect the evidence trail."
                        ),
                    ),
                ),
                "related": ("reports", "blacklist", "compliance"),
                "covers": ("audit_log",),
            },
        ],
    },
]

ARTICLE_TEMPLATES = {
    article["slug"]: "help/article.html"
    for group in HELP_GROUPS
    for article in group["articles"]
}

LEGACY_REDIRECTS = {"logistics": "equipment"}


def _raw_articles():
    for group in HELP_GROUPS:
        yield from group["articles"]


def raw_article(slug: str) -> dict | None:
    return next(
        (article for article in _raw_articles() if article["slug"] == slug), None
    )


def article_is_available(article) -> bool:
    """An article is available when any declared feature flag is enabled."""
    from core.ui.registry import flag_enabled

    flags = article.get("flags")
    return not flags or any(flag_enabled(flag) for flag in flags)


def _condition_enabled(item: dict) -> bool:
    from core.ui.registry import flag_enabled

    if "flag" in item:
        return flag_enabled(item["flag"])
    if "setting" in item:
        return bool(getattr(settings, item["setting"], False))
    return True


def _asset_namespace() -> str:
    namespace = getattr(settings, "HELP_ASSET_NAMESPACE", "")
    if not namespace or not _NAMESPACE.fullmatch(namespace):
        raise ImproperlyConfigured(
            "HELP_ASSET_NAMESPACE must contain only lowercase letters, digits, "
            "underscores, or hyphens."
        )
    return namespace


def article_context(article: dict) -> dict:
    """Copy and enrich an article for the running client's templates."""
    namespace = _asset_namespace()
    prepared = copy(article)
    prepared["thumbnail"] = f"help/screens/{namespace}/{article['slug']}-thumb.webp"
    prepared["screenshots"] = [
        {**screen, "path": f"help/screens/{namespace}/{screen['file']}"}
        for screen in article["screenshots"]
    ]
    prepared["steps"] = [
        *article["steps"],
        *(
            item["text"]
            for item in article.get("conditional_steps", ())
            if _condition_enabled(item)
        ),
    ]
    return prepared


def available_articles() -> list[dict]:
    return [
        article_context(article)
        for article in _raw_articles()
        if article_is_available(article)
    ]


def available_groups() -> list[dict]:
    groups = []
    for group in HELP_GROUPS:
        articles = [
            article_context(article)
            for article in group["articles"]
            if article_is_available(article)
        ]
        if articles:
            groups.append({**group, "articles": articles})
    return groups
