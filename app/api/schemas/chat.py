from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class ChatConversationCreate(BaseModel):
    user_a_id: int
    user_b_id: int

class ChatConversationResponse(BaseModel):
    id: int
    user_a_id: int
    user_b_id: int
    last_message: Optional[str]
    last_message_time: Optional[datetime]
    unread_count_a: int
    unread_count_b: int
    is_pinned: bool
    created_at: datetime
    target_name: str
    target_avatar: Optional[str]

    class Config:
        orm_mode = True

class ChatMessageCreate(BaseModel):
    conversation_id: int
    sender_id: int
    content: Optional[str]
    msg_type: str = "text"
    file_url: Optional[str]
    file_name: Optional[str]

class ChatMessageResponse(BaseModel):
    id: int
    conversation_id: int
    sender_id: int
    content: Optional[str]
    msg_type: str
    file_url: Optional[str]
    file_name: Optional[str]
    is_read: bool
    created_at: datetime
    sender_name: Optional[str]
    sender_avatar: Optional[str]

    class Config:
        orm_mode = True

class ChatConversationDetailResponse(ChatConversationResponse):
    messages: List[ChatMessageResponse] = []