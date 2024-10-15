from typing import Optional, BinaryIO
from supabase_py_async import AsyncClient

import uuid
import logging


logger = logging.getLogger(__name__)

class StorageBase:
    def __init__(self, bucket_name: str = "knowledge"):
        self.bucket_name = bucket_name

    async def upload_file(self, db: AsyncClient, file: BinaryIO, content_type: Optional[str] = None) -> str:
        logger.info(f"upload_file {file} / content_type : {content_type}")
        """
        Uploads a file to the Supabase storage and returns its public URL.

        Args:
            db (AsyncClient): The Supabase client instance.
            file (BinaryIO): The file object to be uploaded.
            content_type (Optional[str]): The content type of the file (e.g., 'image/png').

        Returns:
            str: The public URL of the uploaded file.
        """
        file_name = f"{uuid.uuid4()}"  # Generate a unique file name
        options = {"content_type": content_type} if content_type else None

        await db.storage.from_(self.bucket_name).upload(file_name, file, options)

        # Get and return the public URL of the uploaded file
        return db.storage.from_(self.bucket_name).get_public_url(file_name)

    async def delete_file(self, db: AsyncClient, file_url: str) -> None:
        """
        Deletes a file from the Supabase storage using its public URL.

        Args:
            db (AsyncClient): The Supabase client instance.
            file_url (str): The public URL of the file to be deleted.
        """
        file_name = file_url.split('/')[-1]  # Extract file name from URL
        await db.storage.from_(self.bucket_name).remove([file_name])

storage = StorageBase()