import pytest
from core.container import Container
from core.interfaces import KeyRepository, EmployeeRepository
from services.key_service import KeyService
from models import Employee, Key


class TestContainer:
    def test_singleton_returns_same_instance(self):
        container = Container()
        mock_repo = MockKeyRepoForSingleton()
        container.register_instance(KeyRepository, mock_repo)
        
        instance1 = container.get(KeyRepository)
        instance2 = container.get(KeyRepository)
        
        assert instance1 is instance2

    def test_get_unregistered_raises_key_error(self):
        container = Container()
        
        with pytest.raises(KeyError):
            container.get(KeyRepository)

    def test_has_returns_true_for_registered(self):
        container = Container()
        container.register_instance(KeyRepository, MockKeyRepoForSingleton())
        
        assert container.has(KeyRepository) is True

    def test_clear_removes_all_services(self):
        container = Container()
        container.register_instance(KeyRepository, MockKeyRepoForSingleton())
        
        container.clear()
        
        assert container.has(KeyRepository) is False


class MockKeyRepoForSingleton(KeyRepository):
    def get_all(self):
        return []
    def get_by_cabinet(self, cabinet):
        return None
    def add(self, cabinet):
        pass
    def update(self, key):
        pass
    def delete(self, cabinet):
        pass


class TestKeyService:
    def test_issue_key_requires_employee(self):
        from models import Key
        container = Container()
        mock_repo = MockKeyRepo()
        container.register_instance(KeyRepository, mock_repo)
        
        service = KeyService(container.get(KeyRepository))
        success, message = service.issue_key("101", None)
        
        assert success is False
        assert "не распознан" in message

    def test_return_available_key_fails(self):
        from models import Key
        container = Container()
        mock_repo = MockKeyRepo()
        container.register_instance(KeyRepository, mock_repo)
        
        service = KeyService(container.get(KeyRepository))
        success, message = service.return_key("101")
        
        assert success is False


class MockKeyRepo(KeyRepository):
    def get_all(self):
        return [Key.from_available("101")]
    
    def get_by_cabinet(self, cabinet: str):
        if cabinet == "101":
            return Key.from_available("101")
        return None
    
    def add(self, cabinet: str) -> None:
        pass
    
    def update(self, key) -> None:
        pass
    
    def delete(self, cabinet: str) -> None:
        pass