from celery import shared_task
import logging
from .models.query_history import QueryHistory
from .ask_ai.ask_ai_real import ask_ai_real
from apps.ai.services.agent_service import ask_chatbot_response, score_location

logger = logging.getLogger(__name__)


@shared_task
def async_agent_chat(query, business_type, region, region_stats, intent, history_id):
    try:
        region_coord = region_stats.get("coordinates") if region_stats else None

        # Real OpenAI for getting real advice
        ai_json = ask_ai_real(query, region_coord)

        if ai_json.get("error"):
            raise Exception(f"AI Error: {ai_json.get('error')}")

        location_score = None
        if intent == "business_advice" and region_stats:
            location_score = score_location(region_stats)

        chat_response = None
        if intent == "general_chat":
            chat_response = ask_chatbot_response(query)

        response_json = {
            "intent": intent,
            "region": region,
            "business_type": business_type,
            "region_stats": region_stats,
            "location_score": location_score,
            "chat": chat_response,
            "ai_response": ai_json.get("ai_response"),
            "rationale": ai_json.get("rationale"),
            "sources": ai_json.get("sources", []),
            "context_docs": ai_json.get("context_docs", []),
        }

        # update QueryHistory
        history = QueryHistory.objects.get(id=history_id)
        history.response_json = response_json
        history.status = "done"
        history.save()

        logger.info(f"Async task completed successfully for history_id: {history_id}")

    except QueryHistory.DoesNotExist:
        logger.error(f"QueryHistory not found with id: {history_id}")
    except Exception as e:
        logger.error(f"async_agent_chat error: {str(e)}")
        try:
            history = QueryHistory.objects.get(id=history_id)
            history.response_json = {"error": str(e)}
            history.status = "failed"
            history.save()
        except:
            pass