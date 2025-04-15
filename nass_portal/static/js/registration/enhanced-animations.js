/**
 * Enhanced Animations for Registration Forms
 * Provides smooth, staggered animations and interactive elements
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize animations
    initCardAnimations();
    initFormAnimations();
    initButtonAnimations();
    initPhotoPreviewEnhancements();
    
    // Card entrance animations with staggered timing
    function initCardAnimations() {
        const cards = document.querySelectorAll('.card');
        
        cards.forEach((card, index) => {
            // Set initial state
            card.style.opacity = '0';
            card.style.transform = 'translateY(20px)';
            
            // Animate with staggered delay
            setTimeout(() => {
                card.style.transition = 'all 0.6s cubic-bezier(0.175, 0.885, 0.32, 1.275)';
                card.style.opacity = '1';
                card.style.transform = 'translateY(0)';
            }, 100 + (index * 100));
            
            // Add hover effect
            card.addEventListener('mouseenter', () => {
                card.style.transform = 'translateY(-5px)';
                card.style.boxShadow = '0 8px 25px rgba(0, 0, 0, 0.1)';
            });
            
            card.addEventListener('mouseleave', () => {
                card.style.transform = 'translateY(0)';
                card.style.boxShadow = '0 4px 15px rgba(0, 0, 0, 0.05)';
            });
        });
    }
    
    // Form field animations with staggered timing
    function initFormAnimations() {
        const formGroups = document.querySelectorAll('.form-group, .mb-3');
        
        formGroups.forEach((group, index) => {
            // Set initial state
            group.style.opacity = '0';
            group.style.transform = 'translateY(15px)';
            
            // Animate with staggered delay
            setTimeout(() => {
                group.style.transition = 'all 0.5s ease';
                group.style.opacity = '1';
                group.style.transform = 'translateY(0)';
            }, 300 + (index * 50));
        });
        
        // Add focus effects to form controls
        const formControls = document.querySelectorAll('.form-control, .form-select');
        
        formControls.forEach(control => {
            control.addEventListener('focus', () => {
                const label = control.closest('.mb-3').querySelector('.form-label');
                if (label) {
                    label.style.color = '#1e3c72';
                    label.style.transition = 'color 0.3s ease';
                }
            });
            
            control.addEventListener('blur', () => {
                const label = control.closest('.mb-3').querySelector('.form-label');
                if (label) {
                    label.style.color = '';
                }
            });
        });
    }
    
    // Button animations and effects
    function initButtonAnimations() {
        const buttons = document.querySelectorAll('.btn');
        
        buttons.forEach(button => {
            button.addEventListener('mouseenter', () => {
                button.style.transition = 'all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275)';
                button.style.transform = 'translateY(-2px) scale(1.02)';
            });
            
            button.addEventListener('mouseleave', () => {
                button.style.transform = '';
            });
            
            button.addEventListener('click', () => {
                button.style.transform = 'translateY(1px) scale(0.98)';
                setTimeout(() => {
                    button.style.transform = '';
                }, 200);
            });
        });
    }
    
    // Enhanced photo preview functionality
    function initPhotoPreviewEnhancements() {
        const photoInput = document.getElementById('passport_photo');
        const previewContainer = document.getElementById('photo-preview');
        
        if (!photoInput || !previewContainer) return;
        
        // Add drag and drop functionality
        previewContainer.addEventListener('dragover', (e) => {
            e.preventDefault();
            previewContainer.classList.add('dragover');
        });
        
        previewContainer.addEventListener('dragleave', () => {
            previewContainer.classList.remove('dragover');
        });
        
        previewContainer.addEventListener('drop', (e) => {
            e.preventDefault();
            previewContainer.classList.remove('dragover');
            
            if (e.dataTransfer.files.length) {
                photoInput.files = e.dataTransfer.files;
                
                // Trigger change event
                const event = new Event('change', { bubbles: true });
                photoInput.dispatchEvent(event);
            }
        });
        
        // Add click to upload functionality
        previewContainer.addEventListener('click', () => {
            if (!previewContainer.classList.contains('loaded')) {
                photoInput.click();
            }
        });
    }
});
