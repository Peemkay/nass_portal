// Simple script to ensure the slider starts properly
document.addEventListener('DOMContentLoaded', function() {
    // Get the slider
    const slider = document.querySelector('.simple-slider');
    if (!slider) return;
    
    // Force a reflow to ensure animations start properly
    setTimeout(function() {
        slider.classList.remove('animated');
        void slider.offsetWidth; // Force reflow
        slider.classList.add('animated');
        console.log('Simple slider initialized');
    }, 100);
});
