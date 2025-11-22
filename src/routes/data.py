from fastapi import FastAPI, APIRouter,Depends, UploadFile,status,Request
from fastapi.responses import JSONResponse
import os
import aiofiles
from helpers.config import get_settings,settings
from controllers import DataController,ProjectController,ProcesController
from models import ResponseSignal
import logging
from .schemes.data import ProcessRequest

from models.projectModel import projectModel
from models.db_schemes import data_chunk,Asset
from models.ChunkModel import ChunkModel 
from models.AssetModel import AssetModel
from models.enums.AssetTypeEnum import AssetTypeEnum



logger=logging.getLogger('uvicorn.error')

data_router = APIRouter(
    prefix="/api/v1/data",
    tags=["api_v1","data"],
)

@data_router.post("/upload/{project_id}")
# request will get all information about the request included db_client and this different from ProcessRequest
async def upload_data(request:Request,project_id: str, file: UploadFile,
                      app_settings:settings = Depends(get_settings)):
    
    project_model=await projectModel.create_instance(
        db_client=request.app.db_client
        )
    
    project=await project_model.get_project_or_create_one(
        project_id=project_id
    )


    data_controller=DataController()
    is_valid, result_signal = data_controller.validate_uploaded_file(file=file)

    if not is_valid:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST, content={"Signal": result_signal})
    

    project_dir_path=ProjectController().get_project_path(project_id=project_id)
    # file_path = os.path.join(project_dir_path, file.filename)# old way
    file_path, file_id = data_controller.generate_unique_filepath(original_filename=file.filename,project_id=project_id)
    

    try:
        async with aiofiles.open(file_path, 'wb') as out_file:
            while chunk := await file.read(app_settings.FILE_DEFAULT_CHUNK_SIZE):  # Read file in chunks
                await out_file.write(chunk)  # Write chunk to the destination file

    except Exception as e:
        logger.error(f"Error while uploading file :{e}")
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "Signal":ResponseSignal.FILE_UPLOAD_FAILED.value
            }
        )
    
    # store asset record in the database
    asset_model=await AssetModel.create_instance(
        db_client=request.app.db_client
    )

    asset_resource=Asset(
        asset_project_id=project.id,
        asset_type=AssetTypeEnum.FILE.value,
        asset_name=file_id,
        asset_size=os.path.getsize(file_path),

    )

    asset_record=await asset_model.create_asset(asset=asset_resource)

    return JSONResponse(
            
            content={
                "Signal": ResponseSignal.FILE_UPLOADED_SUCCESS.value,
                "file_id":str(asset_record.id),
                # "project_id":str(project._id)

            }
    )




@data_router.post("/process/{project_id}")
async def process_endpoint(request:Request,project_id: str, process_request:ProcessRequest,
                     ):
    
    chunk_size = process_request.chunk_size
    overlap_size = process_request.overlap_size
    do_reset = process_request.do_reset

    project_model=await projectModel.create_instance(
        db_client=request.app.db_client
        )
    
    project=await project_model.get_project_or_create_one(
        project_id=project_id
    )


    asset_model=await AssetModel.create_instance(
            db_client=request.app.db_client
        )
    
    project_files_ids={}
    if process_request.file_id:
        asset_record=await asset_model.get_asset_record(
            asset_project_id=project.id,
            asset_name=process_request.file_id
        )

        if asset_record is None:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "Signal": ResponseSignal.FILE_ID_ERROR.value,
                  
                }
            )
        project_files_ids={
            asset_record.id:asset_record.asset_name
        }


    else:
        # get all project files
      

        project_files=await asset_model.get_all_project_assets(
            asset_project_id=project.id,
            asset_type=AssetTypeEnum.FILE.value
        )

        project_files_ids={
            asset.id:asset.asset_name
                           for asset in project_files}
        
        if len(project_files_ids)==0:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "Signal": ResponseSignal.NO_FILES_ERROR.value,
                  
                }
            )

    process_controller=ProcesController(project_id=project_id)


    no_records=0
    no_files=0

    chunk_model=await ChunkModel.create_instance(
        db_client=request.app.db_client
        )
    


    if do_reset==1:
        deleted_count=await chunk_model.delete_chunks_by_project_id(
            project_id=project.id
        )
        logger.info(f"Deleted {deleted_count} chunks for project_id: {project.project_id}")
    
    for asset_id ,file_id in project_files_ids.items():
        file_content=process_controller.get_file_content(file_id=file_id)

        if file_content is None:
            logger.error(f"Error while loading file content for file_id: {file_id}")
            continue
        
        file_chunks=process_controller.process_file_content(file_content=file_content,
                                                    file_id=file_id,
                                                        chaunk_size=chunk_size,
                                                        overlap_size=overlap_size)
        
        if file_chunks is None or len(file_chunks)==0:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "Signal": ResponseSignal.FILE_PROCESSING_FAILED.value,
                    "file_id": file_id
                }
            )
        
        
        file_chunks_records=[
            data_chunk(
                chunk_text=chunk.page_content,
                chunk_metadata=chunk.metadata,
                chunk_order=i+1,
                chunk_project_id=project.id,
                chunk_asset_id=asset_id
            )
            for i, chunk in enumerate(file_chunks) 
        ]

        
       

        
        no_records +=await chunk_model.insert_many_chunks(
            chunks=file_chunks_records)
        no_files +=1
    
    # return no_records

    return JSONResponse(
        content={
            "Signal": ResponseSignal.PROCESSING_SUCCESS.value,
            "inserted_chunks": no_records,
            "processed_files": no_files
           
        }
    )
    # return file_chunks