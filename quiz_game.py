"""게임 전체(메뉴, 퀴즈 진행, 추가/목록/삭제, 점수, 저장)를 관리하는 QuizGame 클래스."""

import json
import os
import random
import shutil
from datetime import datetime

from default_quizzes import create_default_quizzes
from quiz import Quiz

LINE = "=" * 40
THIN_LINE = "-" * 40


class QuizGame:
    """퀴즈 게임 전체를 관리하는 클래스."""

    # (메뉴 이름, 실행할 메서드 이름) — 종료는 None
    MENU_ITEMS = [
        ("퀴즈 풀기", "play_quiz"),
        ("퀴즈 추가", "add_quiz"),
        ("퀴즈 목록", "list_quizzes"),
        ("점수 확인", "show_score"),
        ("퀴즈 삭제", "delete_quiz"),
        ("게임 기록 보기", "show_history"),
        ("종료", None),
    ]
    HINT_KEYS = ("h", "힌트")  # 풀이 중 힌트를 보는 입력
    HISTORY_SHOW_COUNT = 10    # 기록 보기에서 보여 줄 최근 기록 수

    def __init__(self, state_path):
        self.state_path = state_path  # pathlib.Path: state.json 위치
        self.quizzes = []             # list[Quiz]: 퀴즈 목록
        self.best_score = None        # int | None: 최고 점수 (0~100), 아직 안 풀었으면 None
        self.best_record = None       # dict | None: 최고 점수 기록의 정답 수/문제 수/힌트 수
        self.history = []             # list[dict]: 모든 게임 기록
        self.is_loaded = False        # 불러오기가 끝나기 전에는 저장하지 않기 위한 표시

    # ==================================================
    # 실행 흐름
    # ==================================================
    def run(self):
        """프로그램 시작: 데이터를 불러오고 메뉴 반복을 실행한다."""
        print(LINE)
        print("        🎯 나만의 퀴즈 게임 🎯")
        print("      (주제: Python & Git 기초)")
        print(LINE)
        self.load()

        while True:
            self.show_menu()
            choice = self.input_number("선택: ", 1, len(self.MENU_ITEMS))
            print()
            _, method_name = self.MENU_ITEMS[choice - 1]
            if method_name is None:
                self.exit_game()
                break
            action = getattr(self, method_name, None)
            if action is None:
                print("🚧 아직 준비 중인 기능입니다.")
                continue
            action()

    def show_menu(self):
        """메뉴를 출력한다."""
        print()
        print(LINE)
        for number, (name, _) in enumerate(self.MENU_ITEMS, start=1):
            print(f"{number}. {name}")
        print(LINE)

    def exit_game(self):
        """저장 후 종료 인사를 출력한다."""
        if self.save():
            print("💾 데이터를 저장했습니다.")
        print("👋 게임을 종료합니다. 다음에 또 만나요!")

    # ==================================================
    # 입력 처리 (공통 입력/예외 처리 기준)
    # ==================================================
    def input_text(self, prompt, allow_empty=False):
        """문자열을 입력받는다. 앞뒤 공백을 제거하고, 빈 입력이면 다시 받는다."""
        while True:
            text = input(prompt).strip()
            if text or allow_empty:
                return text
            print("⚠️ 빈 값은 입력할 수 없습니다. 다시 입력하세요.")

    def input_number(self, prompt, min_value, max_value):
        """min_value~max_value 범위의 정수를 입력받는다. 잘못된 입력이면 다시 받는다."""
        while True:
            text = input(prompt).strip()
            if not text:
                print(f"⚠️ 입력이 비어 있습니다. {min_value}-{max_value} 사이의 숫자를 입력하세요.")
                continue
            try:
                number = int(text)
            except ValueError:
                print(f"⚠️ 잘못된 입력입니다. {min_value}-{max_value} 사이의 숫자를 입력하세요.")
                continue
            if not min_value <= number <= max_value:
                print(f"⚠️ 잘못된 입력입니다. {min_value}-{max_value} 사이의 숫자를 입력하세요.")
                continue
            return number

    def input_yes_no(self, prompt):
        """y/n을 입력받아 True/False로 반환한다."""
        while True:
            text = input(prompt).strip().lower()
            if text in ("y", "yes", "예", "ㅇ"):
                return True
            if text in ("n", "no", "아니오", "ㄴ"):
                return False
            print("⚠️ y 또는 n을 입력하세요.")

    def input_answer(self, quiz):
        """문제의 정답 번호를 입력받는다. 'h'를 입력하면 힌트를 보여 준다.

        반환값: (입력한 번호, 힌트 사용 여부)
        """
        used_hint = False
        guide = "정답 입력 (1-4"
        guide += ", 힌트: h): " if quiz.has_hint() else "): "

        while True:
            text = input(guide).strip()
            if not text:
                print("⚠️ 입력이 비어 있습니다. 1-4 사이의 숫자를 입력하세요.")
                continue
            if text.lower() in self.HINT_KEYS:
                if not quiz.has_hint():
                    print("ℹ️ 이 문제는 힌트가 없습니다.")
                elif used_hint:
                    print(f"💡 힌트: {quiz.hint}")
                else:
                    used_hint = True
                    print(f"💡 힌트: {quiz.hint}  (이 문제는 맞혀도 점수가 절반만 인정됩니다)")
                continue
            try:
                number = int(text)
            except ValueError:
                print("⚠️ 잘못된 입력입니다. 1-4 사이의 숫자를 입력하세요.")
                continue
            if not 1 <= number <= Quiz.CHOICE_COUNT:
                print("⚠️ 잘못된 입력입니다. 1-4 사이의 숫자를 입력하세요.")
                continue
            return number, used_hint

    # ==================================================
    # 1. 퀴즈 풀기
    # ==================================================
    def play_quiz(self):
        """퀴즈를 출제하고 결과를 보여 준 뒤 최고 점수/기록을 갱신한다."""
        if not self.quizzes:
            print("📭 등록된 퀴즈가 없습니다. 먼저 '퀴즈 추가'로 퀴즈를 등록하세요.")
            return

        count = self.ask_question_count()
        selected = random.sample(self.quizzes, count)  # 랜덤 출제 (중복 없이 섞어서 뽑기)

        print()
        print(f"📝 퀴즈를 시작합니다! (총 {count}문제)")
        print("   힌트가 필요하면 h 를 입력하세요. (힌트 사용 시 해당 문제 점수 절반)")

        correct_count = 0
        hint_count = 0
        earned = 0.0  # 문제마다 받은 점수 비율의 합 (정답 1.0, 힌트 정답 0.5, 오답 0)

        for number, quiz in enumerate(selected, start=1):
            print()
            print(THIN_LINE)
            is_correct, used_hint = self.ask_one_question(quiz, number)
            if used_hint:
                hint_count += 1
            if is_correct:
                correct_count += 1
                earned += 0.5 if used_hint else 1.0

        score = self.calculate_score(earned, count)
        self.show_result(count, correct_count, hint_count, score)
        self.record_game(count, correct_count, hint_count, score)

    def ask_question_count(self):
        """몇 문제를 풀지 입력받는다."""
        total = len(self.quizzes)
        if total == 1:
            return 1
        return self.input_number(f"몇 문제를 풀까요? (1-{total}): ", 1, total)

    def ask_one_question(self, quiz, number):
        """문제 하나를 출제하고 (정답 여부, 힌트 사용 여부)를 반환한다."""
        quiz.display(number)
        user_answer, used_hint = self.input_answer(quiz)
        if quiz.is_correct(user_answer):
            if used_hint:
                print("✅ 정답입니다! (힌트 사용: 점수 절반)")
            else:
                print("✅ 정답입니다!")
            return True, used_hint
        print(f"❌ 오답입니다. 정답은 {quiz.answer}번 '{quiz.correct_choice_text()}' 입니다.")
        return False, used_hint

    def calculate_score(self, earned, count):
        """100점 만점 점수를 계산한다."""
        return round(earned / count * 100)

    def show_result(self, count, correct_count, hint_count, score):
        """퀴즈 결과를 출력한다."""
        print()
        print(LINE)
        print(f"🏆 결과: {count}문제 중 {correct_count}문제 정답! ({score}점)")
        if hint_count:
            print(f"💡 힌트 사용: {hint_count}회")
        if self.best_score is None or score > self.best_score:
            print("🎉 새로운 최고 점수입니다!")
        else:
            print(f"현재 최고 점수: {self.best_score}점")
        print(LINE)

    # ==================================================
    # 4. 점수 확인 / 6. 게임 기록
    # ==================================================
    def record_game(self, count, correct_count, hint_count, score):
        """게임 기록을 추가하고, 최고 점수와 비교해 갱신한 뒤 저장한다."""
        self.history.append(
            {
                "played_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "total": count,
                "correct": correct_count,
                "hints_used": hint_count,
                "score": score,
            }
        )
        if self.best_score is None or score > self.best_score:
            self.best_score = score
            self.best_record = {"total": count, "correct": correct_count, "hints_used": hint_count}
        self.save()

    def show_score(self):
        """최고 점수를 출력한다."""
        if self.best_score is None:
            print("📭 아직 퀴즈를 풀지 않았습니다. '퀴즈 풀기'로 도전해 보세요!")
            return
        message = f"🏆 최고 점수: {self.best_score}점"
        if self.best_record:
            message += f" ({self.best_record['total']}문제 중 {self.best_record['correct']}문제 정답"
            if self.best_record.get("hints_used"):
                message += f", 힌트 {self.best_record['hints_used']}회"
            message += ")"
        print(message)
        print(f"🎮 지금까지 플레이한 게임: {len(self.history)}회")

    def show_history(self):
        """최근 게임 기록을 출력한다."""
        if not self.history:
            print("📭 아직 게임 기록이 없습니다.")
            return
        recent = self.history[-self.HISTORY_SHOW_COUNT:]
        print(f"📜 게임 기록 (전체 {len(self.history)}회 중 최근 {len(recent)}회)")
        print(THIN_LINE)
        for record in reversed(recent):
            print(
                f"{record['played_at']} | {record['total']}문제 중 {record['correct']}개 정답"
                f" | 힌트 {record['hints_used']}회 | {record['score']}점"
            )
        print(THIN_LINE)

    # ==================================================
    # 2. 퀴즈 추가
    # ==================================================
    def add_quiz(self):
        """새 퀴즈를 입력받아 등록하고 파일에 저장한다."""
        print("📌 새로운 퀴즈를 추가합니다.")
        print()
        question = self.input_text("문제를 입력하세요: ")

        choices = []
        while len(choices) < Quiz.CHOICE_COUNT:
            choice = self.input_text(f"선택지 {len(choices) + 1}: ")
            if choice in choices:
                print("⚠️ 이미 입력한 선택지와 같습니다. 다른 내용을 입력하세요.")
                continue
            choices.append(choice)

        answer = self.input_number("정답 번호 (1-4): ", 1, Quiz.CHOICE_COUNT)
        hint = self.input_text("힌트 (없으면 그냥 Enter): ", allow_empty=True)

        self.quizzes.append(Quiz(question, choices, answer, hint or None))
        print()
        if self.save():
            print("✅ 퀴즈가 추가되었습니다!")
        else:
            print("✅ 퀴즈가 추가되었습니다. (단, 파일 저장에 실패해 종료하면 사라질 수 있습니다)")

    # ==================================================
    # 3. 퀴즈 목록
    # ==================================================
    def list_quizzes(self):
        """등록된 퀴즈 목록을 출력한다."""
        if not self.quizzes:
            print("📭 등록된 퀴즈가 없습니다.")
            return
        print(f"📋 등록된 퀴즈 목록 (총 {len(self.quizzes)}개)")
        print()
        print(THIN_LINE)
        for number, quiz in enumerate(self.quizzes, start=1):
            mark = " 💡" if quiz.has_hint() else ""
            print(f"[{number}] {quiz.question}{mark}")
        print(THIN_LINE)
        print("(💡 표시는 힌트가 있는 문제)")

    # ==================================================
    # 5. 퀴즈 삭제
    # ==================================================
    def delete_quiz(self):
        """번호를 입력받아 퀴즈를 삭제하고 파일에 반영한다."""
        if not self.quizzes:
            print("📭 삭제할 퀴즈가 없습니다.")
            return
        self.list_quizzes()
        number = self.input_number(
            f"삭제할 퀴즈 번호 (1-{len(self.quizzes)}, 취소는 0): ", 0, len(self.quizzes)
        )
        if number == 0:
            print("↩️ 삭제를 취소했습니다.")
            return
        target = self.quizzes[number - 1]
        if not self.input_yes_no(f"'{target.question}' 퀴즈를 삭제할까요? (y/n): "):
            print("↩️ 삭제를 취소했습니다.")
            return
        self.quizzes.pop(number - 1)
        if self.save():
            print("🗑️ 퀴즈를 삭제했습니다.")
        else:
            print("🗑️ 퀴즈를 삭제했습니다. (단, 파일 저장에 실패했습니다)")

    # ==================================================
    # 파일 저장 / 불러오기 (state.json)
    # ==================================================
    def load(self):
        """state.json에서 데이터를 불러온다. 없거나 손상되었으면 기본 데이터를 사용한다."""
        if not self.state_path.exists():
            self.reset_to_default()
            print(f"📂 저장된 데이터가 없어 기본 퀴즈 {len(self.quizzes)}개로 시작합니다.")
            self.is_loaded = True
            self.save()
            return

        try:
            with open(self.state_path, "r", encoding="utf-8") as file:
                data = json.load(file)
            self.apply_state(data)
        except (json.JSONDecodeError, UnicodeDecodeError, ValueError, TypeError, KeyError) as error:
            # 파일 내용이 손상된 경우: 백업해 두고 기본 데이터로 복구한다.
            print(f"⚠️ 데이터 파일이 손상되어 기본 퀴즈로 복구합니다. (원인: {error})")
            self.backup_broken_file()
            self.reset_to_default()
            self.is_loaded = True
            self.save()
            return
        except OSError as error:
            # 권한 문제 등으로 파일을 읽을 수 없는 경우: 기본 데이터로 실행만 한다.
            print(f"⚠️ 데이터 파일을 읽을 수 없어 기본 퀴즈로 실행합니다. (원인: {error})")
            self.reset_to_default()
            self.is_loaded = True
            return

        self.is_loaded = True
        best = f"{self.best_score}점" if self.best_score is not None else "기록 없음"
        print(f"📂 저장된 데이터를 불러왔습니다. (퀴즈 {len(self.quizzes)}개, 최고점수 {best})")

    def apply_state(self, data):
        """JSON에서 읽은 dict를 검사하고 게임 상태에 반영한다. 형식이 틀리면 ValueError."""
        if not isinstance(data, dict):
            raise ValueError("최상위 데이터가 객체({})가 아닙니다.")

        raw_quizzes = data["quizzes"]
        if not isinstance(raw_quizzes, list):
            raise ValueError("quizzes가 리스트가 아닙니다.")
        quizzes = [Quiz.from_dict(item) for item in raw_quizzes]

        best_score = data.get("best_score")
        if best_score is not None and (
            isinstance(best_score, bool) or not isinstance(best_score, int) or not 0 <= best_score <= 100
        ):
            raise ValueError("best_score는 0~100 사이의 정수 또는 null이어야 합니다.")

        best_record = data.get("best_record")
        if best_record is not None and not isinstance(best_record, dict):
            raise ValueError("best_record 형식이 잘못되었습니다.")

        history = data.get("history", [])
        if not isinstance(history, list) or not all(isinstance(h, dict) for h in history):
            raise ValueError("history 형식이 잘못되었습니다.")
        required = ("played_at", "total", "correct", "hints_used", "score")
        for record in history:
            for key in required:
                if key not in record:
                    raise ValueError(f"history 기록에 '{key}' 항목이 없습니다.")

        # 검사를 모두 통과한 뒤에만 실제 상태를 바꾼다.
        self.quizzes = quizzes
        self.best_score = best_score
        self.best_record = best_record
        self.history = history

    def to_state(self):
        """현재 게임 상태를 JSON으로 저장할 dict로 만든다."""
        return {
            "quizzes": [quiz.to_dict() for quiz in self.quizzes],
            "best_score": self.best_score,
            "best_record": self.best_record,
            "history": self.history,
        }

    def save(self):
        """현재 상태를 state.json에 저장한다. 성공하면 True, 실패하면 False."""
        if not self.is_loaded:
            return False  # 불러오기 전에 저장하면 기존 데이터를 덮어쓸 수 있으므로 막는다.

        temp_path = self.state_path.with_name(self.state_path.name + ".tmp")
        try:
            # 임시 파일에 먼저 쓰고 교체해서, 쓰는 도중 꺼져도 원본이 깨지지 않게 한다.
            with open(temp_path, "w", encoding="utf-8") as file:
                json.dump(self.to_state(), file, ensure_ascii=False, indent=4)
            os.replace(temp_path, self.state_path)
            return True
        except OSError as error:
            print(f"⚠️ 데이터를 저장하지 못했습니다. (원인: {error})")
            return False

    def reset_to_default(self):
        """기본 퀴즈 데이터로 초기화한다."""
        self.quizzes = create_default_quizzes()
        self.best_score = None
        self.best_record = None
        self.history = []

    def backup_broken_file(self):
        """손상된 state.json을 state.json.broken 으로 복사해 둔다."""
        backup_path = self.state_path.with_name(self.state_path.name + ".broken")
        try:
            shutil.copyfile(self.state_path, backup_path)
            print(f"   손상된 파일은 {backup_path.name} 으로 백업해 두었습니다.")
        except OSError:
            pass
