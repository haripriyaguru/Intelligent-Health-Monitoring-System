// Health Assistant Main JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips and popovers
    initializeBootstrapComponents();
    
    // Add any page-specific initialization
    initializePageSpecific();
});

// Initialize Bootstrap components
function initializeBootstrapComponents() {
    // Tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
}

// Page-specific initialization
function initializePageSpecific() {
    const currentPage = document.querySelector('title').textContent;
    
    if (currentPage.includes('Analysis')) {
        initializeAnalysisPage();
    } else if (currentPage.includes('Dashboard')) {
        initializeDashboard();
    }
}

// Initialize Analysis Page
function initializeAnalysisPage() {
    // File input preview
    setupFileInputPreview();
    
    // Form validation
    setupFormValidation();
}

// Initialize Dashboard
function initializeDashboard() {
    // Load dashboard data
    loadDashboardCharts();
}

// File Input Preview
function setupFileInputPreview() {
    const fileInputs = document.querySelectorAll('input[type="file"]');
    
    fileInputs.forEach(input => {
        input.addEventListener('change', function(e) {
            const fileName = this.files[0]?.name || 'No file chosen';
            const label = this.nextElementSibling?.textContent || 'Choose file';
            
            // Update UI to show file selected
            if (this.files[0]) {
                this.classList.add('is-valid');
            }
        });
    });
}

// Form Validation
function setupFormValidation() {
    const forms = document.querySelectorAll('form');
    
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!form.checkValidity()) {
                e.preventDefault();
                e.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });
}

// Load Dashboard Charts
function loadDashboardCharts() {
    // Can be extended to add chart.js or similar
    console.log('Dashboard charts initialized');
}

// Utility Functions

// Show Toast Notification
function showToast(message, type = 'info') {
    const toastHTML = `
        <div class="alert alert-${type} alert-dismissible fade show" role="alert">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;
    
    const container = document.querySelector('[role="main"]') || document.body;
    const toastDiv = document.createElement('div');
    toastDiv.innerHTML = toastHTML;
    toastDiv.className = 'position-fixed top-0 end-0 p-3';
    toastDiv.style.zIndex = 9999;
    
    container.insertBefore(toastDiv, container.firstChild);
    
    setTimeout(() => {
        toastDiv.remove();
    }, 5000);
}

// Format Date
function formatDate(date) {
    const options = { year: 'numeric', month: 'long', day: 'numeric', hour: '2-digit', minute: '2-digit' };
    return new Date(date).toLocaleDateString('en-US', options);
}

// Format Number
function formatNumber(num) {
    return new Intl.NumberFormat('en-US').format(num);
}

// API Request Helper
async function apiRequest(url, options = {}) {
    try {
        const response = await fetch(url, {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error('API Error:', error);
        showToast('An error occurred. Please try again.', 'danger');
        throw error;
    }
}

// Geolocation Helper
function getCurrentLocation() {
    return new Promise((resolve, reject) => {
        if (!navigator.geolocation) {
            reject('Geolocation is not supported');
            return;
        }
        
        navigator.geolocation.getCurrentPosition(
            position => resolve(position.coords),
            error => reject(error.message)
        );
    });
}

// Export Functions for use in HTML
window.showToast = showToast;
window.formatDate = formatDate;
window.apiRequest = apiRequest;
window.getCurrentLocation = getCurrentLocation;
