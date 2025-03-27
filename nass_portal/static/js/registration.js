document.addEventListener('DOMContentLoaded', function() {
    // Photo preview functionality
    const passportInput = document.getElementById('passport');
    const previewImg = document.getElementById('passport-preview');
    
    if (passportInput && previewImg) {
        passportInput.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                // Validate file size (max 2MB)
                if (file.size > 2 * 1024 * 1024) {
                    alert('File size must be less than 2MB');
                    e.target.value = '';
                    return;
                }

                // Validate file type
                if (!file.type.match('image.*')) {
                    alert('Please upload an image file');
                    e.target.value = '';
                    return;
                }

                const reader = new FileReader();
                reader.onload = function(e) {
                    previewImg.src = e.target.result;
                    previewImg.classList.add('preview-animation');
                };
                reader.readAsDataURL(file);
            }
        });
    }

    // Form validation
    const form = document.querySelector('form');
    if (form) {
        form.addEventListener('submit', function(e) {
            if (!form.checkValidity()) {
                e.preventDefault();
                e.stopPropagation();
                highlightInvalidFields();
            }
            form.classList.add('was-validated');
        });
    }

    // Function to highlight invalid fields
    function highlightInvalidFields() {
        const invalidFields = form.querySelectorAll(':invalid');
        invalidFields.forEach(field => {
            field.parentElement.classList.add('invalid-feedback-visible');
        });
    }

    // Progress step animation
    const progressSteps = document.querySelectorAll('.progress-step');
    progressSteps.forEach((step, index) => {
        step.style.animationDelay = `${index * 0.2}s`;
        step.classList.add('fade-in');
    });
});

// Custom file input styling
function updateFileLabel(input) {
    const fileName = input.files[0]?.name || 'No file chosen';
    const label = input.parentElement.querySelector('.custom-file-label');
    if (label) {
        label.textContent = fileName;
    }
}

// Form field animations
document.querySelectorAll('.form-control').forEach(input => {
    input.addEventListener('focus', function() {
        this.parentElement.classList.add('input-focused');
    });

    input.addEventListener('blur', function() {
        if (!this.value) {
            this.parentElement.classList.remove('input-focused');
        }
    });
});