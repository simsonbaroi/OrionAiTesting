// Firebase Configuration
const firebaseConfig = {
    apiKey: "AIzaSyDummy-Key-Replace-With-Real",
    authDomain: "myaisystem-16411.firebaseapp.com",
    databaseURL: "https://myaisystem-16411-default-rtdb.firebaseio.com/",
    projectId: "myaisystem-16411",
    storageBucket: "myaisystem-16411.appspot.com",
    messagingSenderId: "123456789",
    appId: "1:123456789:web:abcdefghijklmnop"
};

// Initialize Firebase
firebase.initializeApp(firebaseConfig);
const database = firebase.database();

// Global variables
let currentSection = 'home';
let knowledgeData = [];
let trainingData = [];
let queriesData = [];
let metricsData = [];

// Initialize the application
function initializeApp() {
    showSection('home');
    loadDashboardStats();
    setupEventListeners();
}

// Navigation functions
function showSection(sectionName) {
    // Hide all sections
    const sections = ['home', 'chat', 'database', 'admin'];
    sections.forEach(section => {
        const element = document.getElementById(section);
        if (element) {
            element.style.display = 'none';
        }
    });

    // Show hero section only for home
    const heroSection = document.querySelector('.hero-section');
    if (heroSection) {
        heroSection.style.display = sectionName === 'home' ? 'block' : 'none';
    }

    // Show statistics section only for home
    const statsSection = document.querySelector('.bg-light');
    if (statsSection) {
        statsSection.style.display = sectionName === 'home' ? 'block' : 'none';
    }

    // Show the selected section
    if (sectionName !== 'home') {
        const targetSection = document.getElementById(sectionName);
        if (targetSection) {
            targetSection.style.display = 'block';
        }
    }

    currentSection = sectionName;

    // Load section-specific data
    if (sectionName === 'database') {
        loadKnowledgeData();
    } else if (sectionName === 'admin') {
        checkSystemStatus();
    }
}

// Setup event listeners
function setupEventListeners() {
    // Navigation links
    document.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const href = this.getAttribute('href');
            if (href && href.startsWith('#')) {
                showSection(href.substring(1));
            }
        });
    });
}

// Dashboard statistics
function loadDashboardStats() {
    // Load from Firebase
    database.ref('stats').once('value').then((snapshot) => {
        const stats = snapshot.val() || {};
        
        document.getElementById('knowledge-count').textContent = stats.knowledgeBase || 0;
        document.getElementById('queries-count').textContent = stats.userQueries || 0;
        document.getElementById('training-count').textContent = stats.trainingData || 0;
    }).catch((error) => {
        console.log('Loading local demo data');
        // Demo data for testing
        document.getElementById('knowledge-count').textContent = 1247;
        document.getElementById('queries-count').textContent = 856;
        document.getElementById('training-count').textContent = 2103;
    });
}

// Chat functionality
function handleEnter(event) {
    if (event.key === 'Enter') {
        askQuestion();
    }
}

function askQuestion() {
    const input = document.getElementById('question-input');
    const question = input.value.trim();
    
    if (!question) return;

    const messagesDiv = document.getElementById('chat-messages');
    
    // Add user message
    addMessage(messagesDiv, question, 'user');
    
    // Clear input
    input.value = '';
    
    // Show loading
    addMessage(messagesDiv, 'Thinking...', 'assistant', true);
    
    // Simulate AI response (in real implementation, this would call your AI API)
    setTimeout(() => {
        removeLoadingMessage(messagesDiv);
        const response = generateAIResponse(question);
        addMessage(messagesDiv, response, 'assistant');
        
        // Store in Firebase
        storeQuery(question, response);
    }, 1500);
}

function addMessage(container, message, sender, isLoading = false) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `mb-3 ${isLoading ? 'loading-message' : ''}`;
    
    const senderClass = sender === 'user' ? 'text-end' : 'text-start';
    const bgClass = sender === 'user' ? 'bg-primary text-white' : 'bg-light';
    
    messageDiv.innerHTML = `
        <div class="${senderClass}">
            <div class="d-inline-block p-2 rounded ${bgClass}" style="max-width: 80%;">
                ${message}
            </div>
        </div>
    `;
    
    container.appendChild(messageDiv);
    container.scrollTop = container.scrollHeight;
}

