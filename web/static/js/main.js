/**
 * Daily English Mecca - 메인 JavaScript
 */

// 전역 변수
let currentTaskId = null;
let pollingInterval = null;

// DOM 요소
const formatSelection = document.getElementById('format-selection');
const manualInput = document.getElementById('manual-input');
const themeInput = document.getElementById('theme-input');
const otherInput = document.getElementById('other-input');
const inputSection = document.getElementById('input-section'); // 하위 호환성 유지
const progressSection = document.getElementById('progress-section');
const resultSection = document.getElementById('result-section');
const sentenceForm = document.getElementById('sentence-form');
const themeForm = document.getElementById('theme-form');
const otherForm = document.getElementById('other-form');
const progressBar = document.getElementById('progress-bar');
const progressText = document.getElementById('progress-text');
const currentStepElement = document.getElementById('current-step');
const logsElement = document.getElementById('logs');

// 폼 제출 이벤트
sentenceForm.addEventListener('submit', async (e) => {
    e.preventDefault();

    // 입력값 가져오기
    const sentences = [
        document.getElementById('sentence1').value.trim(),
        document.getElementById('sentence2').value.trim(),
        document.getElementById('sentence3').value.trim(),
    ];

    const voice = document.getElementById('voice').value;

    // 유효성 검사
    if (sentences.some(s => !s)) {
        alert('모든 문장을 입력해주세요.');
        return;
    }

    // 비디오 생성 시작
    await startVideoGeneration(sentences, voice);
});

/**
 * 비디오 생성 시작
 */
async function startVideoGeneration(sentences, voice) {
    try {
        // UI 전환: 입력 폼 → 진행 상황
        showProgressSection();

        // API 호출
        const response = await fetch('/api/generate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                sentences: sentences,
                voice: voice,
            }),
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || '비디오 생성에 실패했습니다.');
        }

        const data = await response.json();
        currentTaskId = data.task_id;

        // 진행 상황 폴링 시작
        startPolling();

    } catch (error) {
        console.error('Error:', error);
        alert('오류가 발생했습니다: ' + error.message);
        showInputSection();
    }
}

/**
 * 진행 상황 폴링 시작
 */
function startPolling() {
    // 기존 폴링이 있으면 중지
    if (pollingInterval) {
        clearInterval(pollingInterval);
    }

    // 1초마다 상태 확인
    pollingInterval = setInterval(async () => {
        await checkStatus();
    }, 1000);

    // 즉시 한 번 실행
    checkStatus();
}

/**
 * 작업 상태 확인
 */
async function checkStatus() {
    try {
        const response = await fetch(`/api/status/${currentTaskId}`);

        if (!response.ok) {
            throw new Error('상태 확인에 실패했습니다.');
        }

        const data = await response.json();

        // 진행 상황 업데이트
        updateProgress(data);

        // 완료 또는 오류 시 폴링 중지
        if (data.status === 'completed') {
            clearInterval(pollingInterval);
            showResult(data);
        } else if (data.status === 'error') {
            clearInterval(pollingInterval);
            alert('오류가 발생했습니다: ' + data.error);
            showInputSection();
        }

    } catch (error) {
        console.error('Error checking status:', error);
        clearInterval(pollingInterval);
        alert('상태 확인 중 오류가 발생했습니다.');
        showInputSection();
    }
}

/**
 * 진행 상황 업데이트
 */
function updateProgress(data) {
    // 프로그레스 바
    progressBar.style.width = data.progress + '%';
    progressText.textContent = data.progress + '%';

    // 현재 단계
    currentStepElement.textContent = data.current_step;

    // 로그 업데이트
    if (data.logs && data.logs.length > 0) {
        logsElement.innerHTML = data.logs
            .map(log => `<p>${escapeHtml(log)}</p>`)
            .join('');

        // 자동 스크롤
        logsElement.scrollTop = logsElement.scrollHeight;
    }
}

/**
 * 결과 표시
 */
