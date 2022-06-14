# Generated as part of Quick Start project template
from email import message
import json
import os
from tokenize import Name
import uuid
from cdev.resources.simple.api import Api
from cdev.resources.simple.xlambda import simple_function_annotation
from cdev import Project as cdev_project
from cdev.resources.simple.static_site import StaticSite

from sqlalchemy import desc, select, create_engine, insert, delete
from cdev.resources.simple.relational_db import RelationalDB, db_engine
from sqlalchemy.orm import Session
from sqlalchemy.engine import Result

# from . import db
from .models import Volunteers

myProject = cdev_project.instance()

VolunteersApi = Api("volunteers")

# ROUTES ======================
list_volunteers_route = VolunteersApi.route("/list_volunteers", "GET")
add_volunteer_route = VolunteersApi.route("/add_volunteer", "POST")
delete_volunteer_route = VolunteersApi.route("/volunteers", "DELETE")
select_volunteer_route = VolunteersApi.route("/volunteers", "GET")


# ======== DATABASE ==========
myDB = RelationalDB(
    "demo_db",  # Cdev Reource name
    db_engine.aurora_postgresql,
    "vol1234",  # User
    "pass1234",  # Pass
    "volunteers"  # DB Name
)

cluster_arn = os.environ.get("CLUSTER_ARN")
secret_arn = os.environ.get("SECRET_ARN")
database_name = os.environ.get("DB_NAME")

engine = create_engine(f'postgresql+auroradataapi://:@/{database_name}',
                       connect_args=dict(aurora_cluster_arn=cluster_arn, secret_arn=secret_arn))

#  ===========================


def is_valid_uuid(value):
    try:
        uuid.UUID(value)

        return True
    except ValueError:
        return False


def serialyze_volunteer(row):
    return {'id': str(row[0]), 'name': str(row[1]), 'description': str(row[2]), 'img': str(row[3])}


@simple_function_annotation("list_volunteers_function", events=[list_volunteers_route.event()],
                            environment={"CLUSTER_ARN": myDB.output.cluster_arn,
                                         "SECRET_ARN": myDB.output.secret_arn, "DB_NAME": myDB.database_name},
                            permissions=[myDB.available_permissions.DATABASE_ACCESS, myDB.available_permissions.SECRET_ACCESS])
def list_volunteers(event, context):
    print("List volunteers...")

    session = Session(engine)

    stmt = select(Volunteers.id, Volunteers.name,
                  Volunteers.description, Volunteers.img)

    rows = session.execute(stmt).fetchall()

    data = []
    for row in rows:
        data.append(serialyze_volunteer(row))

    # result = session.query(stmt)

    return {"status_code": 200, "data": data}


@simple_function_annotation("add_volunteer_function", events=[add_volunteer_route.event()],
                            environment={"CLUSTER_ARN": myDB.output.cluster_arn,
                                         "SECRET_ARN": myDB.output.secret_arn, "DB_NAME": myDB.database_name},
                            permissions=[myDB.available_permissions.DATABASE_ACCESS, myDB.available_permissions.SECRET_ACCESS])
def add_volunteer(event, context):
    print("volunteer add img")

    session = Session(engine)

    # Load the body of the request into a data obj
    data = json.loads(event.get("body"))

    if all(key in data for key in ('name', 'desc', 'img')):
        temp_id = uuid.uuid4()
        stmt = insert(Volunteers).values(id=temp_id, name=data['name'],
                                         description=data['desc'], img=data['img']).returning(Volunteers.id)
        try:
            stmt.compile()
            result = session.execute(stmt)
            session.commit()
            message = json.dumps({"id": str(temp_id)})
            status = 200
        except:
            message = "Error inserting volunteer..."
            status = 400
    else:
        status = 400
        message = 'Error! Keys not acceptable!'

    return {
        "isBase64Encoded": False,
        "statusCode": status,
        "body": message,
        "headers": {
            "content-type": "application/json"
        }
    }


@simple_function_annotation("delete_volunteers_function", events=[delete_volunteer_route.event()],
                            environment={"CLUSTER_ARN": myDB.output.cluster_arn,
                                         "SECRET_ARN": myDB.output.secret_arn, "DB_NAME": myDB.database_name},
                            permissions=[myDB.available_permissions.DATABASE_ACCESS, myDB.available_permissions.SECRET_ACCESS])
def delete_volunteers(event, context):
    print("Deleting volunteer....")

    session = Session(engine)
    data = []
    data = json.loads(event.get("body"))

    if "id" in data:

        stmt = delete(Volunteers).where(Volunteers.id == data["id"])

        try:
            stmt.compile()
            session.execute(stmt)
            session.commit()
            message = json.dumps("Deleted id:" + str(data["id"]))
            status = 200
        except:
            message = "Error deleting volunteer..."
            status = 400
    else:
        message = "Error deleting volunteer...No ID recieved..."
        status = 400

    return {
        "isBase64Encoded": False,
        "statusCode": status,
        "body": message,
        "headers": {
            "content-type": "application/json"
        }
    }


@simple_function_annotation("select_volunteer_function", events=[select_volunteer_route.event()],
                            environment={"CLUSTER_ARN": myDB.output.cluster_arn,
                                         "SECRET_ARN": myDB.output.secret_arn, "DB_NAME": myDB.database_name},
                            permissions=[myDB.available_permissions.DATABASE_ACCESS, myDB.available_permissions.SECRET_ACCESS])
def select_volunteer(event, context):
    print("List volunteers...")

    session = Session(engine)
    data = []
    data = json.loads(event.get("body"))

    if is_valid_uuid(data["id"]):

        stmt = select(Volunteers.id, Volunteers.name,
                      Volunteers.description, Volunteers.img).where(Volunteers.id == data["id"])

        rows = session.execute(stmt).fetchall()
        data = []
        print("ROWS: " + str(len(rows)))
        if len(rows) > 0:
            for row in rows:
                message = serialyze_volunteer(row)
            status = 200
        else:
            message = "No volunteer found!"
            status = 400

        # result = session.query(stmt)

    else:
        message = "Not valid ID..."
        status = 400

    print("Message: " + str(message) + " Status: " + str(status))

    return {
        "isBase64Encoded": False,
        "statusCode": status,
        "body": str(message),
        "headers": {
            "content-type": "application/json"
        }
    }


myFrontend = StaticSite("demofrontend", content_folder="src/content")
test_rontend = StaticSite("testfrontend", content_folder="src/content_test")


myProject.display_output("Base API URL", VolunteersApi.output.endpoint)
myProject.display_output("Routes", VolunteersApi.output.endpoints)
myProject.display_output("Static Site URl", myFrontend.output.site_url)
myProject.display_output("Static Site URl TEST", test_rontend.output.site_url)
