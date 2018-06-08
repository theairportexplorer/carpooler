import json
import urllib.request as urlrequest
from tinydb import (
    TinyDB,
    where,
    Query)
from tinydb.operations import (
    decrement,
    set)
from attendees import (
    Driver,
    Rider)


def WARNING(msg: str):
    print("[WARNING]: {}".format(msg))

class GoogleMap:
    def __init__(self, address: str, api_key: str):
        url = 'https://maps.googleapis.com/maps/api/geocode/json?address={}&key={}'.format(
            address.replace(' ', '+'),
            api_key
        )
        url_get = urlrequest.urlopen(url).read()
        self._g_result = json.loads(url_get)

    @property
    def coord(self) -> tuple:
        if self._g_result['status'] != 'OK':
            WARNING("Failed to retrieve from Google Maps")
            return (0,0)
        lat = self._g_result['results'][0]['geometry']['location']['lat']
        lng = self._g_result['results'][0]['geometry']['location']['lng']
        return (lat, lng)

class CarpoolUsers:
    def __init__(self, dbfile: str, g_api_key: str):
        self._db = TinyDB(dbfile)
        self._key = g_api_key

    def __enter__(self):
        return self

    def __exit__(self):
        self.close()

    def close(self):
        self._db.close()

    def add_new_rider(self, name: str, email: str, address: str):
        rider = {}
        rider['type'] = "rider"
        rider['name'] = name
        rider['email'] = email
        rider['address'] = address
        rider['geo'] = self._get_geo_coordinates(address).coord
        rider['assigned_driver'] = ''
        self._db.insert(rider)

    def add_new_driver(self, name: str, email: str, address: str, passenger_capacity: int):
        driver = {}
        driver['type'] = "driver"
        driver['name'] = name
        driver['email'] = email
        driver['address'] = address
        driver['geo'] = self._get_geo_coordinates(address).coord
        driver['passenger_capacity'] = passenger_capacity
        driver['assigned_riders'] = []
        self._db.insert(driver)

    def remove_person_by_name(self, name: str):
        self._db.remove(where('name') == name)

    def remove_person_by_email(self, email: str):
        self._db.remove(where('email') == email)

    def _get_geo_coordinates(self, address: str) -> GoogleMap:
        return GoogleMap(address, self._key)

    def get_riders_all(self) -> list:
        Person = Query()
        riders = []
        for r in self._db.search(Person.type == "rider"):
            rider = Rider()
            rider.name = r['name']
            rider.address = r['address']
            rider.coord = tuple(r['geo'])
            rider.email = r['email']
            rider.driver = r['assigned_driver']
            riders.append(rider)
        return riders

    def get_riders_unserviced(self) -> list:
        Person = Query()
        riders = []
        unserviced_riders = self._db.search(
            (Person.type == "rider")
            & (Person.assigned_driver == '')
        )
        for r in unserviced_riders:
            rider = Rider()
            rider.name = r['name']
            rider.address = r['address']
            rider.coord = tuple(r['geo'])
            rider.email = r['email']
            rider.driver = r['assigned_driver']
            riders.append(rider)
        return riders

    def get_drivers_all(self) -> list:
        Person = Query()
        drivers = []
        for d in self._db.search(Person.type == "driver"):
            driver = Driver()
            driver.name = d['name']
            driver.address = d['address']
            driver.coord = tuple(d['geo'])
            driver.email = d['email']
            driver.capacity = d['passenger_capacity']
            driver.riders = d['assigned_riders']
            drivers.append(driver)
        return drivers

    def get_drivers_available(self) -> list:
        Person = Query()
        drivers = []
        available_drivers = self._db.search(
            (Person.type == "driver")
            & (Person.passenger_capacity > 0)
        )
        for d in available_drivers:
            driver = Driver()
            driver.name = d['name']
            driver.address = d['address']
            driver.coord = tuple(d['geo'])
            driver.email = d['email']
            driver.capacity = d['passenger_capacity']
            driver.riders = d['assigned_riders']
            drivers.append(driver)
        return drivers

    def get_driver_by_email(self, email: str) -> Driver:
        Person = Query()
        res = self._db.get(Person.email == email)
        if len(res) == 0:
            return None
        driver = Driver()
        driver.name = res['name']
        driver.address = res['address']
        driver.coord = tuple(res['geo'])
        driver.email = res['email']
        driver.capacity = res['passenger_capacity']
        driver.riders = res['assigned_riders']
        return driver

    def get_rider_by_email(self, email: str) -> Rider:
        Person = Query()
        res = self._db.get(Person.email == email)
        if len(res) == 0:
            return None
        rider = Rider()
        rider.name = res['name']
        rider.address = res['address']
        rider.coord = tuple(res['geo'])
        rider.email = res['email']
        rider.driver = res['assigned_driver']
        return rider

    def update_driver(self, driver_email: str, rider_email: str):
        Person = Query()
        driver = self._db.get(Person.email == driver_email)
        assigned_riders = driver['assigned_riders']
        assigned_riders.append(rider_email)
        self._db.update(
            decrement('passenger_capacity'),
            Person.email == driver_email
        )
        self._db.update(
            set('assigned_riders', assigned_riders),
            Person.email == driver_email
        )

    def update_rider(self, rider_email: str, driver_email: str):
        Person = Query()
        self._db.update(
            set('assigned_driver', driver_email),
            Person.email == rider_email
        )

    def get_type_by_email(self, email: str):
        Person = Query()
        res = self._db.get(Person.email == email)
        return res['type']

if __name__ == "__main__":
    pass