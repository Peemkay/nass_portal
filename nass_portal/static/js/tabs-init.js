// Simple Bootstrap Tabs Initialization
$(document).ready(function() {
    console.log('Initializing course tabs with direct approach...');

    // Initialize Bootstrap tabs directly
    $('#courseTabs a[data-toggle="pill"], #courseTabs button[data-toggle="pill"]').on('click', function(e) {
        e.preventDefault();
        $(this).tab('show');
    });

    $('#courseTabs2 a[data-toggle="pill"], #courseTabs2 button[data-toggle="pill"]').on('click', function(e) {
        e.preventDefault();
        $(this).tab('show');
    });

    // Direct click handler for soldiers tab
    $('#soldiers-tab').on('click', function(e) {
        e.preventDefault();
        console.log('Soldiers tab clicked');
        $(this).tab('show');
    });

    // Direct click handler for soldiers tab in second tab group
    $('#soldiers-tab2').on('click', function(e) {
        e.preventDefault();
        console.log('Soldiers tab 2 clicked');
        $(this).tab('show');
    });

    // Initialize tabs on page load
    $('#all-tab').tab('show');
    $('#officers-tab2').tab('show');

    console.log('Course tabs initialized');
});
