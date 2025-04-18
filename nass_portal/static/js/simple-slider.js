document.addEventListener('DOMContentLoaded', function() {
    // Create a basic slider that changes every 5 seconds
    const sliderContainer = document.querySelector('.announcement-slider');
    if (!sliderContainer) return;
    
    const slides = document.querySelectorAll('.swiper-slide');
    if (slides.length <= 1) return;
    
    console.log('Simple slider initialized with ' + slides.length + ' slides');
    
    let currentIndex = 0;
    
    // Hide all slides except the first one
    for (let i = 1; i < slides.length; i++) {
        slides[i].style.display = 'none';
    }
    
    // Function to show the next slide
    function showNextSlide() {
        // Hide all slides
        for (let i = 0; i < slides.length; i++) {
            slides[i].style.display = 'none';
        }
        
        // Increment index and wrap around if necessary
        currentIndex = (currentIndex + 1) % slides.length;
        
        // Show the current slide
        slides[currentIndex].style.display = 'block';
        
        console.log('Showing slide ' + (currentIndex + 1) + ' of ' + slides.length);
    }
    
    // Set interval to change slides every 5 seconds
    setInterval(showNextSlide, 5000);
});
