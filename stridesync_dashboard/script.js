// StrideSync Hockey Dashboard JavaScript

// Global function to open sidebar (available immediately)
window.openSidebarNow = function() {
    console.log('openSidebarNow called!');
    const sidebar = document.getElementById('sidebar');
    const sidebarOverlay = document.getElementById('sidebarOverlay');
    const mainContent = document.getElementById('mainContent');
    
    if (sidebar && sidebarOverlay && mainContent) {
        console.log('Opening sidebar with direct function...');
        sidebar.classList.add('active');
        sidebarOverlay.classList.add('active');
        mainContent.classList.add('sidebar-open');
        document.body.style.overflow = 'hidden';
    } else {
        console.error('Sidebar elements not found!');
        alert('Sidebar elements not found!');
    }
};

// This function is now called from the main DOMContentLoaded listener below
function initializeCharts() {
    // Initialize charts
    initializeBiomechanicsChart();
    
    // Add interactive features
    addInteractivity();
}

function initializeBiomechanicsChart() {
    const ctx = document.getElementById('biomechanicsChart');
    if (!ctx) {
        console.log('Biomechanics chart canvas not found');
        return;
    }
    
    // Destroy existing chart if it exists
    const existingChart = Chart.getChart(ctx);
    if (existingChart) {
        existingChart.destroy();
    }
    
    const biomechanicsChart = new Chart(ctx.getContext('2d'), {
        type: 'radar',
        data: {
            labels: [
                'Knee Flexion',
                'Hip Extension', 
                'Ankle Dorsiflexion',
                'Stance Width',
                'Shoulder Angle',
                'Elbow Angle',
                'Spine Angle',
                'Balance'
            ],
            datasets: [{
                label: 'Current Session',
                data: [85, 72, 68, 80, 75, 82, 78, 88],
                backgroundColor: 'rgba(0, 102, 204, 0.2)',
                borderColor: 'rgba(0, 102, 204, 1)',
                borderWidth: 2,
                pointBackgroundColor: 'rgba(0, 102, 204, 1)',
                pointBorderColor: '#fff',
                pointHoverBackgroundColor: '#fff',
                pointHoverBorderColor: 'rgba(0, 102, 204, 1)'
            }, {
                label: 'Previous Session',
                data: [78, 65, 62, 75, 70, 78, 72, 82],
                backgroundColor: 'rgba(255, 107, 53, 0.2)',
                borderColor: 'rgba(255, 107, 53, 1)',
                borderWidth: 2,
                pointBackgroundColor: 'rgba(255, 107, 53, 1)',
                pointBorderColor: '#fff',
                pointHoverBackgroundColor: '#fff',
                pointHoverBorderColor: 'rgba(255, 107, 53, 1)'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        usePointStyle: true,
                        padding: 20
                    }
                },
                title: {
                    display: true,
                    text: 'Biomechanics Performance',
                    font: {
                        size: 16,
                        weight: 'bold'
                    }
                }
            },
            scales: {
                r: {
                    beginAtZero: true,
                    max: 100,
                    ticks: {
                        stepSize: 20,
                        font: {
                            size: 12
                        }
                    },
                    pointLabels: {
                        font: {
                            size: 11,
                            weight: 'bold'
                        }
                    }
                }
            },
            elements: {
                point: {
                    radius: 4,
                    hoverRadius: 6
                }
            }
        }
    });
}

