// ========================================
// TRAINING CONTROL & API INTEGRATION
// ========================================

class TrainingController {
    constructor() {
        this.apiBase = '';  // Same origin
        this.eventSource = null;
        this.isConnected = false;
    }

    async startTraining(config) {
        try {
            const response = await fetch(`${this.apiBase}/api/train`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(config)
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            this.connectStream();
            return data;
        } catch (error) {
            console.error('Failed to start training:', error);
            throw error;
        }
    }

    async stopTraining() {
        try {
            const response = await fetch(`${this.apiBase}/api/train/stop`, {
                method: 'POST'
            });

            if (this.eventSource) {
                this.eventSource.close();
                this.eventSource = null;
            }

            return await response.json();
        } catch (error) {
            console.error('Failed to stop training:', error);
            throw error;
        }
    }

    connectStream() {
        if (this.eventSource) {
            this.eventSource.close();
        }

        this.eventSource = new EventSource(`${this.apiBase}/api/train/stream`);
        
        this.eventSource.onopen = () => {
            this.isConnected = true;
            console.log('Training stream connected');
        };

        this.eventSource.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                if (!data.heartbeat) {
                    this.handleTrainingUpdate(data);
                }
            } catch (error) {
                console.error('Failed to parse stream data:', error);
            }
        };

        this.eventSource.onerror = (error) => {
            console.error('Stream error:', error);
            this.isConnected = false;
            
            // Retry connection
            setTimeout(() => {
                if (window.rlTrader.state.training.isRunning) {
                    this.connectStream();
                }
            }, 5000);
        };
    }

    handleTrainingUpdate(data) {
        if (window.updateTrainingMetrics) {
            window.updateTrainingMetrics(data);
        }
    }

    async getStatus() {
        try {
            const response = await fetch(`${this.apiBase}/api/status`);
            return await response.json();
        } catch (error) {
            console.error('Failed to get status:', error);
            return null;
        }
    }

    async getPortfolio() {
        try {
            const response = await fetch(`${this.apiBase}/api/portfolio`);
            const data = await response.json();
            
            if (window.rlTrader && window.rlTrader.updatePortfolioWeights) {
                window.rlTrader.updatePortfolioWeights(data.weights);
            }
            
            return data;
        } catch (error) {
            console.error('Failed to get portfolio:', error);
            return null;
        }
    }

    async getPerformance() {
        try {
            const response = await fetch(`${this.apiBase}/api/performance`);
            const data = await response.json();
            
            if (window.rlTrader) {
                window.rlTrader.state.performance = data;
                window.rlTrader.updatePerformanceMetrics();
            }
            
            return data;
        } catch (error) {
            console.error('Failed to get performance:', error);
            return null;
        }
    }

    async getBacktest() {
        try {
            const response = await fetch(`${this.apiBase}/api/backtest`);
            return await response.json();
        } catch (error) {
            console.error('Failed to get backtest:', error);
            return null;
        }
    }

    disconnect() {
        if (this.eventSource) {
            this.eventSource.close();
            this.eventSource = null;
            this.isConnected = false;
        }
    }
}

// Initialize controller
const trainingController = new TrainingController();

// Periodic portfolio updates
setInterval(async () => {
    if (!window.rlTrader?.state.training.isRunning) {
        await trainingController.getPortfolio();
    }
}, 5000);

// Export
window.trainingController = trainingController;
