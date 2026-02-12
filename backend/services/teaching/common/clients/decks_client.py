import json
from typing import Any, Dict, Optional

import httpx
from django.conf import settings


class DecksServiceClient:
    def __init__(self):
        self.base_url = settings.DECKS_SERVICE_URL
        self.timeout = 6.0

    def _get_headers(self, token: Optional[str] = None) -> Dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        return headers

    def get_deck_sync(
        self, deck_id: int, token: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        with httpx.Client(timeout=self.timeout) as client:
            try:
                response = client.get(
                    f"{self.base_url}/api/decks/{deck_id}/",
                    headers=self._get_headers(token),
                )

                if response.status_code == 200:
                    try:
                        return response.json()
                    except json.JSONDecodeError:
                        return None
                return None
            except httpx.RequestError:
                return None
            except Exception:
                return None


decks_client = DecksServiceClient()
