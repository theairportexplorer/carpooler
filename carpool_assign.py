from carpool_users import CarpoolUsers
from attendees import (
    Rider,
    Driver
)
import pylab as plt
import math as m
from numpy import inf as infinity


def cart_dist(p1: tuple, p2: tuple):
    return m.sqrt(((p2[0]-p1[0])**2) + ((p2[1]-p1[1])**2))


class SortedRiders:
    def __init__(self, riders: dict):
        '''riders is of type {str : float}'''
        self._riders = riders
        self._farthest_away = ''
        self._get_farthest_away()

    def _get_farthest_away(self):
        starting_dist = 0
        for rider, dist in self._riders.items():
            if dist >= starting_dist:
                dist = starting_dist
                self._farthest_away = rider

    @property
    def next_rider(self) -> str:
        return self._farthest_away

    def pop_next_rider(self):
        self._riders.pop(self._farthest_away)
        self._get_farthest_away()

    def is_empty(self) -> bool:
        return len(self._riders) == 0

    def __str__(self) -> str:
        return str(self._riders)


class CarpoolAssign:
    def __init__(self, dbHandler: CarpoolUsers):
        self._carpool = dbHandler

    def display_locations_all(self):
        drivers = self._carpool.get_drivers_all()
        riders = self._carpool.get_riders_all()

        d_name, d_lat, d_long, r_name, r_lat, r_long = [], [], [], [], [], []
        for d in drivers:
            d_lat.append(d.coord[0])
            d_long.append(d.coord[1])
            d_name.append(d.name)

        for r in riders:
            r_lat.append(r.coord[0])
            r_long.append(r.coord[1])
            r_name.append(r.name)

        dr = plt.scatter(d_long, d_lat, marker='o', label='Drivers')
        ri = plt.scatter(r_long, r_lat, marker='x', label='Riders')
        plt.legend([dr, ri], ['drivers', 'riders'])
        for label, x, y in zip(d_name, d_long, d_lat):
            plt.annotate(label, xy=(x, y))
        for label, x, y in zip(r_name, r_long, r_lat):
            plt.annotate(label, xy=(x, y))
        plt.show()

    def _find_geographic_center(self, coordinates: list) -> tuple:
        '''Calculates the lat/long center of provided list of coordinates'''
        x_coord = 0
        y_coord = 0
        for c in coordinates:
            x_coord += c[0]
            y_coord += c[1]
        return x_coord / len(coordinates), y_coord / len(coordinates)

    def _sort_riders_by_distance(
            self,
            riders: list,
            point_of_reference: tuple) -> SortedRiders:
        '''
        Sorts all riders based on their distance from some focal point
        Returns an object SortedRiders()
        '''
        email_dist_dict = {}
        for r in riders:
            email_dist_dict[r.email] = cart_dist(r.coord, point_of_reference)
        return SortedRiders(email_dist_dict)

    def _find_nearest_driver(
            self,
            drivers: list,
            rider_coord: tuple) -> str:
        '''
        Finds nearest driver for a given rider's coordinate
        and returns with the driver's email
        '''
        shortest_dist = infinity
        driver_email = 'unknown@gmail.com'
        for d in drivers:
            dist = cart_dist(d.coord, rider_coord)
            if dist < shortest_dist:
                shortest_dist = dist
                driver_email = d.email
        return driver_email

    def make_assignments(self):
        drivers = self._carpool.get_drivers_available()
        riders = self._carpool.get_riders_unserviced()

        all_coords = []
        for d in drivers:
            all_coords.append(d.coord)
        for r in riders:
            all_coords.append(r.coord)

        geo_center = self._find_geographic_center(all_coords)
        print("(x,y): {}".format(geo_center))

        sorted_riders = self._sort_riders_by_distance(riders, geo_center)
        print("Sorted Riders: {}".format(str(sorted_riders)))
        print("Next Rider to calculate: {}".format(sorted_riders.next_rider))

        while sorted_riders.is_empty() is not True:
            rider = self._carpool.get_rider_by_email(sorted_riders.next_rider)
            driver_email = self._find_nearest_driver(drivers, rider.coord)
            driver = self._carpool.get_driver_by_email(driver_email)
            print("driver: {}; rider: {}".format(driver.email, rider.email))

            self._carpool.update_driver(driver.email, rider.email)
            self._carpool.update_rider(rider.email, driver.email)
            sorted_riders.pop_next_rider()

            drivers = self._carpool.get_drivers_available()