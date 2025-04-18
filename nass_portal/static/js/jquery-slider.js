$(document).ready(function() {
    // Get all slides
    const $slides = $('.jquery-slide');
    if ($slides.length <= 1) return; // No need for slider if only one slide
    
    let currentSlide = 0;
    const totalSlides = $slides.length;
    
    console.log('jQuery slider initialized with ' + totalSlides + ' slides');
    
    // Hide all slides except the first one
    $slides.hide();
    $slides.eq(0).show();
    
    // Function to show the next slide
    function showNextSlide() {
        // Hide current slide with fade out
        $slides.eq(currentSlide).fadeOut(500, function() {
            // Move to next slide (or back to first if at the end)
            currentSlide = (currentSlide + 1) % totalSlides;
            
            // Show the new current slide with fade in
            $slides.eq(currentSlide).fadeIn(500);
            
            console.log('Showing slide ' + (currentSlide + 1) + ' of ' + totalSlides);
        });
    }
    
    // Set interval to change slides every 5 seconds
    const slideInterval = setInterval(showNextSlide, 5000);
    
    // Add navigation buttons functionality
    $('.slider-next').click(function(e) {
        e.preventDefault();
        clearInterval(slideInterval); // Clear the interval
        showNextSlide();
    });
    
    $('.slider-prev').click(function(e) {
        e.preventDefault();
        clearInterval(slideInterval); // Clear the interval
        
        // Hide current slide with fade out
        $slides.eq(currentSlide).fadeOut(500, function() {
            // Move to previous slide (or to last if at the beginning)
            currentSlide = (currentSlide - 1 + totalSlides) % totalSlides;
            
            // Show the new current slide with fade in
            $slides.eq(currentSlide).fadeIn(500);
        });
    });
});
