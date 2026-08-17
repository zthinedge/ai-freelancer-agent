class ApplicationError(Exception):
    """可安全映射为外部响应的应用层错误基类。"""


class ResourceNotFoundError(ApplicationError):
    """请求的领域资源不存在。"""


class ConflictError(ApplicationError):
    """当前状态不允许执行请求的操作。"""


class IntegrationError(ApplicationError):
    """外部模型、工具或存储适配器调用失败。"""
