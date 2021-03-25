from django.core.management.base import BaseCommand
from ...models import Record, Category, CategoryRecord


categories = [
    {
        "name": "Magna Carta",
    },
]

records = [
    {
        "name": "Magna Carta",
        "description": "Duchy of Lancaster: Royal Charters. HENRY III. Magna Carta.",
        "date": "Date: 1225",
        "reference": "Reference: DL 10/71",
        "categories": [
            "Magna Carta",
        ],
    },
    {
        "name": "Magna Carta",
        "description": "Public Record Office: Reproductions of Records, etc: Photographic Copies of Extraneous Documents. Magna Carta.",
        "date": "Date: 15 June 1215",
        "reference": "Reference: PRO 22/11",
        "categories": [
            "Magna Carta",
        ],
    },
    {
        "name": "Magna Carta. Dated at: Westminster",
        "description": "Duchy of Lancaster: Royal Charters. EDWARD I. Magna Carta. Dated at: Westminster.",
        "date": "Date: 1297",
        "reference": "Reference: DL 10/197",
        "categories": [
            "Magna Carta",
        ],
    },
]


class Command(BaseCommand):
    help = ()

    def handle(self, *args, **options):
        for category in categories:
            _, created = Category.objects.update_or_create(
                name=category["name"], defaults=category
            )

        for record in records:
            record_object, created = Record.objects.update_or_create(
                reference=record["reference"],
                defaults={k: v for k, v in record.items() if k != "categories"},
            )
            record_categories = Category.objects.filter(name__in=record["categories"])
            record_object.categories.set(
                [CategoryRecord(category=c) for c in record_categories]
            )
            record_object.save()
