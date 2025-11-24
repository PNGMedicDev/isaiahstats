// IsaiahStats - Frontend JavaScript
let socket;
let currentTab = 'leaderboard';
let currentPlayer = null;
let currentPage = 1;
const BETS_PER_PAGE = 20;

// Initialize Socket.IO connection
function initSocket() {
    socket = io();

    socket.on('connect', () => {
        console.log('Connected to server');
        document.getElementById('connection-status').innerHTML = '<i class="fas fa-check-circle text-neon-green"></i>';
    });

    socket.on('disconnect', () => {
        console.log('Disconnected from server');
        document.getElementById('connection-status').innerHTML = '<i class="fas fa-times-circle text-red-500"></i>';
    });

    socket.on('stats_update', (data) => {
        updateGlobalStats(data);
    });

    socket.on('new_bet', (data) => {
        showLiveBetNotification(data);
        if (currentTab === 'recent') {
            loadRecentBets();
        }
        if (currentTab === 'leaderboard') {
            loadLeaderboards();
        }
    });

    socket.on('vc_update', (data) => {
        if (currentTab === 'discord') {
            loadDiscordVC();
        }
    });
}

// Update global statistics
function updateGlobalStats(data) {
    document.getElementById('total-bets').textContent = data.total_bets_formatted || '0';
    document.getElementById('total-wagered').textContent = data.total_wagered_formatted || '$0';
    document.getElementById('house-profit').textContent = data.house_profit_formatted || '$0';
    document.getElementById('house-edge').textContent = data.house_edge || '0%';
}

// Show live bet notification
function showLiveBetNotification(bet) {
    const notification = document.getElementById('live-bet-notification');
    const avatar = document.getElementById('live-bet-avatar');
    const text = document.getElementById('live-bet-text');
    const amount = document.getElementById('live-bet-amount');

    avatar.src = `https://mc-heads.net/avatar/${bet.username}/48`;

    if (bet.result === 'win') {
        text.textContent = `${bet.username} won!`;
        text.className = 'text-sm font-semibold text-neon-green';
    } else {
        text.textContent = `${bet.username} lost`;
        text.className = 'text-sm font-semibold text-red-400';
    }

    amount.textContent = `${bet.amount_formatted} → ${bet.payout_formatted}`;

    notification.style.display = 'block';

    setTimeout(() => {
        notification.style.display = 'none';
    }, 5000);
}

// Switch tabs
function switchTab(tab) {
    currentTab = tab;

    // Update tab buttons
    document.querySelectorAll('[id^="tab-"]').forEach(btn => {
        btn.classList.remove('tab-active', 'text-black', 'bg-neon-green');
        btn.classList.add('glass-card', 'text-gray-400');
    });

    const activeBtn = document.getElementById(`tab-${tab}`);
    if (activeBtn) {
        activeBtn.classList.add('tab-active', 'text-black', 'bg-neon-green');
        activeBtn.classList.remove('glass-card', 'text-gray-400');
    }

    // Update mobile tabs
    document.querySelectorAll('.mobile-tab').forEach(btn => {
        btn.classList.remove('text-neon-green', 'bg-neon-green/10');
        btn.classList.add('text-gray-400');
    });

    const activeMobileTab = document.querySelector(`.mobile-tab[data-tab="${tab}"]`);
    if (activeMobileTab) {
        activeMobileTab.classList.add('text-neon-green', 'bg-neon-green/10');
        activeMobileTab.classList.remove('text-gray-400');
    }

    // Hide all content
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.add('hidden');
    });

    // Show selected content
    const content = document.getElementById(`content-${tab}`);
    if (content) {
        content.classList.remove('hidden');
    }

    // Load data for the tab
    switch(tab) {
        case 'leaderboard':
            loadLeaderboards();
            break;
        case 'recent':
            loadRecentBets();
            break;
        case 'search':
            // Search is handled by input events
            break;
        case 'discord':
            loadDiscordVC();
            break;
    }
}

// Load leaderboards
async function loadLeaderboards() {
    try {
        const [wagered, won, lost] = await Promise.all([
            fetch('/api/leaderboard/wagered').then(r => r.json()),
            fetch('/api/leaderboard/won').then(r => r.json()),
            fetch('/api/leaderboard/lost').then(r => r.json())
        ]);

        renderLeaderboard('most-wagered', wagered, 'total_wagered_formatted');
        renderLeaderboard('most-won', won, 'net_profit_formatted', true);
        renderLeaderboard('most-lost', lost, 'net_profit_formatted', false);
    } catch (error) {
        console.error('Error loading leaderboards:', error);
    }
}

