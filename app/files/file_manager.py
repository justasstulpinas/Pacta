class FileManager:
    @staticmethod
    def generate_filename(submission_id: int, extension: str) -> str:
        return f"contract_{submission_id}.{extension}"