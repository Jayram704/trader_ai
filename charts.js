// ========================================
// CHART.JS CONFIGURATION & MANAGEMENT
// ========================================

// Chart.js theme configuration
const chartDefaults = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
        legend: {
            labels: {
                color: '#a8a8b8',
                font: {
                    family: "'JetBrains Mono', monospace",
                    size: 11
                }
            }
        },
        tooltip: {
            backgroundColor: 'rgba(26, 26, 36, 0.95)',
            titleColor: '#00f3ff',
            bodyColor: '#ffffff',
            borderColor: '#00f3ff',
            borderWidth: 1,
            padding: 12,
            displayColors: true,
            titleFont: {
                family: "'JetBrains Mono', monospace",
                size: 12,
                weight: 'bold'
            },
            bodyFont: {
                family: "'JetBrains Mono', monospace",
                size: 11
            }
        }
    },
    scales: {
        x: {
            grid: {
                color: 'rgba(107, 107, 123, 0.1)',
                borderColor: 'rgba(107, 107, 123, 0.3)'
            },
            ticks: {
                color: '#6b6b7b',
                font: {
                    family: "'JetBrains Mono', monospace",
                    size: 10
                }
            }
        },
        y: {
            grid: {
                color: 'rgba(107, 107, 123, 0.1)',
                borderColor: 'rgba(107, 107, 123, 0.3)'
            },
            ticks: {
                color: '#6b6b7b',
                font: {
                    family: "'JetBrains Mono', monospace",
                    size: 10
                }
            }
        }
    }
};

// Global chart instances
let charts = {};

// ========================================
// INITIALIZE CHARTS
// ========================================

document.addEventListener('DOMContentLoaded', () => {
    initializeCharts();
});

function initializeCharts() {
    // Portfolio Value Chart
    charts.portfolio = createPortfolioChart();
    
    // Sharpe Ratio Chart
    charts.sharpe = createSharpeChart();
    
    // Drawdown Chart
    charts.drawdown = createDrawdownChart();
    
    // Efficient Frontier Chart
    charts.frontier = createFrontierChart();

    // Start real-time updates
    startChartUpdates();
}

// ========================================
// PORTFOLIO VALUE CHART
// ========================================

function createPortfolioChart() {
    const ctx = document.getElementById('portfolio-chart');
    if (!ctx) return null;

    const gradient = ctx.getContext('2d').createLinearGradient(0, 0, 0, 400);
    gradient.addColorStop(0, 'rgba(0, 243, 255, 0.4)');
    gradient.addColorStop(1, 'rgba(0, 243, 255, 0)');

    return new Chart(ctx, {
        type: 'line',
        data: {
            labels: generateDateLabels(100),
            datasets: [
                {
                    label: 'RL Agent',
                    data: generateMockPortfolioData(100, 100000, 0.002),
                    borderColor: '#00f3ff',
                    backgroundColor: gradient,
                    borderWidth: 2,
                    fill: true,
                    tension: 0.4,
                    pointRadius: 0,
                    pointHoverRadius: 4
                },
                {
                    label: 'Equal Weight',
                    data: generateMockPortfolioData(100, 100000, 0.0015),
                    borderColor: '#8338ec',
                    backgroundColor: 'transparent',
                    borderWidth: 2,
                    borderDash: [5, 5],
                    fill: false,
                    tension: 0.4,
                    pointRadius: 0,
                    pointHoverRadius: 4
                }
            ]
        },
        options: {
            ...chartDefaults,
            interaction: {
                intersect: false,
                mode: 'index'
            },
            plugins: {
                ...chartDefaults.plugins,
                title: {
                    display: false
                },
                legend: {
                    ...chartDefaults.plugins.legend,
                    position: 'top'
                }
            },
            scales: {
                ...chartDefaults.scales,
                y: {
                    ...chartDefaults.scales.y,
                    title: {
                        display: true,
                        text: 'Portfolio Value ($)',
                        color: '#a8a8b8'
                    }
                }
            }
        }
    });
}

// ========================================
// SHARPE RATIO CHART
// ========================================

