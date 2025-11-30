import streamlit as st
import json
import random
from pathlib import Path

# 페이지 설정
st.set_page_config(
    page_title="💕다인공주 공식 팬클럽 퀴즈게임",
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
            loaded_data = json.load(f)
            # 기존 데이터 형식 변환 (값만 있는 경우 -> 값+선택지 형식으로)
            st.session_state.data = {}
            for category, items in loaded_data.items():
                st.session_state.data[category] = {}
                for key, value in items.items():
                    if isinstance(value, dict) and 'answer' in value:
                        # 새 형식 (이미 선택지 있음)
                        st.session_state.data[category][key] = value
                    else:
                        # 기존 형식 (값만 있음) -> 새 형식으로 변환
                        st.session_state.data[category][key] = {
                            'answer': value,
                            'choices': []
                        }
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
if 'quiz_choices' not in st.session_state:
    st.session_state.quiz_choices = []
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
            if isinstance(value, dict):
                answer = value.get('answer', '')
                choices = value.get('choices', [])
            else:
                answer = value
                choices = []
            items.append((category, key, answer, choices))
    return items

def start_quiz():
    """퀴즈 시작"""
    all_items = get_all_items()
    if len(all_items) < 3:
        st.error("❌ 퀴즈를 하려면 최소 3개 이상의 정보가 필요해요!")
        return
    
    num_questions = min(5, len(all_items))
    st.session_state.quiz_questions = random.sample(all_items, num_questions)
    
    # 모든 문제의 선택지를 미리 생성
    st.session_state.quiz_choices = []
    for category, key, answer, custom_choices in st.session_state.quiz_questions:
        # 사용자 지정 선택지가 있으면 사용, 없으면 자동 생성
        if custom_choices and len(custom_choices) >= 3:
            choices = generate_choices_from_custom(answer, custom_choices)
        else:
            all_answers = [item[2] for item in all_items if item[0] == category]
            choices = generate_choices(answer, all_answers)
        st.session_state.quiz_choices.append(choices)
    
    st.session_state.quiz_index = 0
    st.session_state.quiz_score = 0
    st.session_state.quiz_answers = []
    st.session_state.quiz_mode = True

def generate_choices_from_custom(correct_answer, custom_choices):
    """사용자 지정 선택지로 4지선다 생성"""
    # 랜덤으로 3개 선택
    wrong_choices = random.sample(custom_choices, min(3, len(custom_choices)))
    
    # 정답 추가
    choices = [correct_answer] + wrong_choices
    
    # 부족하면 더미 추가
    while len(choices) < 4:
        dummy_options = ["모르겠어요", "기억 안나요", "힌트 주세요"]
        for dummy in dummy_options:
            if dummy not in choices:
                choices.append(dummy)
                break
    
    # 섞기
    random.shuffle(choices)
    return choices

def generate_choices(correct_answer, all_answers):
    """4지선다 보기 생성"""
    # 정답을 제외한 다른 답들
    other_answers = [ans for ans in all_answers if ans != correct_answer]
    
    # 랜덤으로 3개 선택 (답이 4개 미만이면 가능한만큼)
    num_choices = min(3, len(other_answers))
    wrong_choices = random.sample(other_answers, num_choices)
    
    # 정답과 오답 합치기
    choices = [correct_answer] + wrong_choices
    
    # 부족한 보기는 "잘 모르겠어요" 같은 더미 추가
    while len(choices) < 4:
        dummy_options = ["모르겠어요", "기억 안나요", "힌트 주세요", "다시 볼게요"]
        for dummy in dummy_options:
            if dummy not in choices:
                choices.append(dummy)
                break
    
    # 섞기
    random.shuffle(choices)
    return choices

def submit_answer(user_answer, correct_answer):
    """정답 제출"""
    is_correct = user_answer == correct_answer
    st.session_state.quiz_answers.append({
        'user': user_answer,
        'correct': correct_answer,
        'is_correct': is_correct
    })
    if is_correct:
        st.session_state.quiz_score += 1
    st.session_state.quiz_index += 1

def check_admin():
    """팬클럽 회장 권한 확인"""
    return st.session_state.is_admin

# 헤더
st.title("💕다인공주 공식 팬클럽 퀴즈게임")
st.markdown("---")

# 관리자 로그인/로그아웃
with st.sidebar:
    if not st.session_state.is_admin:
        st.header("🔐 팬클럽 회장 로그인")
        with st.form("admin_login"):
            password = st.text_input("비밀번호", type="password")
            login_button = st.form_submit_button("로그인")
            
            if login_button:
                if password == ADMIN_PASSWORD:
                    st.session_state.is_admin = True
                    st.rerun()
                else:
                    st.error("❌ 삐-빅 당신은 호위무사에게 제압되었습니다.")
    else:
        st.success("✅ 팬클럽 회장 모드")
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
        st.info("💡 사생팬은 모든 기능을 사용할 수 있어요!")
    else:
        st.info("💡 퀴즈를 풀어보세요! 정보 관리는 팬클럽 회장만 가능해요.")

# 퀴즈 모드
if st.session_state.quiz_mode:
    if st.session_state.quiz_index < len(st.session_state.quiz_questions):
        # 현재 문제
        category, key, answer, custom_choices = st.session_state.quiz_questions[st.session_state.quiz_index]
        
        # 미리 생성된 선택지 사용
        choices = st.session_state.quiz_choices[st.session_state.quiz_index]
        
        st.subheader(f"🎯 문제 {st.session_state.quiz_index + 1}/{len(st.session_state.quiz_questions)}")
        st.info(f"**[{category}]** {key}은(는)?")
        
        # 객관식 선택
        user_answer = st.radio(
            "답을 선택하세요:",
            choices,
            key=f"answer_{st.session_state.quiz_index}",
            label_visibility="collapsed"
        )
        
        col1, col2 = st.columns([3, 1])
        with col1:
            if st.button("제출", use_container_width=True, key=f"submit_{st.session_state.quiz_index}"):
                submit_answer(user_answer, answer)
                st.rerun()
        with col2:
            if st.button("❌ 나가기", use_container_width=True, key="exit_quiz"):
                st.session_state.quiz_mode = False
                st.rerun()
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
            st.success("💯 완벽해요! 최고의 사생팬!")
        elif percentage >= 70:
            st.success("겨우 이딴게 남자친구?!")
        else:
            st.info("📚 넌 일단 좀 맞고 시작하자")
        
        # 문제별 결과
        st.markdown("### 📊 상세 결과")
        for i, qa in enumerate(st.session_state.quiz_answers, 1):
            category, key, _ = st.session_state.quiz_questions[i-1]
            if qa['is_correct']:
                st.success(f"✅ 문제 {i}: [{category}] {key} - 정답!")
            else:
                st.error(f"❌ 문제 {i}: [{category}] {key}")
                st.write(f"   내 답: {qa['user']} → 정답: {qa['correct']}")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 다시 하기", use_container_width=True):
                st.session_state.quiz_mode = False
                st.rerun()
        with col2:
            if st.button("🏠 홈으로", use_container_width=True):
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
        1. **정보 추가**: 다인공주에 대한 정보를 입력하세요
        2. **정보 보기**: 저장된 모든 정보를 확인하세요
        3. **퀴즈 게임**: 얼마나 기억하고 있는지 테스트하세요!
        
        왼쪽 사이드바에서 메뉴를 선택해주세요 😊
        """)
    else:
        st.markdown("""
        ### 🎮 퀴즈 게임
        저장된 정보를 바탕으로 퀴즈를 풀어보세요!
        
        얼마나 잘 기억하고 있는지 테스트할 수 있어요 😊
        
        **정보 추가/수정/삭제는 팬클럽 회장만 가능합니다.**
        """)

elif menu == "➕ 정보 추가":
    if not check_admin():
        st.warning("⚠️ 팬클럽 회장만 접근 가능합니다!")
    else:
        st.header("➕ 정보 추가하기")
        
        with st.form("add_form"):
            category = st.selectbox(
                "카테고리 선택",
                ["기본정보", "좋아하는것", "싫어하는것", "기념일", "기타"]
            )
            key = st.text_input("항목 (예: 생일, 좋아하는 음식)")
            value = st.text_input("정답")
            
            st.markdown("**오답 선택지 (선택사항)**")
            st.caption("퀴즈에서 사용할 오답 3개를 입력하세요. 비워두면 자동으로 생성됩니다.")
            choice1 = st.text_input("오답 1")
            choice2 = st.text_input("오답 2")
            choice3 = st.text_input("오답 3")
            
            submitted = st.form_submit_button("추가하기", use_container_width=True)
            
            if submitted:
                if key and value:
                    # 선택지 수집
                    custom_choices = [c for c in [choice1, choice2, choice3] if c.strip()]
                    
                    st.session_state.data[category][key] = {
                        'answer': value,
                        'choices': custom_choices
                    }
                    save_data()
                    st.success(f"✅ [{category}] {key}: {value} 추가되었습니다!")
                    if custom_choices:
                        st.info(f"오답 선택지 {len(custom_choices)}개 추가됨")
                    st.rerun()
                else:
                    st.warning("항목과 정답을 입력해주세요!")

elif menu == "📝 정보 보기":
    if not check_admin():
        st.warning("⚠️ 팬클럽 회장만 접근 가능합니다!")
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
                        if isinstance(value, dict):
                            answer = value.get('answer', '')
                            choices = value.get('choices', [])
                            st.write(f"• **{key}**: {answer}")
                            if choices:
                                st.caption(f"   └ 오답 선택지: {', '.join(choices)}")
                        else:
                            st.write(f"• **{key}**: {value}")
                    st.markdown("---")

elif menu == "✏️ 정보 수정":
    if not check_admin():
        st.warning("⚠️ 팬클럽 회장만 접근 가능합니다!")
    else:
        st.header("✏️ 정보 수정하기")
        
        all_items = get_all_items()
        
        if not all_items:
            st.info("수정할 정보가 없습니다.")
        else:
            # 항목 선택
            item_options = [f"[{cat}] {key}: {answer}" for cat, key, answer, choices in all_items]
            selected_index = st.selectbox("수정할 항목 선택", range(len(item_options)), format_func=lambda x: item_options[x])
            
            if selected_index is not None:
                category, old_key, old_answer, old_choices = all_items[selected_index]
                
                st.info(f"현재: [{category}] {old_key}: {old_answer}")
                if old_choices:
                    st.caption(f"오답 선택지: {', '.join(old_choices)}")
                
                with st.form("edit_form"):
                    new_key = st.text_input("항목", value=old_key)
                    new_answer = st.text_input("정답", value=old_answer)
                    
                    st.markdown("**오답 선택지**")
                    choice1 = st.text_input("오답 1", value=old_choices[0] if len(old_choices) > 0 else "")
                    choice2 = st.text_input("오답 2", value=old_choices[1] if len(old_choices) > 1 else "")
                    choice3 = st.text_input("오답 3", value=old_choices[2] if len(old_choices) > 2 else "")
                    
                    submitted = st.form_submit_button("수정하기", use_container_width=True)
                    
                    if submitted:
                        # 선택지 수집
                        new_choices = [c for c in [choice1, choice2, choice3] if c.strip()]
                        
                        del st.session_state.data[category][old_key]
                        st.session_state.data[category][new_key] = {
                            'answer': new_answer,
                            'choices': new_choices
                        }
                        save_data()
                        st.success(f"✅ 수정되었습니다!")
                        st.rerun()

elif menu == "🗑️ 정보 삭제":
    if not check_admin():
        st.warning("⚠️ 팬클럽 회장만 접근 가능합니다!")
    else:
        st.header("🗑️ 정보 삭제하기")
        
        all_items = get_all_items()
        
        if not all_items:
            st.info("삭제할 정보가 없습니다.")
        else:
            item_options = [f"[{cat}] {key}: {answer}" for cat, key, answer, choices in all_items]
            selected_index = st.selectbox("삭제할 항목 선택", range(len(item_options)), format_func=lambda x: item_options[x])
            
            if selected_index is not None:
                category, key, answer, choices = all_items[selected_index]
                
                st.warning(f"정말 '{key}: {answer}'를 삭제하시겠습니까?")
                
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
            st.info("팬클럽 회장에게 정보를 추가해달라고 요청하세요!")
        else:
            st.info("먼저 정보를 추가해주세요!")
    else:
        st.info(f"총 {len(all_items)}개의 정보가 저장되어 있습니다.")
        st.write(f"랜덤으로 {min(10, len(all_items))}개의 문제가 출제됩니다.")
        
        if st.button("🎮 퀴즈 시작!", use_container_width=True):
            start_quiz()
            st.rerun()

# 푸터
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: gray; font-size: 0.8em;'>
    💕다인공주 팬클럽 퀴즈 게임 v2.0 (팬클럽 회장 모드)
    </div>
    """,
    unsafe_allow_html=True
)