function initializeTrendsChart() {
    const ctx = document.getElementById('trendsChart');
    if (!ctx) {
        console.log('Trends chart canvas not found');
        return;
    }
    
    // Destroy existing chart if it exists
    const existingChart = Chart.getChart(ctx);
    if (existingChart) {
        existingChart.destroy();
    }
    
    const trendsChart = new Chart(ctx.getContext('2d'), {
        type: 'line',
        data: {
            labels: ['Week 1', 'Week 2', 'Week 3', 'Week 4'],
            datasets: [{
                label: 'Speed',
                data: [75, 78, 82, 85],
                borderColor: 'rgba(0, 102, 204, 1)',
                backgroundColor: 'rgba(0, 102, 204, 0.1)',
                borderWidth: 2,
                fill: true,
                tension: 0.3
            }, {
                label: 'Agility',
                data: [70, 74, 78, 82],
                borderColor: 'rgba(255, 107, 53, 1)',
                backgroundColor: 'rgba(255, 107, 53, 0.1)',
                borderWidth: 2,
                fill: true,
                tension: 0.3
            }, {
                label: 'Recovery',
                data: [85, 83, 80, 78],
                borderColor: 'rgba(220, 53, 69, 1)',
                backgroundColor: 'rgba(220, 53, 69, 0.1)',
                borderWidth: 2,
                fill: true,
                tension: 0.3
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        usePointStyle: true,
                        padding: 2,
                        font: {
                            size: 9
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100,
                    ticks: {
                        stepSize: 100,
                        font: {
                            size: 8
                        }
                    }
                },
                x: {
                    grid: {
                        display: false
                    },
                    ticks: {
                        font: {
                            size: 8
                        }
                    }
                }
            },
            elements: {
                point: {
                    radius: 1,
                    hoverRadius: 3
                }
            },
            layout: {
                padding: {
                    top: 2,
                    bottom: 2
                }
            }
        }
    });
}

function addInteractivity() {
    // Add click handlers for session items
    const sessionItems = document.querySelectorAll('.session-item');
    sessionItems.forEach(item => {
        item.addEventListener('click', function() {
            // Remove active class from all items
            sessionItems.forEach(i => i.classList.remove('active'));
            // Add active class to clicked item
            this.classList.add('active');
            
            // Show session details modal (placeholder)
            showSessionDetails(this);
        });
    });
    
    // Add hover effects for stat rows
    const statRows = document.querySelectorAll('.stat-row');
    statRows.forEach(row => {
        row.addEventListener('mouseenter', function() {
            this.style.transform = 'scale(1.02)';
            this.style.transition = 'transform 0.2s ease';
        });
        
        row.addEventListener('mouseleave', function() {
            this.style.transform = 'scale(1)';
        });
    });
    
    // Add click handler for settings button
    const settingsBtn = document.querySelector('.btn-outline-light');
    settingsBtn.addEventListener('click', function() {
        showSettingsModal();
    });
}

function showSessionDetails(sessionItem) {
    // Get session data from the clicked item
    const sessionTitle = sessionItem.querySelector('h6').textContent;
    const sessionDescription = sessionItem.querySelector('p').textContent;
    const sessionMetrics = sessionItem.querySelector('.session-metrics').innerHTML;
    
    // Create modal content (placeholder for now)
    console.log('Session Details:', {
        title: sessionTitle,
        description: sessionDescription,
        metrics: sessionMetrics
    });
    
    // In a real implementation, you would show a modal with detailed session information
    // including video playback, detailed metrics, coach notes, etc.
}

function showSettingsModal() {
    // Placeholder for settings modal
    console.log('Settings modal would open here');
    
    // In a real implementation, you would show a modal with:
    // - Profile settings
    // - Notification preferences
    // - Privacy settings
    // - Data export options
    // - Account management
}

// Utility functions for data visualization
function updateBiomechanicsMetrics(newData) {
    // Update the biomechanics chart with new data
    const chart = Chart.getChart('biomechanicsChart');
    if (chart) {
        chart.data.datasets[0].data = newData;
        chart.update();
    }
}

function updateTrendsData(newData) {
    // Update the trends chart with new data
    const chart = Chart.getChart('trendsChart');
    if (chart) {
        chart.data.datasets.forEach((dataset, index) => {
            if (newData[index]) {
                dataset.data = newData[index];
            }
        });
        chart.update();
    }
}

// Real-time data updates (simulated)
function simulateRealTimeUpdates() {
    setInterval(() => {
        // Simulate new biomechanics data
        const newBiomechanicsData = [
            Math.floor(Math.random() * 20) + 75, // Knee Flexion
            Math.floor(Math.random() * 15) + 65, // Hip Extension
            Math.floor(Math.random() * 12) + 60, // Ankle Dorsiflexion
            Math.floor(Math.random() * 15) + 70, // Stance Width
            Math.floor(Math.random() * 10) + 70, // Shoulder Angle
            Math.floor(Math.random() * 8) + 75,  // Elbow Angle
            Math.floor(Math.random() * 10) + 70, // Spine Angle
            Math.floor(Math.random() * 10) + 80  // Balance
        ];
        
        updateBiomechanicsMetrics(newBiomechanicsData);
    }, 30000); // Update every 30 seconds
}

// Export functions for external use
window.StrideSyncDashboard = {
    updateBiomechanicsMetrics,
    updateTrendsData,
    showSessionDetails,
    showSettingsModal
};

// Initialize real-time updates (optional)
// simulateRealTimeUpdates();

// Add functionality for new components
function initializeNewComponents() {
    // Add click handlers for drill items
    const drillItems = document.querySelectorAll('.drill-item');
    drillItems.forEach(item => {
        item.addEventListener('click', function() {
            // Toggle active state
            drillItems.forEach(i => i.classList.remove('active'));
            this.classList.add('active');
            
            // Show drill details (placeholder)
            showDrillDetails(this);
        });
    });
    
    // Add click handlers for skeleton overlay controls
    const playBtn = document.querySelector('.overlay-controls .btn-outline-primary');
    const pauseBtn = document.querySelector('.overlay-controls .btn-outline-secondary');
    const fullscreenBtn = document.querySelector('.overlay-controls .btn-outline-info');
    
    if (playBtn) {
        playBtn.addEventListener('click', function() {
            console.log('Play skeleton overlay');
            // In real implementation, this would control video playback
        });
    }
    
    if (pauseBtn) {
        pauseBtn.addEventListener('click', function() {
            console.log('Pause skeleton overlay');
            // In real implementation, this would pause video playback
        });
    }
    
    if (fullscreenBtn) {
        fullscreenBtn.addEventListener('click', function() {
            console.log('Fullscreen skeleton overlay');
            // In real implementation, this would enter fullscreen mode
        });
    }
    
    // Add dismiss functionality for alerts
    const alertCloseButtons = document.querySelectorAll('.alert .btn-close');
    alertCloseButtons.forEach(button => {
        button.addEventListener('click', function() {
            const alert = this.closest('.alert');
            alert.style.opacity = '0';
            setTimeout(() => {
                alert.remove();
            }, 300);
        });
    });
}

function showDrillDetails(drillItem) {
    const drillName = drillItem.querySelector('.drill-name').textContent;
    const drillDescription = drillItem.querySelector('.drill-description').textContent;
    const drillProgress = drillItem.querySelector('.progress-text').textContent;
    
    console.log('Drill Details:', {
        name: drillName,
        description: drillDescription,
        progress: drillProgress
    });
    
    // In a real implementation, you would show a modal with:
    // - Detailed drill instructions
    // - Video demonstrations
    // - Progress tracking
    // - Coach notes
}

// Update the main initialization
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM loaded, initializing dashboard...');
    
    // Show dashboard page by default
    const dashboardPage = document.getElementById('dashboard-page');
    if (dashboardPage) {
        dashboardPage.style.display = 'block';
        dashboardPage.classList.add('active');
        console.log('Dashboard page shown by default');
    }
    
    // Initialize charts and interactive features
    initializeCharts();
    
    // Initialize new components
    initializeNewComponents();
    
    // Initialize sidebar navigation
    initializeSidebar();

});

