# ────[3] Create a travel itinerary ────────────────────────────────────────────────

import datetime
from langchain_core.messages import HumanMessage, SystemMessage
from app.service.chat_gpt import llm
from langchain.tools import tool
import datetime
today = datetime.date.today()
today_str = today.strftime("%Y-%m-%d")                 # → '2025-05-25'
weekday_str = today.strftime("%A")  
weekday_str_kor = ["월요일", "화요일", "수요일", "목요일", "금요일", "토요일", "일요일"][today.weekday()]

@tool
def generate_itinerary(location: str, wanna_go_place: str,start_date: str, end_date: str, num_people: int = 1, purpose: str = "") -> str:
    """
    여행지(location), 여행 기간(start_date ~ end_date), 인원 수(num_people), 여행 목적(purpose), 방문 희망 장소(wanna_go_place)를 기반으로 
    텍스트 형식의 여행 일정 계획서를 생성합니다.

    # 파라미터 설명:
    - `location`: 여행할 지역 또는 도시 (예: "제주도", "부산")
    - `wanna_go_place`: 방문하고 싶은 장소들의 목록 (관광지, 식당, 카페 등). 사용자가 직접 제공했거나 Travel_Destination_Searcher 에이전트를 통해 수집된 정보로 구성되며, 장소 이름, 주소, 카테고리 등의 풍부한 정보가 포함됩니다.
    - `start_date`, `end_date`: 여행 시작일과 종료일 (형식: YYYY-MM-DD)
    - `num_people`: 여행 인원 수 (예: 2)
    - `purpose`: 여행의 주요 목적 (예: 힐링, 가족여행, 맛집 탐방 등)

    # 출력 결과:
    - 여행 개요 (일정, 인원, 목적 등)
    - 일정 요약 (일자별 요약표)
    - 일자별 세부 일정 (시간대별 활동 + 장소 설명 + 동선 고려)
    - 준비물 및 유의사항
    - 날짜는 `YYYY-MM-DD` 형식, 시간은 `HH:MM~HH:MM` 형식으로 표기

    이 Tool은 오직 계획서 생성에만 사용됩니다. 장소 검색은 수행하지 않으며, 이미 확보된 장소 정보를 기반으로 최적의 일정을 구성합니다.
    """
    
    # 시스템 메시지 작성
    system_msg = SystemMessage(content=
        f"""
        당신은 여행 계획 전문가입니다. Markdown 형식의 여행 계획서를 작성하세요.
        - 시간은 모두 24시간제 HH:MM~HH:MM 형식으로 표기
        - 날짜 표현은 YYYY-MM-DD 또는 MM월 DD일, 요일 형식 사용
        - 모든 일정은 반드시 오늘({today_str}, {weekday_str_kor}) 이후 날짜로 생성
        - 오늘 이전 날짜로 계획을 짜거나 일정이 포함되어 있다면 무시하거나 사용자에게 다시 날짜를 요청하세요.
        - 1. 여행 개요, 2. 일정 요약, 3. 일자별 세부 일정, 4. 준비물 및 유의사항 순서로 구성
        - 여행지, 기간, 인원, 여행 목적을 포함하여 작성
        - 제공된 '가고 싶은 장소들'을 바탕으로 여행 계획서 작성
        - 제공된 '가고 싶은 장소들' 좌표 정보가 있다면, 참고하여 서로 가까운 관광지끼리 묶어서 동선 효율적인 일정표를 작성해줘.
        - 사용자의 여행 목적에 맞는 관광지 및 활동을 포함
        - 예시:
            # 여행 계획서
            ## 1. 여행 개요
            * **여행지:** 제주도
            * **기간:** 2025-06-12 ~ 2025-06-15 (3박 4일)
            * **인원:** 성인 2명
            * **여행 목적:** 자연 풍경 감상 · 음식 체험 · 힐링

            ## 2. 일정 요약
            1. **1일차 (YYYY-MM-DD):** ...
            2. **2일차 (YYYY-MM-DD):** ...
            3. ...

            ## 3. 일자별 세부 일정
            ### 1일차 (YYYY-MM-DD)
            * **08:30** ~ **09:50** 이동 및 일정
            * **10:00** ~ **12:00** 관광지 방문
            * ...

            ## 4. 준비물 및 유의사항
            * 준비물: ...
            * 유의사항: ...

        - 사용자가 제공한 정보만을 사용하여 작성하며, 혼자 생성된 내용(환각)을 내놓아서는 안 됩니다. 
        """
    )
    
    # 사용자 메시지 생성
    user_content = (
        f"여행지: {location}\n"
        f"가고 싶은 장소들: {wanna_go_place}\n"
        f"시작일: {start_date}\n"
        f"종료일: {end_date}\n"
        f"인원: {num_people}명\n"
        + (f"여행 목적: {purpose}\n" if purpose else "")
    )
    user_msg = HumanMessage(content=user_content)

    # LLM 호출
    response = llm([system_msg, user_msg])
    print(f"========= 여행 계획서 생성 결과: =========\n\n{response['choices'][0]['message']['content']}")
    md_content = response["choices"][0]["message"]["content"]
    # 3) 파일로 쓰기
    output_path = "itinerary.md"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(md_content)
    
    print(f"여행 계획서가 {output_path}에 저장되었습니다.")
    print(md_content)
    return response["choices"][0]["message"]["content"]
