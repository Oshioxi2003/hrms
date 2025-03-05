document.addEventListener('DOMContentLoaded', function() {
    // Initialize Bootstrap tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Initialize Bootstrap popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
    
    // Sidebar Toggle
    const sidebarToggle = document.getElementById('sidebarToggle');
    const sidebar = document.getElementById('sidebar');
    const mainContent = document.querySelector('.main-content');
    
    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', function() {
            sidebar.classList.toggle('collapsed');
            
            // Store sidebar state in localStorage
            if (sidebar.classList.contains('collapsed')) {
                localStorage.setItem('sidebar-collapsed', 'true');
            } else {
                localStorage.setItem('sidebar-collapsed', 'false');
            }
        });
    }
    
    // Check localStorage for sidebar state
    if (localStorage.getItem('sidebar-collapsed') === 'true') {
        sidebar.classList.add('collapsed');
    }
    
    // Mobile Sidebar Toggle
    const mobileToggle = document.querySelector('.header-toggle');
    if (mobileToggle) {
        mobileToggle.addEventListener('click', function() {
            sidebar.classList.add('show');
        });
    }
    
    // Close Sidebar on Mobile
    const sidebarClose = document.querySelector('.sidebar-close');
    if (sidebarClose) {
        sidebarClose.addEventListener('click', function() {
            sidebar.classList.remove('show');
        });
    }
    
    // Close Sidebar when clicking outside on mobile
    document.addEventListener('click', function(event) {
        if (window.innerWidth < 992) {
            if (!sidebar.contains(event.target) && !mobileToggle.contains(event.target) && sidebar.classList.contains('show')) {
                sidebar.classList.remove('show');
            }
        }
    });
    
    // Toggle Submenu
    const menuItems = document.querySelectorAll('.menu-item.has-submenu');
    menuItems.forEach(function(item) {
        const menuLink = item.querySelector('.menu-link');
        const submenu = item.querySelector('.submenu');
        
        menuLink.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Close other submenus
            menuItems.forEach(function(otherItem) {
                if (otherItem !== item && otherItem.classList.contains('open')) {
                    otherItem.classList.remove('open');
                    otherItem.querySelector('.submenu').classList.remove('show');
                }
            });
            
            // Toggle current submenu
            item.classList.toggle('open');
            submenu.classList.toggle('show');
        });
    });
    
    // Sidebar Search Functionality
    const searchInput = document.querySelector('.sidebar .search-input');
    if (searchInput) {
        searchInput.addEventListener('keyup', function() {
            const searchTerm = this.value.toLowerCase();
            const menuItems = document.querySelectorAll('.menu-item');
            const sectionTitles = document.querySelectorAll('.menu-section');
            
            if (searchTerm.length > 0) {
                // Hide section titles during search
                sectionTitles.forEach(section => {
                    section.style.display = 'none';
                });
                
                // Filter menu items
                menuItems.forEach(item => {
                    const menuText = item.querySelector('.menu-text');
                    if (menuText) {
                        const text = menuText.textContent.toLowerCase();
                        
                        if (text.includes(searchTerm)) {
                            item.style.display = 'block';
                            
                            // If it's a submenu item, show its parent
                            if (item.classList.contains('has-submenu')) {
                                item.classList.add('open');
                                const submenu = item.querySelector('.submenu');
                                if (submenu) submenu.classList.add('show');
                            }
                            
                                                        // If it's inside a submenu, show the parent menu
                            const parentSubmenu = item.closest('.submenu');
                            if (parentSubmenu) {
                                parentSubmenu.classList.add('show');
                                const parentItem = parentSubmenu.closest('.menu-item');
                                if (parentItem) {
                                    parentItem.classList.add('open');
                                    parentItem.style.display = 'block';
                                }
                            }
                        } else {
                            // Check if any children match
                            const submenuItems = item.querySelectorAll('.submenu-item');
                            let hasMatch = false;
                            
                            submenuItems.forEach(subItem => {
                                const subText = subItem.textContent.toLowerCase();
                                if (subText.includes(searchTerm)) {
                                    hasMatch = true;
                                    subItem.style.display = 'block';
                                } else {
                                    subItem.style.display = 'none';
                                }
                            });
                            
                            if (hasMatch) {
                                item.style.display = 'block';
                                item.classList.add('open');
                                const submenu = item.querySelector('.submenu');
                                if (submenu) submenu.classList.add('show');
                            } else {
                                item.style.display = 'none';
                            }
                        }
                    }
                });
            } else {
                // Reset everything
                sectionTitles.forEach(section => {
                    section.style.display = 'block';
                });
                
                menuItems.forEach(item => {
                    item.style.display = 'block';
                    item.classList.remove('open');
                    
                    const submenu = item.querySelector('.submenu');
                    if (submenu) {
                        submenu.classList.remove('show');
                    }
                    
                    const submenuItems = item.querySelectorAll('.submenu-item');
                    submenuItems.forEach(subItem => {
                        subItem.style.display = 'block';
                    });
                });
                
                // Re-open active submenu
                const activeItems = document.querySelectorAll('.menu-item.active, .submenu-item.active');
                activeItems.forEach(item => {
                    const parentMenu = item.closest('.menu-item.has-submenu');
                    if (parentMenu) {
                        parentMenu.classList.add('open');
                        const submenu = parentMenu.querySelector('.submenu');
                        if (submenu) submenu.classList.add('show');
                    }
                });
            }
        });
    }
    
    // Highlight active menu based on current URL
    const currentPath = window.location.pathname;
    const menuLinks = document.querySelectorAll('.menu-link, .submenu-link');
    
    menuLinks.forEach(link => {
        const href = link.getAttribute('href');
        if (href && href !== '#' && currentPath.includes(href)) {
            // Add active class
            link.closest('.menu-item, .submenu-item').classList.add('active');
            
            // If it's a submenu item, open its parent menu
            const parentMenu = link.closest('.menu-item.has-submenu');
            if (parentMenu) {
                parentMenu.classList.add('open');
                const submenu = parentMenu.querySelector('.submenu');
                if (submenu) submenu.classList.add('show');
            }
        }
    });
    
    // Form validation
    const forms = document.querySelectorAll('.needs-validation');
    Array.from(forms).forEach(form => {
        form.addEventListener('submit', event => {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });
    
    // Date range picker initialization
    if (typeof daterangepicker !== 'undefined') {
        const dateRangePickers = document.querySelectorAll('.daterangepicker-input');
        dateRangePickers.forEach(picker => {
            new daterangepicker(picker, {
                opens: 'left',
                locale: {
                    format: 'YYYY-MM-DD'
                }
            });
        });
    }
    
    // DataTable initialization
    if (typeof $.fn.DataTable !== 'undefined') {
        $('.datatable').DataTable({
            responsive: true,
            language: {
                search: "",
                searchPlaceholder: "Search...",
                lengthMenu: "_MENU_ records per page",
            },
            dom: '<"datatable-header"fl><"datatable-scroll"t><"datatable-footer"ip>',
            lengthMenu: [10, 25, 50, 100],
            pageLength: 10
        });
    }
    
    // Select2 initialization
    if (typeof $.fn.select2 !== 'undefined') {
        $('.select2').select2({
            width: '100%',
            placeholder: 'Select an option',
            allowClear: true
        });
    }
    
    // Initialize Chart.js elements
    initializeCharts();
    
    // Calculate leave days when date changes
    const startDateInput = document.getElementById('id_start_date');
    const endDateInput = document.getElementById('id_end_date');
    const leaveDaysInput = document.getElementById('id_leave_days');
    
    if (startDateInput && endDateInput && leaveDaysInput) {
        [startDateInput, endDateInput].forEach(input => {
            input.addEventListener('change', () => {
                if (startDateInput.value && endDateInput.value) {
                    const start = new Date(startDateInput.value);
                    const end = new Date(endDateInput.value);
                    const diffTime = Math.abs(end - start);
                    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24)) + 1;
                    
                    if (diffDays > 0) {
                        leaveDaysInput.value = diffDays;
                    }
                }
            });
        });
    }
    
    // Attendance form: When status changes, show/hide time fields
    const statusInputs = document.querySelectorAll('[id^=id_status_]');
    statusInputs.forEach(input => {
        input.addEventListener('change', () => {
            const employeeId = input.id.split('_')[2];
            const status = input.value;
            
            const timeInInput = document.getElementById(`id_time_in_${employeeId}`);
            const timeOutInput = document.getElementById(`id_time_out_${employeeId}`);
            
            if (timeInInput && timeOutInput) {
                if (status === 'Present') {
                    timeInInput.disabled = false;
                    timeOutInput.disabled = false;
                } else {
                    timeInInput.disabled = true;
                    timeOutInput.disabled = true;
                }
            }
        });
    });
    
    // Confirm delete
    const deleteButtons = document.querySelectorAll('.btn-delete');
    deleteButtons.forEach(button => {
        button.addEventListener('click', e => {
            if (!confirm('Are you sure you want to delete this item? This action cannot be undone.')) {
                e.preventDefault();
            }
        });
    });
    
    // Password visibility toggle
    const passwordToggles = document.querySelectorAll('.password-toggle');
    passwordToggles.forEach(toggle => {
        toggle.addEventListener('click', () => {
            const input = toggle.previousElementSibling;
            const type = input.getAttribute('type') === 'password' ? 'text' : 'password';
            input.setAttribute('type', type);
            
            // Change icon
            toggle.innerHTML = type === 'password' ? 
                '<i class="fas fa-eye"></i>' : 
                '<i class="fas fa-eye-slash"></i>';
        });
    });
    
    // File input preview
    const fileInputs = document.querySelectorAll('.custom-file-input');
    fileInputs.forEach(input => {
        input.addEventListener('change', () => {
            const label = input.nextElementSibling;
            const fileName = input.files[0]?.name || 'Choose file';
            label.textContent = fileName;
            
            // Image preview
            const preview = document.querySelector(`#${input.id}-preview`);
            if (preview && input.files[0]) {
                const reader = new FileReader();
                reader.onload = e => {
                    preview.src = e.target.result;
                    preview.style.display = 'block';
                };
                reader.readAsDataURL(input.files[0]);
            }
        });
    });
    
    // Notification read status
    const notificationItems = document.querySelectorAll('.notification-item');
    notificationItems.forEach(item => {
        item.addEventListener('click', () => {
            item.classList.remove('unread');
            
            // Update badge counter
            const container = item.closest('.dropdown-notifications');
            const badge = container.previousElementSibling.querySelector('.badge-counter');
            let count = parseInt(badge.textContent);
            
            if (count > 0) {
                count--;
                badge.textContent = count > 0 ? count : '';
                
                if (count === 0) {
                    badge.style.display = 'none';
                }
            }
        });
    });
});

