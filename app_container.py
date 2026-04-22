from core.container import Container
from core.interfaces import KeyRepository, EmployeeRepository
from database import Database
from repository import EmployeeRepositoryImpl, KeyRepositoryImpl
from services import CameraService, FaceService, KeyService
from data import DataStore
import config


def create_container() -> Container:
    container = Container()
    
    db = Database(config.DATABASE_PATH)
    container.register_instance(Database, db)
    
    container.register_instance(DataStore, DataStore(db))
    container.register_instance(KeyRepository, KeyRepositoryImpl(db))
    container.register_instance(EmployeeRepository, EmployeeRepositoryImpl(db))
    
    container.register(CameraService)
    container.register(FaceService)
    container.register(KeyService)
    
    return container