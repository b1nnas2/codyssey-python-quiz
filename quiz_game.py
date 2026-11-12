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
