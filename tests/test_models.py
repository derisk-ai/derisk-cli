"""Tests for data models."""

import pytest

from openderisk_cli.models import (
    ChatCompletionRequest,
    ChatCompletionResponseStreamChoice,
    ChatCompletionStreamResponse,
    ConversationResponse,
    DeltaMessage,
    GptsApp,
    GptsAppResponse,
    McpCreateRequest,
    McpRunRequest,
    McpServer,
    McpTool,
)


class TestMcpServer:
    """Tests for McpServer model."""

    def test_required_fields(self) -> None:
        """Test McpServer with required fields only."""
        server = McpServer(mcp_code="test-mcp", name="Test MCP")
        assert server.mcp_code == "test-mcp"
        assert server.name == "Test MCP"

    def test_all_fields(self) -> None:
        """Test McpServer with all fields."""
        server = McpServer(
            mcp_code="full-mcp",
            name="Full MCP",
            description="A test MCP server",
            type="sse",
            author="Test Author",
            version="1.0.0",
            sse_url="https://example.com/mcp",
            available=True,
        )
        assert server.mcp_code == "full-mcp"
        assert server.name == "Full MCP"
        assert server.description == "A test MCP server"
        assert server.type == "sse"
        assert server.author == "Test Author"
        assert server.version == "1.0.0"
        assert server.sse_url == "https://example.com/mcp"
        assert server.available is True

    def test_model_dump(self) -> None:
        """Test model_dump output."""
        server = McpServer(mcp_code="test", name="Test")
        data = server.model_dump()
        assert data["mcp_code"] == "test"
        assert data["name"] == "Test"


class TestMcpTool:
    """Tests for McpTool model."""

    def test_required_fields(self) -> None:
        """Test McpTool with required fields only."""
        tool = McpTool(name="test_tool")
        assert tool.name == "test_tool"

    def test_with_description(self) -> None:
        """Test McpTool with description."""
        tool = McpTool(name="test_tool", description="A test tool")
        assert tool.name == "test_tool"
        assert tool.description == "A test tool"


class TestMcpCreateRequest:
    """Tests for McpCreateRequest model."""

    def test_empty_request(self) -> None:
        """Test empty McpCreateRequest."""
        request = McpCreateRequest()
        assert request.mcp_code is None
        assert request.name is None

    def test_with_fields(self) -> None:
        """Test McpCreateRequest with fields."""
        request = McpCreateRequest(
            name="New MCP",
            description="Description",
            type="stdio",
        )
        assert request.name == "New MCP"
        assert request.description == "Description"
        assert request.type == "stdio"


class TestMcpRunRequest:
    """Tests for McpRunRequest model."""

    def test_required_fields(self) -> None:
        """Test McpRunRequest with required fields."""
        request = McpRunRequest(name="run-mcp")
        assert request.name == "run-mcp"

    def test_with_params(self) -> None:
        """Test McpRunRequest with params."""
        request = McpRunRequest(
            name="run-mcp",
            stdio_cmd="python server.py",
            params={"arg1": "value1"},
        )
        assert request.name == "run-mcp"
        assert request.stdio_cmd == "python server.py"
        assert request.params == {"arg1": "value1"}


class TestChatCompletionRequest:
    """Tests for ChatCompletionRequest model."""

    def test_default_values(self) -> None:
        """Test default values."""
        request = ChatCompletionRequest()
        assert request.user_input == ""
        assert request.temperature == 0.5
        assert request.max_new_tokens == 64000
        assert request.incremental is True
        assert request.work_mode == "async"

    def test_with_user_input(self) -> None:
        """Test with user input."""
        request = ChatCompletionRequest(user_input="Hello, world!")
        assert request.user_input == "Hello, world!"

    def test_with_all_fields(self) -> None:
        """Test with all fields."""
        request = ChatCompletionRequest(
            conv_uid="conv-123",
            user_input="Test message",
            model_name="gpt-4",
            temperature=0.7,
            max_new_tokens=1000,
        )
        assert request.conv_uid == "conv-123"
        assert request.user_input == "Test message"
        assert request.model_name == "gpt-4"
        assert request.temperature == 0.7
        assert request.max_new_tokens == 1000


class TestConversationResponse:
    """Tests for ConversationResponse model."""

    def test_required_fields(self) -> None:
        """Test with required fields."""
        response = ConversationResponse(conv_uid="conv-456")
        assert response.conv_uid == "conv-456"

    def test_with_all_fields(self) -> None:
        """Test with all fields."""
        response = ConversationResponse(
            conv_uid="conv-789",
            user_input="Hello",
            chat_mode="chat",
            app_code="app-001",
            model_name="gpt-4",
        )
        assert response.conv_uid == "conv-789"
        assert response.user_input == "Hello"
        assert response.chat_mode == "chat"
        assert response.app_code == "app-001"
        assert response.model_name == "gpt-4"


class TestDeltaMessage:
    """Tests for DeltaMessage model."""

    def test_empty(self) -> None:
        """Test empty DeltaMessage."""
        delta = DeltaMessage()
        assert delta.role is None
        assert delta.content is None

    def test_with_content(self) -> None:
        """Test DeltaMessage with content."""
        delta = DeltaMessage(role="assistant", content="Hello")
        assert delta.role == "assistant"
        assert delta.content == "Hello"


class TestChatCompletionStreamResponse:
    """Tests for ChatCompletionStreamResponse model."""

    def test_empty(self) -> None:
        """Test empty response."""
        response = ChatCompletionStreamResponse()
        assert response.id is None
        assert response.choices is None

    def test_with_choices(self) -> None:
        """Test response with choices."""
        delta = DeltaMessage(role="assistant", content="Test")
        choice = ChatCompletionResponseStreamChoice(index=0, delta=delta)
        response = ChatCompletionStreamResponse(
            id="chat-123",
            model="gpt-4",
            choices=[choice],
        )
        assert response.id == "chat-123"
        assert response.model == "gpt-4"
        assert len(response.choices) == 1


class TestGptsApp:
    """Tests for GptsApp model."""

    def test_empty(self) -> None:
        """Test empty GptsApp."""
        app = GptsApp()
        assert app.app_code is None
        assert app.app_name is None
        assert app.published is False

    def test_with_fields(self) -> None:
        """Test GptsApp with fields."""
        app = GptsApp(
            app_code="app-001",
            app_name="Test App",
            app_describe="A test application",
            team_mode="auto",
            published=True,
        )
        assert app.app_code == "app-001"
        assert app.app_name == "Test App"
        assert app.app_describe == "A test application"
        assert app.team_mode == "auto"
        assert app.published is True


class TestGptsAppResponse:
    """Tests for GptsAppResponse model."""

    def test_default_values(self) -> None:
        """Test default values."""
        response = GptsAppResponse()
        assert response.total_count == 0
        assert response.total_page == 0
        assert response.current_page == 0
        assert response.page_size == 20
        assert response.app_list == []

    def test_with_apps(self) -> None:
        """Test response with apps."""
        app1 = GptsApp(app_code="app-1", app_name="App 1")
        app2 = GptsApp(app_code="app-2", app_name="App 2")
        response = GptsAppResponse(
            total_count=2,
            total_page=1,
            current_page=1,
            app_list=[app1, app2],
        )
        assert response.total_count == 2
        assert len(response.app_list) == 2
        assert response.app_list[0].app_code == "app-1"
