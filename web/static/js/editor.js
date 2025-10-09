// ==================== 전역 변수 ====================

let videoId = null;
let config = null;
let selectedClipIndex = null;
let hasUnsavedChanges = false; // 변경사항 추적

// ==================== 초기화 ====================

document.addEventListener('DOMContentLoaded', async () => {
    // URL에서 video_id 추출
    const urlParams = new URLSearchParams(window.location.search);
    videoId = urlParams.get('video_id');

    if (!videoId) {
        showMessage('error', '비디오 ID가 없습니다. 메인 페이지로 돌아가주세요.');
        return;
    }

    // 헤더에 video_id 표시
    document.getElementById('video-id-display').textContent = `Video ID: ${videoId}`;

    // 설정 로드
    await loadConfig();

    // 이벤트 리스너 등록
    initEventListeners();
});

// ==================== 에러 처리 유틸리티 ====================

/**
 * API 에러를 사용자 친화적 메시지로 변환
 */
function handleApiError(error, operation = '작업') {
    console.error(`Error during ${operation}:`, error);

    // 네트워크 에러 (인터넷 연결 문제, CORS 등)
    if (error instanceof TypeError && error.message.includes('fetch')) {
        return `네트워크 오류: 서버에 연결할 수 없습니다. 인터넷 연결을 확인해주세요.`;
    }

    // HTTP 상태 코드별 메시지
    if (error.message.includes('404')) {
        return `${operation} 실패: 비디오 파일 또는 설정을 찾을 수 없습니다.`;
    }

    if (error.message.includes('500') || error.message.includes('502') || error.message.includes('503')) {
        return `${operation} 실패: 서버 오류가 발생했습니다. 잠시 후 다시 시도해주세요.`;
    }

    // 타임아웃 에러
    if (error.name === 'AbortError' || error.message.includes('timeout')) {
        return `${operation} 실패: 요청 시간이 초과되었습니다. 다시 시도해주세요.`;
    }

    // 기타 에러
    return `${operation} 실패: ${error.message}`;
}

// ==================== 설정 로드 ====================

async function loadConfig() {
    try {
        showMessage('info', '설정을 불러오는 중...');

        const response = await fetch(`/api/video/${videoId}/config`);

        if (!response.ok) {
            const errorMsg = `HTTP ${response.status}`;
            throw new Error(errorMsg);
        }

        const data = await response.json();
        config = data.config;

        // UI에 설정 표시
        displayConfig();

        // 비디오 미리보기 설정
        if (data.video_exists) {
            const videoElement = document.getElementById('preview-video');
            videoElement.src = data.video_path;
        }

        showMessage('success', '설정을 불러왔습니다.');
        setTimeout(() => hideMessage(), 2000);

    } catch (error) {
        const friendlyMessage = handleApiError(error, '설정 로드');
        showMessage('error', friendlyMessage);
    }
}

// ==================== UI 표시 ====================

function displayConfig() {
    if (!config) return;

    // 전역 설정 표시
    displayGlobalSettings();

    // 타임라인 클립 생성
    createTimelineClips();
}

function displayGlobalSettings() {
    const globalSettings = config.global_settings;

    // 배경음악
    const bgMusicSelect = document.getElementById('bg-music');
    bgMusicSelect.value = globalSettings.background_music.file;

    // 배경음악 볼륨
    const bgVolumeInput = document.getElementById('bg-volume');
    const volumeValue = Math.round(globalSettings.background_music.volume * 100);
    bgVolumeInput.value = volumeValue;
    document.getElementById('volume-value').textContent = `${volumeValue}%`;

    // 인트로 길이
    const introDurationSelect = document.getElementById('intro-duration');
    introDurationSelect.value = globalSettings.intro.duration;

    // 아웃트로 길이
    const outroDurationSelect = document.getElementById('outro-duration');
    outroDurationSelect.value = globalSettings.outro.duration;
}

