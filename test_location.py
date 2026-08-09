from services.location_service import LocationService


location = LocationService()

result = location.get_device_location()

print(result)