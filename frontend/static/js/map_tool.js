// static/js/secret_map.js
document.addEventListener('DOMContentLoaded', function() {
    // --- 游戏内坐标系定义 ---
    const GAME_COORD = {
        X_MIN: 420,
        X_MAX: 1500,
        Y_MIN: 0,
        Y_MAX: 1080
    };
    GAME_COORD.X_RANGE = GAME_COORD.X_MAX - GAME_COORD.X_MIN;
    GAME_COORD.Y_RANGE = GAME_COORD.Y_MAX - GAME_COORD.Y_MIN;

    // --- DOM 元素 ---
    const mapSelect = document.getElementById('map-select');
    const mapContainer = document.getElementById('map-container');
    const mapImage = document.getElementById('map-image');
    const mapLoader = document.getElementById('map-loader');

    const clickedCoordsDisplay = document.getElementById('clicked-coords-display');

    const playerXInput = document.getElementById('player-x');
    const playerYInput = document.getElementById('player-y');
    const markPlayerBtn = document.getElementById('mark-player-btn');
    const playerMarker = document.getElementById('player-marker');

    const targetXInput = document.getElementById('target-x');
    const targetYInput = document.getElementById('target-y');
    const findSecretBtn = document.getElementById('find-secret-btn');

    const secretMarkersContainer = document.getElementById('secret-markers-container');
    const secretInfoPanel = document.getElementById('secret-info-panel');
    const secretLoader = document.getElementById('secret-loader');
    const secretContent = document.getElementById('secret-content');
    const secretPlaceholder = document.getElementById('secret-placeholder');
    const secretImage = document.getElementById('secret-image');
    const secretName = document.getElementById('secret-name');

    const errorMessage = document.getElementById('error-message');

    // 模态窗口元素
    const imageModal = document.getElementById('image-modal');
    const modalImage = document.getElementById('modal-image');
    const modalCaption = document.getElementById('modal-caption');
    const modalCloseBtn = document.querySelector('.modal-close');

    let currentMapName = mapSelect.value;

    // --- 辅助函数 ---

    function gameToScreenPercent(gameX, gameY) {
        const leftPercent = ((gameX - GAME_COORD.X_MIN) / GAME_COORD.X_RANGE) * 100;
        const topPercent = ((gameY - GAME_COORD.Y_MIN) / GAME_COORD.Y_RANGE) * 100;
        return { left: leftPercent, top: topPercent };
    }

    function screenToGameCoords(clickX, clickY, containerWidth, containerHeight) {
        const xFraction = clickX / containerWidth;
        const yFraction = clickY / containerHeight;
        const gameX = GAME_COORD.X_MIN + (xFraction * GAME_COORD.X_RANGE);
        const gameY = GAME_COORD.Y_MIN + (yFraction * GAME_COORD.Y_RANGE);
        return { x: Math.round(gameX), y: Math.round(gameY) };
    }

    function showError(message) {
        errorMessage.textContent = message;
        errorMessage.classList.add('visible');
        setTimeout(() => errorMessage.classList.remove('visible'), 4000);
    }

    function showLoader(loaderElement, isLoading) {
        loaderElement.classList.toggle('visible', isLoading);
    }

    function resetSecretPanel() {
        secretContent.style.display = 'none';
        secretPlaceholder.style.display = 'block';
        secretImage.src = '';
        secretName.textContent = '';
        secretImage.removeEventListener('click', openImageModal);
    }

    // 模态窗口函数
    function openImageModal() {
        modalImage.src = secretImage.src;
        modalCaption.textContent = secretName.textContent;
        imageModal.classList.add('visible');
        document.addEventListener('keydown', handleEscKey);
    }

    function closeImageModal() {
        imageModal.classList.remove('visible');
        document.removeEventListener('keydown', handleEscKey);
    }

    function handleEscKey(event) {
        if (event.key === 'Escape') {
            closeImageModal();
        }
    }

    // --- 核心功能 ---

    function loadMapDetails(mapName) {
        showLoader(mapLoader, true);
        playerMarker.style.display = 'none';
        secretMarkersContainer.innerHTML = '';
        resetSecretPanel();

        fetch('/secret_map/get_map_details', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ map_name: mapName }),
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                mapImage.src = data.image_path;
                currentMapName = mapName;
                mapImage.onload = () => {
                    drawSecretMarkers(data.secret_spots);
                    showLoader(mapLoader, false);
                };
            } else {
                showError(data.error || '加载地图详情失败');
                showLoader(mapLoader, false);
            }
        })
        .catch(error => {
            showError('网络错误，请检查后端服务是否运行');
            showLoader(mapLoader, false);
        });
    }

    function drawSecretMarkers(spots) {
        spots.forEach(spot => {
            const marker = document.createElement('div');
            marker.className = 'map-marker secret-marker';
            const position = gameToScreenPercent(spot.x, spot.y);
            marker.style.left = `${position.left}%`;
            marker.style.top = `${position.top}%`;
            marker.addEventListener('click', (e) => {
                e.stopPropagation();
                targetXInput.value = spot.x;
                targetYInput.value = spot.y;
                findSecret();
            });
            secretMarkersContainer.appendChild(marker);
        });
    }

    mapContainer.addEventListener('click', function(event) {
        const rect = mapContainer.getBoundingClientRect();
        const clickX = event.clientX - rect.left;
        const clickY = event.clientY - rect.top;
        const gameCoords = screenToGameCoords(clickX, clickY, mapContainer.offsetWidth, mapContainer.offsetHeight);
        clickedCoordsDisplay.textContent = `(${gameCoords.x}, ${gameCoords.y})`;
        targetXInput.value = gameCoords.x;
        targetYInput.value = gameCoords.y;
    });

    function markPlayerPosition() {
        const x = parseFloat(playerXInput.value);
        const y = parseFloat(playerYInput.value);
        if (isNaN(x) || isNaN(y) || x < GAME_COORD.X_MIN || x > GAME_COORD.X_MAX || y < GAME_COORD.Y_MIN || y > GAME_COORD.Y_MAX) {
            showError(`请输入有效的游戏坐标 (X: ${GAME_COORD.X_MIN}-${GAME_COORD.X_MAX}, Y: ${GAME_COORD.Y_MIN}-${GAME_COORD.Y_MAX})`);
            return;
        }
        const position = gameToScreenPercent(x, y);
        playerMarker.style.left = `${position.left}%`;
        playerMarker.style.top = `${position.top}%`;
        playerMarker.style.display = 'block';
    }

    function findSecret() {
        const x = parseFloat(targetXInput.value);
        const y = parseFloat(targetYInput.value);
        if (isNaN(x) || isNaN(y)) {
            showError('请输入有效的目标坐标！');
            return;
        }
        showLoader(secretLoader, true);
        resetSecretPanel();
        fetch('/secret_map/find_secret_by_coords', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ map_name: currentMapName, x, y }),
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                if (data.found) {
                    secretImage.src = data.secret_image;
                    secretName.textContent = data.secret_name;
                    secretPlaceholder.style.display = 'none';
                    secretContent.style.display = 'block';
                    secretImage.addEventListener('click', openImageModal);
                } else {
                    showError('此坐标附近没有发现密室。');
                    resetSecretPanel();
                }
            } else {
                showError(data.error || '查询失败');
            }
        })
        .catch(error => showError('网络错误，查询失败'))
        .finally(() => showLoader(secretLoader, false));
    }

    // --- 事件监听器 ---
    mapSelect.addEventListener('change', () => loadMapDetails(mapSelect.value));
    markPlayerBtn.addEventListener('click', markPlayerPosition);
    findSecretBtn.addEventListener('click', findSecret);

    // 模态窗口关闭事件
    modalCloseBtn.addEventListener('click', closeImageModal);
    imageModal.addEventListener('click', function(event) {
        if (event.target === imageModal) {
            closeImageModal();
        }
    });

    // --- 初始加载 ---
    loadMapDetails(currentMapName);
});
