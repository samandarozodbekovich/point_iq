from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from django.core.exceptions import ValidationError
from geopy.geocoders import Nominatim
import logging

from ..models.query_history import QueryHistory
from ..serializers import QueryHistorySerializer
from ..services.agent_service import (
    detect_intent,
    extract_region_and_business,
    get_region_stats,
    score_location
)
from ..tasks import async_agent_chat
from ..ask_ai.ask_ai_real import ask_ai_real

logger = logging.getLogger(__name__)
geolocator = Nominatim(user_agent="get_place_app")


class UniversalAIView(APIView):
    permission_classes = [AllowAny]

    def _extract_request_data(self, request):
        data = request.data if request.method == "POST" else request.GET
        query = data.get("query", "").strip()
        if not query:
            raise ValidationError({"query": "query required"})
        business_type = data.get("business_type", "").strip()
        region = data.get("region", "").strip()
        sync = data.get("sync", "false").lower() == "true"
        return query, business_type, region, sync

    def post(self, request):
        try:
            query, business_type, region, sync = self._extract_request_data(request)

            intent = detect_intent(query)
            auto_region, auto_business = extract_region_and_business(query)
            region = region or auto_region
            business_type = business_type or auto_business

            # make a QueryHistory
            with transaction.atomic():
                history = QueryHistory.objects.create(
                    user=request.user if request.user.is_authenticated else None,
                    user_query=query,
                    business_type=business_type or "",
                    region=region or "",
                    status="processing",
                    response_json={"status": "processing", "intent": intent}
                )

            # Region koordinates
            region_coord = None
            try:
                if region:
                    location = geolocator.geocode(region)
                    region_coord = (location.latitude, location.longitude) if location else None
            except Exception as e:
                logger.warning(f"Geocoding error: {str(e)}")
                region_coord = None

            region_stats = get_region_stats(region_coord) if region_coord else {}
            if region_coord:
                region_stats["coordinates"] = region_coord

            # SYNC works
            if sync:
                ai_json = ask_ai_real(query, region_coord)

                if ai_json.get("error"):
                    history.status = "failed"
                    history.response_json = {"error": ai_json.get("error")}
                    history.save()
                    return Response(
                        {"error": ai_json.get("error")},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                location_score = None
                if intent == "business_advice" and region_stats:
                    location_score = score_location(region_stats)

                response_json = {
                    "intent": intent,
                    "region": region,
                    "business_type": business_type,
                    "region_stats": region_stats,
                    "location_score": location_score,
                    "ai_response": ai_json.get("ai_response"),
                    "rationale": ai_json.get("rationale"),
                    "sources": ai_json.get("sources", []),
                    "context_docs": ai_json.get("context_docs", []),
                }

                history.response_json = response_json
                history.status = "done"
                history.save()

                serializer = QueryHistorySerializer(history)
                return Response(serializer.data, status=status.HTTP_200_OK)

            # ASYNC works
            async_agent_chat.delay(
                query=query,
                business_type=business_type,
                region=region,
                region_stats=region_stats,
                intent=intent,
                history_id=history.id
            )

            serializer = QueryHistorySerializer(history)
            return Response(
                {
                    **serializer.data,
                    "message": "waiting to get AI's answer"
                },
                status=status.HTTP_202_ACCEPTED
            )

        except ValidationError as e:
            logger.warning(f"Validation error: {str(e)}")
            raise ValidationError({"query": "query required"})

        except Exception as e:
            logger.error(f"UniversalAIView error: {str(e)}")
            return Response(
                {"error": "Server error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    # def get(self, request):
    #     return self.post(request)