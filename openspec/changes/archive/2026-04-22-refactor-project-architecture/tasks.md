## 1. Infrastructure

- [x] 1.1 Create `core/` directory structure
- [x] 1.2 Create `core/interfaces.py` with ABC definitions
- [x] 1.3 Create `core/container.py` with DI container

## 2. Repository Interfaces

- [x] 2.1 Define `KeyRepository` abstract class
- [x] 2.2 Define `EmployeeRepository` abstract class
- [x] 2.3 Define `FaceRecognizer` abstract class

## 3. Implementations

- [x] 3.1 Create `repository/key_repository.py` implementing KeyRepository
- [x] 3.2 Create `repository/employee_repository.py` implementing EmployeeRepository
- [x] 3.3 Update `services/key_service.py` to use KeyRepository
- [x] 3.4 Update `services/face_service.py` to implement FaceRecognizer interface

## 4. Refactor DataStore

- [x] 4.1 Remove business logic from DataStore
- [x] 4.2 Keep only data access methods
- [x] 4.3 Update property names for repositories

## 5. Database Migrations

- [x] 5.1 Add schema_version table creation
- [x] 5.2 Implement `run_migrations()` function
- [x] 5.3 Add CURRENT_SCHEMA_VERSION constant

## 6. UI Integration

- [x] 6.1 Update MainWindow to use Container
- [x] 6.2 Create `app_container.py` for DI setup
- [x] 6.3 Test application startup

## 7. Testing

- [x] 7.1 Create test fixtures with mocked repositories
- [x] 7.2 Add unit tests for KeyService
- [x] 7.3 Add unit tests for DI container