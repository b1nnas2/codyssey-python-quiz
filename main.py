"""퀴즈 게임 실행 파일.  실행: python main.py"""

from pathlib import Path

from quiz_game import QuizGame

# 프로젝트 루트(이 파일이 있는 폴더)의 state.json
STATE_PATH = Path(__file__).resolve().parent / "state.json"


def main():
    game = QuizGame(STATE_PATH)
    try:
        game.run()
    except (KeyboardInterrupt, EOFError):
        # Ctrl+C 또는 입력 스트림 종료(Ctrl+D / Ctrl+Z) 시 비정상 종료하지 않고 저장 후 종료
        print("\n\n⚠️ 입력이 중단되어 프로그램을 종료합니다.")
        if game.save():
            print("💾 지금까지의 데이터를 저장했습니다. (진행 중이던 퀴즈 결과는 저장되지 않습니다)")
        print("👋 안녕히 가세요!")


if __name__ == "__main__":
    main()
