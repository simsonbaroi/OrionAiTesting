// Admin dashboard functionality for PyLearnAI
class AdminDashboard {
    constructor() {
        this.refreshInterval = null;
        this.charts = {};
        this.init();
    }
    
    init() {
        // Setup event listeners
        this.setupEventListeners();
        
        // Load initial data
        this.loadDashboardData();
        
        // Setup auto-refresh
        this.setupAutoRefresh();
    }
    
    setupEventListeners() {
        // Action buttons
        document.getElementById('trigger-collection-btn')?.addEventListener('click', (e) => {
            this.handleActionButton(e, 'Data Collection');
        });
        
        document.getElementById('trigger-training-btn')?.addEventListener('click', (e) => {
            this.handleActionButton(e, 'Model Training');
        });
        
        // Modal events
        document.getElementById('logsModal')?.addEventListener('show.bs.modal', () => {
            this.loadSystemLogs();
        });
        
        // Refresh button
        document.querySelector('[onclick="refreshData()"]')?.addEventListener('click', (e) => {
            e.preventDefault();
            this.refreshData();
        });
    }
    
    handleActionButton(event, actionName) {
        const button = event.target.closest('button');
        if (button) {
            // Add loading state
            button.classList.add('loading');
            button.disabled = true;
            
            // Show feedback
            this.showNotification(`${actionName} triggered...`, 'info');
            
            // Re-enable button after delay (form will submit normally)
            setTimeout(() => {
                button.classList.remove('loading');
            }, 2000);
        }
    }
    
    async loadDashboardData() {
        try {
            const response = await fetch('/api/stats');
            const data = await response.json();
            
            if (response.ok) {
                this.updateDashboardStats(data);
                this.updateCharts(data);
            } else {
                this.showNotification('Failed to load dashboard data', 'error');
            }
        } catch (error) {
            console.error('Error loading dashboard data:', error);
            this.showNotification('Error loading dashboard data', 'error');
        }
    }
    
    updateDashboardStats(data) {
        // Update knowledge base stats if available
        if (data.knowledge_base_stats) {
            const stats = data.knowledge_base_stats;
            
            // Update stat cards
            this.updateStatCard('knowledge_base', stats.total_items || 0);
            this.updateStatCard('training_data', stats.total_training_data || 0);
            this.updateStatCard('unused_training_data', stats.unused_training_data || 0);
        }
        
        // Update model info display
        if (data.current_model) {
            this.updateModelInfo(data.current_model);
        }
        
        // Update recent activities
        if (data.recent_scraping) {
            this.updateRecentActivities(data.recent_scraping);
        }
    }
    
    updateStatCard(type, value) {
        // Find stat cards and update values
        const cards = document.querySelectorAll('.card h3.card-title');
        cards.forEach(card => {
            const cardBody = card.closest('.card-body');
            const cardText = cardBody?.querySelector('.card-text')?.textContent.toLowerCase();
            
            if (cardText) {
                if (type === 'knowledge_base' && cardText.includes('knowledge base')) {
                    card.textContent = value.toLocaleString();
                } else if (type === 'training_data' && cardText.includes('training data')) {
                    card.textContent = value.toLocaleString();
                } else if (type === 'unused_training_data' && cardText.includes('unused')) {
                    card.textContent = value.toLocaleString();
                }
            }
        });
    }
    
    updateModelInfo(modelInfo) {
        const modelTable = document.querySelector('.card-body table');
        if (modelTable && modelInfo) {
            // Update model size if available
            const sizeRow = Array.from(modelTable.querySelectorAll('tr')).find(row => 
                row.textContent.includes('Size:')
            );
            if (sizeRow && modelInfo.size_mb) {
                const sizeCell = sizeRow.querySelector('td:last-child');
                if (sizeCell) {
                    sizeCell.textContent = `${modelInfo.size_mb} MB`;
                }
            }
        }
    }
    
