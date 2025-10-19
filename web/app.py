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
from src.editor.config_manager import ConfigManager
from src.editor.video_editor import VideoEditor

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


def generate_video_task(task_id, sentences, voice='nova', quiz_data=None):
    """
    백그라운드에서 비디오 생성 작업 실행

    Args:
        task_id: 작업 ID
        sentences: 영어 문장 리스트
        voice: TTS 음성
        quiz_data: 퀴즈 데이터 (퀴즈 포맷일 때만)
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

        # 퀴즈 포맷이 아닐 때만 이미지 생성
        if not quiz_data:
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
        else:
            # 퀴즈 포맷은 이미지 생성 건너뛰기
            task.update(25, '퀴즈 모드: 이미지 생성 건너뛰기', '✅ 퀴즈 포맷 (텍스트 기반)')
            image_gen = ImageGenerator(api_key=api_key, resource_manager=resource_manager, use_cache=True)
            image_paths = []
            analysis = {'image_groups': [], 'translations': []}
            hook_phrase = None

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

        # 4. 비디오 생성 (바이럴 훅 포함 or 퀴즈 포맷)
        task.update(75, '비디오 생성 중...', '⏳ 비디오 생성 시작 (3-5분 소요)')
        video_creator = VideoCreator(image_generator=image_gen, resource_manager=resource_manager)
        video_path = videos_dir / f'daily_english_{task_id}.mp4'

        try:
            print(f"[DEBUG] 비디오 생성 시작: {video_path}")
            task.update(77, '비디오 합성 중...', '⏳ MoviePy로 클립 합성 중...')

            # 퀴즈 포맷이면 별도 함수 사용
            if quiz_data:
                print("[DEBUG] 퀴즈 비디오 생성 모드")
                video_creator.create_quiz_video(
                    quiz_data=quiz_data,
                    audio_info=audio_info,
                    output_path=str(video_path)
                )
            else:
                print("[DEBUG] 일반 비디오 생성 모드")
                video_creator.create_video(
                    sentences=sentences,
                    image_paths=image_paths,
                    audio_info=audio_info,
                    output_path=str(video_path),
                    image_groups=analysis['image_groups'],
                    translations=analysis.get('translations', []),
                    hook_phrase=hook_phrase  # AI 자동 생성 바이럴 훅
                )

            print(f"[DEBUG] 비디오 생성 완료: {video_path.exists()}")
            task.update(90, '비디오 생성 완료', '✅ 비디오 생성 완료')
        except Exception as video_error:
            print(f"[ERROR] 비디오 생성 실패: {video_error}")
            raise video_error

        # 4.5. 편집 설정 자동 저장 (편집 기능용)
        task.update(92, '편집 설정 저장 중...', '⏳ 편집 설정 생성 중...')
        config_dir = output_dir / 'edit_configs'
        config_manager = ConfigManager(str(config_dir))

        # 기본 설정 생성 및 저장
        config = config_manager.create_default_config(
            video_id=task_id,
            sentences=sentences,
            translations=analysis.get('translations', []),
            image_paths=image_paths,
            tts_data=audio_info
        )
        config_path = config_manager.save_config(task_id, config)
        task.update(94, '편집 설정 저장 완료', f'✅ 편집 설정 저장 완료: {config_path}')

        # 5. 유튜브 메타정보 생성
        task.update(96, '메타정보 생성 중...', '⏳ 메타정보 생성 시작')
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


@app.route('/editor')
def editor():
    """편집 페이지"""
    return render_template('editor.html')


@app.route('/api/generate', methods=['POST'])
def generate():
    """비디오 생성 API (포맷별 분기 처리)"""
    try:
        data = request.get_json()
        format_type = data.get('format', 'manual')  # manual, theme, quiz, other
        voice = data.get('voice', 'nova')
        sentences = data.get('sentences', [])  # manual 포맷용
        quiz_data = None  # 퀴즈 포맷용 데이터

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

        elif format_type == 'quiz':
            # 퀴즈 챌린지 포맷
            quiz_topic = data.get('quiz_topic')
            quiz_difficulty = data.get('quiz_difficulty', 'intermediate')

            if not quiz_topic:
                return jsonify({'error': '퀴즈 주제를 선택해주세요.'}), 400

            # SentenceGenerator로 퀴즈 콘텐츠 생성
            try:
                sentence_gen = SentenceGenerator(api_key=api_key)
                quiz_content = sentence_gen.generate_quiz_content(quiz_topic, quiz_difficulty)

                # 퀴즈 콘텐츠를 sentences로 변환 (TTS 생성용, 7개로 변경)
                # 1. 질문 (한국어만)
                # 2. 선택지 (영어만)
                # 3. 정답 ("정답은 A입니다" 형태로)
                # 4. 해설
                # 5-7. 예문 3개
                question_text = quiz_content['question']  # 한국어만
                options_text = f"A, {quiz_content['option_a']}. B, {quiz_content['option_b']}."  # 영어만
                answer_text = f"정답은 {quiz_content['correct_answer']}입니다."

                sentences = [
                    question_text,              # 1. 질문 (한국어만)
                    options_text,               # 2. 선택지 (영어만)
                    answer_text,                # 3. 정답
                    quiz_content['explanation'],   # 4. 해설
                ] + quiz_content['examples']       # 5-7. 예문 3개

                # CRITICAL: quiz_data를 비디오 생성 함수에 전달하기 위해 변수에 저장
                quiz_data = quiz_content  # 퀴즈 데이터를 thread에 전달

            except Exception as e:
                return jsonify({'error': f'퀴즈 생성 실패: {str(e)}'}), 500

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

        # manual 모드는 정확히 3문장, quiz는 7개(고정), 나머지는 3~6문장 허용
        if format_type == 'manual':
            if len(sentences) != 3:
                return jsonify({'error': '3개의 문장이 필요합니다.'}), 400
        elif format_type == 'quiz':
            if len(sentences) != 7:
                return jsonify({'error': f'퀴즈 데이터가 올바르지 않습니다 ({len(sentences)}개). 7개여야 합니다.'}), 500
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
            args=(task_id, sentences, voice, quiz_data)  # quiz_data 전달
        )
        thread.daemon = False  # 작업이 완료될 때까지 유지
        thread.start()

        return jsonify({
            'task_id': task_id,
            'status': 'processing',
            'message': '비디오 생성이 시작되었습니다.',
            'sentences': sentences,  # 생성된 문장 반환 (디버깅용)
            'quiz_data': quiz_data if quiz_data else None  # 퀴즈 데이터 반환 (디버깅용)
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


# ==================== 편집 API ====================

@app.route('/api/video/<video_id>/config', methods=['GET'])
def get_video_config(video_id):
    """비디오 편집 설정 가져오기"""
    try:
        output_dir = app.config['OUTPUT_DIR']
        config_dir = output_dir / 'edit_configs'

        config_manager = ConfigManager(str(config_dir))

        # 설정 파일 로드
        config = config_manager.load_config(video_id)

        if config is None:
            return jsonify({'error': '설정 파일을 찾을 수 없습니다.'}), 404

        # 비디오 파일 경로
        video_path = output_dir / 'videos' / f'daily_english_{video_id}.mp4'

        return jsonify({
            'config': config,
            'video_path': f'/api/download/{video_id}/video' if video_path.exists() else None,
            'video_exists': video_path.exists()
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/video/<video_id>/config', methods=['POST'])
def save_video_config(video_id):
    """비디오 편집 설정 저장"""
    try:
        data = request.get_json()

        output_dir = app.config['OUTPUT_DIR']
        config_dir = output_dir / 'edit_configs'

        config_manager = ConfigManager(str(config_dir))

        # 기존 설정 로드
        config = config_manager.load_config(video_id)

        if config is None:
            return jsonify({'error': '설정 파일을 찾을 수 없습니다. 먼저 비디오를 생성해주세요.'}), 404

        # 설정 업데이트
        if 'global_settings' in data:
            config['global_settings'].update(data['global_settings'])

        if 'clips' in data:
            config['clips'] = data['clips']

        # 설정 저장
        config_path = config_manager.save_config(video_id, config)

        return jsonify({
            'success': True,
            'message': '설정이 저장되었습니다.',
            'config_path': config_path
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/video/<video_id>/regenerate', methods=['POST'])
def regenerate_video(video_id):
    """편집된 설정으로 비디오 재생성"""
    try:
        data = request.get_json()
        config = data.get('config')

        output_dir = app.config['OUTPUT_DIR']
        config_dir = output_dir / 'edit_configs'
        videos_dir = output_dir / 'videos'

        # VideoEditor 초기화
        video_editor = VideoEditor(str(config_dir), str(videos_dir))

        # 비디오 재생성
        import time
        start_time = time.time()

        video_path = video_editor.regenerate_video(video_id, config)

        processing_time = time.time() - start_time

        return jsonify({
            'success': True,
            'video_path': f'/api/download/{video_id}/video_edited',
            'processing_time': round(processing_time, 2)
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/download/<video_id>/video_edited')
def download_edited_video(video_id):
    """편집된 비디오 다운로드"""
    try:
        output_dir = app.config['OUTPUT_DIR']
        file_path = output_dir / 'videos' / f'{video_id}_edited.mp4'

        if not file_path.exists():
            return jsonify({'error': '파일을 찾을 수 없습니다.'}), 404

        return send_file(
            file_path,
            mimetype='video/mp4',
            as_attachment=True,
            download_name=f'daily_english_{video_id}_edited.mp4'
        )

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/video/<video_id>/upload-intro-image', methods=['POST'])
def upload_intro_image(video_id):
    """인트로 이미지 파일 업로드"""
    try:
        # 파일 확인
        if 'file' not in request.files:
            return jsonify({'error': '파일이 없습니다.'}), 400

        file = request.files['file']

        if file.filename == '':
            return jsonify({'error': '파일이 선택되지 않았습니다.'}), 400

        # 파일 확장자 검증
        allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
        ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''

        if ext not in allowed_extensions:
            return jsonify({'error': f'지원하지 않는 파일 형식입니다.'}), 400

        # 파일 저장
        output_dir = app.config['OUTPUT_DIR']
        upload_folder = output_dir / 'resources' / 'images'
        upload_folder.mkdir(parents=True, exist_ok=True)

        filename = f"intro_{video_id}.{ext}"
        file_path = upload_folder / filename
        file.save(file_path)

        # Config 업데이트
        config_dir = output_dir / 'edit_configs'
        config_manager = ConfigManager(str(config_dir))
        config = config_manager.load_config(video_id)

        if config:
            if 'global_settings' not in config:
                config['global_settings'] = {}
            if 'intro' not in config['global_settings']:
                config['global_settings']['intro'] = {}

            config['global_settings']['intro']['custom_image'] = str(file_path)
            config_manager.save_config(video_id, config)

        return jsonify({
            'success': True,
            'image_path': str(file_path),
            'message': '인트로 이미지 업로드 완료!'
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/video/<video_id>/upload-outro-image', methods=['POST'])
def upload_outro_image(video_id):
    """아웃트로 이미지 파일 업로드"""
    try:
        # 파일 확인
        if 'file' not in request.files:
            return jsonify({'error': '파일이 없습니다.'}), 400

        file = request.files['file']

        if file.filename == '':
            return jsonify({'error': '파일이 선택되지 않았습니다.'}), 400

        # 파일 확장자 검증
        allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
        ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''

        if ext not in allowed_extensions:
            return jsonify({'error': f'지원하지 않는 파일 형식입니다.'}), 400

        # 파일 저장
        output_dir = app.config['OUTPUT_DIR']
        upload_folder = output_dir / 'resources' / 'images'
        upload_folder.mkdir(parents=True, exist_ok=True)

        filename = f"outro_{video_id}.{ext}"
        file_path = upload_folder / filename
        file.save(file_path)

        # Config 업데이트
        config_dir = output_dir / 'edit_configs'
        config_manager = ConfigManager(str(config_dir))
        config = config_manager.load_config(video_id)

        if config:
            if 'global_settings' not in config:
                config['global_settings'] = {}
            if 'outro' not in config['global_settings']:
                config['global_settings']['outro'] = {}

            config['global_settings']['outro']['custom_image'] = str(file_path)
            config_manager.save_config(video_id, config)

        return jsonify({
            'success': True,
            'image_path': str(file_path),
            'message': '아웃트로 이미지 업로드 완료!'
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/video/<video_id>/generate-intro-image', methods=['POST'])
def generate_intro_image(video_id):
    """인트로 이미지 생성 (커스터마이징)"""
    try:
        data = request.get_json()
        custom_prompt = data.get('prompt', '')

        # API 키 확인
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            return jsonify({'error': 'OPENAI_API_KEY가 설정되지 않았습니다.'}), 500

        output_dir = app.config['OUTPUT_DIR']
        resources_dir = output_dir / 'resources'
        config_dir = output_dir / 'edit_configs'

        # ResourceManager 초기화
        resource_manager = ResourceManager(str(resources_dir))
        image_gen = ImageGenerator(api_key=api_key, resource_manager=resource_manager, use_cache=False)

        # 프롬프트 결정 (커스텀 또는 기본)
        if custom_prompt.strip():
            prompt = custom_prompt + " Vertical 9:16 format for video intro."
        else:
            prompt = """A simple geometric abstract background with bright cheerful blue gradient.
