import streamlit as st
import json
import random
from pathlib import Path

# 페이지 설정
st.set_page_config(
    page_title="💕 다인이의 모든 것을 알아보아요",
    page_icon="💕",
    layout="centered"
)

# 관리자 비밀번호 (여기서 변경하세요!)
ADMIN_PASSWORD = "1234"  # 원하는 비밀번호로 변경!

# 데이터 파일 경로
DATA_FILE = Path("girlfriend_data.json")

# 세션 상태 초기화
if 'data' not in st.session_state:
    if DATA_FILE.exists():
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            st.session_state.data = json.load(f)
    else:
        st.session_state.data = {
            '기본정보': {},
            '좋아하는것': {},
            '싫어하는것': {},
            '기념일': {},
            '기타': {}
        }

if 'quiz_mode' not in st.session_state:
    st.session_state.quiz_mode = False
if 'quiz_questions' not in st.session_state:
    st.session_state.quiz_questions = []
if 'quiz_index' not in st.session_state:
    st.session_state.quiz_index = 0
if 'quiz_score' not in st.session_state:
    st.session_state.quiz_score = 0
if 'quiz_answers' not in st.session_state:
    st.session_state.quiz_answers = []
if 'is_admin' not in st.session_state:
    st.session_state.is_admin = False

def save_data():
    """데이터 저장"""
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(st.session_state.data, f, ensure_ascii=False, indent=2)

def get_all_items():
    """모든 항목을 리스트로 반환"""
    items = []
    for category, data in st.session_state.data.items():
        for key, value in data.items():
            items.append((category, key, value))
    return items

def start_quiz():
    """퀴즈 시작"""
    all_items = get_all_items()
    if len(all_items) < 3:
        st.error("❌ 퀴즈를 하려면 최소 3개 이상의 정보가 필요해요!")
        return
    
    num_questions = min(5, len(all_items))
    st.session_state.quiz_questions = random.sample(all_items, num_questions)
    st.session_state.quiz_index = 0
    st.session_state.quiz_score = 0
    st.session_state.quiz_answers = []
    st.session_state.quiz_mode = True

def submit_answer(user_answer, correct_answer):
    """정답 제출"""
    is_correct = user_answer.strip().lower() == correct_answer.lower()
    st.session_state.quiz_answers.append({
        'user': user_answer,
        'correct': correct_answer,
        'is_correct': is_correct
    })
    if is_correct:
        st.session_state.quiz_score += 1
    st.session_state.quiz_index += 1

def check_admin():
    """관리자 권한 확인"""
    return st.session_state.is_admin

# 헤더
st.title("💕 다인이의 모든 것을 알아보아요")
st.markdown("---")

# 관리자 로그인/로그아웃
with st.sidebar:
    if not st.session_state.is_admin:
        st.header("🔐 관리자 로그인")
        with st.form("admin_login"):
            password = st.text_input("비밀번호", type="password")
            login_button = st.form_submit_button("로그인")
            
            if login_button:
                if password == ADMIN_PASSWORD:
                    st.session_state.is_admin = True
                    st.rerun()
                else:
                    st.error("❌ 비밀번호가 틀렸습니다!")
    else:
        st.success("✅ 관리자 모드")
        if st.button("🚪 로그아웃"):
            st.session_state.is_admin = False
            st.rerun()
    
    st.markdown("---")

# 사이드바 메뉴
with st.sidebar:
    st.header("📋 메뉴")
    
    # 관리자 여부에 따라 메뉴 다르게 표시
    if check_admin():
        menu = st.radio(
            "선택하세요",
            ["🏠 홈", "➕ 정보 추가", "📝 정보 보기", "✏️ 정보 수정", "🗑️ 정보 삭제", "🎮 퀴즈 게임"]
        )
    else:
        menu = st.radio(
            "선택하세요",
            ["🏠 홈", "🎮 퀴즈 게임"]
        )
    
    st.markdown("---")
    if check_admin():
        st.info("💡 관리자는 모든 기능을 사용할 수 있어요!")
    else:
        st.info("💡 퀴즈를 풀어보세요! 정보 관리는 관리자만 가능해요.")