// Initialize Chart.js elements
function initializeCharts() {
    // Attendance Chart
    const attendanceChart = document.getElementById('attendanceChart');
    if (attendanceChart) {
        new Chart(attendanceChart, {
            type: 'doughnut',
            data: {
                labels: ['Present', 'On Leave', 'Absent'],
                datasets: [{
                    data: [
                        parseInt(attendanceChart.getAttribute('data-present') || 0),
                        parseInt(attendanceChart.getAttribute('data-leave') || 0),
                        parseInt(attendanceChart.getAttribute('data-absent') || 0)
                    ],
                    backgroundColor: ['#0abb87', '#ffab00', '#f64e60'],
                    hoverBackgroundColor: ['#08a376', '#e69b00', '#e63e4f'],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                cutout: '75%',
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const label = context.label || '';
                                const value = context.raw || 0;
                                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                const percentage = Math.round((value / total) * 100);
                                return `${label}: ${value} (${percentage}%)`;
                            }
                        }
                    }
                }
            }
        });
    }
    
    // Department Distribution Chart
    const departmentChart = document.getElementById('departmentChart');
    if (departmentChart) {
        const labels = JSON.parse(departmentChart.getAttribute('data-labels') || '[]');
        const values = JSON.parse(departmentChart.getAttribute('data-values') || '[]');
        
        new Chart(departmentChart, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Employees',
                    data: values,
                    backgroundColor: '#4361ee',
                    borderColor: '#3251d4',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            precision: 0
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: false
                    }
                }
            }
        });
    }
    
    // Monthly Attendance Trend
    const attendanceTrendChart = document.getElementById('attendanceTrendChart');
    if (attendanceTrendChart) {
        const labels = JSON.parse(attendanceTrendChart.getAttribute('data-labels') || '[]');
        const present = JSON.parse(attendanceTrendChart.getAttribute('data-present') || '[]');
        const absent = JSON.parse(attendanceTrendChart.getAttribute('data-absent') || '[]');
        const leave = JSON.parse(attendanceTrendChart.getAttribute('data-leave') || '[]');
        
        new Chart(attendanceTrendChart, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [
                    {
                        label: 'Present',
                        data: present,
                        borderColor: '#0abb87',
                        backgroundColor: 'rgba(10, 187, 135, 0.1)',
                        fill: true,
                        tension: 0.4
                    },
                    {
                        label: 'Absent',
                        data: absent,
                        borderColor: '#f64e60',
                        backgroundColor: 'rgba(246, 78, 96, 0.1)',
                        fill: true,
                        tension: 0.4
                    },
                    {
                        label: 'On Leave',
                        data: leave,
                        borderColor: '#ffab00',
                        backgroundColor: 'rgba(255, 171, 0, 0.1)',
                        fill: true,
                        tension: 0.4
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            precision: 0
                        }
                    }
                },
                plugins: {
                    tooltip: {
                        mode: 'index',
                        intersect: false
                    }
                }
            }
        });
    }
}

// Responsive handling
window.addEventListener('resize', function() {
    const sidebar = document.getElementById('sidebar');
    
    if (window.innerWidth < 992) {
        sidebar.classList.remove('collapsed');
        sidebar.classList.remove('show');
    }
});
