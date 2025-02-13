from typing import Optional

from locust import HttpUser, task


class AnonymousUser(HttpUser):
    host = "https://localhost:8081"

    def on_start(self):
        self.search_term = "test"
        self.page = 1

    def _make_get_request(self, path: str, name: str) -> None:
        with self.client.get(
            path, name=name, catch_response=True, stream=True, verify=False
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"{name} failed: {response.status_code}")

    def _handle_stream(self, response) -> Optional[bytes]:
        try:
            content = b""
            for chunk in response.iter_content(chunk_size=8192):
                content += chunk
            return content
        except Exception as e:
            response.failure(f"Stream error: {str(e)}")
            return None

    @task
    def search(self):
        self._make_get_request(
            f"/?search={self.search_term}&page={self.page}", "Task: Search"
        )
