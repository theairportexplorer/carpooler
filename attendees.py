class Attendee:
    def __init__(self):
        self._name = ""
        self._email = ""
        self._coord = (0, 0)
        self._address = ""

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, name: str):
        self._name = name

    @property
    def email(self) -> str:
        return self._email

    @email.setter
    def email(self, email: str):
        self._email = email

    @property
    def coord(self) -> tuple:
        return self._coord

    @coord.setter
    def coord(self, coord: tuple):
        self._coord = coord

    @property
    def address(self) -> str:
        return self._address

    @address.setter
    def address(self, address: str):
        self._address = address


class Driver(Attendee):
    def __init__(self):
        Attendee.__init__(self)
        self._riders = []

    @property
    def riders(self) -> list:
        return self._riders

    @riders.setter
    def riders(self, riders: list):
        self._riders = riders

    def append(self, rider: str):
        self._riders.append(rider)

    def to_dict(self) -> dict:
        return {"Name": self._name,
                "Email": self._email,
                "Coord": self._coord,
                "Address": self._address,
                "Rider": self._riders
                }

    def __str__(self) -> str:
        return str(self.to_dict())


class Rider(Attendee):
    def __init__(self):
        Attendee.__init__(self)
        self._driver = None

    @property
    def driver(self) -> Driver:
        return self._driver

    @driver.setter
    def driver(self, driver: str):
        self._driver = driver

    def to_dict(self) -> dict:
        return {"Name": self._name,
                "Email": self._email,
                "Coord": self._coord,
                "Address": self._address,
                "Driver": self._driver
                }

    def __str__(self) -> str:
        return str(self.to_dict())