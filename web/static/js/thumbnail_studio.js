/**
 * YouTube Thumbnail Studio - JavaScript
 * Author: Kelly & Claude Code
 * Date: 2025-11-09
 */

// ============================================================
// 전역 변수
// ============================================================
let currentSessionId = null;
let currentVersion = 1;
let selectedStyle = 'fire_english';  // 기본값: Fire English 스타일
let currentThumbnailData = null;  // 현재 생성된 썸네일 데이터 (텍스트 수정용)

// ============================================================
// 초기화
// ============================================================
document.addEventListener('DOMContentLoaded', () => {
    initializeTabs();
    initializeFormHandlers();
    initializeStyleSelection();
    initializeColorPickers();
    initializeCheckboxHandlers();
    initializeButtons();

    console.log('✅ Thumbnail Studio 초기화 완료');
});

// ============================================================
// 탭 전환
// ============================================================
function initializeTabs() {
    const tabButtons = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');

    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            const tabName = button.getAttribute('data-tab');

            // 모든 탭 비활성화
            tabButtons.forEach(btn => btn.classList.remove('active'));
            tabContents.forEach(content => content.classList.remove('active'));

            // 선택된 탭 활성화
            button.classList.add('active');
            document.getElementById(`tab-${tabName}`).classList.add('active');
        });
    });
}

// ============================================================
// 폼 핸들러
// ============================================================
function initializeFormHandlers() {
    // 메인 텍스트 글자 수 카운터
    const mainText = document.getElementById('main-text');
    const mainCharCount = mainText.nextElementSibling;

    mainText.addEventListener('input', (e) => {
        const count = e.target.value.length;
        mainCharCount.textContent = `${count}/30`;
    });

    // 서브 텍스트 글자 수 카운터
    const subtitleText = document.getElementById('subtitle-text');
    const subtitleCharCount = subtitleText.nextElementSibling;

    subtitleText.addEventListener('input', (e) => {
        const count = e.target.value.length;
        subtitleCharCount.textContent = `${count}/40`;
    });

    // 참고 이미지 미리보기
    const referenceImage = document.getElementById('reference-image');
    const referencePreview = document.getElementById('reference-preview');

    referenceImage.addEventListener('change', (e) => {
        const file = e.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = (event) => {
                referencePreview.querySelector('img').src = event.target.result;
                referencePreview.classList.remove('hidden');
            };
            reader.readAsDataURL(file);
        }
    });

    // 참고 이미지 제거
    const btnRemove = referencePreview.querySelector('.btn-remove');
    btnRemove.addEventListener('click', () => {
        referenceImage.value = '';
        referencePreview.classList.add('hidden');
    });
}

// ============================================================
// 스타일 선택
// ============================================================
function initializeStyleSelection() {
    const styleCards = document.querySelectorAll('.style-card');

    styleCards.forEach(card => {
        card.addEventListener('click', () => {
            // 모든 카드 비활성화
            styleCards.forEach(c => c.classList.remove('active'));

            // 선택된 카드 활성화
            card.classList.add('active');
            selectedStyle = card.getAttribute('data-style');

            console.log(`스타일 선택: ${selectedStyle}`);
        });
    });
}

// ============================================================
// 색상 선택기
// ============================================================
function initializeColorPickers() {
    const colorPickers = document.querySelectorAll('.color-picker input[type="color"]');

    colorPickers.forEach(picker => {
        const hexInput = picker.nextElementSibling;

        // 색상 변경 시 HEX 값 업데이트
        picker.addEventListener('input', (e) => {
            hexInput.value = e.target.value.toUpperCase();
        });
    });
}

