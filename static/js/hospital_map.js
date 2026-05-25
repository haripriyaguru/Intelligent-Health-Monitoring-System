/**
 * Hospital Map JavaScript Class
 * Manages hospital location mapping using Leaflet.js and Overpass API
 */

/**
 * Escape HTML special characters to prevent XSS
 */
function escapeHtml(text) {
    if (!text) return "";
    return text
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

class HospitalMap {
    constructor(config) {
        // Configuration
        this.mapElementId = config.mapElementId || 'map';
        this.hospitalsListId = config.hospitalsListId || 'hospitalsList';
        this.hospitalCountId = config.hospitalCountId || 'hospitalCount';
        this.loadingSpinnerId = config.loadingSpinnerId || 'loadingSpinner';
        this.errorAlertId = config.errorAlertId || 'errorAlert';
        this.errorMessageId = config.errorMessageId || 'errorMessage';
        this.noResultsAlertId = config.noResultsAlertId || 'noResultsAlert';
        this.noResultsMessageId = config.noResultsMessageId || 'noResultsMessage';
        this.locationStatusId = config.locationStatusId || 'locationStatus';

        // State
        this.map = null;
        this.userMarker = null;
        this.hospitalMarkers = {};
        this.hospitals = [];
        this.userLatitude = null;
        this.userLongitude = null;
        this.selectedHospitalId = null;

        // Bind methods
        this.init = this.init.bind(this);
        this.getUserLocation = this.getUserLocation.bind(this);
        this.initializeMap = this.initializeMap.bind(this);
        this.fetchHospitals = this.fetchHospitals.bind(this);
        this.displayHospitals = this.displayHospitals.bind(this);
        this.addHospitalMarker = this.addHospitalMarker.bind(this);
        this.displayHospitalsList = this.displayHospitalsList.bind(this);
        this.selectHospital = this.selectHospital.bind(this);
        this.openDirections = this.openDirections.bind(this);
        this.showError = this.showError.bind(this);
        this.hideError = this.hideError.bind(this);
        this.updateLocationStatus = this.updateLocationStatus.bind(this);
        this.useSelectedCity = this.useSelectedCity.bind(this);
        this.updateLocationStatus = this.updateLocationStatus.bind(this);
        this.useSelectedCity = this.useSelectedCity.bind(this);
    }

    /**
     * Initialize the hospital map
     */
    init() {
        console.log("Initializing Hospital Map...");
        this.getUserLocation();
    }

    /**
     * Get user location with fallback
     */
    getUserLocation() {
        console.log("Initializing Hospital Map...");

        this.updateLocationStatus("Fetching location...");

        navigator.geolocation.getCurrentPosition(
            (position) => {
                console.log("Location success:", position);

                const lat = position.coords.latitude;
                const lon = position.coords.longitude;

                this.updateLocationStatus("Using your location");
                this.initializeMap(lat, lon);
            },
            (error) => {
                console.error("Geolocation error:", error);

                let message = "";

                if (error.code === 1) {
                    message = "Permission denied.";
                } else if (error.code === 2) {
                    message = "Location unavailable.";
                } else if (error.code === 3) {
                    message = "Location request timed out.";
                }

                // FALLBACK LOCATION (Chennai)
                const fallbackLat = 13.0827;
                const fallbackLon = 80.2707;

                alert(message + " Showing default location (Chennai).");

                this.updateLocationStatus("Using default location (Chennai)");
                this.initializeMap(fallbackLat, fallbackLon);
            },
            {
                enableHighAccuracy: false,
                timeout: 10000,
                maximumAge: 0
            }
        );
    }

    /**
     * Initialize Leaflet map with given coordinates
     */
    initializeMap(latitude, longitude) {
        // Store coordinates
        this.userLatitude = latitude;
        this.userLongitude = longitude;

        // Create map centered at user location
        this.map = L.map(this.mapElementId).setView(
            [this.userLatitude, this.userLongitude],
            13
        );

        // Add OpenStreetMap tiles
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: 'Map data &copy; OpenStreetMap contributors',
            maxZoom: 19,
            minZoom: 2
        }).addTo(this.map);

        // Add user location marker
        this.userMarker = L.marker(
            [this.userLatitude, this.userLongitude],
            {
                icon: L.icon({
                    iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon.png',
                    iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon-2x.png',
                    shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
                    iconSize: [25, 41],
                    iconAnchor: [12, 41],
                    popupAnchor: [1, -34],
                    shadowSize: [41, 41]
                }),
                title: 'Your Location'
            }
        ).addTo(this.map);

        // Add popup to user marker
        this.userMarker.bindPopup(
            '<div class="hospital-popup"><h6>Your Location</h6><p>You are here</p></div>',
            { maxWidth: 300 }
        );

        console.log('Map initialized successfully at:', this.userLatitude, this.userLongitude);

        // Fetch hospitals after map is ready
        this.fetchHospitals();
    }

    /**
     * Fetch hospitals from backend API
     */
    fetchHospitals() {
        const endpoint = `/api/hospitals?latitude=${this.userLatitude}&longitude=${this.userLongitude}`;

        fetch(endpoint)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`API error: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                console.log('Hospitals data received:', data);

                if (data.success === false) {
                    this.hideLoading();
                    this.showError(data.error || 'Failed to fetch hospitals');
                    return;
                }

                try {
                    this.hospitals = data.hospitals || [];
                    
                    if (this.hospitals.length === 0) {
                        this.showNoResults('No hospitals found within 5km of your location. Try expanding your search area.');
                    } else {
                        this.displayHospitals();
                        this.displayHospitalsList();
                        this.hideError();
                    }
                } catch (renderError) {
                    console.error('Error rendering hospitals:', renderError);
                    this.showError(`Error displaying hospitals: ${renderError.message}`);
                } finally {
                    this.hideLoading();
                }
            })
            .catch(error => {
                console.error('Fetch error:', error);
                this.hideLoading();
                this.showError(`Failed to fetch hospitals: ${error.message}`);
            });
    }

    /**
     * Display hospitals on the map
     */
    displayHospitals() {
        console.log("Displaying hospitals:", this.hospitals);

        // Safety check
        if (!this.hospitals || this.hospitals.length === 0) {
            console.warn("No hospitals found");
            return;
        }

        // Clear existing markers
        Object.values(this.hospitalMarkers).forEach(marker => {
            this.map.removeLayer(marker);
        });
        this.hospitalMarkers = {};

        // Add markers for each hospital
        this.hospitals.forEach((hospital, index) => {
            this.addHospitalMarker(hospital, index);
        });

        // Fit map bounds to show all markers
        if (this.hospitals.length > 0) {
            const group = new L.featureGroup(Object.values(this.hospitalMarkers));
            group.addLayer(this.userMarker);
            this.map.fitBounds(group.getBounds().pad(0.1));
        }
    }

    /**
     * Add a single hospital marker to the map
     */
    addHospitalMarker(hospital, index) {
        // Safety check: validate hospital data
        if (!hospital) {
            console.warn(`Hospital at index ${index} is null or undefined`);
            return;
        }

        if (!hospital.latitude || !hospital.longitude) {
            console.warn(`Hospital ${hospital.name} has invalid coordinates`);
            return;
        }

        const hospitalId = `hospital-${index}`;

        // Create custom hospital icon (red)
        const hospitalIcon = L.icon({
            iconUrl: this.getHospitalIconUrl(),
            iconSize: [25, 41],
            iconAnchor: [12, 41],
            popupAnchor: [1, -34],
            shadowSize: [41, 41]
        });

        // Create marker
        const marker = L.marker(
            [hospital.latitude, hospital.longitude],
            {
                icon: hospitalIcon,
                title: hospital.name
            }
        ).addTo(this.map);

        // Bind popup with hospital info
        const popupContent = `
            <div class="hospital-popup">
                <h6>${escapeHtml(hospital.name)}</h6>
                <p><strong>Distance:</strong> ${hospital.distance_display}</p>
                ${hospital.address ? `<p><i class="bi bi-geo-alt"></i> ${escapeHtml(hospital.address)}</p>` : ''}
                ${hospital.phone && hospital.phone !== 'Not available' ? `<p><i class="bi bi-telephone"></i> ${escapeHtml(hospital.phone)}</p>` : ''}
                <a href="#" class="btn-directions" onclick="hospitalMapInstance.openDirections(${hospital.latitude}, ${hospital.longitude}, '${escapeHtml(hospital.name)}'); return false;" style="margin-top: 10px;">
                    Get Directions
                </a>
            </div>
        `;

        marker.bindPopup(popupContent, { maxWidth: 300 });

        // Add click event to select hospital
        marker.on('click', () => {
            this.selectHospital(index);
            marker.openPopup();
        });

        // Store marker reference
        this.hospitalMarkers[hospitalId] = marker;
    }

    /**
     * Get hospital icon URL (red marker for hospitals)
     */
    getHospitalIconUrl() {
        // Using a red marker icon for hospitals
        return 'data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNSIgaGVpZ2h0PSI0MSIgdmlld0JveD0iMCAwIDI1IDQxIj48cGF0aCBkPSJNMTIuNSAwQzUuNTk3IDAgMCA1LjU5NyAwIDEyLjVjMCA4LjQ2IDEyLjUgMjggMTIuNSAyOHMyLjUgLTEzLjAzIDEyLjUtMjhDMjUgNS41OTcgMjEuOTAzIDAgMTIuNSAweiIgZmlsbD0iI2RjMzU0NSIvPjwvc3ZnPg==';
    }

    /**
     * Display hospitals in the list panel
     */
    displayHospitalsList() {
        const container = document.getElementById(this.hospitalsListId);
        
        if (this.hospitals.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <i class="bi bi-hospital"></i>
                    <p>No hospitals found</p>
                </div>
            `;
            return;
        }

        // Update hospital count
        document.getElementById(this.hospitalCountId).textContent = this.hospitals.length;

        // Build HTML for hospitals list
        let html = '';
        this.hospitals.forEach((hospital, index) => {
            const isActive = this.selectedHospitalId === index ? 'active' : '';
            html += `
                <div class="card m-3 hospital-card ${isActive}" data-index="${index}" onclick="hospitalMapInstance.selectHospital(${index})">
                    <div class="card-body">
                        <h6 class="hospital-name">
                            <i class="bi bi-hospital"></i> ${escapeHtml(hospital.name)}
                        </h6>
                        <div class="hospital-distance">${hospital.distance_display}</div>
                        
                        ${hospital.address ? `<div class="hospital-info"><i class="bi bi-geo-alt"></i> ${escapeHtml(hospital.address)}</div>` : ''}
                        
                        ${hospital.phone && hospital.phone !== 'Not available' ? `<div class="hospital-info"><i class="bi bi-telephone"></i> ${escapeHtml(hospital.phone)}</div>` : ''}
                        
                        ${hospital.opening_hours && hospital.opening_hours !== 'Not available' ? `<div class="hospital-info"><i class="bi bi-clock"></i> ${escapeHtml(hospital.opening_hours)}</div>` : ''}
                        
                        ${hospital.beds && hospital.beds !== 'Not specified' ? `<div class="hospital-info"><i class="bi bi-lungs"></i> Beds: ${escapeHtml(hospital.beds)}</div>` : ''}
                        
                        <button class="btn-directions" onclick="hospitalMapInstance.openDirections(${hospital.latitude}, ${hospital.longitude}, '${escapeHtml(hospital.name)}'); event.stopPropagation();">
                            <i class="bi bi-box-arrow-up-right"></i> Get Directions
                        </button>
                    </div>
                </div>
            `;
        });

        container.innerHTML = html;
    }

    /**
     * Select a hospital and highlight it on the map
     */
    selectHospital(index) {
        // Remove active class from all cards
        document.querySelectorAll('.hospital-card').forEach(card => {
            card.classList.remove('active');
        });

        // Add active class to selected card
        const selectedCard = document.querySelector(`[data-index="${index}"]`);
        if (selectedCard) {
            selectedCard.classList.add('active');
            selectedCard.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        }

        // Update selected ID
        this.selectedHospitalId = index;

        // Open popup for hospital marker
        const hospitalId = `hospital-${index}`;
        if (this.hospitalMarkers[hospitalId]) {
            this.map.setView(
                [this.hospitals[index].latitude, this.hospitals[index].longitude],
                15
            );
            this.hospitalMarkers[hospitalId].openPopup();
        }
    }

    /**
     * Open directions in Google Maps
     */
    openDirections(latitude, longitude, hospitalName) {
        const directionsUrl = `https://www.google.com/maps/dir/?api=1&destination=${latitude},${longitude}`;
        window.open(directionsUrl, '_blank');
        console.log(`Opening directions to ${hospitalName}`);
    }

    /**
     * Show error message
     */
    showError(message) {
        const alertElement = document.getElementById(this.errorAlertId);
        const messageElement = document.getElementById(this.errorMessageId);
        
        if (alertElement && messageElement) {
            messageElement.textContent = message;
            alertElement.style.display = 'block';
        }
    }

    /**
     * Hide error message
     */
    hideError() {
        const alertElement = document.getElementById(this.errorAlertId);
        if (alertElement) {
            alertElement.style.display = 'none';
        }
    }

    /**
     * Show no results message
     */
    showNoResults(message) {
        const alertElement = document.getElementById(this.noResultsAlertId);
        const messageElement = document.getElementById(this.noResultsMessageId);
        
        if (alertElement && messageElement) {
            messageElement.textContent = message;
            alertElement.style.display = 'block';
        }
    }

    /**
     * Show loading spinner
     */
    showLoading() {
        const spinnerElement = document.getElementById(this.loadingSpinnerId);
        if (spinnerElement) {
            spinnerElement.style.display = 'flex';
        }
    }

    /**
     * Hide loading spinner
     */
    hideLoading() {
        const spinnerElement = document.getElementById(this.loadingSpinnerId);
        if (spinnerElement) {
            spinnerElement.style.display = 'none';
        }
    }

    /**
     * Update location status message
     */
    updateLocationStatus(message) {
        const statusElement = document.getElementById(this.locationStatusId);
        if (statusElement) {
            statusElement.textContent = message;
            statusElement.className = 'alert alert-info';
            statusElement.style.display = 'block';
        }
    }

    /**
     * Use selected city from dropdown
     */
    useSelectedCity() {
        const value = document.getElementById("citySelect").value;

        if (!value) {
            alert("Please select a city");
            return;
        }

        const [lat, lon] = value.split(",");

        this.updateLocationStatus(`Using selected location (${document.getElementById("citySelect").options[document.getElementById("citySelect").selectedIndex].text})`);
        this.initializeMap(parseFloat(lat), parseFloat(lon));
    }
}

// Global instance for use in HTML event handlers
let hospitalMapInstance;

// Initialize on page load
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function() {
        if (!hospitalMapInstance) {
            hospitalMapInstance = new HospitalMap({
                mapElementId: 'map',
                hospitalsListId: 'hospitalsList',
                hospitalCountId: 'hospitalCount',
                loadingSpinnerId: 'loadingSpinner',
                errorAlertId: 'errorAlert',
                errorMessageId: 'errorMessage',
                noResultsAlertId: 'noResultsAlert',
                locationStatusId: 'locationStatus'
            });
        }
    });
}
