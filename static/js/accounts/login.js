
// Hide the sidebar and header for login page
$(document).ready(function() {
    $('.sidebar, .header, .footer').hide();
    $('.main').css('margin-left', '0');
    
    // Add Bootstrap classes to form inputs if not already added by Django
    $('input[type="text"], input[type="password"]').addClass('form-control');
    
    // Add animation effect on form submission
    $('.login-form').on('submit', function() {
        $('.login-card').css('opacity', '0.7');
        $('button[type="submit"]').html('<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>Signing in...');
    });
    
    // Password visibility toggle
    const togglePassword = document.createElement('span');
    togglePassword.innerHTML = '<i class="far fa-eye"></i>';
    togglePassword.className = 'position-absolute end-0 top-50 translate-middle-y pe-3 text-muted';
    togglePassword.style.cursor = 'pointer';
    togglePassword.style.zIndex = '10';
    
    const passwordField = $('#{{ form.password.id_for_label }}').parent();
    passwordField.css('position', 'relative');
    passwordField.append(togglePassword);
    
    $(togglePassword).click(function() {
        const input = $('#{{ form.password.id_for_label }}');
        if (input.attr('type') === 'password') {
            input.attr('type', 'text');
            $(this).html('<i class="far fa-eye-slash"></i>');
        } else {
            input.attr('type', 'password');
            $(this).html('<i class="far fa-eye"></i>');
        }
    });
    
});
