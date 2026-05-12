import streamlit as st
import fitz
import base64
import re
import os

# 페이지 설정
st.set_page_config(page_title="PDF 통합 검색기", layout="wide")

# --- UI 스타일 복구 (이전 스타일) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Pretendard:wght@400;600&display=swap');
    html, body, [class*="st-"] { font-family: 'Pretendard', sans-serif; }
    
    .result-box {
        background-color: #ffffff;
        border: 1px solid #e1e4e8;
        border-radius: 12px;
        padding: 25px;
        margin-bottom: 20px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
        position: relative;
    }
    .page-label {
        font-size: 0.85rem;
        color: #6a737d;
        font-weight: bold;
        margin-bottom: 10px;
    }
    .content-text {
        font-size: 1.05rem;
        line-height: 1.7;
        color: #24292e;
        white-space: pre-wrap;
    }
    .highlight {
        background-color: #fff5b1;
        color: #d73a49;
        font-weight: bold;
        padding: 0 4px;
        border-radius: 3px;
    }
    /* 버튼 스타일을 박스 안쪽 우측 상단으로 배치 */
    .view-button {
        position: absolute;
        top: 20px;
        right: 20px;
        background-color: #0366d6;
        color: white !important;
        padding: 6px 14px;
        border-radius: 6px;
        text-decoration: none;
        font-size: 0.8rem;
        font-weight: 600;
        transition: background-color 0.2s;
    }
    .view-button:hover {
        background-color: #0056b3;
    }
    </style>
    """, unsafe_allow_html=True)

# 1. 인덱싱 함수
@st.cache_resource
def load_indexed_pdfs(file_list):
    all_indexed_data = []
    for file_name in file_list:
        file_path = f"static/{file_name}"
        if not os.path.exists(file_path):
            continue
        doc = fitz.open(file_path)
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            text = page.get_text("text")
            cleaned_text = re.sub(r'\n+', ' ', text)
            sentences = re.split(r'(?<=[.!?])\s+', cleaned_text)
            all_indexed_data.append({
                "file_name": file_name,
                "file_path": file_path,
                "page": page_num + 1,
                "sentences": sentences
            })
    return all_indexed_data

PDF_FILES = ["search1.pdf", "search2.pdf"] 

with st.spinner("PDF 분석 중..."):
    pdf_index = load_indexed_pdfs(PDF_FILES)

st.title("🔍 PDF 통합 검색 시스템")

col1, col2 = st.columns([0.8, 0.2])
with col1:
    keyword = st.text_input("검색어 입력", placeholder="검색어를 입력하고 엔터를 누르세요")
with col2:
    st.write(" ")
    stop_triggered = st.button("🛑 검색 중지", use_container_width=True)

if stop_triggered:
    st.warning("검색이 중단되었습니다.")
    st.stop()

if keyword:
    found_any = False
    seen_contexts = set()
    
    for data in pdf_index:
        file_name = data["file_name"]
        file_path = data["file_path"]
        page_num = data["page"]
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
                    
                    # 브라우저 보안 우회를 위해 파일을 직접 Base64로 인코딩하여 전송
                    with open(file_path, "rb") as f:
                        base64_pdf = base64.b64encode(f.read()).decode('utf-8')
                    view_url = f"data:application/pdf;base64,{base64_pdf}#page={page_num}"

                    st.markdown(f"""
                        <div class="result-box">
                            <a href="{view_url}" target="_blank" class="view-button">📄 해당 페이지 보기</a>
                            <div class="page-label">FILE: {file_name} | PAGE: {page_num}</div>
                            <div class="content-text">{highlighted_text}</div>
                        </div>
                    """, unsafe_allow_html=True)

    if not found_any:
        st.warning(f"'{keyword}'에 대한 결과가 없습니다.")
