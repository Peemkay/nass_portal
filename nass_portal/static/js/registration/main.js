// Registration Form Handler
class RegistrationForm {
    constructor() {
        this.form = document.querySelector('.registration-form');
        this.steps = document.querySelectorAll('.progress-step');
        this.currentStep = 0;
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.setupFormValidation();
        this.setupFileUploads();
    }

    setupEventListeners() {
        // Navigation buttons
        document.querySelectorAll('.btn-next').forEach(btn => {
            btn.addEventListener('click', () => this.handleNext());
        });

        document.querySelectorAll('.btn-prev').forEach(btn => {
            btn.addEventListener('click', () => this.handlePrevious());
        });

        // Form submission
        this.form?.addEventListener('submit', (e) => this.handleSubmit(e));
    }

    setupFormValidation() {
        // Custom form validation
        const inputs = document.querySelectorAll('.form-control, .form-select');
        inputs.forEach(input => {
            input.addEventListener('blur', () => this.validateField(input));
            input.addEventListener('input', () => this.validateField(input));
        });
    }

    setupFileUploads() {
        // File upload preview and validation
        const fileInputs = document.querySelectorAll('input[type="file"]');
        fileInputs.forEach(input => {
            input.addEventListener('change', (e) => this.handleFileUpload(e));
        });
    }

    validateField(field) {
        const value = field.value.trim();
        const isRequired = field.hasAttribute('required');
        const type = field.type;
        let isValid = true;
        let errorMessage = '';

        // Remove existing validation classes
        field.classList.remove('is-valid', 'is-invalid');

        // Basic validation
        if (isRequired && !value) {
            isValid = false;
            errorMessage = 'This field is required';
        } else {
            // Type-specific validation
            switch (type) {
                case 'email':
                    isValid = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value);
                    errorMessage = 'Please enter a valid email address';
                    break;
                case 'tel':
                    isValid = /^\+?[\d\s-]{10,}$/.test(value);
                    errorMessage = 'Please enter a valid phone number';
                    break;
                case 'file':
                    isValid = this.validateFileUpload(field);
                    errorMessage = 'Please upload a valid file';
                    break;
            }
        }

        // Update UI
        field.classList.add(isValid ? 'is-valid' : 'is-invalid');
        
        // Update or create feedback element
        let feedback = field.nextElementSibling;
        if (!feedback || !feedback.classList.contains('invalid-feedback')) {
            feedback = document.createElement('div');
            feedback.className = 'invalid-feedback';
            field.parentNode.insertBefore(feedback, field.nextSibling);
        }
        feedback.textContent = isValid ? '' : errorMessage;

        return isValid;
    }

    validateFileUpload(fileInput) {
        if (!fileInput.files || !fileInput.files[0]) return false;

        const file = fileInput.files[0];
        const maxSize = fileInput.dataset.maxSize || 5 * 1024 * 1024; // Default 5MB
        const allowedTypes = fileInput.accept.split(',').map(type => type.trim());

        if (file.size > maxSize) {
            fileInput.nextElementSibling.textContent = 'File is too large';
            return false;
        }

        if (!allowedTypes.some(type => {
            if (type.startsWith('.')) {
                return file.name.toLowerCase().endsWith(type.toLowerCase());
            }
            return file.type.match(new RegExp(type.replace('*', '.*')));
        })) {
            fileInput.nextElementSibling.textContent = 'Invalid file type';
            return false;
        }

        return true;
    }

    handleFileUpload(event) {
        const input = event.target;
        const preview = document.querySelector(`#${input.id}-preview`);
        
        if (preview && input.files && input.files[0]) {
            const reader = new FileReader();
            
            reader.onload = (e) => {
                preview.src = e.target.result;
            };
            
            reader.readAsDataURL(input.files[0]);
        }
    }

    async handleSubmit(event) {
        event.preventDefault();
        
        if (!this.validateStep()) return;

        const formData = new FormData(this.form);
        
        try {
            this.setLoading(true);
            
            const response = await fetch(this.form.action, {
                method: 'POST',
                body: formData
            });

            if (!response.ok) throw new Error('Submission failed');

            const data = await response.json();
            
            if (data.success) {
                this.handleSuccess(data);
            } else {
                this.handleError(data.error);
            }
        } catch (error) {
            this.handleError(error);
        } finally {
            this.setLoading(false);
        }
    }

    setLoading(isLoading) {
        const submitBtn = this.form.querySelector('button[type="submit"]');
        if (isLoading) {
            submitBtn.classList.add('loading');
            submitBtn.disabled = true;
        } else {
            submitBtn.classList.remove('loading');
            submitBtn.disabled = false;
        }
    }

    handleSuccess(data) {
        // Show success message or redirect
        window.location.href = data.redirect || '/registration/success';
    }

    handleError(error) {
        // Show error message
        const errorElement = document.createElement('div');
        errorElement.className = 'alert alert-danger alert-dismissible fade show';
        errorElement.innerHTML = `
            <strong>Error!</strong> ${error.message || 'An error occurred during submission.'}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;
        
        // Insert at the top of the form
        this.form.insertBefore(errorElement, this.form.firstChild);
        
        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            errorElement.remove();
        }, 5000);
    }

    handleNext() {
        if (this.validateStep()) {
            this.currentStep++;
            this.updateUI();
        }
    }

    handlePrevious() {
        if (this.currentStep > 0) {
            this.currentStep--;
            this.updateUI();
        }
    }

    validateStep() {
        const currentFields = this.getCurrentStepFields();
        return currentFields.every(field => this.validateField(field));
    }

    getCurrentStepFields() {
        const stepContainer = this.form.querySelector(`.step-${this.currentStep}`);
        return stepContainer ? Array.from(stepContainer.querySelectorAll('.form-control, .form-select')) : [];
    }

    updateUI() {
        // Update progress steps
        this.steps.forEach((step, index) => {
            step.classList.toggle('active', index === this.currentStep);
            step.classList.toggle('completed', index < this.currentStep);
        });

        // Update form sections visibility
        document.querySelectorAll('.step-content').forEach((content, index) => {
            content.style.display = index === this.currentStep ? 'block' : 'none';
        });

        // Update navigation buttons
        const prevBtn = document.querySelector('.btn-prev');
        const nextBtn = document.querySelector('.btn-next');
        const submitBtn = document.querySelector('.btn-submit');

        if (prevBtn) prevBtn.style.display = this.currentStep === 0 ? 'none' : 'block';
        if (nextBtn) nextBtn.style.display = this.currentStep === this.steps.length - 1 ? 'none' : 'block';
        if (submitBtn) submitBtn.style.display = this.currentStep === this.steps.length - 1 ? 'block' : 'none';
    }
}

// Initialize the form handler when the DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new RegistrationForm();
});
