## ADDED Requirements

### Requirement: Issue key to recognized employee
The KeyService SHALL allow issuing a key to a specific cabinet for a recognized employee.

#### Scenario: Issue available key
- **WHEN** `KeyService.issue_key("101", employee)` is called with available cabinet
- **AND** employee is recognized (not None)
- **THEN** key status changes to ISSUED with holder info
- **AND** method returns (True, success_message)

#### Scenario: Refuse issue to unavailable key
- **WHEN** `KeyService.issue_key("101", employee)` is called for already issued key
- **THEN** method returns (False, error_message)
- **AND** no database changes occur

#### Scenario: Refuse issue without recognized employee
- **WHEN** `KeyService.issue_key("101", None)` is called
- **THEN** method returns (False, "Сотрудник не распознан")

### Requirement: Return key from employee
The KeyService SHALL allow returning a key to a specific cabinet.

#### Scenario: Return issued key
- **WHEN** `KeyService.return_key("101")` is called for issued key
- **THEN** key status changes to AVAILABLE
- **AND** holder info is cleared
- **AND** method returns (True, success_message)

#### Scenario: Refuse return of available key
- **WHEN** `KeyService.return_key("101")` is called for available key
- **THEN** method returns (False, error_message)

#### Scenario: Return all keys for employee
- **WHEN** `KeyService.return_all_for_employee(employee)` is called
- **THEN** all keys held by employee are returned
- **AND** method returns list of cabinet numbers