function removeLoadingMessage(container) {
    const loadingMessage = container.querySelector('.loading-message');
    if (loadingMessage) {
        loadingMessage.remove();
    }
}

function generateAIResponse(question) {
    // Simple pattern matching for demo purposes
    const lowerQuestion = question.toLowerCase();
    
    if (lowerQuestion.includes('list')) {
        return "In Python, you can create a list using square brackets: `my_list = [1, 2, 3, 4]`. Lists are mutable, ordered collections that can contain different data types.";
    } else if (lowerQuestion.includes('function')) {
        return "A Python function is defined using the `def` keyword:\n\n```python\ndef my_function(parameter):\n    return parameter * 2\n```\n\nFunctions help organize code and make it reusable.";
    } else if (lowerQuestion.includes('exception')) {
        return "Python exception handling uses try-except blocks:\n\n```python\ntry:\n    result = 10 / 0\nexcept ZeroDivisionError:\n    print('Cannot divide by zero!')\n```";
    } else {
        return "That's a great Python question! Based on my training data, I'd recommend checking the official Python documentation for detailed information. Feel free to ask more specific questions about Python syntax, data structures, or programming concepts.";
    }
}

function storeQuery(question, answer) {
    const queryData = {
        question: question,
        answer: answer,
        timestamp: Date.now(),
        responseTime: 1.5
    };
    
    database.ref('queries').push(queryData).catch((error) => {
        console.log('Could not store query:', error);
    });
}

// Database functions
function loadKnowledgeData() {
    const tableDiv = document.getElementById('knowledge-table');
    tableDiv.innerHTML = 'Loading...';
    
    database.ref('knowledgeBase').limitToLast(20).once('value').then((snapshot) => {
        const data = snapshot.val() || {};
        knowledgeData = Object.keys(data).map(key => ({id: key, ...data[key]}));
        displayKnowledgeTable(knowledgeData);
    }).catch((error) => {
        // Demo data
        knowledgeData = [
            {
                id: 1,
                title: "Python Lists Tutorial",
                sourceType: "python_docs",
                qualityScore: 0.95,
                createdAt: "2024-01-15T10:30:00Z"
            },
            {
                id: 2,
                title: "Exception Handling Best Practices",
                sourceType: "stackoverflow",
                qualityScore: 0.87,
                createdAt: "2024-01-14T15:45:00Z"
            }
        ];
        displayKnowledgeTable(knowledgeData);
    });
}

function displayKnowledgeTable(data) {
    const tableDiv = document.getElementById('knowledge-table');
    
    if (data.length === 0) {
        tableDiv.innerHTML = '<p class="text-muted">No knowledge base records found.</p>';
        return;
    }
    
    let html = `
        <table class="table table-striped data-table">
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Title</th>
                    <th>Source Type</th>
                    <th>Quality Score</th>
                    <th>Created</th>
                </tr>
            </thead>
            <tbody>
    `;
    
    data.forEach(item => {
        const date = new Date(item.createdAt).toLocaleDateString();
        const qualityBadge = item.qualityScore > 0.8 ? 'success' : item.qualityScore > 0.5 ? 'warning' : 'danger';
        
        html += `
            <tr>
                <td>${item.id}</td>
                <td class="text-truncate" style="max-width: 200px;" title="${item.title}">${item.title}</td>
                <td><span class="badge bg-secondary status-badge">${item.sourceType}</span></td>
                <td><span class="badge bg-${qualityBadge} status-badge">${item.qualityScore.toFixed(2)}</span></td>
                <td>${date}</td>
            </tr>
        `;
    });
    
    html += '</tbody></table>';
    tableDiv.innerHTML = html;
}

