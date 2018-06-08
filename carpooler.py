#! python3

from carpool_users import CarpoolUsers
from carpool_assign import CarpoolAssign
import fire
import yaml

with open('carpooler_config.yml', 'r') as fd:
    CONFIG = yaml.load(fd)
_DBFILE = CONFIG['carpool']
_GMAPS_GEOCODING_FILE = CONFIG['google']['geocoding_file']


class Carpooler:
    def __init__(self):
        self._db = _DBFILE
        with open(_GMAPS_GEOCODING_FILE,'r') as fd:
            self._apikey = fd.read()
        self._carpool = CarpoolUsers(self._db, self._apikey)
        self._assign = CarpoolAssign(self._carpool)

    def driver(self, name, email, address, capacity):
        "Add driver"
        self._carpool.add_new_driver(
            name=name,
            email=email,
            address=address,
            passenger_capacity=capacity
        )

    def rider(self, name, email, address):
        "Add rider"
        self._carpool.add_new_rider(
            name=name,
            email=email,
            address=address
        )

    def delete(self, name=None, email=None):
        if name is not None:
            self._carpool.remove_person_by_name(name)
        if email is not None:
            self._carpool.remove_person_by_email(email)

    def plot(self):
        self._assign.display_locations_all()

    def assign(self):
        self._assign.make_assignments()

    def show(self, email):
        ptype = self._carpool.get_type_by_email(email)
        if ptype == "driver":
            person = self._carpool.get_driver_by_email(email)
        else:
            person = self._carpool.get_rider_by_email(email)
        print(str(person))

if __name__ == "__main__":
    fire.Fire(Carpooler)