// ============================================================
// 체크박스 핸들러
// ============================================================
function initializeCheckboxHandlers() {
    // 문장 개수 배지
    const sentenceBadgeCheckbox = document.getElementById('show-sentence-badge');
    const sentenceCountInput = document.getElementById('sentence-count');

    sentenceBadgeCheckbox.addEventListener('change', (e) => {
        sentenceCountInput.disabled = !e.target.checked;
        if (e.target.checked) {
            sentenceCountInput.focus();
        }
    });

    // 영상 길이 배지
    const durationBadgeCheckbox = document.getElementById('show-duration-badge');
    const durationInput = document.getElementById('video-duration');

    durationBadgeCheckbox.addEventListener('change', (e) => {
        durationInput.disabled = !e.target.checked;
        if (e.target.checked) {
            durationInput.focus();
        }
    });
}

// ============================================================
// 버튼 이벤트
// ============================================================
function initializeButtons() {
    // YouTube URL 분석
    document.getElementById('btn-analyze-url').addEventListener('click', analyzeYouTubeURL);

    // 채널 URL 분석 (NEW)
    document.getElementById('btn-analyze-channel').addEventListener('click', analyzeChannelURL);

    // 썸네일 생성
    document.getElementById('btn-generate').addEventListener('click', generateThumbnail);

    // 채널 프로필 저장
    document.getElementById('btn-save-profile').addEventListener('click', saveChannelProfile);

    // 재생성 버튼들
    document.getElementById('btn-download').addEventListener('click', downloadThumbnail);
    document.getElementById('btn-edit-text').addEventListener('click', openTextEditModal);
    document.getElementById('btn-regen-color').addEventListener('click', () => regenerateThumbnail('color'));
    document.getElementById('btn-regen-layout').addEventListener('click', () => regenerateThumbnail('layout'));
    document.getElementById('btn-regen-complete').addEventListener('click', () => regenerateThumbnail('complete'));

    // 텍스트 수정 모달
    document.getElementById('btn-cancel-edit').addEventListener('click', closeTextEditModal);
    document.getElementById('btn-apply-edit').addEventListener('click', applyTextEdit);
}

// ============================================================
// YouTube URL 분석
// ============================================================
async function analyzeYouTubeURL() {
    const url = document.getElementById('youtube-url').value.trim();

    if (!url) {
        showToast('YouTube URL을 입력해주세요', 'warning');
        return;
    }

    showLoading('YouTube URL 분석 중...');

    try {
        const response = await fetch('/thumbnail-studio/api/analyze-url', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ url })
        });

        const data = await response.json();

        if (response.ok && data.success) {
            // 제목을 메인 텍스트에 자동 입력
            if (data.metadata.title) {
                const mainText = data.metadata.title.substring(0, 30);
                document.getElementById('main-text').value = mainText;
                document.querySelector('#main-text + .char-count').textContent = `${mainText.length}/30`;
            }

            // 영상 길이 자동 입력
            if (data.metadata.duration_string) {
                document.getElementById('show-duration-badge').checked = true;
                document.getElementById('video-duration').disabled = false;
                document.getElementById('video-duration').value = data.metadata.duration_string;
            }

            showToast('✅ URL 분석 완료', 'success');
        } else {
            showToast(data.error || 'URL 분석 실패', 'error');
        }
    } catch (error) {
        console.error('URL 분석 오류:', error);
        showToast('URL 분석 중 오류가 발생했습니다', 'error');
    } finally {
        hideLoading();
    }
}

// ============================================================
// 채널 URL 분석 (NEW)
// ============================================================
async function analyzeChannelURL() {
    const channelUrl = document.getElementById('channel-url').value.trim();

    if (!channelUrl) {
        showToast('채널 URL을 입력해주세요', 'warning');
        return;
    }

    showLoading('채널 정보 추출 중...');

    try {
        const response = await fetch('/thumbnail-studio/api/analyze-channel', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ channel_url: channelUrl })
        });

        const data = await response.json();

        if (response.ok && data.success && data.channel_info) {
            const channelInfo = data.channel_info;

            // 채널 이름 자동 입력
            if (channelInfo.channel_name) {
                document.getElementById('channel-name').value = channelInfo.channel_name;
            }

            // 채널 아이콘 미리보기
            if (channelInfo.icon_path) {
                const iconPreview = document.getElementById('channel-icon-preview');
                iconPreview.querySelector('img').src = channelInfo.icon_path;
                iconPreview.querySelector('.icon-name').textContent = channelInfo.channel_name;
                iconPreview.classList.remove('hidden');
            }

            showToast(`✅ 채널 정보 추출 완료: ${channelInfo.channel_name}`, 'success');
        } else {
            showToast(data.error || '채널 정보 추출 실패', 'error');
        }
    } catch (error) {
        console.error('채널 정보 추출 오류:', error);
        showToast('채널 정보 추출 중 오류가 발생했습니다', 'error');
    } finally {
        hideLoading();
    }
}

