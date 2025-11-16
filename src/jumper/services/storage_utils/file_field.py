from pathlib import Path
import uuid

class FileFieldPathFactory:
    def __init__(self, base_path: str, allowed_extensions: list[str] = None):
        self.base_path = base_path
        self.allowed_extensions = allowed_extensions or []

    def build_instance_path(self, instance, filename):
        """Generate file path for FileField."""
        ext = Path(filename).suffix.lower().lstrip(".")
        if self.allowed_extensions and ext not in self.allowed_extensions:
            raise ValueError(f"File extension not allowed: {ext}")
        unique_id = uuid.uuid4().hex
        return f"{self.base_path}/{instance.id}/{unique_id}.{ext}"

    def get_temporary_path(self, instance_id: int) -> str:
        """Generate temporary file path."""
        return f"{self.base_path}/tmp/{instance_id}/tmp"