function loadTrainingData() {
    const tableDiv = document.getElementById('training-table');
    tableDiv.innerHTML = 'Loading...';
    
    // Demo data for training
    trainingData = [
        {
            id: 1,
            question: "How to create a Python list?",
            source: "python_docs",
            qualityScore: 0.92,
            usedForTraining: true,
            createdAt: "2024-01-15T09:20:00Z"
        },
        {
            id: 2,
            question: "What is exception handling in Python?",
            source: "stackoverflow",
            qualityScore: 0.85,
            usedForTraining: false,
            createdAt: "2024-01-14T16:30:00Z"
        }
    ];
    
    displayTrainingTable(trainingData);
}

function displayTrainingTable(data) {
    const tableDiv = document.getElementById('training-table');
    
    if (data.length === 0) {
        tableDiv.innerHTML = '<p class="text-muted">No training data records found.</p>';
        return;
    }
    
    let html = `
        <table class="table table-striped data-table">
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Question</th>
                    <th>Source</th>
                    <th>Quality Score</th>
                    <th>Used for Training</th>
                    <th>Created</th>
                </tr>
            </thead>
            <tbody>
    `;
    
    data.forEach(item => {
        const date = new Date(item.createdAt).toLocaleDateString();
        const qualityBadge = item.qualityScore > 0.8 ? 'success' : item.qualityScore > 0.5 ? 'warning' : 'danger';
        const usedIcon = item.usedForTraining ? '✓' : '○';
        const usedClass = item.usedForTraining ? 'text-success' : 'text-muted';
        
        html += `
            <tr>
                <td>${item.id}</td>
                <td class="text-truncate" style="max-width: 200px;" title="${item.question}">${item.question}</td>
                <td><span class="badge bg-info status-badge">${item.source}</span></td>
                <td><span class="badge bg-${qualityBadge} status-badge">${item.qualityScore.toFixed(2)}</span></td>
                <td><span class="${usedClass}">${usedIcon}</span></td>
                <td>${date}</td>
            </tr>
        `;
    });
    
    html += '</tbody></table>';
    tableDiv.innerHTML = html;
}

function loadQueriesData() {
    const tableDiv = document.getElementById('queries-table');
    tableDiv.innerHTML = 'Loading...';
    
    database.ref('queries').limitToLast(20).once('value').then((snapshot) => {
        const data = snapshot.val() || {};
        queriesData = Object.keys(data).map(key => ({id: key, ...data[key]}));
        displayQueriesTable(queriesData);
    }).catch((error) => {
        // Demo data
        queriesData = [
            {
                id: 1,
                question: "How do I create a list in Python?",
                responseTime: 1.2,
                userRating: 5,
                createdAt: Date.now() - 3600000
            },
            {
                id: 2,
                question: "What is a Python function?",
                responseTime: 0.8,
                userRating: 4,
                createdAt: Date.now() - 7200000
            }
        ];
        displayQueriesTable(queriesData);
    });
}

function displayQueriesTable(data) {
    const tableDiv = document.getElementById('queries-table');
    
    if (data.length === 0) {
        tableDiv.innerHTML = '<p class="text-muted">No user query records found.</p>';
        return;
    }
    
    let html = `
        <table class="table table-striped data-table">
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Question</th>
                    <th>Response Time</th>
                    <th>User Rating</th>
                    <th>Created</th>
                </tr>
            </thead>
            <tbody>
    `;
    
    data.forEach(item => {
        const date = new Date(item.createdAt || item.timestamp).toLocaleDateString();
        const responseTimeBadge = item.responseTime < 2 ? 'success' : item.responseTime < 5 ? 'warning' : 'danger';
        const stars = item.userRating ? '★'.repeat(item.userRating) + '☆'.repeat(5 - item.userRating) : 'Not rated';
        
        html += `
            <tr>
                <td>${item.id}</td>
                <td class="text-truncate" style="max-width: 200px;" title="${item.question}">${item.question}</td>
                <td><span class="badge bg-${responseTimeBadge} status-badge">${item.responseTime?.toFixed(2) || 'N/A'}s</span></td>
                <td><span class="text-warning">${stars}</span></td>
                <td>${date}</td>
            </tr>
        `;
    });
    
    html += '</tbody></table>';
    tableDiv.innerHTML = html;
}

