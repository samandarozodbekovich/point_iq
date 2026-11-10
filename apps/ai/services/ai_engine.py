import json, logging
from django.conf import settings
from openai import OpenAI
from geopy.geocoders import Nominatim
from ..models import QueryHistory
from apps.areas.districts.models import District
from apps.citizens.people_education.models import PeopleEducation
from apps.citizens.population.models import Population
from apps.competitors.competitor.models import Competitor
from apps.government_bodies.models import GovernmentBody

logger = logging.getLogger(__name__)
# From settings (decouple reads .env); os.environ only had it while
# python-dotenv was loaded in settings.
client = OpenAI(api_key=settings.OPENAI_API_KEY)


class BusinessAgent:
    @staticmethod
    def get_history(user, limit=5):
        """The user's recent finished queries as chat messages."""
        if not user or not user.is_authenticated:
            return []

        records = QueryHistory.objects.filter(user=user, status='done').order_by('-created_at', '-id')[:limit]
        messages = []
        for r in reversed(records):
            messages.append({"role": "user", "content": r.user_query})
            # read ai_response from response_json defensively
            if isinstance(r.response_json, dict):
                ai_msg = r.response_json.get('ai_response')
                if ai_msg:
                    messages.append({"role": "assistant", "content": ai_msg})
        return messages

    @staticmethod
    def fetch_stats(coords):
        """Real statistics from the database around the given point."""
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
        return District.find_containing(lat, lon)

    @classmethod
    def ask_ai(cls, query, user=None):
        # 1. Detect the district and its coordinates
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

        # 2. Real data from the database
        stats = cls.fetch_stats(coords)
        history = cls.get_history(user)

        # 3. Data-driven prompt
        system_prompt = (
            "You are the 'Get Place' location analyst. Your goal is to recommend the best place "
            "for the user's business based on the data in our database.\n"
            "INSTRUCTIONS:\n"
            "1. If 'stats' contains numbers, analyse them. For example: 'There are 10 competitors "
            "at this point, so competition is strong.'\n"
            "2. 'education' and 'population' are statistics for the whole district ('district'). "
            "Many schools and kindergartens are a big plus for a training centre.\n"
            "3. Use ONLY the numbers in 'stats'. Never invent a figure that is not there; "
            "say that there is no data for it instead.\n"
            "4. When you rely on the numbers, say so ('According to our data...').\n"
            "5. Answer in Uzbek (Latin script). Do not repeat greetings. Return ONLY JSON."
        )

        messages = [{"role": "system", "content": system_prompt}]
        messages.extend(history)

        # everything the model needs
        messages.append({"role": "user", "content": json.dumps({
            "user_query": query,
            "region": detected_region,
            "stats": stats,  # the real numbers
            "is_returning": len(history) > 0
        })})

        try:
            res = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                response_format={"type": "json_object"},
                temperature=0.6  # a little creativity
            )
            ai_data = json.loads(res.choices[0].message.content)

            final_response = {
                "ai_response": ai_data.get("ai_response", "No data found."),
                "intent": ai_data.get("intent", "general"),
                "business_summary": ai_data.get("business_summary", ""),
                "suggestions": ai_data.get("suggestions", []),
                "risks": ai_data.get("risks", []),
                "region": detected_region,
                "region_stats": stats,  # the user sees the numbers too
                "status": "success"
            }

            # save to history
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
            return {"ai_response": "The analysis could not be completed.", "status": "failed"}