function createTimelineClips() {
    const container = document.getElementById('sentence-clips-container');
    container.innerHTML = '';

    config.clips.forEach((clip, index) => {
        const clipElement = document.createElement('div');
        clipElement.className = 'clip sentence-clip';
        clipElement.dataset.type = 'sentence';
        clipElement.dataset.index = index;

        // 예상 클립 길이 계산 (TTS 3회 반복 + 간격)
        const estimatedDuration = (clip.audio.repeat_count * 3) + clip.audio.pause_after;

        clipElement.innerHTML = `
            <span class="clip-label">문장 ${index + 1}</span>
            <span class="clip-duration">~${estimatedDuration.toFixed(0)}s</span>
        `;

        clipElement.addEventListener('click', () => selectClip(index));

        container.appendChild(clipElement);
    });
}

// ==================== 클립 선택 ====================

function selectClip(index) {
    selectedClipIndex = index;

    // 모든 클립에서 active 제거
    document.querySelectorAll('.clip').forEach(clip => {
        clip.classList.remove('active');
    });

    // 선택된 클립에 active 추가
    const selectedClip = document.querySelector(`.clip[data-index="${index}"]`);
    if (selectedClip) {
        selectedClip.classList.add('active');
    }

    // 클립 설정 표시
    displayClipSettings(index);
}

