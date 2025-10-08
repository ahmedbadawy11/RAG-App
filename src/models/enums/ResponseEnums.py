from enum import Enum

class ResponseSignal(Enum):
    
    FILE_VALIDATED_SUCCESS="file_validate_successfully"

    FILE_TYPE_NOT_SUPPORTED="File_type_not_supported"
    FILE_SIZE_EXCEEDED="File_size_exceeded"
    FILE_UPLOADED_SUCCESS="file_uploaded_success"
    FILE_UPLOAD_FAILED="file_upload_failed"
    PROCESSING_FAILED="processing_failed"
    PROCESSING_SUCCESS="processing_success"