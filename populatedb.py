from app import app, db
from app.irsystem.models.tea import *

if not Tea.query.get(1):
    print "No tea in database"
    import csv
    with open("./data/scraper/clean_data.csv", "rb") as csvfile:
        reader = csv.reader(csvfile)
        header = next(reader)
        tea_data = {}
        i = 1
        for row in reader:
            tea_data = {key: data for key, data in zip(header, row)}
            tea = Tea(**tea_data)
            db.session.add(tea)
            db.session.commit()
            i += 1
            print row[1]
        print i
else:
    print "Database already has teas"