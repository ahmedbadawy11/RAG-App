from .BaseController import BaseController
from .ProjectController import ProjectController
import os
from langchain_community.document_loaders import TextLoader
from langchain_community.document_loaders import PyMuPDFLoader
from models import ProcessingEnum
from langchain_text_splitters import RecursiveCharacterTextSplitter

class ProcesController(BaseController):
    def __init__(self,project_id:str):
        super().__init__()
        self.project_id=project_id
        self.project_path=ProjectController().get_project_path(project_id=project_id)

    def get_file_extension(self,file_id:str):
        return os.path.splitext(file_id)[-1]
    
    def get_file_loader(self,file_id:str):
        file_extension=self.get_file_extension(file_id=file_id)
        file_path=os.path.join(self.project_path,file_id)

        if not os.path.exists(file_path):
            return None


        if file_extension==ProcessingEnum.TXT.value:
            return TextLoader(file_path,encoding="utf-8")
        
        elif file_extension==ProcessingEnum.PDF.value:
            return PyMuPDFLoader(file_path)
        
        else:
            return None
        
    def get_file_content(self,file_id:str):
        loader=self.get_file_loader(file_id=file_id)
        if loader:
            return loader.load()
        
        return None
    

    def process_file_content(self,file_content:list,file_id:str,
                             chaunk_size:int=100,overlap_size:int=20):
        text_splitter=RecursiveCharacterTextSplitter(chunk_size=chaunk_size,
                                                     chunk_overlap=overlap_size,
                                                     length_function=len)
        
        file_content_text=[
            doc.page_content
            for doc in file_content
        ]

        file_content_meatadata=[
            doc.metadata
            for doc in file_content
        ]

        chunks=text_splitter.create_documents(file_content_text,
                                               metadatas=file_content_meatadata)
        

        return chunks
