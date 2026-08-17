# 前端依赖规则

前端采用适合课程周期的轻量Feature分层：

```text
app -> pages -> features -> entities -> shared
```

- `app/`：应用入口、路由和全局Provider；
- `pages/`：页面组合，不实现领域规则；
- `features/`：围绕用户动作组织，例如项目录入和报价确认；
- `entities/`：稳定业务模型与只读类型；
- `shared/`：无业务含义的HTTP、配置和通用UI契约。

约束：下层不能导入上层；Feature之间不直接互相引用；API实现通过Gateway接口注入；服务端JSON到前端领域类型的映射放在Feature适配器中。
