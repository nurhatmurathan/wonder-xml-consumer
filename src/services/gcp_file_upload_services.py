import logging
from botocore.exceptions import ClientError

from src.config import settings


class GCPUploadService:
    def __init__(self):
        self.bucket_name = settings.GCP_BUCKET_NAME
        self.gcp_endpoint_url = settings.GCP_ENDPOINT_URL
        self.client = settings.get_boto3_client

    def upload_xml(self, xml_content: str, destination: str) -> str:
        """
        Upload XML content to the specified destination in the Google Cloud Storage bucket.

        :param xml_content: The XML content to upload
        :param destination: The destination path in the bucket
        :return: The URL of the uploaded file
        """
        try:
            self.client.put_object(
                Bucket=self.bucket_name,
                Key=destination,
                Body=xml_content,
                ContentType="application/xml",
                CacheControl="no-store, must-revalidate, max-age=0",
            )

            return f"{self.gcp_endpoint_url}/{self.bucket_name}/{destination}"
        except Exception as exception:
            logging.error(f"Failed to upload XML content: {str(exception)}")
            raise exception

    def download_xml(self, file_name: str) -> str:
        """
        Download XML content from the specified file in the Google Cloud Storage bucket.

        :param file_name: The path of the file in the bucket
        :return: The content of the XML file as a string
        """
        try:
            response = self.client.get_object(Bucket=self.bucket_name, Key=file_name)

            xml_content = response["Body"].read().decode("utf-8")
            return xml_content
        except ClientError as boto_exception:
            if boto_exception.response["Error"]["Code"] == "NoSuchKey":

                logging.error(f"File not found: gs://{self.bucket_name}/{file_name}")
                raise FileNotFoundError(
                    f"The file {file_name} does not exist in the bucket {self.bucket_name}"
                )

            logging.error(f"Failed to download XML content: {str(boto_exception)}")
            raise boto_exception
