import streamlit as st
import fitz
import base64
import re
import os

# ... 상단 CSS 디자인 부분은 그대로 유지 ...

# 1. 인덱싱 (GitHub 서버에 올라온 파일을 직접 읽기)
@st.cache_resource
def load_local_pdfs(file_list):
    all_indexed_data = []
    for file_name in file_list:
        # 파일이 실제로 존재하는지 확인
        if not os.path.exists(file_name):
            st.error(f"파일을 찾을 수 없습니다: {file_name}. 파일명이 정확한지 확인해 주세요.")
            continue
            
        doc = fitz.open(file_name) # 로컬 경로로 바로 열기
        
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

# --- 핵심 수정 부분 ---
# GitHub 레포지토리에 올린 실제 파일명과 '대소문자'까지 똑같이 적어주세요.
PDF_FILES = ["file1.pdf", "file2.pdf"] 

with st.spinner("PDF 분석 중..."):
    # 함수명을 load_local_pdfs로 변경하여 호출
    pdf_index = load_local_pdfs(PDF_FILES)

# --- 이하 검색 및 출력 로직 ---
# (이전 코드와 동일하되, '해당 페이지 보기' 링크 생성 부분만 아래처럼 수정)

# ... 중략 ...
                    # 로컬 파일을 브라우저로 띄우기 위한 base64 변환
                    with open(file_name, "rb") as f:
                        base64_pdf = base64.b64encode(f.read()).decode('utf-8')
                    view_url = f"data:application/pdf;base64,{base64_pdf}#page={page_num}"

                    st.markdown(f"""
                        <div class="result-box">
                            <div class="header-container">
                                <span class="page-label">📄 {file_name} | PAGE: {page_num}</span>
                                <a href="{view_url}" target="_blank" class="view-button">해당 페이지 보기</a>
                            </div>
                            <div style="line-height:1.8; color:#333;">{highlighted_text}</div>
                        </div>
                    """, unsafe_allow_html=True)
