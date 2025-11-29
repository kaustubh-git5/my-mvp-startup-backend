# backend/app/db.py  (production-ready: secretsmanager + local support)
import os
import json
import boto3
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Use provided DATABASE_URL (local dev) or fetch from SecretsManager
DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    # fetch from Secrets Manager
    SECRET_NAME = os.environ.get("RDS_SECRET_NAME", "my-mvp-startup-db/RDS")
    AWS_REGION = os.environ.get("AWS_REGION", "ap-south-1")

    client = boto3.client("secretsmanager", region_name=AWS_REGION)
    secret_value = client.get_secret_value(SecretId=SECRET_NAME)
    secret = json.loads(secret_value["SecretString"])

    user = secret["username"]
    password = secret["password"]
    host = secret["host"]
    port = secret.get("port", 5432)
    dbname = secret.get("database") or secret.get("dbname") or "my-mvp-startup-db"

    DATABASE_URL = f"postgresql://{user}:{password}@{host}:{port}/{dbname}"

# If using sqlite for local dev, SQLAlchemy needs extra arg; otherwise not.
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
