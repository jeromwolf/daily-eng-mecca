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
    document.getElementById('intro-duration-display').textContent = `${globalSettings.intro.duration}초`;

    // 아웃트로 길이
    const outroDurationSelect = document.getElementById('outro-duration');
    outroDurationSelect.value = globalSettings.outro.duration;
    document.getElementById('outro-duration-display').textContent = `${globalSettings.outro.duration}초`;

    // 인트로 이미지 로드
    loadIntroOutroImages();
}

/**
 * 인트로/아웃트로 이미지 로드
 */
function loadIntroOutroImages() {
    const globalSettings = config.global_settings;

    // 인트로 이미지
    const introThumbnail = document.getElementById('intro-thumbnail');
    const introImagePath = globalSettings.intro.custom_image || globalSettings.intro.default_image;

    if (introImagePath) {
        const webPath = getRelativeImagePath(introImagePath);
        introThumbnail.innerHTML = `<img src="${webPath}" alt="인트로 이미지">`;
    } else {
        // 이미지가 없으면 기본 배경색 표시
        introThumbnail.innerHTML = `
            <div class="thumbnail-placeholder" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; font-weight: 600; display: flex; align-items: center; justify-content: center; height: 100%;">
                <div style="text-align: center;">
                    <div style="font-size: 2rem;">🎬</div>
                    <div style="margin-top: 8px;">Daily English Mecca</div>
                </div>
            </div>
        `;
    }

    // 아웃트로 이미지
    const outroThumbnail = document.getElementById('outro-thumbnail');
    const outroImagePath = globalSettings.outro.custom_image || globalSettings.outro.default_image;

    if (outroImagePath) {
        const webPath = getRelativeImagePath(outroImagePath);
        outroThumbnail.innerHTML = `<img src="${webPath}" alt="아웃트로 이미지">`;
    } else {
        // 이미지가 없으면 기본 배경색 표시
        outroThumbnail.innerHTML = `
            <div class="thumbnail-placeholder" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); color: white; font-weight: 600; display: flex; align-items: center; justify-content: center; height: 100%;">
                <div style="text-align: center;">
                    <div style="font-size: 2rem;">🎭</div>
                    <div style="margin-top: 8px;">좋아요 & 구독</div>
                </div>
            </div>
        `;
    }
}

function createTimelineClips() {
    const container = document.getElementById('sentence-clips-container');
    container.innerHTML = '';

    config.clips.forEach((clip, index) => {
        const cardElement = createSentenceCard(clip, index);
        container.appendChild(cardElement);
    });

    // 아웃트로 시작 시간 업데이트
    updateOutroTime();

    // 인트로/아웃트로 카드에 클릭 이벤트 추가
    setupIntroOutroClickEvents();
}

/**
 * 인트로/아웃트로 카드 클릭 이벤트 설정
 */
function setupIntroOutroClickEvents() {
    // 인트로 카드
    const introCard = document.querySelector('.intro-card');
    if (introCard) {
        introCard.addEventListener('click', (e) => {
            // 버튼 클릭은 제외
            if (!e.target.closest('button')) {
                selectIntro();
            }
        });

        // 인트로 재생 버튼 이벤트
        const introPlayBtn = document.getElementById('btn-play-intro');
        if (introPlayBtn) {
            introPlayBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                toggleIntroAudioPlayback(introPlayBtn);
            });
        }

        // 인트로 미디어 교체 버튼 이벤트
        const introUploadBtn = document.getElementById('btn-upload-intro-media');
        if (introUploadBtn) {
            introUploadBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                openIntroMediaUpload();
            });
        }

        // 인트로 AI 이미지 생성 버튼 이벤트
        const introAIBtn = document.getElementById('btn-generate-intro-ai');
        if (introAIBtn) {
            introAIBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                generateIntroAIImage();
            });
        }
    }

    // 아웃트로 카드
    const outroCard = document.querySelector('.outro-card');
    if (outroCard) {
        outroCard.addEventListener('click', (e) => {
            // 버튼 클릭은 제외
            if (!e.target.closest('button')) {
                selectOutro();
            }
        });

        // 아웃트로 재생 버튼 이벤트
        const outroPlayBtn = document.getElementById('btn-play-outro');
        if (outroPlayBtn) {
            outroPlayBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                toggleOutroAudioPlayback(outroPlayBtn);
            });
        }

        // 아웃트로 미디어 교체 버튼 이벤트
        const outroUploadBtn = document.getElementById('btn-upload-outro-media');
        if (outroUploadBtn) {
            outroUploadBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                openOutroMediaUpload();
            });
        }

        // 아웃트로 AI 이미지 생성 버튼 이벤트
        const outroAIBtn = document.getElementById('btn-generate-outro-ai');
        if (outroAIBtn) {
            outroAIBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                generateOutroAIImage();
            });
        }
    }
}

