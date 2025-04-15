/**
 * Enhanced Progress Bar JavaScript
 * Provides interactive and animated progress bar functionality
 */

document.addEventListener('DOMContentLoaded', function() {
    initProgressBar();
    
    function initProgressBar() {
        const progressSteps = document.querySelectorAll('.progress-step');
        const progressBar = document.querySelector('.progress-steps');
        
        if (!progressBar) return;
        
        // Determine current page from URL
        const currentUrl = window.location.pathname;
        let currentPage = 0;
        
        if (currentUrl.includes('registration_page_1')) {
            currentPage = 0;
        } else if (currentUrl.includes('registration_page_2')) {
            currentPage = 1;
        } else if (currentUrl.includes('registration_page_3')) {
            currentPage = 2;
        } else if (currentUrl.includes('registration_page_4')) {
            currentPage = 3;
        } else if (currentUrl.includes('registration_page_5')) {
            currentPage = 4;
        } else if (currentUrl.includes('registration_page_6')) {
            currentPage = 5;
        } else if (currentUrl.includes('registration_page_7')) {
            currentPage = 6;
        }
        
        // Update progress bar
        progressBar.setAttribute('data-progress', currentPage);
        
        // Mark steps as active or completed
        progressSteps.forEach((step, index) => {
            // Reset classes first
            step.classList.remove('active', 'completed');
            
            // Set appropriate class
            if (index === currentPage) {
                step.classList.add('active');
            } else if (index < currentPage) {
                step.classList.add('completed');
            }
            
            // Add hover effects
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
            
            // Add click functionality for completed steps (navigation)
            if (step.classList.contains('completed')) {
                step.style.cursor = 'pointer';
                step.addEventListener('click', () => {
                    // Navigate to the corresponding page
                    window.location.href = `/registration_page_${index + 1}`;
                });
            }
        });
        
        // Add animation to active step
        const activeStep = document.querySelector('.progress-step.active');
        if (activeStep) {
            setTimeout(() => {
                activeStep.querySelector('.step-number').classList.add('animated');
            }, 300);
        }
    }
});
