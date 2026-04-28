from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import base64

from app.database import get_session
from app.models.employee import Employee
from app.schemas.employee import EmployeeCreate, EmployeeOut
from app.middleware.auth import verify_api_key

router = APIRouter(prefix="/api/employees", tags=["employees"])


@router.get("/", response_model=list[EmployeeOut])
async def list_employees(
    api_key: str = Depends(verify_api_key),
    db: AsyncSession = Depends(get_session),
):
    result = await db.execute(select(Employee))
    employees = result.scalars().all()
    return [
        EmployeeOut(
            id=e.id,
            name=e.name,
            surname=e.surname,
            department=e.department,
            position=e.position,
            face_embedding_b64=base64.b64encode(e.face_embedding).decode(),
            updated_at=e.updated_at,
        )
        for e in employees
    ]


@router.post("/", response_model=EmployeeOut, status_code=201)
async def create_employee(
    data: EmployeeCreate,
    api_key: str = Depends(verify_api_key),
    db: AsyncSession = Depends(get_session),
):
    emp = Employee(
        name=data.name,
        surname=data.surname,
        department=data.department,
        position=data.position,
        face_embedding=base64.b64decode(data.face_embedding_b64),
    )
    db.add(emp)
    await db.commit()
    await db.refresh(emp)
    return EmployeeOut(
        id=emp.id,
        name=emp.name,
        surname=emp.surname,
        department=emp.department,
        position=emp.position,
        face_embedding_b64=base64.b64encode(emp.face_embedding).decode(),
        updated_at=emp.updated_at,
    )


@router.put("/{emp_id}", response_model=EmployeeOut)
async def update_employee(
    emp_id: int,
    data: EmployeeCreate,
    api_key: str = Depends(verify_api_key),
    db: AsyncSession = Depends(get_session),
):
    emp = await db.get(Employee, emp_id)
    if not emp:
        raise HTTPException(404, "Сотрудник не найден")
    emp.name = data.name
    emp.surname = data.surname
    emp.department = data.department
    emp.position = data.position
    emp.face_embedding = base64.b64decode(data.face_embedding_b64)
    await db.commit()
    await db.refresh(emp)
    return EmployeeOut(
        id=emp.id,
        name=emp.name,
        surname=emp.surname,
        department=emp.department,
        position=emp.position,
        face_embedding_b64=base64.b64encode(emp.face_embedding).decode(),
        updated_at=emp.updated_at,
    )


@router.delete("/{emp_id}", status_code=204)
async def delete_employee(
    emp_id: int,
    api_key: str = Depends(verify_api_key),
    db: AsyncSession = Depends(get_session),
):
    emp = await db.get(Employee, emp_id)
    if not emp:
        raise HTTPException(404, "Сотрудник не найден")
    await db.delete(emp)
    await db.commit()