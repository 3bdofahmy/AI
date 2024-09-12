import csv
import ast
import os
from .BaseDataModel import BaseDataModel
from .data_schema.data_chunk import DataChunk
from pydantic import BaseModel

class ChunkModel(BaseDataModel):

    def __init__(self):
        super().__init__()

    def create_chunk(self, project_id: str, chunk: DataChunk):
        project_dir = self.ensure_project_dir(project_id)
        chunk_file = os.path.join(project_dir, 'chunks.csv')

        file_exists = os.path.isfile(chunk_file)

        with open(chunk_file, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=chunk.model_dump().keys())
            if not file_exists:
                writer.writeheader()  
            writer.writerow(chunk.model_dump())
        
        return chunk
    def get_chunk(self, project_id: str):
        project_dir = self.ensure_project_dir(project_id)
        chunk_file = os.path.join(project_dir, 'chunks.csv')

        with open(chunk_file, mode='r' ,  encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                return DataChunk(**row)
        return None

    def insert_many_chunks(self, project_id: str, chunks: list):
        for chunk in chunks:
            self.create_chunk(project_id, chunk)
        return len(chunks)

    def delete_chunks_by_project_id(self, project_id: str):
        project_dir = self.ensure_project_dir(project_id)
        chunk_file = os.path.join(project_dir, 'chunks.csv')

        if os.path.exists(chunk_file):
            os.remove(chunk_file)
            return True
        return False
    
    # def get_project_chunks(self, project_id: str, page_no: int = 1, page_size: int = 50):
    #     project_dir = self.ensure_project_dir(project_id)
    #     chunk_file = os.path.join(project_dir, 'chunks.csv')

    #     if not os.path.exists(chunk_file):
    #         return []

    #     with open(chunk_file, mode='r', encoding='utf-8') as file:
    #         reader = csv.DictReader(file)
    #         all_chunks = [DataChunk(**row) for row in reader]

    #     start_index = (page_no - 1) * page_size
    #     end_index = start_index + page_size

    
    #     return all_chunks[start_index:end_index]

    def get_project_chunks(self, project_id: str, page_no: int = 1, page_size: int = 50):
        project_dir = self.ensure_project_dir(project_id)
        chunk_file = os.path.join(project_dir, 'chunks.csv')

        if not os.path.exists(chunk_file):
            return []

        all_chunks = []
        with open(chunk_file, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                try:
                    # Parse chunk_metadata string to a dictionary
                    row['chunk_metadata'] = ast.literal_eval(row['chunk_metadata'])
                except (ValueError, SyntaxError):
                    # Handle error in parsing, e.g., skip the row or log the error
                    continue
                # Convert chunk_order to an integer
                row['chunk_order'] = int(row['chunk_order'])
                all_chunks.append(DataChunk(**row))

        start_index = (page_no - 1) * page_size
        end_index = start_index + page_size

        return all_chunks[start_index:end_index]

    