function createSharpeChart() {
    const ctx = document.getElementById('sharpe-chart');
    if (!ctx) return null;

    return new Chart(ctx, {
        type: 'line',
        data: {
            labels: generateEpisodeLabels(100),
            datasets: [{
                label: 'Sharpe Ratio',
                data: generateSharpeMockData(100),
                borderColor: '#00ff88',
                backgroundColor: 'rgba(0, 255, 136, 0.1)',
                borderWidth: 2,
                fill: true,
                tension: 0.4,
                pointRadius: 0,
                pointHoverRadius: 4
            }]
        },
        options: {
            ...chartDefaults,
            plugins: {
                ...chartDefaults.plugins,
                annotation: {
                    annotations: {
                        targetLine: {
                            type: 'line',
                            yMin: 1.5,
                            yMax: 1.5,
                            borderColor: '#ff006e',
                            borderWidth: 2,
                            borderDash: [10, 5],
                            label: {
                                content: 'Target (1.5)',
                                enabled: true,
                                position: 'end',
                                backgroundColor: 'rgba(255, 0, 110, 0.8)',
                                color: '#fff'
                            }
                        }
                    }
                }
            },
            scales: {
                ...chartDefaults.scales,
                y: {
                    ...chartDefaults.scales.y,
                    title: {
                        display: true,
                        text: 'Sharpe Ratio',
                        color: '#a8a8b8'
                    }
                }
            }
        }
    });
}

// ========================================
// DRAWDOWN CHART
// ========================================

function createDrawdownChart() {
    const ctx = document.getElementById('drawdown-chart');
    if (!ctx) return null;

    return new Chart(ctx, {
        type: 'line',
        data: {
            labels: generateDateLabels(100),
            datasets: [{
                label: 'Drawdown',
                data: generateDrawdownMockData(100),
                borderColor: '#ff3864',
                backgroundColor: 'rgba(255, 56, 100, 0.2)',
                borderWidth: 2,
                fill: true,
                tension: 0.4,
                pointRadius: 0,
                pointHoverRadius: 4
            }]
        },
        options: {
            ...chartDefaults,
            plugins: {
                ...chartDefaults.plugins,
                annotation: {
                    annotations: {
                        constraintLine: {
                            type: 'line',
                            yMin: -0.15,
                            yMax: -0.15,
                            borderColor: '#ffbe0b',
                            borderWidth: 2,
                            borderDash: [10, 5],
                            label: {
                                content: 'Limit (-15%)',
                                enabled: true,
                                position: 'start',
                                backgroundColor: 'rgba(255, 190, 11, 0.8)',
                                color: '#000'
                            }
                        }
                    }
                }
            },
            scales: {
                ...chartDefaults.scales,
                y: {
                    ...chartDefaults.scales.y,
                    title: {
                        display: true,
                        text: 'Drawdown (%)',
                        color: '#a8a8b8'
                    },
                    ticks: {
                        ...chartDefaults.scales.y.ticks,
                        callback: function(value) {
                            return (value * 100).toFixed(0) + '%';
                        }
                    }
                }
            }
        }
    });
}

// ========================================
// EFFICIENT FRONTIER CHART
// ========================================

