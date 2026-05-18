import streamlit as st
from docx import Document
from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from io import BytesIO
import time
from google import genai
from google.genai import types

# 1. 페이지 기본 설정 및 디자인 (감성 테마 적용)
st.set_page_config(
    page_title="Image To Text in English",
    page_icon="🎨",
    layout="centered"
)

# 30대 원장님 취향의 감성적이고 세련된 커스텀 CSS (완전 새단장)
st.markdown("""
    <style>
    /* 전체 배경색: 포근한 크림톤 */
    .stApp {
        background-color: #FDFBF6;
    }
    
    /* 메인 타이틀: 100% 확대, 뮤티드 그린 컬러 */
    .main-title {
        font-size: 56px !important; /* 원본 28px의 2배 */
        font-weight: 800;
        color: #5C715E; /* 차분한 그린 */
        margin-bottom: 0px;
        letter-spacing: -1px;
        line-height: 1.1;
    }
    
    /* 서브 타이틀: 감성 서체 적용 */
    .sub-title {
        font-size: 16px;
        color: #8C8C8C;
        margin-bottom: 40px;
        font-weight: 400;
    }
    
    /* 업로드 영역: 카페 메뉴판처럼 은은한 그림자와 둥근 모서리 */
    .stFileUploader {
        border-radius: 20px !important;
        background-color: white;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        padding: 20px;
    }
    
    /* 버튼 스타일: 뮤티드 민트 */
    div.stButton > button:first-child {
        background-color: #94A69A; /* 뮤티드 민트 */
        color: white;
        border-radius: 12px;
        border: none;
        padding: 12px 30px;
        font-weight: 600;
        font-size: 16px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
    }
    div.stButton > button:first-child:hover {
        background-color: #7E8F83;
        transform: translateY(-1px);
    }
    
    /* 결과 상자 및 다운로드 버튼 섹션 */
    .status-box {
        padding: 25px;
        border-radius: 20px;
        background-color: white;
        margin-top: 30px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        text-align: center;
    }
    .success-text {
        color: #5C715E;
        font-weight: 600;
        margin-bottom: 20px;
    }
    
    /* 부드러운 퍼센트 바 전용 스타일 */
    .progress-wrapper {
        margin-bottom: 10px;
        font-size: 14px;
        color: #6B7280;
        text-align: right;
    }
    </style>
""", unsafe_allow_html=True)

# UI 상단 타이틀 (100% 확대 및 문구 수정 반영)
st.markdown('<p class="main-title">Image To Text</p>', unsafe_allow_html=True)
st.markdown('<p class="main-title" style="margin-top:-10px;">in English</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">영어 지문 사진을 뮤티드 감성으로 세련된 Word 파일로 변환해 드립니다.</p>', unsafe_allow_html=True)