// ============================================================
// 썸네일 생성
// ============================================================
async function generateThumbnail() {
    const mainText = document.getElementById('main-text').value.trim();

    if (!mainText) {
        showToast('메인 텍스트는 필수입니다', 'warning');
        document.getElementById('main-text').focus();
        return;
    }

    showLoading('TED 스타일 썸네일 생성 중... (10-15초 소요)');

    try {
        // FormData 생성
        const formData = new FormData();
        formData.append('main_text', mainText);
        formData.append('subtitle_text', document.getElementById('subtitle-text').value.trim());
        formData.append('style', selectedStyle);

        // YouTube URL 및 채널 URL (NEW)
        formData.append('youtube_url', document.getElementById('youtube-url').value.trim());
        formData.append('channel_url', document.getElementById('channel-url').value.trim());

        // 텍스트 위치 (NEW)
        const textPosition = document.querySelector('input[name="text-position"]:checked').value;
        formData.append('text_position', textPosition);

        // 배지 옵션
        if (document.getElementById('show-sentence-badge').checked) {
            formData.append('sentence_count', document.getElementById('sentence-count').value);
        }

        if (document.getElementById('show-duration-badge').checked) {
            formData.append('video_duration', document.getElementById('video-duration').value);
        }

        // 브랜드 색상
        formData.append('brand_color_primary', document.getElementById('brand-color-primary').value);
        formData.append('brand_color_secondary', document.getElementById('brand-color-secondary').value);
        formData.append('brand_color_accent', document.getElementById('brand-color-accent').value);

        // Kelly 캐릭터 사용 여부
        formData.append('use_kelly', document.getElementById('use-kelly-character').checked);

        // 참고 이미지
        const referenceImage = document.getElementById('reference-image').files[0];
        if (referenceImage) {
            formData.append('reference_image', referenceImage);
        }

        // API 호출
        const response = await fetch('/thumbnail-studio/api/generate', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (response.ok && data.success) {
            currentSessionId = data.session_id;

            // 현재 썸네일 데이터 저장 (텍스트 수정용)
            currentThumbnailData = {
                main_text: mainText,
                subtitle_text: document.getElementById('subtitle-text').value.trim(),
                style: selectedStyle,
                youtube_url: document.getElementById('youtube-url').value.trim(),
                channel_url: document.getElementById('channel-url').value.trim(),
                text_position: document.querySelector('input[name="text-position"]:checked').value,
                sentence_count: document.getElementById('show-sentence-badge').checked ? document.getElementById('sentence-count').value : null,
                video_duration: document.getElementById('show-duration-badge').checked ? document.getElementById('video-duration').value : null,
                brand_color_primary: document.getElementById('brand-color-primary').value,
                brand_color_secondary: document.getElementById('brand-color-secondary').value,
                brand_color_accent: document.getElementById('brand-color-accent').value,
                use_kelly: document.getElementById('use-kelly-character').checked
            };

            // 3개의 썸네일이 생성된 경우 선택 UI 표시
            if (data.count && data.count > 1 && data.thumbnail_urls) {
                displayThumbnailSelection(data.thumbnail_urls, data.versions);
                showToast(`✅ ${data.count}개 썸네일 생성 완료! 마음에 드는 것을 선택하세요.`, 'success');
            } else {
                // 1개만 생성된 경우 기존 로직
                currentVersion = data.versions ? data.versions[0] : data.version;
                displayThumbnail(data.thumbnail_urls ? data.thumbnail_urls[0] : data.thumbnail_url);
                document.getElementById('regeneration-options').classList.remove('hidden');
                loadHistory(currentSessionId);
                showToast('✅ 썸네일 생성 완료!', 'success');
            }
        } else {
            showToast(data.error || '썸네일 생성 실패', 'error');
        }
    } catch (error) {
        console.error('썸네일 생성 오류:', error);
        showToast('썸네일 생성 중 오류가 발생했습니다', 'error');
    } finally {
        hideLoading();
    }
}

// ============================================================
// 썸네일 재생성
// ============================================================
async function regenerateThumbnail(variationType) {
    if (!currentSessionId) {
        showToast('먼저 썸네일을 생성해주세요', 'warning');
        return;
    }

    const messages = {
        'color': '색상 변경 중... (5초)',
        'layout': '레이아웃 변경 중... (8초)',
        'complete': '완전히 새로 생성 중... (15초)'
    };

    showLoading(messages[variationType]);

    try {
        const response = await fetch('/thumbnail-studio/api/regenerate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                session_id: currentSessionId,
                current_version: currentVersion,
                variation_type: variationType
            })
        });

        const data = await response.json();

        if (response.ok && data.success) {
            currentVersion = data.version;

            // 새 썸네일 표시
            displayThumbnail(data.thumbnail_url);

            // 히스토리 업데이트
            loadHistory(currentSessionId);

            showToast('✅ 새 버전 생성 완료!', 'success');
        } else {
            showToast(data.error || '재생성 실패', 'error');
        }
    } catch (error) {
        console.error('재생성 오류:', error);
        showToast('재생성 중 오류가 발생했습니다', 'error');
    } finally {
        hideLoading();
    }
}