# 퀴즈 모드
if st.session_state.quiz_mode:
    if st.session_state.quiz_index < len(st.session_state.quiz_questions):
        # 현재 문제
        category, key, answer = st.session_state.quiz_questions[st.session_state.quiz_index]
        
        st.subheader(f"🎯 문제 {st.session_state.quiz_index + 1}/{len(st.session_state.quiz_questions)}")
        st.info(f"**[{category}]** {key}은(는)?")
        
        with st.form(key=f"quiz_form_{st.session_state.quiz_index}"):
            user_answer = st.text_input("답:", key=f"answer_{st.session_state.quiz_index}")
            submitted = st.form_submit_button("제출")
            
            if submitted:
                if user_answer:
                    submit_answer(user_answer, answer)
                    st.rerun()
                else:
                    st.warning("답을 입력해주세요!")
    else:
        # 퀴즈 결과
        st.subheader("🎊 퀴즈 결과")
        
        total = len(st.session_state.quiz_questions)
        score = st.session_state.quiz_score
        percentage = (score / total * 100) if total > 0 else 0
        
        # 점수 표시
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("총 문제", total)
        with col2:
            st.metric("맞은 개수", score)
        with col3:
            st.metric("정답률", f"{percentage:.1f}%")
        
        # 결과 메시지
        if percentage == 100:
            st.success("💯 완벽해요! 최고의 남자친구!")
        elif percentage >= 70:
            st.success("👍 잘하고 있어요!")
        else:
            st.info("📚 조금만 더 노력하면 될 거예요!")
        
        # 문제별 결과
        st.markdown("### 📊 상세 결과")
        for i, qa in enumerate(st.session_state.quiz_answers, 1):
            category, key, _ = st.session_state.quiz_questions[i-1]
            if qa['is_correct']:
                st.success(f"✅ 문제 {i}: [{category}] {key} - 정답!")
            else:
                st.error(f"❌ 문제 {i}: [{category}] {key}")
                st.write(f"   내 답: {qa['user']} → 정답: {qa['correct']}")
        
        if st.button("🔄 다시 하기", use_container_width=True):
            st.session_state.quiz_mode = False
            st.rerun()

# 메뉴별 화면
elif menu == "🏠 홈":
    st.header("환영합니다! 👋")
    
    total_items = len(get_all_items())
    
    st.metric("📊 저장된 퀴즈", f"{total_items}개")
    
    st.markdown("---")
    if check_admin():
        st.markdown("""
        ### 🎯 사용 방법
        1. **정보 추가**: 여자친구에 대한 정보를 입력하세요
        2. **정보 보기**: 저장된 모든 정보를 확인하세요
        3. **퀴즈 게임**: 얼마나 기억하고 있는지 테스트하세요!
        
        왼쪽 사이드바에서 메뉴를 선택해주세요 😊
        """)
    else:
        st.markdown("""
        ### 🎮 퀴즈 게임
        저장된 정보를 바탕으로 퀴즈를 풀어보세요!
        
        얼마나 잘 기억하고 있는지 테스트할 수 있어요 😊
        
        **정보 추가/수정/삭제는 관리자만 가능합니다.**
        """)

elif menu == "➕ 정보 추가":
    if not check_admin():
        st.warning("⚠️ 관리자만 접근 가능합니다!")
    else:
        st.header("➕ 정보 추가하기")
        
        with st.form("add_form"):
            category = st.selectbox(
                "카테고리 선택",
                ["기본정보", "좋아하는것", "싫어하는것", "기념일", "기타"]
            )
            key = st.text_input("항목 (예: 생일, 좋아하는 음식)")
            value = st.text_input("값")
            
            submitted = st.form_submit_button("추가하기", use_container_width=True)
            
            if submitted:
                if key and value:
                    st.session_state.data[category][key] = value
                    save_data()
                    st.success(f"✅ [{category}] {key}: {value} 추가되었습니다!")
                    st.rerun()
                else:
                    st.warning("모든 항목을 입력해주세요!")

