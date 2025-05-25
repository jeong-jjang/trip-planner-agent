# ────[4] Search for travel locations ──────────────────────────────────────────────

# === nodes/search_node.py ===
import requests
from langchain_core.messages import HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain.tools import tool

import os
from dotenv import load_dotenv
NAVER_CLIENT_ID = os.getenv("NAVER_CLIENT_ID")
NAVER_CLIENT_SECRET = os.getenv("NAVER_CLIENT_SECRET")

@tool
def search_travel_places(query: str, limit: int = 5) -> str:
    """
    사용자의 요청에 따라 특정 여행지에 대한 관광지, 명소, 맛집 등의 장소 정보를 검색합니다.

    - `query`: 사용자가 찾고자 하는 장소에 대한 설명 또는 키워드 (예: "제주도 관광지 추천", "부산 해운대 근처 점심 맛집").
    - `limit`: 검색 결과 개수 (기본값은 5개).

    반환값은 각 장소에 대해 다음 정보를 포함한 목록입니다:
    - 장소명 (카테고리 포함)
    - 도로명 주소 또는 일반 주소
    - 전화번호
    - 간략 설명 (존재하는 경우)
    - 지도 좌표 (x, y)
    - 링크 URL (블로그/홈페이지 등)

    사용자는 이 Tool을 활용하여 여행 계획에 필요한 장소 정보를 얻을 수 있습니다.
    예를 들어, 계획서에 넣을 관광지나 하루 두 번의 식사 장소(점심/저녁)를 찾고자 할 때 활용됩니다.

    - 이 Tool은 장소 정보만 검색합니다. 계획서 작성은 하지 않으며, 장소 검색 후 해당 정보를 기반으로 다른 Agent가 계획서를 작성합니다.
    """

    headers = {
        "X-Naver-Client-Id": NAVER_CLIENT_ID,
        "X-Naver-Client-Secret": NAVER_CLIENT_SECRET,
    }
    url = "https://openapi.naver.com/v1/search/local.json"
    params = {
        "query": query,
        "display": limit,
        "sort": "comment"
    }
    response = requests.get(url, headers=headers, params=params)
    items = response.json().get("items", [])

    result_text = f"✅ {query} 검색 결과:\n"
    for i, item in enumerate(items, 1):
        title       = item['title'].replace("<b>", "").replace("</b>", "")
        category    = item.get("category", "")
        address     = item.get("address", "")
        road_addr   = item.get("roadAddress", "")
        phone       = item.get("telephone", "정보 없음")
        desc        = item.get("description", "").strip()
        mapx, mapy  = item.get("mapx"), item.get("mapy")
        link        = item.get("link", "")

        result_text += (
            f"{i}. {title} ({category})\n"
            f"   📍 주소: {road_addr or address}\n"
            f"   📞 전화: {phone}\n"
            + (f"   📝 설명: {desc}\n" if desc else "")
            + (f"   🗺 좌표: ({mapy}, {mapx})\n" if mapx and mapy else "")
            + f"   🔗 상세보기: {link}\n\n"
        )


    print(f"검색 결과: {result_text}")
    # return result_text
    results = []
    for item in items:
        results.append({
            "name": item['title'].replace("<b>", "").replace("</b>", ""),
            "category": item.get("category", ""),
            "address": item.get("roadAddress") or item.get("address", ""),
            "phone": item.get("telephone", ""),
            "description": item.get("description", ""),
            "coordinates": {"x": item.get("mapx"), "y": item.get("mapy")},
            "link": item.get("link", "")
        })
    if not items:
        return f"❌ '{query}'에 대해 검색 결과가 없습니다. 다른 키워드로 다시 시도해 주세요."

    return results

