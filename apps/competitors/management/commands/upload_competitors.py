from django.core.management.base import BaseCommand
from django.db import transaction
from apps.competitors.competitor.models import Competitor
from apps.competitors.competitor_categories.models import CompetitorCategory
from apps.competitors.utils.search_place_foursquare import search_places_with_geocode
from apps.ai.logger import logger


class Command(BaseCommand):
    help = 'Fetch competitors from Foursquare API for all categories'

    def add_arguments(self, parser):
        parser.add_argument(
            '--query',
            type=str,
            default=None,
            help='Search query: city name or business center name (misol: "Tashkent" yoki "Mirzo Ulugbek")'
        )
        parser.add_argument(
            '--category',
            type=str,
            default=None,
            help='Filter by specific category name (uz) - agar bo\'lmasa, barcha category\'lar'
        )

    def handle(self, *args, **options):
        # User parametrlarini olish
        search_query = options.get('query')
        filter_category = options.get('category')

        # Category'larni olish
        if filter_category:
            categories = CompetitorCategory.objects.filter(name_uz__icontains=filter_category)
            if not categories.exists():
                logger.error(f"[Upload Competitors] Category not found: {filter_category}")
                self.stdout.write(self.style.ERROR(f"Category not found: {filter_category}"))
                return
        else:
            categories = CompetitorCategory.objects.all()

        if not categories.exists():
            logger.warning("[Upload Competitors] No categories found")
            self.stdout.write(self.style.WARNING("No categories found"))
            return

        # Agar query berilmasa, default qiymat
        if search_query:
            self.stdout.write(f"Search query: {search_query}")
            logger.info(f"[Upload Competitors] Starting with query: {search_query}")
        else:
            self.stdout.write("No search query provided - using category names")
            logger.info("[Upload Competitors] No search query - using category names")

        total_new = 0
        total_updated = 0
        total_skipped = 0

        for category in categories:
            try:
                # Query aniqlash: user qiymati yoki category nomi
                if search_query:
                    query = search_query
                else:
                    query = category.name_uz or category.name_ru

                category_name = category.name_uz

                self.stdout.write(f"\nProcessing: {category_name}")
                self.stdout.write(f"  Query: {query}")

                # Foursquare dan search qilish
                places = search_places_with_geocode(query, category_name)

                if not places:
                    logger.info(f"[Upload Competitors] No results: query={query}, category={category_name}")
                    self.stdout.write(self.style.WARNING(f"  ⚠ No results"))
                    total_skipped += 1
                    continue

                # Mavjud competitor'larni map qilish
                existing_map = {
                    (c.name_uz, c.address): c
                    for c in Competitor.objects.filter(category=category)
                }

                new_objs = []
                update_objs = []

                for item in places:
                    key = (item["name_uz"], item["address"])
                    if key in existing_map:
                        # Mavjudni update qilish
                        comp = existing_map[key]
                        comp.latitude = item["latitude"]
                        comp.longitude = item["longitude"]
                        update_objs.append(comp)
                    else:
                        # Yangi competitor yaratish
                        new_objs.append(Competitor(**item))

                # Database ga saqlaash
                with transaction.atomic():
                    if new_objs:
                        Competitor.objects.bulk_create(new_objs, ignore_conflicts=True)
                        total_new += len(new_objs)
                    if update_objs:
                        Competitor.objects.bulk_update(update_objs, ["latitude", "longitude"])
                        total_updated += len(update_objs)

                self.stdout.write(
                    self.style.SUCCESS(
                        f"  ✓ {len(new_objs)} new, {len(update_objs)} updated"
                    )
                )
                logger.info(
                    f"[Foursquare] category={category_name}, query={query}, "
                    f"new={len(new_objs)}, updated={len(update_objs)}"
                )

            except Exception as e:
                logger.exception(
                    f"Error processing category {category.name_uz} with query {query}: {e}"
                )
                self.stdout.write(
                    self.style.ERROR(f"  ✗ Error: {str(e)}")
                )

        # Final report
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write(
            self.style.SUCCESS(
                f"✓ COMPLETED!\n"
                f"  New: {total_new}\n"
                f"  Updated: {total_updated}\n"
                f"  Skipped: {total_skipped}"
            )
        )
        logger.info(
            f"[Upload Competitors] Completed! new={total_new}, updated={total_updated}, skipped={total_skipped}"
        )