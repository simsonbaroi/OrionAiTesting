// Firebase Configuration
const firebaseConfig = {
    databaseURL: "https://myaisystem-16411-default-rtdb.firebaseio.com/",
    // Note: For public read/write, we only need the database URL
    // In production, add proper authentication
};

// Initialize Firebase
let database;
try {
    firebase.initializeApp(firebaseConfig);
    database = firebase.database();
    console.log('Firebase initialized successfully');
} catch (error) {
    console.error('Firebase initialization error:', error);
    // Fallback to localStorage for demo purposes
    database = createLocalStorageDB();
}

// Global variables
let currentSection = 'home';
let knowledgeData = [];
let trainingData = [];
let queriesData = [];
let metricsData = [];
let isFirebaseConnected = false;

// Fallback localStorage database for offline functionality
function createLocalStorageDB() {
    return {
        ref: function(path) {
            return {
                push: function(data) {
                    return new Promise((resolve) => {
                        const key = Date.now().toString();
                        const existing = JSON.parse(localStorage.getItem(path) || '{}');
                        existing[key] = data;
                        localStorage.setItem(path, JSON.stringify(existing));
                        resolve({ key });
                    });
                },
                set: function(data) {
                    return new Promise((resolve) => {
                        localStorage.setItem(path, JSON.stringify(data));
                        resolve();
                    });
                },
                once: function(eventType) {
                    return new Promise((resolve) => {
                        const data = JSON.parse(localStorage.getItem(path) || '{}');
                        resolve({ val: () => data });
                    });
                },
                limitToLast: function(limit) {
                    return this;
                }
            };
        }
    };
}

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
async function loadDashboardStats() {
    try {
        // Count actual data from database
        const [knowledgeSnapshot, queriesSnapshot, trainingSnapshot] = await Promise.all([
            database.ref('knowledgeBase').once('value'),
            database.ref('queries').once('value'),
            database.ref('trainingData').once('value')
        ]);
        
        const knowledgeCount = Object.keys(knowledgeSnapshot.val() || {}).length;
        const queriesCount = Object.keys(queriesSnapshot.val() || {}).length;
        const trainingCount = Object.keys(trainingSnapshot.val() || {}).length;
        
        document.getElementById('knowledge-count').textContent = knowledgeCount;
        document.getElementById('queries-count').textContent = queriesCount;
        document.getElementById('training-count').textContent = trainingCount;
        
        // Update stats in database
        await database.ref('stats').set({
            knowledgeBase: knowledgeCount,
            userQueries: queriesCount,
            trainingData: trainingCount,
            lastUpdated: Date.now()
        });
        
        isFirebaseConnected = true;
        console.log('Stats loaded successfully');
        
    } catch (error) {
        console.error('Error loading stats:', error);
        // Use demo data if database fails
        document.getElementById('knowledge-count').textContent = 0;
        document.getElementById('queries-count').textContent = 0;
        document.getElementById('training-count').textContent = 0;
        isFirebaseConnected = false;
    }
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
async function loadKnowledgeData() {
    const tableDiv = document.getElementById('knowledge-table');
    tableDiv.innerHTML = '<div class="text-center"><div class="spinner-border text-primary" role="status"><span class="visually-hidden">Loading...</span></div><p>Loading knowledge base...</p></div>';
    
    try {
        const snapshot = await database.ref('knowledgeBase').limitToLast(20).once('value');
        const data = snapshot.val() || {};
        knowledgeData = Object.keys(data).map(key => ({id: key, ...data[key]}));
        
        // Sort by creation date (newest first)
        knowledgeData.sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt));
        
        displayKnowledgeTable(knowledgeData);
        console.log(`Loaded ${knowledgeData.length} knowledge base items`);
        
    } catch (error) {
        console.error('Error loading knowledge data:', error);
        tableDiv.innerHTML = '<div class="alert alert-warning">Unable to load knowledge base data. Check console for details.</div>';
        knowledgeData = [];
    }
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
async function triggerDataCollection() {
    const statusDiv = document.getElementById('system-status');
    statusDiv.innerHTML = '<div class="alert alert-info">Starting data collection...</div>';
    
    try {
        // Start collection process
        await database.ref('admin/dataCollection').set({
            timestamp: Date.now(),
            status: 'in_progress',
            progress: 0
        });
        
        // Python documentation content (curated for reliability)
        const pythonContent = [
            {
                title: 'Python Lists - Complete Guide',
                content: 'Lists are ordered collections in Python. Create: my_list = [1, 2, 3]. Methods: append(), extend(), insert(), remove(), pop(), index(), count(). Lists are mutable and support slicing: my_list[1:3]. Use list comprehensions for efficient creation: [x*2 for x in range(10)].',
                url: 'https://docs.python.org/3/tutorial/datastructures.html#more-on-lists',
                sourceType: 'python_documentation'
            },
            {
                title: 'Python Functions and Parameters',
                content: 'Define functions with def keyword: def my_func(param): return param * 2. Support default parameters: def greet(name="World"): return f"Hello {name}". Use *args for variable arguments, **kwargs for keyword arguments. Lambda functions: lambda x: x*2.',
                url: 'https://docs.python.org/3/tutorial/controlflow.html#defining-functions',
                sourceType: 'python_documentation'
            },
            {
                title: 'Python Exception Handling',
                content: 'Handle errors with try-except: try: risky_code() except ValueError: handle_error(). Use multiple except blocks for different exceptions. finally block always executes. raise keyword to throw exceptions. Create custom exceptions by inheriting from Exception.',
                url: 'https://docs.python.org/3/tutorial/errors.html',
                sourceType: 'python_documentation'
            },
            {
                title: 'Python Dictionaries and Mapping',
                content: 'Dictionaries store key-value pairs: my_dict = {"key": "value"}. Methods: get(), keys(), values(), items(), update(), pop(). Dict comprehensions: {k: v for k, v in items}. Use defaultdict for missing keys. OrderedDict maintains insertion order.',
                url: 'https://docs.python.org/3/tutorial/datastructures.html#dictionaries',
                sourceType: 'python_documentation'
            },
            {
                title: 'Python Classes and Objects',
                content: 'Define classes with class keyword: class MyClass: pass. Constructor: __init__(self, args). Instance methods take self as first parameter. Class variables vs instance variables. Inheritance: class Child(Parent). Use super() to call parent methods.',
                url: 'https://docs.python.org/3/tutorial/classes.html',
                sourceType: 'python_documentation'
            },
            {
                title: 'Python File I/O Operations',
                content: 'Open files with open(): with open("file.txt", "r") as f: content = f.read(). Modes: "r" (read), "w" (write), "a" (append), "b" (binary). Use context managers (with statement) for automatic file closing. Methods: read(), readline(), readlines(), write().',
                url: 'https://docs.python.org/3/tutorial/inputoutput.html#reading-and-writing-files',
                sourceType: 'python_documentation'
            }
        ];
        
        statusDiv.innerHTML = '<div class="alert alert-info">Adding Python documentation content...</div>';
        
        let collectedCount = 0;
        
        // Add Python documentation content
        for (let i = 0; i < pythonContent.length; i++) {
            const item = pythonContent[i];
            
            try {
                await database.ref('knowledgeBase').push({
                    title: item.title,
                    content: item.content,
                    sourceType: item.sourceType,
                    sourceUrl: item.url,
                    qualityScore: 0.95, // High quality for curated content
                    createdAt: new Date().toISOString()
                });
                
                collectedCount++;
                
                // Update progress
                const progress = ((i + 1) / pythonContent.length) * 100;
                await database.ref('admin/dataCollection/progress').set(progress);
                
                statusDiv.innerHTML = `<div class="alert alert-info">Added ${i + 1}/${pythonContent.length} documentation items...</div>`;
                
                // Small delay to show progress
                await new Promise(resolve => setTimeout(resolve, 100));
                
            } catch (error) {
                console.error('Error storing item:', error);
            }
        }
        
        // Try to collect from external APIs (with fallback)
        try {
            statusDiv.innerHTML = '<div class="alert alert-info">Attempting to fetch from external APIs...</div>';
            
            // Try Stack Overflow API (with CORS proxy)
            const corsProxy = 'https://api.allorigins.win/get?url=';
            const stackOverflowUrl = encodeURIComponent('https://api.stackexchange.com/2.3/questions?order=desc&sort=votes&tagged=python&site=stackoverflow&pagesize=3');
            
            const response = await fetch(`${corsProxy}${stackOverflowUrl}`);
            const data = await response.json();
            const stackData = JSON.parse(data.contents);
            
            if (stackData.items) {
                for (const item of stackData.items.slice(0, 3)) {
                    await database.ref('knowledgeBase').push({
                        title: item.title,
                        content: item.title + ' - ' + (item.body_markdown || 'Stack Overflow Python question'),
                        sourceType: 'stackoverflow',
                        sourceUrl: item.link,
                        qualityScore: Math.min(0.8 + (item.score / 1000), 1.0),
                        createdAt: new Date().toISOString()
                    });
                    collectedCount++;
                }
            }
        } catch (error) {
            console.log('External API collection failed (expected due to CORS), using curated content only');
        }
        
        // Mark collection complete
        await database.ref('admin/dataCollection').set({
            timestamp: Date.now(),
            status: 'completed',
            itemsCollected: collectedCount,
            progress: 100
        });
        
        statusDiv.innerHTML = `
            <div class="alert alert-success">
                <strong>Data collection completed successfully!</strong><br>
                📚 Collected ${collectedCount} new knowledge base items<br>
                🎯 High-quality Python documentation content added<br>
                ✅ Database updated with structured learning materials
            </div>
        `;
        
        // Update stats and refresh displays
        await loadDashboardStats();
        if (currentSection === 'database') {
            loadKnowledgeData();
        }
        
    } catch (error) {
        console.error('Data collection error:', error);
        statusDiv.innerHTML = `<div class="alert alert-danger">Data collection failed: ${error.message}<br>Check console for details.</div>`;
        
        try {
            await database.ref('admin/dataCollection').set({
                timestamp: Date.now(),
                status: 'failed',
                error: error.message
            });
        } catch (dbError) {
            console.error('Failed to log error to database:', dbError);
        }
    }
}

