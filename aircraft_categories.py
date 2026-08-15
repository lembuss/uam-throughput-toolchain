
class Aircraft:
    def __init__(self, name, classification, category):
        self.name = name
        self.classification = classification
        self.category = category
        #self.arrival = arrival

class AircraftCatalog:
    def __init__(self):
        self.aircraft_list = []

    def add_aircraft(self, name, classification, category):
        aircraft = Aircraft(name, classification, category)
        self.aircraft_list.append(aircraft)

    def get_aircraft_by_category(self, category):
        matching_aircraft = []
        for aircraft in self.aircraft_list:
            if aircraft.category == category:
                matching_aircraft.append(aircraft)
        return matching_aircraft
    
    def get_category_by_aircraft(self, aircraft_name):
        for aircraft in self.aircraft_list:
            if aircraft.name == aircraft_name:
                return aircraft.category
        return None

    def get_class_by_aircraft(self, aircraft_name):
        for aircraft in self.aircraft_list:
            if aircraft.name == aircraft_name:
                return aircraft.classification
        return None
    
    def display_all_aircraft(self):
        for aircraft in self.aircraft_list:
            print(f"Name: {aircraft.name}, Class: {aircraft.classification}, Category: {aircraft.category}")

class Category:
    def __init__(self, separation):
        self.name = self.__class__.__name__
        self.separation = separation
        
class CAT_A(Category):
    def __init__(self):
        separation = 8 # wake turbulence separation distance in nm

        super().__init__(separation)

class CAT_B(Category):
    def __init__(self):
        separation = 7 # wake turbulence separation distance in nm

        super().__init__(separation)

class CAT_C(Category):
    def __init__(self):
        separation = 6 # wake turbulence separation distance in nm

        super().__init__(separation)

class CAT_D(Category):
    def __init__(self):
        separation = 5 # wake turbulence separation distance in nm

        super().__init__(separation)

class CAT_E(Category):
    def __init__(self):
        separation = 4 # wake turbulence separation distance in nm

        super().__init__(separation)

class CAT_F(Category):
    def __init__(self):
        separation = 3 # wake turbulence separation distance in nm

        super().__init__(separation)