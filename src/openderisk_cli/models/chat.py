"""Chat models."""

from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field


class ChatCompletionRequest(BaseModel):
    """Chat completion request model."""

    conv_uid: Optional[str] = Field(None, description="conversation uid")
    user_input: Union[str, Dict[str, Any]] = Field(default="", description="User input messages.")
    messages: Optional[List[Dict[str, Any]]] = Field(
        None, description="OpenAI compatible messages list"
    )
    app_code: Optional[str] = Field(None, description="app code")
    app_config_code: Optional[str] = Field(None, description="app config code")
    team_mode: Optional[str] = Field(None, description="team mode")
    user_name: Optional[str] = Field(None, description="user name")
    sys_code: Optional[str] = Field(None, description="system code")
    temperature: Optional[float] = Field(0.5, description="temperature")
    max_new_tokens: Optional[int] = Field(64000, description="max new tokens")
    model_name: Optional[str] = Field(None, description="model name")
    incremental: bool = Field(True, description="incremental output")
    select_param: Optional[Any] = Field(None, description="chat scene select param")
    prompt_code: Optional[str] = Field(None, description="prompt code")
    chat_in_params: Optional[List[Dict[str, Any]]] = Field(None, description="chat in params")
    ext_info: Optional[Dict[str, Any]] = Field(default_factory=dict, description="extra info")
    work_mode: Optional[str] = Field(
        "async", description="Work mode: simple, quick, background, async"
    )


class ConversationResponse(BaseModel):
    """Conversation response model."""

    conv_uid: str = Field(..., description="The conversation uid.")
    user_input: Optional[str] = Field(None, description="The user input.")
    chat_mode: Optional[str] = Field(None, description="The chat mode.")
    app_code: Optional[str] = Field(None, description="The chat app code.")
    select_param: Optional[str] = Field(None, description="The select param.")
    model_name: Optional[str] = Field(None, description="The model name.")
    user_name: Optional[str] = Field(None, description="The user name.")
    sys_code: Optional[str] = Field(None, description="The system code.")
    gmt_created: Optional[str] = Field(None, description="The record creation time.")
    gmt_modified: Optional[str] = Field(None, description="The record update time.")


class MessageVo(BaseModel):
    """Message model."""

    role: str = Field(..., description="The role that sends out the current message.")
    context: str = Field(..., description="The current message content.")
    order: int = Field(..., description="The current message order.")
    time_stamp: Optional[Any] = Field(None, description="The current message time stamp.")
    model_name: Optional[str] = Field(None, description="The model name.")
    feedback: Optional[Dict[str, Any]] = Field(default_factory=dict, description="feedback info")


class ModelInfo(BaseModel):
    """Model info."""

    model_name: str = Field(..., description="Model name")
    worker_type: Optional[str] = Field(None, description="Worker type")
    host: Optional[str] = Field(None, description="Host")
    port: Optional[int] = Field(None, description="Port")
    healthy: Optional[bool] = Field(None, description="Healthy status")
    last_heartbeat: Optional[str] = Field(None, description="Last heartbeat")


class DeltaMessage(BaseModel):
    """Delta message for streaming."""

    role: Optional[str] = None
    content: Optional[str] = None


class ChatCompletionResponseStreamChoice(BaseModel):
    """Chat completion stream choice."""

    index: Optional[int] = None
    delta: Optional[DeltaMessage] = None
    finish_reason: Optional[str] = None


class ChatCompletionStreamResponse(BaseModel):
    """Chat completion stream response."""

    id: Optional[str] = None
    created: Optional[int] = None
    model: Optional[str] = None
    choices: Optional[List[ChatCompletionResponseStreamChoice]] = None