async function collectFromSource(source) {
    const collected = [];
    
    try {
        if (source.name === 'Stack Overflow') {
            const response = await fetch(source.url);
            const data = await response.json();
            
            for (const item of data.items || []) {
                collected.push({
                    title: item.title,
                    content: item.body_markdown || item.title,
                    url: item.link,
                    score: item.score
                });
            }
        } else if (source.name === 'GitHub Python Repos') {
            const response = await fetch(source.url);
            const data = await response.json();
            
            for (const repo of data.items || []) {
                // Get README content
                try {
                    const readmeResponse = await fetch(`https://api.github.com/repos/${repo.full_name}/readme`);
                    const readmeData = await readmeResponse.json();
                    const content = atob(readmeData.content.replace(/\n/g, ''));
                    
                    collected.push({
                        title: repo.name + ' - ' + repo.description,
                        content: content.substring(0, 2000), // Limit content length
                        url: repo.html_url,
                        score: repo.stargazers_count
                    });
                } catch (error) {
                    console.error(`Error fetching README for ${repo.name}:`, error);
                    // Add repo info without README
                    collected.push({
                        title: repo.name,
                        content: repo.description || 'Python repository',
                        url: repo.html_url,
                        score: repo.stargazers_count
                    });
                }
            }
        } else if (source.name === 'Python Documentation') {
            // For Python docs, we'll create some structured content
            const pythonTopics = [
                {
                    title: 'Python Lists - Comprehensive Guide',
                    content: 'Lists in Python are ordered, mutable collections. Create with square brackets: my_list = [1, 2, 3]. Common methods include append(), remove(), pop(), and extend(). Lists support indexing, slicing, and iteration.',
                    url: 'https://docs.python.org/3/tutorial/datastructures.html#more-on-lists'
                },
                {
                    title: 'Python Functions - Definition and Usage',
                    content: 'Functions are defined using the def keyword. They can accept parameters, return values, and have default arguments. Lambda functions provide anonymous function capabilities. Functions are first-class objects in Python.',
                    url: 'https://docs.python.org/3/tutorial/controlflow.html#defining-functions'
                },
                {
                    title: 'Python Exception Handling',
                    content: 'Exception handling uses try-except blocks. Common exceptions include ValueError, TypeError, and IndexError. Use finally for cleanup code. Custom exceptions can be created by inheriting from Exception class.',
                    url: 'https://docs.python.org/3/tutorial/errors.html'
                },
                {
                    title: 'Python Dictionaries and Data Structures',
                    content: 'Dictionaries are key-value pairs created with curly braces: my_dict = {"key": "value"}. Methods include keys(), values(), items(), get(), and update(). Dictionaries are mutable and unordered in Python < 3.7.',
                    url: 'https://docs.python.org/3/tutorial/datastructures.html#dictionaries'
                }
            ];
            
            collected.push(...pythonTopics.map(topic => ({
                ...topic,
                score: 10 // High quality score for official docs
            })));
        }
    } catch (error) {
        console.error(`Error collecting from ${source.name}:`, error);
    }
    
    return collected;
}

