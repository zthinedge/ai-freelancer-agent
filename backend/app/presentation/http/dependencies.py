from fastapi import Request

from app.application.services import ProjectAnalysisService
from app.bootstrap.container import ApplicationContainer


def get_project_analysis_service(request: Request) -> ProjectAnalysisService:
    container: ApplicationContainer = request.app.state.container
    return container.project_analysis