function showResult(data) {
    // UI 전환: 진행 상황 → 결과
    progressSection.style.display = 'none';
    resultSection.style.display = 'block';

    const result = data.result;

    // 비디오 설정
    const videoSource = document.getElementById('video-source');
    const resultVideo = document.getElementById('result-video');
    videoSource.src = result.video_path;
    resultVideo.load();

    // 메타정보 표시
    const metadata = result.metadata;
    document.getElementById('meta-title').textContent = metadata.title;
    document.getElementById('meta-description').value = metadata.description;
    document.getElementById('meta-tags').textContent = metadata.tags.join(', ');

    // 다운로드 버튼 설정
    document.getElementById('download-video-btn').href = result.video_path;
    document.getElementById('download-video-btn').download = result.video_filename;

    document.getElementById('download-metadata-btn').href = result.metadata_path;
    document.getElementById('download-metadata-btn').download = `metadata_${currentTaskId}.json`;
}

/**
 * UI 섹션 전환 (레거시 함수 - 포맷 선택 섹션에서 재정의됨)
 */
// showInputSection과 showProgressSection은 파일 하단에서 재정의됩니다

/**
 * 클립보드에 복사
 */
function copyToClipboard(elementId) {
    const element = document.getElementById(elementId);
    let text;

    if (element.tagName === 'TEXTAREA' || element.tagName === 'INPUT') {
        text = element.value;
    } else {
        text = element.textContent;
    }

    // 클립보드 API 사용
    navigator.clipboard.writeText(text).then(() => {
        // 복사 성공 피드백
        const button = event.target;
        const originalText = button.textContent;
        button.textContent = '✅ 복사됨!';

        setTimeout(() => {
            button.textContent = originalText;
        }, 2000);
    }).catch(err => {
        console.error('복사 실패:', err);
        alert('복사에 실패했습니다.');
    });
}

/**
 * HTML 이스케이프 (XSS 방지)
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

/**
 * 편집 페이지로 이동
 */
function openEditor() {
    if (!currentTaskId) {
        alert('비디오 ID를 찾을 수 없습니다.');
        return;
    }
    window.location.href = `/editor?video_id=${currentTaskId}`;
}

// 페이지 로드 시 포맷 선택 표시
window.addEventListener('DOMContentLoaded', () => {
    initializeFormatSelection();
});

// ==================== 포맷 선택 로직 (새로 추가) ====================

/**
 * 포맷 선택 초기화
 */
function initializeFormatSelection() {
    // 포맷 카드 클릭 이벤트
    document.querySelectorAll('.format-card').forEach(card => {
        card.addEventListener('click', function() {
            const format = this.dataset.format;
            selectFormat(format);
        });
    });

    // 테마 폼 제출 이벤트
    themeForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        const theme = document.getElementById('theme').value;
        const themeDetail = document.getElementById('theme-detail').value.trim();
        const voice = document.getElementById('theme-voice').value;

        if (!theme) {
            alert('주제를 선택해주세요.');
            return;
        }

        await startThemeGeneration(theme, themeDetail, voice);
    });

    // 다른 포맷 폼 제출 이벤트
    otherForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        const otherFormat = document.getElementById('other-format').value;
        const voice = document.getElementById('other-voice').value;

        if (!otherFormat) {
            alert('포맷을 선택해주세요.');
            return;
        }

        const formatData = {
            format: 'other',  // 메인 포맷 타입
            other_format: otherFormat,  // 서브 포맷 (movie, pronunciation, news, story)
            voice: voice
        };

        // 스토리 시리즈인 경우 추가 데이터
        if (otherFormat === 'story') {
            formatData.story_theme = document.getElementById('story-theme').value.trim();
            formatData.story_day = document.getElementById('story-day').value;
        }

        await startOtherFormatGeneration(formatData);
    });

    // 다른 포맷 선택 변경 시 옵션 표시/숨김
    document.getElementById('other-format').addEventListener('change', function() {
        const storyOptions = document.getElementById('story-options');
        const movieOptions = document.getElementById('movie-options');

        // 모두 숨기기
        storyOptions.style.display = 'none';
        movieOptions.style.display = 'none';

        // 선택된 포맷에 따라 표시
        if (this.value === 'story') {
            storyOptions.style.display = 'block';
        } else if (this.value === 'movie') {
            movieOptions.style.display = 'block';
        }
    });

    // 영화 명대사 리스트 로드
    loadMovieQuotes();

    // 초기 화면: 포맷 선택 표시
    showFormatSelection();
}

