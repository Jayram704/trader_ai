// RL Portfolio Trader - Frontend Application

// Initialize Socket.IO
const socket = io();

// Charts
let rewardChart, sharpeChart, allocationChart;

// Training state
let isTraining = false;

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    initializeCharts();
    setupEventListeners();
    setupSocketListeners();
    loadStatus();
    addLog('System initialized and ready', 'success');
});

// Initialize Charts
function initializeCharts() {
    // Reward Chart
    const rewardCtx = document.getElementById('rewardChart').getContext('2d');
    rewardChart = new Chart(rewardCtx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'Episode Reward',
                data: [],
                borderColor: 'rgba(240, 147, 251, 1)',
                backgroundColor: 'rgba(240, 147, 251, 0.1)',
                tension: 0.4,
                fill: true,
                pointRadius: 4,
                pointHoverRadius: 6
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    labels: { color: 'white' }
                }
            },
            scales: {
                x: {
                    ticks: { color: 'rgba(255,255,255,0.7)' },
                    grid: { color: 'rgba(255,255,255,0.1)' }
                },
                y: {
                    ticks: { color: 'rgba(255,255,255,0.7)' },
                    grid: { color: 'rgba(255,255,255,0.1)' }
                }
            },
            animation: {
                duration: 750,
                easing: 'easeInOutQuart'
            }
        }
    });

    // Sharpe Ratio Chart
    const sharpeCtx = document.getElementById('sharpeChart').getContext('2d');
    sharpeChart = new Chart(sharpeCtx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'Sharpe Ratio',
                data: [],
                borderColor: 'rgba(102, 126, 234, 1)',
                backgroundColor: 'rgba(102, 126, 234, 0.1)',
                tension: 0.4,
                fill: true,
                pointRadius: 4,
                pointHoverRadius: 6
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    labels: { color: 'white' }
                }
            },
            scales: {
                x: {
                    ticks: { color: 'rgba(255,255,255,0.7)' },
                    grid: { color: 'rgba(255,255,255,0.1)' }
                },
                y: {
                    ticks: { color: 'rgba(255,255,255,0.7)' },
                    grid: { color: 'rgba(255,255,255,0.1)' }
                }
            },
            animation: {
                duration: 750,
                easing: 'easeInOutQuart'
            }
        }
    });

    // Allocation Chart (Doughnut)
    const allocationCtx = document.getElementById('allocationChart').getContext('2d');
    allocationChart = new Chart(allocationCtx, {
        type: 'doughnut',
        data: {
            labels: [],
            datasets: [{
                data: [],
                backgroundColor: [
                    'rgba(102, 126, 234, 0.8)',
                    'rgba(118, 75, 162, 0.8)',
                    'rgba(240, 147, 251, 0.8)',
                    'rgba(74, 222, 128, 0.8)',
                    'rgba(251, 191, 36, 0.8)',
                    'rgba(248, 113, 113, 0.8)',
                    'rgba(96, 165, 250, 0.8)',
                    'rgba(167, 139, 250, 0.8)',
                    'rgba(251, 146, 60, 0.8)',
                    'rgba(244, 63, 94, 0.8)'
                ],
                borderWidth: 2,
                borderColor: 'rgba(255,255,255,0.2)'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: { 
                        color: 'white',
                        padding: 15,
                        font: { size: 12 }
                    }
                }
            },
            animation: {
                animateRotate: true,
                animateScale: true,
                duration: 1000
            }
        }
    });
}

// Setup Event Listeners
function setupEventListeners() {
    document.getElementById('startTraining').addEventListener('click', startTraining);
    document.getElementById('stopTraining').addEventListener('click', stopTraining);
    document.getElementById('runBacktest').addEventListener('click', runBacktest);
    document.getElementById('clearLog').addEventListener('click', clearLog);
}

