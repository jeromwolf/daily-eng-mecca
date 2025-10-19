"""
Quiz preview generator - generates static PNG previews for each clip
"""
import os
from pathlib import Path
from PIL import Image
from src.clips.quiz import (
    QuestionClip, CountdownClip, AnswerClip,
    ExplanationClip, ExampleClip
)
from src.clips.base_clip import BaseClip
from moviepy import ColorClip, TextClip, CompositeVideoClip, vfx
from src.config import VideoSettings


class IntroClip(BaseClip):
    """인트로 클립 (프리뷰용)"""

    def create(self, hook_phrase: str, duration: float = 3.0):
        bg = self.create_background(
            color=self.settings.Colors.INTRO_BG,
            duration=duration
        )

        # 텍스트 위치를 더 위로 조정 (이미지 위에서 텍스트가 잘리는 문제 해결)
        txt = self.create_text(
            text=hook_phrase if hook_phrase else "오늘의 3문장\nDaily English",
            font_size=self.settings.Intro.FONT_SIZE,
            color=self.settings.Colors.WHITE,
            position=('center', 600),  # 800 → 600 (더 위로)
            duration=duration,
            size=(self.width - 120, None),
            method='caption'
        )

        txt = txt.with_effects([vfx.FadeIn(0.5), vfx.FadeOut(0.5)])
        return self.compose([bg, txt])


class OutroClip(BaseClip):
    """아웃트로 클립 (프리뷰용)"""

    def create(self, duration: float = 3.0):
        bg = self.create_background(
            color=self.settings.Colors.OUTRO_BG,
            duration=duration
        )

        main_txt = self.create_text(
            text="댓글에 A or B\n남겨주세요!",
            font_size=52,
            color=self.settings.Colors.WHITE,
            position=('center', 650),
            duration=duration,
            size=(self.width - 120, None),
            method='caption'
        )

        sub_txt = self.create_text(
            text="좋아요 & 구독",
            font_size=42,
            color=self.settings.Colors.GOLD,
            position=('center', 900),
            duration=duration
        )

        main_txt = main_txt.with_effects([vfx.FadeIn(0.3)])
        sub_txt = sub_txt.with_effects([vfx.FadeIn(0.5)])

        return self.compose([bg, main_txt, sub_txt])


