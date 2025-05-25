import streamlit as st
import requests
import json
from langchain_core.messages import HumanMessage

API_URL = "http://localhost:8000/chat/stream"

# 초기화
if "history" not in st.session_state:
    st.session_state["history"] = []

if "conversations" not in st.session_state:
    st.session_state["conversations"] = []

st.set_page_config(page_title="여행 일정 도우미", page_icon="✈️")
st.title("✈️ 여행 일정 도우미")

# st.markdown("## [DEBUG] st.session_state")
# st.json(st.session_state)

# 과거 대화 기록 출력
# st.subheader("대화 기록")
for i, entry in enumerate(st.session_state["conversations"]):
    st.markdown(f"### 💁🏻 Q{i+1}: {entry['question']}")
    
    if entry["steps"]:
        st.markdown("**🛠 중간 처리 과정:**")
        for step in entry["steps"]:
            for node_name, node_output in step.items():
                if isinstance(node_output, dict) and "messages" in node_output and node_output["messages"]:
                    content = node_output["messages"][-1]["content"]
                    with st.expander(f"{node_name} 단계 응답"):
                        st.markdown(content, unsafe_allow_html=True)

                    # st.markdown(last_msg["content"], unsafe_allow_html=True)
    st.markdown(f"🛫 **답변:**\n\n{entry['answer']}", unsafe_allow_html=True)

# 사용자 입력
st.divider()
# st.markdown("## 새로운 질문 입력")
user_input = st.text_input("질문을 입력하세요:")

if st.button("질문하기") and user_input:
    # 1. 현재까지의 대화 context 구성
    messages = st.session_state["history"] + [{"role": "human", "content": user_input}]
    steps = []
    latest_box = st.empty()

    if "stream_buffer" not in st.session_state:
        st.session_state["stream_buffer"] = []
    try:
        with requests.post(API_URL, json={"messages": messages}, stream=True) as r:
            r.raise_for_status()
            for line in r.iter_lines():
                if line:
                    try:
                        step = json.loads(line.decode("utf-8"))
                        steps.append(step)

                        # 실시간 표시 (가장 마지막 메시지)
                        for node_data in step.values():
                            if "messages" in node_data and node_data["messages"]:
                                content = node_data["messages"][-1]["content"]
                                st.session_state["stream_buffer"].append(content)
                                latest_box.markdown("\n\n".join(st.session_state["stream_buffer"]), unsafe_allow_html=True)
                                # latest_box.markdown(f"⏳ 진행 중: {content}", unsafe_allow_html=True)
                    except Exception as parse_err:
                        latest_box.error(f"응답 파싱 실패: {parse_err}")
    except Exception as e:
        st.error(f"❌ 오류 발생: {e}")
        st.stop()

    # 2. 마지막 valid 응답 추출
    final_answer = "응답을 생성하지 못했습니다."
    for step in reversed(steps):
        for v in step.values():
            if "messages" in v and v["messages"]:
                final_answer = v["messages"][-1]["content"]
                break
        if final_answer != "응답을 생성하지 못했습니다.":
            break
    st.markdown(final_answer)

    # 3. 상태 저장 및 표시
    st.session_state["history"].append({"role": "human", "content": user_input})
    st.session_state["history"].append({"role": "ai", "content": final_answer})
    st.session_state["conversations"].append({
        "question": user_input,
        "answer": final_answer,
        "steps": steps
    })

    st.rerun()  # 최신 반영 위해 새로고침
