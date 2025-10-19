"""
MoviePy를 사용한 유튜브 쇼츠 비디오 생성 모듈
"""
import os
from pathlib import Path
from moviepy import (
    VideoClip, ImageClip, AudioFileClip, TextClip,
    CompositeVideoClip, concatenate_videoclips, ColorClip, vfx
)
from src.clips.quiz import (
    QuestionClip, CountdownClip, AnswerClip,
    ExplanationClip, ExampleClip
)
from src.preview import QuizPreviewGenerator


class VideoCreator:
    def __init__(self, image_generator=None, resource_manager=None):
        """VideoCreator 초기화"""
        self.width = 1080  # 세로 영상 너비
        self.height = 1920  # 세로 영상 높이
        self.fps = 30
        self.image_generator = image_generator
        self.resource_manager = resource_manager

        # 커스텀 인트로/아웃트로 이미지 경로 (설정에서 가져옴)
        self.intro_custom_image = None
        self.outro_custom_image = None

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
            final_video.write_videofile(
                output_path,
                fps=self.fps,
                codec='libx264',
                audio_codec='aac',
                temp_audiofile='temp-audio.m4a',
                remove_temp=True,
                preset='medium'
            )

            # 리소스 정리
            for audio_clip in audio_clips:
                audio_clip.close()
            combined_audio.close()
            final_video.close()

            print(f"✓ 비디오 저장 완료: {output_path}")
            return output_path

        except Exception as e:
            print(f"✗ 비디오 생성 실패: {e}")
            raise

    def _create_intro_clip(self, duration: float = 3, hook_phrase: str = None) -> VideoClip:
        """
        인트로 클립 생성 (AI 자동 생성 훅 포함)

        Args:
            duration: 인트로 지속 시간
            hook_phrase: AI가 생성한 바이럴 훅 문구 (없으면 기본값)

        Returns:
            인트로 VideoClip
        """
        # 인트로 이미지 우선순위: 커스텀 > 캐시 > 생성 > 기본 배경
        intro_image_path = None

        # 1. 커스텀 이미지 확인
        if self.intro_custom_image and os.path.exists(self.intro_custom_image):
            print(f"✓ 커스텀 인트로 이미지 사용: {self.intro_custom_image}")
            intro_image_path = self.intro_custom_image
        # 2. 캐시된 템플릿 이미지 확인
        elif self.image_generator and self.resource_manager:
            intro_prompt = """A simple geometric abstract background with bright cheerful blue gradient.
Modern minimalist design with soft shapes and clean composition.
Vertical 9:16 format. Educational and friendly mood.
Simple flat design with pastel colors."""

            # 캐시 확인
            cached_intro = self.resource_manager.get_image_path("intro_template")
            if self.resource_manager.image_exists("intro_template"):
                print("✓ 캐시된 인트로 이미지 사용")
                intro_image_path = cached_intro
            else:
                try:
                    print("인트로 이미지 생성 중...")
                    intro_image_path = self.image_generator.generate_image(
                        intro_prompt,
                        cached_intro,
                        size="1024x1792"
                    )
                except Exception as e:
                    print(f"⚠ 인트로 이미지 생성 실패 (기본 배경 사용): {e}")
                    intro_image_path = None

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
            # 기본 배경색 (파스텔 블루)
            bg = ColorClip(
                size=(self.width, self.height),
                color=(100, 150, 255),
                duration=duration
            )

        # 텍스트 (한글 지원 폰트 - 직접 경로 지정)
        korean_font = "/System/Library/AssetsV2/com_apple_MobileAsset_Font7/bad9b4bf17cf1669dde54184ba4431c22dcad27b.asset/AssetData/NanumGothic.ttc"

        # AI 생성 훅 문구 또는 기본 문구 사용
        intro_text = hook_phrase if hook_phrase else "오늘의 3문장\nDaily English"

        txt = TextClip(
            text=intro_text,
            font_size=65,  # 폰트 크기 줄임 (90 → 65)
            color='white',
            font=korean_font,  # 나눔고딕 직접 경로
            size=(self.width - 120, None),
            method='caption',
            text_align='center',
            stroke_color='black',
            stroke_width=3,
            margin=(10, 20)  # 여백 추가로 한글 깨짐 방지
        ).with_position(('center', 600)).with_duration(duration)  # 더 위로 조정 (800 → 600, 이미지 위에서 텍스트 잘림 방지)

        # 페이드 효과
        txt = txt.with_effects([vfx.FadeIn(0.5), vfx.FadeOut(0.5)])

        return CompositeVideoClip([bg, txt], size=(self.width, self.height))

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
        tts_duration: float = None
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

        Returns:
            문장 VideoClip
        """
        # 배경 이미지
        img = ImageClip(image_path).with_duration(duration)

        # 디버깅: 이미지 크기 출력
        print(f"📸 문장 이미지 크기: {img.w}x{img.h} (경로: {image_path.split('/')[-1]})")

        # 이미지가 가로 방향이면 90도 회전 (세로 영상이어야 함)
        if img.w > img.h:
            print(f"⚠ 이미지가 가로 방향입니다 ({img.w}x{img.h}). 90도 회전합니다.")
            img = img.rotated(90)
            print(f"✓ 회전 후 크기: {img.w}x{img.h}")
        else:
            print(f"✓ 이미지가 이미 세로 방향입니다 ({img.w}x{img.h})")

        # 이미지를 9:16 비율로 리사이즈 (크롭 또는 패딩)
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
        korean_font = "/System/Library/AssetsV2/com_apple_MobileAsset_Font7/bad9b4bf17cf1669dde54184ba4431c22dcad27b.asset/AssetData/NanumGothic.ttc"

        # 텍스트 배경 박스 (가독성 향상) - 화면 하단에 작게 배치
        txt_bg = ColorClip(
            size=(self.width - 80, 350),  # 높이 줄임 (800 → 350)
            color=(0, 0, 0),
            duration=duration
        ).with_opacity(0.7).with_position(('center', 1400))  # 하단으로 이동 (500 → 1400)
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
        ).with_position(('center', 1450)).with_duration(duration)

        text_clips.append(txt)

        # 모든 요소 합성 (전체 화면 오버레이 제거)
        return CompositeVideoClip(
            [img] + text_clips,
            size=(self.width, self.height)
        )

    def _create_outro_clip(self, duration: float = 2) -> VideoClip:
        """
        아웃트로 클립 생성 (구독 유도)

        Args:
            duration: 아웃트로 지속 시간

        Returns:
            아웃트로 VideoClip
        """
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

        # 한글 폰트 직접 경로 지정
        korean_font = "/System/Library/AssetsV2/com_apple_MobileAsset_Font7/bad9b4bf17cf1669dde54184ba4431c22dcad27b.asset/AssetData/NanumGothic.ttc"

        # 메인 텍스트 (강화된 CTA)
        main_txt = TextClip(
            text="좋아요 & 구독하기!",
            font_size=58,  # 폰트 크기 줄임 (80 → 58)
            color='white',
            font=korean_font,  # 나눔고딕 직접 경로
            size=(self.width - 120, None),
            method='caption',
            text_align='center',
            stroke_color='black',
            stroke_width=3,
            margin=(10, 20)  # 여백 추가로 한글 깨짐 방지
        ).with_position(('center', 700)).with_duration(duration)  # 위로 조정 (750 → 700)

        # 서브 텍스트 (댓글 유도 - 참여도 증가)
        sub_txt = TextClip(
            text="댓글에 오늘 배운 문장 써보세요!",
            font_size=38,  # 폰트 크기 줄임 (50 → 38)
            color='white',
            font=korean_font,  # 나눔고딕 직접 경로
            stroke_color='black',
            stroke_width=2,
            margin=(10, 20)  # 여백 추가로 한글 깨짐 방지
        ).with_position(('center', 850)).with_duration(duration)  # 위로 조정 (950 → 850)

        # 페이드 효과
        main_txt = main_txt.with_effects([vfx.FadeIn(0.3)])
        sub_txt = sub_txt.with_effects([vfx.FadeIn(0.5)])

        return CompositeVideoClip(
            [bg, main_txt, sub_txt],
            size=(self.width, self.height)
        )

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
            final_video.write_videofile(
                output_path,
                fps=self.fps,
                codec='libx264',
                audio_codec='aac',
                temp_audiofile='temp-audio.m4a',
                remove_temp=True,
                preset='medium'
            )

            # 리소스 정리
            for audio_clip in audio_clips:
                audio_clip.close()
            combined_audio.close()
            final_video.close()

            print(f"✓ 퀴즈 비디오 저장 완료: {output_path}")
            return output_path

        except Exception as e:
            print(f"✗ 퀴즈 비디오 생성 실패: {e}")
            raise

    def _create_quiz_question_clip(self, question: str, option_a: str, option_b: str, duration: float) -> VideoClip:
        """문제 제시 클립 (TTS 재생만, pause 제외)"""
        # 파스텔 블루 배경
        bg = ColorClip(size=(self.width, self.height), color=(100, 150, 255), duration=duration)

        korean_font = "/System/Library/AssetsV2/com_apple_MobileAsset_Font7/bad9b4bf17cf1669dde54184ba4431c22dcad27b.asset/AssetData/NanumGothic.ttc"

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

        korean_font = "/System/Library/AssetsV2/com_apple_MobileAsset_Font7/bad9b4bf17cf1669dde54184ba4431c22dcad27b.asset/AssetData/NanumGothic.ttc"

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

        korean_font = "/System/Library/AssetsV2/com_apple_MobileAsset_Font7/bad9b4bf17cf1669dde54184ba4431c22dcad27b.asset/AssetData/NanumGothic.ttc"

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

        korean_font = "/System/Library/AssetsV2/com_apple_MobileAsset_Font7/bad9b4bf17cf1669dde54184ba4431c22dcad27b.asset/AssetData/NanumGothic.ttc"

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

        korean_font = "/System/Library/AssetsV2/com_apple_MobileAsset_Font7/bad9b4bf17cf1669dde54184ba4431c22dcad27b.asset/AssetData/NanumGothic.ttc"

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

        korean_font = "/System/Library/AssetsV2/com_apple_MobileAsset_Font7/bad9b4bf17cf1669dde54184ba4431c22dcad27b.asset/AssetData/NanumGothic.ttc"

        # 텍스트 배경 박스 추가 (가독성 향상)
        text_bg = ColorClip(
            size=(self.width - 100, 500),
            color=(0, 0, 0),
            duration=duration
        ).with_opacity(0.7).with_position(('center', 600))

        # "댓글에 A or B 남겨주세요!" - 크기 증가
        main_txt = TextClip(
            text="댓글에 A or B\n남겨주세요!",
            font_size=68,  # 52 → 68 (크기 증가)
            color='white',
            font=korean_font,
            size=(self.width - 140, None),
            method='caption',
            text_align='center',
            stroke_color='black',
            stroke_width=4,  # 3 → 4 (외곽선 두껍게)
            margin=(10, 20)
        ).with_position(('center', 680)).with_duration(duration)

        # "좋아요 & 구독" - 크기 증가
        sub_txt = TextClip(
            text="좋아요 & 구독",
            font_size=56,  # 42 → 56 (크기 증가)
            color='#FFD700',
            font=korean_font,
            stroke_color='black',
            stroke_width=3,  # 2 → 3 (외곽선 두껍게)
            margin=(10, 20)
        ).with_position(('center', 920)).with_duration(duration)

        # 페이드 효과
        main_txt = main_txt.with_effects([vfx.FadeIn(0.3)])
        sub_txt = sub_txt.with_effects([vfx.FadeIn(0.5)])

        return CompositeVideoClip([bg, text_bg, main_txt, sub_txt], size=(self.width, self.height))

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
