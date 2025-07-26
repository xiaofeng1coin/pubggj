document.addEventListener('DOMContentLoaded', function() {
    // --- DOM Element Selection ---
    const playerXInput = document.getElementById('player-x');
    const playerYInput = document.getElementById('player-y');
    const targetXInput = document.getElementById('target-x');
    const targetYInput = document.getElementById('target-y');
    const distanceResultEl = document.getElementById('distance-result');
    const calculateBtn = document.getElementById('calculate-btn');
    const errorMessageEl = document.getElementById('error-message');
    const mapSelector = document.getElementById('map-selector');

    let errorTimeout;

    // --- 与后端通信的核心函数 ---
    async function sendCalculationRequest() {
        clearError();
        const payload = {
            player_x_px: parseFloat(playerXInput.value),
            player_y_px: parseFloat(playerYInput.value),
            target_x_px: parseFloat(targetXInput.value),
            target_y_px: parseFloat(targetYInput.value),
            map_name: mapSelector.value
        };

        if (Object.values(payload).some(v => isNaN(v) && typeof v === 'number')) {
            showError('所有像素坐标都必须是有效的数字！');
            return;
        }

        calculateBtn.disabled = true;
        calculateBtn.querySelector('.btn-text').textContent = '计算中...';

        try {
            const response = await fetch('/mortar_calculator/calculate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            const result = await response.json();
            if (response.ok && result.success) {
                animateValue(distanceResultEl, result.distance);
            } else {
                showError(result.error || '服务器返回未知错误');
                distanceResultEl.textContent = '---';
            }
        } catch (error) {
            showError('无法连接到服务器。请检查后端服务是否运行。');
        } finally {
            calculateBtn.disabled = false;
            calculateBtn.querySelector('.btn-text').textContent = '计算距离';
        }
    }

    // --- UI辅助函数 ---
    function showError(message) {
        errorMessageEl.textContent = message;
        errorMessageEl.classList.add('visible');
        if (errorTimeout) clearTimeout(errorTimeout);
        errorTimeout = setTimeout(() => {
            errorMessageEl.classList.remove('visible');
        }, 3000);
    }

    function clearError() {
        errorMessageEl.classList.remove('visible');
        if (errorTimeout) clearTimeout(errorTimeout);
    }

    function animateValue(el, endValue, duration = 500) {
        let startValue = parseFloat(el.textContent) || 0;
        if (startValue === endValue) return;
        if (isNaN(endValue)) {
            el.textContent = '---';
            return;
        }
        let startTime = null;
        function animation(currentTime) {
            if (!startTime) startTime = currentTime;
            const progress = Math.min((currentTime - startTime) / duration, 1);
            const currentValue = startValue + (endValue - startValue) * progress;
            el.textContent = currentValue.toFixed(2);
            if (progress < 1) {
                requestAnimationFrame(animation);
            } else {
                el.textContent = endValue.toFixed(2);
            }
        }
        requestAnimationFrame(animation);
    }

    // --- Event Listeners ---
    calculateBtn.addEventListener('click', sendCalculationRequest);

    // <<<< (3) 新增：禁用数字输入框的鼠标滚轮功能 >>>>
    const numberInputs = document.querySelectorAll('input[type="number"]');
    numberInputs.forEach(input => {
        input.addEventListener('wheel', function(event) {
            // 当鼠标焦点在输入框内时，阻止滚轮的默认行为（即改变数值）
            event.preventDefault();
        });
    });

});