// Render leaderboard
function renderLeaderboard(containerId, players, valueKey, isProfit = null) {
    const container = document.getElementById(containerId);
    if (!container) return;

    const emojis = ['👑', '🥈', '🥉'];

    container.innerHTML = players.map((player, index) => {
        const rankEmoji = index < 3 ? emojis[index] : `#${index + 1}`;
        const isHighRoller = player.total_wagered >= 10000000000; // 10B+

        let valueColor = 'text-white';
        let valueText = player[valueKey];

        if (isProfit !== null) {
            if (player.is_profitable) {
                valueColor = 'text-neon-green';
                valueText = '+' + player.net_profit_formatted;
            } else {
                valueColor = 'text-red-400';
                valueText = '-' + player.net_profit_formatted;
            }
        }

        return `
            <div class="group relative overflow-hidden rounded-xl cursor-pointer transition-all duration-200" onclick="searchPlayer('${player.username}')">
                <div class="relative flex items-center justify-between p-3 sm:p-4 bg-dark-card border border-dark-border group-hover:border-neon-green/50 rounded-xl transition-all duration-200">
                    <div class="flex items-center space-x-2 sm:space-x-3 flex-1 min-w-0">
                        <div class="text-xl sm:text-2xl flex-shrink-0">${rankEmoji}</div>
                        <img src="https://mc-heads.net/avatar/${player.username}/48" alt="${player.username}" class="w-8 h-8 sm:w-10 sm:h-10 rounded-lg border border-gray-800 flex-shrink-0" onerror="this.src='https://mc-heads.net/avatar/MHF_Steve/48'">
                        <div class="flex-1 min-w-0">
                            <div class="flex items-center space-x-2">
                                <span class="text-white font-semibold text-sm sm:text-base truncate">${player.username}</span>
                                ${isHighRoller ? '<span class="high-roller-badge px-2 py-0.5 rounded text-xs font-bold text-black flex-shrink-0"><i class="fas fa-crown text-xs"></i></span>' : ''}
                            </div>
                            <span class="text-gray-600 text-xs">Rank #${index + 1}</span>
                        </div>
                    </div>
                    <div class="text-right flex-shrink-0 ml-2">
                        <span class="${valueColor} font-bold text-sm sm:text-lg block">
                            ${valueText}
                        </span>
                    </div>
                </div>
            </div>
        `;
    }).join('');
}

// Load recent bets
async function loadRecentBets() {
    try {
        const bets = await fetch('/api/recent').then(r => r.json());
        const container = document.getElementById('recent-bets');
        if (!container) return;

        container.innerHTML = bets.map(bet => {
            const resultClass = bet.result === 'win' ? 'bg-neon-green/20 text-neon-green' : 'bg-red-500/20 text-red-500';
            const resultText = bet.result === 'win' ? 'Win' : 'Loss';

            return `
                <tr class="border-b border-dark-border hover:bg-gray-900/50 transition-colors duration-200">
                    <td class="py-3 px-2 sm:px-4 text-gray-400 text-xs sm:text-sm">${bet.timestamp}</td>
                    <td class="py-3 px-2 sm:px-4">
                        <div class="flex items-center space-x-2">
                            <img src="https://mc-heads.net/avatar/${bet.username}/32" alt="${bet.username}" class="w-6 h-6 sm:w-8 sm:h-8 rounded-lg border border-gray-800" onerror="this.src='https://mc-heads.net/avatar/MHF_Steve/32'">
                            <span class="text-white font-semibold text-xs sm:text-sm">${bet.username}</span>
                        </div>
                    </td>
                    <td class="py-3 px-2 sm:px-4 text-white font-semibold text-xs sm:text-sm">${bet.amount_formatted}</td>
                    <td class="py-3 px-2 sm:px-4">
                        <span class="px-2 py-1 rounded text-xs font-bold ${resultClass}">
                            ${resultText}
                        </span>
                    </td>
                    <td class="py-3 px-2 sm:px-4 text-gray-400 text-xs sm:text-sm hidden sm:table-cell">${bet.multiplier}</td>
                    <td class="py-3 px-2 sm:px-4 text-white font-semibold text-xs sm:text-sm">${bet.payout_formatted}</td>
                </tr>
            `;
        }).join('');
    } catch (error) {
        console.error('Error loading recent bets:', error);
    }
}

// Search functionality
let searchTimeout;
const searchInput = document.getElementById('player-search');

