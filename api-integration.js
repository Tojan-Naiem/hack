// API Configuration
const API_BASE_URL = 'http://localhost:8000';
const API_ENDPOINT = `${API_BASE_URL}/asteroids/raw`;

// Fetch asteroids data from API
async function fetchAsteroidsData() {
    try {
        const response = await fetch(API_ENDPOINT);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Error fetching asteroids data:', error);
        return null;
    }
}

// Format date to readable string
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' });
}

// Calculate days until impact
function getDaysUntilImpact(dateString) {
    const impactDate = new Date(dateString);
    const today = new Date();
    const diffTime = impactDate - today;
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    return diffDays;
}

// Get asteroid image based on spectral type
function getAsteroidImage(spectralType) {
    const imageMap = {
        'C': 'https://images.unsplash.com/photo-1446776653964-20c1d3a81b06?w=400&h=400&fit=crop&crop=center',
        'S': 'https://images.unsplash.com/photo-1462331940025-496dfbfc7564?w=400&h=400&fit=crop&crop=center',
        'M': 'https://images.unsplash.com/photo-1464802686167-b939a6910659?w=400&h=400&fit=crop&crop=center',
        'B': 'https://images.unsplash.com/photo-1502136969935-8d8eef54d77b?w=400&h=400&fit=crop&crop=center',
        'K': 'https://images.unsplash.com/photo-1462332420958-a05d1e002413?w=400&h=400&fit=crop&crop=center',
        'Q': 'https://images.unsplash.com/photo-1444703686981-a3abbc4d4fe3?w=400&h=400&fit=crop&crop=center',
        'V': 'https://images.unsplash.com/photo-1630142771937-86e30961baca?w=400&h=400&fit=crop&crop=center',
        'A': 'https://images.unsplash.com/photo-1446776877081-d282a0f896e2?w=400&h=400&fit=crop&crop=center',
        'D': 'https://images.unsplash.com/photo-1446776653964-20c1d3a81b06?w=400&h=400&fit=crop&crop=center',
        'P': 'https://images.unsplash.com/photo-1462331940025-496dfbfc7564?w=400&h=400&fit=crop&crop=center',
        'L': 'https://images.unsplash.com/photo-1464802686167-b939a6910659?w=400&h=400&fit=crop&crop=center'
    };
    return imageMap[spectralType] || 'https://images.unsplash.com/photo-1446776653964-20c1d3a81b06?w=400&h=400&fit=crop&crop=center';
}

// ==================== ASTEROIDS.HTML FUNCTIONS ====================

// Filter asteroids by timeframe
function filterAsteroidsByTimeframe(asteroids, timeframeYears) {
    const today = new Date();
    const futureDate = new Date();
    futureDate.setFullYear(today.getFullYear() + timeframeYears);

    return asteroids.filter(asteroid => {
        const asteroidDate = new Date(asteroid.date);
        return asteroidDate >= today && asteroidDate <= futureDate;
    });
}

// Create asteroid card for grid
function createAsteroidCard(asteroid) {
    const card = document.createElement('div');
    card.className = 'asteroid-card';
    
    const image = getAsteroidImage(asteroid.spectral_classification.type_code);
    
    card.innerHTML = `
        <img src="${image}" alt="${asteroid.name}" class="asteroid-image">
        <button class="more-info-btn" onclick="showAsteroidInfo('${asteroid.name}')">
            More Info
        </button>
        <div class="asteroid-name">${asteroid.name}</div>
    `;
    
    return card;
}

// Initialize asteroids page
async function initAsteroidsPage() {
    const asteroidsGrid = document.getElementById('asteroids-grid');
    const timeframeDisplay = document.getElementById('timeframe-display');
    
    if (!asteroidsGrid) return;

    // Get timeframe from URL
    const urlParams = new URLSearchParams(window.location.search);
    const timeframe = parseInt(urlParams.get('timeframe')) || 1;

    // Fetch data
    const data = await fetchAsteroidsData();
    if (!data || !data.data) {
        asteroidsGrid.innerHTML = '<p style="text-align: center; grid-column: 1/-1;">Failed to load asteroids data</p>';
        return;
    }

    // Filter asteroids
    const filteredAsteroids = filterAsteroidsByTimeframe(data.data, timeframe);

    // Update display
    timeframeDisplay.textContent = getDurationText(timeframe);
    asteroidsGrid.innerHTML = '';

    if (filteredAsteroids.length === 0) {
        asteroidsGrid.innerHTML = '<p style="text-align: center; grid-column: 1/-1;">No asteroids found for this timeframe</p>';
        return;
    }

    // Add cards
    filteredAsteroids.forEach(asteroid => {
        const card = createAsteroidCard(asteroid);
        asteroidsGrid.appendChild(card);
    });
}

function getDurationText(duration) {
    switch(duration) {
        case 1: return "Next 1 Year";
        case 5: return "Next 5 Years";
        case 10: return "Next 10 Years";
        case 15: return "Next 15 Years";
        case 50: return "Next 50 Years";
        case 100: return "Next 100 Years";
        default: return "Next 1 Year";
    }
}