/**
 * 아웃트로 시작 시간 계산 및 업데이트
 */
function updateOutroTime() {
    let totalTime = config.global_settings.intro.duration; // 인트로

    // 모든 문장 클립 길이 누적
    config.clips.forEach(clip => {
        const duration = (clip.audio.repeat_count * 3) + clip.audio.pause_after;
        totalTime += duration;
    });

    // 아웃트로 시작 시간 업데이트
    const outroStartElement = document.getElementById('outro-start-time');
    if (outroStartElement) {
        outroStartElement.textContent = formatTime(totalTime);
    }

    // 아웃트로 길이 업데이트
    const outroDurationElement = document.getElementById('outro-duration-display');
    if (outroDurationElement) {
        const outroDuration = config.global_settings.outro.duration;
        outroDurationElement.textContent = `${outroDuration}초`;
    }
}

/**
 * 문장 카드 생성 (VREW 스타일)
 */
function createSentenceCard(clip, index) {
    const cardElement = document.createElement('div');
    cardElement.className = 'sentence-card';
    cardElement.dataset.type = 'sentence';
    cardElement.dataset.index = index;

    // 시간 계산
    const times = calculateClipTimes(index);
    const startTime = formatTime(times.start);
    const duration = times.duration.toFixed(0);

    // 음성 정보
    const firstVoice = clip.audio.tts_voices[0];
    const voiceNames = {
        'alloy': 'Alloy',
        'nova': 'Nova',
        'shimmer': 'Shimmer'
    };

    // 이미지 경로
    const imagePath = getRelativeImagePath(clip.image.path);

    cardElement.innerHTML = `
        <div class="card-header">
            <span class="sentence-number">${index + 1}</span>
            <span class="card-title">${truncateText(clip.sentence_text, 30)}</span>
            <span class="voice-badge">🔊 ${voiceNames[firstVoice]}</span>
            <button class="btn-play-audio" data-index="${index}" title="소리 미리듣기">
                ▶
            </button>
        </div>

        <div class="card-body">
            <div class="sentence-text">
                ${clip.sentence_text}
            </div>

            <div class="thumbnail">
                ${clip.image.path
                    ? `<img src="${imagePath}" alt="${clip.sentence_text}">`
                    : `<div class="thumbnail-placeholder">이미지 없음</div>`
                }
            </div>

            <div class="translation">
                <span class="icon">📄</span>
                <span class="text">${clip.translation}</span>
            </div>

            <div class="time-range">
                <span class="start-time">${startTime}</span>
                <span class="separator">~</span>
                <span class="duration">${duration}초</span>
            </div>
        </div>

        <div class="card-footer">
            <button class="btn-upload-media" data-index="${index}">
                📁 미디어 교체
            </button>
            <button class="btn-generate-ai-image" data-index="${index}">
                ✨ AI 이미지 생성
            </button>
        </div>
    `;

    // 카드 클릭 시 선택
    cardElement.addEventListener('click', (e) => {
        // 버튼 클릭은 제외
        if (!e.target.closest('button')) {
            selectClip(index);
            seekVideoToClip(index, times.start);
        }
    });

    // 재생 버튼 이벤트
    const playBtn = cardElement.querySelector('.btn-play-audio');
    playBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        toggleAudioPlayback(index, playBtn);
    });

    // 미디어 교체 버튼 이벤트
    const uploadBtn = cardElement.querySelector('.btn-upload-media');
    uploadBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        openFileUploadDialog(index);
    });

    // AI 이미지 생성 버튼 이벤트
    const generateBtn = cardElement.querySelector('.btn-generate-ai-image');
    generateBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        generateAIImage(index);
    });

    return cardElement;
}

/**
 * 클립 시작 시간 및 길이 계산
 */
