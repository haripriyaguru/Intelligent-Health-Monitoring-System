"""
Hospital Locator Service
Uses Overpass API (OpenStreetMap) to find nearby hospitals
"""

import requests
import math
from typing import List, Dict, Tuple

# Overpass API endpoint
OVERPASS_API_URL = "https://overpass-api.de/api/interpreter"

# Maximum number of hospitals to return
MAX_HOSPITALS = 15
# Search radius in meters
SEARCH_RADIUS = 5000


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate distance between two points on Earth using Haversine formula
    
    Args:
        lat1, lon1: User's latitude and longitude
        lat2, lon2: Hospital's latitude and longitude
    
    Returns:
        Distance in kilometers
    """
    # Earth's radius in kilometers
    R = 6371.0
    
    # Convert degrees to radians
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)
    
    # Differences
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    
    # Haversine formula
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2) ** 2
    c = 2 * math.asin(math.sqrt(a))
    distance = R * c
    
    return round(distance, 2)


def parse_hospital_data(elements: List[Dict]) -> List[Dict]:
    """
    Parse Overpass API response and extract hospital information
    
    Args:
        elements: List of elements from Overpass API response
    
    Returns:
        List of parsed hospital data
    """
    hospitals = []
    
    for element in elements:
        if element.get('type') != 'node':
            continue
        
        tags = element.get('tags', {})
        
        # Skip if not a hospital
        if tags.get('amenity') != 'hospital':
            continue
        
        hospital = {
            'name': tags.get('name', 'Hospital'),
            'latitude': element.get('lat'),
            'longitude': element.get('lon'),
            'address': tags.get('addr:street', 'Address not available'),
            'phone': tags.get('phone', 'Not available'),
            'website': tags.get('website', ''),
            'opening_hours': tags.get('opening_hours', 'Not available'),
            'beds': tags.get('beds', 'Not specified'),
        }
        
        hospitals.append(hospital)
    
    return hospitals


def get_nearby_hospitals(latitude: float, longitude: float) -> Dict:
    """
    Fetch nearby hospitals using Overpass API
    
    Args:
        latitude: User's latitude
        longitude: User's longitude
    
    Returns:
        Dictionary containing list of hospitals and status information
    """
    try:
        # Build Overpass QL query
        # This query finds all hospital nodes within 5000 meters of the user's location
        overpass_query = f"""
        [out:json];
        node["amenity"="hospital"](around:{SEARCH_RADIUS},{latitude},{longitude});
        out center;
        """
        
        # Make request to Overpass API
        headers = {'User-Agent': 'Health-Assistant/1.0'}
        response = requests.post(
            OVERPASS_API_URL,
            data=overpass_query,
            headers=headers,
            timeout=10
        )
        
        # Check if request was successful
        if response.status_code != 200:
            return {
                'success': False,
                'error': f'Overpass API error: {response.status_code}',
                'hospitals': []
            }
        
        # Parse response
        data = response.json()
        elements = data.get('elements', [])
        
        # Parse hospital data
        hospitals = parse_hospital_data(elements)
        
        # Calculate distances and sort by distance
        for hospital in hospitals:
            hospital['latitude'] = float(hospital['latitude'])
            hospital['longitude'] = float(hospital['longitude'])
            distance = haversine_distance(
                latitude, longitude,
                hospital['latitude'], hospital['longitude']
            )
            hospital['distance'] = distance
            
            # Generate distance display
            if distance < 1:
                hospital['distance_display'] = f"{int(distance * 1000)}m"
            else:
                hospital['distance_display'] = f"{distance}km"
        
        # Sort by distance
        hospitals.sort(key=lambda x: x['distance'])
        
        # Limit to max hospitals
        hospitals = hospitals[:MAX_HOSPITALS]
        
        return {
            'success': True,
            'hospitals': hospitals,
            'count': len(hospitals),
            'location': {
                'latitude': latitude,
                'longitude': longitude
            }
        }
    
    except requests.exceptions.Timeout:
        return {
            'success': False,
            'error': 'API request timed out. Please try again.',
            'hospitals': []
        }
    except requests.exceptions.ConnectionError:
        return {
            'success': False,
            'error': 'Failed to connect to hospital database. Please check your internet connection.',
            'hospitals': []
        }
    except ValueError as e:
        return {
            'success': False,
            'error': f'Invalid coordinates provided: {str(e)}',
            'hospitals': []
        }
    except Exception as e:
        return {
            'success': False,
            'error': f'Error fetching hospitals: {str(e)}',
            'hospitals': []
        }


def validate_coordinates(latitude: float, longitude: float) -> Tuple[bool, str]:
    """
    Validate latitude and longitude values
    
    Args:
        latitude: Latitude value
        longitude: Longitude value
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        lat = float(latitude)
        lon = float(longitude)
        
        if not (-90 <= lat <= 90):
            return False, "Latitude must be between -90 and 90"
        
        if not (-180 <= lon <= 180):
            return False, "Longitude must be between -180 and 180"
        
        return True, ""
    
    except (ValueError, TypeError):
        return False, "Invalid coordinate format"
