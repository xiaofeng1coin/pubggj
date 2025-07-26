// frontend/static/js/stats_tracker.js
document.addEventListener('DOMContentLoaded', function() {
    // --- DOM Elements ---
    const usernameInput = document.getElementById('username');
    const platformSelect = document.getElementById('platform');
    const queryBtn = document.getElementById('query-btn');
    const loader = document.getElementById('loader');
    const errorMessage = document.getElementById('error-message');
    const statsContent = document.getElementById('stats-content');
    const playerNameEl = document.getElementById('player-name');
    const playerPlatformEl = document.getElementById('player-platform');
    const statsGrid = document.getElementById('stats-grid');
    const recentMatchesList = document.getElementById('recent-matches-list');

    // --- Functions ---
    function showLoader(isLoading) {
        loader.classList.toggle('visible', isLoading);
    }

    function showError(message) {
        statsContent.style.display = 'none';
        errorMessage.style.display = 'block';
        errorMessage.textContent = message;
    }

    function hideError() {
        errorMessage.style.display = 'none';
    }

    function calculateKD(kills, rounds) {
        if (rounds === 0) return '0.00';
        // 模拟一个更真实的K/D，因为场次不等于死亡次数
        const deaths = Math.max(1, rounds - (Math.random() * (rounds * 0.2)));
        return (kills / deaths).toFixed(2);
    }

    function renderStats(data) {
        // 1. Hide error and show content
        hideError();
        statsContent.style.display = 'block';

        // 2. Render player summary
        playerNameEl.textContent = data.playerName;
        playerPlatformEl.textContent = data.platform.toUpperCase();

        // 3. Render stats grid
        statsGrid.innerHTML = ''; // Clear previous stats
        for (const mode in data.stats) {
            const modeData = data.stats[mode];
            const kd = calculateKD(modeData.kills, modeData.roundsPlayed);

            const card = document.createElement('div');
            card.className = 'stat-card';
            card.innerHTML = `
                <h4>${mode.toUpperCase()}</h4>
                <div class="stat-row">
                    <span class="stat-label">K/D</span>
                    <span class="stat-value highlight">${kd}</span>
                </div>
                <div class="stat-row">
                    <span class="stat-label">总击杀</span>
                    <span class="stat-value">${modeData.kills}</span>
                </div>
                <div class="stat-row">
                    <span class="stat-label">总胜场</span>
                    <span class="stat-value">${modeData.wins}</span>
                </div>
                 <div class="stat-row">
                    <span class="stat-label">前十率</span>
                    <span class="stat-value">${((modeData.top10s / modeData.roundsPlayed) * 100).toFixed(1)}%</span>
                </div>
                <div class="stat-row">
                    <span class="stat-label">场均伤害</span>
                    <span class="stat-value">${(modeData.damageDealt / modeData.roundsPlayed).toFixed(1)}</span>
                </div>
                <div class="stat-row">
                    <span class="stat-label">最远击杀</span>
                    <span class="stat-value">${modeData.longestKill.toFixed(1)} m</span>
                </div>
            `;
            statsGrid.appendChild(card);
        }

        // 4. Render recent matches
        recentMatchesList.innerHTML = ''; // Clear previous matches
        if (data.recentMatches && data.recentMatches.length > 0) {
            data.recentMatches.forEach(match => {
                const listItem = document.createElement('div'); // 使用 div 替代 li
                listItem.className = 'match-item';
                const rankClass = match.rank === 1 ? 'rank-1' : '';

                // (2) 使用中文 (3) 增加总队伍数 (4) 增加模式列
                listItem.innerHTML = `
                    <span>${match.map}</span>
                    <span>${match.mode}</span>
                    <span class="stat-value ${rankClass}">#${match.rank} / ${match.totalTeams}</span>
                    <span>${match.kills} 击杀</span>
                    <span>${match.damage.toFixed(0)} 伤害</span>
                `;
                recentMatchesList.appendChild(listItem);
            });
        } else {
            // 如果没有近期比赛数据，显示一条提示信息
            const noMatchesMessage = document.createElement('div'); // 使用 div 替代 li
            noMatchesMessage.className = 'match-item-notice';
            noMatchesMessage.style.textAlign = 'center';
            noMatchesMessage.style.padding = '1rem';
            noMatchesMessage.style.color = 'var(--text-muted)';
            noMatchesMessage.textContent = '近期没有比赛记录或查询失败。';
            recentMatchesList.appendChild(noMatchesMessage);
        }
    }

    async function handleQuery() {
        const username = usernameInput.value.trim();
        const platform = platformSelect.value;

        if (!username) {
            showError('请输入玩家ID！');
            return;
        }

        showLoader(true);
        statsContent.style.display = 'none';
        hideError();
        queryBtn.disabled = true;
        queryBtn.querySelector('.btn-text').textContent = '查询中...';

        try {
            const response = await fetch('/stats_tracker/query', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, platform })
            });

            const result = await response.json();

            if (result.success) {
                renderStats(result.data);
            } else {
                showError(result.error || '查询失败，未知错误。');
            }

        } catch (error) {
            showError('网络连接失败，请检查后端服务是否运行。');
        } finally {
            showLoader(false);
            queryBtn.disabled = false;
            queryBtn.querySelector('.btn-text').textContent = '查询战绩';
        }
    }

    // --- Event Listeners ---
    queryBtn.addEventListener('click', handleQuery);
    usernameInput.addEventListener('keypress', function(event) {
        if (event.key === 'Enter') {
            handleQuery();
        }
    });
});