function calculateClipTimes(index) {
    let startTime = config.global_settings.intro.duration; // 인트로 길이

    // 이전 클립들 길이 누적
    for (let i = 0; i < index; i++) {
        const prevClip = config.clips[i];
        const prevDuration = (prevClip.audio.repeat_count * 3) + prevClip.audio.pause_after;
        startTime += prevDuration;
    }

    // 현재 클립 길이
    const currentClip = config.clips[index];
    const duration = (currentClip.audio.repeat_count * 3) + currentClip.audio.pause_after;

    return { start: startTime, duration: duration };
}

/**
 * 비디오를 해당 클립 시작 시점으로 이동
 */
function seekVideoToClip(index, startTime) {
    const video = document.getElementById('preview-video');
    video.currentTime = startTime;

    // 자동 재생 (선택사항)
    // video.play();

    // 선택된 카드 하이라이트
    document.querySelectorAll('.sentence-card').forEach(card => {
        card.classList.remove('active');
    });
    document.querySelector(`.sentence-card[data-index="${index}"]`)?.classList.add('active');
}

/**
 * 절대 경로를 웹 URL로 변환
 * 예: /Users/.../output/resources/images/xxx.png → /output/resources/images/xxx.png
 */
function getRelativeImagePath(fullPath) {
    if (!fullPath) return '';

    // output 폴더 이후의 경로만 추출
    const match = fullPath.match(/\/output\/(.*)/);
    if (match) {
        return `/output/${match[1]}`;
    }

    // output이 없는 경우 (레거시) - daily-english-mecca 이후 경로 사용
    return fullPath.replace(/.*\/daily-english-mecca\//, '/');
}

/**
 * 텍스트 자르기
 */
function truncateText(text, maxLength) {
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
}

// ==================== 인트로/아웃트로 미디어 관리 ====================

/**
 * 인트로 미디어 업로드 다이얼로그 열기
 */
function openIntroMediaUpload() {
    const fileInput = document.createElement('input');
    fileInput.type = 'file';
    fileInput.accept = 'image/*';
    fileInput.className = 'file-input-hidden';

    fileInput.addEventListener('change', async (e) => {
        const file = e.target.files[0];
        if (!file) return;

        // 파일 크기 검증 (50MB 제한)
        if (file.size > 50 * 1024 * 1024) {
            showMessage('error', '파일 크기는 50MB 이하여야 합니다.');
            return;
        }

        // 이미지 타입만 허용
        if (!file.type.startsWith('image/')) {
            showMessage('error', '이미지 파일만 업로드 가능합니다.');
            return;
        }

        await uploadIntroImage(file);
    });

    fileInput.click();
}

/**
 * 아웃트로 미디어 업로드 다이얼로그 열기
 */
function openOutroMediaUpload() {
    const fileInput = document.createElement('input');
    fileInput.type = 'file';
    fileInput.accept = 'image/*';
    fileInput.className = 'file-input-hidden';

    fileInput.addEventListener('change', async (e) => {
        const file = e.target.files[0];
        if (!file) return;

        // 파일 크기 검증 (50MB 제한)
        if (file.size > 50 * 1024 * 1024) {
            showMessage('error', '파일 크기는 50MB 이하여야 합니다.');
            return;
        }

        // 이미지 타입만 허용
        if (!file.type.startsWith('image/')) {
            showMessage('error', '이미지 파일만 업로드 가능합니다.');
            return;
        }

        await uploadOutroImage(file);
    });

    fileInput.click();
}

/**
 * 인트로 이미지 업로드
 */
async function uploadIntroImage(file) {
    try {
        showMessage('info', '인트로 이미지 업로드 중...');

        const formData = new FormData();
        formData.append('file', file);

        const response = await fetch(`/api/video/${videoId}/upload-intro-image`, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }

        const data = await response.json();

        // Config 업데이트
        if (!config.global_settings.intro.custom_image) {
            config.global_settings.intro.custom_image = data.image_path;
        }

        // 썸네일 업데이트
        const introThumbnail = document.getElementById('intro-thumbnail');
        const webPath = getRelativeImagePath(data.image_path);
        introThumbnail.innerHTML = `<img src="${webPath}?t=${Date.now()}" alt="인트로 이미지">`;

        // 편집 패널 이미지도 업데이트
        const introImagePreview = document.getElementById('intro-image-preview');
        if (introImagePreview) {
            introImagePreview.src = webPath + '?t=' + Date.now();
        }

        showMessage('success', '인트로 이미지 업로드 완료!');
        setTimeout(() => hideMessage(), 3000);

        markAsChanged();

    } catch (error) {
        const friendlyMessage = handleApiError(error, '인트로 이미지 업로드');
        showMessage('error', friendlyMessage);
    }
}

/**
 * 아웃트로 이미지 업로드
 */
async function uploadOutroImage(file) {
    try {
        showMessage('info', '아웃트로 이미지 업로드 중...');

        const formData = new FormData();
        formData.append('file', file);

        const response = await fetch(`/api/video/${videoId}/upload-outro-image`, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }

        const data = await response.json();

        // Config 업데이트
        if (!config.global_settings.outro.custom_image) {
            config.global_settings.outro.custom_image = data.image_path;
        }

        // 썸네일 업데이트
        const outroThumbnail = document.getElementById('outro-thumbnail');
        const webPath = getRelativeImagePath(data.image_path);
        outroThumbnail.innerHTML = `<img src="${webPath}?t=${Date.now()}" alt="아웃트로 이미지">`;

        // 편집 패널 이미지도 업데이트
        const outroImagePreview = document.getElementById('outro-image-preview');
        if (outroImagePreview) {
            outroImagePreview.src = webPath + '?t=' + Date.now();
        }

        showMessage('success', '아웃트로 이미지 업로드 완료!');
        setTimeout(() => hideMessage(), 3000);

        markAsChanged();

    } catch (error) {
        const friendlyMessage = handleApiError(error, '아웃트로 이미지 업로드');
        showMessage('error', friendlyMessage);
    }
}

/**
 * 인트로 AI 이미지 생성 (카드 버튼용)
 */
async function generateIntroAIImage() {
    const customPrompt = prompt(
        '인트로 이미지를 생성할 프롬프트를 입력하세요.\n\n※ 비워두면 기본 파란색 배경이 생성됩니다',
        ''
    );

    if (customPrompt === null) return; // 취소

    try {
        showMessage('info', 'AI 이미지 생성 중... (약 10-15초 소요)');

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
            throw new Error(`HTTP ${response.status}`);
        }

        const data = await response.json();

        // Config 업데이트
        if (!config.global_settings.intro.custom_image) {
            config.global_settings.intro.custom_image = data.image_path;
        }

        // 썸네일 업데이트
        const introThumbnail = document.getElementById('intro-thumbnail');
        const webPath = getRelativeImagePath(data.image_path);
        introThumbnail.innerHTML = `<img src="${webPath}?t=${Date.now()}" alt="인트로 이미지">`;

        // 편집 패널 이미지도 업데이트
        const introImagePreview = document.getElementById('intro-image-preview');
        if (introImagePreview) {
            introImagePreview.src = webPath + '?t=' + Date.now();
        }

        showMessage('success', `인트로 이미지 생성 완료! ${data.message}`);
        setTimeout(() => hideMessage(), 3000);

        markAsChanged();

    } catch (error) {
        const friendlyMessage = handleApiError(error, 'AI 이미지 생성');
        showMessage('error', friendlyMessage);
    }
}

