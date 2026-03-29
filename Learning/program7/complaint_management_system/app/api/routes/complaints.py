from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.schemas.complaint import (
    ComplaintCreateRequest, ComplaintUpdateRequest, ComplaintStageUpdateRequest,
    ComplaintResponse, ComplaintDetailCreateRequest, ComplaintDetailUpdateRequest, ComplaintDetailResponse,
)
from app.schemas.pagination import PaginationParams, PaginatedResponse
from app.usecases.commands.create_complaint import CreateComplaintUseCase, CreateComplaintCommand
from app.usecases.commands.update_complaint import UpdateComplaintUseCase, UpdateComplaintCommand
from app.usecases.commands.update_stage import UpdateStageUseCase
from app.usecases.commands.delete_complaint import DeleteComplaintUseCase
from app.usecases.commands.complaint_detail import (
    CreateComplaintDetailUseCase, UpdateComplaintDetailUseCase, ApproveFinancialsUseCase,
)
from app.usecases.queries.get_complaint import GetComplaintQuery
from app.services.auth_service import get_current_user, require_role
from app.models.user import User
from app.repositories.complaint_repository import ComplaintRepository
import math

router = APIRouter(prefix="/complaints", tags=["Complaints"])


# --- Complaint CRUD ---

@router.post("/", response_model=ComplaintResponse, status_code=201)
async def create_complaint(
    data: ComplaintCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    command = CreateComplaintCommand(title=data.title, description=data.description, priority=data.priority)
    print ("\n command >>>>>>>>>>> ",command)
    return await CreateComplaintUseCase(db).execute(command, current_user)


@router.get("/", response_model=PaginatedResponse[ComplaintResponse])
async def list_complaints(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    pagination = PaginationParams(page=page, page_size=page_size)
    repo = ComplaintRepository(db)
    complaints, total = await repo.get_paginated(pagination)
    return PaginatedResponse(
        items=complaints, total=total, page=page,
        page_size=page_size, total_pages=math.ceil(total / page_size) if total else 0,
    )


@router.get("/{complaint_id}", response_model=ComplaintResponse)
async def get_complaint(
    complaint_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await GetComplaintQuery(db).execute(complaint_id)


@router.patch("/{complaint_id}", response_model=ComplaintResponse)
async def update_complaint(
    complaint_id: int,
    data: ComplaintUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    command = UpdateComplaintCommand(
        title=data.title, description=data.description,
        priority=data.priority, assigned_to=data.assigned_to,
    )
    return await UpdateComplaintUseCase(db).execute(complaint_id, command, current_user)


@router.delete("/{complaint_id}", status_code=204)
async def delete_complaint(
    complaint_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    await DeleteComplaintUseCase(db).execute(complaint_id, current_user)


# --- Stage Transitions ---

@router.patch("/{complaint_id}/stage", response_model=ComplaintResponse)
async def update_stage(
    complaint_id: int,
    data: ComplaintStageUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await UpdateStageUseCase(db).execute(complaint_id, data.stage, current_user)


# --- Complaint Detail ---

@router.post("/{complaint_id}/detail", response_model=ComplaintDetailResponse, status_code=201)
async def create_detail(
    complaint_id: int,
    data: ComplaintDetailCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await CreateComplaintDetailUseCase(db).execute(complaint_id, data, current_user)


@router.patch("/{complaint_id}/detail", response_model=ComplaintDetailResponse)
async def update_detail(
    complaint_id: int,
    data: ComplaintDetailUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await UpdateComplaintDetailUseCase(db).execute(complaint_id, data, current_user)


@router.post("/{complaint_id}/detail/approve-financials", response_model=ComplaintDetailResponse)
async def approve_financials(
    complaint_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("approver")),
):
    return await ApproveFinancialsUseCase(db).execute(complaint_id, current_user)