// Sidebar functionality
function initializeSidebar() {
    const sidebarToggle = document.getElementById('sidebarToggle');
    const sidebar = document.getElementById('sidebar');
    const sidebarClose = document.getElementById('sidebarClose');
    const sidebarOverlay = document.getElementById('sidebarOverlay');
    const mainContent = document.getElementById('mainContent');
    const navLinks = document.querySelectorAll('.sidebar .nav-link');
    const pageContents = document.querySelectorAll('.page-content');
    
    console.log('Sidebar elements found:', {
        sidebarToggle: !!sidebarToggle,
        sidebar: !!sidebar,
        sidebarClose: !!sidebarClose,
        sidebarOverlay: !!sidebarOverlay,
        mainContent: !!mainContent
    });
    
    // Function to open sidebar
    function openSidebar() {
        console.log('Opening sidebar...');
        sidebar.classList.add('active');
        sidebarOverlay.classList.add('active');
        mainContent.classList.add('sidebar-open');
        document.body.style.overflow = 'hidden';
    }
    
    // Function to close sidebar
    function closeSidebar() {
        console.log('Closing sidebar...');
        sidebar.classList.remove('active');
        sidebarOverlay.classList.remove('active');
        mainContent.classList.remove('sidebar-open');
        document.body.style.overflow = '';
    }
    
    // Toggle sidebar - using both click and touchstart for mobile
    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            console.log('=== SIDEBAR TOGGLE CLICKED ===');
            console.log('Event:', e);
            console.log('Button element:', this);
            openSidebar();
        }, { passive: false });
        
        // Add visual feedback on click
        sidebarToggle.addEventListener('mousedown', function() {
            console.log('Button mousedown');
        });
        
        console.log('✅ Sidebar toggle event listener attached successfully');
    } else {
        console.error('❌ Sidebar toggle button not found!');
    }
    
    // Close sidebar
    if (sidebarClose) {
        sidebarClose.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            closeSidebar();
        });
    }
    
    // Close sidebar when clicking overlay
    if (sidebarOverlay) {
        sidebarOverlay.addEventListener('click', function() {
            closeSidebar();
        });
    }
    
    // Close sidebar when pressing Escape key
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && sidebar.classList.contains('active')) {
            closeSidebar();
        }
    });
    
    // Navigation functionality
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            console.log('Navigation link clicked:', this.getAttribute('data-page'));
            
            // Remove active class from all links and pages
            navLinks.forEach(l => l.classList.remove('active'));
            pageContents.forEach(p => {
                p.classList.remove('active');
                p.style.display = 'none';
                p.style.opacity = '0';
                p.style.visibility = 'hidden';
            });
            
            // Add active class to clicked link
            this.classList.add('active');
            
            // Show corresponding page
            const targetPage = this.getAttribute('data-page');
            const targetPageElement = document.getElementById(targetPage + '-page');
            
            console.log('Target page:', targetPage);
            console.log('Target page element:', targetPageElement);
            
            if (targetPageElement) {
                // Hide all pages first with aggressive hiding
                pageContents.forEach(p => {
                    p.classList.remove('active');
                    p.style.display = 'none';
                    p.style.opacity = '0';
                    p.style.visibility = 'hidden';
                    p.style.position = 'static';
                    p.style.zIndex = '0';
                });
                
                // Show target page
                targetPageElement.classList.add('active');
                targetPageElement.style.display = 'block';
                targetPageElement.style.opacity = '1';
                targetPageElement.style.visibility = 'visible';
                targetPageElement.style.position = 'relative';
                targetPageElement.style.zIndex = '1';
                targetPageElement.style.background = 'white';
                
                // Force scroll to absolute top
                window.scrollTo(0, 0);
                document.body.scrollTop = 0;
                document.documentElement.scrollTop = 0;
                
                console.log('Showing page:', targetPage);
                console.log('Page display style:', targetPageElement.style.display);
                console.log('Page classes:', targetPageElement.className);
                
                // If it's the about page, log to confirm content is there
                if (targetPage === 'about') {
                    console.log('About page content length:', targetPageElement.innerHTML.length);
                    console.log('About page content preview:', targetPageElement.innerHTML.substring(0, 200));
                }
            } else {
                console.error('Page not found:', targetPage);
                console.log('Available pages:', document.querySelectorAll('.page-content'));
            }
            
            // Close sidebar after navigation
            closeSidebar();
        });
    });
    
    // Handle form submission
    const contactForm = document.querySelector('#contact-page form');
    if (contactForm) {
        contactForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Get form data
            const firstName = document.getElementById('firstName').value;
            const lastName = document.getElementById('lastName').value;
            const email = document.getElementById('email').value;
            const subject = document.getElementById('subject').value;
            const message = document.getElementById('message').value;
            
            // Show success message (in real implementation, this would send to server)
            alert(`Thank you for your message, ${firstName}! We'll get back to you soon.`);
            
            // Reset form
            this.reset();
        });
    }
    

}