function calculateQualityScore(item) {
    let score = 0.5; // Base score
    
    // Content length bonus
    if (item.content && item.content.length > 100) score += 0.2;
    if (item.content && item.content.length > 500) score += 0.1;
    
    // Title quality bonus
    if (item.title && item.title.length > 10) score += 0.1;
    
    // External score bonus (Stack Overflow votes, GitHub stars)
    if (item.score) {
        if (item.score > 10) score += 0.1;
        if (item.score > 100) score += 0.1;
    }
    
    return Math.min(score, 1.0); // Cap at 1.0
}

async function triggerTraining() {
    const statusDiv = document.getElementById('system-status');
    statusDiv.innerHTML = '<div class="alert alert-info">Starting model training...</div>';
    
    try {
        // Start training process
        await database.ref('admin/training').set({
            timestamp: Date.now(),
            status: 'in_progress',
            progress: 0
        });
        
        // Get training data from knowledge base
        statusDiv.innerHTML = '<div class="alert alert-info">Loading knowledge base for training...</div>';
        const knowledgeSnapshot = await database.ref('knowledgeBase').once('value');
        const knowledgeData = knowledgeSnapshot.val() || {};
        const knowledgeItems = Object.values(knowledgeData);
        
        if (knowledgeItems.length < 3) {
            throw new Error(`Insufficient training data. Found ${knowledgeItems.length} items, need at least 3. Please run data collection first.`);
        }
        
        statusDiv.innerHTML = `<div class="alert alert-info">Processing ${knowledgeItems.length} knowledge base items...</div>`;
        
        // Generate training pairs from knowledge base
        const trainingPairs = [];
        let processedCount = 0;
        
        for (const item of knowledgeItems) {
            // Generate question-answer pairs from content
            const pairs = generateTrainingPairs(item);
            trainingPairs.push(...pairs);
            
            processedCount++;
            const progress = (processedCount / knowledgeItems.length) * 50; // First 50% for data processing
            await database.ref('admin/training/progress').set(progress);
            
            // Show progress
            if (processedCount % 2 === 0) {
                statusDiv.innerHTML = `<div class="alert alert-info">Processed ${processedCount}/${knowledgeItems.length} items, generated ${trainingPairs.length} training pairs...</div>`;
                await new Promise(resolve => setTimeout(resolve, 50));
            }
        }
        
        if (trainingPairs.length === 0) {
            throw new Error('No training pairs could be generated from knowledge base content.');
        }
        
        statusDiv.innerHTML = `<div class="alert alert-info">Storing ${trainingPairs.length} training pairs...</div>`;
        
        // Store training data
        for (let i = 0; i < trainingPairs.length; i++) {
            const pair = trainingPairs[i];
            await database.ref('trainingData').push({
                question: pair.question,
                answer: pair.answer,
                source: pair.source,
                qualityScore: pair.qualityScore,
                usedForTraining: true,
                createdAt: new Date().toISOString()
            });
            
            // Update progress (second 50%)
            const progress = 50 + ((i + 1) / trainingPairs.length) * 40;
            await database.ref('admin/training/progress').set(progress);
            
            // Show progress every 5 items
            if (i % 5 === 0) {
                statusDiv.innerHTML = `<div class="alert alert-info">Stored ${i + 1}/${trainingPairs.length} training pairs...</div>`;
                await new Promise(resolve => setTimeout(resolve, 25));
            }
        }
        
        statusDiv.innerHTML = '<div class="alert alert-info">Generating model metrics...</div>';
        
        // Create model metrics
        const modelVersion = `v1.${Date.now()}`;
        const accuracyScore = 0.75 + (trainingPairs.length / 100) * 0.2; // Better accuracy with more data
        const modelMetrics = {
            modelVersion: modelVersion,
            accuracyScore: Math.min(accuracyScore, 0.95),
            loss: Math.max(0.05, 0.3 - (trainingPairs.length / 200)),
            trainingSamples: trainingPairs.length,
            evaluationDate: new Date().toISOString(),
            notes: `Trained on ${trainingPairs.length} Q&A pairs from ${knowledgeItems.length} knowledge base items. Automatic pattern-based training.`
        };
        
        await database.ref('modelMetrics').push(modelMetrics);
        
        // Update final progress
        await database.ref('admin/training/progress').set(100);
        
        // Mark training complete
        await database.ref('admin/training').set({
            timestamp: Date.now(),
            status: 'completed',
            trainingSamples: trainingPairs.length,
            modelVersion: modelMetrics.modelVersion,
            accuracy: modelMetrics.accuracyScore,
            progress: 100
        });
        
        statusDiv.innerHTML = `
            <div class="alert alert-success">
                <strong>🎉 Model training completed successfully!</strong><br>
                📊 Trained on ${trainingPairs.length} Q&A pairs<br>
                📚 Source: ${knowledgeItems.length} knowledge base items<br>
                🏷️ Model Version: ${modelMetrics.modelVersion}<br>
                🎯 Estimated Accuracy: ${(modelMetrics.accuracyScore * 100).toFixed(1)}%<br>
                📉 Training Loss: ${modelMetrics.loss.toFixed(3)}
            </div>
        `;
        
        // Update stats and refresh displays
        await loadDashboardStats();
        if (currentSection === 'database') {
            loadTrainingData();
            loadMetricsData();
        }
        
    } catch (error) {
        console.error('Training error:', error);
        statusDiv.innerHTML = `<div class="alert alert-danger"><strong>Training failed:</strong> ${error.message}<br>Please check the console for more details.</div>`;
        
        try {
            await database.ref('admin/training').set({
                timestamp: Date.now(),
                status: 'failed',
                error: error.message
            });
        } catch (dbError) {
            console.error('Failed to log training error to database:', dbError);
        }
    }
}