// ============================================================
// 썸네일 표시
// ============================================================
function displayThumbnail(thumbnailUrl) {
    const preview = document.getElementById('thumbnail-preview');

    // 기존 placeholder 제거
    preview.innerHTML = '';

    // 이미지 표시
    const img = document.createElement('img');
    img.src = thumbnailUrl;
    img.alt = '생성된 썸네일';
    preview.appendChild(img);
}

// ============================================================
// 3개 썸네일 선택 UI 표시 (NEW)
// ============================================================
function displayThumbnailSelection(thumbnailUrls, versions) {
    const preview = document.getElementById('thumbnail-preview');
    preview.innerHTML = '';

    // 선택 안내 메시지
    const header = document.createElement('div');
    header.className = 'selection-header';
    header.innerHTML = `
        <h3>✨ 썸네일 생성 완료! 마음에 드는 버전을 선택하세요</h3>
        <p>동영상의 다른 장면에서 추출한 3개의 썸네일입니다</p>
    `;
    preview.appendChild(header);

    // 썸네일 그리드
    const grid = document.createElement('div');
    grid.className = 'thumbnail-selection-grid';

    thumbnailUrls.forEach((url, index) => {
        const card = document.createElement('div');
        card.className = 'thumbnail-option';
        card.dataset.version = versions[index];

        card.innerHTML = `
            <div class="thumbnail-option-wrapper">
                <img src="${url}" alt="썸네일 옵션 ${index + 1}">
                <div class="thumbnail-option-overlay">
                    <span class="thumbnail-option-label">버전 ${index + 1}</span>
                </div>
            </div>
            <label class="thumbnail-option-select">
                <input type="radio" name="thumbnail-choice" value="${versions[index]}" ${index === 1 ? 'checked' : ''}>
                <span>선택</span>
            </label>
        `;

        // 클릭 시 선택
        card.addEventListener('click', () => {
            const radio = card.querySelector('input[type="radio"]');
            radio.checked = true;

            // 다른 카드 비활성화
            document.querySelectorAll('.thumbnail-option').forEach(c => {
                c.classList.remove('selected');
            });
            card.classList.add('selected');
        });

        // 기본 선택 (중간 버전)
        if (index === 1) {
            card.classList.add('selected');
        }

        grid.appendChild(card);
    });

    preview.appendChild(grid);

    // 액션 버튼들 (가로 배치)
    const actions = document.createElement('div');
    actions.className = 'selection-actions';
    actions.innerHTML = `
        <button id="btn-download-selected" class="btn-primary">
            📥 다운로드
        </button>
        <button id="btn-edit-selected-text" class="btn-primary">
            ✏️ 텍스트 수정
        </button>
        <button id="btn-regenerate-new" class="btn-secondary">
            🔄 새로 생성
        </button>
    `;
    preview.appendChild(actions);

    // 이벤트 리스너
    document.getElementById('btn-download-selected').addEventListener('click', downloadSelectedThumbnail);
    document.getElementById('btn-edit-selected-text').addEventListener('click', openTextEditModal);
    document.getElementById('btn-regenerate-new').addEventListener('click', () => {
        if (confirm('새로 생성하시겠습니까?')) {
            location.reload();
        }
    });
}