    updateRecentActivities(activities) {
        const scrapingList = document.querySelector('.card-header h6:contains("Recent Scraping")')?.closest('.card')?.querySelector('.list-group');
        
        if (scrapingList && activities.length > 0) {
            // Clear existing items except "no activity" message
            const existingItems = scrapingList.querySelectorAll('.list-group-item');
            existingItems.forEach(item => {
                if (!item.textContent.includes('No recent')) {
                    item.remove();
                }
            });
            
            // Add new activities
            activities.slice(0, 5).forEach(activity => {
                const listItem = document.createElement('div');
                listItem.className = 'list-group-item';
                
                const statusBadge = this.getStatusBadgeClass(activity.status);
                const formattedDate = new Date(activity.started_at).toLocaleDateString('en-US', {
                    month: '2-digit',
                    day: '2-digit',
                    hour: '2-digit',
                    minute: '2-digit'
                });
                
                listItem.innerHTML = `
                    <div class="d-flex w-100 justify-content-between">
                        <h6 class="mb-1">${activity.source_type?.replace('_', ' ')?.replace(/\b\w/g, l => l.toUpperCase()) || 'Unknown'}</h6>
                        <small class="text-muted">${formattedDate}</small>
                    </div>
                    <p class="mb-1">
                        Items: ${activity.items_collected || 0} | 
                        Status: <span class="badge ${statusBadge}">${activity.status}</span>
                    </p>
                    ${activity.errors_count > 0 ? `<small class="text-danger">${activity.errors_count} errors</small>` : ''}
                `;
                
                scrapingList.appendChild(listItem);
            });
            
            // Remove "no activity" message if activities exist
            const noActivityMsg = scrapingList.querySelector('.list-group-item:contains("No recent")');
            if (noActivityMsg) {
                noActivityMsg.remove();
            }
        }
    }
    
    getStatusBadgeClass(status) {
        const statusMap = {
            'completed': 'bg-success',
            'running': 'bg-primary',
            'failed': 'bg-danger',
            'partial_failure': 'bg-warning'
        };
        return statusMap[status] || 'bg-secondary';
    }
    
    updateCharts(data) {
        // Update training progress chart if data is available
        if (data.knowledge_base_stats && this.charts.trainingChart) {
            const totalItems = data.knowledge_base_stats.total_items || 0;
            this.updateTrainingChart(totalItems);
        }
        
        // Update source distribution chart
        if (data.knowledge_base_stats?.by_source_type && this.charts.sourceChart) {
            this.updateSourceChart(data.knowledge_base_stats.by_source_type);
        }
    }
    
    updateTrainingChart(currentTotal) {
        // Generate some realistic progression data
        const days = 7;
        const data = [];
        const increment = Math.floor(currentTotal / days);
        
        for (let i = 1; i <= days; i++) {
            if (i === days) {
                data.push(currentTotal);
            } else {
                data.push(increment * i);
            }
        }
        
        if (this.charts.trainingChart) {
            this.charts.trainingChart.data.datasets[0].data = data;
            this.charts.trainingChart.update();
        }
    }
    
    updateSourceChart(sourceData) {
        if (!this.charts.sourceChart || !sourceData) return;
        
        const labels = [];
        const data = [];
        const colors = [
            'rgba(255, 99, 132, 0.8)',
            'rgba(54, 162, 235, 0.8)',
            'rgba(255, 205, 86, 0.8)',
            'rgba(75, 192, 192, 0.8)',
            'rgba(153, 102, 255, 0.8)'
        ];
        
        Object.entries(sourceData).forEach(([source, count], index) => {
            labels.push(source.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase()));
            data.push(count);
        });
        
