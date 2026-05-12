import streamlit as st
import fitz
import re
import os

# 페이지 설정
st.set_page_config(page_title="PDF 통합 검색 시스템", layout="wide")

# --- 사용자께서 좋아하셨던 깔끔한 디자인 ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Pretendard:wght@400;600&display=swap');
    html, body, [class*="st-"] { font-family: 'Pretendard', sans-serif; }
    
    .result-box { 
        background-color: #ffffff; 
        border: 1px solid #e1e4e8; 
        border-radius: 12px; 
        padding: 20px; 
        margin-bottom: 20px; 
        box-shadow: 0 2px 8px rgba(0,0,0,0.05); 
    }
    .header-container { 
        display: flex; 
        justify-content: space-between; 
        align-items: center; 
        margin-bottom: 12px; 
        border-bottom: 1px solid #f0f2f5; 
        padding-bottom: 10px; 
    }
    .page-label { 
        font-size: 0.9rem; 
        color: #444; 
        font-weight: 700; 
    }
    .view-button { 
        background-color: #f0f7ff; 
        color: #0056b3 !important; 
        padding: 5px 15px; 
        border-radius: 6px; 
        text-decoration: none; 
        font-size: 0.85rem; 
        font-weight: 600; 
        border: 1px solid #cce3ff; 
        transition: 0.2s; 
    }
    .view-button:hover { 
        background-color: #0056b3; 
        color: white !important; 
    }
    .highlight { 
        background-color: #fff5b1; 
        color: #d73a49; 
        font-weight: bold; 
        padding: 0 2px; 
    }
    </style>
    """, unsafe_allow_html=True)

# 1. 인덱싱 함수 (static 폴더 안의 파일을 읽도록 경로 설정)
@st.cache_resource
def load_local_pdfs(file_list):
    all_indexed_data = []
    for file_name in file_list:
        file_path = f"static/{file_name}"  # static 폴더 내 파일 경로
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
                "page": page_num + 1,
                "sentences": sentences
            })
    return all_indexed_data

# --- 사용자 설정 정보 반영 ---
GITHUB_USER = "sjoh6136"
GITHUB_REPO = "jinijin_search"
PDF_FILES = ["search1.pdf", "search2.pdf"] 

with st.spinner("PDF 데이터를 분석하고 있습니다..."):
    pdf_index = load_local_pdfs(PDF_FILES)

st.title("📂 PDF 통합 검색 시스템")

# 검색창 레이아웃
col1, col2 = st.columns([0.8, 0.2])
with col1:
    keyword = st.text_input("검색어 입력", placeholder="찾으시는 단어를 입력하세요")
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
                    
                    # 깃허브에서 웹으로 바로 보기 위한 URL (blob 경로 사용)
                    # 이 링크는 깃허브 공식 뷰어를 통해 열립니다.
                    view_url = f"https://github.com/{GITHUB_USER}/{GITHUB_REPO}/blob/main/static/{file_name}#page={page_num}"

                    st.markdown(f"""
                        <div class="result-box">
                            <div class="header-container">
                                <span class="page-label">📄 {file_name} | PAGE: {page_num}</span>
                                <a href="{view_url}" target="_blank" class="view-button">해당 페이지 보기</a>
                            </div>
                            <div style="line-height:1.8; color:#333;">{highlighted_text}</div>
                        </div>
                    """, unsafe_allow_html=True)

    if not found_any:
        st.warning(f"'{keyword}'에 대한 검색 결과가 없습니다.")
