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
    
    // Sidebar Toggle in Header (Mobile)
    const headerToggle = document.getElementById('sidebarToggle');
    const sidebar = document.getElementById('sidebar');
    const mainContent = document.querySelector('.main-content');
    
    if (headerToggle) {
        headerToggle.addEventListener('click', function() {
            if (window.innerWidth < 992) {
                sidebar.classList.toggle('show');
            } else {
                sidebar.classList.toggle('collapsed');
                
                // Store sidebar state in localStorage
                if (sidebar.classList.contains('collapsed')) {
                    localStorage.setItem('sidebar-collapsed', 'true');
                } else {
                    localStorage.setItem('sidebar-collapsed', 'false');
                }
            }
        });
    }
    
    // Sidebar Collapse Button (Desktop)
    const sidebarCollapseBtn = document.getElementById('sidebarCollapseBtn');
    
    if (sidebarCollapseBtn) {
        sidebarCollapseBtn.addEventListener('click', function() {
            sidebar.classList.toggle('collapsed');
            
            // Store sidebar state in localStorage
            if (sidebar.classList.contains('collapsed')) {
                localStorage.setItem('sidebar-collapsed', 'true');
            } else {
                localStorage.setItem('sidebar-collapsed', 'false');
            }
        });
    }
    
    // Check localStorage for sidebar state on page load
    if (localStorage.getItem('sidebar-collapsed') === 'true') {
        sidebar.classList.add('collapsed');
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
            if (!sidebar.contains(event.target) && 
                !headerToggle.contains(event.target) && 
                sidebar.classList.contains('show')) {
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
            
            // If sidebar is collapsed and on desktop, don't toggle submenu on click
            if (sidebar.classList.contains('collapsed') && window.innerWidth >= 992) {
                return;
            }
            
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
        
        // Handle hover for collapsed sidebar
        if (window.innerWidth >= 992) {
            item.addEventListener('mouseenter', function() {
                if (sidebar.classList.contains('collapsed')) {
                    const submenu = this.querySelector('.submenu');
                    if (submenu) {
                        // Position the submenu properly
                        const itemRect = this.getBoundingClientRect();
                        submenu.style.top = itemRect.top + 'px';
                        
                        // Open the submenu
                        this.classList.add('open');
                        submenu.classList.add('show');
                    }
                }
            });
            
            item.addEventListener('mouseleave', function() {
                if (sidebar.classList.contains('collapsed')) {
                    const submenu = this.querySelector('.submenu');
                    if (submenu) {
                        // Close the submenu
                        this.classList.remove('open');
                        submenu.classList.remove('show');
                    }
                }
            });
        }
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
                    
                    // Don't close submenus when clearing search if not in collapsed mode
                    if (!sidebar.classList.contains('collapsed')) {
                        // Keep the active submenu open
                        if (!item.classList.contains('active') && !item.querySelector('.submenu-item.active')) {
                            item.classList.remove('open');
                            const submenu = item.querySelector('.submenu');
                            if (submenu) {
                                submenu.classList.remove('show');
                            }
                        }
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
                    if (parentMenu && !sidebar.classList.contains('collapsed')) {
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
            if (parentMenu && !sidebar.classList.contains('collapsed')) {
                parentMenu.classList.add('open');
                const submenu = parentMenu.querySelector('.submenu');
                if (submenu) submenu.classList.add('show');
            }
        }
    });
    
    // Adjust submenu position on window resize
    window.addEventListener('resize', function() {
        if (sidebar.classList.contains('collapsed') && window.innerWidth >= 992) {
            const openSubmenu = document.querySelector('.menu-item.has-submenu.open .submenu');
            if (openSubmenu) {
                const parentItem = openSubmenu.closest('.menu-item');
                if (parentItem) {
                    const itemRect = parentItem.getBoundingClientRect();
                    openSubmenu.style.top = itemRect.top + 'px';
                }
            }
        } else if (window.innerWidth < 992) {
            // Reset for mobile view
            sidebar.classList.remove('collapsed');
            if (localStorage.getItem('sidebar-collapsed') === 'true') {
                sidebar.classList.remove('show');
            }
        } else {
            // Restore collapsed state on desktop
            if (localStorage.getItem('sidebar-collapsed') === 'true') {
                sidebar.classList.add('collapsed');
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
    
    // Initialize Chart.js elements if they exist
    if (typeof Chart !== 'undefined') {
        initializeCharts();
    }
    
    // Auto-hide alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach(alert => {
        setTimeout(() => {
            const closeBtn = alert.querySelector('.btn-close');
            if (closeBtn) {
                closeBtn.click();
            }
        }, 5000);
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
