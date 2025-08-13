import logging
from typing import Any, Dict

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)


class TeamsService:
    @staticmethod
    async def send_task_completion_notification(task_data: Dict[str, Any]):
        if not settings.teams_webhook_url:
            logger.warning("Teams webhook URL not configured")
            return

        try:
            message = {
                "@type": "MessageCard",
                "@context": "http://schema.org/extensions",
                "themeColor": "00FF00",
                "summary": "Tarefa Concluída",
                "sections": [
                    {
                        "activityTitle": "✅ Tarefa Concluída",
                        "activitySubtitle": f"**{task_data['titulo']}**",
                        "facts": [
                            {"name": "ID", "value": str(task_data["id"])},
                            {
                                "name": "Descrição",
                                "value": task_data.get("descricao", "N/A"),
                            },
                            {
                                "name": "Data de Criação",
                                "value": task_data["data_criacao"],
                            },
                            {
                                "name": "Concluída em",
                                "value": task_data.get("data_atualizacao", "N/A"),
                            },
                        ],
                    }
                ],
            }

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    settings.teams_webhook_url, json=message, timeout=10.0
                )
                response.raise_for_status()
                logger.info(f"Teams notification sent for task {task_data['id']}")

        except Exception as e:
            logger.error(f"Failed to send Teams notification: {e}")


teams_service = TeamsService()
