// Bootstrap Carousel Initialization
$(document).ready(function() {
    // Initialize the carousel with a 5-second interval
    $('#announcementCarousel').carousel({
        interval: 5000,
        pause: false,
        ride: 'carousel',
        wrap: true
    });
    
    console.log('Bootstrap carousel initialized with 5-second interval');
    
    // Force the carousel to start
    $('#announcementCarousel').carousel('cycle');
    
    // Add event listener for slide events
    $('#announcementCarousel').on('slide.bs.carousel', function (e) {
        console.log('Carousel sliding to item ' + (e.to + 1));
    });
    
    // Ensure carousel continues to cycle even after user interaction
    $('.carousel-control-prev, .carousel-control-next, .carousel-indicators li').on('click', function() {
        setTimeout(function() {
            $('#announcementCarousel').carousel('cycle');
        }, 100);
    });
    
    // Additional check to ensure carousel is running
    setTimeout(function() {
        $('#announcementCarousel').carousel('cycle');
        console.log('Carousel cycling confirmed after delay');
    }, 2000);
});
