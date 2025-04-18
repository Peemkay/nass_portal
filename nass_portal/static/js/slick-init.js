$(document).ready(function(){
    // Initialize Slick Slider for announcements
    $('.announcement-slider .swiper-wrapper').slick({
        dots: true,
        arrows: true,
        infinite: true,
        speed: 500,
        fade: true,
        cssEase: 'linear',
        autoplay: true,
        autoplaySpeed: 5000,
        slidesToShow: 1,
        slidesToScroll: 1,
        adaptiveHeight: true,
        prevArrow: $('.swiper-button-prev'),
        nextArrow: $('.swiper-button-next')
    });
    
    console.log('Slick slider initialized with 5-second autoplay');
});
