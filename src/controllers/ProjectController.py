from .BaseController import BaseController
import os
from models import ResponseSignal


class ProjectController(BaseController):
    def __init__(self):
        super().__init__()

    def get_project_path(self, project_id: str):
        project_path = os.path.join(self.file_storage_path, project_id)
        if not os.path.exists(project_path):
            os.makedirs(project_path)
        return project_path