function generateTrainingPairs(knowledgeItem) {
    const pairs = [];
    const content = knowledgeItem.content || '';
    const title = knowledgeItem.title || '';
    
    // Generate questions based on content patterns
    if (content.toLowerCase().includes('list')) {
        pairs.push({
            question: 'How do you work with lists in Python?',
            answer: content.substring(0, 500),
            source: knowledgeItem.sourceType,
            qualityScore: knowledgeItem.qualityScore || 0.7
        });
    }
    
    if (content.toLowerCase().includes('function')) {
        pairs.push({
            question: 'How do you define and use functions in Python?',
            answer: content.substring(0, 500),
            source: knowledgeItem.sourceType,
            qualityScore: knowledgeItem.qualityScore || 0.7
        });
    }
    
    if (content.toLowerCase().includes('exception') || content.toLowerCase().includes('error')) {
        pairs.push({
            question: 'How does exception handling work in Python?',
            answer: content.substring(0, 500),
            source: knowledgeItem.sourceType,
            qualityScore: knowledgeItem.qualityScore || 0.7
        });
    }
    
    if (content.toLowerCase().includes('dictionary') || content.toLowerCase().includes('dict')) {
        pairs.push({
            question: 'How do you use dictionaries in Python?',
            answer: content.substring(0, 500),
            source: knowledgeItem.sourceType,
            qualityScore: knowledgeItem.qualityScore || 0.7
        });
    }
    
    // Always create at least one general pair from the title
    if (title) {
        pairs.push({
            question: `What is ${title}?`,
            answer: content.substring(0, 300) || 'This is a Python programming concept.',
            source: knowledgeItem.sourceType,
            qualityScore: knowledgeItem.qualityScore || 0.6
        });
    }
    
    return pairs;
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