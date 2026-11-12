# 🎯 나만의 퀴즈 게임 (Python & Git 기초 퀴즈)

## 1. 프로젝트 개요

터미널에서 동작하는 4지선다 퀴즈 게임입니다.
메뉴에서 번호를 골라 퀴즈를 풀고, 새 퀴즈를 추가하고, 목록과 최고 점수를 확인할 수 있습니다.
퀴즈와 점수는 `state.json` 파일에 저장되기 때문에 프로그램을 껐다 켜도 그대로 남아 있습니다.

- 언어: Python 3.10 이상 (외부 라이브러리 없이 표준 라이브러리만 사용)
- 구조: `Quiz`(퀴즈 한 문제) / `QuizGame`(게임 전체 관리) 두 개의 클래스로 역할 분리
- 버전 관리: Git, GitHub (기능 단위 커밋, 브랜치 생성/병합)

## 2. 퀴즈 주제와 선정 이유

**주제: Python & Git 기초 상식**

이 미션에서 배우는 자료형, 클래스, JSON 파일 입출력, Git 명령어를 퀴즈로 만들면
게임을 만드는 동안 개념을 한 번 더 정리할 수 있고, 완성한 뒤에도 게임을 하면서 복습할 수 있습니다.
문제를 직접 만들면서 "정답이 왜 정답인지"를 설명할 수 있어야 해서 공부에도 도움이 되기 때문에 이 주제를 골랐습니다.

## 3. 실행 방법

```bash
# 1) 저장소 복제
git clone https://github.com/b1nnas2/codyssey-python-quiz.git
cd codyssey-python-quiz

# 2) Python 버전 확인 (3.10 이상)
python --version

# 3) 실행
python main.py
```

> macOS/Linux에서 `python`이 Python 2를 가리키면 `python3 main.py`로 실행합니다.

## 4. 기능 목록

| 메뉴 | 기능 | 설명 |
|---|---|---|
| 1 | 퀴즈 풀기 | 풀 문제 수를 고르면 문제를 **랜덤 순서**로 출제하고, 정답/오답과 최종 결과를 보여 줍니다. 풀이 중 `h`를 입력하면 **힌트**를 볼 수 있습니다(힌트를 쓴 문제는 맞혀도 점수 절반). |
| 2 | 퀴즈 추가 | 문제, 선택지 4개, 정답 번호(1-4), 힌트(선택)를 입력받아 등록하고 바로 파일에 저장합니다. |
| 3 | 퀴즈 목록 | 등록된 퀴즈를 번호와 함께 보여 줍니다. 힌트가 있는 문제는 💡로 표시합니다. |
| 4 | 점수 확인 | 최고 점수와 그때의 정답 수, 총 플레이 횟수를 보여 줍니다. |
| 5 | 퀴즈 삭제 | 번호를 골라 확인(y/n) 후 퀴즈를 삭제하고 파일에 반영합니다. (0 입력 시 취소) |
| 6 | 게임 기록 보기 | 날짜/시간, 푼 문제 수, 정답 수, 힌트 사용 수, 점수를 최근 10회까지 보여 줍니다. |
| 7 | 종료 | 데이터를 저장하고 종료합니다. |

### 점수 계산 방법
- 100점 만점, 문제당 `100 ÷ 푼 문제 수` 점
- 정답: 문제 점수 전부 / 힌트 사용 후 정답: 절반 / 오답: 0점
- 게임이 끝날 때마다 최고 점수와 비교해 더 높으면 갱신하고 저장합니다.

### 입력/예외 처리
- 모든 입력은 앞뒤 공백을 제거한 뒤 처리합니다. (예: ` 1 ` → `1`)
- 숫자가 아닌 입력(`abc`), 범위 밖 숫자(메뉴 `9`, 정답 `0`), 빈 입력(그냥 Enter)은 안내 메시지를 보여 주고 다시 입력받습니다.
- 퀴즈가 하나도 없을 때 풀기/목록/삭제를 고르면 안내 메시지를 보여 줍니다.
- 아직 퀴즈를 풀지 않았을 때 점수 확인/기록 보기를 고르면 안내 메시지를 보여 줍니다.
- `Ctrl+C`(KeyboardInterrupt)나 입력 스트림 종료(EOFError, `Ctrl+D`/`Ctrl+Z`)가 발생해도 오류 없이 저장 후 종료합니다.
- `state.json`이 없으면 기본 퀴즈로 시작하고, 손상되었으면 안내 메시지와 함께 `state.json.broken`으로 백업한 뒤 기본 퀴즈로 복구합니다.