// ============================================================
// 선택한 썸네일 다운로드 (NEW)
// ============================================================
function downloadSelectedThumbnail() {
    const selectedRadio = document.querySelector('input[name="thumbnail-choice"]:checked');

    if (!selectedRadio) {
        showToast('썸네일을 선택해주세요', 'warning');
        return;
    }

    const selectedVersion = selectedRadio.value;
    const downloadUrl = `/thumbnail-studio/api/download/${currentSessionId}/v${selectedVersion}`;

    // 다운로드 트리거
    const a = document.createElement('a');
    a.href = downloadUrl;
    a.download = `thumbnail_v${selectedVersion}.png`;
    a.style.display = 'none';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);

    // 선택한 버전을 현재 버전으로 설정
    currentVersion = parseInt(selectedVersion);

    showToast('✅ 썸네일 다운로드 시작!', 'success');

    // 2초 후 단일 미리보기로 전환
    setTimeout(() => {
        const thumbnailUrl = `/thumbnail-studio/api/download/${currentSessionId}/v${selectedVersion}`;
        displayThumbnail(thumbnailUrl);
        document.getElementById('regeneration-options').classList.remove('hidden');
        loadHistory(currentSessionId);
    }, 2000);
}

// ============================================================
// 히스토리 로드
// ============================================================
async function loadHistory(sessionId) {
    try {
        const response = await fetch(`/thumbnail-studio/api/history/${sessionId}`);
        const data = await response.json();

        if (response.ok && data.thumbnails) {
            const historyContainer = document.getElementById('thumbnail-history');
            historyContainer.innerHTML = '';

            // 최신 버전부터 표시 (역순)
            const thumbnails = [...data.thumbnails].reverse();

            thumbnails.forEach(thumb => {
                const item = document.createElement('div');
                item.className = 'history-item';
                if (thumb.version === currentVersion) {
                    item.classList.add('current');
                }

                item.innerHTML = `
                    <img src="${thumb.url}" alt="버전 ${thumb.version}">
                    <div class="history-item-info">
                        <strong>v${thumb.version}</strong>
                        ${thumb.variation_type ? `<br><small>${thumb.variation_type}</small>` : ''}
                    </div>
                `;

                // 클릭하면 해당 버전으로 전환
                item.addEventListener('click', () => {
                    currentVersion = thumb.version;
                    displayThumbnail(thumb.url);

                    // 현재 표시 업데이트
                    document.querySelectorAll('.history-item').forEach(i => i.classList.remove('current'));
                    item.classList.add('current');
                });

                historyContainer.appendChild(item);
            });

            // 히스토리 카운트 업데이트
            document.getElementById('history-count').textContent = thumbnails.length;
        }
    } catch (error) {
        console.error('히스토리 로드 오류:', error);
    }
}

