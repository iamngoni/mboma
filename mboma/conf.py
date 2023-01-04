import os
from decouple import config

AWS_ACCESS_KEY_ID = config("SPACES_KEY")
AWS_SECRET_ACCESS_KEY = config("SPACES_SECRET")
AWS_STORAGE_BUCKET_NAME = "mboma"
AWS_S3_ENDPOINT_URL = "https://modestnerds.ams3.digitaloceanspaces.com"
AWS_S3_OBJECT_PARAMETERS = {"CacheControl": "max-age=86400", "ACL": "public-read"}
AWS_LOCATION = "https://trydjango.nyc3.digitaloceanspaces.com"
DEFAULT_FILE_STORAGE = "mboma.backends.MediaRootS3BotoStorage"
STATICFILES_STORAGE = "mboma.backends.StaticRootS3BotoStorage"
