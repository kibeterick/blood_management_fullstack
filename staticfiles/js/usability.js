// Usability Enhancements for Blood Management System

// 1. Loading Indicators
function showLoading(message = 'Loading...') {
    const loadingHTML = `
        <div id="loadingOverlay" style="position: fixed; top: 0; left: 0; width: 100%; height: 100%; 
             background: rgba(0,0,0,0.5); z-index: 9999; display: flex; align-items: center; justify-content: center;">
            <div style="background: white; padding: 30px; border-radius: 10px; text-align: center;">
                <div class="spinner-border text-danger" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
                <p class="mt-3 mb-0">${message}</p>
            </div>
        </div>
    `;
    document.body.insertAdjacentHTML('beforeend', loadingHTML);
}

function hideLoading() {
    const overlay = document.getElementById('loadingOverlay');
    if (overlay) overlay.remove();
}

// 2. Success/Error Toast Messages
function showToast(message, type = 'success') {
    const bgColor = type === 'success' ? 'bg-success' : type === 'error' ? 'bg-danger' : 'bg-info';
    const icon = type === 'success' ? '✓' : type === 'error' ? '✗' : 'ℹ';
    
    const toastHTML = `
        <div class="toast align-items-center text-white ${bgColor} border-0" role="alert" 
             style="position: fixed; top: 20px; right: 20px; z-index: 10000; min-width: 300px;">
            <div class="d-flex">
                <div class="toast-body">
                    <strong>${icon}</strong> ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        </div>
    `;
    
    document.body.insertAdjacentHTML('beforeend', toastHTML);
    const toastElement = document.querySelector('.toast:last-child');
    const toast = new bootstrap.Toast(toastElement, { delay: 3000 });
    toast.show();
    
    setTimeout(() => toastElement.remove(), 4000);
}