Modern minimalist design with soft shapes and clean composition.
Vertical 9:16 format. Educational and friendly mood.
Simple flat design with pastel colors."""

        # 이미지 생성 (비디오별 고유 경로)
        image_filename = f"intro_{video_id}.png"
        image_path = resources_dir / "images" / image_filename

        generated_path = image_gen.generate_image(
            prompt=prompt,
            output_path=str(image_path),
            size="1024x1792"
        )

        # Config 업데이트
        config_manager = ConfigManager(str(config_dir))
        config = config_manager.load_config(video_id)

        if config:
            if 'global_settings' not in config:
                config['global_settings'] = {}
            if 'intro' not in config['global_settings']:
                config['global_settings']['intro'] = {}

            config['global_settings']['intro']['custom_image'] = str(generated_path)
            config_manager.save_config(video_id, config)

        return jsonify({
            'success': True,
            'image_path': str(generated_path),
            'message': '인트로 이미지가 생성되었습니다.'
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/video/<video_id>/generate-outro-image', methods=['POST'])
def generate_outro_image(video_id):
    """아웃트로 이미지 생성 (커스터마이징)"""
    try:
        data = request.get_json()
        custom_prompt = data.get('prompt', '')

        # API 키 확인
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            return jsonify({'error': 'OPENAI_API_KEY가 설정되지 않았습니다.'}), 500

        output_dir = app.config['OUTPUT_DIR']
        resources_dir = output_dir / 'resources'
        config_dir = output_dir / 'edit_configs'

        # ResourceManager 초기화
        resource_manager = ResourceManager(str(resources_dir))
        image_gen = ImageGenerator(api_key=api_key, resource_manager=resource_manager, use_cache=False)

        # 프롬프트 결정 (커스텀 또는 기본)
        if custom_prompt.strip():
            prompt = custom_prompt + " Vertical 9:16 format for video outro."
        else:
            prompt = """A simple geometric abstract background with warm pink coral gradient.
