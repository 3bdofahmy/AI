from .BaseDataModel import BaseDataModel
from .data_schema.project import Project
import os
import csv

class ProjectModel(BaseDataModel):

    def __init__(self):
        super().__init__()

    def create_project(self, project: Project):
        project_dir = self.ensure_project_dir(project.project_id)
        
        chunks_file_path = os.path.join(project_dir, 'chunks.csv')
        
        if not os.path.exists(chunks_file_path):
            with open(chunks_file_path, mode='w', newline='') as file:
                writer = csv.DictWriter(file, fieldnames=["chunk_text", "chunk_metadata", "chunk_order"])
                writer.writeheader()  

        return project

    def get_project_or_create_one(self, project_id: str):
        project_dir = self.ensure_project_dir(project_id)
        
        if not os.path.exists(project_dir):
            new_project = Project(project_id=project_id)
            self.create_project(new_project)
            return new_project
        else:
            return Project(project_id=project_id)

    def get_all_projects(self):
        projects = []
        project_dirs = [d for d in os.listdir(self.app_settings.data_dir) if os.path.isdir(os.path.join(self.app_settings.data_dir, d))]
        
        for project_id in project_dirs:
            projects.append(Project(project_id=project_id))

        return projects
