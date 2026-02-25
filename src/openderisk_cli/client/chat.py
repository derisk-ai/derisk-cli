"""Chat API client."""

import json
import logging
import time
from typing import Any, Dict, Generator, List, Optional

from openderisk_cli.client.base import OpenDeriskClient

logger = logging.getLogger(__name__)
from openderisk_cli.exceptions import APIError, TimeoutError
from openderisk_cli.models.chat import (
    ChatCompletionRequest,
    ConversationResponse,
    ModelInfo,
)


class ChatClient(OpenDeriskClient):
    """Client for Chat APIs."""

    def chat_completions(
        self,
        user_input: str,
        conv_uid: Optional[str] = None,
        app_code: Optional[str] = None,
        model_name: Optional[str] = None,
        temperature: Optional[float] = None,
        max_new_tokens: Optional[int] = None,
        incremental: bool = True,
        user_name: Optional[str] = None,
        messages: Optional[List[Dict[str, Any]]] = None,
        timeout: int = 300,
        max_retries: int = 10,
        initial_delay: float = 2.0,
    ) -> Generator[str, None, None]:
        """Send chat message and stream response.

        Args:
            user_input: User input message
            conv_uid: Conversation UID (optional, creates new if not provided)
            app_code: App code (optional)
            model_name: Model name (optional)
            temperature: Temperature (optional)
            max_new_tokens: Max new tokens (optional)
            incremental: Whether to return incremental output
            user_name: User name (optional)
            messages: OpenAI-compatible messages list (optional)
            timeout: Timeout in seconds
            max_retries: Max retries when session not found (default 10)
            initial_delay: Initial delay in seconds before first query (default 2.0)

        Yields:
            Streamed response chunks
        """
        request = ChatCompletionRequest(
            user_input=user_input,
            conv_uid=conv_uid,
            app_code=app_code,
            model_name=model_name,
            temperature=temperature,
            max_new_tokens=max_new_tokens,
            incremental=incremental,
            user_name=user_name or "cli_user",
            messages=messages,
            app_config_code=None,
            team_mode=None,
            sys_code=None,
            select_param=None,
            prompt_code=None,
            chat_in_params=None,
            work_mode="async",
        )

        body = request.model_dump(exclude_none=True)
        logger.debug("Request body: %s", json.dumps(body, ensure_ascii=False, indent=2))

        response = self.http_client.post(
            "/api/v1/chat/completions",
            json=body,
        )

        if not response.get("success"):
            raise APIError(message="Failed to submit chat", response=response)

        data = response.get("data", {})
        conv_id = data.get("conv_id")
        if not conv_id:
            raise APIError(message="No conv_id in response", response=response)

        logger.info(f"Got conv_id: {conv_id}")

        time.sleep(initial_delay)

        retry_count = 0
        start_time = time.time()
        while time.time() - start_time < timeout:
            query_response = self.http_client.get(
                "/api/v1/chat/query",
                params={"conv_id": conv_id},
            )

            if not query_response.get("success"):
                error_code = query_response.get("code", "")
                if error_code == "E0103" and retry_count < max_retries:
                    retry_count += 1
                    logger.debug(f"Session not found, retry {retry_count}/{max_retries}")
                    time.sleep(1)
                    continue
                raise APIError(message="Failed to query chat status", response=query_response)

            query_data = query_response.get("data", {})
            is_final = query_data.get("is_final", False)
            user_answer = query_data.get("user_answer", "")

            if is_final:
                if user_answer:
                    yield user_answer
                return

            time.sleep(1)

        raise TimeoutError(
            message="Chat timed out",
            suggestion=f"The chat did not complete within {timeout} seconds.",
        )

    def chat_async(
        self,
        user_input: str,
        conv_uid: Optional[str] = None,
        app_code: Optional[str] = None,
        model_name: Optional[str] = None,
        timeout: int = 300,
    ) -> str:
        """Send chat message in async mode and get complete response.

        Args:
            user_input: User input message
            conv_uid: Conversation UID
            app_code: App code
            model_name: Model name
            timeout: Timeout in seconds

        Returns:
            Complete response text
        """
        result_chunks = []
        for chunk in self.chat_completions(
            user_input=user_input,
            conv_uid=conv_uid,
            app_code=app_code,
            model_name=model_name,
            incremental=True,
            timeout=timeout,
        ):
            result_chunks.append(chunk)

        return "".join(result_chunks)

    def delete_conversation(self, conv_uid: str) -> bool:
        """Delete a conversation.

        Args:
            conv_uid: Conversation UID

        Returns:
            True if deleted successfully
        """
        response = self.http_client.post(
            "/api/v1/chat/dialogue/delete",
            params={"con_uid": conv_uid},
        )
        return response.get("success", False)

    def list_conversations(
        self,
        user_name: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> List[ConversationResponse]:
        """List conversations.

        Args:
            user_name: User name
            page: Page number
            page_size: Page size

        Returns:
            List of conversations
        """
        params: Dict[str, Any] = {"page": page, "page_size": page_size}
        if user_name:
            params["user_name"] = user_name

        response = self.http_client.get(
            "/api/v1/chat/dialogue/list",
            params=params,
        )

        if response.get("success") and response.get("data"):
            return [ConversationResponse(**item) for item in response["data"]]
        return []

    def list_models(self) -> List[ModelInfo]:
        """List available healthy models.

        Returns:
            List of healthy models (deduplicated by model_name, first one kept)
        """
        response = self.http_client.get("/api/v2/serve/model/models")

        if response.get("success") and response.get("data"):
            seen_names = set()
            healthy_models = []
            for item in response["data"]:
                if item.get("healthy"):
                    model_name = item.get("model_name")
                    if model_name and model_name not in seen_names:
                        seen_names.add(model_name)
                        healthy_models.append(ModelInfo(**item))
            return healthy_models
        return []

    def stop_chat(self, conv_session_id: str) -> bool:
        """Stop chat.

        Args:
            conv_session_id: Conversation session ID

        Returns:
            True if stopped successfully
        """
        response = self.http_client.post(
            "/api/v1/chat/stop",
            params={"conv_session_id": conv_session_id},
        )
        return response.get("success", False)