if (searchInput) {
    searchInput.addEventListener('input', (e) => {
        clearTimeout(searchTimeout);
        const query = e.target.value.trim();

        if (query.length < 2) {
            document.getElementById('search-suggestions').innerHTML = '';
            return;
        }

        searchTimeout = setTimeout(async () => {
            try {
                const results = await fetch(`/api/search?q=${encodeURIComponent(query)}`).then(r => r.json());

                document.getElementById('search-suggestions').innerHTML = results.map(username => `
                    <div class="glass-card p-3 rounded-lg cursor-pointer hover:border-neon-green/50 transition-all duration-200 mb-2" onclick="searchPlayer('${username}')">
                        <div class="flex items-center space-x-3">
                            <img src="https://mc-heads.net/avatar/${username}/32" alt="${username}" class="w-8 h-8 rounded-lg border border-gray-800">
                            <span class="text-white font-semibold">${username}</span>
                        </div>
                    </div>
                `).join('');
            } catch (error) {
                console.error('Error searching players:', error);
            }
        }, 300);
    });
}

// Search for a specific player
async function searchPlayer(username) {
    try {
        switchTab('search');
        document.getElementById('player-search').value = username;
        document.getElementById('search-suggestions').innerHTML = '';

        const stats = await fetch(`/api/player/${encodeURIComponent(username)}`).then(r => r.json());

        if (stats.error) {
            alert('Player not found');
            return;
        }

        currentPlayer = stats;
        currentPage = 1;
        renderPlayerStats(stats);
    } catch (error) {
        console.error('Error loading player stats:', error);
        alert('Error loading player stats');
    }
}

// Render player statistics
function renderPlayerStats(stats) {
    const container = document.getElementById('player-stats');
    if (!container) return;

    const profitClass = stats.is_profitable ? 'text-neon-green' : 'text-red-400';
    const profitSign = stats.is_profitable ? '+' : '-';

    container.classList.remove('hidden');

    container.innerHTML = `
        <div class="gradient-border">
            <div class="gradient-border-inner p-4 sm:p-6">
                <div class="flex flex-col sm:flex-row items-center sm:items-start space-y-4 sm:space-y-0 sm:space-x-6">
                    <div class="relative">
                        <img src="https://mc-heads.net/avatar/${stats.username}/96" alt="${stats.username}" class="w-20 h-20 sm:w-24 sm:h-24 rounded-2xl border-4 border-neon-purple shadow-2xl">
                    </div>
                    <div class="flex-1 text-center sm:text-left">
                        <h2 class="text-2xl sm:text-3xl font-black text-white orbitron mb-2">${stats.username}</h2>
                        <p class="text-sm sm:text-base text-gray-400 mb-3 sm:mb-4">Player Statistics</p>
                        <div class="grid grid-cols-2 sm:grid-cols-4 gap-3 sm:gap-4">
                            <div class="bg-dark-card rounded-lg p-3">
                                <p class="text-xs text-gray-400 mb-1">Total Bets</p>
                                <p class="text-lg sm:text-xl font-bold text-white orbitron">${stats.total_bets}</p>
                            </div>
                            <div class="bg-dark-card rounded-lg p-3">
                                <p class="text-xs text-gray-400 mb-1">Win Rate</p>
                                <p class="text-lg sm:text-xl font-bold text-neon-green orbitron">${stats.win_rate}</p>
                            </div>
                            <div class="bg-dark-card rounded-lg p-3">
                                <p class="text-xs text-gray-400 mb-1">Wagered</p>
                                <p class="text-lg sm:text-xl font-bold text-white orbitron">${stats.total_wagered}</p>
                            </div>
                            <div class="bg-dark-card rounded-lg p-3">
                                <p class="text-xs text-gray-400 mb-1">Net P/L</p>
                                <p class="text-lg sm:text-xl font-bold ${profitClass} orbitron">${profitSign}${stats.net_profit_formatted}</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <div class="glass-card rounded-xl sm:rounded-2xl p-4 sm:p-6">
            <div class="flex items-center justify-between mb-4">
                <h3 class="text-base sm:text-lg font-bold text-white orbitron flex items-center">
                    <i class="fas fa-history text-neon-green mr-2"></i>
                    Recent Bets
                </h3>
            </div>
            <div class="overflow-x-auto scrollbar-hide">
                <table class="w-full text-sm">
                    <thead>
                        <tr class="border-b border-dark-border">
                            <th class="text-left py-3 px-2 sm:px-4 text-gray-400 font-semibold">Time</th>
                            <th class="text-left py-3 px-2 sm:px-4 text-gray-400 font-semibold">Bet</th>
                            <th class="text-left py-3 px-2 sm:px-4 text-gray-400 font-semibold">Result</th>
                            <th class="text-left py-3 px-2 sm:px-4 text-gray-400 font-semibold hidden sm:table-cell">Multiplier</th>
                            <th class="text-left py-3 px-2 sm:px-4 text-gray-400 font-semibold">Payout</th>
                            <th class="text-left py-3 px-2 sm:px-4 text-gray-400 font-semibold">P/L</th>
                        </tr>
                    </thead>
                    <tbody id="player-bet-history">
                        ${renderPlayerHistory(stats.history)}
                    </tbody>
                </table>
            </div>
        </div>
    `;
}

