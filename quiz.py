"""개별 퀴즈 한 문제를 표현하는 Quiz 클래스."""


class Quiz:
    """문제(question), 선택지(choices), 정답(answer), 힌트(hint)를 가진 퀴즈 한 개."""

    CHOICE_COUNT = 4  # 선택지는 항상 4개

    def __init__(self, question, choices, answer, hint=None):
        self.question = question      # str: 문제 내용
        self.choices = list(choices)  # list[str]: 선택지 4개
        self.answer = answer          # int: 정답 번호 (1~4)
        self.hint = hint              # str | None: 힌트 (없으면 None)

    # ---------- 출력 ----------
    def display(self, number=None):
        """문제와 선택지를 화면에 출력한다."""
        title = f"[문제 {number}]" if number is not None else "[문제]"
        print(title)
        print(self.question)
        print()
        for index, choice in enumerate(self.choices, start=1):
            print(f"{index}. {choice}")
        print()

    # ---------- 정답 확인 ----------
    def is_correct(self, user_answer):
        """사용자가 입력한 번호가 정답이면 True를 반환한다."""
        return user_answer == self.answer

    def correct_choice_text(self):
        """정답 선택지의 내용을 반환한다."""
        return self.choices[self.answer - 1]

    def has_hint(self):
        """힌트가 있으면 True를 반환한다."""
        return bool(self.hint)

    # ---------- 저장용 변환 ----------
    def to_dict(self):
        """JSON으로 저장할 수 있도록 dict로 바꾼다."""
        return {
            "question": self.question,
            "choices": self.choices,
            "answer": self.answer,
            "hint": self.hint,
        }

    @classmethod
    def from_dict(cls, data):
        """dict(JSON에서 읽은 데이터)로 Quiz 객체를 만든다.

        데이터 형식이 잘못되었으면 ValueError를 발생시킨다.
        """
        if not isinstance(data, dict):
            raise ValueError("퀴즈 데이터가 dict 형식이 아닙니다.")

        question = data.get("question")
        choices = data.get("choices")
        answer = data.get("answer")
        hint = data.get("hint")

        if not isinstance(question, str) or not question.strip():
            raise ValueError("문제(question)가 비어 있거나 문자열이 아닙니다.")
        if (
            not isinstance(choices, list)
            or len(choices) != cls.CHOICE_COUNT
            or not all(isinstance(c, str) and c.strip() for c in choices)
        ):
            raise ValueError("선택지(choices)는 비어 있지 않은 문자열 4개여야 합니다.")
        # bool은 int의 하위 타입이라 True/False를 따로 걸러낸다.
        if isinstance(answer, bool) or not isinstance(answer, int):
            raise ValueError("정답(answer)은 정수여야 합니다.")
        if not 1 <= answer <= cls.CHOICE_COUNT:
            raise ValueError("정답(answer)은 1~4 사이여야 합니다.")
        if hint is not None and not isinstance(hint, str):
            raise ValueError("힌트(hint)는 문자열이거나 null이어야 합니다.")

        return cls(question, choices, answer, hint or None)
