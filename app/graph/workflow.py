from langgraph.graph import StateGraph, START, END
from .supervisor import supervisor_agent

from app.agents.Travel_Planner import travel_plan_node
from app.agents.Travel_Destination_Searcher import travel_destination_search_node
from app.agents.Travel_Itinerary_Share import itinerary_share_node
from app.agents.Scheduler import scheduler_node

from typing import Annotated, Sequence, TypedDict, Literal, Dict, Optional
import functools
import operator

from pydantic import BaseModel
from langchain.tools import tool
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from langgraph.graph import START, END, StateGraph
from langgraph.prebuilt import create_react_agent, ToolNode
# ─── Worker agent nodes ──────────────────────────────────────────────────────

# Define AgentState for the graph
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    next: str
    last_agent: Optional[str]

def get_next(state):
    return state["next"]

members = [
    "Scheduler",                  # 캘린더 일정 생성·조회·수정·삭제
    "Travel_Destination_Searcher",# 여행지·관광지 검색
    "Travel_Planner",             # 여행 계획서(일정표) 생성
    "Travel_Itinerary_Share"      # 여행 계획서 이메일 공유
]
options = ["FINISH"] + members

# ─── Build and compile the workflow ───────────────────────────────────────────

# 1) Instantiate graph
workflow = StateGraph(AgentState)

# 2) Add nodes
workflow.add_node("Scheduler", scheduler_node)
workflow.add_node("Travel_Destination_Searcher", travel_destination_search_node)
workflow.add_node("Travel_Planner", travel_plan_node)
workflow.add_node("Travel_Itinerary_Share", itinerary_share_node)
workflow.add_node("supervisor", supervisor_agent)

# 3) Wire edges for round-trip
for member in members:
    workflow.add_edge(member, "supervisor")
workflow.add_edge(START, "supervisor")

# turn your router into a BaseTool
@tool
def route_next(state: dict) -> str:
    """Supervisor가 정한 next 필드에 따라 분기"""
    return state["next"]

# 4) Add conditional router
conditional_map = {m: m for m in members}
conditional_map["FINISH"] = END

workflow.add_conditional_edges(
    "supervisor",
    get_next,
    conditional_map
)

# 5) Compile the graph
graph = workflow.compile()
