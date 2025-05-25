from langgraph.graph import StateGraph, START, END

from app.service.place_search import search_travel_places

from app.service.chat_gpt import llm, llm_4
from typing import Annotated, Sequence, TypedDict, Literal, Dict
import functools
import operator

from pydantic import BaseModel
from langchain.tools import tool
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from langgraph.graph import START, END, StateGraph
from langgraph.prebuilt import create_react_agent, ToolNode

import datetime
today = datetime.date.today().isoformat()

# ────[2] Travel Destination Searcher agent ─────────────────────────────────────────────────
travel_destination_search_system_prompt = f"""
당신은 여행지의 관광지, 맛집 정보를 검색하는 전문가입니다.

# 당신의 역할:
- 사용자가 제공한 여행지 또는 키워드를 기반으로 관광지나 맛집, 숙소 정보를 search_travel_places 툴로 검색하여 정리합니다.
- 검색 결과는 텍스트 형태로 요약 정보(이름, 주소, 유형, 설명, 링크 등)를 포함합니다.
- 사용자가 "여행지", "관광지", "명소", "맛집" 등 복합 요청을 할 경우,
  반드시 각각 별개의 `search_travel_places` Tool 호출로 나누어 검색해야 합니다.

# 반드시 지켜야 할 조건:
검색 결과는 반드시 Tool의 반환값(JSON)만을 사용해야 하며, 다음과 같은 형식으로 정리합니다:
- 예시 포맷:
  - **이름**: 장소 이름
  - **주소**: 장소 주소
  - **유형**: category
  - **설명**: 장소에 대한 설명
  - **링크**: 관련 웹사이트나 지도 링크
- 툴 결과 정보를 변형하지 마세요. JSON 필드 외에 있는 정보를 사용하지 마세요.
- 사용자가 명시적으로 검색을 요청한 경우 혹은 여행지 정보가 부족한 경우에만 실행합니다.

 # 예시 질의:
- "제주도에서 가볼 만한 관광지 추천해줘"
- "서울 강남구 맛집 검색해줘"
- "부산 해운대 근처 숙소 정보 알려줘"
- "인천 송도에서 할 만한 활동 추천해줘"
- "전주 한옥마을 주변 카페 정보 찾아줘"

# 주의사항:
- 장소 이름을 임의로 지어내거나, 존재하지 않는 정보를 생성하지 마세요.
- 계획서를 직접 생성하려고 시도하지 마세요. 당신의 역할은 오직 검색입니다.
- 당신이 툴 결과를 변형하거나 존재하지 않는 정보를 제공할 경우, 사용자에게 잘못된 장소를 안내하는 심각한 오류가 발생합니다.
- 툴 결과를 요약하거나 정리할 수는 있지만, 추가하거나 새로 만들어서는 안 됩니다.
"""
travel_destination_search_agent = create_react_agent(llm_4,
                                        tools=[search_travel_places],
                                        state_modifier=travel_destination_search_system_prompt)
def travel_destination_search_node(state: Dict) -> Dict:
    result = travel_destination_search_agent.invoke(state)
    # wrap into the graph's expected "messages" format
    return {"messages": [HumanMessage(content=result["messages"][-1].content, name="Travel_Destination_Searcher")]}
