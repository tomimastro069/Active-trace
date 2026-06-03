import httpx
from typing import List, Optional
from app.schemas.padron import EntradaPadronCreate
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception

def is_transient_http_error(exception: Exception) -> bool:
    """
    Returns True if the exception is a transient network error or HTTP 502/503/504 status.
    """
    if isinstance(exception, httpx.HTTPStatusError):
        return exception.response.status_code in [502, 503, 504]
    return isinstance(exception, httpx.RequestError)

class MoodleWSClient:
    def __init__(self, base_url: str, token: str):
        self.base_url = base_url.rstrip('/')
        self.token = token

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception(is_transient_http_error),
        reraise=True
    )
    async def get_enrolled_students(self, course_id: int) -> List[EntradaPadronCreate]:
        """
        Fetches enrolled students from Moodle for the given course_id.
        Retries on transient network errors or 502/503/504 HTTP codes.
        """
        url = f"{self.base_url}/webservice/rest/server.php"
        params = {
            "wstoken": self.token,
            "wsfunction": "core_enrol_get_enrolled_users",
            "moodlewsrestformat": "json",
            "courseid": course_id
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                url,
                params=params,
                timeout=10.0
            )
            response.raise_for_status()
            
            data = response.json()
            
            # Check if Moodle returned a webservice error (e.g. invalid token, course not found)
            if isinstance(data, dict) and "exception" in data:
                # Webservice errors are not transient, do not retry, raise directly
                raise ValueError(f"Moodle WS Error: {data.get('message', 'Unknown error')}")
                
            if not isinstance(data, list):
                raise ValueError(f"Unexpected response format from Moodle WS: {data}")
            
            students = []
            for user in data:
                # Map Moodle fields to EntradaPadronCreate
                comision = None
                groups = user.get("groups", [])
                if groups and isinstance(groups, list):
                    comision = groups[0].get("name")

                students.append(
                    EntradaPadronCreate(
                        nombre=user.get("firstname", ""),
                        apellidos=user.get("lastname", ""),
                        email=user.get("email", ""),
                        comision=comision,
                        regional=None,
                        usuario_id=None
                    )
                )
            return students
