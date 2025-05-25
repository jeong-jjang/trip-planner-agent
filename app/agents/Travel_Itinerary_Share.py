from langgraph.graph import StateGraph, START, END

from app.service.email_sender import send_email_text
from app.service.chat_gpt import llm

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

import os
from dotenv import load_dotenv

# 상대 경로로 .env 불러오기
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "../../.env"))

SENDER = os.getenv("SENDER")
EMAIL_PASWORD = os.getenv("EMAIL_PASWORD")  # 앱 비밀번호 또는 OAuth2 토큰
# ────[4] Itinerary Share agent ────────────────────────────────────────────────
itinerary_share_node_system_prompt = f"""
당신은 여행 계획서를 이메일로 공유하는 역할을 담당합니다.

# 당신의 목표:
- 여행 계획서를 텍스트 형식으로 입력받아, 사용자가 지정한 이메일로 **메일 제목**과 함께 전송하는 것입니다.
- 다음 정보를 반드시 확인하고 포함하세요:
  - 발신자 이메일(sender): 기본값은 {SENDER}
  - 비밀번호(password): 기본값은 {EMAIL_PASWORD}
  - 수신자 이메일(recipient): 사용자가 반드시 명시해야 합니다.
  - 메일 제목(subject): 사용자가 제공하지 않으면 `여행 계획서 공유드립니다`로 설정합니다.
  - 본문 내용(html_body): 마크다운 형식으로 입력된 여행 계획서를 html형식으로 포함해야 합니다.

# 주의사항:
- 모든 입력 필드가 누락되지 않았는지 확인하고, 누락된 정보가 있다면 사용자에게 요청하세요.
- 메일 전송 후 '여행 계획표를 이메일로 공유했습니다.'라는 메시지를 반환하세요.

# 예시 질의:
- "6월 12~15일 제주 여행 계획서를 제 친구에게 공유하고 싶어요. 이메일은 friend@example.com이에요."
- "저장된 여행 계획서를 공유해 주세요. 수신자는 travelmate@naver.com 입니다."

- 가능하면 다음과 같이 Tool 호출 형식을 구성하세요:

{{
  'tool': 'send_email_text',
  'params': {{
    'sender': 'sender@gmail.com',
    'password': 'zchb uryq fkwi feha',
    'recipient': 'friend@example.com'
    'subject': '여행 계획서 공유드립니다',
    'html_body': '<html><body>여행 계획서 내용...</body></html>'
  }}
}}

# 절대 하지 말 것:
- 여행 계획서 공유 외 다른 작업(예: 여행 계획서 작성, 검색 등)은 하지 마세요.
- 에이전트는 절대로 사실 확인되지 않은 정보를 말하거나, 툴 호출 없이 혼자 생성된 내용(환각)을 내놓아서는 안 됩니다.
"""
itinerary_share_agent = create_react_agent(llm,
                                          tools=[send_email_text],
                                        state_modifier=itinerary_share_node_system_prompt)
def itinerary_share_node(state: Dict) -> Dict:
    result = itinerary_share_agent.invoke(state)
    # wrap into the graph's expected "messages" format
    fin_content = f"[SHARE_COMPLETE]"
    return {"messages": [HumanMessage(content=fin_content+result["messages"][-1].content, name="Travel_Itinerary_Share")]}