/**
 * 아웃트로 AI 이미지 생성 (카드 버튼용)
 */
async function generateOutroAIImage() {
    const customPrompt = prompt(
        '아웃트로 이미지를 생성할 프롬프트를 입력하세요.\n\n※ 비워두면 기본 핑크색 배경이 생성됩니다',
        ''
    );

    if (customPrompt === null) return; // 취소

    try {
        showMessage('info', 'AI 이미지 생성 중... (약 10-15초 소요)');

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
            throw new Error(`HTTP ${response.status}`);
        }

        const data = await response.json();

        // Config 업데이트
        if (!config.global_settings.outro.custom_image) {
            config.global_settings.outro.custom_image = data.image_path;
        }

        // 썸네일 업데이트
        const outroThumbnail = document.getElementById('outro-thumbnail');
        const webPath = getRelativeImagePath(data.image_path);
        outroThumbnail.innerHTML = `<img src="${webPath}?t=${Date.now()}" alt="아웃트로 이미지">`;

        // 편집 패널 이미지도 업데이트
        const outroImagePreview = document.getElementById('outro-image-preview');
        if (outroImagePreview) {
            outroImagePreview.src = webPath + '?t=' + Date.now();
        }

        showMessage('success', `아웃트로 이미지 생성 완료! ${data.message}`);
        setTimeout(() => hideMessage(), 3000);

        markAsChanged();

    } catch (error) {
        const friendlyMessage = handleApiError(error, 'AI 이미지 생성');
        showMessage('error', friendlyMessage);
    }
}

