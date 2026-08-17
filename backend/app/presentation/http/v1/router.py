from fastapi import APIRouter

router = APIRouter(prefix="/v1")

# 业务路由将在P3-P6阶段按用例逐个注册：
# - POST /projects
# - GET /projects
# - GET /agent-runs/{run_id}
# - POST /agent-runs/{run_id}/answers
# - POST /agent-runs/{run_id}/approve