function displayClipSettings(index) {
    const clip = config.clips[index];

    // 클립 설정 섹션 표시
    const clipSettingsSection = document.getElementById('clip-settings');
    clipSettingsSection.style.display = 'block';

    // 제목 업데이트
    document.getElementById('clip-title').textContent = `문장 ${index + 1}`;

    // 영어 문장
    document.getElementById('sentence-text').value = clip.sentence_text;

    // 한글 번역
    document.getElementById('translation-text').value = clip.translation;

    // 폰트 크기
    const fontSizeInput = document.getElementById('font-size');
    fontSizeInput.value = clip.text.font_size;
    document.getElementById('font-size-value').textContent = `${clip.text.font_size}px`;

    // 텍스트 위치
    const position = clip.text.position;
    document.querySelectorAll('.position-btn').forEach(btn => {
        btn.classList.remove('active');
        if (btn.dataset.position === position) {
            btn.classList.add('active');
        }
    });

    // TTS 음성 (첫 번째)
    const ttsVoiceSelect = document.getElementById('tts-voice');
    const firstVoice = clip.audio.tts_voices[0];
    ttsVoiceSelect.value = firstVoice;

    // 문장 후 간격
    const pauseAfterInput = document.getElementById('pause-after');
    pauseAfterInput.value = clip.audio.pause_after;
    document.getElementById('pause-value').textContent = `${clip.audio.pause_after.toFixed(1)}초`;

    // 이미지
    const clipImage = document.getElementById('clip-image');
    const imagePath = document.getElementById('image-path');
    if (clip.image.path) {
        // 이미지 경로를 상대 경로로 변환 (프로젝트 루트 기준)
        const relativePath = clip.image.path.replace(/.*\/daily-english-mecca\//, '');
        clipImage.src = `/${relativePath}`;
        imagePath.textContent = clip.image.path;
    } else {
        clipImage.src = '';
        imagePath.textContent = '이미지 없음';
    }
}

// ==================== 이벤트 리스너 ====================

/**
 * beforeunload 이벤트 핸들러 (페이지 나가기 전 경고)
 */
function beforeUnloadHandler(e) {
    if (hasUnsavedChanges) {
        e.preventDefault();
        e.returnValue = ''; // Chrome requires returnValue to be set
        return '';
    }
}

/**
 * 키보드 단축키 핸들러
 */
function keyboardShortcutHandler(e) {
    // Ctrl+S or Cmd+S: 저장
    if ((e.ctrlKey || e.metaKey) && e.key === 's') {
        e.preventDefault();
        onSave();
    }
}

function initEventListeners() {
    // 전역 설정 이벤트
    document.getElementById('bg-music').addEventListener('change', onGlobalSettingChange);
    document.getElementById('bg-volume').addEventListener('input', onVolumeChange);
    document.getElementById('intro-duration').addEventListener('change', onGlobalSettingChange);
    document.getElementById('outro-duration').addEventListener('change', onGlobalSettingChange);

    // 이미지 생성 버튼
    document.getElementById('btn-generate-intro-image').addEventListener('click', onGenerateIntroImage);
    document.getElementById('btn-generate-outro-image').addEventListener('click', onGenerateOutroImage);

    // 클립별 설정 이벤트
    document.getElementById('sentence-text').addEventListener('input', onClipSettingChange);
    document.getElementById('translation-text').addEventListener('input', onClipSettingChange);
    document.getElementById('font-size').addEventListener('input', onFontSizeChange);
    document.getElementById('tts-voice').addEventListener('change', onClipSettingChange);
    document.getElementById('pause-after').addEventListener('input', onPauseAfterChange);

    // 텍스트 위치 버튼
    document.querySelectorAll('.position-btn').forEach(btn => {
        btn.addEventListener('click', onPositionChange);
    });

    // 비디오 재생 컨트롤
    document.getElementById('btn-play').addEventListener('click', () => {
        document.getElementById('preview-video').play();
    });

    document.getElementById('btn-pause').addEventListener('click', () => {
        document.getElementById('preview-video').pause();
    });

    // 액션 버튼
    document.getElementById('btn-cancel').addEventListener('click', onCancel);
    document.getElementById('btn-save').addEventListener('click', onSave);
    document.getElementById('btn-regenerate').addEventListener('click', onRegenerate);

    // 비디오 시간 업데이트
    const videoElement = document.getElementById('preview-video');
    videoElement.addEventListener('timeupdate', updateTimestamp);

    // 페이지 나가기 전 경고 (변경사항이 있을 때만)
    window.addEventListener('beforeunload', beforeUnloadHandler);

    // 키보드 단축키 (Ctrl+S / Cmd+S)
    document.addEventListener('keydown', keyboardShortcutHandler);
}

// ==================== 입력 검증 ====================

/**
 * 문장 텍스트 검증
 */
function validateSentence(text) {
    if (!text || text.trim().length === 0) {
        return { valid: false, message: '문장을 입력해주세요.' };
    }
    if (text.length > 200) {
        return { valid: false, message: '문장이 너무 깁니다 (최대 200자).' };
    }
    return { valid: true };
}

/**
 * 폰트 크기 검증
 */
function validateFontSize(size) {
    if (size < 30 || size > 80) {
        return { valid: false, message: '폰트 크기는 30~80px 사이여야 합니다.' };
    }
    return { valid: true };
}

/**
 * 간격 검증
 */
function validatePause(pause) {
    if (pause < 0 || pause > 5) {
        return { valid: false, message: '간격은 0~5초 사이여야 합니다.' };
    }
    return { valid: true };
}

// ==================== 설정 변경 핸들러 ====================

function markAsChanged() {
    hasUnsavedChanges = true;
}

function onGlobalSettingChange(event) {
    if (!config) return;

    const id = event.target.id;
    const value = event.target.value;

    if (id === 'bg-music') {
        config.global_settings.background_music.file = value;
    } else if (id === 'intro-duration') {
        config.global_settings.intro.duration = parseInt(value);
    } else if (id === 'outro-duration') {
        config.global_settings.outro.duration = parseInt(value);
    }

    markAsChanged();
}

function onVolumeChange(event) {
    if (!config) return;

    const value = parseInt(event.target.value);
    config.global_settings.background_music.volume = value / 100;
    document.getElementById('volume-value').textContent = `${value}%`;

    markAsChanged();
}

function onClipSettingChange(event) {
    if (!config || selectedClipIndex === null) return;

    const id = event.target.id;
    const value = event.target.value;
    const clip = config.clips[selectedClipIndex];

    if (id === 'sentence-text') {
        const validation = validateSentence(value);
        if (!validation.valid) {
            showMessage('warning', validation.message);
            return;
        }
        clip.sentence_text = value;
    } else if (id === 'translation-text') {
        clip.translation = value;
    } else if (id === 'tts-voice') {
        // 첫 번째 음성만 변경 (3회 반복은 고정)
        clip.audio.tts_voices[0] = value;
    }

    markAsChanged();
}

function onFontSizeChange(event) {
    if (!config || selectedClipIndex === null) return;

    const value = parseInt(event.target.value);

    const validation = validateFontSize(value);
    if (!validation.valid) {
        showMessage('warning', validation.message);
        event.target.value = config.clips[selectedClipIndex].text.font_size; // 원래 값으로 복원
        return;
    }

    config.clips[selectedClipIndex].text.font_size = value;
    document.getElementById('font-size-value').textContent = `${value}px`;

    markAsChanged();
}

function onPauseAfterChange(event) {
    if (!config || selectedClipIndex === null) return;

    const value = parseFloat(event.target.value);

    const validation = validatePause(value);
    if (!validation.valid) {
        showMessage('warning', validation.message);
        event.target.value = config.clips[selectedClipIndex].audio.pause_after; // 원래 값으로 복원
        return;
    }

    config.clips[selectedClipIndex].audio.pause_after = value;
    document.getElementById('pause-value').textContent = `${value.toFixed(1)}초`;

    markAsChanged();
}

function onPositionChange(event) {
    if (!config || selectedClipIndex === null) return;

    const position = event.target.dataset.position;

    // 모든 버튼에서 active 제거
    document.querySelectorAll('.position-btn').forEach(btn => {
        btn.classList.remove('active');
    });

    // 클릭된 버튼에 active 추가
    event.target.classList.add('active');

    // 설정 업데이트
    config.clips[selectedClipIndex].text.position = position;

    markAsChanged();
}

// ==================== 액션 핸들러 ====================

function onCancel() {
    // 변경사항이 있으면 경고
    if (hasUnsavedChanges) {
        if (!confirm('저장하지 않은 변경사항이 있습니다. 정말 돌아가시겠습니까?')) {
            return;
        }
    }

    // beforeunload 이벤트 제거 (의도적으로 페이지를 나가는 경우)
    window.removeEventListener('beforeunload', beforeUnloadHandler);
    window.location.href = '/';
}

async function onSave() {
    if (!config) {
        showMessage('error', '설정이 없습니다.');
        return;
    }

    const saveBtn = document.getElementById('btn-save');

    try {
        // 버튼 로딩 상태 시작
        setButtonLoading(saveBtn, true);
        showMessage('info', '설정을 저장하는 중...');

        const response = await fetch(`/api/video/${videoId}/config`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                global_settings: config.global_settings,
                clips: config.clips
            })
        });

        if (!response.ok) {
            const errorMsg = `HTTP ${response.status}`;
            throw new Error(errorMsg);
        }

        const data = await response.json();

        // 저장 성공 시 변경사항 플래그 해제
        hasUnsavedChanges = false;

        showMessage('success', '설정이 저장되었습니다.');
        setTimeout(() => hideMessage(), 3000);

    } catch (error) {
        const friendlyMessage = handleApiError(error, '설정 저장');
        showMessage('error', friendlyMessage);
    } finally {
        // 버튼 로딩 상태 해제
        setButtonLoading(saveBtn, false);
    }
}