// ============================================================
// 썸네일 다운로드
// ============================================================
function downloadThumbnail() {
    if (!currentSessionId || !currentVersion) {
        showToast('다운로드할 썸네일이 없습니다', 'warning');
        return;
    }

    const downloadUrl = `/thumbnail-studio/api/download/${currentSessionId}/v${currentVersion}`;

    // 다운로드 링크 생성 및 클릭
    const a = document.createElement('a');
    a.href = downloadUrl;
    a.download = `thumbnail_v${currentVersion}.png`;
    a.style.display = 'none';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);

    showToast('📥 다운로드 시작', 'success');
}

// ============================================================
// 채널 프로필 저장
// ============================================================
async function saveChannelProfile() {
    const profileData = {
        channel_name: document.getElementById('channel-name').value,
        brand_colors: {
            primary: document.getElementById('brand-color-primary').value,
            secondary: document.getElementById('brand-color-secondary').value,
            accent: document.getElementById('brand-color-accent').value
        },
        use_kelly: document.getElementById('use-kelly-character').checked
    };

    try {
        const response = await fetch('/thumbnail-studio/api/channel-profile', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(profileData)
        });

        const data = await response.json();

        if (response.ok && data.success) {
            showToast('✅ 채널 프로필 저장 완료', 'success');
        } else {
            showToast(data.error || '프로필 저장 실패', 'error');
        }
    } catch (error) {
        console.error('프로필 저장 오류:', error);
        showToast('프로필 저장 중 오류가 발생했습니다', 'error');
    }
}

// ============================================================
// UI 헬퍼 함수
// ============================================================
function showLoading(message) {
    const overlay = document.getElementById('loading-overlay');
    const messageEl = document.getElementById('loading-message');

    messageEl.textContent = message;
    overlay.classList.remove('hidden');
}

function hideLoading() {
    const overlay = document.getElementById('loading-overlay');
    overlay.classList.add('hidden');
}

function showToast(message, type = 'info') {
    const toast = document.getElementById('toast');

    toast.textContent = message;
    toast.className = `toast ${type}`;
    toast.classList.remove('hidden');

    // 3초 후 자동 숨김
    setTimeout(() => {
        toast.classList.add('hidden');
    }, 3000);
}

// ============================================================
// 텍스트 수정 모달
// ============================================================
function openTextEditModal() {
    if (!currentThumbnailData) {
        showToast('먼저 썸네일을 생성해주세요', 'warning');
        return;
    }

    // 현재 텍스트 값으로 입력 필드 채우기
    document.getElementById('edit-main-text').value = currentThumbnailData.main_text || '';
    document.getElementById('edit-subtitle-text').value = currentThumbnailData.subtitle_text || '';

    // 모달 표시
    document.getElementById('text-edit-modal').classList.remove('hidden');

    console.log('✅ 텍스트 수정 모달 열림');
}

function closeTextEditModal() {
    document.getElementById('text-edit-modal').classList.add('hidden');
}

