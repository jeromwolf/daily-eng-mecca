"""
MoviePy를 사용한 유튜브 쇼츠 비디오 생성 모듈
"""
import os
from pathlib import Path
from moviepy import (
    VideoClip, ImageClip, AudioFileClip, TextClip,
    CompositeVideoClip, concatenate_videoclips, ColorClip, vfx
)


class VideoCreator:
    def __init__(self, image_generator=None, resource_manager=None):
        """VideoCreator 초기화"""
        self.width = 1080  # 세로 영상 너비
        self.height = 1920  # 세로 영상 높이
        self.fps = 30
        self.image_generator = image_generator
        self.resource_manager = resource_manager

    def create_video(
        self,
        sentences: list[str],
        image_paths: list[str],
        audio_info: list[dict],
        output_path: str,
        image_groups: list[list[int]] = None,
        translations: list[str] = None
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

        Returns:
            생성된 비디오 파일 경로
        """
        try:
            print("비디오 생성 중...")

            # 기본 이미지 그룹 설정 (각 문장에 하나씩)
            if image_groups is None:
                image_groups = [[i] for i in range(len(sentences))]

            # 인트로 생성 (3초)
            intro_clip = self._create_intro_clip(duration=3)

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
            # 각 문장을 3번 반복
            current_time = 3.0  # 인트로 3초 후부터 시작
            pause_duration = 1.0  # 각 문장 사이 간격 (사용자가 따라 읽을 수 있도록)
            repeat_count = 3  # 각 문장을 3번 반복

            for repeat in range(repeat_count):
                print(f"\n=== {repeat + 1}회차 반복 ===")

                for sent_idx in range(len(sentences)):
                    if sent_idx >= len(audio_info):
                        continue

                    # 해당 문장의 이미지
                    img_path = sentence_to_image.get(sent_idx, image_paths[0])

                    # 해당 문장과 번역
                    sentence_text = sentences[sent_idx]
                    translation_text = translations[sent_idx] if translations and sent_idx < len(translations) else ""

                    # 해당 문장의 오디오 duration + 간격
                    clip_duration = audio_info[sent_idx]['duration'] + pause_duration

                    print(f"  문장 {sent_idx + 1}: {audio_info[sent_idx]['duration']:.2f}초 + 간격 {pause_duration}초 = {clip_duration:.2f}초 (시작: {current_time:.2f}초)")

                    # 클립 생성
                    clip = self._create_sentence_clip(
                        image_path=img_path,
                        sentences=[sentence_text],
                        translations=[translation_text] if translation_text else [],
                        duration=clip_duration,
                        start_time=0
                    )
                    sentence_clips.append(clip)

                    # 오디오 클립 추가 (정확한 시작 시간 설정, duration은 원본 유지)
                    audio_clip = AudioFileClip(audio_info[sent_idx]['path']).with_start(current_time)
                    audio_clips.append(audio_clip)

                    current_time += clip_duration

            # 아웃트로 생성 (2초)
            outro_clip = self._create_outro_clip(duration=2)

            # 모든 클립 연결
            video_clips = [intro_clip] + sentence_clips + [outro_clip]
            final_video = concatenate_videoclips(video_clips, method="compose")

            # 총 비디오 길이 확인
            sentences_duration = sum(info['duration'] for info in audio_info) * repeat_count + (pause_duration * len(audio_info) * repeat_count)
            total_duration = 3 + sentences_duration + 2
            print(f"\n총 비디오 길이: {total_duration:.2f}초")
            print(f"  - 인트로: 3.00초")
            print(f"  - 문장들: {sentences_duration:.2f}초 (TTS + 간격 포함, {repeat_count}회 반복)")
            print(f"  - 아웃트로: 2.00초")

            # 오디오 클립들을 정확한 시작 시간으로 합성
            from moviepy import CompositeAudioClip
            combined_audio = CompositeAudioClip(audio_clips)

            # 배경 음악 추가 (낮은 볼륨)
            background_music_path = None
            if self.resource_manager:
                # resources 폴더에서 배경 음악 찾기
                bg_music_candidates = [
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

                    # 비디오 길이에 맞게 자르기 (반복 없이 간단하게)
                    if bg_music.duration < total_duration:
                        print(f"  ⚠ 배경 음악({bg_music.duration:.2f}초)이 비디오({total_duration:.2f}초)보다 짧습니다")
                        print(f"  - 배경 음악은 {bg_music.duration:.2f}초까지만 재생됩니다")
                    else:
                        # 비디오 길이만큼 자르기
                        bg_music = bg_music.subclipped(0, total_duration)
                        print(f"  - 배경 음악을 {total_duration:.2f}초로 조정")

                    # 볼륨 낮추기 (5%) - MoviePy 2.x에서는 스칼라 곱셈 사용
                    bg_music = bg_music * 0.05
                    print(f"  - 볼륨 조절 완료: 5%")

                    # TTS와 배경음악 합성
                    combined_audio = CompositeAudioClip([combined_audio, bg_music]).with_duration(total_duration)
                    print("✓ 배경 음악 추가 완료")
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

    def _create_intro_clip(self, duration: float = 3) -> VideoClip:
        """
        인트로 클립 생성

        Args:
            duration: 인트로 지속 시간

        Returns:
            인트로 VideoClip
        """
        # 인트로 이미지 생성 또는 캐시에서 가져오기
        intro_image_path = None
        if self.image_generator and self.resource_manager:
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
        txt = TextClip(
            text="오늘의 3문장\nDaily English",
            font_size=65,  # 폰트 크기 줄임 (90 → 65)
            color='white',
            font=korean_font,  # 나눔고딕 직접 경로
            size=(self.width - 120, None),
            method='caption',
            text_align='center',
            stroke_color='black',
            stroke_width=3,
            margin=(10, 20)  # 여백 추가로 한글 깨짐 방지
        ).with_position(('center', 800)).with_duration(duration)  # 위로 조정 (900 → 800)

        # 페이드 효과
        txt = txt.with_effects([vfx.FadeIn(0.5), vfx.FadeOut(0.5)])

        return CompositeVideoClip([bg, txt], size=(self.width, self.height))

    def _create_sentence_clip(
        self,
        image_path: str,
        sentences: list[str],
        translations: list[str],
        duration: float,
        start_time: float = 0
    ) -> VideoClip:
        """
        문장 클립 생성

        Args:
            image_path: 배경 이미지 경로
            sentences: 표시할 문장 리스트
            translations: 한글 번역 리스트
            duration: 클립 지속 시간
            start_time: 오디오 시작 시간 (사용하지 않음, 호환성 유지)

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

        # 영어와 번역을 함께 표시
        combined_lines = []
        for i, sentence in enumerate(sentences):
            combined_lines.append(sentence)  # 영어 문장
            if translations and i < len(translations):
                combined_lines.append(translations[i])  # 한글 번역
            if i < len(sentences) - 1:  # 마지막 문장이 아니면 빈 줄 추가
                combined_lines.append("")

        combined_text = "\n".join(combined_lines)

        # 텍스트 배경 박스 (가독성 향상) - 화면 하단에 작게 배치
        txt_bg = ColorClip(
            size=(self.width - 80, 350),  # 높이 줄임 (800 → 350)
            color=(0, 0, 0),
            duration=duration
        ).with_opacity(0.7).with_position(('center', 1400))  # 하단으로 이동 (500 → 1400)
        text_clips.append(txt_bg)

        # 상단 타이틀 추가 (브랜딩) - 배경 박스 + 텍스트
        korean_font = "/System/Library/AssetsV2/com_apple_MobileAsset_Font7/bad9b4bf17cf1669dde54184ba4431c22dcad27b.asset/AssetData/NanumGothic.ttc"

        # 타이틀 배경 박스 (눈에 띄게)
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

        # 한글 폰트 직접 경로 지정
        txt = TextClip(
            text=combined_text,
            font_size=42,  # 폰트 크기 줄임 (56 → 42)
            color='white',
            font=korean_font,  # 나눔고딕 직접 경로
            size=(self.width - 120, None),
            method='caption',
            text_align='center',
            stroke_color='black',
            stroke_width=3,
            margin=(10, 20)  # 좌우 10px, 상하 20px 여백 추가 (한글 잘림 방지)
        ).with_position(('center', 1450)).with_duration(duration)  # 하단으로 이동 (600 → 1450)

        # 페이드 효과 제거 (TTS와 정확한 동기화를 위해)
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
        # 아웃트로 이미지 생성 또는 캐시에서 가져오기
        outro_image_path = None
        if self.image_generator and self.resource_manager:
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

        # 메인 텍스트
        main_txt = TextClip(
            text="구독하고\n매일 3문장 배우기!",
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

        # 서브 텍스트 (이모지 대신 텍스트)
        sub_txt = TextClip(
            text="좋아요 & 구독 & 알림 설정",
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