## 5. 파일 구조

```
codyssey-python-quiz/
├── main.py              # 프로그램 시작점. Ctrl+C / EOF 처리 후 안전 종료
├── quiz_game.py         # QuizGame 클래스: 메뉴, 입력 처리, 게임 진행, 추가/목록/삭제, 점수, 저장/불러오기
├── quiz.py              # Quiz 클래스: 문제 출력, 정답 확인, dict 변환
├── default_quizzes.py   # 기본 퀴즈 8개 (Quiz 인스턴스로 생성)
├── state.json           # 퀴즈/점수 데이터 파일 (없으면 실행 시 자동 생성)
├── .gitignore
├── README.md
└── docs/
    └── screenshots/     # 실행 화면 캡처
```

## 6. 데이터 파일 설명 (`state.json`)

- **경로**: 프로젝트 루트(`main.py`와 같은 폴더)의 `state.json`
- **역할**: 퀴즈 목록, 최고 점수, 게임 기록을 저장해서 프로그램을 다시 실행해도 유지되게 합니다.
- **인코딩**: UTF-8 (`ensure_ascii=False`로 한글을 그대로 저장)
- **저장 시점**: 퀴즈 추가/삭제 직후, 게임 한 판이 끝난 직후, 종료할 때
- **안전한 저장**: `state.json.tmp`에 먼저 쓴 뒤 교체해서, 저장 도중 꺼져도 원본이 깨지지 않습니다.
- **파일이 없을 때**: 기본 퀴즈 8개로 시작하고 `state.json`을 새로 만듭니다.

### 스키마

| 키 | 타입 | 설명 |
|---|---|---|
| `quizzes` | list | 퀴즈 목록 |
| `quizzes[].question` | str | 문제 |
| `quizzes[].choices` | list[str] | 선택지 4개 |
| `quizzes[].answer` | int | 정답 번호 (1~4) |
| `quizzes[].hint` | str 또는 null | 힌트 (없으면 null) |
| `best_score` | int 또는 null | 최고 점수 (0~100), 아직 안 풀었으면 null |
| `best_record` | object 또는 null | 최고 점수 기록의 `total`(문제 수), `correct`(정답 수), `hints_used`(힌트 수) |
| `history` | list | 모든 게임 기록 |
| `history[].played_at` | str | 플레이 날짜/시간 (`YYYY-MM-DD HH:MM:SS`) |
| `history[].total` / `correct` / `hints_used` / `score` | int | 푼 문제 수 / 정답 수 / 힌트 사용 수 / 점수 |

### 예시

```json
{
    "quizzes": [
        {
            "question": "Python을 처음 만든 사람은?",
            "choices": ["귀도 반 로섬", "리누스 토르발스", "비야네 스트롭스트룹", "제임스 고슬링"],
            "answer": 1,
            "hint": "네덜란드 출신 프로그래머입니다."
        }
    ],
    "best_score": 80,
    "best_record": {"total": 5, "correct": 4, "hints_used": 0},
    "history": [
        {"played_at": "2026-11-09 17:30:00", "total": 5, "correct": 4, "hints_used": 0, "score": 80}
    ]
}
```

## 7. 실행 화면

| 메뉴 | 퀴즈 풀기 |
|---|---|
| ![메뉴](docs/screenshots/menu.png) | ![퀴즈 풀기](docs/screenshots/play.png) |

| 퀴즈 추가 | 점수 확인 |
|---|---|
| ![퀴즈 추가](docs/screenshots/add_quiz.png) | ![점수 확인](docs/screenshots/score.png) |