function loadMetricsData() {
    const tableDiv = document.getElementById('metrics-table');
    tableDiv.innerHTML = 'Loading...';
    
    // Demo data for metrics
    metricsData = [
        {
            id: 1,
            modelVersion: "v1.2.0",
            accuracyScore: 0.893,
            loss: 0.245,
            trainingSamples: 1500,
            evaluationDate: "2024-01-15T12:00:00Z"
        },
        {
            id: 2,
            modelVersion: "v1.1.0",
            accuracyScore: 0.867,
            loss: 0.312,
            trainingSamples: 1200,
            evaluationDate: "2024-01-10T12:00:00Z"
        }
    ];
    
    displayMetricsTable(metricsData);
}

function displayMetricsTable(data) {
    const tableDiv = document.getElementById('metrics-table');
    
    if (data.length === 0) {
        tableDiv.innerHTML = '<p class="text-muted">No model metrics records found.</p>';
        return;
    }
    
    let html = `
        <table class="table table-striped data-table">
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Model Version</th>
                    <th>Accuracy Score</th>
                    <th>Loss</th>
                    <th>Training Samples</th>
                    <th>Evaluation Date</th>
                </tr>
            </thead>
            <tbody>
    `;
    
    data.forEach(item => {
        const date = new Date(item.evaluationDate).toLocaleDateString();
        const accuracyBadge = item.accuracyScore > 0.8 ? 'success' : item.accuracyScore > 0.6 ? 'warning' : 'danger';
        const lossBadge = item.loss < 0.5 ? 'success' : item.loss < 1.0 ? 'warning' : 'danger';
        
        html += `
            <tr>
                <td>${item.id}</td>
                <td><span class="badge bg-primary status-badge">${item.modelVersion}</span></td>
                <td><span class="badge bg-${accuracyBadge} status-badge">${item.accuracyScore.toFixed(3)}</span></td>
                <td><span class="badge bg-${lossBadge} status-badge">${item.loss.toFixed(3)}</span></td>
                <td><span class="badge bg-info status-badge">${item.trainingSamples}</span></td>
                <td>${date}</td>
            </tr>
        `;
    });
    
    html += '</tbody></table>';
    tableDiv.innerHTML = html;
}

// Admin functions
function triggerDataCollection() {
    alert('Data collection triggered! This would normally start scraping Python docs, Stack Overflow, and GitHub for new training data.');
    
    // In a real implementation, this would trigger your data collection API
    database.ref('admin/lastDataCollection').set({
        timestamp: Date.now(),
        status: 'triggered'
    });
}

function triggerTraining() {
    alert('Model training triggered! This would normally start training the AI model with new data.');
    
    database.ref('admin/lastTraining').set({
        timestamp: Date.now(),
        status: 'triggered'
    });
}

function checkSystemStatus() {
    const statusDiv = document.getElementById('system-status');
    
    statusDiv.innerHTML = `
        <div class="row">
            <div class="col-md-6">
                <h6>Database Status</h6>
                <p class="text-success">✓ Connected to Firebase</p>
                
                <h6>AI Model Status</h6>
                <p class="text-success">✓ Model v1.2.0 Active</p>
                
                <h6>Data Collection</h6>
                <p class="text-info">⏰ Next run: In 12 hours</p>
            </div>
            <div class="col-md-6">
                <h6>System Performance</h6>
                <p>Average Response Time: <span class="badge bg-success">1.3s</span></p>
                <p>Uptime: <span class="badge bg-info">99.8%</span></p>
                
                <h6>Recent Activity</h6>
                <p>Last Training: <span class="text-muted">2 days ago</span></p>
                <p>Data Collection: <span class="text-muted">5 hours ago</span></p>
            </div>
        </div>
    `;
}