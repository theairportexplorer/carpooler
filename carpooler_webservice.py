#! python3

from flask import (
    Flask,
    request,
    render_template
)
import yaml
from tinydb import (
    TinyDB,
    Query
)
from attendees import (
    Driver,
    Rider
)
import os

with open('carpooler_config.yml', 'r') as fd:
    CONFIG = yaml.load(fd)
_DBFILE = CONFIG['carpool']
_DB = TinyDB(_DBFILE)

app = Flask("carpooler")


def _print_driver(d: Driver):
    return "Your assigned riders' email(s): " + ", ".join(d.riders)


def _print_rider(r: Rider):
    return "Your assigned driver's email: {}".format(r.driver)


@app.errorhandler(404)
def handle_404(e):
    return render_template("page_not_found.html")


@app.route("/")
def main_page():
    return render_template("carpooler.html", output="")


@app.route("/", methods=["POST"])
def main_page_post():
    email = request.form["text"]
    Person = Query()
    res = _DB.get(Person.email == email)
    if res is None:
        return render_template("carpooler.html", output="{} not found".format(email))
    ptype = res["type"]
    if ptype == "driver":
        res = _DB.get(Person.email == email)
        driver = Driver()
        driver.name = res['name']
        driver.address = res['address']
        driver.coord = tuple(res['geo'])
        driver.email = res['email']
        driver.capacity = res['passenger_capacity']
        driver.riders = res['assigned_riders']
        return render_template("carpooler.html", output=_print_driver(driver))
    elif ptype == "rider":
        res = _DB.get(Person.email == email)
        rider = Rider()
        rider.name = res['name']
        rider.address = res['address']
        rider.coord = tuple(res['geo'])
        rider.email = res['email']
        rider.driver = res['assigned_driver']
        return render_template("carpooler.html", output=_print_rider(rider))
    return render_template("carpooler.html", output="Unknown internal error")


def main():
    port = int(os.environ.get("PORT", 80))
    app.run(host='0.0.0.0', port=port, threaded=True)


if __name__ == "__main__":
    main()