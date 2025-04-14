/**
 * Modern Registration Form JavaScript
 * Handles form validation, animations, and interactive elements
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize all components
    initFormValidation();
    initFileUploads();
    initProgressSteps();
    initAnimations();
    initCalculations();

    // Form validation with enhanced feedback
    function initFormValidation() {
        const forms = document.querySelectorAll('.needs-validation');

        // Bootstrap's built-in validation
        Array.from(forms).forEach(form => {
            form.addEventListener('submit', event => {
                if (!form.checkValidity()) {
                    event.preventDefault();
                    event.stopPropagation();
                }
                form.classList.add('was-validated');

                // Scroll to first invalid field
                const invalidField = form.querySelector(':invalid');
                if (invalidField) {
                    invalidField.focus();
                    invalidField.scrollIntoView({
                        behavior: 'smooth',
                        block: 'center'
                    });
                }
            }, false);
        });

        // Real-time validation feedback
        const inputs = document.querySelectorAll('.form-control, .form-select');
        inputs.forEach(input => {
            // Validate on blur
            input.addEventListener('blur', () => {
                validateField(input);
            });

            // Validate on input after first blur
            input.addEventListener('input', () => {
                if (input.classList.contains('is-invalid') || input.classList.contains('is-valid')) {
                    validateField(input);
                }
            });
        });
    }

    // Validate individual field
    function validateField(field) {
        // Skip validation if field is disabled or readonly
        if (field.disabled || field.readOnly) return;

        const isValid = field.checkValidity();

        if (isValid) {
            field.classList.remove('is-invalid');
            field.classList.add('is-valid');
        } else {
            field.classList.remove('is-valid');
            field.classList.add('is-invalid');
        }

        // Special validation for specific field types
        if (field.type === 'file' && field.files.length > 0) {
            validateFileUpload(field);
        }

        // Special validation for date fields
        if (field.type === 'date') {
            validateDateField(field);
        }
    }

    // File upload handling
    function initFileUploads() {
        const fileInputs = document.querySelectorAll('input[type="file"]');

        fileInputs.forEach(input => {
            input.addEventListener('change', (e) => {
                const file = e.target.files[0];
                if (!file) return;

                // Find preview element (assumes it's in the same parent container)
                const previewContainer = input.closest('.card-body').querySelector('.photo-preview');
                const previewImage = previewContainer ? previewContainer.querySelector('img') : null;

                if (previewImage) {
                    const reader = new FileReader();
                    reader.onload = function(e) {
                        previewImage.src = e.target.result;
                        previewImage.style.display = 'block';

                        // Add loaded class for animation
                        previewContainer.classList.add('loaded');
                    };
                    reader.readAsDataURL(file);
                }

                validateFileUpload(input);
            });
        });
    }

    // Validate file uploads
    function validateFileUpload(field) {
        const file = field.files[0];
        if (!file) return true;

        const maxSize = 2 * 1024 * 1024; // 2MB
        const allowedTypes = ['image/jpeg', 'image/png', 'image/jpg'];

        // Check file size
        if (file.size > maxSize) {
            field.setCustomValidity('File size must be less than 2MB');
            field.classList.add('is-invalid');
            return false;
        }

        // Check file type
        if (!allowedTypes.includes(file.type)) {
            field.setCustomValidity('Only JPG, JPEG, and PNG files are allowed');
            field.classList.add('is-invalid');
            return false;
        }

        field.setCustomValidity('');
        return true;
    }

    // Validate date fields
    function validateDateField(field) {
        const value = field.value;
        if (!value) return;

        const date = new Date(value);
        const today = new Date();

        // Check if date is in the future
        if (field.id === 'date_of_birth' && date > today) {
            field.setCustomValidity('Date of birth cannot be in the future');
            return;
        }

        // Check if date of commission is in the future
        if (field.id === 'date_of_commission' && date > today) {
            field.setCustomValidity('Date of commission cannot be in the future');
            return;
        }

        field.setCustomValidity('');
    }

    // Progress steps interaction
    function initProgressSteps() {
        const progressSteps = document.querySelectorAll('.progress-step');
        const progressBar = document.querySelector('.progress-steps');

        if (progressBar) {
            // Find the active step index
            let activeIndex = 0;
            progressSteps.forEach((step, index) => {
                if (step.classList.contains('active')) {
                    activeIndex = index;
                }
            });

            // Set the progress bar data attribute
            progressBar.setAttribute('data-progress', activeIndex);
        }

        progressSteps.forEach((step, index) => {
            step.addEventListener('mouseenter', () => {
                if (!step.classList.contains('active') && !step.classList.contains('completed')) {
                    step.querySelector('.step-number').style.transform = 'scale(1.1)';
                }
            });

            step.addEventListener('mouseleave', () => {
                if (!step.classList.contains('active') && !step.classList.contains('completed')) {
                    step.querySelector('.step-number').style.transform = 'scale(1)';
                }
            });
        });
    }

    // Animations
    function initAnimations() {
        // Staggered animation for form groups
        const formGroups = document.querySelectorAll('.form-group, .mb-3');
        formGroups.forEach((group, index) => {
            group.style.opacity = '0';
            group.style.transform = 'translateY(20px)';

            setTimeout(() => {
                group.style.transition = 'all 0.5s ease';
                group.style.opacity = '1';
                group.style.transform = 'translateY(0)';
            }, 100 + (index * 50));
        });

        // Card entrance animation
        const cards = document.querySelectorAll('.card');
        cards.forEach((card, index) => {
            card.style.opacity = '0';
            card.style.transform = 'translateY(20px)';

            setTimeout(() => {
                card.style.transition = 'all 0.5s ease';
                card.style.opacity = '1';
                card.style.transform = 'translateY(0)';
            }, 300 + (index * 100));
        });
    }

    // Automatic calculations
    function initCalculations() {
        // Calculate Years in Service based on Date of Commission
        const commissionDateInput = document.getElementById('date_of_commission');
        const yearsInServiceInput = document.getElementById('years_in_service');

        if (commissionDateInput && yearsInServiceInput) {
            // Calculate on change
            commissionDateInput.addEventListener('change', calculateYearsInService);

            // Calculate on page load if commission date has a value
            if (commissionDateInput.value) {
                calculateYearsInService();
            }

            // Also calculate when the form loads with existing data
            window.addEventListener('load', function() {
                if (commissionDateInput.value) {
                    calculateYearsInService();
                }
            });
        }

        function calculateYearsInService() {
            if (!commissionDateInput.value) {
                return;
            }

            const commissionDate = new Date(commissionDateInput.value);
            const today = new Date();

            // Validate the date
            if (isNaN(commissionDate.getTime())) {
                console.error('Invalid date format');
                return;
            }

            // Calculate the difference in years
            let years = today.getFullYear() - commissionDate.getFullYear();

            // Adjust for months and days
            if (today.getMonth() < commissionDate.getMonth() ||
                (today.getMonth() === commissionDate.getMonth() && today.getDate() < commissionDate.getDate())) {
                years--;
            }

            // Ensure we don't have negative years
            years = Math.max(0, years);

            // Set the calculated value
            yearsInServiceInput.value = years;

            // Trigger change event to update validation
            const event = new Event('change');
            yearsInServiceInput.dispatchEvent(event);

            console.log(`Years in service calculated: ${years} years (from ${commissionDateInput.value} to today)`);
        }
    }
});
