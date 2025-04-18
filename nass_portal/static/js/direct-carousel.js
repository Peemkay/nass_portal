// Direct JavaScript implementation of carousel
document.addEventListener('DOMContentLoaded', function() {
    // Get the carousel element
    const carousel = document.getElementById('announcementCarousel');
    if (!carousel) {
        console.log('Carousel element not found');
        return;
    }

    // Get all carousel items
    const items = carousel.querySelectorAll('.carousel-item');
    if (items.length <= 1) {
        console.log('Not enough items for carousel');
        return;
    }

    console.log('Setting up direct carousel with ' + items.length + ' items');

    // Initialize Bootstrap carousel with explicit 5-second interval
    $(carousel).carousel({
        interval: 5000,  // 5 seconds
        pause: false,    // Don't pause on hover
        wrap: true,      // Cycle continuously
        keyboard: true   // Allow keyboard navigation
    });

    // Force start the carousel
    $(carousel).carousel('cycle');

    console.log('Bootstrap carousel initialized with 5-second interval');

    // Add event listeners to ensure carousel continues to work
    carousel.addEventListener('slide.bs.carousel', function(e) {
        console.log('Carousel sliding to item ' + (e.to + 1) + ' of ' + items.length);
    });

    // Add a class to indicate the carousel is initialized
    carousel.classList.add('carousel-initialized');

    // Additional check to ensure carousel is running
    setTimeout(function() {
        // Force restart the carousel if needed
        $(carousel).carousel('cycle');
        console.log('Carousel cycling confirmed after delay');
    }, 1000);
});
