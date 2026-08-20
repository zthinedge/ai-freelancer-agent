from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.application.contracts import (
    AgentRunView,
    ApproveQuoteCommand,
    CreateProjectCommand,
    ProjectView,
    SubmitClarificationCommand,
)
from app.application.services import ProjectAnalysisService
from app.presentation.http.contracts import ApproveQuoteRequest, SubmitClarificationRequest
from app.presentation.http.dependencies import get_project_analysis_service

router = APIRouter(tags=["project-analysis"])
ProjectService = Annotated[ProjectAnalysisService, Depends(get_project_analysis_service)]


@router.post("/projects", response_model=ProjectView, status_code=status.HTTP_201_CREATED)
async def create_project(command: CreateProjectCommand, service: ProjectService) -> ProjectView:
    return await service.create_project(command)


@router.get("/projects", response_model=list[ProjectView])
async def list_projects(service: ProjectService) -> tuple[ProjectView, ...]:
    return await service.list_projects()


@router.get("/agent-runs/{run_id}", response_model=AgentRunView)
async def get_agent_run(run_id: UUID, service: ProjectService) -> AgentRunView:
    return await service.get_run(run_id)


@router.post("/agent-runs/{run_id}/answers", response_model=AgentRunView)
async def submit_answers(
    run_id: UUID,
    request: SubmitClarificationRequest,
    service: ProjectService,
) -> AgentRunView:
    command = SubmitClarificationCommand(run_id=run_id, answers=request.answers)
    return await service.submit_answers(command)


@router.post("/agent-runs/{run_id}/approve", response_model=AgentRunView)
async def approve_quote(
    run_id: UUID,
    request: ApproveQuoteRequest,
    service: ProjectService,
) -> AgentRunView:
    command = ApproveQuoteCommand(
        run_id=run_id,
        approved=request.approved,
        selected_tier=request.selected_tier,
        note=request.note,
    )
    return await service.approve_quote(command)