function createFrontierChart() {
    const ctx = document.getElementById('frontier-chart');
    if (!ctx) return null;

    return new Chart(ctx, {
        type: 'scatter',
        data: {
            datasets: [
                {
                    label: 'Random Portfolios',
                    data: generateFrontierPoints(1000),
                    backgroundColor: 'rgba(131, 56, 236, 0.3)',
                    borderColor: 'rgba(131, 56, 236, 0.5)',
                    pointRadius: 3,
                    pointHoverRadius: 5
                },
                {
                    label: 'RL Agent',
                    data: [{x: 0.18, y: 0.22}],
                    backgroundColor: '#00f3ff',
                    borderColor: '#00f3ff',
                    pointRadius: 10,
                    pointHoverRadius: 12,
                    pointStyle: 'star'
                },
                {
                    label: 'Equal Weight',
                    data: [{x: 0.20, y: 0.15}],
                    backgroundColor: '#8338ec',
                    borderColor: '#8338ec',
                    pointRadius: 8,
                    pointHoverRadius: 10,
                    pointStyle: 'triangle'
                },
                {
                    label: 'Markowitz',
                    data: [{x: 0.16, y: 0.19}],
                    backgroundColor: '#00ff88',
                    borderColor: '#00ff88',
                    pointRadius: 8,
                    pointHoverRadius: 10,
                    pointStyle: 'rect'
                }
            ]
        },
        options: {
            ...chartDefaults,
            scales: {
                x: {
                    ...chartDefaults.scales.x,
                    title: {
                        display: true,
                        text: 'Volatility (Risk)',
                        color: '#a8a8b8'
                    },
                    ticks: {
                        ...chartDefaults.scales.x.ticks,
                        callback: function(value) {
                            return (value * 100).toFixed(0) + '%';
                        }
                    }
                },
                y: {
                    ...chartDefaults.scales.y,
                    title: {
                        display: true,
                        text: 'Expected Return',
                        color: '#a8a8b8'
                    },
                    ticks: {
                        ...chartDefaults.scales.y.ticks,
                        callback: function(value) {
                            return (value * 100).toFixed(0) + '%';
                        }
                    }
                }
            },
            plugins: {
                ...chartDefaults.plugins,
                legend: {
                    ...chartDefaults.plugins.legend,
                    position: 'bottom'
                }
            }
        }
    });
}

// ========================================
// MOCK DATA GENERATORS
// ========================================

function generateDateLabels(count) {
    const labels = [];
    const now = new Date();
    for (let i = count - 1; i >= 0; i--) {
        const date = new Date(now - i * 24 * 60 * 60 * 1000);
        labels.push(date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }));
    }
    return labels;
}

function generateEpisodeLabels(count) {
    return Array.from({length: count}, (_, i) => `Ep ${i + 1}`);
}

function generateMockPortfolioData(count, start, dailyReturn) {
    const data = [start];
    for (let i = 1; i < count; i++) {
        const change = (Math.random() - 0.4) * dailyReturn;
        data.push(data[i-1] * (1 + change));
    }
    return data;
}

function generateSharpeMockData(count) {
    const data = [];
    for (let i = 0; i < count; i++) {
        const progress = i / count;
        const value = 0.8 + progress * 1.2 + (Math.random() - 0.5) * 0.3;
        data.push(Math.max(0, value));
    }
    return data;
}

function generateDrawdownMockData(count) {
    const data = [0];
    let maxValue = 0;
    for (let i = 1; i < count; i++) {
        const change = (Math.random() - 0.5) * 0.02;
        const cumReturn = (data[i-1] || 0) + change;
        maxValue = Math.max(maxValue, cumReturn);
        const drawdown = cumReturn - maxValue;
        data.push(Math.max(-0.2, drawdown));
    }
    return data;
}

function generateFrontierPoints(count) {
    const points = [];
    for (let i = 0; i < count; i++) {
        const risk = Math.random() * 0.3 + 0.05;
        const returnVal = risk * (1.5 + Math.random() * 0.5) - 0.05 + (Math.random() - 0.5) * 0.1;
        points.push({x: risk, y: Math.max(0, returnVal)});
    }
    return points;
}

// ========================================
// CHART UPDATES
// ========================================

function updateTrainingCharts(data) {
    // Update Sharpe chart
    if (charts.sharpe && data.sharpe !== undefined) {
        const sharpeData = charts.sharpe.data.datasets[0].data;
        sharpeData.push(data.sharpe);
        if (sharpeData.length > 100) sharpeData.shift();
        
        charts.sharpe.data.labels.push(`Ep ${data.episode}`);
        if (charts.sharpe.data.labels.length > 100) {
            charts.sharpe.data.labels.shift();
        }
        
        charts.sharpe.update('none');
    }
}

function startChartUpdates() {
    // Simulate real-time updates
    setInterval(() => {
        if (window.rlTrader && window.rlTrader.state.training.isRunning) {
            // Charts update via updateTrainingCharts called from main.js
        }
    }, 1000);
}

// Export for global access
window.charts = charts;
window.updateTrainingCharts = updateTrainingCharts;