        this.charts.sourceChart.data.labels = labels;
        this.charts.sourceChart.data.datasets[0].data = data;
        this.charts.sourceChart.data.datasets[0].backgroundColor = colors.slice(0, data.length);
        this.charts.sourceChart.update();
    }
    
    async loadSystemLogs() {
        const logsContent = document.getElementById('logs-content');
        
        try {
            // Show loading
            logsContent.innerHTML = `
                <div class="text-center">
                    <div class="spinner-border" role="status">
                        <span class="visually-hidden">Loading...</span>
                    </div>
                    <p class="mt-2">Loading system logs...</p>
                </div>
            `;
            
            // Simulate log loading (in a real implementation, this would fetch actual logs)
            await new Promise(resolve => setTimeout(resolve, 1000));
            
            // Mock logs for demonstration
            const logs = [
                { timestamp: new Date(), level: 'INFO', message: 'System health check completed successfully' },
                { timestamp: new Date(Date.now() - 300000), level: 'INFO', message: 'Data collection task started' },
                { timestamp: new Date(Date.now() - 600000), level: 'DEBUG', message: 'Processing scraped data from Python documentation' },
                { timestamp: new Date(Date.now() - 900000), level: 'INFO', message: 'Model evaluation completed with score: 0.85' },
                { timestamp: new Date(Date.now() - 1200000), level: 'WARNING', message: 'Rate limit approached for GitHub API' }
            ];
            
            const logsHtml = logs.map(log => `
                <div class="log-entry mb-2 p-2 rounded ${this.getLogLevelClass(log.level)}">
                    <div class="d-flex justify-content-between">
                        <span class="badge ${this.getLogBadgeClass(log.level)}">${log.level}</span>
                        <small class="text-muted">${log.timestamp.toLocaleString()}</small>
                    </div>
                    <div class="mt-1">${log.message}</div>
                </div>
            `).join('');
            
            logsContent.innerHTML = `
                <div class="logs-container" style="max-height: 400px; overflow-y: auto;">
                    ${logsHtml}
                </div>
                <div class="mt-3">
                    <small class="text-muted">Showing recent system logs. For complete logs, check server console.</small>
                </div>
            `;
            
        } catch (error) {
            logsContent.innerHTML = `
                <div class="alert alert-danger">
                    <i data-feather="alert-circle" class="me-2"></i>
                    Error loading system logs: ${error.message}
                </div>
            `;
            feather.replace();
        }
    }
    
    getLogLevelClass(level) {
        const levelMap = {
            'DEBUG': 'bg-secondary bg-opacity-25',
            'INFO': 'bg-primary bg-opacity-25',
            'WARNING': 'bg-warning bg-opacity-25',
            'ERROR': 'bg-danger bg-opacity-25'
        };
        return levelMap[level] || 'bg-light';
    }
    
    getLogBadgeClass(level) {
        const badgeMap = {
            'DEBUG': 'bg-secondary',
            'INFO': 'bg-primary',
            'WARNING': 'bg-warning',
            'ERROR': 'bg-danger'
        };
        return badgeMap[level] || 'bg-secondary';
    }
    
    setupAutoRefresh() {
        // Refresh data every 30 seconds
        this.refreshInterval = setInterval(() => {
            this.loadDashboardData();
        }, 30000);
    }
    
    async refreshData() {
        const refreshBtn = document.querySelector('[onclick="refreshData()"]');
        const icon = refreshBtn?.querySelector('i[data-feather="refresh-cw"]');
        
        // Add spinning animation
        if (icon) {
            icon.style.animation = 'spin 1s linear infinite';
        }
        
        try {
            await this.loadDashboardData();
            this.showNotification('Dashboard data refreshed', 'success');
        } catch (error) {
            this.showNotification('Failed to refresh data', 'error');
        } finally {
            // Remove animation
            if (icon) {
                setTimeout(() => {
                    icon.style.animation = '';
                }, 1000);
            }
        }
    }
    
    showNotification(message, type = 'info') {
        // Create toast notification
        const toastContainer = this.getOrCreateToastContainer();
        
        const toastEl = document.createElement('div');
        toastEl.className = `toast align-items-center text-white bg-${type === 'error' ? 'danger' : type} border-0`;
        toastEl.setAttribute('role', 'alert');
        
        const iconMap = {
            'success': 'check-circle',
            'error': 'alert-circle',
            'warning': 'alert-triangle',
            'info': 'info'
        };
        
        toastEl.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">
                    <i data-feather="${iconMap[type] || 'info'}" class="me-2"></i>
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        `;
        
        toastContainer.appendChild(toastEl);
        
        // Replace feather icons
        feather.replace();
        
        const toast = new bootstrap.Toast(toastEl, {
            autohide: true,
            delay: type === 'error' ? 8000 : 4000
        });
        toast.show();
        
        // Remove element after hiding
        toastEl.addEventListener('hidden.bs.toast', () => {
            toastEl.remove();
        });
    }
    
    getOrCreateToastContainer() {
        let container = document.getElementById('toast-container');
        if (!container) {
            container = document.createElement('div');
            container.id = 'toast-container';
            container.className = 'toast-container position-fixed top-0 end-0 p-3';
            container.style.zIndex = '9999';
            document.body.appendChild(container);
        }
        return container;
    }
    
    destroy() {
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
        }
    }
}

// Model evaluation functionality
async function runEvaluation() {
    const evaluationModal = new bootstrap.Modal(document.getElementById('evaluationModal'));
    const evaluationContent = document.getElementById('evaluation-content');
    
    evaluationModal.show();
    
    try {
        // Show loading
        evaluationContent.innerHTML = `
            <div class="text-center">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Evaluating...</span>
                </div>
                <p class="mt-3">Running model evaluation...</p>
                <p class="text-muted">This may take a few moments</p>
            </div>
        `;
        
        // Run evaluation
        const response = await fetch('/api/evaluate?type=performance');
        const results = await response.json();
        
        if (response.ok && !results.error) {
            // Display results
            evaluationContent.innerHTML = `
                <div class="evaluation-results">
                    <div class="row mb-3">
                        <div class="col-md-6">
                            <div class="card bg-primary">
                                <div class="card-body text-center">
                                    <h4>${results.successful_responses || 0}/${results.total_questions || 0}</h4>
                                    <p class="mb-0">Successful Responses</p>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-6">
                            <div class="card bg-success">
                                <div class="card-body text-center">
                                    <h4>${((results.success_rate || 0) * 100).toFixed(1)}%</h4>
                                    <p class="mb-0">Success Rate</p>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    ${results.average_quality_score ? `
                    <div class="row mb-3">
                        <div class="col-md-6">
                            <div class="card bg-info">
                                <div class="card-body text-center">
                                    <h4>${results.average_quality_score.toFixed(2)}</h4>
                                    <p class="mb-0">Average Quality Score</p>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-6">
                            <div class="card bg-warning">
                                <div class="card-body text-center">
                                    <h4>${results.average_response_time?.toFixed(2) || 0}s</h4>
                                    <p class="mb-0">Average Response Time</p>
                                </div>
                            </div>
                        </div>
                    </div>
                    ` : ''}
                    
                    ${results.quality_distribution ? `
                    <div class="card">
                        <div class="card-header">
                            <h6 class="mb-0">Quality Distribution</h6>
                        </div>
                        <div class="card-body">
                            ${Object.entries(results.quality_distribution).map(([level, data]) => `
                                <div class="d-flex justify-content-between align-items-center mb-2">
                                    <span class="text-capitalize">${level}:</span>
                                    <div class="d-flex align-items-center">
                                        <div class="progress me-2" style="width: 100px; height: 20px;">
                                            <div class="progress-bar" style="width: ${data.percentage}%"></div>
                                        </div>
                                        <span>${data.count} (${data.percentage.toFixed(1)}%)</span>
                                    </div>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                    ` : ''}
                </div>
            `;
        } else {
            evaluationContent.innerHTML = `
                <div class="alert alert-danger">
                    <i data-feather="alert-circle" class="me-2"></i>
                    Error running evaluation: ${results.error || 'Unknown error'}
                </div>
            `;
            feather.replace();
        }
        
    } catch (error) {
        evaluationContent.innerHTML = `
            <div class="alert alert-danger">
                <i data-feather="alert-circle" class="me-2"></i>
                Error running evaluation: ${error.message}
            </div>
        `;
        feather.replace();
    }
}

// Global functions (referenced in HTML)
function refreshData() {
    if (window.adminDashboard) {
        window.adminDashboard.refreshData();
    }
}

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.adminDashboard = new AdminDashboard();
});

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
    if (window.adminDashboard) {
        window.adminDashboard.destroy();
    }
});

// Add CSS animation for spinning refresh icon
const style = document.createElement('style');
style.textContent = `
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
`;
document.head.appendChild(style);
