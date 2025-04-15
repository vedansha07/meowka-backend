import requests
import time
import random
from datetime import datetime, timedelta

# Configuration
BASE_URL = "http://localhost:3000/api/vehicles"  # Change this to your actual API base URL
VEHICLE_IDS = ["VH002", "VH003"]  # Your vehicle IDs

# Coordinates from your first set (main route)
ROUTE_1 = [
    [73.86193, 18.51463], [73.86181, 18.51295], [73.86316, 18.5129], 
    [73.86434, 18.51239], [73.8658, 18.51182], [73.86763, 18.51103], 
    [73.86827, 18.51077], [73.86852, 18.51125], [73.86642, 18.5122], 
    [73.86662, 18.51263], [73.86729, 18.51273], [73.86782, 18.513], 
    [73.86871, 18.51304], [73.86867, 18.51424], [73.86858, 18.51558], 
    [73.86861, 18.51662], [73.86783, 18.51672], [73.86721, 18.51676], 
    [73.86601, 18.5167], [73.86603, 18.5154], [73.86543, 18.5154], 
    [73.86429, 18.51576], [73.86374, 18.51616], [73.86249, 18.51606], 
    [73.86179, 18.51602], [73.86057, 18.5159], [73.85943, 18.516], 
    [73.85941, 18.51488], [73.85949, 18.51419], [73.85956, 18.51333], 
    [73.85975, 18.51262], [73.86031, 18.51122], [73.86031, 18.51034], 
    [73.86043, 18.51002], [73.86105, 18.51014], [73.86216, 18.51008], 
    [73.86317, 18.51004]
]

# Coordinates from your second set (alternate route)
ROUTE_2 = [
    [73.86186, 18.51311], [73.86307, 18.5129], [73.86461, 18.51225], 
    [73.86616, 18.51168], [73.86779, 18.51103], [73.86826, 18.51054], 
    [73.86688, 18.51034], [73.86543, 18.51059], [73.86388, 18.51067], 
    [73.86242, 18.5105], [73.86208, 18.51042], [73.86211, 18.50834], 
    [73.86241, 18.50647], [73.86265, 18.50558], [73.86379, 18.50571], 
    [73.86492, 18.50606], [73.86613, 18.50608]
]

# Define vehicle routes
VEHICLE_ROUTES = {
    "VH002": ROUTE_1,
    "VH003": ROUTE_2
}

def generate_vehicle_data(vehicle_id, start_time, points, duration_minutes=120):
    """
    Generate tracking data for a vehicle over a specific time period
    
    Args:
        vehicle_id: ID of the vehicle
        start_time: Start time for the data generation
        points: List of coordinate points [longitude, latitude]
        duration_minutes: Total duration to spread the points over in minutes
    
    Returns:
        List of tracking data points with timestamps
    """
    data_points = []
    
    # Calculate time interval between points
    time_interval = duration_minutes * 60 / len(points)
    
    # Base fuel levels and variations
    base_fuel = 75 if vehicle_id == "VH002" else 90
    
    for i, point in enumerate(points):
        # Calculate timestamp for this point
        point_time = start_time + timedelta(seconds=i * time_interval)
        
        # Calculate speed (varying between 0-60 km/h with occasional stops)
        if i > 0 and i < len(points) - 1:
            # Normal movement
            if random.random() < 0.1:  # 10% chance of stopping/slow traffic
                speed = random.uniform(0, 5)
            else:
                speed = random.uniform(15, 60)
        else:
            # Starting or ending point - slower speed
            speed = random.uniform(0, 15)
        
        # Calculate remaining fuel (gradually decreasing)
        fuel_consumption_rate = 0.02  # % per point
        random_variation = random.uniform(-0.5, 0.5)  # Small random variation
        fuel_left = max(0, base_fuel - (i * fuel_consumption_rate) + random_variation)
        
        data_points.append({
            "latitude": point[0],  # Longitude
            "longitude": point[1],  # Latitude
            "speed": round(speed, 2),
            "fuelLeft": round(fuel_left, 2),
            "timestamp": point_time.isoformat()
        })
    
    return data_points

def simulate_one_day():
    """Simulate tracking data for one full day"""
    # Define yesterday's date (to ensure it's "today" in the system)
    yesterday = datetime.now() - timedelta(days=1)
    start_time = yesterday.replace(hour=8, minute=0, second=0, microsecond=0)  # Start at 8 AM
    
    for vehicle_id in VEHICLE_IDS:
        # Morning journey (8 AM - 10 AM)
        route = VEHICLE_ROUTES[vehicle_id]
        morning_data = generate_vehicle_data(
            vehicle_id, 
            start_time, 
            route,
            duration_minutes=120
        )
        
        # Afternoon journey (2 PM - 4 PM)
        afternoon_start = start_time.replace(hour=14, minute=0)
        # Use reversed route for return journey
        afternoon_data = generate_vehicle_data(
            vehicle_id, 
            afternoon_start, 
            list(reversed(route)),
            duration_minutes=120
        )
        
        # Evening journey (6 PM - 8 PM)
        evening_start = start_time.replace(hour=18, minute=0)
        evening_data = generate_vehicle_data(
            vehicle_id, 
            evening_start, 
            route + list(reversed(route[:10])),  # Different route variation
            duration_minutes=120
        )
        
        # Combine all journeys
        all_data = morning_data + afternoon_data + evening_data
        
        print(f"Generated {len(all_data)} tracking points for vehicle {vehicle_id}")
        
        # Submit data to API
        for point in all_data:
            try:
                response = requests.post(
                    f"{BASE_URL}/addinfo/{vehicle_id}", 
                    json=point
                )
                
                if response.status_code == 200:
                    print(f"Successfully added point for {vehicle_id} at {point['timestamp']}")
                else:
                    print(f"Failed to add point: {response.status_code} - {response.text}")
                
                # Small delay to prevent overwhelming the server
                time.sleep(0.2)
                
            except Exception as e:
                print(f"Error adding point: {str(e)}")

if __name__ == "__main__":
    print("Starting vehicle tracking data simulation...")
    simulate_one_day()
    print("Simulation complete!")