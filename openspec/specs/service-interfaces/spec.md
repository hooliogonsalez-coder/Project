# service-interfaces Specification

## Purpose
TBD - created by archiving change refactor-project-architecture. Update Purpose after archive.
## Requirements
### Requirement: KeyRepository interface for key data access
The system SHALL provide `KeyRepository` interface with methods for CRUD operations on keys.

#### Scenario: Get all keys
- **WHEN** `KeyRepository.get_all()` is called
- **THEN** method returns list of all Key objects from database

#### Scenario: Get key by cabinet number
- **WHEN** `KeyRepository.get_by_cabinet("101")` is called
- **THEN** method returns Key object or None if not found

#### Scenario: Save key
- **WHEN** `KeyRepository.save(key)` is called with new Key
- **THEN** key is persisted to database

### Requirement: EmployeeRepository interface for employee data access
The system SHALL provide `EmployeeRepository` interface with methods for employee CRUD and face matching.

#### Scenario: Get employee by ID
- **WHEN** `EmployeeRepository.get_by_id(1)` is called
- **THEN** method returns Employee object or None

#### Scenario: Find employee by face encoding
- **WHEN** `EmployeeRepository.find_by_face(encoding)` is called
- **THEN** method returns best matching Employee based on cosine similarity

#### Scenario: Add new employee
- **WHEN** `EmployeeRepository.add(employee)` is called
- **THEN** employee is persisted and ID is assigned

### Requirement: FaceRecognizer interface for face operations
The system SHALL provide `FaceRecognizer` interface abstracting face detection and encoding.

#### Scenario: Encode face from image
- **WHEN** `FaceRecognizer.encode(image_bytes)` is called
- **THEN** method returns face embedding bytes or None

#### Scenario: Recognize employee from frame
- **WHEN** `FaceRecognizer.recognize(frame)` is called
- **THEN** method returns recognized Employee or None