async function applyTextEdit() {
    const mainText = document.getElementById('edit-main-text').value.trim();
    const subtitleText = document.getElementById('edit-subtitle-text').value.trim();

    if (!mainText) {
        showToast('메인 텍스트를 입력해주세요', 'warning');
        return;
    }

    // 모달 닫기
    closeTextEditModal();

    // 새 텍스트로 썸네일 재생성
    showLoading('새 텍스트로 썸네일 재생성 중...');

    try {
        // FormData 생성 (백엔드가 FormData를 기대함)
        const formData = new FormData();
        formData.append('main_text', mainText);
        formData.append('subtitle_text', subtitleText);
        formData.append('style', currentThumbnailData.style || 'fire_english');
        formData.append('text_position', currentThumbnailData.text_position || 'center');

        // 기존 세션 ID 전달 (배경 이미지 재사용)
        if (currentSessionId) {
            formData.append('session_id', currentSessionId);
            console.log('📝 텍스트 수정 모드: 기존 세션 재사용 →', currentSessionId);
        }

        // YouTube URL은 텍스트 수정 시 제외 (새로 프레임 추출 방지, 1개만 생성)
        // 채널 URL도 제외 (아이콘 다시 로드 방지)
        console.log('📝 텍스트 수정 모드: YouTube URL 제외 (1개 썸네일만 생성)');

        // 배지 옵션
        if (currentThumbnailData.sentence_count) {
            formData.append('sentence_count', currentThumbnailData.sentence_count);
        }
        if (currentThumbnailData.video_duration) {
            formData.append('video_duration', currentThumbnailData.video_duration);
        }

        // 브랜드 색상
        if (currentThumbnailData.brand_color_primary) {
            formData.append('brand_color_primary', currentThumbnailData.brand_color_primary);
        }
        if (currentThumbnailData.brand_color_secondary) {
            formData.append('brand_color_secondary', currentThumbnailData.brand_color_secondary);
        }
        if (currentThumbnailData.brand_color_accent) {
            formData.append('brand_color_accent', currentThumbnailData.brand_color_accent);
        }

        // Kelly 캐릭터
        if (currentThumbnailData.use_kelly !== undefined) {
            formData.append('use_kelly', currentThumbnailData.use_kelly);
        }

        const response = await fetch('/thumbnail-studio/api/generate', {
            method: 'POST',
            body: formData  // JSON이 아닌 FormData로 전송
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || '썸네일 재생성 실패');
        }

        const data = await response.json();

        console.log('✅ 백엔드 응답:', data);

        // 현재 썸네일 데이터 업데이트
        currentThumbnailData.main_text = mainText;
        currentThumbnailData.subtitle_text = subtitleText;

        // 세션 ID 및 버전 업데이트
        if (data.session_id) {
            currentSessionId = data.session_id;
        }

        // 응답 처리 (3가지 경우)
        if (data.success && data.count && data.count > 1 && data.thumbnail_urls) {
            // 경우 1: 3개 썸네일 생성된 경우 (YouTube URL 포함)
            console.log('📸 3개 썸네일 생성됨:', data.thumbnail_urls);

            if (data.versions) {
                displayThumbnailSelection(data.thumbnail_urls, data.versions);
                showToast(`✅ ${data.count}개 썸네일 생성 완료! 마음에 드는 것을 선택하세요.`, 'success');
            }
        } else if (data.thumbnail_url || data.thumbnail_urls) {
            // 경우 2: 1개 썸네일 생성된 경우
            const thumbnailUrl = data.thumbnail_url || (data.thumbnail_urls && data.thumbnail_urls[0]);

            console.log('📸 1개 썸네일 생성됨:', thumbnailUrl);

            if (data.version) {
                currentVersion = data.version;
            } else if (data.versions && data.versions[0]) {
                currentVersion = data.versions[0];
            }

            displayThumbnail(thumbnailUrl);

            // 히스토리 새로고침 (세션이 있으면)
            if (currentSessionId) {
                loadHistory(currentSessionId);
            }

            // 재생성 옵션 표시
            document.getElementById('regeneration-options').classList.remove('hidden');
        } else {
            // 경우 3: 썸네일 URL을 못 받은 경우
            console.error('❌ 응답 데이터:', data);

            // 더 자세한 에러 메시지
            let errorMsg = '썸네일 URL을 받지 못했습니다.';
            if (data.error) {
                errorMsg = data.error;
            } else if (!data.success) {
                errorMsg = '썸네일 생성에 실패했습니다. 잠시 후 다시 시도해주세요.';
            }

            throw new Error(errorMsg);
        }

        hideLoading();

        // 성공 메시지는 1개 생성 시에만 표시 (3개 생성 시는 선택 UI에서 표시)
        if (!(data.count && data.count > 1)) {
            showToast('텍스트가 수정되었습니다!', 'success');
        }

        console.log('✅ 텍스트 수정 완료:', { mainText, subtitleText });

    } catch (error) {
        console.error('❌ 텍스트 수정 실패:', error);
        hideLoading();
        showToast(error.message, 'error');
    }
}