async function onRegenerate() {
    if (!config) {
        showMessage('error', '설정이 없습니다.');
        return;
    }

    if (!confirm('편집된 설정으로 비디오를 재생성하시겠습니까?\n\n소요 시간: 약 3-5분\n\n* 변경사항이 저장되지 않았다면 먼저 저장해주세요.')) {
        return;
    }

    const regenerateBtn = document.getElementById('btn-regenerate');

    try {
        // 로딩 오버레이 및 버튼 상태 시작
        showLoadingOverlay('🎬 비디오 재생성 중...', '약 3-5분 소요됩니다. 잠시만 기다려주세요.');
        setButtonLoading(regenerateBtn, true);

        const response = await fetch(`/api/video/${videoId}/regenerate`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                config: config
            })
        });

        if (!response.ok) {
            const errorMsg = `HTTP ${response.status}`;
            throw new Error(errorMsg);
        }

        const data = await response.json();

        // 로딩 오버레이 숨기기
        hideLoadingOverlay();

        showMessage('success', `비디오 재생성 완료! (${data.processing_time}초 소요)`);

        // 비디오 미리보기 업데이트
        const videoElement = document.getElementById('preview-video');
        videoElement.src = data.video_path + '?t=' + Date.now(); // 캐시 방지

        setTimeout(() => hideMessage(), 5000);

    } catch (error) {
        // 로딩 오버레이 숨기기
        hideLoadingOverlay();

        const friendlyMessage = handleApiError(error, '비디오 재생성');
        showMessage('error', friendlyMessage);
    } finally {
        // 버튼 로딩 상태 해제
        setButtonLoading(regenerateBtn, false);
    }
}

