/**
 * HoloVoice - Frontend JavaScript
 * Handles file upload, WebSocket communication, and UI interactions
 */

class HoloVoiceApp {
    constructor() {
        this.currentJobId = null;
        this.websocket = null;
        this.init();
    }

    init() {
        this.bindEvents();
        this.setupFileValidation();
    }

    bindEvents() {
        // File upload form
        const uploadForm = document.getElementById('uploadForm');
        uploadForm.addEventListener('submit', (e) => this.handleFileUpload(e));

        // Download button
        const downloadBtn = document.getElementById('downloadBtn');
        downloadBtn.addEventListener('click', () => this.downloadResult());

        // File input change
        const fileInput = document.getElementById('fileInput');
        fileInput.addEventListener('change', (e) => this.validateFile(e.target));
    }

    setupFileValidation() {
        const fileInput = document.getElementById('fileInput');
        const uploadBtn = document.getElementById('uploadBtn');

        fileInput.addEventListener('change', function() {
            if (this.files.length > 0) {
                uploadBtn.disabled = false;
            } else {
                uploadBtn.disabled = true;
            }
        });
    }

    validateFile(input) {
        const file = input.files[0];
        if (!file) return;

        const allowedTypes = ['image/png', 'image/jpeg', 'image/jpg', 'video/avi', 'video/mp4'];
        const maxSize = 50 * 1024 * 1024; // 50MB

        if (!allowedTypes.includes(file.type)) {
            this.showError('Please select a valid file type (PNG, JPG, AVI, MP4)');
            input.value = '';
            return false;
        }

        if (file.size > maxSize) {
            this.showError('File size must be less than 50MB');
            input.value = '';
            return false;
        }

        this.hideError();
        return true;
    }

    async handleFileUpload(event) {
        event.preventDefault();

        const fileInput = document.getElementById('fileInput');
        const file = fileInput.files[0];

        if (!file || !this.validateFile(fileInput)) {
            return;
        }

        // Prepare form data
        const formData = new FormData();
        formData.append('file', file);

        // Show processing status
        this.showProcessing();

        try {
            // Upload file
            const response = await fetch('/upload', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                throw new Error(`Upload failed: ${response.statusText}`);
            }

            const result = await response.json();
            this.currentJobId = result.job_id;

            // Start WebSocket monitoring
            this.startWebSocketMonitoring(result.job_id);

        } catch (error) {
            console.error('Upload error:', error);
            this.showError('Failed to upload file. Please try again.');
            this.hideProcessing();
        }
    }

    startWebSocketMonitoring(jobId) {
        try {
            // Close existing WebSocket if any
            if (this.websocket) {
                this.websocket.close();
            }

            // Create new WebSocket connection
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            const wsUrl = `${protocol}//${window.location.host}/ws/${jobId}`;

            this.websocket = new WebSocket(wsUrl);

            this.websocket.onopen = () => {
                console.log('WebSocket connected');
            };

            this.websocket.onmessage = (event) => {
                const status = JSON.parse(event.data);
                this.updateProcessingStatus(status);
            };

            this.websocket.onerror = (error) => {
                console.error('WebSocket error:', error);
                this.showError('Connection lost. Please refresh the page.');
            };

            this.websocket.onclose = () => {
                console.log('WebSocket closed');
            };

        } catch (error) {
            console.error('Failed to create WebSocket:', error);
            this.showError('Real-time updates not available. Please check status manually.');
        }
    }

    updateProcessingStatus(status) {
        const progressText = document.getElementById('progressText');

        switch (status.status) {
            case 'processing':
                progressText.textContent = `Processing... ${status.progress || 0}%`;
                break;

            case 'completed':
                this.hideProcessing();
                this.showResult(status.output_file);
                this.showSuccess('Hologram generated successfully!');
                break;

            case 'failed':
                this.hideProcessing();
                this.showError(status.error || 'Processing failed');
                break;

            default:
                progressText.textContent = status.status || 'Unknown status';
        }
    }

    showProcessing() {
        document.getElementById('processingStatus').style.display = 'block';
        document.getElementById('resultsSection').style.display = 'none';
        document.getElementById('errorSection').style.display = 'none';
        document.getElementById('uploadBtn').disabled = true;
    }

    hideProcessing() {
        document.getElementById('processingStatus').style.display = 'none';
        document.getElementById('uploadBtn').disabled = false;
    }

    showResult(outputFile) {
        const resultContainer = document.getElementById('resultContainer');
        const resultsSection = document.getElementById('resultsSection');

        // Determine file type and create appropriate element
        const isVideo = outputFile.toLowerCase().endsWith('.mp4') || outputFile.toLowerCase().endsWith('.avi');

        if (isVideo) {
            resultContainer.innerHTML = `
                <video controls class="hologram-result">
                    <source src="/outputs/${outputFile.split('/').pop()}" type="video/mp4">
                    Your browser does not support video playback.
                </video>
            `;
        } else {
            resultContainer.innerHTML = `
                <img src="/outputs/${outputFile.split('/').pop()}" alt="Generated Hologram" class="hologram-result hologram-effect">
            `;
        }

        resultsSection.style.display = 'block';
    }

    downloadResult() {
        if (!this.currentJobId) return;

        window.open(`/download/${this.currentJobId}`, '_blank');
    }

    showError(message) {
        const errorSection = document.getElementById('errorSection');
        const errorMessage = document.getElementById('errorMessage');

        errorMessage.textContent = message;
        errorSection.style.display = 'block';
        errorSection.classList.add('error-animation');

        setTimeout(() => {
            errorSection.classList.remove('error-animation');
        }, 500);
    }

    hideError() {
        document.getElementById('errorSection').style.display = 'none';
    }

    showSuccess(message) {
        // Create a temporary success alert
        const alert = document.createElement('div');
        alert.className = 'alert alert-success alert-dismissible fade show position-fixed success-animation';
        alert.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
        alert.innerHTML = `
            <i class="fas fa-check-circle"></i> ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;

        document.body.appendChild(alert);

        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (alert.parentNode) {
                alert.remove();
            }
        }, 5000);
    }
}

// Initialize the app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.holoVoiceApp = new HoloVoiceApp();
});

// Add some visual enhancements
document.addEventListener('DOMContentLoaded', () => {
    // Add loading animation to progress text
    const progressText = document.getElementById('progressText');
    if (progressText) {
        progressText.classList.add('loading-dots');
    }

    // Add smooth scrolling
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth'
                });
            }
        });
    });
});