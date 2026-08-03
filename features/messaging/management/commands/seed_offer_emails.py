"""Seed offer-email templates and a couple of demo job offers (ADR 0029).

Templates are seeded **per language**, which is the point of the feature and
the thing `seed_messaging` could not do: an SMS body goes out in whatever
language it was written in, while an offer email is picked to match
`Person.preferred_language`. Jober's three worker languages are Slovak,
Hungarian and Ukrainian, so every kind gets all three.

These are operator-authored texts, deliberately outside the gettext catalogs
(`docs/i18n-seeded-data.md` says the same about SMS template bodies) - the
per-language rows *are* the translation mechanism here.

Offers hang off whatever demo projects exist, so this must run after the
project seeds. Idempotent: templates match on (kind, language) and offers on
title, so re-running repairs a hand-edited body instead of duplicating it.
"""

from __future__ import annotations

from datetime import date

from django.core.management.base import BaseCommand

from core.offices.models import Office
from core.projects.models import Project
from features.messaging.models import JobOffer, OfferEmailKind, OfferEmailTemplate

#: (kind, language, subject, body). Bodies use $placeholders resolved by
#: features.messaging.services.render_offer_email.
TEMPLATES = [
    (
        OfferEmailKind.NEW_OFFER,
        "sk",
        "Pracovná ponuka: $offer_title",
        "Dobrý deň, $first_name,\n\n"
        "máme pre Vás pracovnú ponuku: $offer_title.\n"
        "Miesto: $location\n"
        "Mzda: $wage\n"
        "Nástup: $start_date\n\n"
        "$terms\n\n"
        "V prípade záujmu odpovedzte na tento e-mail.\n"
        "$coordinator",
    ),
    (
        OfferEmailKind.NEW_OFFER,
        "hu",
        "Állásajánlat: $offer_title",
        "Jó napot, $first_name!\n\n"
        "Állásajánlatunk van az Ön számára: $offer_title.\n"
        "Helyszín: $location\n"
        "Bér: $wage\n"
        "Kezdés: $start_date\n\n"
        "$terms\n\n"
        "Ha érdekli, válaszoljon erre az e-mailre.\n"
        "$coordinator",
    ),
    (
        OfferEmailKind.NEW_OFFER,
        "uk",
        "Пропозиція роботи: $offer_title",
        "Доброго дня, $first_name!\n\n"
        "Маємо для Вас пропозицію роботи: $offer_title.\n"
        "Місце: $location\n"
        "Оплата: $wage\n"
        "Початок: $start_date\n\n"
        "$terms\n\n"
        "Якщо Вас це цікавить, дайте відповідь на цей лист.\n"
        "$coordinator",
    ),
    (
        OfferEmailKind.REMINDER,
        "sk",
        "Pripomienka: $offer_title",
        "Dobrý deň, $first_name,\n\n"
        "pripomíname našu ponuku $offer_title s nástupom $start_date. "
        "Ak máte záujem, dajte nám prosím vedieť.\n\n"
        "$coordinator",
    ),
    (
        OfferEmailKind.REMINDER,
        "hu",
        "Emlékeztető: $offer_title",
        "Jó napot, $first_name!\n\n"
        "Emlékeztetjük a(z) $offer_title ajánlatunkra, kezdés: $start_date. "
        "Ha érdekli, kérjük jelezze.\n\n"
        "$coordinator",
    ),
    (
        OfferEmailKind.REMINDER,
        "uk",
        "Нагадування: $offer_title",
        "Доброго дня, $first_name!\n\n"
        "Нагадуємо про пропозицію $offer_title, початок $start_date. "
        "Якщо Вас це цікавить, повідомте нас.\n\n"
        "$coordinator",
    ),
    (
        OfferEmailKind.SEASONAL,
        "sk",
        "Sezónne pozície: $offer_title",
        "Dobrý deň, $first_name,\n\n"
        "otvárame sezónne pozície na projekte $project ($location). "
        "Mzda: $wage, nástup $start_date.\n\n"
        "$terms\n\n"
        "$coordinator",
    ),
    (
        OfferEmailKind.SEASONAL,
        "hu",
        "Szezonális pozíciók: $offer_title",
        "Jó napot, $first_name!\n\n"
        "Szezonális pozíciókat nyitunk a(z) $project projekten ($location). "
        "Bér: $wage, kezdés: $start_date.\n\n"
        "$terms\n\n"
        "$coordinator",
    ),
    (
        OfferEmailKind.SEASONAL,
        "uk",
        "Сезонні вакансії: $offer_title",
        "Доброго дня, $first_name!\n\n"
        "Відкриваємо сезонні вакансії на проєкті $project ($location). "
        "Оплата: $wage, початок $start_date.\n\n"
        "$terms\n\n"
        "$coordinator",
    ),
    (
        OfferEmailKind.CLOSING,
        "sk",
        "Posledná možnosť: $offer_title",
        "Dobrý deň, $first_name,\n\n"
        "ponuka $offer_title sa čoskoro uzatvára. Ak máte záujem, "
        "ozvite sa nám prosím čo najskôr.\n\n"
        "$coordinator",
    ),
    (
        OfferEmailKind.CLOSING,
        "hu",
        "Utolsó lehetőség: $offer_title",
        "Jó napot, $first_name!\n\n"
        "A(z) $offer_title ajánlat hamarosan lezárul. Ha érdekli, "
        "kérjük mielőbb jelentkezzen.\n\n"
        "$coordinator",
    ),
    (
        OfferEmailKind.CLOSING,
        "uk",
        "Остання можливість: $offer_title",
        "Доброго дня, $first_name!\n\n"
        "Пропозиція $offer_title скоро закривається. Якщо Вас це цікавить, "
        "зв'яжіться з нами якомога швидше.\n\n"
        "$coordinator",
    ),
]

