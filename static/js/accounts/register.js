// Hide the sidebar and header for register page
$(document).ready(function() {
    $('.sidebar, .header, .footer').hide();
    $('.main').css('margin-left', '0');
    
    // Add Bootstrap classes to form inputs if not already added by Django
    $('input[type="text"], input[type="email"], input[type="password"]').addClass('form-control');
    
    // Add animation effect on form submission
    $('form').on('submit', function() {
        $('.register-card').css('opacity', '0.7');
        $('button[type="submit"]').html('<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>Creating account...');
    });
});