# 2. Streamlit Secrets에서 API 키를 자동으로 로드
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    client = genai.Client(api_key=api_key)
    
    # 3. 파일 업로드 UI (복수 선택 가능)
    uploaded_files = st.file_uploader(
        "교재 사진을 선택하세요 (복수 선택 가능)", 
        type=["jpg", "jpeg", "png"],
        accept_multiple_files=True
    )

    if uploaded_files:
        st.write(f"📂 총 **{len(uploaded_files)}개**의 지문이 준비되었습니다.")
        
        # 변환 시작 버튼
        if st.button("세련된 Word 파일로 변환 ✨"):
            
            # 워드 문서 객체 생성
            doc = Document()
            # 문서 전체 기본 글꼴 세팅 (가독성 좋은 글꼴 추천)
            style = doc.styles['Normal']
            font = style.font
            font.name = 'Arial'
            font.size = Pt(11)
            
            # 진행 상황 연출을 위한 컨테이너들
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            total_files = len(uploaded_files)
            # '부드러운 퍼센트' 연출을 위한 총 단계 (파일당 20프레임)
            visual_frames_per_file = 20
            total_visual_steps = total_files * visual_frames_per_file
            
            # 실제 파일 처리와 시각적 퍼센트 바 속도를 맞추기 위한 로직
            base_percent = 0
            
            # 각 이미지 순회하며 실제 파일 처리 (부하는 파일 처리 자체에 집중)
            for idx, file in enumerate(uploaded_files):
                # 실제 파일 분석 시작
                image_bytes = file.read()
                
                # Gemini 모델에게 '원본 느낌' 지시
                # (글씨체 조절, 진하게 설정, 문맥에 맞춘 줄바꿈 포함)
                try:
                    prompt = """
                    이 사진 속의 영어 지문 텍스트를 정확하게 추출해줘. 
                    - 최대한 원본 사진의 디자인 의도를 반영해서 결과물을 구성해줘.
                    - 지문의 제목이 있다면 글씨 크기를 키우고 '진하게(Bold)' 처리해줘.
                    - 본문 중 강조된 키워드나 소제목이 있다면 '진하게(Bold)' 처리해줘.
                    - 줄바꿈은 원본과 동일할 필요는 없지만, 문맥에 맞도록 가독성 있게 적절히 나눠줘.
                    - 영어 외의 불필요한 설명은 포함하지 마.
                    """
                    
                    response = client.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=[
                            types.Part.from_bytes(
                                data=image_bytes,
                                mime_type=file.type,
                            ),
                            prompt
                        ]
                    )
                    extracted_text = response.text
                    
                    # --- 부드러운 퍼센트 바 연출 시작 ---
                    # 파일 처리가 끝난 후, 다음 퍼센트까지 부드럽게 올라가는 연출을 합니다.
                    target_percent = int(((idx + 1) / total_files) * 100)
                    
                    for step in range(visual_frames_per_file):
                        # 끊김 없이 올라가는 듯한 퍼센트 계산
                        current_visual_percent = base_percent + int((target_percent - base_percent) * (step / visual_frames_per_file))
                        
                        # 화면 업데이트
                        progress_bar.progress(current_visual_percent)
                        # 부하를 고르게 나눠 끊김 없는 속도로 보이게 함 (약 0.05초 간격)
                        time.sleep(0.05) 
                        
                    # 최종 퍼센트 맞춤
                    base_percent = target_percent
                    progress_bar.progress(base_percent)
                    status_text.text(f"⏳ [{idx+1}/{total_files}] '{file.name}' 분석 완료!")
                    # --- 부드러운 퍼센트 바 연출 끝 ---
                    
                    # 워드 문서에 원본 느낌 살려 추가
                    # 소제목으로 파일명 추가
                    file_header = doc.add_heading(level=2)
                    run_header = file_header.add_run(f"Source: {file.name}")
                    run_header.font.size = Pt(14)
                    run_header.font.name = 'Arial'
                    
                    # AI가 제목과 볼드처리를 구별해서 준 텍스트를 처리
                    # (Gemini가 마크다운 볼드 **text** 형식으로 주는 것을 워드 볼드로 변환)
                    paragraphs = extracted_text.split('\n')
                    for para_text in paragraphs:
                        if not para_text.strip():
                            continue
                            
                        p = doc.add_paragraph()
                        
                        # **제목** 또는 **강조** 처리된 부분 구별
                        parts = para_text.split('**')
                        for i, part in enumerate(parts):
                            run = p.add_run(part)
                            if i % 2 == 1: # 짝수번째(마크다운 볼드 안쪽) 텍스트는 진하게
                                run.bold = True
                                run.font.size = Pt(12) # 강조된 부분은 살짝 크게
                            else:
                                run.font.size = Pt(11)
                                
                    doc.add_page_break()  # 다음 사진은 다음 페이지에
                    
                except Exception as e:
                    st.error(f"❌ '{file.name}' 처리 중 오류 발생: {str(e)}")
            
            # 최종 100% 도달 및 연출
            progress_bar.progress(100)
            status_text.text("🎉 모든 파일 변환 완료!")
            
            # 워드 파일을 메모리 상의 바이트 스트림으로 변환
            docx_buffer = BytesIO()
            doc.save(docx_buffer)
            docx_buffer.seek(0)
            
            # 4. 다운로드 UI 제공 (은은한 그림자 상자 적용)
            st.markdown('<div class="status-box">', unsafe_allow_html=True)
            st.markdown('<p class="success-text">🎉 Word 파일 작성이 완료되었습니다!</p>', unsafe_allow_html=True)
            st.download_button(
                label="📥 변환된 Word 파일 다운로드",
                data=docx_buffer,
                file_name="영어지문_모음.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )
            st.markdown('</div>', unsafe_allow_html=True)

except KeyError:
    # Secrets 설정을 누락했을 경우 (감성 안내문)
    st.markdown("""
        <div class="status-box" style="border: 2px solid #D1D5DB; color: #6B7280;">
        🔒 시스템 에러: Streamlit 클라우드 설정(Secrets)에 'GEMINI_API_KEY'가 등록되지 않았습니다. 관리자 페이지를 확인해 주세요.
        </div>
    """, unsafe_allow_html=True)
