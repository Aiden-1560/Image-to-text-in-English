import streamlit as st
import base64

# ... existing code ...

# 스타일을 위해 커스텀 CSS 사용
st.markdown("""
    <style>
    .reportview-container {
        background: #FDFBF6;
    }
    .main-title {
        font-size: 56px;
        font-weight: 800;
        color: #5C715E;
        margin-bottom: 0px;
    }
    .sub-title {
        font-size: 16px;
        color: #8C8C8C;
        margin-bottom: 40px;
    }
    .stFileUploader {
        border-radius: 20px;
        background-color: white;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        padding: 20px;
    }
    /* (Made by Manju) 문구를 위한 스타일 */
    .author-footer {
        position: absolute;
        bottom: -20px; /* 제목/설명 영역 아래에 위치 */
        right: 0px;
        font-size: 14px;
        color: #B2B2B2; /* 밝은 회색 */
        text-align: right;
    }
    /* 기존 버튼 스타일 */
    div.stButton > button:first-child {
        background-color: #94A69A;
        color: white;
        border-radius: 12px;
        border: none;
        padding: 12px 30px;
    }
    </style>
""", unsafe_allow_html=True)

# UI 상단 타이틀 및 설명
col1, col2 = st.columns([1, 10]) # 문구 배치를 위해 컬럼 사용
with col2:
    st.markdown('<p class="main-title">Image To Text</p>', unsafe_allow_html=True)
    st.markdown('<p class="main-title" style="margin-top:-10px;">in English</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-title">영어 지문 사진을 뮤티드 감성으로 세련된 Word 파일로 변환해 드립니다.</p>', unsafe_allow_html=True)
    
    # 💡 [문구 추가] 사용자 요청에 따라 (Made by Manju) 문구 배치
    st.markdown('<div class="author-footer">(Made by Manju)</div>', unsafe_allow_html=True)

# ... 파일 업로더 코드 ...
