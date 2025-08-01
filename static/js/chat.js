// Chat functionality for PyLearnAI
class ChatInterface {
    constructor() {
        this.chatMessages = document.getElementById('chat-messages');
        this.questionForm = document.getElementById('question-form');
        this.questionInput = document.getElementById('question-input');
        this.submitBtn = document.getElementById('submit-btn');
        this.currentQueryId = null;
        this.isProcessing = false;
        
        this.init();
    }
    
    init() {
        // Form submission
        this.questionForm.addEventListener('submit', (e) => {
            e.preventDefault();
            this.handleQuestionSubmit();
        });
        
        // Quick question buttons
        document.querySelectorAll('.quick-question').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const question = e.target.dataset.question;
                this.questionInput.value = question;
                this.handleQuestionSubmit();
            });
        });
        
        // Enter key handling (Shift+Enter for new line, Enter to submit)
        this.questionInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.handleQuestionSubmit();
            }
        });
        
        // Rating modal handlers
        this.setupRatingModal();
        
        // Auto-resize textarea
        this.questionInput.addEventListener('input', this.autoResizeTextarea.bind(this));
    }
    
    async handleQuestionSubmit() {
        const question = this.questionInput.value.trim();
        
        if (!question || this.isProcessing) {
            return;
        }
        
        this.isProcessing = true;
        this.setLoadingState(true);
        
        // Add user message to chat
        this.addMessage(question, 'user');
        
        // Clear input
        this.questionInput.value = '';
        this.autoResizeTextarea();
        
        // Show typing indicator
        const typingId = this.showTypingIndicator();
        
        try {
            // Send question to server
            const formData = new FormData();
            formData.append('question', question);
            
            const response = await fetch('/ask', {
                method: 'POST',
                body: formData
            });
            
            const result = await response.json();
            
            // Remove typing indicator
            this.removeTypingIndicator(typingId);
            
            if (response.ok) {
                // Add AI response
                this.addMessage(result.response, 'ai', result.response_time);
                this.currentQueryId = result.query_id;
                
                // Show rating modal after a delay
                setTimeout(() => {
                    if (this.currentQueryId) {
                        const ratingModal = new bootstrap.Modal(document.getElementById('ratingModal'));
                        ratingModal.show();
                    }
                }, 2000);
                
            } else {
                this.addMessage(`Error: ${result.error}`, 'ai', 0, true);
            }
            
        } catch (error) {
            this.removeTypingIndicator(typingId);
            this.addMessage('Sorry, there was an error processing your request. Please try again.', 'ai', 0, true);
            console.error('Error:', error);
        } finally {
            this.isProcessing = false;
            this.setLoadingState(false);
        }
    }
    
    addMessage(content, sender, responseTime = null, isError = false) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}-message`;
        
        const avatar = document.createElement('div');
        avatar.className = 'message-avatar';
        avatar.innerHTML = sender === 'user' ? '<i data-feather="user"></i>' : '<i data-feather="cpu"></i>';
        
        const messageContent = document.createElement('div');
        messageContent.className = 'message-content';
        
        const messageBubble = document.createElement('div');
        messageBubble.className = 'message-bubble';
        
        if (isError) {
            messageBubble.classList.add('text-danger');
        }
        
        // Process content for code highlighting and formatting
        messageBubble.innerHTML = this.formatMessage(content);
        
        const messageTime = document.createElement('div');
        messageTime.className = 'message-time';
        
        let timeText = 'Just now';
        if (responseTime !== null) {
            timeText = `${responseTime}s`;
        }
        messageTime.textContent = timeText;
        
        messageContent.appendChild(messageBubble);
        messageContent.appendChild(messageTime);
        
        messageDiv.appendChild(avatar);
        messageDiv.appendChild(messageContent);
        
        this.chatMessages.appendChild(messageDiv);
        
        // Replace feather icons
        feather.replace();
        
        // Scroll to bottom
        this.scrollToBottom();
    }
    
    formatMessage(content) {
        // Convert markdown-style code blocks to HTML
        content = content.replace(/```python\n([\s\S]*?)\n```/g, (match, code) => {
            return `<pre><code class="language-python">${this.escapeHtml(code)}</code></pre>`;
        });
        
        content = content.replace(/```\n([\s\S]*?)\n```/g, (match, code) => {
            return `<pre><code>${this.escapeHtml(code)}</code></pre>`;
        });
        
        // Convert inline code
        content = content.replace(/`([^`]+)`/g, '<code>$1</code>');
        
        // Convert line breaks
        content = content.replace(/\n/g, '<br>');
        
        return content;
    }
    
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    showTypingIndicator() {
        const typingId = 'typing-' + Date.now();
        const typingDiv = document.createElement('div');
        typingDiv.className = 'message ai-message';
        typingDiv.id = typingId;
        
        typingDiv.innerHTML = `
            <div class="message-avatar">
                <i data-feather="cpu"></i>
            </div>
            <div class="message-content">
                <div class="message-bubble">
                    <div class="typing-indicator">
                        <span>Thinking</span>
                        <div class="typing-dots ms-2">
                            <div class="typing-dot"></div>
                            <div class="typing-dot"></div>
                            <div class="typing-dot"></div>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        this.chatMessages.appendChild(typingDiv);
        feather.replace();
        this.scrollToBottom();
        
        return typingId;
    }
    
    removeTypingIndicator(typingId) {
        const typingElement = document.getElementById(typingId);
        if (typingElement) {
            typingElement.remove();
        }
    }
    
    setLoadingState(loading) {
        if (loading) {
            this.submitBtn.disabled = true;
            this.submitBtn.classList.add('loading');
            this.questionInput.disabled = true;
        } else {
            this.submitBtn.disabled = false;
            this.submitBtn.classList.remove('loading');
            this.questionInput.disabled = false;
            this.questionInput.focus();
        }
    }
    
    scrollToBottom() {
        this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
    }
    
    autoResizeTextarea() {
        this.questionInput.style.height = 'auto';
        this.questionInput.style.height = Math.min(this.questionInput.scrollHeight, 200) + 'px';
    }
    
    setupRatingModal() {
        const ratingModal = document.getElementById('ratingModal');
        const ratingStars = document.querySelectorAll('.rating-star');
        const submitRatingBtn = document.getElementById('submit-rating');
        let selectedRating = 0;
        
        // Rating star interactions
        ratingStars.forEach((star, index) => {
            star.addEventListener('mouseenter', () => {
                this.highlightStars(index + 1);
            });
            
            star.addEventListener('mouseleave', () => {
                this.highlightStars(selectedRating);
            });
            
            star.addEventListener('click', () => {
                selectedRating = index + 1;
                this.highlightStars(selectedRating);
                submitRatingBtn.disabled = false;
            });
        });
        
        // Submit rating
        submitRatingBtn.addEventListener('click', async () => {
            if (selectedRating > 0 && this.currentQueryId) {
                try {
                    const formData = new FormData();
                    formData.append('query_id', this.currentQueryId);
                    formData.append('rating', selectedRating);
                    
                    await fetch('/rate', {
                        method: 'POST',
                        body: formData
                    });
                    
                    // Close modal
                    const modal = bootstrap.Modal.getInstance(ratingModal);
                    modal.hide();
                    
                    // Reset rating state
                    this.currentQueryId = null;
                    selectedRating = 0;
                    this.highlightStars(0);
                    submitRatingBtn.disabled = true;
                    
                } catch (error) {
                    console.error('Error submitting rating:', error);
                }
            }
        });
        
        // Reset modal when hidden
        ratingModal.addEventListener('hidden.bs.modal', () => {
            selectedRating = 0;
            this.highlightStars(0);
            submitRatingBtn.disabled = true;
        });
    }
    
    highlightStars(count) {
        const stars = document.querySelectorAll('.rating-star');
        stars.forEach((star, index) => {
            if (index < count) {
                star.classList.add('selected');
                star.querySelector('svg').style.fill = 'currentColor';
            } else {
                star.classList.remove('selected');
                star.querySelector('svg').style.fill = 'none';
            }
        });
    }
}

// Initialize chat interface when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new ChatInterface();
});

// Utility functions
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        // Show success feedback
        showToast('Copied to clipboard!', 'success');
    }).catch(() => {
        // Fallback for older browsers
        const textarea = document.createElement('textarea');
        textarea.value = text;
        document.body.appendChild(textarea);
        textarea.select();
        document.execCommand('copy');
        document.body.removeChild(textarea);
        showToast('Copied to clipboard!', 'success');
    });
}

function showToast(message, type = 'info') {
    // Create toast element
    const toastContainer = document.getElementById('toast-container') || createToastContainer();
    
    const toastEl = document.createElement('div');
    toastEl.className = `toast align-items-center text-white bg-${type} border-0`;
    toastEl.setAttribute('role', 'alert');
    
    toastEl.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">${message}</div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
    `;
    
    toastContainer.appendChild(toastEl);
    
    const toast = new bootstrap.Toast(toastEl);
    toast.show();
    
    // Remove element after hiding
    toastEl.addEventListener('hidden.bs.toast', () => {
        toastEl.remove();
    });
}

