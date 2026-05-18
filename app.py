import streamlit as st
from docx import Document
from docx.shared import Pt
from io import BytesIO
import time
from google import genai
from google.genai import types

# 1. 페이지 기본 설정 및 디자인
st.set_page_config(
    page_title="Image To Text in English",
    page_icon="📝",
    layout="centered"
)

# 세련되고 직관적인 커스텀 CSS
st.markdown("""
    <style>
    /* 배경색: 차분하고 포근한 톤 */
    .stApp {
        background-color: #FDFBF6;
    }
    
    /* 메인 타이틀: 한 줄 배치 및 폰트 크기 최적화 */
    .main-title {
        font-size: 42px !important; 
        font-weight: 800;
        color: #5C715E; /* 뮤티드 그린 */
        text-align: center;
        margin-bottom: 10px;
        letter-spacing: -1.5px;
        white-space: nowrap; /* 한 줄 유지 */
    }
    
    /* 서브 타이틀: 기능 중심의 명확한 설명 */
    .sub-title {
        font-size: 18px;
        color: #7A7A7A;
        text-align: center;
        margin-bottom: 45px;
        font-weight: 400;
        letter-spacing: -0.5px;
    }
    
    /* 업로드 섹션 디자인 */
    .stFileUploader {
        border-radius: 15px !important;
        background-color: white;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        padding: 10px;
    }
    
    /* 버튼 스타일 */
    div.stButton > button:first-child {
        background-color: #94A69A;
        color: white;
        border-radius: 10px;
        border: none;
        padding: 12px 40px;
        font-weight: 600;
        font-size: 16px;
        width: 100%; /* 버튼을 가로로 꽉 차게 변경하여 시원한 느낌 */
        transition: all 0.3s ease;
    }
    div.stButton > button:first-child:hover {
        background-color: #7E8F83;
    }
    
    /* 결과 박스 */
    .status-box {
        padding: 25px;
        border-radius: 20px;
        background-color: white;
        margin-top: 30px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        text-align: center;
    }
    </style>
""", unsafe_allow_html=True)

# 텍스트 섹션 (요청하신 대로 한 줄 배치 및 문구 수정)
st.markdown('<p class="main-title">Image To Text in English</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">사진 속 지문을 인식하여 편집 가능한 워드 문서(.docx)로 변환합니다.</p>', unsafe_allow_html=True)

# 2. API Key 자동 로드
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    client = genai.Client(api_key=api_key)
    
    # 3. 파일 업로드 UI
    uploaded_files = st.file_uploader(
        "변환할 영어 지문 사진을 업로드하세요 (복수 선택 가능)", 
        type=["jpg", "jpeg", "png"],
        accept_multiple_files=True
    )

    if uploaded_files:
        st.write(f"📂 **{len(uploaded_files)}개**의 파일이 선택되었습니다.")
        
        if st.button("Word 파일로 변환하기 ✨"):
            
            doc = Document()
            # 기본 폰트 설정
            style = doc.styles['Normal']
            style.font.name = 'Arial'
            style.font.size = Pt(11)
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            total_files = len(uploaded_files)
            base_percent = 0
            
            for idx, file in enumerate(uploaded_files):
                image_bytes = file.read()
                
                try:
                    # AI에게 편집 가능한 고퀄리티 결과물 요청
                    prompt = """
                    이 사진 속의 영어 지문 텍스트를 정확하게 추출해줘. 
                    - 지문의 제목은 반드시 '진하게(Bold)' 처리하고 텍스트 크기를 키워줘.
                    - 본문의 문맥을 분석하여 문단(Paragraph) 구분을 가독성 있게 해줘.
                    - 강조된 단어나 핵심 문구는 '진하게(Bold)' 유지해줘.
                    - 결과물은 오직 추출된 텍스트만 보여주고, 다른 설명은 하지 마.
                    """
                    
                    response = client.models.generate_content(
                        model='gemini-2.0-flash',
                        contents=[
                            types.Part.from_bytes(data=image_bytes, mime_type=file.type),
                            prompt
                        ]
                    )
                    extracted_text = response.text
                    
                    # 부드러운 프로그레스 바 연출 (파일당 약 1초 내외)
                    target_percent = int(((idx + 1) / total_files) * 100)
                    for step in range(15):
                        curr = base_percent + int((target_percent - base_percent) * (step / 15))
                        progress_bar.progress(curr)
                        time.sleep(0.04)
                    
                    base_percent = target_percent
                    progress_bar.progress(base_percent)
                    status_text.text(f"✅ {file.name} 분석 완료")
                    
                    # 워드 문서 작성
                    doc.add_heading(f"Source: {file.name}", level=2)
                    
                    paragraphs = extracted_text.split('\n')
                    for para_text in paragraphs:
                        if para_text.strip():
                            p = doc.add_paragraph()
                            # 마크다운 볼드(**) 처리
                            parts = para_text.split('**')
                            for i, part in enumerate(parts):
                                run = p.add_run(part)
                                if i % 2 == 1:
                                    run.bold = True
                                    run.font.size = Pt(12)
                    
                    doc.add_page_break()
                    
                except Exception as e:
                    st.error(f"❌ '{file.name}' 처리 오류: {str(e)}")
            
            progress_bar.progress(100)
            status_text.text("모든 파일 변환이 완료되었습니다.")
            
            # 다운로드 버튼
            docx_buffer = BytesIO()
            doc.save(docx_buffer)
            docx_buffer.seek(0)
            
            st.markdown('<div class="status-box">', unsafe_allow_html=True)
            st.download_button(
                label="📥 변환된 Word 파일 다운로드",
                data=docx_buffer,
                file_name="Converted_English_Texts.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )
            st.markdown('</div>', unsafe_allow_html=True)

except KeyError:
    st.error("🔒 설정 오류: Streamlit Secrets에 API Key를 등록해 주세요.")
