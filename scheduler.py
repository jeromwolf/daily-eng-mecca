"""
매일 오전 7시 자동 비디오 생성 스케줄러

사용법:
    python scheduler.py

백그라운드 실행:
    nohup python scheduler.py >> logs/scheduler.log 2>&1 &
"""

import os
import sys
import schedule
import time
import requests
import json
from datetime import datetime
from pathlib import Path

# 프로젝트 루트 경로
PROJECT_ROOT = Path(__file__).parent
sys.path.append(str(PROJECT_ROOT))

# 로그 디렉토리
LOG_DIR = PROJECT_ROOT / 'logs'
LOG_DIR.mkdir(exist_ok=True)


# 요일별 테마 순환
DAILY_THEMES = {
    0: {'theme': 'daily', 'detail': '일상 대화'},        # 월요일
    1: {'theme': 'business', 'detail': '직장 회의'},     # 화요일
    2: {'theme': 'travel', 'detail': '공항 체크인'},     # 수요일
    3: {'theme': 'restaurant', 'detail': '레스토랑'},   # 목요일
    4: {'theme': 'shopping', 'detail': '쇼핑몰'},       # 금요일
    5: {'theme': 'hobby', 'detail': '취미 활동'},       # 토요일
    6: {'theme': 'study', 'detail': '영어 공부'}        # 일요일
}


def log_message(message):
    """로그 메시지 출력 및 파일 저장"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_msg = f"[{timestamp}] {message}"
    print(log_msg)

    # 로그 파일에 저장
    log_file = LOG_DIR / f"scheduler_{datetime.now().strftime('%Y%m')}.log"
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(log_msg + '\n')


def generate_daily_video():
    """오늘의 테마로 비디오 자동 생성"""
    try:
        log_message("=" * 50)
        log_message("🎬 Daily English Mecca - 자동 생성 시작")

        # 오늘 요일 (0=월요일, 6=일요일)
        weekday = datetime.now().weekday()
        theme_config = DAILY_THEMES[weekday]

        log_message(f"📅 오늘 요일: {['월', '화', '수', '목', '금', '토', '일'][weekday]}요일")
        log_message(f"🎯 테마: {theme_config['theme']} - {theme_config['detail']}")

        # Flask API 호출
        api_url = 'http://localhost:5001/api/generate'

        payload = {
            'format': 'theme',
            'theme': theme_config['theme'],
            'theme_detail': theme_config['detail'],
            'voice': 'nova'
        }

        log_message(f"📡 API 요청: {api_url}")
        log_message(f"   Payload: {json.dumps(payload, ensure_ascii=False)}")

        response = requests.post(api_url, json=payload, timeout=600)  # 10분 타임아웃

        if response.status_code == 200:
            result = response.json()
            task_id = result.get('task_id')
            log_message(f"✅ 비디오 생성 작업 시작")
            log_message(f"   Task ID: {task_id}")

            # 작업 완료 대기 (최대 10분)
            status_url = f'http://localhost:5001/api/status/{task_id}'
            max_wait_time = 600  # 10분
            wait_interval = 5  # 5초마다 체크
            elapsed_time = 0

            while elapsed_time < max_wait_time:
                time.sleep(wait_interval)
                elapsed_time += wait_interval

                status_response = requests.get(status_url)
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    task_status = status_data.get('status')
                    progress = status_data.get('progress', 0)

                    log_message(f"   진행 상황: {progress}% - {status_data.get('current_step', '')}")

                    if task_status == 'completed':
                        log_message("🎉 비디오 생성 완료!")
                        log_message(f"   파일: {status_data.get('result', {}).get('video_filename', '')}")
                        log_message(f"   다운로드: http://localhost:5001{status_data.get('result', {}).get('video_path', '')}")

                        # 성공 로그 저장
                        success_log = LOG_DIR / 'success_videos.json'
                        success_data = []

                        if success_log.exists():
                            with open(success_log, 'r', encoding='utf-8') as f:
                                success_data = json.load(f)

                        success_data.append({
                            'date': datetime.now().isoformat(),
                            'task_id': task_id,
                            'theme': theme_config,
                            'result': status_data.get('result')
                        })

                        with open(success_log, 'w', encoding='utf-8') as f:
                            json.dump(success_data, f, indent=2, ensure_ascii=False)

                        return True

                    elif task_status == 'error':
                        error_msg = status_data.get('error', '알 수 없는 오류')
                        log_message(f"❌ 비디오 생성 실패: {error_msg}")
                        return False

            log_message("⏰ 타임아웃: 비디오 생성이 10분 내에 완료되지 않았습니다.")
            return False

        else:
            log_message(f"❌ API 요청 실패: {response.status_code}")
            log_message(f"   응답: {response.text}")
            return False

    except Exception as e:
        log_message(f"❌ 오류 발생: {str(e)}")
        import traceback
        log_message(traceback.format_exc())
        return False
    finally:
        log_message("=" * 50 + "\n")


def check_server():
    """Flask 서버 실행 확인"""
    try:
        response = requests.get('http://localhost:5001/', timeout=5)
        return response.status_code == 200
    except:
        return False


def main():
    """메인 스케줄러"""
    log_message("🚀 Daily English Mecca 스케줄러 시작")
    log_message(f"   프로젝트 경로: {PROJECT_ROOT}")
    log_message(f"   로그 경로: {LOG_DIR}")

    # 서버 확인
    if not check_server():
        log_message("❌ Flask 서버가 실행되지 않았습니다!")
        log_message("   먼저 서버를 시작하세요: cd web && python app.py")
        sys.exit(1)

    log_message("✅ Flask 서버 연결 확인")

    # 매일 오전 7시에 실행
    schedule.every().day.at("07:00").do(generate_daily_video)

    log_message("⏰ 스케줄 등록 완료: 매일 오전 7시")
    log_message("   다음 실행 예정 시간:")

    for job in schedule.get_jobs():
        log_message(f"   - {job}")

    # 테스트 실행 옵션 (주석 해제하면 즉시 실행)
    # log_message("\n🧪 테스트 실행 시작...")
    # generate_daily_video()

    # 무한 루프
    log_message("\n대기 중... (Ctrl+C로 종료)")

    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # 1분마다 체크
    except KeyboardInterrupt:
        log_message("\n👋 스케줄러 종료")


if __name__ == '__main__':
    main()