elif menu == "📝 정보 보기":
    if not check_admin():
        st.warning("⚠️ 관리자만 접근 가능합니다!")
    else:
        st.header("📝 저장된 정보")
        
        all_items = get_all_items()
        
        if not all_items:
            st.info("아직 저장된 정보가 없습니다. 정보를 추가해주세요!")
        else:
            for category in st.session_state.data.keys():
                if st.session_state.data[category]:
                    st.subheader(f"📁 {category}")
                    for key, value in st.session_state.data[category].items():
                        st.write(f"• **{key}**: {value}")
                    st.markdown("---")

elif menu == "✏️ 정보 수정":
    if not check_admin():
        st.warning("⚠️ 관리자만 접근 가능합니다!")
    else:
        st.header("✏️ 정보 수정하기")
        
        all_items = get_all_items()
        
        if not all_items:
            st.info("수정할 정보가 없습니다.")
        else:
            # 항목 선택
            item_options = [f"[{cat}] {key}: {val}" for cat, key, val in all_items]
            selected_index = st.selectbox("수정할 항목 선택", range(len(item_options)), format_func=lambda x: item_options[x])
            
            if selected_index is not None:
                category, old_key, old_value = all_items[selected_index]
                
                st.info(f"현재: [{category}] {old_key}: {old_value}")
                
                with st.form("edit_form"):
                    edit_type = st.radio("수정할 내용", ["값만 수정", "항목만 수정", "둘 다 수정"])
                    
                    new_key = old_key
                    new_value = old_value
                    
                    if edit_type in ["항목만 수정", "둘 다 수정"]:
                        new_key = st.text_input("새로운 항목", value=old_key)
                    
                    if edit_type in ["값만 수정", "둘 다 수정"]:
                        new_value = st.text_input("새로운 값", value=old_value)
                    
                    submitted = st.form_submit_button("수정하기", use_container_width=True)
                    
                    if submitted:
                        del st.session_state.data[category][old_key]
                        st.session_state.data[category][new_key] = new_value
                        save_data()
                        st.success(f"✅ 수정되었습니다!")
                        st.rerun()

elif menu == "🗑️ 정보 삭제":
    if not check_admin():
        st.warning("⚠️ 관리자만 접근 가능합니다!")
    else:
        st.header("🗑️ 정보 삭제하기")
        
        all_items = get_all_items()
        
        if not all_items:
            st.info("삭제할 정보가 없습니다.")
        else:
            item_options = [f"[{cat}] {key}: {val}" for cat, key, val in all_items]
            selected_index = st.selectbox("삭제할 항목 선택", range(len(item_options)), format_func=lambda x: item_options[x])
            
            if selected_index is not None:
                category, key, value = all_items[selected_index]
                
                st.warning(f"정말 '{key}: {value}'를 삭제하시겠습니까?")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("✅ 삭제", use_container_width=True):
                        del st.session_state.data[category][key]
                        save_data()
                        st.success("✅ 삭제되었습니다!")
                        st.rerun()
                with col2:
                    if st.button("❌ 취소", use_container_width=True):
                        st.info("취소되었습니다.")

elif menu == "🎮 퀴즈 게임":
    st.header("🎮 퀴즈 게임")
    
    all_items = get_all_items()
    
    if len(all_items) < 3:
        st.warning("❌ 퀴즈를 하려면 최소 3개 이상의 정보가 필요해요!")
        if not check_admin():
            st.info("관리자에게 정보를 추가해달라고 요청하세요!")
        else:
            st.info("먼저 정보를 추가해주세요!")
    else:
        st.info(f"총 {len(all_items)}개의 정보가 저장되어 있습니다.")
        st.write(f"랜덤으로 {min(5, len(all_items))}개의 문제가 출제됩니다.")
        
        if st.button("🎮 퀴즈 시작!", use_container_width=True):
            start_quiz()
            st.rerun()

# 푸터
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: gray; font-size: 0.8em;'>
    💕 여자친구 정보 퀴즈 게임 v2.0 (관리자 모드)
    </div>
    """,
    unsafe_allow_html=True
)