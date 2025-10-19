"""
비디오 생성 설정 (폰트, 색상, 위치, 크기 등)
"""

class VideoSettings:
    """비디오 생성 관련 모든 설정 상수"""

    # === 비디오 크기 ===
    WIDTH = 1080
    HEIGHT = 1920
    FPS = 30

    # === 폰트 ===
    KOREAN_FONT = "/System/Library/AssetsV2/com_apple_MobileAsset_Font7/bad9b4bf17cf1669dde54184ba4431c22dcad27b.asset/AssetData/NanumGothic.ttc"

    # === 색상 ===
    class Colors:
        # 배경색
        INTRO_BG = (100, 150, 255)  # 파스텔 블루
        OUTRO_BG = (255, 150, 180)  # 파스텔 핑크
        QUIZ_QUESTION_BG = (100, 150, 255)  # 파스텔 블루
        QUIZ_ANSWER_BG = (100, 200, 100)  # 파스텔 그린
        QUIZ_EXPLANATION_BG = (255, 220, 100)  # 파스텔 옐로우
        QUIZ_EXAMPLE_BG = (180, 150, 255)  # 파스텔 퍼플

        # 텍스트색
        WHITE = 'white'
        BLACK = 'black'
        GOLD = '#FFD700'

    # === 퀴즈 클립 설정 ===
    class Quiz:
        # 문제 클립
        class Question:
            QUESTION_Y = 550
            QUESTION_FONT_SIZE = 48
            OPTION_A_Y = 850
            OPTION_B_Y = 1050
            OPTION_FONT_SIZE = 42
            OPTION_X = 80

        # 카운트다운 클립
        class Countdown:
            QUESTION_Y = 300
            QUESTION_FONT_SIZE = 36
            OPTION_A_Y = 550
            OPTION_B_Y = 680
            OPTION_FONT_SIZE = 32
            OPTION_X = 80
            COUNTDOWN_Y = 1100
            COUNTDOWN_FONT_SIZE = 200
            COUNTDOWN_STROKE_WIDTH = 8

        # 정답 클립
        class Answer:
            TITLE_Y = 550
            TITLE_FONT_SIZE = 45
            ANSWER_Y = 750
            ANSWER_FONT_SIZE = 120
            ANSWER_STROKE_WIDTH = 5
            OPTION_Y = 950
            OPTION_FONT_SIZE = 40

        # 해설 클립
        class Explanation:
            TITLE_Y = 450
            TITLE_FONT_SIZE = 45
            CONTENT_Y = 750
            CONTENT_FONT_SIZE = 38

        # 예문 클립
        class Example:
            TITLE_Y = 450
            TITLE_FONT_SIZE = 40
            GUIDE_Y = 600
            GUIDE_FONT_SIZE = 32
            CONTENT_Y = 900
            CONTENT_FONT_SIZE = 48

    # === 인트로/아웃트로 설정 ===
    class Intro:
        TEXT_Y = 800
        FONT_SIZE = 65
        DURATION = 3.0

    class Outro:
        MAIN_TEXT_Y = 700
        MAIN_FONT_SIZE = 58
        SUB_TEXT_Y = 850
        SUB_FONT_SIZE = 38
        DURATION = 2.0

    # === 타이밍 설정 ===
    class Timing:
        PAUSE_BETWEEN_SCENES = 2.0  # 일반 장면 전환 간격
        COUNTDOWN_DURATION = 3.0     # 카운트다운 고정 시간
        INTRO_BG_MUSIC_DURATION = 3.0  # 배경음악 재생 시간

    # === 텍스트 공통 설정 ===
    class Text:
        MARGIN = (10, 20)  # 텍스트 여백 (한글 깨짐 방지)
        STROKE_COLOR = 'black'
        STROKE_WIDTH = 3
        STROKE_WIDTH_SMALL = 2
