/**
 * Daily English Mecca - 메인 JavaScript
 */

// 전역 변수
let currentTaskId = null;
let pollingInterval = null;

// DOM 요소
const inputSection = document.getElementById('input-section');
const progressSection = document.getElementById('progress-section');
const resultSection = document.getElementById('result-section');
const sentenceForm = document.getElementById('sentence-form');
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
 * UI 섹션 전환
 */
function showInputSection() {
    inputSection.style.display = 'block';
    progressSection.style.display = 'none';
    resultSection.style.display = 'none';
}

function showProgressSection() {
    inputSection.style.display = 'none';
    progressSection.style.display = 'block';
    resultSection.style.display = 'none';

    // 초기화
    progressBar.style.width = '0%';
    progressText.textContent = '0%';
    currentStepElement.textContent = '시작 중...';
    logsElement.innerHTML = '';
}

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

// 페이지 로드 시 입력 섹션 표시
window.addEventListener('DOMContentLoaded', () => {
    showInputSection();
});