// Render player bet history
function renderPlayerHistory(history) {
    return history.map(bet => {
        const resultClass = bet.result === 'win' ? 'bg-neon-green/20 text-neon-green' : 'bg-red-500/20 text-red-500';
        const resultText = bet.result === 'win' ? 'Win' : 'Loss';
        const profitClass = bet.profit >= 0 ? 'text-neon-green' : 'text-red-400';
        const profitSign = bet.profit >= 0 ? '+' : '-';

        return `
            <tr class="border-b border-dark-border hover:bg-gray-900/50 transition-colors duration-200">
                <td class="py-3 px-2 sm:px-4 text-gray-400 text-xs sm:text-sm">${bet.timestamp}</td>
                <td class="py-3 px-2 sm:px-4 text-white font-semibold text-xs sm:text-sm">${bet.amount_formatted}</td>
                <td class="py-3 px-2 sm:px-4">
                    <span class="px-2 py-1 rounded text-xs font-bold ${resultClass}">
                        ${resultText}
                    </span>
                </td>
                <td class="py-3 px-2 sm:px-4 text-gray-400 text-xs sm:text-sm hidden sm:table-cell">${bet.multiplier}x</td>
                <td class="py-3 px-2 sm:px-4 text-white font-semibold text-xs sm:text-sm">${bet.payout_formatted}</td>
                <td class="py-3 px-2 sm:px-4 ${profitClass} font-semibold text-xs sm:text-sm">${profitSign}${bet.profit_formatted}</td>
            </tr>
        `;
    }).join('');
}

// Load Discord VC status
async function loadDiscordVC() {
    try {
        const users = await fetch('/api/discord/vc').then(r => r.json());
        const container = document.getElementById('discord-vc-list');
        const emptyState = document.getElementById('discord-vc-empty');

        if (!container) return;

        if (users.length === 0) {
            container.innerHTML = '';
            container.classList.add('hidden');
            emptyState.classList.remove('hidden');
            return;
        }

        container.classList.remove('hidden');
        emptyState.classList.add('hidden');

        container.innerHTML = users.map(user => {
            const mcUsername = user.minecraft_username && user.minecraft_username !== 'Unknown'
                ? user.minecraft_username
                : null;

            return `
                <div class="bg-dark-card border border-dark-border rounded-xl p-4 hover:border-neon-purple/30 transition-all duration-200">
                    <div class="flex items-center space-x-4">
                        ${mcUsername ?
                            `<img src="https://mc-heads.net/avatar/${mcUsername}/48"
                                  alt="${mcUsername}"
                                  class="w-12 h-12 rounded-lg border-2 border-neon-purple shadow-lg"
                                  onerror="this.src='https://mc-heads.net/avatar/MHF_Steve/48'">` :
                            `<div class="w-12 h-12 rounded-lg border-2 border-gray-700 bg-gray-800 flex items-center justify-center">
                                <i class="fab fa-discord text-gray-600 text-2xl"></i>
                             </div>`
                        }
                        <div class="flex-1">
                            <div class="flex items-center space-x-2 mb-1">
                                ${mcUsername ?
                                    `<span class="text-white font-semibold">${mcUsername}</span>` :
                                    `<span class="text-white font-semibold">${user.discord_username}</span>`
                                }
                                <span class="text-xs text-gray-500">•</span>
                                <span class="text-xs text-gray-400">${user.duration}</span>
                            </div>
                            <div class="flex items-center space-x-2 text-xs text-gray-400">
                                <i class="fas fa-headphones text-neon-purple"></i>
                                <span>${user.channel_name}</span>
                                ${user.guild_name ? `<span class="text-gray-600">in ${user.guild_name}</span>` : ''}
                            </div>
                            ${!mcUsername ?
                                `<div class="text-xs text-gray-500 mt-1">
                                    Discord: ${user.discord_username}
                                 </div>` :
                                `<div class="text-xs text-gray-500 mt-1">
                                    Discord: ${user.discord_username}
                                 </div>`
                            }
                        </div>
                        <div class="flex items-center">
                            <div class="w-2 h-2 bg-neon-green rounded-full live-indicator"></div>
                        </div>
                    </div>
                </div>
            `;
        }).join('');
    } catch (error) {
        console.error('Error loading Discord VC data:', error);
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    initSocket();

    // Load initial data
    fetch('/api/stats')
        .then(r => r.json())
        .then(data => updateGlobalStats(data))
        .catch(error => console.error('Error loading stats:', error));

    loadLeaderboards();
});