#: (title, location, wage, unit, start_date, terms)
OFFERS = [
    (
        "Operátor výroby",
        "Velký Meder",
        "8.50",
        JobOffer.WageUnit.HOUR,
        date(2026, 9, 1),
        "Trojzmenná prevádzka, ubytovanie zabezpečené, doprava na zmenu.",
    ),
    (
        "Skladník",
        "Győr",
        "1450.00",
        JobOffer.WageUnit.MONTH,
        date(2026, 9, 15),
        "Jednozmenná prevádzka, VZV preukaz výhodou.",
    ),
]


class Command(BaseCommand):
    help = "Seed offer-email templates (SK/HU/UK) and a couple of demo job offers."

    def handle(self, *args, **options):
        created_templates = 0
        for kind, language, subject, body in TEMPLATES:
            _obj, was_created = OfferEmailTemplate.objects.update_or_create(
                kind=kind,
                language=language,
                defaults={"subject": subject, "body": body, "is_active": True},
            )
            created_templates += int(was_created)

        # Offers need an office to be visible under ADR 0026: unlike a Person,
        # an office-less non-Person record has no owning-recruiter fallback, so
        # it is visible to unrestricted roles *only*. A seeded offer nobody but
        # Observer can see would look like a broken feature, so fall back to
        # any office rather than leaving the column null. A demo with no
        # offices at all (CorvinumEU's permanent state) still seeds cleanly.
        created_offers = 0
        projects = list(Project.objects.filter(is_active=True).order_by("pk"))
        fallback_office = Office.objects.order_by("pk").first()
        for index, (title, location, wage, unit, start, terms) in enumerate(OFFERS):
            project = projects[index] if index < len(projects) else None
            office = project.office if project and project.office else fallback_office
            _obj, was_created = JobOffer.objects.update_or_create(
                title=title,
                defaults={
                    "project": project,
                    "office": office,
                    "location": location,
                    "wage": wage,
                    "wage_unit": unit,
                    "currency": "EUR",
                    "start_date": start,
                    "terms": terms,
                    "is_active": True,
                },
            )
            created_offers += int(was_created)

        self.stdout.write(
            self.style.SUCCESS(
                f"Offer emails: {created_templates} templates created "
                f"({OfferEmailTemplate.objects.count()} total), "
                f"{created_offers} offers created "
                f"({JobOffer.objects.count()} total)."
            )
        )
