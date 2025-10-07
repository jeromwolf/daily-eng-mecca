"""
Daily English Mecca - Flask 웹 애플리케이션
"""

import os
import sys
import json
import threading
from datetime import datetime
from pathlib import Path
from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
from dotenv import load_dotenv

# 상위 디렉토리의 src 모듈 임포트를 위한 경로 추가
sys.path.append(str(Path(__file__).parent.parent))

from src.content_analyzer import ContentAnalyzer
from src.image_generator import ImageGenerator
from src.tts_generator import TTSGenerator
from src.video_creator import VideoCreator
from src.youtube_metadata import YouTubeMetadataGenerator
from src.resource_manager import ResourceManager
from src.background_music_downloader import BackgroundMusicDownloader
from src.sentence_generator import SentenceGenerator

# 환경변수 로드
load_dotenv()

# Flask 앱 초기화
app = Flask(__name__)
CORS(app)

# 설정
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB
app.config['OUTPUT_DIR'] = Path(__file__).parent.parent / 'output'

# 작업 상태 저장 (실제 프로덕션에서는 Redis 등 사용)
tasks = {}


class TaskStatus:
    """작업 상태 관리 클래스"""

    def __init__(self, task_id):
        self.task_id = task_id
        self.status = 'processing'  # processing, completed, error
        self.progress = 0
        self.current_step = ''
        self.logs = []
        self.result = None
        self.error = None

    def update(self, progress, step, log=None):
        """상태 업데이트"""
        self.progress = progress
        self.current_step = step
        if log:
            self.logs.append(log)

    def to_dict(self):
        """딕셔너리로 변환"""
        return {
            'task_id': self.task_id,
            'status': self.status,
            'progress': self.progress,
            'current_step': self.current_step,
            'logs': self.logs,
            'result': self.result,
            'error': self.error
        }


