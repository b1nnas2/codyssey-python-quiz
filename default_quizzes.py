"""처음 실행하거나 state.json이 손상되었을 때 사용하는 기본 퀴즈 데이터.

주제: Python & Git 기초 상식
"""

from quiz import Quiz


def create_default_quizzes():
    """기본 퀴즈 목록(Quiz 인스턴스 리스트)을 새로 만들어 반환한다."""
    return [
        Quiz(
            "Python을 처음 만든 사람은?",
            ["귀도 반 로섬", "리누스 토르발스", "비야네 스트롭스트룹", "제임스 고슬링"],
            1,
            "네덜란드 출신 프로그래머입니다.",
        ),
        Quiz(
            "다음 중 한 번 만들면 값을 바꿀 수 없는(immutable) 자료형은?",
            ["list", "dict", "tuple", "set"],
            3,
            "소괄호 ( ) 로 만듭니다.",
        ),
        Quiz(
            "print(type(3 / 2)) 의 실행 결과에 나오는 자료형은?",
            ["int", "float", "str", "bool"],
            2,
            "/ 연산은 나누어떨어지지 않아도 소수점까지 계산합니다.",
        ),
        Quiz(
            "len([1, [2, 3], 4]) 의 결과는?",
            ["3", "4", "2", "5"],
            1,
            "안쪽 리스트 [2, 3]은 요소 1개로 셉니다.",
        ),
        Quiz(
            "클래스의 인스턴스 메서드에서 첫 번째 매개변수로 관례적으로 쓰는 이름은?",
            ["this", "self", "obj", "me"],
            2,
            "'자기 자신'이라는 뜻의 영어 단어입니다.",
        ),
        Quiz(
            "JSON 파일을 열어 파이썬 객체(dict, list 등)로 읽어오는 함수는?",
            ["json.dump()", "json.load()", "json.write()", "json.read()"],
            2,
            "dump는 저장, 그 반대는 불러오기입니다.",
        ),
        Quiz(
            "원격 저장소의 변경사항을 가져와 현재 브랜치에 합치는 Git 명령어는?",
            ["git push", "git clone", "git pull", "git commit"],
            3,
            "'당기다'라는 뜻의 영어 단어입니다.",
        ),
        Quiz(
            "새 브랜치를 만들면서 바로 그 브랜치로 이동하는 Git 명령어는?",
            ["git checkout -b 브랜치명", "git branch -d 브랜치명", "git merge 브랜치명", "git init 브랜치명"],
            1,
            "checkout 명령에 옵션을 하나 붙입니다.",
        ),
    ]
