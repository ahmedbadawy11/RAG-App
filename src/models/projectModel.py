from .BaseDatamodel import BaseDatamodel
from .db_schemes import project
from .enums.BataBaseEnum import DataBaseEnum



class projectModel(BaseDatamodel):
    def __init__(self,db_client:object):
        super().__init__(db_client=db_client)
        self.collection = self.db_client[DataBaseEnum.COLLECTION_PROJECT_NAME.value]

    @classmethod
    async def create_instance(cls,db_client:object): 
        # this created because __init__ cann't be async and we need to call async init_collection inside constructor 

        instance=cls(db_client=db_client)
        await instance.init_collection()
        return instance


    async def init_collection(self):
        all_collections=await self.db_client.list_collection_names() # list all collections in the database
        if DataBaseEnum.COLLECTION_PROJECT_NAME.value not in all_collections:
            self.collection = self.db_client[DataBaseEnum.COLLECTION_PROJECT_NAME.value]
            indexes = project.get_indexes()
            for index in indexes:
                await self.collection.create_index(
                    index['key'], 
                    name=index['name'],
                    unique=index['unique']
                
                )

    async def create_project(self,project:project):
        result=await self.collection.insert_one(project.dict(by_alias=True, exclude_unset=True))# to use the alias when pathing to mongo
        # exclude_unset means that any attribute that not set will not be include in the dict (like id because it is optional and None)
        project.id=result.inserted_id

        return project
    

    
    
    async def get_project_or_create_one(self,project_id:str):
        
        record=await self.collection.find_one({
            "project_id":project_id
        })

        if record is None:
            # create New Project
            new_project=project(project_id=project_id)
            new_project=await self.create_project(project=new_project)

            return new_project
        
        return project(**record) # this take every value from record (dict) and create project class
    
    async def get_all_projects(self,page:int=1,page_size:int=10):
        #count total number of documents

        total_documents= await self.collection.count_documents({}) # empty filter to count any record

        # calculate total number of pages
        total_pages=total_documents//page_size

        if total_pages % page_size >0:
            total_pages +=1

        cursor=self.collection.find().skip((page-1)*page_size).limit(page_size)# this not return data but return cursor

        projects=[]

        async for document in cursor:
            projects.append(
                project(**document)
            )

        return projects,total_pages