async function onGenerateIntroImage() {
    const promptInput = document.getElementById('intro-image-prompt');
    const customPrompt = promptInput.value.trim();
    const generateBtn = document.getElementById('btn-generate-intro-image');

    try {
        // 버튼 로딩 상태 시작
        setButtonLoading(generateBtn, true);
        showMessage('info', '인트로 이미지 생성 중... (약 10-15초 소요)');

        const response = await fetch(`/api/video/${videoId}/generate-intro-image`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                prompt: customPrompt
            })
        });

        if (!response.ok) {
            const errorMsg = `HTTP ${response.status}`;
            throw new Error(errorMsg);
        }

        const data = await response.json();

        showMessage('success', `인트로 이미지 생성 완료! ${data.message}`);
        setTimeout(() => hideMessage(), 3000);

        // 프롬프트 입력 초기화
        promptInput.value = '';

    } catch (error) {
        const friendlyMessage = handleApiError(error, '인트로 이미지 생성');
        showMessage('error', friendlyMessage);
    } finally {
        // 버튼 로딩 상태 해제
        setButtonLoading(generateBtn, false);
    }
}

async function onGenerateOutroImage() {
    const promptInput = document.getElementById('outro-image-prompt');
    const customPrompt = promptInput.value.trim();
    const generateBtn = document.getElementById('btn-generate-outro-image');

    try {
        // 버튼 로딩 상태 시작
        setButtonLoading(generateBtn, true);
        showMessage('info', '아웃트로 이미지 생성 중... (약 10-15초 소요)');

        const response = await fetch(`/api/video/${videoId}/generate-outro-image`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                prompt: customPrompt
            })
        });

        if (!response.ok) {
            const errorMsg = `HTTP ${response.status}`;
            throw new Error(errorMsg);
        }

        const data = await response.json();

        showMessage('success', `아웃트로 이미지 생성 완료! ${data.message}`);
        setTimeout(() => hideMessage(), 3000);

        // 프롬프트 입력 초기화
        promptInput.value = '';

    } catch (error) {
        const friendlyMessage = handleApiError(error, '아웃트로 이미지 생성');
        showMessage('error', friendlyMessage);
    } finally {
        // 버튼 로딩 상태 해제
        setButtonLoading(generateBtn, false);
    }
}

// ==================== 유틸리티 함수 ====================

function updateTimestamp() {
    const video = document.getElementById('preview-video');
    const current = formatTime(video.currentTime);
    const total = formatTime(video.duration);
    document.getElementById('timestamp').textContent = `${current} / ${total}`;
}

function formatTime(seconds) {
    if (isNaN(seconds)) return '00:00';
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
}

function showMessage(type, message) {
    const statusMessage = document.getElementById('status-message');
    statusMessage.className = `status-message ${type}`;
    statusMessage.textContent = message;
}

function hideMessage() {
    const statusMessage = document.getElementById('status-message');
    statusMessage.className = 'status-message';
    statusMessage.textContent = '';
}

// ==================== 로딩 관련 함수 ====================

/**
 * 로딩 오버레이 표시
 */
function showLoadingOverlay(text = '처리 중...', subtext = '잠시만 기다려주세요.') {
    const overlay = document.getElementById('loading-overlay');
    const loadingText = document.getElementById('loading-text');
    const loadingSubtext = document.getElementById('loading-subtext');

    loadingText.textContent = text;
    loadingSubtext.textContent = subtext;
    overlay.classList.add('active');
}

/**
 * 로딩 오버레이 숨기기
 */
function hideLoadingOverlay() {
    const overlay = document.getElementById('loading-overlay');
    overlay.classList.remove('active');
}

/**
 * 버튼 로딩 상태 설정
 */
function setButtonLoading(button, isLoading) {
    if (isLoading) {
        button.classList.add('loading');
        button.disabled = true;
    } else {
        button.classList.remove('loading');
        button.disabled = false;
    }
}