// Setup Socket Listeners
function setupSocketListeners() {
    socket.on('connect', () => {
        updateStatus('Connected', 'success');
        addLog('Connected to server', 'success');
    });

    socket.on('disconnect', () => {
        updateStatus('Disconnected', 'danger');
        addLog('Disconnected from server', 'warning');
    });

    socket.on('training_step', (data) => {
        // Real-time step updates
        if (data.step % 20 === 0) {
            addLog(`Episode ${data.episode}, Step ${data.step}: Reward ${data.reward.toFixed(4)}`, 'info');
        }
    });

    socket.on('episode_complete', (data) => {
        updateTrainingProgress(data);
        updateCharts(data);
        addLog(
            `Episode ${data.episode}/${data.total_episodes} complete - Sharpe: ${data.sharpe_ratio.toFixed(3)}, Drawdown: ${(data.max_drawdown * 100).toFixed(2)}%`,
            'success'
        );
    });

    socket.on('training_complete', (data) => {
        isTraining = false;
        updateStatus('Training Complete', 'success');
        document.getElementById('startTraining').disabled = false;
        document.getElementById('stopTraining').disabled = true;
        
        showToast(
            'Training Complete!',
            `Final Sharpe Ratio: ${data.final_sharpe.toFixed(3)}`,
            'success'
        );
        
        addLog(`Training completed! Final portfolio value: $${data.final_portfolio_value.toFixed(2)}`, 'success');
    });
}

// Start Training
async function startTraining() {
    const config = {
        tickers: Array.from(document.getElementById('assetSelect').selectedOptions).map(opt => opt.value),
        episodes: parseInt(document.getElementById('episodes').value),
        start_date: document.getElementById('startDate').value,
        end_date: document.getElementById('endDate').value,
        initial_balance: parseFloat(document.getElementById('initialBalance').value)
    };

    if (config.tickers.length === 0) {
        showToast('Error', 'Please select at least one asset', 'danger');
        return;
    }

    try {
        const response = await fetch('/api/start_training', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(config)
        });

        if (response.ok) {
            isTraining = true;
            updateStatus('Training', 'primary');
            document.getElementById('startTraining').disabled = true;
            document.getElementById('stopTraining').disabled = false;
            
            // Reset charts
            rewardChart.data.labels = [];
            rewardChart.data.datasets[0].data = [];
            sharpeChart.data.labels = [];
            sharpeChart.data.datasets[0].data = [];
            rewardChart.update();
            sharpeChart.update();
            
            addLog(`Training started with ${config.tickers.length} assets for ${config.episodes} episodes`, 'info');
            showToast('Success', 'Training started successfully', 'success');
        } else {
            const error = await response.json();
            showToast('Error', error.error || 'Failed to start training', 'danger');
        }
    } catch (error) {
        console.error('Error starting training:', error);
        showToast('Error', 'Failed to connect to server', 'danger');
    }
}

// Stop Training
async function stopTraining() {
    try {
        const response = await fetch('/api/stop_training', {
            method: 'POST'
        });

        if (response.ok) {
            isTraining = false;
            updateStatus('Stopped', 'warning');
            document.getElementById('startTraining').disabled = false;
            document.getElementById('stopTraining').disabled = true;
            addLog('Training stopped by user', 'warning');
            showToast('Stopped', 'Training stopped', 'warning');
        }
    } catch (error) {
        console.error('Error stopping training:', error);
    }
}

// Run Backtest
async function runBacktest() {
    const config = {
        tickers: Array.from(document.getElementById('assetSelect').selectedOptions).map(opt => opt.value),
        start_date: document.getElementById('startDate').value,
        end_date: document.getElementById('endDate').value
    };

    if (config.tickers.length === 0) {
        showToast('Error', 'Please select at least one asset', 'danger');
        return;
    }

    addLog('Running backtest...', 'info');
    
    try {
        const response = await fetch('/api/backtest', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(config)
        });

        if (response.ok) {
            const data = await response.json();
            displayBacktestResults(data);
            showToast('Success', 'Backtest completed successfully', 'success');
        } else {
            const error = await response.json();
            showToast('Error', error.error || 'Backtest failed', 'danger');
        }
    } catch (error) {
        console.error('Error running backtest:', error);
        showToast('Error', 'Failed to run backtest', 'danger');
    }
}

// Update Training Progress
function updateTrainingProgress(data) {
    document.getElementById('currentEpisode').textContent = data.episode;
    document.getElementById('sharpeRatio').textContent = data.sharpe_ratio.toFixed(3);
    document.getElementById('maxDrawdown').textContent = `${(data.max_drawdown * 100).toFixed(2)}%`;
    document.getElementById('portfolioValue').textContent = `$${data.portfolio_value.toLocaleString()}`;
    
    const progressFill = document.getElementById('progressFill');
    const progressText = document.getElementById('progressText');
    
    progressFill.style.width = `${data.progress}%`;
    progressText.textContent = `Episode ${data.episode}/${data.total_episodes} (${data.progress.toFixed(1)}%)`;
}

