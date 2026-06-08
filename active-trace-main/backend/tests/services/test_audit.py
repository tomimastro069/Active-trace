import pytest
from uuid import uuid4
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

from app.services.audit import AuditService
from app.schemas.auth import CurrentUser

@pytest.mark.asyncio
async def test_audit_service_check_access_global_admin():
    # Mocking
    db = AsyncMock()
    tenant_id = uuid4()
    service = AuditService(db, tenant_id)
    
    # Mock asignacion repo
    service.asignacion_repo = AsyncMock()
    service.asignacion_repo.get_effective_permissions.return_value = ["auditoria:ver"]
    
    current_user = CurrentUser(id=uuid4(), tenant_id=tenant_id, email="admin@test.com", roles=["ADMIN"])
    
    # Check
    result = await service._check_access_and_get_materia_filter(current_user)
    assert result is None

@pytest.mark.asyncio
async def test_audit_service_check_access_propio():
    db = AsyncMock()
    tenant_id = uuid4()
    service = AuditService(db, tenant_id)
    
    service.asignacion_repo = AsyncMock()
    service.asignacion_repo.get_effective_permissions.return_value = ["auditoria:ver_propio"]
    
    materia_activa_id = uuid4()
    mock_assignment = MagicMock()
    mock_assignment.materia_id = materia_activa_id
    mock_assignment.estado_vigencia = "Vigente"
    
    service.asignacion_repo.list_assignments.return_value = [mock_assignment]
    
    current_user = CurrentUser(id=uuid4(), tenant_id=tenant_id, email="coord@test.com", roles=["COORDINADOR"])
    
    result = await service._check_access_and_get_materia_filter(current_user)
    assert result == [materia_activa_id]

@pytest.mark.asyncio
async def test_get_interaction_metrics():
    db = AsyncMock()
    tenant_id = uuid4()
    service = AuditService(db, tenant_id)
    
    with patch.object(service, '_check_access_and_get_materia_filter', return_value=None):
        # Mock execution result
        mock_result = MagicMock()
        mock_result.all.return_value = []
        db.execute.return_value = mock_result
        
        current_user = CurrentUser(id=uuid4(), tenant_id=tenant_id, email="admin@test.com", roles=["ADMIN"])
        metrics = await service.get_interaction_metrics(current_user)
        
        assert "daily_activity" in metrics
        assert "teacher_communications" in metrics
        assert "teacher_subject_interactions" in metrics

@pytest.mark.asyncio
async def test_get_logs():
    db = AsyncMock()
    tenant_id = uuid4()
    service = AuditService(db, tenant_id)
    
    with patch.object(service, '_check_access_and_get_materia_filter', return_value=None):
        # Mock execution result
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        db.execute.return_value = mock_result
        
        current_user = CurrentUser(id=uuid4(), tenant_id=tenant_id, email="admin@test.com", roles=["ADMIN"])
        logs = await service.get_logs(current_user)
        
        assert isinstance(logs, list)
        assert len(logs) == 0

@pytest.mark.asyncio
async def test_audit_service_check_access_propio_unauthorized_subject():
    db = AsyncMock()
    tenant_id = uuid4()
    service = AuditService(db, tenant_id)
    
    service.asignacion_repo = AsyncMock()
    service.asignacion_repo.get_effective_permissions.return_value = ["auditoria:ver_propio"]
    
    subject_a = uuid4()
    subject_b = uuid4()
    
    mock_assignment = MagicMock()
    mock_assignment.materia_id = subject_a
    mock_assignment.estado_vigencia = "Vigente"
    
    service.asignacion_repo.list_assignments.return_value = [mock_assignment]
    
    current_user = CurrentUser(id=uuid4(), tenant_id=tenant_id, email="coord@test.com", roles=["COORDINADOR"])
    
    with pytest.raises(ValueError, match="El usuario no tiene una asignación vigente para la materia especificada"):
        await service._check_access_and_get_materia_filter(current_user, materia_id=subject_b)



