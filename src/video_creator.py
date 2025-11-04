"""
MoviePy를 사용한 유튜브 비디오 생성 모듈 (롱폼 16:9 가로)
"""
import os
from pathlib import Path
from moviepy import (
    VideoClip, ImageClip, AudioFileClip, TextClip,
    CompositeVideoClip, CompositeAudioClip, concatenate_videoclips, ColorClip, vfx
)
from src.clips.quiz import (
    QuestionClip, CountdownClip, AnswerClip,
    ExplanationClip, ExampleClip
)
from src.preview import QuizPreviewGenerator
from src.config.kelly_dialogues import (
    get_random_intro, get_random_outro,
    get_random_quiz_intro, get_random_quiz_outro
)
from src.config.video_settings import VideoSettings


class VideoCreator:
    def __init__(self, image_generator=None, resource_manager=None, use_kelly=True):
        """VideoCreator 초기화"""
        # VideoSettings에서 가져오기
        self.width = VideoSettings.WIDTH  # 1920 (가로)
        self.height = VideoSettings.HEIGHT  # 1080 (세로)
        self.fps = VideoSettings.FPS  # 30

        # Kelly 레이아웃 설정
        self.kelly_width = VideoSettings.KELLY_WIDTH  # 640 (왼쪽 1/3)
        self.content_width = VideoSettings.CONTENT_WIDTH  # 1280 (오른쪽 2/3)

        self.image_generator = image_generator
        self.resource_manager = resource_manager

        # Kelly Cat 캐릭터 사용 여부
        self.use_kelly = use_kelly

        # 커스텀 인트로/아웃트로 이미지 경로 (설정에서 가져옴)
        self.intro_custom_image = None
        self.outro_custom_image = None

    def _get_kelly_image_path(self, kelly_type: str = "casual_hoodie") -> str:
        """
        Kelly 캐릭터 이미지 경로 가져오기

        Args:
            kelly_type: Kelly 이미지 타입 (casual_hoodie, ponytail, glasses)

        Returns:
            Kelly 이미지 파일 경로 (없으면 None)
        """
        if not self.resource_manager:
            return None

        # Kelly 이미지 파일명
        kelly_filename = f"kelly_{kelly_type}.png"
        kelly_path = Path(self.resource_manager.resources_dir) / "images" / kelly_filename

        if kelly_path.exists():
            return str(kelly_path)

        print(f"⚠️ Kelly 이미지를 찾을 수 없습니다: {kelly_path}")
        return None

    def create_video(
        self,
        sentences: list[str],
        image_paths: list[str],
        audio_info: list[dict],
        output_path: str,
        image_groups: list[list[int]] = None,
        translations: list[str] = None,
        hook_phrase: str = None
    ) -> str:
        """
        유튜브 쇼츠 비디오 생성

        Args:
            sentences: 영어 문장 리스트
            image_paths: 이미지 파일 경로 리스트
            audio_info: 각 문장별 오디오 정보 [{'path': str, 'duration': float}, ...]
            output_path: 비디오 저장 경로
            image_groups: 각 이미지에 표시할 문장 인덱스 리스트
            translations: 한글 번역 리스트
            hook_phrase: 인트로 훅 문구 (AI 자동 생성, 없으면 기본값)

        Returns:
            생성된 비디오 파일 경로
        """
        try:
            print("비디오 생성 중...")

            # 기본 이미지 그룹 설정 (각 문장에 하나씩)
            if image_groups is None:
                image_groups = [[i] for i in range(len(sentences))]

            # 인트로 생성 (3초, 훅 문구 포함)
            intro_clip = self._create_intro_clip(duration=3, hook_phrase=hook_phrase)

            # 각 이미지에 어떤 문장들이 매핑되는지 확인
            # 각 문장마다 개별 클립을 생성 (정확한 타이밍을 위해)
            sentence_clips = []
            audio_clips = []

            # 문장 인덱스 -> 이미지 경로 매핑 생성
            sentence_to_image = {}
            for img_idx, sent_indices in enumerate(image_groups):
                for sent_idx in sent_indices:
                    if sent_idx < len(sentences) and img_idx < len(image_paths):
                        sentence_to_image[sent_idx] = image_paths[img_idx]

            # 각 문장마다 개별 클립 생성 (TTS와 정확히 동기화)
            # 각 문장을 3번 반복 (각 반복마다 다른 음성 사용 - 학습 효과 향상)
            current_time = 3.0  # 인트로 3초 후부터 시작
            pause_duration = 2.0  # 각 문장 사이 간격 (사용자가 따라 말할 시간)
            repeat_count = 3  # 각 문장을 3번 반복
            voices_list = ['alloy', 'nova', 'shimmer']  # 각 반복마다 다른 음성

            for repeat in range(repeat_count):
                current_voice = voices_list[repeat]
                print(f"\n=== {repeat + 1}회차 반복 ({current_voice} 음성) ===")

                for sent_idx in range(len(sentences)):
                    if sent_idx >= len(audio_info):
                        continue

                    # 해당 문장의 이미지
                    img_path = sentence_to_image.get(sent_idx, image_paths[0])

                    # 해당 문장과 번역
                    sentence_text = sentences[sent_idx]
                    translation_text = translations[sent_idx] if translations and sent_idx < len(translations) else ""

                    # 해당 문장의 오디오 duration + 간격 (현재 음성 기준)
                    audio_duration = audio_info[sent_idx]['voices'][current_voice]['duration']
                    clip_duration = audio_duration + pause_duration

                    print(f"  문장 {sent_idx + 1}: {audio_duration:.2f}초 + 간격 {pause_duration}초 = {clip_duration:.2f}초 (시작: {current_time:.2f}초)")

                    # 클립 생성 (타이핑 애니메이션 TTS 동기화)
                    clip = self._create_sentence_clip(
                        image_path=img_path,
                        sentences=[sentence_text],
                        translations=[translation_text] if translation_text else [],
                        duration=clip_duration,
                        start_time=0,
                        tts_duration=audio_duration  # TTS 길이 전달 (타이핑 애니메이션 동기화)
                    )
                    sentence_clips.append(clip)

                    # 오디오 클립 추가 (정확한 시작 시간 설정, 현재 음성 사용)
                    audio_path = audio_info[sent_idx]['voices'][current_voice]['path']
                    audio_clip = AudioFileClip(audio_path).with_start(current_time)
                    audio_clips.append(audio_clip)

                    current_time += clip_duration

            # 아웃트로 생성 (2초)
            outro_clip = self._create_outro_clip(duration=2)

            # 모든 클립 연결
            video_clips = [intro_clip] + sentence_clips + [outro_clip]
            final_video = concatenate_videoclips(video_clips, method="compose")

            # 총 비디오 길이 확인
            sentences_duration = sum(info['voices']['alloy']['duration'] for info in audio_info) * repeat_count + (pause_duration * len(audio_info) * repeat_count)
            total_duration = 3 + sentences_duration + 2
            print(f"\n총 비디오 길이: {total_duration:.2f}초")
            print(f"  - 인트로: 3.00초")
            print(f"  - 문장들: {sentences_duration:.2f}초 (TTS + 간격 포함, {repeat_count}회 반복)")
            print(f"  - 아웃트로: 2.00초")

            # 오디오 클립들을 정확한 시작 시간으로 합성
            from moviepy import CompositeAudioClip
            combined_audio = CompositeAudioClip(audio_clips)

            # 배경 음악 추가 (낮은 볼륨, 인트로 3초에만 재생)
            background_music_path = None
            if self.resource_manager:
                # resources 폴더에서 배경 음악 찾기 (original 파일 우선)
                bg_music_candidates = [
                    os.path.join(str(self.resource_manager.resources_dir), "background_music_original.mp3"),
                    os.path.join(str(self.resource_manager.resources_dir), "background_music.mp3"),
                    os.path.join(str(self.resource_manager.resources_dir), "bgm.mp3"),
                ]
                for path in bg_music_candidates:
                    if os.path.exists(path):
                        background_music_path = path
                        break

            if background_music_path:
                try:
                    print(f"배경 음악 추가: {background_music_path}")
                    bg_music = AudioFileClip(background_music_path)
                    print(f"  - 원본 음악 길이: {bg_music.duration:.2f}초")
                    print(f"  - 비디오 길이: {total_duration:.2f}초")

                    # 볼륨 먼저 낮추기 (5%) - 순서 중요! (볼륨 먼저, 자르기 나중)
                    bg_music = bg_music * 0.05
                    print(f"  - 볼륨 조절 완료: 5%")
                    print(f"  - 볼륨 조절 후 길이: {bg_music.duration:.2f}초")

                    # 인트로 3초만 재생 (볼륨 조정 후 자르기)
                    intro_duration = 3.0
                    if bg_music.duration >= intro_duration:
                        # 원본 파일의 앞 3초만 자르기
                        bg_music = bg_music.subclipped(0, intro_duration)
                        print(f"  - background_music_original.mp3의 앞 {intro_duration:.2f}초만 재생")
                    else:
                        # 3초보다 짧으면 그대로 사용
                        print(f"  - 배경 음악 길이 {bg_music.duration:.2f}초 그대로 사용")

                    print(f"  - 최종 배경음악 길이: {bg_music.duration:.2f}초")

                    # 배경 음악을 시작(0초)에 배치 - 인트로와 동시 재생
                    bg_music = bg_music.with_start(0)

                    # TTS와 배경음악 합성 (배경음악은 인트로 3초에만 재생)
                    # with_duration 제거 - 자동으로 올바른 길이가 설정됨
                    combined_audio = CompositeAudioClip([combined_audio, bg_music])
                    print(f"✓ 배경 음악 추가 완료 (인트로 {intro_duration:.2f}초에만 재생)")
                    print(f"  - 최종 오디오 길이: {combined_audio.duration:.2f}초")
                except Exception as e:
                    print(f"⚠ 배경 음악 추가 실패 (계속 진행): {e}")
                    import traceback
                    traceback.print_exc()

            # 음성 추가 (각 오디오 클립은 이미 정확한 시작 시간이 설정됨)
            final_video = final_video.with_audio(combined_audio)

            # 비디오 저장
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            print(f"[DEBUG] write_videofile 시작 (create_video): {output_path}")

            final_video.write_videofile(
                output_path,
                fps=self.fps,
                codec='libx264',
                audio_codec='aac',
                temp_audiofile='temp-audio.m4a',
                remove_temp=True,
                preset='medium',
                logger='bar',  # 프로그레스 바 표시
                threads=4,     # 멀티스레드 (안정성 향상)
                ffmpeg_params=['-max_muxing_queue_size', '9999']  # 파이프 버퍼 증가 (Broken pipe 방지)
            )

            print(f"[DEBUG] write_videofile 완료")

            # 리소스 정리
            for audio_clip in audio_clips:
                audio_clip.close()
            combined_audio.close()
            final_video.close()

            print(f"✓ 비디오 저장 완료: {output_path}")
            return output_path

        except BrokenPipeError as e:
            print(f"✗ [Errno 32] Broken pipe 발생 - FFmpeg 파이프라인 오류")
            print(f"   원인: MoviePy write_videofile 중 FFmpeg와의 통신 끊김")
            print(f"   해결: 비디오 길이 단축, 메모리 확보, 또는 시스템 리소스 확인")
            raise Exception(f"비디오 저장 중 파이프 오류 발생: {e}")
        except Exception as e:
            print(f"✗ 비디오 생성 실패: {e}")
            import traceback
            traceback.print_exc()
            raise
        finally:
            # 리소스 정리 (에러 발생 시에도 실행)
            try:
                if 'audio_clips' in locals():
                    for audio_clip in audio_clips:
                        if audio_clip:
                            audio_clip.close()
                if 'combined_audio' in locals() and combined_audio:
                    combined_audio.close()
                if 'final_video' in locals() and final_video:
                    final_video.close()
                print("[DEBUG] 리소스 정리 완료")
            except Exception as cleanup_error:
                print(f"[WARNING] 리소스 정리 중 오류: {cleanup_error}")

    def _create_intro_clip(self, duration: float = 3, hook_phrase: str = None) -> VideoClip:
        """
        인트로 클립 생성 (AI 자동 생성 훅 포함)

        Args:
            duration: 인트로 지속 시간
            hook_phrase: AI가 생성한 바이럴 훅 문구 (없으면 기본값)

        Returns:
            인트로 VideoClip
        """
        # 인트로 이미지 우선순위: 커스텀 > Kelly 캐릭터 > 기본 배경
        intro_image_path = None

        # 1. 커스텀 이미지 확인
        if self.intro_custom_image and os.path.exists(self.intro_custom_image):
            print(f"✓ 커스텀 인트로 이미지 사용: {self.intro_custom_image}")
            intro_image_path = self.intro_custom_image
        # 2. Kelly 캐릭터 이미지 로드 (Shorts에서도 Kelly 사용)
        elif self.resource_manager:
            kelly_candidates = [
                os.path.join(str(self.resource_manager.resources_dir), "images", "kelly_casual_hoodie.png"),
                os.path.join(str(self.resource_manager.resources_dir), "images", "kelly_ponytail.png"),
                os.path.join(str(self.resource_manager.resources_dir), "images", "kelly_glasses.png"),
            ]
            for path in kelly_candidates:
                if os.path.exists(path):
                    intro_image_path = path
                    print(f"✓ [Shorts 인트로] Kelly 이미지 로드: {os.path.basename(path)}")
                    break

            if not intro_image_path:
                print("⚠ [Shorts 인트로] Kelly 이미지를 찾을 수 없습니다. 기본 배경을 사용합니다.")

        # 배경 설정
        if intro_image_path and os.path.exists(intro_image_path):
            bg = ImageClip(intro_image_path).with_duration(duration)

            # 디버깅: 이미지 크기 출력
            print(f"📸 인트로 이미지 크기: {bg.w}x{bg.h}")

            # 이미지가 가로 방향이면 90도 회전
            if bg.w > bg.h:
                print(f"⚠ 인트로 이미지가 가로 방향입니다 ({bg.w}x{bg.h}). 90도 회전합니다.")
                bg = bg.rotated(90)
                print(f"✓ 회전 후 크기: {bg.w}x{bg.h}")
            else:
                print(f"✓ 인트로 이미지가 이미 세로 방향입니다")

            bg = bg.resized(height=self.height)
            if bg.w > self.width:
                bg = bg.cropped(x_center=bg.w / 2, width=self.width, height=self.height)
            elif bg.w < self.width:
                bg_fill = ColorClip(size=(self.width, self.height), color=(100, 150, 255)).with_duration(duration)
                bg = CompositeVideoClip([bg_fill, bg.with_position('center')])
        else:
            # 폴백: PIL로 그라데이션 생성 (DALL-E 실패 시)
            print("⚠ DALL-E 이미지 없음. 폴백 그라데이션 생성 중...")
            from PIL import Image
            import numpy as np

            # 그라데이션 이미지 생성
            gradient = Image.new('RGB', (self.width, self.height))
            pixels = gradient.load()

            # 상단 색상 (밝은 하늘색) → 하단 색상 (진한 파스텔 블루)
            top_color = (173, 216, 230)      # Light Blue
            bottom_color = (100, 149, 237)   # Cornflower Blue

            # 그라데이션 생성
            for y in range(self.height):
                # 0.0 (상단) ~ 1.0 (하단)
                ratio = y / self.height

                # 색상 보간
                r = int(top_color[0] * (1 - ratio) + bottom_color[0] * ratio)
                g = int(top_color[1] * (1 - ratio) + bottom_color[1] * ratio)
                b = int(top_color[2] * (1 - ratio) + bottom_color[2] * ratio)

                # 가로줄 전체에 색상 적용
                for x in range(self.width):
                    pixels[x, y] = (r, g, b)

            # PIL Image를 MoviePy ImageClip으로 변환
            gradient_array = np.array(gradient)
            bg = ImageClip(gradient_array).with_duration(duration)
            print("✓ 폴백 그라데이션 배경 생성 완료")

        # 텍스트 (한글 지원 폰트 - 직접 경로 지정)
        korean_font = "/System/Library/Fonts/Supplemental/AppleGothic.ttf"

        # ===== Kelly Cat 추가 여부 결정 =====
        layers = [bg]  # 기본 배경

        if self.use_kelly and self.image_generator:
            # Kelly Cat 인트로 이미지 생성
            try:
                kelly_image_path = self.image_generator.generate_kelly_for_scenario('intro')
                kelly_clip = ImageClip(kelly_image_path).with_duration(duration)

                # Kelly를 하단에 배치 (크기 조절)
                kelly_height = 400  # Kelly 크기
                kelly_clip = kelly_clip.resized(height=kelly_height)
                kelly_y = self.height - kelly_height - 50  # 하단에서 50px 위
                kelly_clip = kelly_clip.with_position(('center', kelly_y))
                kelly_clip = kelly_clip.with_effects([vfx.FadeIn(0.5), vfx.FadeOut(0.5)])

                layers.append(kelly_clip)
                print("✅ Kelly Cat 인트로에 추가됨")

                # Kelly 대사 사용
                intro_text = get_random_intro() if not hook_phrase else hook_phrase
            except Exception as e:
                print(f"⚠ Kelly 이미지 생성 실패: {e}. 기본 인트로 사용")
                intro_text = hook_phrase if hook_phrase else "오늘의 3문장\nDaily English"
        else:
            # Kelly 없이 기본 인트로
            intro_text = hook_phrase if hook_phrase else "오늘의 3문장\nDaily English"

        # ===== 텍스트 박스와 훅 문구 =====
        # 배경 박스 크기: 넓고 충분한 높이 (텍스트가 2-3줄일 수 있음)
        text_bg = ColorClip(
            size=(self.width - 80, 450),  # 너비: 거의 전체, 높이: 넉넉하게
            color=(0, 0, 0),  # 검은색
            duration=duration
        ).with_opacity(0.75).with_position(('center', 300))  # Kelly 위에 배치

        # 훅 텍스트 (배경 박스 위에 배치)
        txt_hook = TextClip(
            text=intro_text,
            font_size=68,  # 폰트 크기 (Kelly와 함께 사용 시 약간 작게)
            color='white',
            font=korean_font,
            size=(self.width - 160, None),  # 박스보다 약간 작게
            method='caption',
            text_align='center',
            stroke_color='#FFD700',  # Gold stroke (브랜딩 색상)
            stroke_width=4,
            margin=(20, 30)
        ).with_position(('center', 350)).with_duration(duration)

        # 페이드 효과
        text_bg = text_bg.with_effects([vfx.FadeIn(0.5), vfx.FadeOut(0.5)])
        txt_hook = txt_hook.with_effects([vfx.FadeIn(0.5), vfx.FadeOut(0.5)])

        # 레이어 추가
        layers.extend([text_bg, txt_hook])

        # 레이어 순서: 배경 → Kelly → 반투명 박스 → 훅 텍스트
        return CompositeVideoClip(layers, size=(self.width, self.height))

    def _calculate_font_size(self, text: str) -> int:
        """
        텍스트 길이에 따라 동적으로 폰트 크기 계산

        Args:
            text: 표시할 텍스트 (영어 + 한글 번역 포함)

        Returns:
            적절한 폰트 크기 (px)
        """
        text_length = len(text)

        # 텍스트 길이별 폰트 크기 (짧은 문장은 크게, 긴 문장은 작게)
        if text_length < 50:
            return 58  # 매우 짧은 문장 → 크게
        elif text_length < 80:
            return 52  # 짧은 문장
        elif text_length < 120:
            return 46  # 보통 길이
        elif text_length < 160:
            return 42  # 긴 문장 (현재 기본값)
        else:
            return 38  # 매우 긴 문장 → 작게 (오버플로우 방지)

    def _create_sentence_clip(
        self,
        image_path: str,
        sentences: list[str],
        translations: list[str],
        duration: float,
        start_time: float = 0,
        tts_duration: float = None,
        format_type: str = "shorts"
    ) -> VideoClip:
        """
        문장 클립 생성

        Args:
            image_path: 배경 이미지 경로
            sentences: 표시할 문장 리스트
            translations: 한글 번역 리스트
            duration: 클립 지속 시간
            start_time: 오디오 시작 시간 (사용하지 않음, 호환성 유지)
            tts_duration: (사용 안 함, 호환성 유지)
            format_type: 비디오 포맷 ("shorts" = 9:16 세로, "longform" = 16:9 가로)

        Returns:
            문장 VideoClip
        """
        # 배경 이미지 (PIL로 먼저 회전 처리)
        from PIL import Image
        import tempfile

        pil_image = Image.open(image_path)
        original_w, original_h = pil_image.size
        print(f"📸 원본 이미지 크기: {original_w}x{original_h} (경로: {image_path.split('/')[-1]})")

        # Shorts 포맷: 이미지가 가로 방향이면 90도 회전 (세로 영상이어야 함)
        # Longform 포맷: 이미지가 세로 방향이면 90도 회전 (가로 영상이어야 함)
        rotated_image_path = image_path  # 기본값: 회전 안 함

        if format_type == "longform":
            # 롱폼은 16:9 가로 포맷 → 세로 이미지를 가로로 회전
            if original_h > original_w:
                print(f"⚠ [롱폼] 이미지가 세로 방향입니다 ({original_w}x{original_h}). 90도 회전합니다.")
                # transpose를 사용하여 정확한 90도 회전 (반시계 방향)
                pil_image = pil_image.transpose(Image.ROTATE_90)  # 90도 반시계 방향 회전
                print(f"✓ 회전 후 크기: {pil_image.size}")

                # 임시 파일로 저장
                with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp:
                    pil_image.save(tmp.name, 'PNG')
                    rotated_image_path = tmp.name
            else:
                print(f"✓ [롱폼] 이미지가 이미 가로 방향입니다 ({original_w}x{original_h})")
        else:
            # Shorts는 9:16 세로 포맷 → 가로 이미지를 세로로 회전
            if original_w > original_h:
                print(f"⚠ [Shorts] 이미지가 가로 방향입니다 ({original_w}x{original_h}). 90도 회전합니다.")
                # transpose를 사용하여 정확한 90도 회전 (반시계 방향)
                pil_image = pil_image.transpose(Image.ROTATE_90)  # 90도 반시계 방향 회전
                print(f"✓ 회전 후 크기: {pil_image.size}")

                # 임시 파일로 저장
                with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp:
                    pil_image.save(tmp.name, 'PNG')
                    rotated_image_path = tmp.name
            else:
                print(f"✓ [Shorts] 이미지가 이미 세로 방향입니다 ({original_w}x{original_h})")

        # MoviePy ImageClip 생성
        img = ImageClip(rotated_image_path).with_duration(duration)
        print(f"📸 MoviePy 클립 크기: {img.w}x{img.h}")

        # 이미지 리사이즈 (포맷에 따라 다르게 처리)
        if format_type == "longform":
            # 롱폼: 16:9 가로 → width 기준 리사이즈
            img = img.resized(width=self.width)
            if img.h > self.height:
                # 높이가 크면 중앙 크롭
                img = img.cropped(
                    y_center=img.h / 2,
                    width=self.width,
                    height=self.height
                )
            elif img.h < self.height:
                # 높이가 작으면 패딩
                bg = ColorClip(
                    size=(self.width, self.height),
                    color=(255, 255, 255)
                ).with_duration(duration)
                img = CompositeVideoClip([bg, img.with_position('center')])
        else:
            # Shorts: 9:16 세로 → height 기준 리사이즈
            img = img.resized(height=self.height)
            if img.w > self.width:
                # 너비가 크면 중앙 크롭
                img = img.cropped(
                    x_center=img.w / 2,
                    width=self.width,
                    height=self.height
                )
            elif img.w < self.width:
                # 너비가 작으면 패딩
                bg = ColorClip(
                    size=(self.width, self.height),
                    color=(255, 255, 255)
                ).with_duration(duration)
                img = CompositeVideoClip([bg, img.with_position('center')])

        # 문장 텍스트 (영어 + 한글 번역)
        text_clips = []

        # 한글 폰트 경로
        korean_font = "/System/Library/Fonts/Supplemental/AppleGothic.ttf"

        # 텍스트 배경 박스 (가독성 향상) - 화면 하단에 작게 배치
        # 포맷에 따라 위치 조정 (Shorts: 1400, Longform: 650)
        txt_bg_y = 650 if format_type == "longform" else 1400
        txt_bg = ColorClip(
            size=(self.width - 80, 350),  # 높이 줄임 (800 → 350)
            color=(0, 0, 0),
            duration=duration
        ).with_opacity(0.7).with_position(('center', txt_bg_y))
        text_clips.append(txt_bg)

        # 상단 타이틀 추가 (브랜딩) - 배경 박스 + 텍스트
        title_bg = ColorClip(
            size=(550, 70),  # 타이틀 크기에 맞게
            color=(0, 0, 0),
            duration=duration
        ).with_opacity(0.75).with_position(('center', 50))
        text_clips.append(title_bg)

        # 타이틀 텍스트 (더 크고 눈에 띄게)
        title = TextClip(
            text="Daily English Mecca",
            font_size=38,  # 크기 증가 (30 → 38)
            color='white',
            font=korean_font,
            stroke_color='#FFD700',  # 금색 외곽선으로 더 눈에 띄게
            stroke_width=2
        ).with_position(('center', 62)).with_duration(duration)
        text_clips.append(title)

        # === 영어 + 한글 텍스트 (간결하고 안정적인 방식) ===

        # 영어와 한글을 함께 표시
        combined_lines = []
        for i, sentence in enumerate(sentences):
            combined_lines.append(sentence)  # 영어 문장
            if translations and i < len(translations):
                combined_lines.append(translations[i])  # 한글 번역
            if i < len(sentences) - 1:  # 마지막 문장이 아니면 빈 줄 추가
                combined_lines.append("")

        combined_text = "\n".join(combined_lines)

        # 동적 폰트 크기 계산
        dynamic_font_size = self._calculate_font_size(combined_text)

        # 텍스트 클립 생성 (강화된 스타일)
        # 포맷에 따라 위치 조정 (Shorts: 1450, Longform: 700)
        txt_y = 700 if format_type == "longform" else 1450
        txt = TextClip(
            text=combined_text,
            font_size=dynamic_font_size,
            color='white',
            font=korean_font,
            size=(self.width - 120, None),
            method='caption',
            text_align='center',
            stroke_color='black',
            stroke_width=4,  # stroke 두껍게 (3 → 4)
            margin=(10, 20)
        ).with_position(('center', txt_y)).with_duration(duration)

        text_clips.append(txt)

        # 모든 요소 합성 (전체 화면 오버레이 제거)
        return CompositeVideoClip(
            [img] + text_clips,
            size=(self.width, self.height)
        )

    def _create_longform_sentence_clip(
        self,
        sentence: str,
        translation: str,
        duration: float,
        kelly_image_path: str = None
    ) -> VideoClip:
        """
        롱폼 비디오용 문장 클립 생성 (Kelly 왼쪽 + 콘텐츠 오른쪽 레이아웃)

        레이아웃:
        ┌──────────┬───────────────────────┐
        │  Kelly   │   English Sentence    │
        │  (640px) │   한글 번역            │
        │          │   (1280px)            │
        └──────────┴───────────────────────┘

        Args:
            sentence: 영어 문장
            translation: 한글 번역
            duration: 클립 지속 시간
            kelly_image_path: Kelly 캐릭터 이미지 경로

        Returns:
            문장 VideoClip
        """
        korean_font = "/System/Library/Fonts/Supplemental/AppleGothic.ttf"
        layers = []

        # 1. 배경 (파스텔 블루)
        bg = ColorClip(
            size=(self.width, self.height),
            color=(220, 235, 255),  # 연한 파스텔 블루
            duration=duration
        )
        layers.append(bg)

        # 2. Kelly 영역 (왼쪽 1/3, 더 진한 파스텔)
        kelly_bg = ColorClip(
            size=(self.kelly_width, self.height),
            color=(200, 220, 255),  # 더 진한 파스텔 블루
            duration=duration
        ).with_position((0, 0))
        layers.append(kelly_bg)

        # 3. Kelly 캐릭터 이미지 (왼쪽 영역에 배치)
        if kelly_image_path and os.path.exists(kelly_image_path):
            kelly_clip = ImageClip(kelly_image_path).with_duration(duration)

            # Kelly 이미지를 왼쪽 영역에 맞게 리사이즈 (비율 유지)
            kelly_clip = kelly_clip.resized(height=self.height * 0.8)  # 80% 높이

            # Kelly를 왼쪽 영역 중앙에 배치
            kelly_x = (self.kelly_width - kelly_clip.w) // 2
            kelly_y = (self.height - kelly_clip.h) // 2
            kelly_clip = kelly_clip.with_position((kelly_x, kelly_y))

            # 페이드 효과
            kelly_clip = kelly_clip.with_effects([vfx.FadeIn(0.3), vfx.FadeOut(0.3)])

            layers.append(kelly_clip)
        else:
            print(f"⚠️ Kelly 이미지 없음, 기본 배경만 사용")

        # 4. 구분선 (Kelly 영역과 콘텐츠 영역 사이)
        divider = ColorClip(
            size=(4, self.height),  # 4px 두께
            color=(100, 150, 200),  # 진한 블루
            duration=duration
        ).with_position((self.kelly_width, 0))
        layers.append(divider)

        # 5. 영어 문장 (오른쪽 영역 상단)
        sentence_txt = TextClip(
            text=sentence,
            font_size=60,
            color='#2C3E50',  # 진한 네이비
            font=korean_font,
            size=(self.content_width - 100, None),  # 좌우 여백 50px씩
            method='caption',
            text_align='center',
            stroke_color='white',
            stroke_width=3,
            margin=(10, 20)
        ).with_position((self.kelly_width + 50, 300)).with_duration(duration)  # y=300 (상단)

        layers.append(sentence_txt)

        # 6. 한글 번역 (오른쪽 영역 하단)
        translation_txt = TextClip(
            text=translation,
            font_size=45,
            color='#7F8C8D',  # 회색
            font=korean_font,
            size=(self.content_width - 100, None),
            method='caption',
            text_align='center',
            stroke_color='white',
            stroke_width=2,
            margin=(10, 20)
        ).with_position((self.kelly_width + 50, 600)).with_duration(duration)  # y=600 (하단)

        layers.append(translation_txt)

        # 7. 모든 레이어 합성
        return CompositeVideoClip(layers, size=(self.width, self.height))

    def _create_outro_clip(self, duration: float = 2) -> VideoClip:
        """
        아웃트로 클립 생성 (구독 유도)

        Args:
            duration: 아웃트로 지속 시간

        Returns:
            아웃트로 VideoClip
        """
        # 아웃트로 이미지 우선순위: 커스텀 > Kelly 캐릭터 > 기본 배경
        outro_image_path = None

        # 1. 커스텀 이미지 확인
        if self.outro_custom_image and os.path.exists(self.outro_custom_image):
            print(f"✓ 커스텀 아웃트로 이미지 사용: {self.outro_custom_image}")
            outro_image_path = self.outro_custom_image
        # 2. Kelly 캐릭터 이미지 로드 (Shorts에서도 Kelly 사용)
        elif self.resource_manager:
            kelly_candidates = [
                os.path.join(str(self.resource_manager.resources_dir), "images", "kelly_casual_hoodie.png"),
                os.path.join(str(self.resource_manager.resources_dir), "images", "kelly_ponytail.png"),
                os.path.join(str(self.resource_manager.resources_dir), "images", "kelly_glasses.png"),
            ]
            for path in kelly_candidates:
                if os.path.exists(path):
                    outro_image_path = path
                    print(f"✓ [Shorts 아웃트로] Kelly 이미지 로드: {os.path.basename(path)}")
                    break

            if not outro_image_path:
                print("⚠ [Shorts 아웃트로] Kelly 이미지를 찾을 수 없습니다. 기본 배경을 사용합니다.")

        # 배경 설정
        if outro_image_path and os.path.exists(outro_image_path):
            bg = ImageClip(outro_image_path).with_duration(duration)

            # 디버깅: 이미지 크기 출력
            print(f"📸 아웃트로 이미지 크기: {bg.w}x{bg.h}")

            # 이미지가 가로 방향이면 90도 회전
            if bg.w > bg.h:
                print(f"⚠ 아웃트로 이미지가 가로 방향입니다 ({bg.w}x{bg.h}). 90도 회전합니다.")
                bg = bg.rotated(90)
                print(f"✓ 회전 후 크기: {bg.w}x{bg.h}")
            else:
                print(f"✓ 아웃트로 이미지가 이미 세로 방향입니다")

            bg = bg.resized(height=self.height)
            if bg.w > self.width:
                bg = bg.cropped(x_center=bg.w / 2, width=self.width, height=self.height)
            elif bg.w < self.width:
                bg_fill = ColorClip(size=(self.width, self.height), color=(255, 150, 180)).with_duration(duration)
                bg = CompositeVideoClip([bg_fill, bg.with_position('center')])
        else:
            # 기본 배경색 (파스텔 핑크)
            bg = ColorClip(
                size=(self.width, self.height),
                color=(255, 150, 180),
                duration=duration
            )

        # 한글 폰트 직접 경로 지정
        korean_font = "/System/Library/Fonts/Supplemental/AppleGothic.ttf"

        # ===== Kelly Cat 추가 여부 결정 =====
        layers = [bg]  # 기본 배경

        if self.use_kelly and self.image_generator:
            # Kelly Cat 아웃트로 이미지 생성
            try:
                kelly_image_path = self.image_generator.generate_kelly_for_scenario('outro')
                kelly_clip = ImageClip(kelly_image_path).with_duration(duration)

                # Kelly를 하단에 배치
                kelly_height = 450
                kelly_clip = kelly_clip.resized(height=kelly_height)
                kelly_y = self.height - kelly_height - 50
                kelly_clip = kelly_clip.with_position(('center', kelly_y))
                kelly_clip = kelly_clip.with_effects([vfx.FadeIn(0.3)])

                layers.append(kelly_clip)
                print("✅ Kelly Cat 아웃트로에 추가됨")

                # Kelly 대사 사용
                outro_message = get_random_outro()
            except Exception as e:
                print(f"⚠ Kelly 이미지 생성 실패: {e}. 기본 아웃트로 사용")
                outro_message = "댓글에 오늘 배운 문장 써보세요!"
        else:
            outro_message = "댓글에 오늘 배운 문장 써보세요!"

        # ===== 텍스트 레이어 =====
        # 브랜딩 텍스트 (상단)
        branding_text = TextClip(
            text="Daily English Mecca",
            font_size=54,
            color='#FFD700',
            font=korean_font,
            stroke_color='white',
            stroke_width=3,
            text_align='center'
        ).with_position(('center', 300)).with_duration(duration)

        # 메인 CTA (중앙)
        main_txt = TextClip(
            text="좋아요 & 구독하기!",
            font_size=58,
            color='white',
            font=korean_font,
            size=(self.width - 120, None),
            method='caption',
            text_align='center',
            stroke_color='#FFD700',
            stroke_width=4,
            margin=(10, 20)
        ).with_position(('center', 450)).with_duration(duration)

        # Kelly 대사 또는 기본 메시지
        sub_txt = TextClip(
            text=outro_message,
            font_size=40,
            color='white',
            font=korean_font,
            size=(self.width - 100, None),
            method='caption',
            text_align='center',
            stroke_color='black',
            stroke_width=2,
            margin=(10, 20)
        ).with_position(('center', 650)).with_duration(duration)

        # 페이드 효과
        branding_text = branding_text.with_effects([vfx.FadeIn(0.3)])
        main_txt = main_txt.with_effects([vfx.FadeIn(0.3)])
        sub_txt = sub_txt.with_effects([vfx.FadeIn(0.5)])

        # 레이어 추가
        layers.extend([branding_text, main_txt, sub_txt])

        # 레이어 순서: 배경 → Kelly → 브랜딩 → CTA → 메시지
        return CompositeVideoClip(
            layers,
            size=(self.width, self.height)
        )

    def _create_longform_intro_clip(self, duration: float = 5, kelly_image_path: str = None) -> VideoClip:
        """
        롱폼 비디오용 인트로 클립 생성

        Args:
            duration: 인트로 지속 시간
            kelly_image_path: Kelly 이미지 경로

        Returns:
            인트로 VideoClip
        """
        korean_font = "/System/Library/Fonts/Supplemental/AppleGothic.ttf"
        layers = []

        # 1. 배경 (그라데이션 효과를 위한 파스텔 블루)
        bg = ColorClip(
            size=(self.width, self.height),
            color=(180, 210, 255),  # 파스텔 블루
            duration=duration
        )
        layers.append(bg)

        # 2. Kelly 캐릭터 (전체 화면 배경)
        if kelly_image_path and os.path.exists(kelly_image_path):
            kelly_clip = ImageClip(kelly_image_path).with_duration(duration)
            # 전체 화면 크기로 리사이즈 (16:9 비율에 맞춤)
            kelly_clip = kelly_clip.resized(height=self.height)
            # 가로가 부족하면 가로 기준으로 리사이즈
            if kelly_clip.w < self.width:
                kelly_clip = kelly_clip.resized(width=self.width)

            # 중앙 정렬
            kelly_clip = kelly_clip.with_position('center')
            kelly_clip = kelly_clip.with_effects([vfx.FadeIn(0.5)])

            # 배경으로 먼저 추가 (bg 다음, 텍스트 이전)
            layers.append(kelly_clip)

        # 3. 타이틀 (중앙)
        title_txt = TextClip(
            text="Daily English Mecca",
            font_size=80,
            color='white',
            font=korean_font,
            size=(1200, None),
            method='caption',
            text_align='center',
            stroke_color='#2C3E50',
            stroke_width=6,
            margin=(10, 20)
        ).with_position(('center', 300)).with_duration(duration)

        layers.append(title_txt)

        # 4. 서브타이틀 (오늘의 학습)
        subtitle_txt = TextClip(
            text="Today's 3 Expressions",
            font_size=50,
            color='#FFD700',  # 골드
            font=korean_font,
            size=(1000, None),
            method='caption',
            text_align='center',
            stroke_color='black',
            stroke_width=3,
            margin=(10, 20)
        ).with_position(('center', 500)).with_duration(duration)

        layers.append(subtitle_txt)

        # 5. 페이드 효과
        title_txt = title_txt.with_effects([vfx.FadeIn(0.8)])
        subtitle_txt = subtitle_txt.with_effects([vfx.FadeIn(1.0)])

        # 6. 배경 음악 추가
        intro_video = CompositeVideoClip(layers, size=(self.width, self.height))

        # 배경 음악 찾기 및 추가
        background_music_path = None
        if self.resource_manager:
            bg_music_candidates = [
                os.path.join(str(self.resource_manager.resources_dir), "background_music_original.mp3"),
                os.path.join(str(self.resource_manager.resources_dir), "background_music.mp3"),
            ]
            for path in bg_music_candidates:
                if os.path.exists(path):
                    background_music_path = path
                    break

        if background_music_path:
            try:
                print(f"[인트로] 배경 음악 추가: {background_music_path}")
                bg_music = AudioFileClip(background_music_path)
                # 볼륨 10% (인트로는 음성 없어서 조금 더 크게)
                bg_music = bg_music * 0.10
                # 인트로 길이만큼 자르기
                if bg_music.duration >= duration:
                    bg_music = bg_music.subclipped(0, duration)
                bg_music = bg_music.with_start(0)

                # 비디오에 오디오 추가
                intro_video = intro_video.with_audio(bg_music)
                print(f"  - 배경 음악 {duration:.2f}초 추가 완료 (볼륨 10%)")
            except Exception as e:
                print(f"⚠ 배경 음악 추가 실패: {e}")

        return intro_video

    def _create_longform_outro_clip(self, duration: float = 5, kelly_image_path: str = None) -> VideoClip:
        """
        롱폼 비디오용 아웃트로 클립 생성

        Args:
            duration: 아웃트로 지속 시간
            kelly_image_path: Kelly 이미지 경로

        Returns:
            아웃트로 VideoClip
        """
        korean_font = "/System/Library/Fonts/Supplemental/AppleGothic.ttf"
        layers = []

        # 1. 배경 (파스텔 핑크)
        bg = ColorClip(
            size=(self.width, self.height),
            color=(255, 200, 220),  # 파스텔 핑크
            duration=duration
        )
        layers.append(bg)

        # 2. Kelly 캐릭터 (전체 화면 배경)
        if kelly_image_path and os.path.exists(kelly_image_path):
            kelly_clip = ImageClip(kelly_image_path).with_duration(duration)
            # 전체 화면 크기로 리사이즈 (16:9 비율에 맞춤)
            kelly_clip = kelly_clip.resized(height=self.height)
            # 가로가 부족하면 가로 기준으로 리사이즈
            if kelly_clip.w < self.width:
                kelly_clip = kelly_clip.resized(width=self.width)

            # 중앙 정렬
            kelly_clip = kelly_clip.with_position('center')
            kelly_clip = kelly_clip.with_effects([vfx.FadeIn(0.3)])

            # 배경으로 먼저 추가 (bg 다음, 텍스트 이전)
            layers.append(kelly_clip)

        # 3. 메인 CTA (중앙)
        main_txt = TextClip(
            text="좋아요 & 구독 & 알림설정!",
            font_size=70,
            color='white',
            font=korean_font,
            size=(1200, None),
            method='caption',
            text_align='center',
            stroke_color='#E74C3C',  # 빨간색
            stroke_width=5,
            margin=(10, 20)
        ).with_position(('center', 300)).with_duration(duration)

        layers.append(main_txt)

        # 4. 서브 메시지 (중앙)
        sub_txt = TextClip(
            text="댓글에 오늘 배운 표현 써보세요!",
            font_size=45,
            color='#FFD700',  # 골드
            font=korean_font,
            size=(1000, None),
            method='caption',
            text_align='center',
            stroke_color='black',
            stroke_width=3,
            margin=(10, 20)
        ).with_position(('center', 500)).with_duration(duration)

        layers.append(sub_txt)

        # 5. 페이드 효과
        main_txt = main_txt.with_effects([vfx.FadeIn(0.5)])
        sub_txt = sub_txt.with_effects([vfx.FadeIn(0.8)])

        return CompositeVideoClip(layers, size=(self.width, self.height))

    def create_quiz_video(
        self,
        quiz_data: dict,
        audio_info: list[dict],
        output_path: str
    ) -> str:
        """
        퀴즈 챌린지 전용 비디오 생성

        Args:
            quiz_data: 퀴즈 데이터
                {
                    'question': '문제 질문',
                    'option_a': '선택지 A',
                    'option_b': '선택지 B',
                    'correct_answer': 'A' or 'B',
                    'explanation': '해설',
                    'examples': ['예문1', '예문2', '예문3']
                }
            audio_info: 각 항목별 오디오 정보 (8개)
            output_path: 비디오 저장 경로

        Returns:
            생성된 비디오 파일 경로
        """
        try:
            print("퀴즈 비디오 생성 중...")

            # === 1. 인트로 (3초): Daily English Mecca ===
            intro_clip = self._create_intro_clip(duration=3, hook_phrase="한국인 95% 틀리는 문제!")

            # 실제 TTS 길이를 사용하여 클립 duration 계산
            # 각 장면 사이에 2초 간격 추가 (사용자 생각 시간)
            pause_between_scenes = 2.0  # 장면 전환 간격 (일반 장면용)

            # 질문 (한글) + 선택지 (영어) = 첫 2개 TTS
            question_tts_duration = audio_info[0]['voices']['alloy']['duration'] + audio_info[1]['voices']['alloy']['duration']
            question_duration = question_tts_duration  # TTS만 (pause 제거, 카운트다운 클립이 대신 함)

            # === 2. 문제 제시 (실제 TTS 길이만, pause 없음) ===
            question_clip_obj = QuestionClip()
            question_clip = question_clip_obj.create(
                question=quiz_data['question'],
                option_a=quiz_data['option_a'],
                option_b=quiz_data['option_b'],
                duration=question_duration
            )

            # === 2-1. 카운트다운 클립 (3초 대기, 3-2-1 애니메이션) ===
            countdown_clip_obj = CountdownClip()
            countdown_clip = countdown_clip_obj.create(
                question=quiz_data['question'],
                option_a=quiz_data['option_a'],
                option_b=quiz_data['option_b'],
                duration=3.0  # 고정 3초
            )

            # === 3. 정답 공개 (실제 TTS 길이 + 간격) ===
            answer_tts_duration = audio_info[2]['voices']['alloy']['duration']
            answer_duration = answer_tts_duration + pause_between_scenes
            answer_clip_obj = AnswerClip()
            answer_clip = answer_clip_obj.create(
                answer=quiz_data['correct_answer'],
                correct_option=quiz_data['option_a'] if quiz_data['correct_answer'] == 'A' else quiz_data['option_b'],
                duration=answer_duration
            )

            # === 4. 해설 (실제 TTS 길이 + 간격) ===
            explanation_tts_duration = audio_info[3]['voices']['alloy']['duration']
            explanation_duration = explanation_tts_duration + pause_between_scenes
            explanation_clip_obj = ExplanationClip()
            explanation_clip = explanation_clip_obj.create(
                explanation=quiz_data['explanation'],
                duration=explanation_duration
            )

            # === 5. 예문들 (실제 TTS 길이 + 간격) ===
            example_clips = []
            for i, example in enumerate(quiz_data['examples']):
                example_tts_duration = audio_info[4 + i]['voices']['alloy']['duration']  # 예문은 index 4부터
                example_duration = example_tts_duration + pause_between_scenes
                example_clip_obj = ExampleClip()
                example_clip = example_clip_obj.create(
                    example=example,
                    index=i + 1,
                    duration=example_duration
                )
                example_clips.append(example_clip)

            # === 6. 아웃트로 (3초): CTA ===
            outro_clip = self._create_quiz_outro_clip(duration=3)

            # === 모든 클립 연결 ===
            # 순서: 인트로 → 문제 → 카운트다운(3-2-1) → 정답 → 해설 → 예문들 → 아웃트로
            all_clips = [intro_clip, question_clip, countdown_clip, answer_clip, explanation_clip] + example_clips + [outro_clip]
            final_video = concatenate_videoclips(all_clips, method="compose")

            # === 오디오 추가 (TTS 음성) ===
            audio_clips = []
            current_time = 3.0  # 인트로 3초 후부터 시작

            # 실제 TTS 길이를 사용하여 정확한 타이밍 계산
            for i in range(7):  # 질문, 선택지, 정답, 해설, 예문3개 (총 7개, 인트로/아웃트로 제외)
                if i >= len(audio_info):
                    break

                # 첫 번째 음성 사용 (alloy)
                audio_path = audio_info[i]['voices']['alloy']['path']
                actual_duration = audio_info[i]['voices']['alloy']['duration']

                audio_clip = AudioFileClip(audio_path).with_start(current_time)
                audio_clips.append(audio_clip)

                print(f"  TTS {i+1}: {actual_duration:.2f}초 (시작: {current_time:.2f}초)")

                # 타이밍 계산
                if i == 1:
                    # 선택지 TTS 후: 카운트다운 3초 대기
                    current_time += actual_duration + 3.0
                    print(f"  → 카운트다운 3초 대기 (다음 시작: {current_time:.2f}초)")
                else:
                    # 나머지: TTS + pause
                    current_time += actual_duration + pause_between_scenes

            # 오디오 합성
            from moviepy import CompositeAudioClip
            combined_audio = CompositeAudioClip(audio_clips)

            # 배경 음악 추가 (인트로 3초에만)
            background_music_path = None
            if self.resource_manager:
                bg_music_candidates = [
                    os.path.join(str(self.resource_manager.resources_dir), "background_music_original.mp3"),
                    os.path.join(str(self.resource_manager.resources_dir), "background_music.mp3"),
                ]
                for path in bg_music_candidates:
                    if os.path.exists(path):
                        background_music_path = path
                        break

            if background_music_path:
                try:
                    print(f"배경 음악 추가: {background_music_path}")
                    bg_music = AudioFileClip(background_music_path)
                    bg_music = bg_music * 0.05  # 볼륨 5%
                    bg_music = bg_music.subclipped(0, 3.0)  # 인트로 3초만
                    bg_music = bg_music.with_start(0)
                    combined_audio = CompositeAudioClip([combined_audio, bg_music])
                except Exception as e:
                    print(f"⚠ 배경 음악 추가 실패: {e}")

            # 비디오에 오디오 추가
            final_video = final_video.with_audio(combined_audio)

            # 비디오 저장
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            print(f"[DEBUG] write_videofile 시작 (create_quiz_video): {output_path}")

            final_video.write_videofile(
                output_path,
                fps=self.fps,
                codec='libx264',
                logger='bar',  # 프로그레스 바 표시
                threads=4,     # 멀티스레드 (안정성 향상)
                ffmpeg_params=['-max_muxing_queue_size', '9999'],  # 파이프 버퍼 증가 (Broken pipe 방지)
                audio_codec='aac',
                temp_audiofile='temp-audio.m4a',
                remove_temp=True,
                preset='medium'
            )

            print(f"[DEBUG] write_videofile 완료")

            # 리소스 정리
            for audio_clip in audio_clips:
                audio_clip.close()
            combined_audio.close()
            final_video.close()

            print(f"✓ 퀴즈 비디오 저장 완료: {output_path}")
            return output_path

        except BrokenPipeError as e:
            print(f"✗ [Errno 32] Broken pipe 발생 - FFmpeg 파이프라인 오류")
            print(f"   원인: MoviePy write_videofile 중 FFmpeg와의 통신 끊김")
            print(f"   해결: 비디오 길이 단축, 메모리 확보, 또는 시스템 리소스 확인")
            raise Exception(f"퀴즈 비디오 저장 중 파이프 오류 발생: {e}")
        except Exception as e:
            print(f"✗ 퀴즈 비디오 생성 실패: {e}")
            import traceback
            traceback.print_exc()
            raise
        finally:
            # 리소스 정리 (에러 발생 시에도 실행)
            try:
                if 'audio_clips' in locals():
                    for audio_clip in audio_clips:
                        if audio_clip:
                            audio_clip.close()
                if 'combined_audio' in locals() and combined_audio:
                    combined_audio.close()
                if 'final_video' in locals() and final_video:
                    final_video.close()
                print("[DEBUG] 리소스 정리 완료 (퀴즈)")
            except Exception as cleanup_error:
                print(f"[WARNING] 리소스 정리 중 오류 (퀴즈): {cleanup_error}")

    def _create_quiz_question_clip(self, question: str, option_a: str, option_b: str, duration: float) -> VideoClip:
        """문제 제시 클립 (TTS 재생만, pause 제외)"""
        # 파스텔 블루 배경
        bg = ColorClip(size=(self.width, self.height), color=(100, 150, 255), duration=duration)

        korean_font = "/System/Library/Fonts/Supplemental/AppleGothic.ttf"

        # 질문
        question_txt = TextClip(
            text=question,
            font_size=48,
            color='white',
            font=korean_font,
            size=(self.width - 120, None),
            method='caption',
            text_align='center',
            stroke_color='black',
            stroke_width=3,
            margin=(10, 20)
        ).with_position(('center', 550)).with_duration(duration)

        # 선택지 A
        option_a_txt = TextClip(
            text=f"A) {option_a}",
            font_size=42,
            color='white',
            font=korean_font,
            size=(self.width - 160, None),
            method='caption',
            text_align='left',
            stroke_color='black',
            stroke_width=2,
            margin=(10, 20)
        ).with_position((80, 850)).with_duration(duration)

        # 선택지 B
        option_b_txt = TextClip(
            text=f"B) {option_b}",
            font_size=42,
            color='white',
            font=korean_font,
            size=(self.width - 160, None),
            method='caption',
            text_align='left',
            stroke_color='black',
            stroke_width=2,
            margin=(10, 20)
        ).with_position((80, 1050)).with_duration(duration)

        return CompositeVideoClip([bg, question_txt, option_a_txt, option_b_txt], size=(self.width, self.height))

    def _create_quiz_countdown_clip(self, question: str, option_a: str, option_b: str, duration: float = 3.0) -> VideoClip:
        """퀴즈 문제 카운트다운 클립 (3-2-1 애니메이션)"""
        # 파스텔 블루 배경 (문제 클립과 동일)
        bg = ColorClip(size=(self.width, self.height), color=(100, 150, 255), duration=duration)

        korean_font = "/System/Library/Fonts/Supplemental/AppleGothic.ttf"

        # 질문 (작게 표시 - 상단)
        question_txt = TextClip(
            text=question,
            font_size=36,
            color='white',
            font=korean_font,
            size=(self.width - 120, None),
            method='caption',
            text_align='center',
            stroke_color='black',
            stroke_width=2,
            margin=(10, 20)
        ).with_position(('center', 300)).with_duration(duration)  # 400 → 300 (위로 이동)

        # 선택지 A (작게)
        option_a_txt = TextClip(
            text=f"A) {option_a}",
            font_size=32,
            color='white',
            font=korean_font,
            size=(self.width - 160, None),
            method='caption',
            text_align='left',
            stroke_color='black',
            stroke_width=2,
            margin=(10, 20)
        ).with_position((80, 550)).with_duration(duration)  # 700 → 550 (위로 이동)

        # 선택지 B (작게)
        option_b_txt = TextClip(
            text=f"B) {option_b}",
            font_size=32,
            color='white',
            font=korean_font,
            size=(self.width - 160, None),
            method='caption',
            text_align='left',
            stroke_color='black',
            stroke_width=2,
            margin=(10, 20)
        ).with_position((80, 680)).with_duration(duration)  # 850 → 680 (위로 이동)

        # 카운트다운 숫자들 (각 1초씩 표시)
        countdown_clips = []

        # 3 (0~1초)
        countdown_3 = TextClip(
            text="3",
            font_size=200,
            color='#FFD700',
            font=korean_font,
            stroke_color='black',
            stroke_width=8,
            margin=(20, 30)
        ).with_position(('center', 1100)).with_duration(1.0).with_effects([vfx.FadeIn(0.1), vfx.FadeOut(0.2)])
        countdown_clips.append(countdown_3)

        # 2 (1~2초)
        countdown_2 = TextClip(
            text="2",
            font_size=200,
            color='#FFD700',
            font=korean_font,
            stroke_color='black',
            stroke_width=8,
            margin=(20, 30)
        ).with_position(('center', 1100)).with_start(1.0).with_duration(1.0).with_effects([vfx.FadeIn(0.1), vfx.FadeOut(0.2)])
        countdown_clips.append(countdown_2)

        # 1 (2~3초)
        countdown_1 = TextClip(
            text="1",
            font_size=200,
            color='#FFD700',
            font=korean_font,
            stroke_color='black',
            stroke_width=8,
            margin=(20, 30)
        ).with_position(('center', 1100)).with_start(2.0).with_duration(1.0).with_effects([vfx.FadeIn(0.1), vfx.FadeOut(0.2)])
        countdown_clips.append(countdown_1)

        return CompositeVideoClip([bg, question_txt, option_a_txt, option_b_txt] + countdown_clips, size=(self.width, self.height))

    def _create_quiz_answer_clip(self, correct_answer: str, correct_option: str, duration: float) -> VideoClip:
        """정답 공개 클립"""
        # 파스텔 그린 배경
        bg = ColorClip(size=(self.width, self.height), color=(100, 200, 100), duration=duration)

        korean_font = "/System/Library/Fonts/Supplemental/AppleGothic.ttf"

        # "정답은..." (작게)
        title_txt = TextClip(
            text="정답은...",
            font_size=45,
            color='white',
            font=korean_font,
            stroke_color='black',
            stroke_width=2,
            margin=(10, 20)  # 여백 추가로 한글 깨짐 방지
        ).with_position(('center', 550)).with_duration(duration)  # 위로 조정 (600 → 550)

        # 정답 (크게)
        answer_txt = TextClip(
            text=f"{correct_answer}!",
            font_size=120,
            color='#FFD700',
            font=korean_font,
            stroke_color='black',
            stroke_width=5,
            margin=(20, 30)  # 여백 추가로 큰 텍스트 깨짐 방지
        ).with_position(('center', 750)).with_duration(duration)

        # 정답 문장
        option_txt = TextClip(
            text=correct_option,
            font_size=40,
            color='white',
            font=korean_font,
            size=(self.width - 120, None),
            method='caption',
            text_align='center',
            stroke_color='black',
            stroke_width=2,
            margin=(10, 20)  # 여백 추가로 한글 깨짐 방지
        ).with_position(('center', 950)).with_duration(duration)  # 위로 조정 (1000 → 950)

        # 페이드 효과
        answer_txt = answer_txt.with_effects([vfx.FadeIn(0.5)])

        return CompositeVideoClip([bg, title_txt, answer_txt, option_txt], size=(self.width, self.height))

    def _create_quiz_explanation_clip(self, explanation: str, duration: float) -> VideoClip:
        """해설 클립"""
        # 파스텔 옐로우 배경
        bg = ColorClip(size=(self.width, self.height), color=(255, 220, 100), duration=duration)

        korean_font = "/System/Library/Fonts/Supplemental/AppleGothic.ttf"

        # "해설" 타이틀
        title_txt = TextClip(
            text="📚 해설",
            font_size=45,
            color='white',
            font=korean_font,
            stroke_color='black',
            stroke_width=3,
            margin=(10, 20)  # 여백 추가로 한글 깨짐 방지
        ).with_position(('center', 450)).with_duration(duration)  # 위로 조정 (500 → 450)

        # 해설 내용
        explanation_txt = TextClip(
            text=explanation,
            font_size=38,
            color='black',
            font=korean_font,
            size=(self.width - 120, None),
            method='caption',
            text_align='center',
            margin=(10, 20)  # 여백 추가로 한글 깨짐 방지
        ).with_position(('center', 750)).with_duration(duration)  # 위로 조정 (800 → 750)

        return CompositeVideoClip([bg, title_txt, explanation_txt], size=(self.width, self.height))

    def _create_quiz_example_clip(self, example: str, index: int, duration: float) -> VideoClip:
        """예문 클립"""
        # 파스텔 퍼플 배경
        bg = ColorClip(size=(self.width, self.height), color=(180, 150, 255), duration=duration)

        korean_font = "/System/Library/Fonts/Supplemental/AppleGothic.ttf"

        # "예문 N" 타이틀
        title_txt = TextClip(
            text=f"예문 {index}",
            font_size=40,
            color='white',
            font=korean_font,
            stroke_color='black',
            stroke_width=2,
            margin=(10, 20)  # 여백 추가로 한글 깨짐 방지
        ).with_position(('center', 450)).with_duration(duration)  # 위로 조정 (550 → 450)

        # "예문을 말해볼게요!" 안내 텍스트
        guide_txt = TextClip(
            text="예문을 말해볼게요!",
            font_size=32,
            color='#FFD700',
            font=korean_font,
            stroke_color='black',
            stroke_width=2,
            margin=(10, 20)
        ).with_position(('center', 600)).with_duration(duration)

        # 예문 내용
        example_txt = TextClip(
            text=example,
            font_size=48,
            color='white',
            font=korean_font,
            size=(self.width - 120, None),
            method='caption',
            text_align='center',
            stroke_color='black',
            stroke_width=3,
            margin=(10, 20)  # 여백 추가로 한글 깨짐 방지
        ).with_position(('center', 900)).with_duration(duration)  # 아래로 조정 (850 → 900)

        return CompositeVideoClip([bg, title_txt, guide_txt, example_txt], size=(self.width, self.height))

    def _create_quiz_outro_clip(self, duration: float) -> VideoClip:
        """퀴즈 아웃트로 (CTA)"""
        # 아웃트로 이미지 우선순위: 커스텀 > 캐시 > 생성 > 기본 배경
        outro_image_path = None

        # 1. 커스텀 이미지 확인
        if self.outro_custom_image and os.path.exists(self.outro_custom_image):
            print(f"✓ 커스텀 아웃트로 이미지 사용: {self.outro_custom_image}")
            outro_image_path = self.outro_custom_image
        # 2. 캐시된 템플릿 이미지 확인
        elif self.image_generator and self.resource_manager:
            outro_prompt = """A simple geometric abstract background with warm pink coral gradient.
Modern minimalist design with soft shapes and clean composition.
Vertical 9:16 format. Friendly and inviting mood.
Simple flat design with pastel colors."""

            # 캐시 확인
            cached_outro = self.resource_manager.get_image_path("outro_template")
            if self.resource_manager.image_exists("outro_template"):
                print("✓ 캐시된 아웃트로 이미지 사용")
                outro_image_path = cached_outro
            else:
                try:
                    print("아웃트로 이미지 생성 중...")
                    outro_image_path = self.image_generator.generate_image(
                        outro_prompt,
                        cached_outro,
                        size="1024x1792"
                    )
                except Exception as e:
                    print(f"⚠ 아웃트로 이미지 생성 실패 (기본 배경 사용): {e}")
                    outro_image_path = None

        # 배경 설정
        if outro_image_path and os.path.exists(outro_image_path):
            bg = ImageClip(outro_image_path).with_duration(duration)

            # 디버깅: 이미지 크기 출력
            print(f"📸 아웃트로 이미지 크기: {bg.w}x{bg.h}")

            # 이미지가 가로 방향이면 90도 회전
            if bg.w > bg.h:
                print(f"⚠ 아웃트로 이미지가 가로 방향입니다 ({bg.w}x{bg.h}). 90도 회전합니다.")
                bg = bg.rotated(90)
                print(f"✓ 회전 후 크기: {bg.w}x{bg.h}")
            else:
                print(f"✓ 아웃트로 이미지가 이미 세로 방향입니다")

            bg = bg.resized(height=self.height)
            if bg.w > self.width:
                bg = bg.cropped(x_center=bg.w / 2, width=self.width, height=self.height)
            elif bg.w < self.width:
                bg_fill = ColorClip(size=(self.width, self.height), color=(255, 150, 180)).with_duration(duration)
                bg = CompositeVideoClip([bg_fill, bg.with_position('center')])
        else:
            # 기본 배경색 (파스텔 핑크)
            bg = ColorClip(
                size=(self.width, self.height),
                color=(255, 150, 180),
                duration=duration
            )

        korean_font = "/System/Library/Fonts/Supplemental/AppleGothic.ttf"

        # ===== 개선: "Daily English Mecca" 브랜딩 추가 (최상단) =====
        branding_text = TextClip(
            text="Daily English Mecca",
            font_size=52,  # 큰 폰트
            color='#FFD700',  # Gold 색상 (메인 브랜딩)
            font=korean_font,
            stroke_color='white',  # 흰색 외곽선
            stroke_width=3,
            text_align='center'
        ).with_position(('center', 550)).with_duration(duration)  # 최상단에 배치

        # 텍스트 배경 박스 추가 (가독성 향상)
        text_bg = ColorClip(
            size=(self.width - 100, 550),  # 높이 증가 (500 → 550)
            color=(0, 0, 0),
            duration=duration
        ).with_opacity(0.7).with_position(('center', 650))  # 아래로 이동

        # "댓글에 A or B 남겨주세요!" - 크기 증가
        main_txt = TextClip(
            text="댓글에 A or B\n남겨주세요!",
            font_size=68,  # 52 → 68 (크기 증가)
            color='white',
            font=korean_font,
            size=(self.width - 140, None),
            method='caption',
            text_align='center',
            stroke_color='#FFD700',  # Gold stroke (강조)
            stroke_width=4,
            margin=(10, 20)
        ).with_position(('center', 730)).with_duration(duration)

        # "좋아요 & 구독" - 크기 증가
        sub_txt = TextClip(
            text="좋아요 & 구독",
            font_size=56,  # 42 → 56 (크기 증가)
            color='#FFD700',
            font=korean_font,
            stroke_color='white',  # 흰색 외곽선 (반전)
            stroke_width=3,
            margin=(10, 20)
        ).with_position(('center', 970)).with_duration(duration)

        # 페이드 효과
        branding_text = branding_text.with_effects([vfx.FadeIn(0.3)])
        main_txt = main_txt.with_effects([vfx.FadeIn(0.3)])
        sub_txt = sub_txt.with_effects([vfx.FadeIn(0.5)])

        # 레이어 순서: 배경 → 브랜딩 텍스트 → 반투명 박스 → 메인 CTA → 서브 CTA
        return CompositeVideoClip([bg, branding_text, text_bg, main_txt, sub_txt], size=(self.width, self.height))

    def create_simple_video(
        self,
        sentences: list[str],
        image_paths: list[str],
        audio_path: str,
        output_path: str
    ) -> str:
        """
        간단한 버전의 비디오 생성 (이미지 개수와 문장 개수가 같을 때)

        Args:
            sentences: 영어 문장 리스트
            image_paths: 이미지 파일 경로 리스트
            audio_path: 음성 파일 경로
            output_path: 비디오 저장 경로

        Returns:
            생성된 비디오 파일 경로
        """
        # 각 문장에 이미지 1개씩 매핑
        image_groups = [[i] for i in range(len(sentences))]
        return self.create_video(
            sentences,
            image_paths,
            audio_path,
            output_path,
            image_groups
        )

    def generate_quiz_preview(
        self,
        quiz_data: dict,
        audio_info: list[dict],
        output_dir: str
    ) -> dict:
        """
        퀴즈 비디오 프리뷰 생성 (각 클립의 정적 이미지 + 타이밍 정보)

        Args:
            quiz_data: 퀴즈 데이터
            audio_info: 각 항목별 오디오 정보
            output_dir: 프리뷰 이미지 저장 디렉토리

        Returns:
            {
                'clips': [{'name': str, 'image': str, 'duration': float}, ...],
                'total_duration': float,
                'timeline': {...}
            }
        """
        # QuizPreviewGenerator를 사용하여 프리뷰 생성 (컴포넌트로 분리)
        preview_generator = QuizPreviewGenerator()
        return preview_generator.generate(quiz_data, audio_info, output_dir)

    def _create_idiom_intro_clip(self, duration: float = 3.0) -> VideoClip:
        """
        속어 비교 모듈 전용 인트로 클립 생성 (화면 분할 디자인)

        Args:
            duration: 인트로 지속 시간 (기본 3초)

        Returns:
            인트로 VideoClip
        """
        from pathlib import Path

        # 배경 이미지 경로
        intro_bg_path = Path(__file__).parent.parent / "output" / "resources" / "images" / "idiom_intro_bg.png"

        if not intro_bg_path.exists():
            print(f"⚠ 속어 비교 인트로 배경 이미지가 없습니다: {intro_bg_path}")
            # 폴백: 기본 색상 배경 (화면 분할)
            # 왼쪽 (한국어 - 파란색)
            left_bg = ColorClip(
                size=(self.width // 2, self.height),
                color=(184, 212, 227)  # 파스텔 블루
            ).with_duration(duration).with_position((0, 0))

            # 오른쪽 (영어 - 핑크색)
            right_bg = ColorClip(
                size=(self.width // 2, self.height),
                color=(227, 184, 196)  # 파스텔 핑크
            ).with_duration(duration).with_position((self.width // 2, 0))

            # 중앙 구분선
            divider = ColorClip(
                size=(5, self.height),
                color=(255, 255, 255)  # 흰색
            ).with_duration(duration).with_position(((self.width // 2) - 2, 0))

            bg = CompositeVideoClip([left_bg, right_bg, divider], size=(self.width, self.height))
        else:
            # 배경 이미지 로드
            bg = ImageClip(str(intro_bg_path)).with_duration(duration)
            bg = bg.resized(height=self.height)

            # 이미지 크기가 width와 맞지 않으면 조정
            if bg.w != self.width:
                bg_fill = ColorClip(size=(self.width, self.height), color=(200, 200, 220)).with_duration(duration)
                bg = CompositeVideoClip([bg_fill, bg.with_position('center')], size=(self.width, self.height))

        # 메인 타이틀 텍스트 (하단 중앙)
        # 폰트 잘림 방지: size 높이를 None으로 설정하여 자동 조정
        title_txt = TextClip(
            text="한국어 속어 vs 원어민 영어 속어",
            font_size=55,  # 적당한 크기
            color='white',
            stroke_color='black',
            stroke_width=3,  # 외곽선 (가독성)
            method='caption',  # 자동 줄바꿈 및 높이 조정
            size=(self.width - 160, None),  # 좌우 여백 80px, 높이는 자동
            font='AppleGothic',
            text_align='center'
        ).with_position(('center', 1650)).with_duration(duration)  # 하단에 위치 (폰트 잘림 방지)

        # 서브 타이틀 (상단)
        subtitle_txt = TextClip(
            text="Daily English Mecca",
            font_size=42,
            color='white',
            stroke_color='gold',
            stroke_width=3,
            method='caption',
            size=(self.width - 200, None),
            font='AppleGothic',
            text_align='center'
        ).with_position(('center', 180)).with_duration(duration)  # 상단 (폰트 잘림 방지)

        return CompositeVideoClip(
            [bg, title_txt, subtitle_txt],
            size=(self.width, self.height)
        )

    def _create_idiom_outro_clip(self, duration: float = 5.0) -> VideoClip:
        """
        속어 비교 모듈 전용 아웃트로 클립 생성

        Args:
            duration: 아웃트로 지속 시간 (기본 5초)

        Returns:
            아웃트로 VideoClip
        """
        from pathlib import Path

        # 배경 이미지 경로
        outro_bg_path = Path(__file__).parent.parent / "output" / "resources" / "images" / "idiom_outro_bg.png"

        if not outro_bg_path.exists():
            print(f"⚠ 속어 비교 아웃트로 배경 이미지가 없습니다: {outro_bg_path}")
            # 폴백: 기본 그라데이션 배경
            bg = ColorClip(
                size=(self.width, self.height),
                color=(212, 196, 227)  # 파스텔 퍼플
            ).with_duration(duration)
        else:
            # 배경 이미지 로드
            bg = ImageClip(str(outro_bg_path)).with_duration(duration)
            bg = bg.resized(height=self.height)

            # 이미지 크기가 width와 맞지 않으면 조정
            if bg.w != self.width:
                bg_fill = ColorClip(size=(self.width, self.height), color=(240, 230, 250)).with_duration(duration)
                bg = CompositeVideoClip([bg_fill, bg.with_position('center')], size=(self.width, self.height))

        # 반투명 배경 박스 (텍스트 가독성)
        text_bg = ColorClip(
            size=(self.width - 100, 600),  # 충분한 높이 (폰트 잘림 방지)
            color=(0, 0, 0)
        ).with_opacity(0.6).with_position(('center', 660)).with_duration(duration)

        # 메인 CTA 텍스트
        main_txt = TextClip(
            text="알고 있던 속어\n댓글로 남겨주세요!",
            font_size=62,  # 크기 증가
            color='white',
            stroke_color='gold',
            stroke_width=4,
            method='caption',
            size=(self.width - 160, None),  # 높이 자동
            font='AppleGothic',
            text_align='center'
        ).with_position(('center', 760)).with_duration(duration)  # 중앙보다 약간 위 (폰트 잘림 방지)

        # 서브 텍스트
        sub_txt = TextClip(
            text="좋아요 & 구독",
            font_size=52,
            color='#FFD700',  # 금색
            stroke_color='black',
            stroke_width=3,
            method='caption',
            size=(self.width - 200, None),
            font='AppleGothic',
            text_align='center'
        ).with_position(('center', 1050)).with_duration(duration)  # 하단 (폰트 잘림 방지)

        return CompositeVideoClip(
            [bg, text_bg, main_txt, sub_txt],
            size=(self.width, self.height)
        )

    def _create_idiom_korean_intro_clip(
        self,
        korean_idiom: str,
        korean_meaning: str,
        duration: float,
        background_image_path: str = None
    ) -> VideoClip:
        """
        한국어 속어 소개 클립 생성

        Args:
            korean_idiom: 한국어 속어 (예: '대박')
            korean_meaning: 한국어 의미 설명
            duration: 클립 지속 시간
            background_image_path: DALL-E 배경 이미지 경로 (선택사항)

        Returns:
            한국어 소개 VideoClip
        """
        # 배경 (DALL-E 이미지 또는 기본 색상)
        if background_image_path and os.path.exists(background_image_path):
            bg = ImageClip(background_image_path).resized(
                height=self.height
            ).with_duration(duration)
            # 중앙 크롭 (9:16 비율)
            bg = bg.with_position(('center', 'center')).cropped(
                x_center=bg.w // 2,
                width=self.width,
                height=self.height
            )
        else:
            # 기본 배경 (파스텔 블루)
            bg = ColorClip(
                size=(self.width, self.height),
                color=(184, 212, 227)
            ).with_duration(duration)

        # 반투명 배경 박스
        text_bg = ColorClip(
            size=(self.width - 120, 700),  # 충분한 높이
            color=(255, 255, 255)
        ).with_opacity(0.85).with_position(('center', 610)).with_duration(duration)

        # 한국어 속어 (큰 텍스트)
        idiom_txt = TextClip(
            text=f'"{korean_idiom}"',
            font_size=90,
            color='#2E5090',  # 짙은 파란색
            stroke_color='white',
            stroke_width=2,
            method='caption',
            size=(self.width - 180, None),
            font='AppleGothic',
            text_align='center'
        ).with_position(('center', 700)).with_duration(duration)

        # 의미 설명 (작은 텍스트)
        meaning_txt = TextClip(
            text=korean_meaning,
            font_size=42,
            color='#4A4A4A',  # 회색
            method='caption',
            size=(self.width - 200, None),
            font='AppleGothic',
            text_align='center'
        ).with_position(('center', 950)).with_duration(duration)

        # 상단 라벨
        label_txt = TextClip(
            text="🇰🇷 한국어 속어",
            font_size=45,
            color='white',
            stroke_color='#2E5090',
            stroke_width=3,
            method='caption',
            size=(self.width - 200, None),
            font='AppleGothic',
            text_align='center'
        ).with_position(('center', 420)).with_duration(duration)

        return CompositeVideoClip(
            [bg, text_bg, label_txt, idiom_txt, meaning_txt],
            size=(self.width, self.height)
        )

    def _create_idiom_wrong_clip(
        self,
        wrong_translation: str,
        why_wrong: str,
        duration: float,
        background_image_path: str = None
    ) -> VideoClip:
        """
        틀린 번역 클립 생성 (화면 분할)

        Args:
            wrong_translation: 틀린 영어 번역
            why_wrong: 왜 틀렸는지 설명
            duration: 클립 지속 시간
            background_image_path: DALL-E 배경 이미지 경로 (선택사항)

        Returns:
            틀린 번역 VideoClip
        """
        # 배경 (DALL-E 이미지 또는 기본 색상)
        if background_image_path and os.path.exists(background_image_path):
            bg = ImageClip(background_image_path).resized(
                height=self.height
            ).with_duration(duration)
            # 중앙 크롭 (9:16 비율)
            bg = bg.with_position(('center', 'center')).cropped(
                x_center=bg.w // 2,
                width=self.width,
                height=self.height
            )
            clips = [bg]
        else:
            # 기본 배경 (분할 화면 - 왼쪽 레드, 오른쪽 옐로우)
            left_bg = ColorClip(
                size=(self.width // 2, self.height),
                color=(230, 150, 150)  # 파스텔 레드
            ).with_duration(duration).with_position((0, 0))

            right_bg = ColorClip(
                size=(self.width // 2, self.height),
                color=(250, 240, 180)  # 파스텔 옐로우
            ).with_duration(duration).with_position((self.width // 2, 0))

            clips = [left_bg, right_bg]

        # 중앙 구분선
        divider = ColorClip(
            size=(5, self.height),
            color=(100, 100, 100)
        ).with_duration(duration).with_position(((self.width // 2) - 2, 0))

        # 왼쪽: 틀린 표현
        wrong_txt = TextClip(
            text=f'❌\n{wrong_translation}',
            font_size=52,
            color='#8B0000',  # 다크 레드
            stroke_color='white',
            stroke_width=2,
            method='caption',
            size=(self.width // 2 - 80, None),
            font='AppleGothic',
            text_align='center'
        ).with_position((40, 650)).with_duration(duration)

        # 왼쪽 라벨
        left_label = TextClip(
            text="틀린 번역",
            font_size=38,
            color='white',
            stroke_color='#8B0000',
            stroke_width=2,
            method='caption',
            size=(self.width // 2 - 80, None),
            font='AppleGothic',
            text_align='center'
        ).with_position((40, 450)).with_duration(duration)

        # 오른쪽: 설명
        why_txt = TextClip(
            text=f'💡 왜?\n\n{why_wrong}',
            font_size=38,
            color='#4A4A4A',
            method='caption',
            size=(self.width // 2 - 100, None),
            font='AppleGothic',
            text_align='center'
        ).with_position((self.width // 2 + 50, 600)).with_duration(duration)

        # 오른쪽 라벨
        right_label = TextClip(
            text="설명",
            font_size=38,
            color='#4A4A4A',
            stroke_color='white',
            stroke_width=2,
            method='caption',
            size=(self.width // 2 - 100, None),
            font='AppleGothic',
            text_align='center'
        ).with_position((self.width // 2 + 50, 450)).with_duration(duration)

        # 텍스트 요소들 추가
        clips.extend([divider, left_label, wrong_txt, right_label, why_txt])

        return CompositeVideoClip(
            clips,
            size=(self.width, self.height)
        )

    def _create_idiom_correct_clip(
        self,
        correct_expressions: list[dict],
        duration: float,
        background_image_path: str = None
    ) -> VideoClip:
        """
        올바른 표현들 클립 생성 (3개 표현)

        Args:
            correct_expressions: 올바른 표현 리스트 (3개)
                [
                    {
                        'english': str,
                        'usage_level': str,
                        'korean_label': str,
                        'example': str
                    },
                    ...
                ]
            duration: 클립 지속 시간
            background_image_path: DALL-E 배경 이미지 경로 (선택사항)

        Returns:
            올바른 표현 VideoClip
        """
        # 배경 (DALL-E 이미지 또는 기본 색상)
        if background_image_path and os.path.exists(background_image_path):
            bg = ImageClip(background_image_path).resized(
                height=self.height
            ).with_duration(duration)
            # 중앙 크롭 (9:16 비율)
            bg = bg.with_position(('center', 'center')).cropped(
                x_center=bg.w // 2,
                width=self.width,
                height=self.height
            )
        else:
            # 기본 배경 (파스텔 그린)
            bg = ColorClip(
                size=(self.width, self.height),
                color=(180, 230, 180)
            ).with_duration(duration)

        # 반투명 배경 박스
        text_bg = ColorClip(
            size=(self.width - 100, 1100),  # 충분한 높이 (3개 표현)
            color=(255, 255, 255)
        ).with_opacity(0.9).with_position(('center', 460)).with_duration(duration)

        # 상단 라벨 (이모지 제거하고 텍스트만)
        label_txt = TextClip(
            text="올바른 표현",
            font_size=50,
            color='white',
            stroke_color='#2E7D32',  # 다크 그린
            stroke_width=4,
            method='caption',
            size=(self.width - 160, None),
            font='AppleGothic',
            text_align='center'
        ).with_position(('center', 320)).with_duration(duration)

        clips = [bg, text_bg, label_txt]

        # 3개 표현을 세로로 배치 (간격을 넓혀서 예문 공간 확보)
        y_positions = [500, 900, 1300]  # 간격 400px

        for idx, expr in enumerate(correct_expressions[:3]):  # 최대 3개
            english = expr['english']
            korean_label = expr['korean_label']
            usage_level = expr['usage_level']
            example = expr.get('example', '')  # 예문 추가

            # 사용 수준별 색상
            level_colors = {
                'informal': '#1976D2',  # 파란색
                'formal': '#7B1FA2',    # 보라색
                'slang': '#F57C00'      # 주황색
            }
            color = level_colors.get(usage_level, '#4A4A4A')

            # 영어 표현 텍스트 (번호 + 영어)
            expr_txt = TextClip(
                text=f'{idx + 1}. {english}',
                font_size=48,
                color=color,
                stroke_color='white',
                stroke_width=2,
                method='caption',
                size=(self.width - 160, None),
                font='AppleGothic',
                text_align='center'
            ).with_position(('center', y_positions[idx])).with_duration(duration)

            # 한국어 라벨 (사용 수준)
            label = TextClip(
                text=f'({korean_label})',
                font_size=34,
                color='#666666',
                method='caption',
                size=(self.width - 180, None),
                font='AppleGothic',
                text_align='center'
            ).with_position(('center', y_positions[idx] + 70)).with_duration(duration)

            clips.extend([expr_txt, label])

            # 예문 추가 (더 작고 회색으로)
            if example:
                example_txt = TextClip(
                    text=f'예: {example}',
                    font_size=30,
                    color='#888888',
                    method='caption',
                    size=(self.width - 200, None),
                    font='AppleGothic',
                    text_align='center'
                ).with_position(('center', y_positions[idx] + 130)).with_duration(duration)
                clips.append(example_txt)

        return CompositeVideoClip(clips, size=(self.width, self.height))

    def create_idiom_comparison_video(
        self,
        idiom_data: dict,
        audio_info: list[dict],
        output_path: str
    ):
        """
        속어 비교 비디오 생성 (전체 파이프라인)

        Args:
            idiom_data: 속어 비교 데이터
                {
                    'format': 'idiom_comparison',
                    'korean_idiom': str,
                    'korean_meaning': str,
                    'wrong_translation': str,
                    'why_wrong': str,
                    'correct_expressions': [...]
                }
            audio_info: 5개 항목의 오디오 정보
                [
                    {'sentence': str, 'voices': {'alloy': {...}, ...}},  # 한국어 속어
                    {...},  # 틀린 번역
                    {...},  # 올바른 표현 1
                    {...},  # 올바른 표현 2
                    {...}   # 올바른 표현 3
                ]
            output_path: 비디오 저장 경로
        """
        print("=" * 60)
        print("속어 비교 비디오 생성 시작")
        print("=" * 60)

        # 0. 이미지 생성 (DALL-E 3)
        image_paths = {}
        if 'image_prompts' in idiom_data and self.image_generator:
            print("0. DALL-E 배경 이미지 생성 중...")
            prompts = idiom_data['image_prompts']

            # 한국어 인트로 이미지
            print("   - 한국어 인트로 이미지 생성...")
            korean_image_path = self.image_generator.resource_manager.get_image_path(
                f"idiom_korean_{idiom_data.get('id', 'temp')}"
            )
            image_paths['korean_intro'] = self.image_generator.generate_image(
                prompt=prompts['korean_intro'],
                output_path=korean_image_path
            )

            # 틀린 번역 이미지
            print("   - 틀린 번역 이미지 생성...")
            wrong_image_path = self.image_generator.resource_manager.get_image_path(
                f"idiom_wrong_{idiom_data.get('id', 'temp')}"
            )
            image_paths['wrong'] = self.image_generator.generate_image(
                prompt=prompts['wrong'],
                output_path=wrong_image_path
            )

            # 올바른 표현 이미지
            print("   - 올바른 표현 이미지 생성...")
            correct_image_path = self.image_generator.resource_manager.get_image_path(
                f"idiom_correct_{idiom_data.get('id', 'temp')}"
            )
            image_paths['correct'] = self.image_generator.generate_image(
                prompt=prompts['correct'],
                output_path=correct_image_path
            )

            print(f"   ✓ 3개 배경 이미지 생성 완료")
        else:
            print("   ⚠ 이미지 프롬프트 없음 - 기본 배경색 사용")

        all_clips = []
        current_time = 0.0

        # 1. 인트로 클립 (3초)
        print("1. 인트로 클립 생성 중...")
        intro_clip = self._create_idiom_intro_clip(duration=3.0)
        intro_clip = intro_clip.with_start(current_time)
        all_clips.append(intro_clip)
        current_time += 3.0

        # 2. 한국어 속어 소개 클립
        print("2. 한국어 속어 소개 클립 생성 중...")
        korean_duration = audio_info[0]['voices']['alloy']['duration'] + 2.0  # 간격 2초
        korean_clip = self._create_idiom_korean_intro_clip(
            korean_idiom=idiom_data['korean_idiom'],
            korean_meaning=idiom_data['korean_meaning'],
            duration=korean_duration,
            background_image_path=image_paths.get('korean_intro')  # DALL-E 배경 이미지
        )
        korean_clip = korean_clip.with_start(current_time)
        all_clips.append(korean_clip)
        current_time += korean_duration

        # 3. 틀린 번역 클립
        print("3. 틀린 번역 클립 생성 중...")
        wrong_duration = audio_info[1]['voices']['alloy']['duration'] + 2.0  # 간격 2초
        wrong_clip = self._create_idiom_wrong_clip(
            wrong_translation=idiom_data['wrong_translation'],
            why_wrong=idiom_data['why_wrong'],
            duration=wrong_duration,
            background_image_path=image_paths.get('wrong')  # DALL-E 배경 이미지
        )
        wrong_clip = wrong_clip.with_start(current_time)
        all_clips.append(wrong_clip)
        current_time += wrong_duration

        # 4. 올바른 표현들 클립 (3개 표현을 하나의 클립에)
        print("4. 올바른 표현들 클립 생성 중...")
        # 3개 오디오 duration 합계 + 간격
        correct_duration = sum(
            audio_info[i]['voices']['alloy']['duration']
            for i in range(2, 5)  # 인덱스 2, 3, 4
        ) + 2.0  # 간격
        correct_clip = self._create_idiom_correct_clip(
            correct_expressions=idiom_data['correct_expressions'],
            duration=correct_duration,
            background_image_path=image_paths.get('correct')  # DALL-E 배경 이미지
        )
        correct_clip = correct_clip.with_start(current_time)
        all_clips.append(correct_clip)
        current_time += correct_duration

        # 5. 아웃트로 클립 (5초)
        print("5. 아웃트로 클립 생성 중...")
        outro_clip = self._create_idiom_outro_clip(duration=5.0)
        outro_clip = outro_clip.with_start(current_time)
        all_clips.append(outro_clip)
        current_time += 5.0

        # 비디오 합성
        print("6. 비디오 클립 합성 중...")
        final_video = CompositeVideoClip(all_clips, size=(self.width, self.height))
        final_video = final_video.with_duration(current_time)

        # 오디오 트랙 생성 (5개 음성)
        print("7. 오디오 트랙 합성 중...")
        audio_clips = []
        audio_start_times = [
            3.0,  # 인트로 후
            3.0 + korean_duration,  # 한국어 소개 후
            3.0 + korean_duration + wrong_duration,  # 틀린 번역 후
            3.0 + korean_duration + wrong_duration,  # 올바른 표현 1
            3.0 + korean_duration + wrong_duration,  # 올바른 표현 2-3 (시작 시간 동일, duration으로 조정)
        ]

        # 각 오디오 클립 추가 (alloy, nova, shimmer 순환)
        voices = ['alloy', 'nova', 'shimmer']
        for i, info in enumerate(audio_info[:5]):  # 5개만
            voice = voices[i % 3]  # 음성 순환
            audio_path = info['voices'][voice]['path']
            audio_clip = AudioFileClip(audio_path)

            # 올바른 표현 3개는 순차적으로 재생
            if i >= 2:  # 인덱스 2, 3, 4 (올바른 표현)
                # 이전 오디오들의 duration 합산
                accumulated_duration = sum(
                    audio_info[j]['voices'][voices[j % 3]]['duration']
                    for j in range(2, i)
                )
                start_time = audio_start_times[2] + accumulated_duration
            else:
                start_time = audio_start_times[i]

            audio_clip = audio_clip.with_start(start_time)
            audio_clips.append(audio_clip)

        # 배경 음악 추가 (인트로 3초에만)
        background_music_path = None
        if self.resource_manager:
            bg_music_candidates = [
                os.path.join(str(self.resource_manager.resources_dir), "background_music_original.mp3"),
                os.path.join(str(self.resource_manager.resources_dir), "background_music.mp3"),
            ]
            for path in bg_music_candidates:
                if os.path.exists(path):
                    background_music_path = path
                    break

        if background_music_path:
            try:
                print(f"배경 음악 추가: {background_music_path}")
                bg_music = AudioFileClip(background_music_path)
                bg_music = bg_music * 0.05  # 볼륨 5%
                bg_music = bg_music.subclipped(0, 3.0)  # 인트로 3초만
                bg_music = bg_music.with_start(0)
                audio_clips.append(bg_music)
            except Exception as e:
                print(f"⚠ 배경 음악 추가 실패: {e}")

        # 최종 오디오 합성
        if audio_clips:
            combined_audio = CompositeAudioClip(audio_clips)
            final_video = final_video.with_audio(combined_audio)

        # 파일 저장
        print(f"8. 비디오 파일 저장 중: {output_path}")
        final_video.write_videofile(
            output_path,
            fps=24,
            codec='libx264',
            audio_codec='aac',
            temp_audiofile='temp-audio.m4a',
            remove_temp=True,
            logger=None  # 로그 출력 최소화
        )

        print("=" * 60)
        print("속어 비교 비디오 생성 완료!")
        print(f"총 길이: {current_time:.1f}초")
        print("=" * 60)

    def create_longform_video(
        self,
        sentences: list[str],
        image_paths: list[str],
        audio_info: list[dict],
        output_path: str,
        image_groups: list[int],
        translations: list[str],
        hook_phrase: str = None,
        kelly_style: str = 'casual_hoodie'
    ) -> str:
        """
        롱폼 교육 비디오 생성 - Shorts 확장판 (16:9 가로, 3-4분)

        각 문장을 3번 반복 (alloy, nova, shimmer)하여 학습 효과 극대화
        Kelly는 인트로/아웃트로에만 등장 (브랜딩)

        Args:
            sentences: 3개의 영어 문장 리스트 (Shorts와 동일)
            image_paths: 문장별 이미지 경로 리스트 (3개)
            audio_info: 각 문장별 오디오 정보 [{'sentence': str, 'voices': {...}}, ...]
            output_path: 비디오 저장 경로
            image_groups: 이미지 그룹 정보
            translations: 3개의 한글 번역 리스트
            hook_phrase: AI 생성 훅 문구 (선택사항)
            kelly_style: Kelly 캐릭터 스타일 (casual_hoodie, business, etc.)

        Returns:
            생성된 비디오 파일 경로
        """
        try:
            print("\n" + "=" * 80)
            print("🎬 롱폼 비디오 생성 시작 (16:9, 3문장 × 3번 반복)")
            print("=" * 80)

            # Kelly 이미지 로드 (롱폼에서도 Kelly 캐릭터 사용)
            kelly_image_path = None
            if self.resource_manager:
                kelly_candidates = [
                    os.path.join(str(self.resource_manager.resources_dir), "images", "kelly_casual_hoodie.png"),
                    os.path.join(str(self.resource_manager.resources_dir), "images", "kelly_ponytail.png"),
                    os.path.join(str(self.resource_manager.resources_dir), "images", "kelly_glasses.png"),
                ]
                for path in kelly_candidates:
                    if os.path.exists(path):
                        kelly_image_path = path
                        print(f"✓ Kelly 이미지 로드: {os.path.basename(path)}")
                        break

            if not kelly_image_path:
                print("⚠ Kelly 이미지를 찾을 수 없습니다. 텍스트만 표시됩니다.")

            all_clips = []
            audio_clips = []
            current_time = 0.0

            # 1. 인트로 (5초) - Kelly 포함
            print("\n[1/11] 인트로 클립 생성 중...")
            intro_clip = self._create_longform_intro_clip(
                duration=5.0,
                kelly_image_path=kelly_image_path
            )
            all_clips.append(intro_clip)
            current_time += 5.0
            print("✓ 인트로 클립 완료 (5.0초)")

            # 2. 3개 문장 × 3번 반복 = 9개 클립
            print("\n[2-10/11] 문장 클립 생성 중 (각 문장 3번 반복)...")
            for i in range(min(3, len(sentences))):
                sentence = sentences[i]
                translation = translations[i] if i < len(translations) else ""
                image_path = image_paths[i] if i < len(image_paths) else None

                print(f"[DEBUG 롱폼] 문장 {i+1} 이미지 경로: {image_path}")
                print(f"[DEBUG 롱폼] 파일 존재 여부: {os.path.exists(image_path) if image_path else False}")

                if not image_path or not os.path.exists(image_path):
                    print(f"⚠️ 문장 {i+1} 이미지 없음, 건너뜁니다.")
                    continue

                # 3번 반복: alloy → nova → shimmer
                for voice_name in ['alloy', 'nova', 'shimmer']:
                    if i < len(audio_info):
                        audio_data = audio_info[i]['voices'].get(voice_name)
                        if audio_data:
                            audio_path = audio_data['path']
                            duration = audio_data['duration'] + 2.0  # 2초 간격 (따라 말하기 시간)

                            # Longform 방식 클립 생성 (16:9 가로 이미지)
                            sentence_clip = self._create_sentence_clip(
                                image_path=image_path,
                                sentences=[sentence],
                                translations=[translation],
                                duration=duration,
                                format_type="longform"
                            )
                            all_clips.append(sentence_clip)

                            # 오디오 클립 추가
                            audio_clip = AudioFileClip(audio_path).with_start(current_time)
                            audio_clips.append(audio_clip)

                            current_time += duration
                            print(f"✓ 문장 {i+1}/10 - {voice_name} 완료 ({duration:.1f}초)")
                        else:
                            print(f"⚠️ 문장 {i+1} {voice_name} 오디오 없음")
                    else:
                        print(f"⚠️ 문장 {i+1} 오디오 정보 없음")

            # 3. 아웃트로 (5초) - Kelly 포함
            print("\n[11/11] 아웃트로 클립 생성 중...")
            outro_clip = self._create_longform_outro_clip(
                duration=5.0,
                kelly_image_path=kelly_image_path
            )
            all_clips.append(outro_clip)
            print("✓ 아웃트로 클립 완료 (5.0초)")

            # 4. 모든 비디오 클립 연결
            print("\n비디오 클립 연결 중...")
            final_video = concatenate_videoclips(all_clips, method="compose")

            # 5. 오디오 합성
            print("오디오 합성 중...")
            if audio_clips:
                combined_audio = CompositeAudioClip(audio_clips)

                # 배경 음악 추가 (인트로 5초에만)
                background_music_path = None
                if self.resource_manager:
                    bg_music_candidates = [
                        os.path.join(str(self.resource_manager.resources_dir), "background_music_original.mp3"),
                        os.path.join(str(self.resource_manager.resources_dir), "background_music.mp3"),
                    ]
                    for path in bg_music_candidates:
                        if os.path.exists(path):
                            background_music_path = path
                            break

                if background_music_path:
                    try:
                        print(f"배경 음악 추가: {background_music_path}")
                        bg_music = AudioFileClip(background_music_path)
                        bg_music = bg_music * 0.05  # 볼륨 5% (TTS 방해 안 함)
                        bg_music = bg_music.subclipped(0, 5.0)  # 인트로 5초만
                        bg_music = bg_music.with_start(0)
                        combined_audio = CompositeAudioClip([combined_audio, bg_music])
                        print("✓ 배경 음악 추가 완료 (인트로 5초)")
                    except Exception as e:
                        print(f"⚠ 배경 음악 추가 실패: {e}")

                final_video = final_video.with_audio(combined_audio)
            else:
                print("⚠️ 오디오 클립이 없습니다.")

            # 6. 비디오 저장
            total_duration = final_video.duration
            print(f"\n비디오 저장 중... (총 길이: {total_duration:.1f}초 = {total_duration/60:.1f}분)")
            print(f"출력 경로: {output_path}")

            final_video.write_videofile(
                output_path,
                fps=self.fps,
                codec='libx264',
                audio_codec='aac',
                preset='medium',
                threads=4
            )

            print("\n" + "=" * 80)
            print("✅ 롱폼 비디오 생성 완료!")
            print(f"📊 통계:")
            print(f"   - 총 길이: {total_duration:.1f}초 ({total_duration/60:.1f}분)")
            print(f"   - 해상도: {self.width}x{self.height} (16:9)")
            print(f"   - 문장 수: 3개 × 3번 반복 = 9개 클립")
            print(f"   - Kelly: 인트로/아웃트로만 (브랜딩)")
            print(f"   - 학습 방식: Shorts 동일 (3번 반복)")
            print("=" * 80)

            return output_path

        except Exception as e:
            print(f"\n❌ 롱폼 비디오 생성 실패: {e}")
            import traceback
            traceback.print_exc()
            raise
