$(document).ready(function() {
    // Toggle sidebar
    $('.sidebar-toggle, .header-toggle').on('click', function() {
        $('.sidebar').toggleClass('collapsed');
        $('.main').toggleClass('expanded');
        
        // Store sidebar state in localStorage
        localStorage.setItem('sidebar-collapsed', $('.sidebar').hasClass('collapsed'));
    });
    
    // Check localStorage for sidebar state on page load
    if (localStorage.getItem('sidebar-collapsed') === 'true') {
        $('.sidebar').addClass('collapsed');
        $('.main').addClass('expanded');
    }
    
    // Submenu toggle
    $('.has-submenu > .sidebar-link').on('click', function(e) {
        e.preventDefault();
        
        // If sidebar is collapsed, expand it first
        if ($('.sidebar').hasClass('collapsed')) {
            $('.sidebar').removeClass('collapsed');
            $('.main').removeClass('expanded');
            localStorage.setItem('sidebar-collapsed', 'false');
        }
        
        $(this).parent().toggleClass('open');
        $(this).next('.submenu').slideToggle(200);
    });
    
    // Hover effect for collapsed sidebar
    $('.sidebar-item').hover(
        function() {
            if ($('.sidebar').hasClass('collapsed')) {
                $(this).find('.submenu').addClass('hover-show');
            }
        },
        function() {
            if ($('.sidebar').hasClass('collapsed')) {
                $(this).find('.submenu').removeClass('hover-show');
            }
        }
    );
    
    // Initialize any datepickers
    if($.fn.datepicker) {
        $('.datepicker').datepicker({
            format: 'yyyy-mm-dd',
            autoclose: true,
            todayHighlight: true
        });
    }
    
    // Initialize any select2 dropdowns
    if($.fn.select2) {
        $('.select2').select2({
            theme: 'bootstrap4',
        });
    }
    
    // Initialize any datatables
    if($.fn.DataTable) {
        $('.datatable').DataTable({
            responsive: true
        });
    }
    
    // Form validation
    $('.needs-validation').on('submit', function(event) {
        if (this.checkValidity() === false) {
            event.preventDefault();
            event.stopPropagation();
        }
        $(this).addClass('was-validated');
    });
    
    // Calculate leave days when date changes
    $('#id_start_date, #id_end_date').on('change', function() {
        var startDate = $('#id_start_date').val();
        var endDate = $('#id_end_date').val();
        
        if(startDate && endDate) {
            var start = new Date(startDate);
            var end = new Date(endDate);
            var diffTime = Math.abs(end - start);
            var diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24)) + 1;
            
            if(diffDays > 0) {
                $('#id_leave_days').val(diffDays);
            }
        }
    });
    
    // Attendance form: When status changes, show/hide time fields
    $('[id^=id_status_]').on('change', function() {
        var employeeId = $(this).attr('id').split('_')[2];
        var status = $(this).val();
        
        if(status === 'Present') {
            $(`#id_time_in_${employeeId}`).prop('disabled', false);
            $(`#id_time_out_${employeeId}`).prop('disabled', false);
        } else {
            $(`#id_time_in_${employeeId}`).prop('disabled', true);
            $(`#id_time_out_${employeeId}`).prop('disabled', true);
        }
    });
    
    // Initialize tooltips
    $('[data-toggle="tooltip"]').tooltip();
    
    // Initialize popovers
    $('[data-toggle="popover"]').popover();
    
    // Confirm delete
    $('.btn-delete').on('click', function(e) {
        if(!confirm('Are you sure you want to delete this item? This action cannot be undone.')) {
            e.preventDefault();
        }
    });
});
