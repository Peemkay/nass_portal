// Basic slider implementation with no dependencies
document.addEventListener('DOMContentLoaded', function() {
    // Basic slider functionality
    function setupSlider() {
        // Get all slides
        const slides = document.querySelectorAll('.basic-slide');
        if (!slides || slides.length <= 1) {
            console.log('No slides found or only one slide');
            return;
        }
        
        console.log('Setting up basic slider with ' + slides.length + ' slides');
        
        // Set initial state - hide all slides except the first one
        for (let i = 0; i < slides.length; i++) {
            if (i === 0) {
                slides[i].style.display = 'block';
            } else {
                slides[i].style.display = 'none';
            }
        }
        
        let currentIndex = 0;
        
        // Function to show a specific slide
        function showSlide(index) {
            // Hide all slides
            for (let i = 0; i < slides.length; i++) {
                slides[i].style.display = 'none';
            }
            
            // Show the selected slide
            slides[index].style.display = 'block';
            currentIndex = index;
            
            console.log('Showing slide ' + (currentIndex + 1) + ' of ' + slides.length);
        }
        
        // Function to show the next slide
        function showNextSlide() {
            const nextIndex = (currentIndex + 1) % slides.length;
            showSlide(nextIndex);
        }
        
        // Function to show the previous slide
        function showPrevSlide() {
            const prevIndex = (currentIndex - 1 + slides.length) % slides.length;
            showSlide(prevIndex);
        }
        
        // Set up next/prev buttons
        const nextButton = document.querySelector('.slider-next');
        const prevButton = document.querySelector('.slider-prev');
        
        if (nextButton) {
            nextButton.addEventListener('click', function(e) {
                e.preventDefault();
                showNextSlide();
            });
        }
        
        if (prevButton) {
            prevButton.addEventListener('click', function(e) {
                e.preventDefault();
                showPrevSlide();
            });
        }
        
        // Set up automatic sliding
        setInterval(showNextSlide, 5000);
    }
    
    // Run the setup
    setupSlider();
});
