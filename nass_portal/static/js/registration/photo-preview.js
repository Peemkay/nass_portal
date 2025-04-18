/**
 * Enhanced Photo Preview Functionality
 */

document.addEventListener('DOMContentLoaded', function() {
    console.log('Photo preview script loaded');
    initPhotoPreview();

    function initPhotoPreview() {
        const photoInput = document.getElementById('passport_photo');
        if (!photoInput) {
            console.log('Photo input element not found');
            return;
        }

        const previewImage = document.getElementById('preview-image');
        const photoPreview = document.getElementById('photo-preview');
        if (!previewImage || !photoPreview) {
            console.log('Preview elements not found');
            return;
        }

        console.log('Photo preview elements found, initializing');
        const uploadHint = photoPreview.querySelector('.photo-upload-hint');

        // Handle file selection
        photoInput.addEventListener('change', function(e) {
            console.log('File selected via input');
            handleFileSelection(this.files[0]);
        });

        // Handle drag and drop
        photoPreview.addEventListener('dragover', function(e) {
            e.preventDefault();
            e.stopPropagation();
            this.classList.add('dragover');
        });

        photoPreview.addEventListener('dragleave', function(e) {
            e.preventDefault();
            e.stopPropagation();
            this.classList.remove('dragover');
        });

        photoPreview.addEventListener('drop', function(e) {
            e.preventDefault();
            e.stopPropagation();
            this.classList.remove('dragover');

            if (e.dataTransfer.files.length) {
                console.log('File dropped');
                handleFileSelection(e.dataTransfer.files[0]);

                // Update the file input
                try {
                    const dataTransfer = new DataTransfer();
                    dataTransfer.items.add(e.dataTransfer.files[0]);
                    photoInput.files = dataTransfer.files;
                } catch (err) {
                    console.error('Error setting files:', err);
                }
            }
        });

        // Click to browse
        photoPreview.addEventListener('click', function() {
            console.log('Preview clicked');
            photoInput.click();
        });

        // Check if there's already a file selected (e.g. after page refresh)
        if (photoInput.files && photoInput.files[0]) {
            console.log('Existing file found');
            handleFileSelection(photoInput.files[0]);
        }

        // Function to handle file selection
        function handleFileSelection(file) {
            if (!file) {
                console.log('No file provided');
                return;
            }

            console.log('Processing file:', file.name);
            const reader = new FileReader();

            reader.onload = function(e) {
                console.log('File loaded successfully');
                previewImage.src = e.target.result;
                previewImage.style.display = 'block';

                // Hide the upload hint when image is loaded
                if (uploadHint) {
                    uploadHint.style.display = 'none';
                }

                // Add a loaded class for styling
                photoPreview.classList.add('loaded');

                // Show success message
                const successMsg = document.createElement('div');
                successMsg.className = 'alert alert-success mt-2';
                successMsg.innerHTML = '<i class="fas fa-check-circle"></i> Photo loaded successfully!';

                // Remove any existing success messages
                const existingMsg = photoPreview.parentNode.querySelector('.alert-success');
                if (existingMsg) {
                    existingMsg.remove();
                }

                photoPreview.parentNode.appendChild(successMsg);

                // Remove after 3 seconds
                setTimeout(() => {
                    successMsg.remove();
                }, 3000);
            };

            reader.onerror = function(e) {
                console.error('Error loading file:', e);
                // Show error message
                const errorMsg = document.createElement('div');
                errorMsg.className = 'alert alert-danger mt-2';
                errorMsg.innerHTML = '<i class="fas fa-exclamation-circle"></i> Failed to load image. Please try again.';

                // Remove any existing messages
                const existingMsg = photoPreview.parentNode.querySelector('.alert');
                if (existingMsg) {
                    existingMsg.remove();
                }

                photoPreview.parentNode.appendChild(errorMsg);

                // Remove after 3 seconds
                setTimeout(() => {
                    errorMsg.remove();
                }, 3000);
            };

            reader.readAsDataURL(file);
        }
    }
});

// Legacy function for backward compatibility
function previewImage(input) {
    console.log('Legacy preview function called');
    if (input.files && input.files[0]) {
        const reader = new FileReader();
        reader.onload = function(e) {
            const preview = document.getElementById('passport-preview') || document.getElementById('preview-image');
            if (preview) {
                preview.src = e.target.result;

                // Also hide the upload hint if it exists
                const uploadHint = document.querySelector('.photo-upload-hint');
                if (uploadHint) {
                    uploadHint.style.display = 'none';
                }
            }
        }
        reader.readAsDataURL(input.files[0]);
    }
}