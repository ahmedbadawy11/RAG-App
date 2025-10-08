from fastapi import FastAPI, APIRouter,Depends, UploadFile,status
from fastapi.responses import JSONResponse
import os
import aiofiles
from helpers.config import get_settings,settings
from controllers import DataController,ProjectController,ProcesController
from models import ResponseSignal
import logging
from .schemes.data import ProcessRequest


logger=logging.getLogger('uvicorn.error')

data_router = APIRouter(
    prefix="/api/v1/data",
    tags=["api_v1","data"],
)

@data_router.post("/upload/{project_id}")
async def upload_data(project_id: str, file: UploadFile,
                      app_settings:settings = Depends(get_settings)):
    
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
    
    return JSONResponse(
            
            content={
                "Signal": ResponseSignal.FILE_UPLOADED_SUCCESS.value,
                "file_id":file_id,

            }
    )




@data_router.post("/process/{project_id}")
async def process_endpoint(project_id: str, process_request:ProcessRequest,
                     ):
    
    file_id = process_request.file_id
    chunk_size = process_request.chunk_size
    overlap_size = process_request.overlap_size

    process_controller=ProcesController(project_id=project_id)

    file_content=process_controller.get_file_content(file_id=file_id)
    
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
    return file_chunks