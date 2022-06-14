import os
from sqlalchemy import select, create_engine
from cdev.resources.simple.relational_db import RelationalDB, db_engine

from .models import Volunteers


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
