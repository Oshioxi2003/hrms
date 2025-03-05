$(document).ready(function() {
    // Hide the sidebar and header for password reset page
    $('.sidebar, .header, .footer').hide();
    $('.main').css('margin-left', '0');
    
    // Password toggle functionality
    setupPasswordToggle('#id_new_password1', '#togglePassword1');
    setupPasswordToggle('#id_new_password2', '#togglePassword2');
    
    // Password strength and validation
    const password1Field = $('#id_new_password1');
    const password2Field = $('#id_new_password2');
    const strengthIndicator = $('#strengthIndicator');
    const strengthText = $('#strengthText');
    const passwordMatchFeedback = $('#passwordMatch');
    const submitBtn = $('#submitBtn');
    
    // Requirements elements
    const reqLength = $('#req-length');
    const reqUppercase = $('#req-uppercase');
    const reqLowercase = $('#req-lowercase');
    const reqNumber = $('#req-number');
    const reqSpecial = $('#req-special');
    
    // Password requirements regex patterns
    const patterns = {
        length: /.{8,}/,
        uppercase: /[A-Z]/,
        lowercase: /[a-z]/,
        number: /[0-9]/,
        special: /[^A-Za-z0-9]/
    };
    
    // Check password strength
    password1Field.on('input', function() {
        const password = $(this).val();
        let strength = 0;
        let strengthClass = '';
        let strengthMessage = '';
        
        // Update requirements indicators
        updateRequirement(reqLength, patterns.length.test(password));
        updateRequirement(reqUppercase, patterns.uppercase.test(password));
        updateRequirement(reqLowercase, patterns.lowercase.test(password));
        updateRequirement(reqNumber, patterns.number.test(password));
        updateRequirement(reqSpecial, patterns.special.test(password));
        
        // Calculate password strength
        if (password.length > 0) {
            if (patterns.length.test(password)) strength += 20;
            if (patterns.uppercase.test(password)) strength += 20;
            if (patterns.lowercase.test(password)) strength += 20;
            if (patterns.number.test(password)) strength += 20;
            if (patterns.special.test(password)) strength += 20;
            
            if (strength <= 20) {
                strengthClass = 'bg-danger';
                strengthMessage = 'Very Weak';
            } else if (strength <= 40) {
                strengthClass = 'bg-warning';
                strengthMessage = 'Weak';
            } else if (strength <= 60) {
                strengthClass = 'bg-info';
                strengthMessage = 'Medium';
            } else if (strength <= 80) {
                strengthClass = 'bg-primary';
                strengthMessage = 'Strong';
            } else {
                strengthClass = 'bg-success';
                strengthMessage = 'Very Strong';
            }
        } else {
            strengthMessage = 'Password strength';
        }
        
        // Update UI
        strengthIndicator.attr('class', 'strength-indicator ' + strengthClass);
        strengthIndicator.css('width', strength + '%');
        strengthText.text(strengthMessage);
        
        // Check if passwords match
        checkPasswordsMatch();
    });
    
    // Check if passwords match
    password2Field.on('input', function() {
        checkPasswordsMatch();
    });
    
    function checkPasswordsMatch() {
        const password1 = password1Field.val();
        const password2 = password2Field.val();
        
        if (password2.length > 0) {
            if (password1 === password2) {
                passwordMatchFeedback.text('Passwords match');
                passwordMatchFeedback.removeClass('invalid').addClass('valid');
            } else {
                passwordMatchFeedback.text('Passwords do not match');
                passwordMatchFeedback.removeClass('valid').addClass('invalid');
            }
        } else {
            passwordMatchFeedback.text('');
            passwordMatchFeedback.removeClass('valid invalid');
        }
        
        // Enable/disable submit button based on validation
        validateForm();
    }
    
    function validateForm() {
        const password1 = password1Field.val();
        const password2 = password2Field.val();
        const allRequirementsMet = 
            patterns.length.test(password1) && 
            patterns.uppercase.test(password1) && 
            patterns.lowercase.test(password1) && 
            patterns.number.test(password1) && 
            patterns.special.test(password1);
        
        if (allRequirementsMet && password1 === password2 && password2.length > 0) {
            submitBtn.prop('disabled', false);
        } else {
            submitBtn.prop('disabled', true);
        }
    }
    
    function updateRequirement(element, isValid) {
        if (isValid) {
            element.addClass('valid');
            element.find('i').removeClass('fa-circle').addClass('fa-check-circle');
        } else {
            element.removeClass('valid');
            element.find('i').removeClass('fa-check-circle').addClass('fa-circle');
        }
    }
    
    function setupPasswordToggle(inputSelector, toggleSelector) {
        const toggleBtn = $(toggleSelector);
        const input = $(inputSelector);
        
        toggleBtn.click(function() {
            const type = input.attr('type') === 'password' ? 'text' : 'password';
            input.attr('type', type);
            toggleBtn.find('i').toggleClass('fa-eye fa-eye-slash');
        });
    }
    
    // Form submission
    $('#passwordResetForm').on('submit', function() {
        $('.btn-text').addClass('d-none');
        $('.btn-loader').removeClass('d-none');
        submitBtn.prop('disabled', true);
    });
    
    // Initialize validation on page load
    validateForm();
});
