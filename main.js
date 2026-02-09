// ========================================
// RL PORTFOLIO TRADER - MAIN JS
// ========================================

// Global state
const state = {
    training: {
        isRunning: false,
        currentEpisode: 0,
        totalEpisodes: 0,
        metrics: {
            reward: 0,
            avgReward: 0,
            actorLoss: 0,
            criticLoss: 0
        }
    },
    portfolio: {
        weights: [],
        assets: ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'JPM', 'BAC', 'JNJ', 'PG', 'GBTC', 'ETHE'],
        performance: []
    },
    performance: {
        sharpeRatio: 0,
        maxDrawdown: 0,
        annualReturn: 0
    }
};

// ========================================
// INITIALIZATION
// ========================================

document.addEventListener('DOMContentLoaded', () => {
    initializeUI();
    initializeEventListeners();
    loadMockData(); // Load demo data
    startAnimations();
});

function initializeUI() {
    // Smooth scroll for navigation
    document.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const targetId = link.getAttribute('href').substring(1);
            const targetSection = document.getElementById(targetId);
            if (targetSection) {
                targetSection.scrollIntoView({ behavior: 'smooth' });
                
                // Update active link
                document.querySelectorAll('.nav-link').forEach(l => l.classList.remove('active'));
                link.classList.add('active');
            }
        });
    });

    // Initialize portfolio weights visualization
    updatePortfolioWeights(state.portfolio.assets.map(() => Math.random() * 0.2));
}

function initializeEventListeners() {
    // Training form
    const trainForm = document.getElementById('training-form');
    trainForm.addEventListener('submit', handleTrainingSubmit);

    // Risk penalty slider
    const riskSlider = document.getElementById('risk-penalty');
    const sliderValue = document.querySelector('.slider-value');
    riskSlider.addEventListener('input', (e) => {
        sliderValue.textContent = e.target.value;
    });

    // Chart controls
    document.querySelectorAll('.control-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const chartType = btn.dataset.chart;
            document.querySelectorAll('.control-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            updateChartView(chartType);
        });
    });
}

// ========================================
// TRAINING CONTROL
// ========================================

async function handleTrainingSubmit(e) {
    e.preventDefault();

    if (state.training.isRunning) {
        stopTraining();
        return;
    }

    // Get form data
    const formData = {
        episodes: parseInt(document.getElementById('episodes').value),
        learningRate: parseFloat(document.getElementById('learning-rate').value),
        riskPenalty: parseFloat(document.getElementById('risk-penalty').value),
        useHER: document.getElementById('use-her').checked,
        twinCritics: document.getElementById('twin-critics').checked
    };

    state.training.totalEpisodes = formData.episodes;
    state.training.isRunning = true;

    // Update UI
    updateTrainingStatus('Training', true);
    document.getElementById('train-btn').querySelector('.btn-text').textContent = 'STOP TRAINING';
    document.getElementById('total-episodes-display').textContent = formData.episodes;

    // Log start
    addLog(`Starting training with ${formData.episodes} episodes...`, 'success');
    addLog(`Configuration: LR=${formData.learningRate}, Risk Penalty=${formData.riskPenalty}`);
    addLog(`Using HER: ${formData.useHER}, Twin Critics: ${formData.twinCritics}`);

    try {
        // Send to backend
        const response = await fetch('/api/train', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(formData)
        });

        if (response.ok) {
            // Start receiving training updates via SSE
            startTrainingMonitor();
        } else {
            throw new Error('Training start failed');
        }
    } catch (error) {
        addLog(`Error: ${error.message}`, 'error');
        stopTraining();
    }
}

function startTrainingMonitor() {
    const eventSource = new EventSource('/api/train/stream');

    eventSource.onmessage = (event) => {
        const data = JSON.parse(event.data);
        updateTrainingMetrics(data);
    };

    eventSource.onerror = () => {
        eventSource.close();
        if (state.training.isRunning) {
            simulateTraining(); // Fallback to simulation
        }
    };

    // Fallback: simulate training if backend not available
    setTimeout(() => {
        if (eventSource.readyState !== EventSource.OPEN) {
            eventSource.close();
            simulateTraining();
        }
    }, 2000);
}

