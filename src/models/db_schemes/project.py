from pydantic import BaseModel, Field,validator
from typing import List, Optional
from bson.objectid import ObjectId


class project(BaseModel):
    id:Optional[ObjectId]=Field(None,alias="_id") 
    project_id: str=Field(...,min_length=1)


    @validator('project_id')
    def validate_project_id(cls,value):
        if not value.isalnum():
            raise ValueError ('Project_id Must be alphanumeric')
        
        return value
    

    class Config: # to ignore any un know data type like 'ObjectId'
        arbitrary_types_allowed = True

    @classmethod
    def get_indexes(cls):
        return [
            {
                "key":[
                ("project_id",1) # 1 for ascending order
                
                ],
                "name":"project_id_index_1",
                "unique":True
            } 
        ]
