// Vanilla JavaScript slider with no dependencies
window.addEventListener('load', function() {
    // Wait for everything to load completely
    setTimeout(function() {
        // Get all slides
        const slides = document.querySelectorAll('.basic-slide');
        if (!slides || slides.length <= 1) {
            console.log('No slides found or only one slide');
            return;
        }
        
        console.log('Setting up vanilla slider with ' + slides.length + ' slides');
        
        // Set initial state - hide all slides except the first one
        for (let i = 0; i < slides.length; i++) {
            slides[i].style.display = i === 0 ? 'block' : 'none';
        }
        
        let currentIndex = 0;
        let slideInterval = null;
        
        // Function to show a specific slide
        function showSlide(index) {
            // Hide current slide
            slides[currentIndex].style.display = 'none';
            
            // Update index
            currentIndex = index;
            
            // Show new slide
            slides[currentIndex].style.display = 'block';
            
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
                // Clear existing interval
                if (slideInterval) {
                    clearInterval(slideInterval);
                }
                showNextSlide();
                // Restart interval
                slideInterval = setInterval(showNextSlide, 5000);
            });
        }
        
        if (prevButton) {
            prevButton.addEventListener('click', function(e) {
                e.preventDefault();
                // Clear existing interval
                if (slideInterval) {
                    clearInterval(slideInterval);
                }
                showPrevSlide();
                // Restart interval
                slideInterval = setInterval(showNextSlide, 5000);
            });
        }
        
        // Start automatic sliding
        slideInterval = setInterval(showNextSlide, 5000);
        
        // For debugging - add a visual indicator of which slide is active
        const slider = document.querySelector('.basic-slider');
        if (slider) {
            const indicator = document.createElement('div');
            indicator.className = 'slide-indicator';
            indicator.style.position = 'absolute';
            indicator.style.bottom = '10px';
            indicator.style.left = '50%';
            indicator.style.transform = 'translateX(-50%)';
            indicator.style.zIndex = '10';
            indicator.style.display = 'flex';
            indicator.style.gap = '5px';
            
            for (let i = 0; i < slides.length; i++) {
                const dot = document.createElement('span');
                dot.style.width = '10px';
                dot.style.height = '10px';
                dot.style.borderRadius = '50%';
                dot.style.backgroundColor = i === 0 ? 'white' : 'rgba(255, 255, 255, 0.5)';
                dot.style.transition = 'background-color 0.3s ease';
                
                // Store the index on the dot
                dot.dataset.index = i;
                
                // Add click event
                dot.addEventListener('click', function() {
                    const index = parseInt(this.dataset.index);
                    // Clear existing interval
                    if (slideInterval) {
                        clearInterval(slideInterval);
                    }
                    showSlide(index);
                    // Update indicators
                    updateIndicators();
                    // Restart interval
                    slideInterval = setInterval(showNextSlide, 5000);
                });
                
                indicator.appendChild(dot);
            }
            
            slider.appendChild(indicator);
            
            // Function to update indicators
            function updateIndicators() {
                const dots = indicator.querySelectorAll('span');
                for (let i = 0; i < dots.length; i++) {
                    dots[i].style.backgroundColor = i === currentIndex ? 'white' : 'rgba(255, 255, 255, 0.5)';
                }
            }
            
            // Update indicators when slide changes
            const originalShowSlide = showSlide;
            showSlide = function(index) {
                originalShowSlide(index);
                updateIndicators();
            };
        }
    }, 500); // Wait 500ms to ensure everything is loaded
});