function simulateTraining() {
    addLog('Running in simulation mode...', 'warning');
    
    const interval = setInterval(() => {
        if (!state.training.isRunning) {
            clearInterval(interval);
            return;
        }

        state.training.currentEpisode++;
        
        // Simulate metrics
        const progress = state.training.currentEpisode / state.training.totalEpisodes;
        state.training.metrics = {
            reward: (Math.random() * 0.1 - 0.05).toFixed(4),
            avgReward: (progress * 0.05 + Math.random() * 0.01).toFixed(4),
            actorLoss: (Math.random() * 0.5).toFixed(4),
            criticLoss: (Math.random() * 1.0).toFixed(4)
        };

        updateTrainingMetrics({
            episode: state.training.currentEpisode,
            ...state.training.metrics
        });

        // Update performance metrics
        if (state.training.currentEpisode % 10 === 0) {
            state.performance.sharpeRatio = Math.min(2.5, 0.8 + progress * 1.2 + Math.random() * 0.3);
            state.performance.maxDrawdown = -(0.05 + Math.random() * 0.1);
            state.performance.annualReturn = 0.1 + progress * 0.2 + Math.random() * 0.05;
            updatePerformanceMetrics();
        }

        if (state.training.currentEpisode >= state.training.totalEpisodes) {
            completeTraining();
            clearInterval(interval);
        }
    }, 100); // Fast simulation
}

function updateTrainingMetrics(data) {
    // Update current episode
    state.training.currentEpisode = data.episode || state.training.currentEpisode;
    document.getElementById('current-episode').textContent = state.training.currentEpisode;

    // Update progress bar
    const progress = (state.training.currentEpisode / state.training.totalEpisodes) * 100;
    document.getElementById('training-progress').style.width = `${progress}%`;

    // Update metrics
    if (data.reward !== undefined) {
        document.getElementById('episode-reward').textContent = data.reward;
    }
    if (data.avgReward !== undefined) {
        document.getElementById('avg-reward').textContent = data.avgReward;
    }
    if (data.actorLoss !== undefined) {
        document.getElementById('actor-loss').textContent = data.actorLoss;
    }
    if (data.criticLoss !== undefined) {
        document.getElementById('critic-loss').textContent = data.criticLoss;
    }

    // Log episode completion
    if (state.training.currentEpisode % 10 === 0) {
        addLog(`Episode ${state.training.currentEpisode}/${state.training.totalEpisodes} - Reward: ${data.reward || data.avgReward}`);
    }

    // Update charts
    updateTrainingCharts(data);
}

function completeTraining() {
    state.training.isRunning = false;
    updateTrainingStatus('Complete', false);
    document.getElementById('train-btn').querySelector('.btn-text').textContent = 'START TRAINING';
    addLog('Training completed successfully!', 'success');
    addLog(`Final Sharpe Ratio: ${state.performance.sharpeRatio.toFixed(4)}`, 'success');
    addLog(`Final Max Drawdown: ${(state.performance.maxDrawdown * 100).toFixed(2)}%`, 'success');
}

function stopTraining() {
    state.training.isRunning = false;
    updateTrainingStatus('Stopped', false);
    document.getElementById('train-btn').querySelector('.btn-text').textContent = 'START TRAINING';
    addLog('Training stopped by user.', 'warning');
}

function updateTrainingStatus(text, active) {
    const statusText = document.querySelector('.status-text');
    const statusDot = document.querySelector('.status-dot');
    
    statusText.textContent = text;
    if (active) {
        statusDot.classList.add('active');
    } else {
        statusDot.classList.remove('active');
    }
}

// ========================================
// LOGGING
// ========================================

function addLog(message, type = 'info') {
    const logContent = document.getElementById('log-content');
    const logLine = document.createElement('div');
    logLine.className = `log-line ${type}`;
    
    const timestamp = new Date().toLocaleTimeString();
    logLine.textContent = `[${timestamp}] ${message}`;
    
    logContent.appendChild(logLine);
    logContent.scrollTop = logContent.scrollHeight;

    // Keep only last 50 lines
    while (logContent.children.length > 50) {
        logContent.removeChild(logContent.firstChild);
    }
}

