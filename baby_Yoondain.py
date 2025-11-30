import json
import random
from datetime import datetime

class GirlfriendQuiz:
    def __init__(self):
        self.data_file = 'girlfriend_data.json'
        self.load_data()
    
    def load_data(self):
        """저장된 데이터 불러오기"""
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                self.data = json.load(f)
        except FileNotFoundError:
            self.data = {
                '기본정보': {},
                '좋아하는것': {},
                '싫어하는것': {},
                '기념일': {},
                '기타': {}
            }
    
    def save_data(self):
        """데이터 저장하기"""
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)
        print("✅ 저장되었습니다!")
    
    def add_info(self):
        """정보 추가하기"""
        print("\n📝 정보 추가하기")
        print("카테고리: 1)기본정보 2)좋아하는것 3)싫어하는것 4)기념일 5)기타")
        choice = input("선택 (1-5): ")
        
        categories = ['기본정보', '좋아하는것', '싫어하는것', '기념일', '기타']
        if choice.isdigit() and 1 <= int(choice) <= 5:
            category = categories[int(choice)-1]
            key = input("항목 (예: 생일, 좋아하는 음식): ")
            value = input("값: ")
            self.data[category][key] = value
            self.save_data()
        else:
            print("❌ 잘못된 선택입니다.")
    
    def view_all(self):
        """모든 정보 보기"""
        print("\n💕 저장된 정보")
        print("=" * 50)
        for category, items in self.data.items():
            if items:
                print(f"\n[{category}]")
                for key, value in items.items():
                    print(f"  • {key}: {value}")
        print("=" * 50)
    
    def play_quiz(self):
        """퀴즈 게임 시작"""
        # 모든 항목 수집
        all_questions = []
        for category, items in self.data.items():
            for key, value in items.items():
                all_questions.append((category, key, value))
        
        if len(all_questions) < 3:
            print("\n❌ 퀴즈를 하려면 최소 3개 이상의 정보가 필요해요!")
            return
        
        print("\n🎮 퀴즈 게임 시작!")
        print("=" * 50)
        
        # 랜덤으로 5개 문제 선택 (또는 전체 문제 수가 5개 미만이면 전체)
        num_questions = min(5, len(all_questions))
        questions = random.sample(all_questions, num_questions)
        
        score = 0
        for i, (category, key, answer) in enumerate(questions, 1):
            print(f"\n문제 {i}/{num_questions}")
            print(f"[{category}] {key}은(는)?")
            user_answer = input("답: ").strip()
            
            if user_answer.lower() == answer.lower():
                print("✅ 정답! 완벽해요!")
                score += 1
            else:
                print(f"❌ 땡! 정답은 '{answer}'입니다.")
        
        print("\n" + "=" * 50)
        print(f"🎯 최종 점수: {score}/{num_questions} ({score/num_questions*100:.1f}%)")
        
        if score == num_questions:
            print("💯 완벽해요! 최고의 남자친구!")
        elif score >= num_questions * 0.7:
            print("👍 잘하고 있어요!")
        else:
            print("📚 조금만 더 노력하면 될 거예요!")
        print("=" * 50)
    
    def edit_info(self):
        """정보 수정하기"""
        # 모든 항목을 리스트로 만들기
        all_items = []
        for category, items in self.data.items():
            for key, value in items.items():
                all_items.append((category, key, value))
        
        if not all_items:
            print("\n❌ 수정할 정보가 없습니다.")
            return
        
        print("\n✏️ 정보 수정하기")
        print("=" * 50)
        
        # 번호와 함께 목록 표시
        for i, (category, key, value) in enumerate(all_items, 1):
            print(f"{i}. [{category}] {key}: {value}")
        
        print("=" * 50)
        choice = input("\n수정할 항목 번호 (취소: 0): ")
        
        if choice == '0':
            print("취소되었습니다.")
            return
        
        if choice.isdigit() and 1 <= int(choice) <= len(all_items):
            category, old_key, old_value = all_items[int(choice)-1]
            
            print(f"\n현재 항목: {old_key}")
            print(f"현재 값: {old_value}")
            print("\n수정할 내용을 선택하세요:")
            print("1. 항목만 수정")
            print("2. 값만 수정")
            print("3. 둘 다 수정")
            
            edit_choice = input("선택 (1-3, 취소: 0): ")
            
            if edit_choice == '0':
                print("취소되었습니다.")
                return
            
            new_key = old_key
            new_value = old_value
            
            if edit_choice in ['1', '3']:
                new_key = input(f"새로운 항목 (현재: {old_key}, 유지하려면 Enter): ").strip()
                if not new_key:
                    new_key = old_key
            
            if edit_choice in ['2', '3']:
                new_value = input(f"새로운 값 (현재: {old_value}, 유지하려면 Enter): ").strip()
                if not new_value:
                    new_value = old_value
            
            if edit_choice in ['1', '2', '3']:
                # 기존 항목 삭제
                del self.data[category][old_key]
                # 새 항목 추가
                self.data[category][new_key] = new_value
                self.save_data()
                
                if old_key != new_key and old_value != new_value:
                    print(f"✅ '{old_key}: {old_value}' → '{new_key}: {new_value}'로 수정되었습니다!")
                elif old_key != new_key:
                    print(f"✅ 항목이 '{old_key}' → '{new_key}'로 수정되었습니다!")
                elif old_value != new_value:
                    print(f"✅ 값이 '{old_value}' → '{new_value}'로 수정되었습니다!")
                else:
                    print("변경사항이 없습니다.")
            else:
                print("❌ 잘못된 선택입니다.")
        else:
            print("❌ 잘못된 선택입니다.")

    
    def delete_info(self):
        """정보 삭제하기"""
        # 모든 항목을 리스트로 만들기
        all_items = []
        for category, items in self.data.items():
            for key, value in items.items():
                all_items.append((category, key, value))
        
        if not all_items:
            print("\n❌ 삭제할 정보가 없습니다.")
            return
        
        print("\n🗑️ 정보 삭제하기")
        print("=" * 50)
        
        # 번호와 함께 목록 표시
        for i, (category, key, value) in enumerate(all_items, 1):
            print(f"{i}. [{category}] {key}: {value}")
        
        print("=" * 50)
        choice = input("\n삭제할 항목 번호 (취소: 0): ")
        
        if choice == '0':
            print("취소되었습니다.")
            return
        
        if choice.isdigit() and 1 <= int(choice) <= len(all_items):
            category, key, value = all_items[int(choice)-1]
            confirm = input(f"정말 '{key}: {value}'를 삭제하시겠습니까? (y/n): ")
            
            if confirm.lower() == 'y':
                del self.data[category][key]
                self.save_data()
                print("✅ 삭제되었습니다!")
            else:
                print("취소되었습니다.")
        else:
            print("❌ 잘못된 선택입니다.")
    
    def run(self):
        """메인 메뉴"""
        while True:
            print("\n" + "💝" * 25)
            print("     여자친구 정보 퀴즈 게임")
            print("💝" * 25)
            print("\n1. 정보 추가하기")
            print("2. 모든 정보 보기")
            print("3. 퀴즈 게임 하기")
            print("4. 정보 수정하기")
            print("5. 정보 삭제하기")
            print("6. 종료")
            
            choice = input("\n선택 (1-6): ")
            
            if choice == '1':
                self.add_info()
            elif choice == '2':
                self.view_all()
            elif choice == '3':
                self.play_quiz()
            elif choice == '4':
                self.edit_info()
            elif choice == '5':
                self.delete_info()
            elif choice == '6':
                print("\n👋 좋은 연애 하세요!")
                break
            else:
                print("❌ 잘못된 선택입니다.")

if __name__ == "__main__":
    game = GirlfriendQuiz()
    game.run()