// 3. Confirm Dialogs with Better UX
function confirmAction(message, onConfirm) {
    const modalHTML = `
        <div class="modal fade" id="confirmModal" tabindex="-1">
            <div class="modal-dialog modal-dialog-centered">
                <div class="modal-content">
                    <div class="modal-header bg-danger text-white">
                        <h5 class="modal-title">Confirm Action</h5>
                        <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <p class="mb-0">${message}</p>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                        <button type="button" class="btn btn-danger" id="confirmBtn">Confirm</button>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    document.body.insertAdjacentHTML('beforeend', modalHTML);
    const modal = new bootstrap.Modal(document.getElementById('confirmModal'));
    modal.show();
    
    document.getElementById('confirmBtn').onclick = () => {
        modal.hide();
        onConfirm();
        setTimeout(() => document.getElementById('confirmModal').remove(), 500);
    };
    
    document.getElementById('confirmModal').addEventListener('hidden.bs.modal', () => {
        setTimeout(() => document.getElementById('confirmModal').remove(), 500);
    });
}

// 4. Form Validation with Better Messages
function validateForm(formId) {
    const form = document.getElementById(formId);
    if (!form) return true;
    
    const requiredFields = form.querySelectorAll('[required]');
    let isValid = true;
    
    requiredFields.forEach(field => {
        if (!field.value.trim()) {
            isValid = false;
            field.classList.add('is-invalid');
            
            let feedback = field.nextElementSibling;
            if (!feedback || !feedback.classList.contains('invalid-feedback')) {
                feedback = document.createElement('div');
                feedback.className = 'invalid-feedback';
                field.parentNode.insertBefore(feedback, field.nextSibling);
            }
            feedback.textContent = `Please enter ${field.placeholder || field.name}`;
        } else {
            field.classList.remove('is-invalid');
        }
    });
    
    return isValid;
}

// 5. Tooltips Initialization
function initTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// 6. Search/Filter Enhancement
function enhanceSearch(inputId, tableId) {
    const input = document.getElementById(inputId);
    const table = document.getElementById(tableId);
    
    if (!input || !table) return;
    
    input.addEventListener('keyup', function() {
        const filter = this.value.toLowerCase();
        const rows = table.getElementsByTagName('tr');
        
        for (let i = 1; i < rows.length; i++) {
            const row = rows[i];
            const text = row.textContent.toLowerCase();
            row.style.display = text.includes(filter) ? '' : 'none';
        }
    });
}

// 7. Auto-save Draft (for forms)
function enableAutoSave(formId, storageKey) {
    const form = document.getElementById(formId);
    if (!form) return;
    
    // Load saved data
    const savedData = localStorage.getItem(storageKey);
    if (savedData) {
        const data = JSON.parse(savedData);
        Object.keys(data).forEach(key => {
            const field = form.elements[key];
            if (field) field.value = data[key];
        });
        showToast('Draft restored', 'info');
    }
    
    // Save on change
    form.addEventListener('change', () => {
        const formData = new FormData(form);
        const data = {};
        formData.forEach((value, key) => data[key] = value);
        localStorage.setItem(storageKey, JSON.stringify(data));
    });
    
    // Clear on submit
    form.addEventListener('submit', () => {
        localStorage.removeItem(storageKey);
    });
}

// 8. Keyboard Shortcuts
function initKeyboardShortcuts() {
    document.addEventListener('keydown', (e) => {
        // Ctrl/Cmd + K for search
        if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
            e.preventDefault();
            const searchInput = document.querySelector('input[type="search"], input[placeholder*="Search"]');
            if (searchInput) searchInput.focus();
        }
        
        // Escape to close modals
        if (e.key === 'Escape') {
            const modals = document.querySelectorAll('.modal.show');
            modals.forEach(modal => {
                const bsModal = bootstrap.Modal.getInstance(modal);
                if (bsModal) bsModal.hide();
            });
        }
    });
}

// 9. Empty State Messages
function showEmptyState(containerId, message, actionText, actionUrl) {
    const container = document.getElementById(containerId);
    if (!container) return;
    
    const emptyHTML = `
        <div class="text-center py-5">
            <i class="bi bi-inbox" style="font-size: 4rem; color: #ccc;"></i>
            <h4 class="mt-3 text-muted">${message}</h4>
            ${actionText ? `<a href="${actionUrl}" class="btn btn-danger mt-3">${actionText}</a>` : ''}
        </div>
    `;
    
    container.innerHTML = emptyHTML;
}

// 10. Progress Indicators for Multi-step Forms
function updateProgress(currentStep, totalSteps) {
    const percentage = (currentStep / totalSteps) * 100;
    const progressHTML = `
        <div class="progress mb-4" style="height: 25px;">
            <div class="progress-bar bg-danger" role="progressbar" 
                 style="width: ${percentage}%" aria-valuenow="${percentage}" 
                 aria-valuemin="0" aria-valuemax="100">
                Step ${currentStep} of ${totalSteps}
            </div>
        </div>
    `;
    
    const container = document.querySelector('.progress-container');
    if (container) container.innerHTML = progressHTML;
}

// 11. Password Toggle (Show/Hide)
function initPasswordToggles() {
    // Find all password fields
    const passwordFields = document.querySelectorAll('input[type="password"]');
    
    passwordFields.forEach(field => {
        // Skip if already has toggle
        if (field.parentElement.querySelector('.password-toggle')) return;
        
        // Create wrapper if field is not already wrapped
        if (!field.parentElement.classList.contains('password-wrapper')) {
            const wrapper = document.createElement('div');
            wrapper.className = 'password-wrapper position-relative';
            field.parentNode.insertBefore(wrapper, field);
            wrapper.appendChild(field);
        }
        
        // Create toggle button
        const toggleBtn = document.createElement('button');
        toggleBtn.type = 'button';
        toggleBtn.className = 'password-toggle btn btn-sm position-absolute';
        toggleBtn.innerHTML = '<i class="bi bi-eye"></i>';
        toggleBtn.style.cssText = 'right: 10px; top: 50%; transform: translateY(-50%); border: none; background: transparent; color: #6c757d; z-index: 10;';
        toggleBtn.setAttribute('data-bs-toggle', 'tooltip');
        toggleBtn.setAttribute('data-bs-placement', 'top');
        toggleBtn.setAttribute('title', 'Show password');
        
        // Add toggle functionality
        toggleBtn.addEventListener('click', function() {
            const type = field.getAttribute('type');
            if (type === 'password') {
                field.setAttribute('type', 'text');
                this.innerHTML = '<i class="bi bi-eye-slash"></i>';
                this.setAttribute('title', 'Hide password');
            } else {
                field.setAttribute('type', 'password');
                this.innerHTML = '<i class="bi bi-eye"></i>';
                this.setAttribute('title', 'Show password');
            }
            
            // Reinitialize tooltip
            const tooltip = bootstrap.Tooltip.getInstance(this);
            if (tooltip) {
                tooltip.dispose();
            }
            new bootstrap.Tooltip(this);
        });
        
        // Add padding to input to make room for button
        field.style.paddingRight = '45px';
        
        // Insert toggle button
        field.parentElement.appendChild(toggleBtn);
        
        // Initialize tooltip
        new bootstrap.Tooltip(toggleBtn);
    });
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    initTooltips();
    initKeyboardShortcuts();
    initPasswordToggles();
    
    // Add helpful hints
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!validateForm(form.id)) {
                e.preventDefault();
                showToast('Please fill in all required fields', 'error');
            } else {
                showLoading('Processing...');
            }
        });
    });
    
    // Enhance delete buttons
    const deleteButtons = document.querySelectorAll('[data-action="delete"]');
    deleteButtons.forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            const itemName = this.dataset.itemName || 'this item';
            confirmAction(
                `Are you sure you want to delete ${itemName}? This action cannot be undone.`,
                () => {
                    showLoading('Deleting...');
                    window.location.href = this.href;
                }
            );
        });
    });
});

// Export functions for use in templates
window.bloodSystem = {
    showLoading,
    hideLoading,
    showToast,
    confirmAction,
    validateForm,
    enhanceSearch,
    enableAutoSave,
    showEmptyState,
    updateProgress,
    initPasswordToggles
};
