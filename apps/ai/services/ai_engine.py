import os, json, logging
from openai import OpenAI
from geopy.geocoders import Nominatim
from ..models import QueryHistory
from apps.areas.districts.models import District
from apps.citizens.people_education.models import PeopleEducation
from apps.citizens.population.models import Population
from apps.competitors.competitor.models import Competitor
from apps.government_bodies.models import GovernmentBody

logger = logging.getLogger(__name__)
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))


class BusinessAgent:
    @staticmethod
    def get_history(user, limit=5):
        """Foydalanuvchi tarixini xavfsiz formatda yuklash."""
        if not user or not user.is_authenticated:
            return []

        records = QueryHistory.objects.filter(user=user, status='done').order_by('-created_at')[:limit]
        messages = []
        for r in reversed(records):
            messages.append({"role": "user", "content": r.user_query})
            # response_json ichidan ai_response kalitini xavfsiz olish
            if isinstance(r.response_json, dict):
                ai_msg = r.response_json.get('ai_response')
                if ai_msg:
                    messages.append({"role": "assistant", "content": ai_msg})
        return messages

    @staticmethod
    def fetch_stats(coords):
        """Berilgan nuqta atrofidagi real statistikani bazadan olish."""
        if not coords:
            return None
        lat, lon = coords
        r = 0.01  # ~1.1 km radius
        stats = {
            "competitors": Competitor.objects.filter(latitude__range=(lat - r, lat + r),
                                                     longitude__range=(lon - r, lon + r)).count(),
            "gov_bodies": GovernmentBody.objects.filter(latitude__range=(lat - r, lat + r),
                                                        longitude__range=(lon - r, lon + r)).count(),
        }

        # Education and population are stored per district, not per point,
        # so look them up through the district that contains the point.
        # A missing figure is left out rather than guessed: the prompt tells
        # the model these are real numbers from our database.
        district = BusinessAgent.find_district(lat, lon)
        if district is None:
            return stats
        stats["district"] = district.name_uz

        education = PeopleEducation.objects.filter(district=district).first()
        if education:
            stats["education"] = {
                "schools": education.regional_school,
                "kindergartens": education.regional_kindergarten,
                "teachers": education.regional_teachers,
                "students": education.regional_students,
            }

        population = Population.objects.filter(district=district).first()
        if population:
            stats["population"] = {
                "total": round(population.count_male + population.count_female),
                "density": population.population_density,
                "average_income": population.average_income,
                "unemployment_rate": population.unemployment_rate,
            }
        return stats

    @staticmethod
    def find_district(lat, lon):
        for district in District.objects.exclude(boundary_json__isnull=True):
            if district.is_point_inside(lat, lon):
                return district
        return None

    @classmethod
    def ask_ai(cls, query, user=None):
        # 1. Hudud va Koordinatani aniqlash (Oldingi mantiq)
        q_lower = query.lower()
        regions = ["mirobod", "chilonzor", "yunusobod", "sergeli", "yakkasaroy", "mirzo ulug'bek", "shayxontohur",
                   "olmazar", "yashnobod", "uchtepa"]
        detected_region = next((r.capitalize() for r in regions if r in q_lower), None)

        coords = None
        if detected_region:
            try:
                geolocator = Nominatim(user_agent="get_place_app")
                location = geolocator.geocode(f"{detected_region}, Tashkent")
                if location: coords = (location.latitude, location.longitude)
            except:
                pass

        # 2. Bazadan REAL ma'lumotlarni olish
        stats = cls.fetch_stats(coords)
        history = cls.get_history(user)

        # 3. Promptni MA'LUMOTLARGA ASOSLANGAN (Data-Driven) qilish
        system_prompt = (
            "Siz 'Get Place' tahlilchisisiz. Sizning maqsadingiz — bazadagi ma'lumotlar asosida "
            "foydalanuvchiga eng to'g'ri joyni ko'rsatish.\n"
            "YO'RIQNOMA:\n"
            "1. Agar 'stats' ichida raqamlar bo'lsa, ularni tahlil qiling. "
            "Masalan: 'Ushbu nuqtada 10 ta raqobatchi bor, bu raqobat ancha kuchli ekanini ko'rsatadi'.\n"
            "2. 'education' va 'population' butun tuman ('district') bo'yicha statistika. "
            "Maktab va bog'chalar ko'p bo'lsa, bu o'quv markazi uchun katta plyus ekanini ayting.\n"
            "3. FAQAT 'stats' ichidagi raqamlardan foydalaning. U yerda yo'q ko'rsatkichni o'ylab topmang; "
            "bunday holatda bu bo'yicha ma'lumot yo'qligini ayting.\n"
            "4. Raqamlarga tayanganda 'Bazadagi ma'lumotlarimizga ko'ra...' deb javob bering.\n"
            "5. Takroriy salomlashmang. FAQAT JSON formatda qaytaring."
        )

        messages = [{"role": "system", "content": system_prompt}]
        messages.extend(history)

        # AIga barcha ma'lumotlarni yuboramiz
        messages.append({"role": "user", "content": json.dumps({
            "user_query": query,
            "region": detected_region,
            "stats": stats,  # Real raqamlar shu yerda
            "is_returning": len(history) > 0
        })})

        try:
            res = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                response_format={"type": "json_object"},
                temperature=0.6  # Biroz kreativlik qo'shdik
            )
            ai_data = json.loads(res.choices[0].message.content)

            final_response = {
                "ai_response": ai_data.get("ai_response", "Ma'lumot topilmadi."),
                "intent": ai_data.get("intent", "general"),
                "business_summary": ai_data.get("business_summary", ""),
                "suggestions": ai_data.get("suggestions", []),
                "risks": ai_data.get("risks", []),
                "region": detected_region,
                "region_stats": stats,  # Foydalanuvchi ham raqamlarni ko'rsin
                "status": "success"
            }

            # Tarixni saqlash
            QueryHistory.objects.create(
                user=user if user and user.is_authenticated else None,
                user_query=query,
                region=detected_region or "",
                business_type=final_response['intent'],
                response_json=final_response,
                status='done'
            )
            return final_response

        except Exception as e:
            logger.error(f"AI Error: {e}")
            return {"ai_response": "Tizim tahlilni yakunlay olmadi.", "status": "failed"}