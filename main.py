import streamlit as st
import fitz
import base64
import requests
import io
import re

st.set_page_config(page_title="GitHub PDF 검색기", layout="wide")

# --- CSS 디자인 (PAGE 옆에 버튼 배치) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Pretendard:wght@400;600&display=swap');
    html, body, [class*="st-"] { font-family: 'Pretendard', sans-serif; }
    .result-box { background-color: #ffffff; border: 1px solid #e1e4e8; border-radius: 12px; padding: 20px; margin-bottom: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.05); }
    .header-container { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; border-bottom: 1px solid #f0f2f5; padding-bottom: 10px; }
    .page-label { font-size: 0.9rem; color: #444; font-weight: 700; }
    .view-button { background-color: #f0f7ff; color: #0056b3 !important; padding: 5px 15px; border-radius: 6px; text-decoration: none; font-size: 0.85rem; font-weight: 600; border: 1px solid #cce3ff; transition: 0.2s; }
    .view-button:hover { background-color: #0056b3; color: white !important; }
    .highlight { background-color: #fff5b1; color: #d73a49; font-weight: bold; padding: 0 2px; }
    </style>
    """, unsafe_allow_html=True)

# 1. 깃허브에서 PDF 데이터 가져오기 및 인덱싱
@st.cache_resource
def load_github_pdfs(url_list):
    all_indexed_data = []
    for url in url_list:
        response = requests.get(url)
        pdf_file = io.BytesIO(response.content)
        doc = fitz.open(stream=pdf_file, filetype="pdf")
        file_name = url.split("/")[-1]
        
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            text = page.get_text("text")
            # 문장 단위 정제 및 합치기
            cleaned_text = re.sub(r'\n+', ' ', text)
            sentences = re.split(r'(?<=[.!?])\s+', cleaned_text)
            all_indexed_data.append({
                "file_name": file_name,
                "url": url,
                "page": page_num + 1,
                "sentences": sentences
            })
    return all_indexed_data

# 깃허브 Raw URL 리스트 (여기에 실제 주소를 넣으세요)
PDF_URLS = [
    "https://raw.githubusercontent.com/사용자/레포/main/file1.pdf",
    "https://raw.githubusercontent.com/사용자/레포/main/file2.pdf"
]

with st.spinner("깃허브에서 PDF 분석 중..."):
    pdf_index = load_github_pdfs(PDF_URLS)

st.title("📂 GitHub PDF 통합 검색 시스템")

# 검색 및 중지 컨트롤
col1, col2 = st.columns([0.8, 0.2])
with col1:
    keyword = st.text_input("검색어 입력", placeholder="검색어를 입력하고 엔터를 누르세요", key="main_search")
with col2:
    st.write(" ")
    stop_triggered = st.button("🛑 검색 즉시 중지", use_container_width=True)

if stop_triggered:
    st.warning("검색이 중단되었습니다.")
    st.stop()

if keyword:
    found_any = False
    seen_contexts = set()
    
    # 검색 진행바 (시각적 효과)
    progress_bar = st.progress(0)
    
    for idx, data in enumerate(pdf_index):
        # 중지 버튼 클릭 여부 체크 (Streamlit 자동 재실행 활용)
        progress_bar.progress((idx + 1) / len(pdf_index))
        
        page_num = data["page"]
        file_name = data["file_name"]
        sentences = data["sentences"]

        for i, sent in enumerate(sentences):
            if keyword in sent:
                start = max(0, i - 1)
                end = min(len(sentences), i + 2)
                context = " ".join(sentences[start:end]).strip()

                if context not in seen_contexts:
                    found_any = True
                    seen_contexts.add(context)
                    
                    highlighted_text = context.replace(keyword, f'<span class="highlight">{keyword}</span>')
                    # 깃허브 URL 뒤에 페이지 번호 붙여서 바로 열기
                    view_url = f"{data['url']}#page={page_num}"

                    st.markdown(f"""
                        <div class="result-box">
                            <div class="header-container">
                                <span class="page-label">📄 {file_name} | PAGE: {page_num}</span>
                                <a href="{view_url}" target="_blank" class="view-button">해당 페이지 보기</a>
                            </div>
                            <div style="line-height:1.8; color:#333;">{highlighted_text}</div>
                        </div>
                    """, unsafe_allow_html=True)

    progress_bar.empty()
    if not found_any:
        st.warning(f"'{keyword}'에 대한 검색 결과가 없습니다.")