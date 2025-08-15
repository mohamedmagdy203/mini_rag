from enum import Enum

class DatabaseEnum(str, Enum):
    COLLECTION_PROJECTS_NAME = "projects"
    COLLECTION_CHUNKS_NAME = "chunks"
