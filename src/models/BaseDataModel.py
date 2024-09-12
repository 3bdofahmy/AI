import os
from helpers.config import get_settings

class BaseDataModel:
    
    def __init__(self):
        self.app_settings = get_settings()
        self.base_dir = os.path.dirname( os.path.dirname(__file__) )


    def ensure_project_dir(self, project_id: str) -> str:

        project_dir = os.path.join(
            self.base_dir,
            "projects_data",
            project_id 
        )

        if not os.path.exists(project_dir):
            os.makedirs(project_dir)
        
        return project_dir  