def generate_video_task(task_id, sentences, voice='nova'):
    """
    백그라운드에서 비디오 생성 작업 실행

    Args:
        task_id: 작업 ID
        sentences: 영어 문장 리스트
        voice: TTS 음성
    """
    task = tasks[task_id]

    try:
        # API 키 확인
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY가 설정되지 않았습니다.")

        # 출력 디렉토리 설정
        output_dir = app.config['OUTPUT_DIR']
        audio_dir = output_dir / 'audio' / task_id
        videos_dir = output_dir / 'videos'
        metadata_dir = output_dir / 'metadata'
        resources_dir = output_dir / 'resources'

        for dir_path in [audio_dir, videos_dir, metadata_dir, resources_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)

        # 리소스 매니저 초기화 (캐싱 활성화)
        resource_manager = ResourceManager(str(resources_dir))

        # 배경 음악 자동 다운로드 (없는 경우에만)
        bg_downloader = BackgroundMusicDownloader(str(resources_dir))
        if not bg_downloader.check_music_exists():
            try:
                task.update(5, '배경 음악 다운로드 중...', '⏳ 무료 배경 음악 다운로드 중...')
                bg_downloader.download_music()
                task.update(8, '배경 음악 준비 완료', '✅ 배경 음악 다운로드 완료')
            except Exception as e:
                print(f"⚠ 배경 음악 다운로드 실패 (배경 음악 없이 계속 진행): {e}")

        # 1. 콘텐츠 분석
        task.update(10, '문장 분석 중...', '✅ 문장 분석 시작')
        analyzer = ContentAnalyzer(api_key=api_key)
        analysis = analyzer.analyze_sentences(sentences)
        task.update(15, '문장 분석 완료', f'✅ 문장 분석 완료 - 이미지 {analysis["num_images"]}개 생성 예정')

        # 1.5. 바이럴 훅 문구 생성 (AI 자동)
        task.update(17, '훅 문구 생성 중...', '⏳ AI 훅 문구 생성 중...')
        hook_phrase = analyzer.generate_hook_phrase(sentences)
        task.update(20, '훅 문구 생성 완료', f'✅ 훅 문구: {hook_phrase}')

        # 2. 이미지 생성 (모든 이미지는 resources/images에서 캐싱 관리)
        task.update(25, '이미지 생성 중...', '⏳ 이미지 생성 시작')
        image_gen = ImageGenerator(api_key=api_key, resource_manager=resource_manager, use_cache=True)
        image_paths = []

        for idx, prompt in enumerate(analysis['prompts']):
            # 이미지를 resources/images에 직접 저장 (캐싱 + 재사용)
            # output_path를 resource_manager 경로로 설정하여 중복 저장 방지
            output_path = resource_manager.get_image_path(prompt)

            image_path = image_gen.generate_image(
                prompt=prompt,
                output_path=str(output_path)
            )
            image_paths.append(image_path)
            progress = 25 + (idx + 1) * (25 // len(analysis['prompts']))
            task.update(progress, f'이미지 {idx+1}/{len(analysis["prompts"])} 생성 완료',
                       f'✅ 이미지 {idx+1} 생성 완료')

        # 3. 음성 생성 (각 문장별로 3가지 음성 생성 - 학습 효과 향상)
        task.update(55, '음성 생성 중...', '⏳ 음성 생성 시작 (3가지 음성)')
        tts_gen = TTSGenerator(api_key=api_key, resource_manager=resource_manager, use_cache=True)

        audio_info = tts_gen.generate_speech_per_sentence_multi_voice(
            sentences=sentences,
            output_dir=str(audio_dir)
        )
        # 평균 duration 계산 (alloy 기준)
        total_audio_duration = sum(info['voices']['alloy']['duration'] for info in audio_info)
        task.update(70, '음성 생성 완료', f'✅ 음성 생성 완료 (3가지 음성, 평균 {total_audio_duration:.1f}초)')

        # 4. 비디오 생성 (바이럴 훅 포함)
        task.update(75, '비디오 생성 중...', '⏳ 비디오 생성 시작')
        video_creator = VideoCreator(image_generator=image_gen, resource_manager=resource_manager)
        video_path = videos_dir / f'daily_english_{task_id}.mp4'

        video_creator.create_video(
            sentences=sentences,
            image_paths=image_paths,
            audio_info=audio_info,
            output_path=str(video_path),
            image_groups=analysis['image_groups'],
            translations=analysis.get('translations', []),
            hook_phrase=hook_phrase  # AI 자동 생성 바이럴 훅
        )
        task.update(90, '비디오 생성 완료', '✅ 비디오 생성 완료')

        # 5. 유튜브 메타정보 생성
        task.update(92, '메타정보 생성 중...', '⏳ 메타정보 생성 시작')
        metadata_gen = YouTubeMetadataGenerator(api_key=api_key)
        metadata = metadata_gen.generate_metadata(sentences)

        metadata_path = metadata_dir / f'metadata_{task_id}.json'
        metadata_gen.save_metadata(metadata, str(metadata_path))
        task.update(100, '완료!', '✅ 모든 작업 완료!')

        # 작업 완료
        task.status = 'completed'
        task.result = {
            'video_path': f'/api/download/{task_id}/video',
            'video_filename': f'daily_english_{task_id}.mp4',
            'metadata': metadata,
            'metadata_path': f'/api/download/{task_id}/metadata'
        }

    except Exception as e:
        task.status = 'error'
        task.error = str(e)
        task.update(0, '오류 발생', f'❌ 오류: {str(e)}')


# ==================== 라우트 ====================

@app.route('/')
def index():
    """메인 페이지"""
    return render_template('index.html')


@app.route('/api/generate', methods=['POST'])
def generate():
    """비디오 생성 API (포맷별 분기 처리)"""
    try:
        data = request.get_json()
        format_type = data.get('format', 'manual')  # manual, theme, other
        voice = data.get('voice', 'nova')
        sentences = data.get('sentences', [])  # manual 포맷용

        # API 키 확인
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            return jsonify({'error': 'OPENAI_API_KEY가 설정되지 않았습니다.'}), 500

        # 포맷별 문장 생성
        if format_type == 'theme':
            # 테마별 묶음
            theme = data.get('theme')
            theme_detail = data.get('theme_detail', '')

            if not theme:
                return jsonify({'error': '주제를 선택해주세요.'}), 400

            # SentenceGenerator로 문장 생성
            try:
                sentence_gen = SentenceGenerator(api_key=api_key)
                sentences = sentence_gen.generate_theme_sentences(theme, theme_detail)
            except Exception as e:
                return jsonify({'error': f'문장 생성 실패: {str(e)}'}), 500

        elif format_type == 'other':
            # 다른 포맷 (스토리 시리즈, 영화 명대사 등)
            other_format = data.get('other_format')  # story, movie, pronunciation, news

            try:
                sentence_gen = SentenceGenerator(api_key=api_key)

                if other_format == 'story':
                    story_theme = data.get('story_theme', '해외 여행')
                    story_day = int(data.get('story_day', 1))
                    sentences = sentence_gen.generate_story_series(story_theme, story_day)

                elif other_format == 'movie':
                    movie_quote_id = data.get('movie_quote_id')  # 선택된 명대사 ID (없으면 None = 랜덤)
                    if movie_quote_id:
                        movie_quote_id = int(movie_quote_id)
                    sentences = sentence_gen.generate_movie_quotes(selected_quote_id=movie_quote_id)

                elif other_format == 'pronunciation':
                    sentences = sentence_gen.generate_pronunciation_sentences()

                elif other_format == 'news':
                    sentences = sentence_gen.generate_news_sentences()

                else:
                    return jsonify({'error': f'지원하지 않는 포맷입니다: {other_format}'}), 400

            except Exception as e:
                return jsonify({'error': f'문장 생성 실패: {str(e)}'}), 500

        else:
            # manual 포맷 (기존 로직)
            # 입력 검증
            if not sentences or len(sentences) != 3:
                return jsonify({'error': '3개의 문장이 필요합니다.'}), 400

            for sentence in sentences:
                if not sentence.strip():
                    return jsonify({'error': '빈 문장이 있습니다.'}), 400

        # 최종 문장 검증 (모든 포맷 공통)
        if not sentences:
            return jsonify({'error': '문장 생성 결과가 올바르지 않습니다.'}), 500

        # manual 모드는 정확히 3문장, 나머지는 3~6문장 허용
        if format_type == 'manual':
            if len(sentences) != 3:
                return jsonify({'error': '3개의 문장이 필요합니다.'}), 400
        else:
            if len(sentences) < 3 or len(sentences) > 6:
                return jsonify({'error': f'문장 개수가 올바르지 않습니다 ({len(sentences)}개). 3~6개여야 합니다.'}), 500

        # 작업 ID 생성
        task_id = datetime.now().strftime("%Y%m%d_%H%M%S")

        # 작업 상태 초기화
        tasks[task_id] = TaskStatus(task_id)

        # 백그라운드 스레드에서 비디오 생성
        thread = threading.Thread(
            target=generate_video_task,
            args=(task_id, sentences, voice)
        )
        thread.daemon = True
        thread.start()

        return jsonify({
            'task_id': task_id,
            'status': 'processing',
            'message': '비디오 생성이 시작되었습니다.',
            'sentences': sentences  # 생성된 문장 반환 (디버깅용)
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/status/<task_id>')
def get_status(task_id):
    """작업 상태 조회 API"""
    task = tasks.get(task_id)

    if not task:
        return jsonify({'error': '작업을 찾을 수 없습니다.'}), 404

    return jsonify(task.to_dict())


@app.route('/api/movie-quotes')
def get_movie_quotes():
    """100개 영화 명대사 리스트 반환 API"""
    try:
        import json
        quotes_file = Path(__file__).parent.parent / 'src' / 'movie_quotes.json'

        with open(quotes_file, 'r', encoding='utf-8') as f:
            quotes_data = json.load(f)

        return jsonify(quotes_data)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/download/<task_id>/<file_type>')
def download(task_id, file_type):
    """파일 다운로드 API"""
    try:
        output_dir = app.config['OUTPUT_DIR']

        if file_type == 'video':
            file_path = output_dir / 'videos' / f'daily_english_{task_id}.mp4'
            mimetype = 'video/mp4'
            download_name = f'daily_english_{task_id}.mp4'
        elif file_type == 'metadata':
            file_path = output_dir / 'metadata' / f'metadata_{task_id}.json'
            mimetype = 'application/json'
            download_name = f'metadata_{task_id}.json'
        else:
            return jsonify({'error': '잘못된 파일 타입입니다.'}), 400

        if not file_path.exists():
            return jsonify({'error': '파일을 찾을 수 없습니다.'}), 404

        return send_file(
            file_path,
            mimetype=mimetype,
            as_attachment=True,
            download_name=download_name
        )

    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    # API 키 확인
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ 경고: OPENAI_API_KEY가 설정되지 않았습니다.")
        print("   .env 파일에 API 키를 입력해주세요.")

    print("\n🌟 Daily English Mecca - 웹 버전")
    print("=" * 50)
    print("🔗 http://localhost:5001 에서 실행 중...")
    print("=" * 50 + "\n")

    app.run(debug=True, host='0.0.0.0', port=5001)