class QuizPreviewGenerator:
    """퀴즈 비디오 프리뷰 생성기"""

    def __init__(self):
        """초기화"""
        self.settings = VideoSettings

    def generate(
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
        try:
            print("퀴즈 프리뷰 생성 중...")
            Path(output_dir).mkdir(parents=True, exist_ok=True)

            clips_info = []
            current_time = 0.0

            # 타이밍 상수
            pause_between_scenes = self.settings.Timing.PAUSE_BETWEEN_SCENES
            countdown_duration = self.settings.Timing.COUNTDOWN_DURATION

            # 실제 TTS 길이 계산
            question_tts_duration = (
                audio_info[0]['voices']['alloy']['duration'] +
                audio_info[1]['voices']['alloy']['duration']
            )
            question_duration = question_tts_duration

            # === 1. 인트로 프리뷰 ===
            intro_clip_obj = IntroClip()
            intro_clip = intro_clip_obj.create(
                hook_phrase="한국인 95% 틀리는 문제!",
                duration=self.settings.Intro.DURATION
            )
            intro_frame = intro_clip.get_frame(0)
            intro_path = os.path.join(output_dir, "01_intro.png")
            Image.fromarray(intro_frame).save(intro_path)

            clips_info.append({
                'name': '인트로',
                'image': intro_path,
                'duration': self.settings.Intro.DURATION,
                'start_time': current_time
            })
            current_time += self.settings.Intro.DURATION

            # === 2. 문제 클립 프리뷰 ===
            question_clip_obj = QuestionClip()
            question_clip = question_clip_obj.create(
                question=quiz_data['question'],
                option_a=quiz_data['option_a'],
                option_b=quiz_data['option_b'],
                duration=question_duration
            )
            question_frame = question_clip.get_frame(0)
            question_path = os.path.join(output_dir, "02_question.png")
            Image.fromarray(question_frame).save(question_path)

            clips_info.append({
                'name': '문제',
                'image': question_path,
                'duration': question_duration,
                'start_time': current_time
            })
            current_time += question_duration

            # === 3. 카운트다운 클립 프리뷰 (3장: 3, 2, 1) ===
            countdown_clip_obj = CountdownClip()
            countdown_clip = countdown_clip_obj.create(
                question=quiz_data['question'],
                option_a=quiz_data['option_a'],
                option_b=quiz_data['option_b'],
                duration=countdown_duration
            )

            # 카운트다운 각 1초 시점의 프레임 저장
            for i, second in enumerate([0.5, 1.5, 2.5]):
                frame = countdown_clip.get_frame(second)
                countdown_path = os.path.join(output_dir, f"03_countdown_{3-i}.png")
                Image.fromarray(frame).save(countdown_path)

                clips_info.append({
                    'name': f'카운트다운 {3-i}',
                    'image': countdown_path,
                    'duration': 1.0,
                    'start_time': current_time + i
                })
            current_time += countdown_duration

            # === 4. 정답 공개 프리뷰 ===
            answer_tts_duration = audio_info[2]['voices']['alloy']['duration']
            answer_duration = answer_tts_duration + pause_between_scenes

            answer_clip_obj = AnswerClip()
            answer_clip = answer_clip_obj.create(
                answer=quiz_data['correct_answer'],
                correct_option=(
                    quiz_data['option_a']
                    if quiz_data['correct_answer'] == 'A'
                    else quiz_data['option_b']
                ),
                duration=answer_duration
            )
            answer_frame = answer_clip.get_frame(0.5)
            answer_path = os.path.join(output_dir, "04_answer.png")
            Image.fromarray(answer_frame).save(answer_path)

            clips_info.append({
                'name': '정답 공개',
                'image': answer_path,
                'duration': answer_duration,
                'start_time': current_time
            })
            current_time += answer_duration

            # === 5. 해설 프리뷰 ===
            explanation_tts_duration = audio_info[3]['voices']['alloy']['duration']
            explanation_duration = explanation_tts_duration + pause_between_scenes

            explanation_clip_obj = ExplanationClip()
            explanation_clip = explanation_clip_obj.create(
                explanation=quiz_data['explanation'],
                duration=explanation_duration
            )
            explanation_frame = explanation_clip.get_frame(0)
            explanation_path = os.path.join(output_dir, "05_explanation.png")
            Image.fromarray(explanation_frame).save(explanation_path)

            clips_info.append({
                'name': '해설',
                'image': explanation_path,
                'duration': explanation_duration,
                'start_time': current_time
            })
            current_time += explanation_duration

            # === 6. 예문들 프리뷰 ===
            for i, example in enumerate(quiz_data['examples']):
                example_tts_duration = audio_info[4 + i]['voices']['alloy']['duration']
                example_duration = example_tts_duration + pause_between_scenes

                example_clip_obj = ExampleClip()
                example_clip = example_clip_obj.create(
                    example=example,
                    index=i + 1,
                    duration=example_duration
                )
                example_frame = example_clip.get_frame(0)
                example_path = os.path.join(output_dir, f"06_example_{i+1}.png")
                Image.fromarray(example_frame).save(example_path)

                clips_info.append({
                    'name': f'예문 {i+1}',
                    'image': example_path,
                    'duration': example_duration,
                    'start_time': current_time
                })
                current_time += example_duration

            # === 7. 아웃트로 프리뷰 ===
            outro_clip_obj = OutroClip()
            outro_clip = outro_clip_obj.create(duration=self.settings.Outro.DURATION)
            outro_frame = outro_clip.get_frame(0.5)
            outro_path = os.path.join(output_dir, "07_outro.png")
            Image.fromarray(outro_frame).save(outro_path)

            clips_info.append({
                'name': '아웃트로',
                'image': outro_path,
                'duration': self.settings.Outro.DURATION,
                'start_time': current_time
            })
            current_time += self.settings.Outro.DURATION

            # 타임라인 정보 생성
            timeline = {
                'intro': {
                    'start': 0,
                    'end': self.settings.Intro.DURATION
                },
                'question': {
                    'start': self.settings.Intro.DURATION,
                    'end': self.settings.Intro.DURATION + question_duration
                },
                'countdown': {
                    'start': self.settings.Intro.DURATION + question_duration,
                    'end': self.settings.Intro.DURATION + question_duration + countdown_duration
                }
            }

            print(f"✓ 프리뷰 생성 완료: {len(clips_info)}개 클립, 총 {current_time:.2f}초")

            return {
                'clips': clips_info,
                'total_duration': current_time,
                'timeline': timeline
            }

        except Exception as e:
            print(f"✗ 프리뷰 생성 실패: {e}")
            import traceback
            traceback.print_exc()
            raise
