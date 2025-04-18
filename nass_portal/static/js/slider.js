// Simple slider implementation
document.addEventListener('DOMContentLoaded', function() {
    // Wait for DOM to be fully loaded
    setTimeout(function() {
        // Get all slides
        const slides = document.querySelectorAll('.swiper-slide');
        if (slides.length <= 1) return; // No need for slider if only one slide
        
        let currentSlide = 0;
        const totalSlides = slides.length;
        
        console.log('Simple slider initialized with ' + totalSlides + ' slides');
        
        // Hide all slides except the first one
        for (let i = 1; i < slides.length; i++) {
            slides[i].style.display = 'none';
        }
        
        // Function to show the next slide
        function showNextSlide() {
            // Hide current slide
            slides[currentSlide].style.display = 'none';
            
            // Move to next slide (or back to first if at the end)
            currentSlide = (currentSlide + 1) % totalSlides;
            
            // Show the new current slide
            slides[currentSlide].style.display = 'block';
            
            console.log('Showing slide ' + (currentSlide + 1) + ' of ' + totalSlides);
        }
        
        // Set interval to change slides every 5 seconds
        const slideInterval = setInterval(showNextSlide, 5000);
        
        // Add navigation buttons functionality
        const nextButton = document.querySelector('.swiper-button-next');
        const prevButton = document.querySelector('.swiper-button-prev');
        
        if (nextButton) {
            nextButton.addEventListener('click', function() {
                clearInterval(slideInterval); // Clear the interval
                showNextSlide();
                // Restart the interval
                setInterval(showNextSlide, 5000);
            });
        }
        
        if (prevButton) {
            prevButton.addEventListener('click', function() {
                clearInterval(slideInterval); // Clear the interval
                
                // Hide current slide
                slides[currentSlide].style.display = 'none';
                
                // Move to previous slide (or to last if at the beginning)
                currentSlide = (currentSlide - 1 + totalSlides) % totalSlides;
                
                // Show the new current slide
                slides[currentSlide].style.display = 'block';
                
                // Restart the interval
                setInterval(showNextSlide, 5000);
            });
        }
    }, 500);
});