// ==================== 미디어 업로드 ====================

/**
 * 파일 업로드 다이얼로그 열기
 */
function openFileUploadDialog(index) {
    // 파일 input 생성 (동적)
    const fileInput = document.createElement('input');
    fileInput.type = 'file';
    fileInput.accept = 'image/*,video/*,.gif';
    fileInput.className = 'file-input-hidden';

    fileInput.addEventListener('change', async (e) => {
        const file = e.target.files[0];
        if (!file) return;

        // 파일 크기 검증 (50MB 제한)
        if (file.size > 50 * 1024 * 1024) {
            showMessage('error', '파일 크기는 50MB 이하여야 합니다.');
            return;
        }

        // 파일 타입 검증
        const validTypes = ['image/png', 'image/jpeg', 'image/gif', 'video/mp4', 'video/quicktime', 'video/x-msvideo'];
        if (!validTypes.includes(file.type)) {
            showMessage('error', '지원하지 않는 파일 형식입니다. (지원: PNG, JPG, GIF, MP4, MOV, AVI)');
            return;
        }

        // 업로드 시작
        await uploadMediaFile(index, file);
    });

    // 다이얼로그 열기
    fileInput.click();
}

/**
 * 미디어 파일 업로드
 */
async function uploadMediaFile(index, file) {
    try {
        showMessage('info', '미디어 업로드 중...');

        const formData = new FormData();
        formData.append('media', file);

        const response = await fetch(`/api/video/${videoId}/upload-media/${index}`, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            const errorMsg = `HTTP ${response.status}`;
            throw new Error(errorMsg);
        }

        const data = await response.json();

        // Config 업데이트
        config.clips[index].image.path = data.file_path;

        // 썸네일 업데이트
        const card = document.querySelector(`.sentence-card[data-index="${index}"]`);
        const thumbnail = card.querySelector('.thumbnail img');
        if (thumbnail) {
            thumbnail.src = getRelativeImagePath(data.file_path) + '?t=' + Date.now(); // 캐시 방지
        }

        showMessage('success', `미디어 교체 완료! (${data.file_type})`);
        setTimeout(() => hideMessage(), 3000);

        // 변경사항 표시
        markAsChanged();

    } catch (error) {
        const friendlyMessage = handleApiError(error, '미디어 업로드');
        showMessage('error', friendlyMessage);
    }
}

/**
 * AI 이미지 생성
 */
