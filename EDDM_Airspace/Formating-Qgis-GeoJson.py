# Formating of GeoJson Data exported from Qgis

import json
import os
import glob

# Folder path of GeoJson files exported from Qgis

folder_path = r'C:\Users\reini\LRZ Sync+Share\Masterarbeit-Desktop\QGis\EDDM\GeoJson-from-Qgis'


routes = {
"type": "FeatureCollection",
"features": []
}
        
# Load the GeoJSON file

for filename in glob.glob(os.path.join(folder_path, '*')):
    

        try:
            with open(filename, 'r') as file:
                data = json.load(file)
        except json.decoder.JSONDecodeError:
            print(f"Error: {filename} is not valid JSON. Skipping file...")
            continue
        # Create the GeoJson Object

        route_features = {
            "type": "FeatureCollection",
            "id": data["name"],
            "waypoints": []
        }
        # Extract the Data from the Qgis GeoJson files

        id = 0
    
        for features in data["features"]:
            
            for coordinates in features["geometry"]["coordinates"]:
                #id = id+1
                for coordinate in coordinates:
                    id = id+1
                    feature = {
                
            
                
                            "id": id,
                            "geometry": {
                                "type": "Point",
                                "coordinates": [coordinate[0], coordinate[1]]
                            },
                            "elevation": coordinate[2]

                
                    }


                    route_features["waypoints"].append(feature)    

        routes["features"].append(route_features)


features_str = []
for feature in routes["features"]:
    feature_str = json.dumps(feature, indent=4)
    features_str.append(feature_str)

                
with open("Approaches08.geojson", "w") as f:
    f.write("{\n")
    f.write(f'"type": "FeatureCollection",\n')
    f.write(f'"Routes": [\n')
    f.write(",\n".join(features_str))
    f.write("\n]\n")
    f.write("}")