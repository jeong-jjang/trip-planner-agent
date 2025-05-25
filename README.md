# 여행 일정 생성 에이전트 - Travel Planner Agent System

LangGraph 기반의 에이전트 분기 구조와 FastAPI + Streamlit UI를 결합하여  
**여행지 추천 → 일정 생성 → 캘린더 등록 → 이메일 공유**까지 자동화된 여행 플래너 서비스를 제공합니다.  
실시간 스트리밍 응답과 다단계 Agent 흐름을 통해 사용자 친화적이며 신뢰할 수 있는 여행 경험을 제공합니다.

---

## 프로젝트 구조

TRAVEL_AGENT/
│
├── app/
│ ├── agents/ # 각 기능을 담당하는 에이전트
│ │ ├── Scheduler.py
│ │ ├── Travel_Destination_Searcher.py
│ │ ├── Travel_Itinerary_Share.py
│ │ └── Travel_Planner.py
│ │
│ ├── frontend/ # Streamlit UI
│ │ └── ui.py
│ │
│ ├── graph/ # LangGraph 워크플로우 정의
│ │ ├── supervisor.py
│ │ └── workflow.py
│ │
│ ├── service/ # 외부 API 및 내부 유틸 서비스
│ │ ├── chat_gpt.py
│ │ ├── email_sender.py
│ │ ├── google_calendar.py
│ │ ├── place_search.py
│ │ └── planner.py
│ │
│ └── main.py # FastAPI 실행 진입점
│
├── .env # API Key 등 환경 변수
├── environment.full.yml # Conda 환경 설정 파일
├── Makefile # 실행 명령 자동화
├── requirements.txt # 의존성 목록
└── README.md # 프로젝트 설명 문서

---

## 실행 방법

### Conda 환경 구성

```bash
conda env create -f environment.full.yml
conda activate Flanner

# API 서버 및 UI 실행
make run-api     # FastAPI 실행 (localhost:8000)
make run-ui      # Streamlit UI 실행

# 또는 수동 실행:
PYTHONPATH=. uvicorn app.main:app --reload # FastAPI 서버 실행 (Streaming API 포함)
PYTHONPATH=. streamlit run app/frontend/ui.py # Streamlit UI 실행
```

### .env 환경 설정
NAVER_CLIENT_ID=xxxx
NAVER_CLIENT_SECRET=xxxx
GOOGLE_KEY_FILE=app/service/xxxx.json
CAL_ID=your_calendar_id@group.calendar.google.com
SENDER=youremail@gmail.com
EMAIL_PASWORD=xxxxxx # Gmail OAuth2 토큰

## 서비스 개요
- 사용자 입력 기반으로 LLM 에이전트들이 순차적으로 동작
- 각 노드는 LangGraph 기반으로 구성되어 Supervisor → 에이전트 → Supervisor 순환 흐름 유지
- 최종 응답 전까지 각 노드의 메시지를 StreamingResponse로 전송


## 주요 에이전트 기능

| Agent 이름                      | 역할                         | 입력 조건 및 판단 로직 (Supervisor에 의해 분기됨) |
| ----------------------------- | -------------------------- | ---------------------------------- |
| `Travel_Destination_Searcher` | 여행지, 맛집, 숙소 등 장소 검색        | 키워드 기반 요청 또는 장소 정보 부족 시 호출         |
| `Travel_Planner`              | 장소 기반 일정표(계획서) 마크다운 생성     | 장소 목록 + 일정 요청 발화 포함 시 호출           |
| `Scheduler`                   | 일정을 Google Calendar에 등록/조회/수정/삭제 | "일정 등록/삭제/변경" 등의 발화 포함 시 호출        |
| `Travel_Itinerary_Share`      | 이메일로 계획서 공유                | "이메일 보내줘", "계획 공유해줘" 등 포함 시 호출     |

- Supervisor는 LLM 기반 CoT reasoning을 통해 위 에이전트 중 하나를 분기
- 각 하위 에이전트는 자신의 역할만 수행하며, ToolNode 형태로 정의되며 Tool 호출을 포함해야 결과가 유효
- 입력 정보가 부족할 경우, 즉시 사용자에게 요청합니다.

### Tool 목록
- search_travel_places: Naver Local API 기반 장소 검색
- generate_itinerary: 사용자가 제공한 장소/일정 기반 Markdown 계획서 생성
- create_event, create_multiple_events, update_event, delete_event, list_events: Google Calendar API 연동
- send_email_text: 여행 계획서를 HTML 이메일로 발송

## ✅ 예시 사용 흐름
1. 사용자: “6월 12일부터 3박 4일간 제주도 여행, 맛집도 찾아줘”

2. 시스템 흐름:
- 장소 검색 (Travel_Destination_Searcher)
- 일정 생성 (Travel_Planner)
- 캘린더 등록 (Scheduler)
- 이메일 공유 (Travel_Itinerary_Share)

3. 최종 결과:
- 사용자에게 실시간으로 중간 처리 결과 출력
- 최종 여행 계획서 및 등록 완료 메시지 전달

## 기술 스택
- LLM 기반:
    - LangGraph: StateGraph, Supervisor 기반 분기 흐름
    - LangChain: ToolNode 기반 Agent 추론 구조
    - Chat GPT 4o / Chat GPT 4o-mini
- Flow Controller: Supervisor Agent (Chain-of-Thought + Guardrail 포함)
- API 서버: FastAPI
- UI 인터페이스: Streamlit
- 캘린더 연동: Google Calendar API
- 이메일 발송: Gmail SMTP
- 검색 연동: Naver Local API (관광지/맛집 검색)

## Guardrail & Supervisor Logic
- 같은 Agent의 연속 호출 방지
- 장소 없음 → Planner 금지, 공유 완료 → FINISH 등 규칙 기반 분기
- 에이전트 실행 조건은 명시적으로 정의된 system prompt 기준으로 결정

## 개발 의도 및 확장성
이 프로젝트는 단순한 챗봇이 아닌, 실제 일정 생성과 공유까지 가능한 자동화된 에이전트 시스템을 목표로 합니다.
- LangGraph 기반으로 agent들의 작업 흐름을 유연하게 관리
- LLM 출력 신뢰성을 높이기 위해 구조적 입력/출력(JSON 기반 상태) 사용
- 향후:
    - 호텔 예약 / 교통편 추천 기능 연동
    - 사용자 맞춤형 여행 리포트 생성
    - 멀티 모달 UI 확장 가능
    - 숙소 정보 수집 및 비교 기능
    - 여행 스타일(힐링/모험/가족형 등)에 따른 자동화된 여행 테마 추천
    - 여행 보고서 PDF 다운로드 기능
    - LangSmith 기반 품질 평가 및 피드백 저장 기능

## 참고 결과물
- [부산_여행 일정 도우미.pdf](./부산_여행 일정 도우미.pdf): 실제 에이전트를 통해 생성된 여행 계획서
-  Google Calendar, Gmail, Streamlit 인터페이스까지 통합된 end-to-end 작동 결과