function showAsteroidInfo(asteroidName) {
    window.location.href = `details.html?asteroid=${encodeURIComponent(asteroidName)}`;
}

// ==================== DETAILS.HTML FUNCTIONS ====================

// Find asteroid by name
function findAsteroidByName(asteroids, name) {
    return asteroids.find(a => a.name === name);
}

// Update countdown timer
function updateCountdown(targetDate) {
    const now = new Date().getTime();
    const timeLeft = targetDate - now;

    const days = Math.floor(timeLeft / (1000 * 60 * 60 * 24));
    const hours = Math.floor((timeLeft % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
    const minutes = Math.floor((timeLeft % (1000 * 60 * 60)) / (1000 * 60));
    const seconds = Math.floor((timeLeft % (1000 * 60)) / 1000);

    document.getElementById('days').textContent = days.toString().padStart(2, '0');
    document.getElementById('hours').textContent = hours.toString().padStart(2, '0');
    document.getElementById('minutes').textContent = minutes.toString().padStart(2, '0');
    document.getElementById('seconds').textContent = seconds.toString().padStart(2, '0');
}

// Calculate estimated deaths based on energy
function estimateDeaths(energyMT) {
    // Simple formula: deaths increase logarithmically with energy
    return Math.floor(energyMT * 1000);
}

// Initialize details page
async function initDetailsPage() {
    // Get asteroid name from URL
    const urlParams = new URLSearchParams(window.location.search);
    const asteroidName = urlParams.get('asteroid');
    
    if (!asteroidName) {
        alert('No asteroid specified');
        window.location.href = 'asteroids.html';
        return;
    }

    // Fetch data
    const data = await fetchAsteroidsData();
    if (!data || !data.data) {
        alert('Failed to load asteroid data');
        return;
    }

    // Find the specific asteroid
    const asteroid = findAsteroidByName(data.data, asteroidName);
    if (!asteroid) {
        alert('Asteroid not found');
        window.location.href = 'asteroids.html';
        return;
    }

    // Update page with asteroid data
    updateDetailsPage(asteroid);
}

function updateDetailsPage(asteroid) {
    // Update image
    const image = document.querySelector('.card-header img');
    if (image) {
        image.src = getAsteroidImage(asteroid.spectral_classification.type_code);
        image.alt = asteroid.name;
    }

    // Update title
    const title = document.querySelector('.asteroid-data-card h2');
    if (title) {
        title.textContent = asteroid.name;
    }

    // Update basic data
    const dataCard = document.querySelector('.asteroid-data-card > div');
    if (dataCard) {
        dataCard.innerHTML = `
            <div>Diameter: <span>${asteroid.diameter_avg.toFixed(2)} meters</span></div>
            <div>Velocity: <span>${asteroid.velocity_km_s.toFixed(2)} km/s</span></div>
            <div>Miss Distance: <span>${(asteroid.miss_distance_km / 1000000).toFixed(2)}M km</span></div>
            <div>Energy: <span>${asteroid.energy_megatons_TNT.toFixed(2)} MT TNT</span></div>
            <div>Type: <span>${asteroid.spectral_classification.type_name}</span></div>
            <div>Hazardous: <span>${asteroid.is_potentially_hazardous ? 'Yes' : 'No'}</span></div>
        `;
    }

    // Update countdown
    const targetDate = new Date(asteroid.date).getTime();
    updateCountdown(targetDate);
    setInterval(() => updateCountdown(targetDate), 1000);

    // Update simulation data
    updateSimulationData(asteroid);
}

function updateSimulationData(asteroid) {
    // Update info panel
    document.getElementById('asteroid-name').textContent = asteroid.name;
    document.getElementById('energy').textContent = asteroid.energy_megatons_TNT.toFixed(2) + ' MT';
    
    // Random impact location (you can improve this)
    const lat = (Math.random() * 180 - 90).toFixed(4);
    const lng = (Math.random() * 360 - 180).toFixed(4);
    document.getElementById('location').textContent = `${lat}, ${lng}`;
    
    const estimatedDeaths = estimateDeaths(asteroid.energy_megatons_TNT);
    document.getElementById('deaths').textContent = estimatedDeaths.toLocaleString();
    
    // Determine impact type based on energy
    let impactType = 'Rural';
    if (asteroid.energy_megatons_TNT > 100) impactType = 'Urban';
    else if (asteroid.energy_megatons_TNT > 50) impactType = 'Suburban';
    document.getElementById('impact-type').textContent = impactType;

    // Update map simulation with actual data
    if (typeof map !== 'undefined') {
        const impactData = {
            name: asteroid.name,
            energy_megatons: asteroid.energy_megatons_TNT,
            impact_lat: parseFloat(lat),
            impact_lng: parseFloat(lng),
            estimated_deaths: estimatedDeaths,
            seismic: { 
                intensity: "VII-IX", 
                radius_km: Math.min(asteroid.energy_megatons_TNT * 3, 500), 
                duration_sec: 45 
            },
            tsunami: { 
                tsunami_expected: asteroid.energy_megatons_TNT > 50, 
                wave_height_m: "10-50", 
                inundation_radius_km: Math.min(asteroid.energy_megatons_TNT * 6, 1000)
            },
            atmospheric_hazards: { 
                shockwave_radius_km: Math.min(asteroid.energy_megatons_TNT * 2, 310)
            }
        };
        
        // Update global variable if needed
        window.asteroidData = impactData;
    }
}

// ==================== INDEX.HTML FUNCTIONS ====================

// Handle search button click in index.html
function initIndexPage() {
    const searchButton = document.querySelector('.glass-button');
    const timeframeSelect = document.getElementById('timeframe');
    
    if (!searchButton || !timeframeSelect) return;
    
    searchButton.addEventListener('click', function() {
        const selectedValue = timeframeSelect.value;
        
        if (!selectedValue || selectedValue === '') {
            alert('Please select a timeframe');
            return;
        }
        
        // Map the selected value to years
        let timeframeYears;
        switch(selectedValue) {
            case '7': timeframeYears = 1; break;
            case '30': timeframeYears = 5; break;
            case '90': timeframeYears = 10; break;
            case '365': timeframeYears = 20; break;
            case 'custom':
                // Check which option was selected
                const selectedText = timeframeSelect.options[timeframeSelect.selectedIndex].text;
                if (selectedText.includes('50')) timeframeYears = 50;
                else if (selectedText.includes('100')) timeframeYears = 100;
                break;
            default: timeframeYears = 1;
        }
        
        // Navigate to asteroids page with timeframe parameter
        window.location.href = `asteroids.html?timeframe=${timeframeYears}`;
    });
}

// ==================== TRY.HTML FUNCTIONS ====================

// Fix Results Panel Position - Scroll to it when displayed
function showResultsPanel() {
    const resultsPanel = document.getElementById('results-panel');
    if (resultsPanel) {
        resultsPanel.classList.add('active');
        // Smooth scroll to results
        setTimeout(() => {
            resultsPanel.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }, 100);
    }
}

// Enhanced Visual Simulation with better effects
function enhanceVisualSimulation() {
    // Override the original startSimulation if it exists
    if (typeof window.startSimulation !== 'undefined') {
        const originalStartSimulation = window.startSimulation;
        
        window.startSimulation = function() {
            originalStartSimulation();
            
            // Add enhanced visual effects
            setTimeout(() => {
                addEnhancedExplosionEffect();
            }, 500);
        };
    }
}

function addEnhancedExplosionEffect() {
    const overlay = document.getElementById('impact-overlay');
    if (!overlay) return;
    
    // Add multiple explosion layers for more realistic effect
    const markerPoint = map.latLngToContainerPoint([currentLat, currentLng]);
    
    // Create fiery explosion particles
    for (let i = 0; i < 12; i++) {
        setTimeout(() => {
            const particle = document.createElement('div');
            particle.style.position = 'absolute';
            particle.style.left = markerPoint.x + 'px';
            particle.style.top = markerPoint.y + 'px';
            particle.style.width = '10px';
            particle.style.height = '10px';
            particle.style.borderRadius = '50%';
            particle.style.background = i % 2 === 0 ? '#ff4500' : '#ffaa00';
            particle.style.boxShadow = '0 0 20px ' + (i % 2 === 0 ? '#ff4500' : '#ffaa00');
            
            const angle = (i / 12) * Math.PI * 2;
            const distance = 50 + Math.random() * 100;
            particle.style.animation = `particle-explosion-${i} 2s ease-out forwards`;
            
            // Create custom animation
            const styleSheet = document.createElement('style');
            styleSheet.textContent = `
                @keyframes particle-explosion-${i} {
                    0% { transform: translate(-50%, -50%) scale(1); opacity: 1; }
                    100% { 
                        transform: translate(calc(-50% + ${Math.cos(angle) * distance}px), calc(-50% + ${Math.sin(angle) * distance}px)) scale(0);
                        opacity: 0;
                    }
                }
            `;
            document.head.appendChild(styleSheet);
            
            overlay.appendChild(particle);
            
            setTimeout(() => {
                overlay.removeChild(particle);
                document.head.removeChild(styleSheet);
            }, 2000);
        }, i * 50);
    }
}

function initTryPage() {
    enhanceVisualSimulation();
    
    // Override showDemoResults to include scroll
    if (typeof window.showDemoResults !== 'undefined') {
        const originalShowDemoResults = window.showDemoResults;
        
        window.showDemoResults = function(userData) {
            originalShowDemoResults(userData);
            showResultsPanel();
        };
    }
    
    // Override displayResults to include scroll
    if (typeof window.displayResults !== 'undefined') {
        const originalDisplayResults = window.displayResults;
        
        window.displayResults = function(data) {
            originalDisplayResults(data);
            showResultsPanel();
        };
    }
}

// ==================== PAGE INITIALIZATION ====================

// Auto-initialize based on page
document.addEventListener('DOMContentLoaded', function() {
    const currentPage = window.location.pathname.split('/').pop();
    
    if (currentPage.includes('index.html') || currentPage === '') {
        initIndexPage();
    } else if (currentPage.includes('asteroids.html')) {
        initAsteroidsPage();
    } else if (currentPage.includes('details.html')) {
        initDetailsPage();
    }
});