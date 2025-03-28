document.addEventListener('DOMContentLoaded', function() {
    // Form sections animation
    const formSections = document.querySelectorAll('.form-section');
    formSections.forEach((section, index) => {
        section.style.animationDelay = `${index * 0.2}s`;
    });

    // Progress steps interaction
    const progressSteps = document.querySelectorAll('.progress-step');
    progressSteps.forEach((step, index) => {
        step.addEventListener('mouseenter', () => {
            step.querySelector('.step-icon').style.transform = 'scale(1.1) rotate(5deg)';
        });
        step.addEventListener('mouseleave', () => {
            if (!step.classList.contains('active')) {
                step.querySelector('.step-icon').style.transform = 'scale(1) rotate(0deg)';
            }
        });
    });

    // Enhanced form validation
    const form = document.querySelector('form');
    const inputs = form.querySelectorAll('input, select, textarea');

    inputs.forEach(input => {
        input.addEventListener('input', function() {
            validateField(this);
        });

        input.addEventListener('focus', function() {
            this.closest('.form-floating').style.transform = 'translateY(-5px)';
        });

        input.addEventListener('blur', function() {
            this.closest('.form-floating').style.transform = 'translateY(0)';
            validateField(this);
        });
    });

    // Image preview functionality
    const passportInput = document.getElementById('passport');
    const previewImg = document.getElementById('passport-preview');

    passportInput.addEventListener('change', function(e) {
        const file = e.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = function(e) {
                previewImg.src = e.target.result;
                previewImg.style.animation = 'pulse 0.5s';
                setTimeout(() => {
                    previewImg.style.animation = '';
                }, 500);
            };
            reader.readAsDataURL(file);
        }
    });

    // Field validation function
    function validateField(field) {
        const parent = field.closest('.form-floating');
        
        if (field.checkValidity()) {
            field.classList.remove('is-invalid');
            field.classList.add('is-valid');
            parent.classList.remove('has-error');
            parent.classList.add('has-success');
        } else {
            field.classList.remove('is-valid');
            field.classList.add('is-invalid');
            parent.classList.remove('has-success');
            parent.classList.add('has-error');
        }
    }

    // State field toggle based on country selection
    window.toggleStateField = function() {
        const countrySelect = document.getElementById('country');
        const stateContainer = document.getElementById('stateFieldContainer');
        const stateSelect = document.getElementById('state');

        if (countrySelect.value === 'Nigeria') {
            stateContainer.style.display = 'block';
            stateSelect.required = true;
        } else {
            stateContainer.style.display = 'none';
            stateSelect.required = false;
        }
    }
});