async function generateAIImage(index) {
    const clip = config.clips[index];
    const sentence = clip.sentence_text;

    // 프롬프트 확인
    const customPrompt = prompt(
        `AI 이미지를 생성할 프롬프트를 입력하세요.\n\n기본값: "${sentence}"`,
        sentence
    );

    if (!customPrompt) return; // 취소

    try {
        showMessage('info', 'AI 이미지 생성 중... (약 10-15초 소요)');

        const response = await fetch(`/api/video/${videoId}/generate-clip-image/${index}`, {
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

        // Config 업데이트
        config.clips[index].image.path = data.image_path;

        // 썸네일 업데이트
        const card = document.querySelector(`.sentence-card[data-index="${index}"]`);
        const thumbnail = card.querySelector('.thumbnail img');
        if (thumbnail) {
            thumbnail.src = getRelativeImagePath(data.image_path) + '?t=' + Date.now();
        }

        showMessage('success', `AI 이미지 생성 완료! ${data.message}`);
        setTimeout(() => hideMessage(), 3000);

        // 변경사항 표시
        markAsChanged();

    } catch (error) {
        const friendlyMessage = handleApiError(error, 'AI 이미지 생성');
        showMessage('error', friendlyMessage);
    }
}

// ==================== 오디오 재생 ====================

let currentAudio = null; // 현재 재생 중인 오디오
let currentPlayBtn = null; // 현재 재생 중인 버튼

/**
 * 오디오 재생/일시정지 토글 (문장 클립)
 */
function toggleAudioPlayback(index, playBtn) {
    const clip = config.clips[index];
    const firstVoice = clip.audio.tts_voices[0];

    // 오디오 파일 경로 생성
    const audioPath = `/output/audio/${videoId}/sentence_${index + 1}_${firstVoice}.mp3`;

    // 이미 재생 중인 오디오가 있으면 정지
    if (currentAudio && currentPlayBtn) {
        currentAudio.pause();
        currentAudio.currentTime = 0;
        currentPlayBtn.classList.remove('playing');
        currentPlayBtn.textContent = '▶';

        // 같은 버튼을 다시 클릭한 경우
        if (currentPlayBtn === playBtn) {
            currentAudio = null;
            currentPlayBtn = null;
            return;
        }
    }

    // 새 오디오 생성 및 재생
    const audio = new Audio(audioPath);

    audio.addEventListener('loadeddata', () => {
        audio.play();
        playBtn.classList.add('playing');
        playBtn.textContent = '⏸';

        currentAudio = audio;
        currentPlayBtn = playBtn;
    });

    audio.addEventListener('ended', () => {
        playBtn.classList.remove('playing');
        playBtn.textContent = '▶';
        currentAudio = null;
        currentPlayBtn = null;
    });

    audio.addEventListener('error', (e) => {
        console.error('오디오 로드 실패:', audioPath, e);
        showMessage('error', '오디오 파일을 찾을 수 없습니다.');
        playBtn.classList.remove('playing');
        playBtn.textContent = '▶';
        currentAudio = null;
        currentPlayBtn = null;
    });
}

/**
 * 인트로 오디오 재생/일시정지 토글
 * (비디오를 인트로 시작 시점으로 이동 및 재생)
 */
function toggleIntroAudioPlayback(playBtn) {
    const video = document.getElementById('preview-video');

    // 비디오를 인트로 시작 시점(0초)으로 이동
    video.currentTime = 0;

    // 비디오 재생
    video.play().then(() => {
        showMessage('info', '비디오가 인트로 시작 시점으로 이동되었습니다.');
        setTimeout(() => hideMessage(), 2000);
    }).catch((e) => {
        console.error('비디오 재생 실패:', e);
        showMessage('error', '비디오 재생에 실패했습니다.');
    });
}

/**
 * 아웃트로 오디오 재생/일시정지 토글
 * (비디오를 아웃트로 시작 시점으로 이동 및 재생)
 */
function toggleOutroAudioPlayback(playBtn) {
    const video = document.getElementById('preview-video');

    // 아웃트로 시작 시간 계산
    let totalTime = config.global_settings.intro.duration; // 인트로

    // 모든 문장 클립 길이 누적
    config.clips.forEach(clip => {
        const duration = (clip.audio.repeat_count * 3) + clip.audio.pause_after;
        totalTime += duration;
    });

    // 비디오를 아웃트로 시작 시점으로 이동
    video.currentTime = totalTime;

    // 비디오 재생
    video.play().then(() => {
        showMessage('info', '비디오가 아웃트로 시작 시점으로 이동되었습니다.');
        setTimeout(() => hideMessage(), 2000);
    }).catch((e) => {
        console.error('비디오 재생 실패:', e);
        showMessage('error', '비디오 재생에 실패했습니다.');
    });
}

// ==================== 클립/인트로/아웃트로 선택 ====================

function selectClip(index) {
    selectedClipIndex = index;

    // 모든 카드에서 active 제거
    document.querySelectorAll('.sentence-card').forEach(card => {
        card.classList.remove('active');
    });

    // 선택된 카드에 active 추가
    const selectedCard = document.querySelector(`.sentence-card[data-index="${index}"]`);
    if (selectedCard) {
        selectedCard.classList.add('active');
    }

    // 모든 설정 섹션 숨기기
    hideAllSettingSections();

    // 클립 설정 표시
    displayClipSettings(index);
}

function selectIntro() {
    selectedClipIndex = null;

    // 모든 카드에서 active 제거
    document.querySelectorAll('.sentence-card').forEach(card => {
        card.classList.remove('active');
    });

    // 인트로 카드에 active 추가
    const introCard = document.querySelector('.intro-card');
    if (introCard) {
        introCard.classList.add('active');
    }

    // 모든 설정 섹션 숨기기
    hideAllSettingSections();

    // 인트로 설정 표시
    displayIntroSettings();
}

function selectOutro() {
    selectedClipIndex = null;

    // 모든 카드에서 active 제거
    document.querySelectorAll('.sentence-card').forEach(card => {
        card.classList.remove('active');
    });

    // 아웃트로 카드에 active 추가
    const outroCard = document.querySelector('.outro-card');
    if (outroCard) {
        outroCard.classList.add('active');
    }

    // 모든 설정 섹션 숨기기
    hideAllSettingSections();

    // 아웃트로 설정 표시
    displayOutroSettings();
}

/**
 * 모든 설정 섹션 숨기기
 */
function hideAllSettingSections() {
    document.getElementById('global-settings').style.display = 'none';
    document.getElementById('intro-settings').style.display = 'none';
    document.getElementById('outro-settings').style.display = 'none';
    document.getElementById('clip-settings').style.display = 'none';
}

function displayIntroSettings() {
    const introSettings = config.global_settings.intro;

    // 인트로 설정 섹션 표시
    document.getElementById('intro-settings').style.display = 'block';

    // 인트로 길이
    const introDurationSelect = document.getElementById('intro-duration');
    introDurationSelect.value = introSettings.duration;

    // 인트로 이미지
    const introImagePreview = document.getElementById('intro-image-preview');
    const introImagePath = introSettings.custom_image || introSettings.default_image;

    if (introImagePath) {
        const webPath = getRelativeImagePath(introImagePath);
        introImagePreview.src = webPath;
    } else {
        introImagePreview.src = '';
    }
}

function displayOutroSettings() {
    const outroSettings = config.global_settings.outro;

    // 아웃트로 설정 섹션 표시
    document.getElementById('outro-settings').style.display = 'block';

    // 아웃트로 길이
    const outroDurationSelect = document.getElementById('outro-duration');
    outroDurationSelect.value = outroSettings.duration;

    // 아웃트로 이미지
    const outroImagePreview = document.getElementById('outro-image-preview');
    const outroImagePath = outroSettings.custom_image || outroSettings.default_image;

    if (outroImagePath) {
        const webPath = getRelativeImagePath(outroImagePath);
        outroImagePreview.src = webPath;
    } else {
        outroImagePreview.src = '';
    }
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
        // 이미지 경로를 웹 URL로 변환
        const webPath = getRelativeImagePath(clip.image.path);
        clipImage.src = webPath;
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
    document.getElementById('btn-download').addEventListener('click', onDownload);
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

function onDownload() {
    const videoElement = document.getElementById('preview-video');
    const videoSrc = videoElement.src;

    if (!videoSrc || videoSrc === '') {
        showMessage('error', '다운로드할 비디오가 없습니다.');
        return;
    }

    // 비디오 파일명 생성
    const filename = `daily_english_${videoId}.mp4`;

    // 다운로드 링크 생성
    const a = document.createElement('a');
    a.href = videoSrc;
    a.download = filename;
    a.style.display = 'none';
    document.body.appendChild(a);

    // 다운로드 트리거
    a.click();

    // 링크 제거
    document.body.removeChild(a);

    showMessage('success', '비디오 다운로드를 시작합니다.');
    setTimeout(() => hideMessage(), 3000);
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

        // Config 업데이트
        if (!config.global_settings.intro.custom_image) {
            config.global_settings.intro.custom_image = data.image_path;
        }

        // 썸네일 업데이트
        const introThumbnail = document.getElementById('intro-thumbnail');
        const webPath = getRelativeImagePath(data.image_path);
        introThumbnail.innerHTML = `<img src="${webPath}?t=${Date.now()}" alt="인트로 이미지">`;

        showMessage('success', `인트로 이미지 생성 완료! ${data.message}`);
        setTimeout(() => hideMessage(), 3000);

        // 프롬프트 입력 초기화
        promptInput.value = '';

        // 변경사항 표시
        markAsChanged();

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

        // Config 업데이트
        if (!config.global_settings.outro.custom_image) {
            config.global_settings.outro.custom_image = data.image_path;
        }

        // 썸네일 업데이트
        const outroThumbnail = document.getElementById('outro-thumbnail');
        const webPath = getRelativeImagePath(data.image_path);
        outroThumbnail.innerHTML = `<img src="${webPath}?t=${Date.now()}" alt="아웃트로 이미지">`;

        showMessage('success', `아웃트로 이미지 생성 완료! ${data.message}`);
        setTimeout(() => hideMessage(), 3000);

        // 프롬프트 입력 초기화
        promptInput.value = '';

        // 변경사항 표시
        markAsChanged();

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