Modern minimalist design with soft shapes and clean composition.
Vertical 9:16 format. Friendly and inviting mood.
Simple flat design with pastel colors."""

        # 이미지 생성 (비디오별 고유 경로)
        image_filename = f"outro_{video_id}.png"
        image_path = resources_dir / "images" / image_filename

        generated_path = image_gen.generate_image(
            prompt=prompt,
            output_path=str(image_path),
            size="1024x1792"
        )

        # Config 업데이트
        config_manager = ConfigManager(str(config_dir))
        config = config_manager.load_config(video_id)

        if config:
            if 'global_settings' not in config:
                config['global_settings'] = {}
            if 'outro' not in config['global_settings']:
                config['global_settings']['outro'] = {}

            config['global_settings']['outro']['custom_image'] = str(generated_path)
            config_manager.save_config(video_id, config)

        return jsonify({
            'success': True,
            'image_path': str(generated_path),
            'message': '아웃트로 이미지가 생성되었습니다.'
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/video/<video_id>/upload-media/<int:clip_index>', methods=['POST'])
def upload_media(video_id, clip_index):
    """
    미디어 파일 업로드 (이미지/GIF/동영상)
    """
    try:
        # 파일 확인
        if 'media' not in request.files:
            return jsonify({'error': '파일이 없습니다.'}), 400

        file = request.files['media']

        if file.filename == '':
            return jsonify({'error': '파일이 선택되지 않았습니다.'}), 400

        # 파일 확장자 검증
        allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'mov', 'avi', 'webp'}
        ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''

        if ext not in allowed_extensions:
            return jsonify({'error': f'지원하지 않는 파일 형식입니다. 허용: {", ".join(allowed_extensions)}'}), 400

        # 파일 저장 디렉토리
        output_dir = app.config['OUTPUT_DIR']
        upload_folder = output_dir / 'media' / video_id
        upload_folder.mkdir(parents=True, exist_ok=True)

        # 파일 저장
        filename = f"clip_{clip_index}_{file.filename}"
        file_path = upload_folder / filename
        file.save(file_path)

        # Config 업데이트
        config_dir = output_dir / 'edit_configs'
        config_manager = ConfigManager(str(config_dir))
        config = config_manager.load_config(video_id)

        if config:
            # 클립 이미지 경로 업데이트
            config['clips'][clip_index]['image']['path'] = str(file_path)

            # 미디어 타입 저장
            if ext == 'gif':
                config['clips'][clip_index]['image']['type'] = 'gif'
            elif ext in ['mp4', 'mov', 'avi']:
                config['clips'][clip_index]['image']['type'] = 'video'
            else:
                config['clips'][clip_index]['image']['type'] = 'image'

            config_manager.save_config(video_id, config)

        return jsonify({
            'success': True,
            'message': '미디어 업로드 완료!',
            'file_path': str(file_path),
            'file_type': ext
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/video/<video_id>/generate-clip-image/<int:clip_index>', methods=['POST'])
def generate_clip_image(video_id, clip_index):
    """
    특정 클립의 AI 이미지 생성
    """
    try:
        data = request.get_json()
        custom_prompt = data.get('prompt', '')

        # API 키 확인
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            return jsonify({'error': 'OPENAI_API_KEY가 설정되지 않았습니다.'}), 500

        output_dir = app.config['OUTPUT_DIR']
        resources_dir = output_dir / 'resources'
        config_dir = output_dir / 'edit_configs'

        # 설정 로드
        config_manager = ConfigManager(str(config_dir))
        config = config_manager.load_config(video_id)

        if not config:
            return jsonify({'error': '설정 파일을 찾을 수 없습니다.'}), 404

        # 클립 정보 가져오기
        if clip_index >= len(config['clips']):
            return jsonify({'error': '잘못된 클립 인덱스입니다.'}), 400

        clip = config['clips'][clip_index]
        sentence = clip['sentence_text']

        # 프롬프트 결정
        if not custom_prompt.strip():
            custom_prompt = sentence

        prompt = custom_prompt + " Vertical 9:16 format for video background. Photorealistic style."

        # ResourceManager 초기화
        resource_manager = ResourceManager(str(resources_dir))
        image_gen = ImageGenerator(api_key=api_key, resource_manager=resource_manager, use_cache=False)

        # 이미지 생성 (비디오+클립별 고유 경로)
        image_filename = f"clip_{video_id}_{clip_index}.png"
        image_path = resources_dir / "images" / image_filename

        generated_path = image_gen.generate_image(
            prompt=prompt,
            output_path=str(image_path),
            size="1024x1792"
        )

        # Config 업데이트
        config['clips'][clip_index]['image']['path'] = str(generated_path)
        config['clips'][clip_index]['image']['type'] = 'image'
        config_manager.save_config(video_id, config)

        return jsonify({
            'success': True,
            'image_path': str(generated_path),
            'message': f'문장 {clip_index + 1} 이미지 생성 완료!'
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== Static 파일 서빙 ====================

@app.route('/output/<path:filename>')
def serve_output_files(filename):
    """
    output 폴더의 파일들을 static으로 서빙
    (이미지, 오디오, 동영상 등)
    """
    try:
        output_dir = app.config['OUTPUT_DIR']
        file_path = output_dir / filename

        if not file_path.exists():
            return jsonify({'error': '파일을 찾을 수 없습니다.'}), 404

        return send_file(file_path)

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