function clearLog() {
    const logContent = document.getElementById('log-content');
    logContent.innerHTML = '<div class="log-line">$ Log cleared</div>';
}

// ========================================
// PERFORMANCE METRICS
// ========================================

function updatePerformanceMetrics() {
    // Update hero stats
    document.getElementById('sharpe-ratio').textContent = state.performance.sharpeRatio.toFixed(2);
    document.getElementById('max-drawdown').textContent = `${(state.performance.maxDrawdown * 100).toFixed(1)}%`;
    document.getElementById('annual-return').textContent = `${(state.performance.annualReturn * 100).toFixed(1)}%`;
    document.getElementById('total-episodes').textContent = state.training.currentEpisode;

    // Add animation
    animateValue('sharpe-ratio');
    animateValue('max-drawdown');
    animateValue('annual-return');
}

function animateValue(elementId) {
    const element = document.getElementById(elementId);
    element.style.transform = 'scale(1.1)';
    element.style.color = 'var(--neon-yellow)';
    
    setTimeout(() => {
        element.style.transform = 'scale(1)';
        element.style.color = 'var(--neon-cyan)';
    }, 300);
}

// ========================================
// PORTFOLIO VISUALIZATION
// ========================================

function updatePortfolioWeights(weights) {
    const container = document.getElementById('weights-container');
    container.innerHTML = '';

    state.portfolio.assets.forEach((asset, index) => {
        const weight = weights[index] || 0;
        
        const barDiv = document.createElement('div');
        barDiv.className = 'weight-bar';
        barDiv.innerHTML = `
            <div class="weight-label">${asset}</div>
            <div class="weight-progress">
                <div class="weight-fill" style="width: ${weight * 100}%">
                    <span class="weight-value">${(weight * 100).toFixed(1)}%</span>
                </div>
            </div>
        `;
        
        container.appendChild(barDiv);
    });

    // Update table
    updateAssetsTable(weights);
}

function updateAssetsTable(weights) {
    const tbody = document.getElementById('assets-tbody');
    tbody.innerHTML = '';

    state.portfolio.assets.forEach((asset, index) => {
        const weight = weights[index] || 0;
        const returnVal = (Math.random() * 0.4 - 0.2).toFixed(2);
        const contribution = (weight * parseFloat(returnVal)).toFixed(2);

        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${asset}</td>
            <td>${(weight * 100).toFixed(1)}%</td>
            <td class="${parseFloat(returnVal) >= 0 ? 'text-success' : 'text-error'}">
                ${returnVal}%
            </td>
            <td>${contribution}%</td>
        `;
        
        tbody.appendChild(row);
    });
}

// ========================================
// MOCK DATA
// ========================================

function loadMockData() {
    // Set initial performance metrics
    state.performance = {
        sharpeRatio: 1.64,
        maxDrawdown: -0.132,
        annualReturn: 0.187
    };
    updatePerformanceMetrics();

    // Set initial portfolio weights
    const mockWeights = [0.12, 0.15, 0.10, 0.08, 0.11, 0.09, 0.13, 0.07, 0.08, 0.07];
    updatePortfolioWeights(mockWeights);
}

// ========================================
// ANIMATIONS
// ========================================

function startAnimations() {
    // Animate stat cards on scroll
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, { threshold: 0.1 });

    document.querySelectorAll('.stat-card, .panel-card, .viz-card').forEach(card => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(30px)';
        card.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        observer.observe(card);
    });
}

// ========================================
// CHART VIEW CONTROL
// ========================================

function updateChartView(viewType) {
    addLog(`Switching to ${viewType} view`);
    // This would update the chart.js charts based on view type
}

// ========================================
// UTILITY FUNCTIONS
// ========================================

function formatNumber(num, decimals = 2) {
    return parseFloat(num).toFixed(decimals);
}

function formatPercent(num, decimals = 1) {
    return `${(num * 100).toFixed(decimals)}%`;
}

// Export for use in other scripts
window.rlTrader = {
    state,
    updatePerformanceMetrics,
    updatePortfolioWeights,
    addLog
};
