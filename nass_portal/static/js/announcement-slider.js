document.addEventListener('DOMContentLoaded', function() {
    // Wait a bit to ensure DOM is fully loaded
    setTimeout(function() {
        // Check if the swiper container exists
        const swiperContainer = document.querySelector('.swiper-container');
        if (!swiperContainer) {
            console.log('Swiper container not found');
            return;
        }

        console.log('Initializing Swiper with 5-second autoplay...');

        // Initialize Swiper with explicit autoplay
        const announcementSwiper = new Swiper('.swiper-container', {
        slidesPerView: 1,
        spaceBetween: 30,
        loop: true,
        speed: 1000,
        autoplay: {
            delay: 5000, // 5 seconds
            disableOnInteraction: false,
            pauseOnMouseEnter: false,
        },
        pagination: {
            el: '.swiper-pagination',
            clickable: true,
        },
        navigation: {
            nextEl: '.swiper-button-next',
            prevEl: '.swiper-button-prev',
        },
    });

    // Force start autoplay
    announcementSwiper.autoplay.start();

    // Debug log
    console.log('Swiper initialized with autoplay:', announcementSwiper.autoplay.running);

        // Add event listeners to ensure autoplay continues
        swiperContainer.addEventListener('mouseenter', function() {
            console.log('Mouse entered, autoplay status:', announcementSwiper.autoplay.running);
        });

        swiperContainer.addEventListener('mouseleave', function() {
            console.log('Mouse left, restarting autoplay');
            announcementSwiper.autoplay.start();
        });
    }, 500); // 500ms delay to ensure DOM is ready
});