// Update Charts
function updateCharts(data) {
    // Reward Chart
    rewardChart.data.labels.push(`Ep ${data.episode}`);
    rewardChart.data.datasets[0].data.push(data.reward);
    
    // Keep only last 50 points
    if (rewardChart.data.labels.length > 50) {
        rewardChart.data.labels.shift();
        rewardChart.data.datasets[0].data.shift();
    }
    
    rewardChart.update('none'); // Smooth update

    // Sharpe Chart
    sharpeChart.data.labels.push(`Ep ${data.episode}`);
    sharpeChart.data.datasets[0].data.push(data.sharpe_ratio);
    
    if (sharpeChart.data.labels.length > 50) {
        sharpeChart.data.labels.shift();
        sharpeChart.data.datasets[0].data.shift();
    }
    
    sharpeChart.update('none');
}

// Display Backtest Results
function displayBacktestResults(data) {
    addLog(`Backtest Results - Sharpe: ${data.metrics.sharpe_ratio.toFixed(3)}, Return: ${(data.metrics.annualized_return * 100).toFixed(2)}%`, 'success');
    
    // Update allocation chart with final weights
    if (data.weights_history && data.weights_history.length > 0) {
        const finalWeights = data.weights_history[data.weights_history.length - 1];
        const tickers = Array.from(document.getElementById('assetSelect').selectedOptions).map(opt => opt.value);
        
        updateAllocationChart(tickers, finalWeights);
    }
}

// Update Allocation Chart
function updateAllocationChart(tickers, weights) {
    allocationChart.data.labels = tickers;
    allocationChart.data.datasets[0].data = weights;
    allocationChart.update();
    
    // Update allocation table
    const tableHTML = tickers.map((ticker, i) => `
        <div class="allocation-row">
            <span class="allocation-ticker">${ticker}</span>
            <span class="allocation-weight">${(weights[i] * 100).toFixed(2)}%</span>
        </div>
    `).join('');
    
    document.getElementById('allocationTable').innerHTML = tableHTML;
}

// Update Status Badge
function updateStatus(text, type) {
    const badge = document.getElementById('statusBadge');
    const dot = badge.querySelector('.status-dot');
    const span = badge.querySelector('span:last-child');
    
    span.textContent = text;
    
    const colors = {
        success: '#4ade80',
        danger: '#f87171',
        warning: '#fbbf24',
        primary: '#667eea'
    };
    
    dot.style.background = colors[type] || colors.primary;
}

// Add Log Entry
function addLog(message, type = 'info') {
    const log = document.getElementById('activityLog');
    const entry = document.createElement('div');
    entry.className = 'log-entry';
    
    const timestamp = new Date().toLocaleTimeString();
    
    entry.innerHTML = `
        <div class="log-time">${timestamp}</div>
        <div class="log-message">${message}</div>
    `;
    
    log.insertBefore(entry, log.firstChild);
    
    // Keep only last 50 entries
    while (log.children.length > 50) {
        log.removeChild(log.lastChild);
    }
}

// Clear Log
function clearLog() {
    document.getElementById('activityLog').innerHTML = '';
    addLog('Log cleared', 'info');
}

// Show Toast Notification
function showToast(title, message, type = 'success') {
    const toast = document.getElementById('toast');
    const icon = toast.querySelector('.toast-icon i');
    const titleEl = toast.querySelector('.toast-title');
    const messageEl = toast.querySelector('.toast-message');
    
    const icons = {
        success: 'fa-check-circle',
        danger: 'fa-times-circle',
        warning: 'fa-exclamation-circle',
        info: 'fa-info-circle'
    };
    
    icon.className = `fas ${icons[type] || icons.info}`;
    titleEl.textContent = title;
    messageEl.textContent = message;
    
    toast.classList.add('show');
    
    setTimeout(() => {
        toast.classList.remove('show');
    }, 3000);
}

// Load Initial Status
async function loadStatus() {
    try {
        const response = await fetch('/api/status');
        if (response.ok) {
            const data = await response.json();
            addLog(`Server ready - Device: ${data.device}`, 'info');
        }
    } catch (error) {
        console.error('Error loading status:', error);
    }
}

// Format number
function formatNumber(num, decimals = 2) {
    return num.toFixed(decimals).replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

// Animate number counting
function animateValue(element, start, end, duration) {
    const range = end - start;
    const increment = range / (duration / 16);
    let current = start;
    
    const timer = setInterval(() => {
        current += increment;
        if ((increment > 0 && current >= end) || (increment < 0 && current <= end)) {
            current = end;
            clearInterval(timer);
        }
        element.textContent = formatNumber(current);
    }, 16);
}
