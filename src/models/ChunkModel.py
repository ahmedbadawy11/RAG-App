from .BaseDatamodel import BaseDatamodel
from .db_schemes import data_chunk
from .enums.BataBaseEnum import DataBaseEnum
from bson.objectid import ObjectId
from pymongo import InsertOne # this is the type of the operation  imagine that we define the operation type but we not execute it yet


class ChunkModel(BaseDatamodel):
    def __init__(self,db_client:object):
        super().__init__(db_client=db_client)
        self.collection = self.db_client[DataBaseEnum.COLLECTION_CHUNK_NAME.value]

    @classmethod
    async def create_instance(cls,db_client:object): 
        # this created because __init__ cann't be async and we need to call async init_collection inside constructor 

        instance=cls(db_client=db_client)
        await instance.init_collection()
        return instance

    
    async def init_collection(self):
        all_collections=await self.db_client.list_collection_names() # list all collections in the database
        if DataBaseEnum.COLLECTION_CHUNK_NAME.value not in all_collections:
            self.collection = self.db_client[DataBaseEnum.COLLECTION_CHUNK_NAME.value]
            indexes = data_chunk.get_indexes()
            for index in indexes:
                await self.collection.create_index(
                    index['key'], 
                    name=index['name'],
                    unique=index['unique']
                
                )

    async def create_chunk(self,chunk:data_chunk):
        result=await self.collection.insert_one(chunk.dict(by_alias=True, exclude_unset=True)) # this is the action of the operation 
        chunk._id=result.inserted_id
        return 
    
    async def get_chunk(self,chunk_id:str):
        record=await self.collection.find_one({
            "_id":ObjectId(chunk_id)
        })

        if record is None:
            return None
        
        return data_chunk(**record)
    

    async def insert_many_chunks(self,chunks:list,batch_size:int=100):   
        # i  cann't inser one by one is aheadic opration instead i use bulk_write

        for i in range(0,len(chunks),batch_size):
            batch=chunks[i:i+batch_size]


            operaton=[
                InsertOne(chunk.dict(by_alias=True, exclude_unset=True))
                for chunk in batch
            ]

            await self.collection.bulk_write(operaton)

        return len(chunks)

    async def delete_chunks_by_project_id(self,project_id:ObjectId):
        result= await self.collection.delete_many({
            "chunk_project_id":project_id
        })

        return result.deleted_count
    