function createToastContainer() {
    const container = document.createElement('div');
    container.id = 'toast-container';
    container.className = 'toast-container position-fixed bottom-0 end-0 p-3';
    container.style.zIndex = '9999';
    document.body.appendChild(container);
    return container;
}

// Add copy button to code blocks
document.addEventListener('DOMContentLoaded', () => {
    // Add copy buttons to existing code blocks
    const codeBlocks = document.querySelectorAll('pre');
    codeBlocks.forEach(addCopyButton);
    
    // Observer for dynamically added code blocks
    const observer = new MutationObserver((mutations) => {
        mutations.forEach((mutation) => {
            mutation.addedNodes.forEach((node) => {
                if (node.nodeType === 1) { // Element node
                    const newCodeBlocks = node.querySelectorAll ? node.querySelectorAll('pre') : [];
                    newCodeBlocks.forEach(addCopyButton);
                }
            });
        });
    });
    
    observer.observe(document.body, {
        childList: true,
        subtree: true
    });
});

function addCopyButton(codeBlock) {
    // Skip if button already exists
    if (codeBlock.querySelector('.copy-btn')) {
        return;
    }
    
    const copyBtn = document.createElement('button');
    copyBtn.className = 'btn btn-sm btn-outline-secondary copy-btn position-absolute top-0 end-0 m-2';
    copyBtn.innerHTML = '<i data-feather="copy" style="width: 14px; height: 14px;"></i>';
    copyBtn.title = 'Copy code';
    
    codeBlock.style.position = 'relative';
    codeBlock.appendChild(copyBtn);
    
    copyBtn.addEventListener('click', () => {
        const code = codeBlock.querySelector('code')?.textContent || codeBlock.textContent;
        copyToClipboard(code);
        
        // Visual feedback
        copyBtn.innerHTML = '<i data-feather="check" style="width: 14px; height: 14px;"></i>';
        setTimeout(() => {
            copyBtn.innerHTML = '<i data-feather="copy" style="width: 14px; height: 14px;"></i>';
            feather.replace();
        }, 1000);
    });
    
    feather.replace();
}
