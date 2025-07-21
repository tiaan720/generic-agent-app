from __future__ import annotations

from typing import TypedDict

from langgraph.graph import add_messages
from typing_extensions import Annotated


class OverallState(TypedDict):
    messages: Annotated[list, add_messages]