/**
 * 포맷 선택
 */
function selectFormat(format) {
    formatSelection.style.display = 'none';

    if (format === 'manual') {
        manualInput.style.display = 'block';
    } else if (format === 'theme') {
        themeInput.style.display = 'block';
    } else if (format === 'other') {
        otherInput.style.display = 'block';
    }
}

/**
 * 포맷 선택 화면 표시
 */
function showFormatSelection() {
    formatSelection.style.display = 'block';
    manualInput.style.display = 'none';
    themeInput.style.display = 'none';
    otherInput.style.display = 'none';
    progressSection.style.display = 'none';
    resultSection.style.display = 'none';
}

/**
 * 테마별 비디오 생성 시작
 */
async function startThemeGeneration(theme, themeDetail, voice) {
    try {
        showProgressSection();

        const response = await fetch('/api/generate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                format: 'theme',
                theme: theme,
                theme_detail: themeDetail,
                voice: voice,
            }),
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || '비디오 생성에 실패했습니다.');
        }

        const data = await response.json();
        currentTaskId = data.task_id;

        startPolling();

    } catch (error) {
        console.error('Error:', error);
        alert('오류가 발생했습니다: ' + error.message);
        showFormatSelection();
    }
}

/**
 * 다른 포맷 비디오 생성 시작
 */
async function startOtherFormatGeneration(formatData) {
    try {
        showProgressSection();

        // 영화 명대사인 경우 movie_quote_id 추가
        if (formatData.other_format === 'movie') {
            const movieQuoteId = document.getElementById('movie-quote').value;
            if (movieQuoteId) {
                formatData.movie_quote_id = movieQuoteId;
            }
        }

        const response = await fetch('/api/generate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                format: 'other',
                ...formatData
            }),
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || '비디오 생성에 실패했습니다.');
        }

        const data = await response.json();
        currentTaskId = data.task_id;

        startPolling();

    } catch (error) {
        console.error('Error:', error);
        alert('오류가 발생했습니다: ' + error.message);
        showFormatSelection();
    }
}

/**
 * 영화 명대사 리스트 로드
 */
async function loadMovieQuotes() {
    try {
        const response = await fetch('/api/movie-quotes');

        if (!response.ok) {
            console.error('Failed to load movie quotes');
            return;
        }

        const data = await response.json();
        const quotes = data.quotes;

        // 드롭다운 채우기
        const movieQuoteSelect = document.getElementById('movie-quote');

        quotes.forEach(quote => {
            const option = document.createElement('option');
            option.value = quote.id;
            option.textContent = `${quote.quote} (${quote.movie}, ${quote.year})`;
            movieQuoteSelect.appendChild(option);
        });

        console.log(`✅ ${quotes.length}개의 영화 명대사 로드 완료`);

    } catch (error) {
        console.error('Error loading movie quotes:', error);
    }
}

// 기존 함수 수정: showInputSection()을 showFormatSelection()으로 변경
function showInputSection() {
    // 하위 호환성을 위해 유지하지만, 포맷 선택으로 리다이렉트
    showFormatSelection();
}

// 프로그레스 섹션에서 뒤로가기 시 포맷 선택으로
function showProgressSection() {
    formatSelection.style.display = 'none';
    manualInput.style.display = 'none';
    themeInput.style.display = 'none';
    otherInput.style.display = 'none';
    progressSection.style.display = 'block';
    resultSection.style.display = 'none';

    // 초기화
    progressBar.style.width = '0%';
    progressText.textContent = '0%';
    currentStepElement.textContent = '시작 중...';
    logsElement.innerHTML = '';
}
