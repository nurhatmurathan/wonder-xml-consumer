import logging

import boto3
from botocore.client import Config
from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()


class Settings(BaseSettings):
    RMQ_HOST: str
    RMQ_PORT: int
    RMQ_USER: str
    RMQ_PASSWORD: str
    MQ_EXCHANGE: str
    PROD_GCP_BUCKET_NAME: str
    DEV_GCP_BUCKET_NAME: str
    GCP_BUCKET_REGION: str
    GCP_ACCESS_KEY_ID: str
    GCP_SECRET_ACCESS_KEY: str
    GCP_ENDPOINT_URL: str
    MQ_CREATE_USER_XML_QUEUE: str
    MQ_ADD_NEW_OFFER_TO_XML_QUEUE: str
    MQ_DELETE_OFFER_XML_QUEUE: str
    MQ_DISABLE_PICKUP_POINT_XML_QUEUE: str
    MQ_ENABLE_PICKUP_POINT_XML_QUEUE: str
    MQ_SET_CITY_PRICES_XML_QUEUE: str
    MQ_SET_STORE_AVAILABILITY_XML_QUEUE: str
    GCP_STORAGE_XML_FILE_PATH: str

    @property
    def get_boto3_client(self):
        return boto3.client(
            "s3",
            region_name=self.GCP_BUCKET_REGION,
            endpoint_url=self.GCP_ENDPOINT_URL,
            aws_access_key_id=self.GCP_ACCESS_KEY_ID,
            aws_secret_access_key=self.GCP_SECRET_ACCESS_KEY,
            config=Config(signature_version="s3v4"),
        )

    @property
    def rmq_url(self) -> str:
        return f"amqp://{self.RMQ_USER}:{self.RMQ_PASSWORD}@{self.RMQ_HOST}:{self.RMQ_PORT}/"

    @staticmethod
    def configure_logging(level: int = logging.INFO) -> None:
        logging.basicConfig(
            level=level,
            datefmt="%Y-%m-%d %H:%M:%S",
            format="[%(asctime)s.%(msecs)03d] %(funcName)20s %(module)s:%(lineno)d %(levelname)-8s - %(message)s",
        )

    model_config = SettingsConfigDict(env_file="../.env.local")


settings = Settings()
