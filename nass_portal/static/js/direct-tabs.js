// Direct implementation of tab functionality
$(document).ready(function() {
    console.log('Direct tabs implementation loaded');
    
    // Function to activate a tab
    function activateTab(tabId, contentId) {
        // Deactivate all tabs and content
        $('.nav-link').removeClass('active');
        $('.tab-pane').removeClass('show active');
        
        // Activate the selected tab and content
        $(tabId).addClass('active');
        $(contentId).addClass('show active');
        
        console.log('Activated tab:', tabId, 'Content:', contentId);
    }
    
    // Handle soldiers tab click in first tab group
    $('#soldiers-tab').click(function(e) {
        e.preventDefault();
        activateTab('#soldiers-tab', '#soldiers');
        console.log('Soldiers tab clicked directly');
    });
    
    // Handle soldiers tab click in second tab group
    $('#soldiers-tab2').click(function(e) {
        e.preventDefault();
        activateTab('#soldiers-tab2', '#soldiers2');
        console.log('Soldiers tab 2 clicked directly');
    });
    
    // Add click handlers for all tabs
    $('#all-tab').click(function(e) {
        e.preventDefault();
        activateTab('#all-tab', '#all');
    });
    
    $('#officers-tab').click(function(e) {
        e.preventDefault();
        activateTab('#officers-tab', '#officers');
    });
    
    $('#officers-tab2').click(function(e) {
        e.preventDefault();
        activateTab('#officers-tab2', '#officers2');
    });
});
