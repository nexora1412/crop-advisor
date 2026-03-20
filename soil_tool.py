import requests
import os
from dotenv import load_dotenv
load_dotenv()

def get_soil_data(lat: float, lon: float) -> dict:
    try:
        offset = 0.01
        polygon_coords = [
            [lon - offset, lat - offset],
            [lon + offset, lat - offset],
            [lon + offset, lat + offset],
            [lon - offset, lat + offset],
            [lon - offset, lat - offset]
        ]

        params = {"appid": os.getenv("AGROMONITORING_API_KEY")}
        headers = {"Content-Type": "application/json"}

        polygon_data = {
            "name": "farm_field",
            "geo_json": {
                "type": "Feature",
                "properties": {},
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [polygon_coords]
                }
            }
        }

        r = requests.post(
            "http://agromonitoring.com/agromonitoring/v1/polygons",
            json=polygon_data,
            params=params,
            headers=headers
        )

        polygon_id = r.json().get("id", "")

        soil_r = requests.get(
            "http://agromonitoring.com/agromonitoring/v1/soil",
            params={"polyid": polygon_id, "appid": os.getenv("AGROMONITORING_API_KEY")}
        )

        soil = soil_r.json()
        return {
            "soil_moisture": soil.get("moisture", "N/A"),
            "soil_temp_10cm": soil.get("t10", "N/A"),
            "soil_temp_surface": soil.get("t0", "N/A")
        }

    except Exception as e:
        return {
            "soil_moisture": "N/A",
            "soil_temp_10cm": "N/A",
            "soil_temp_surface": "N/A"
        }