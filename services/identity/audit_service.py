"""
Serviço de auditoria para registrar ações no sistema.

Este serviço é responsável por:
- Registrar ações dos usuários
- Consultar logs de auditoria
- Filtrar logs por tenant, usuário, ação, etc.
"""

from typing import Optional, List
from uuid import UUID
from datetime import datetime
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


class AuditService:
    """Serviço de gerenciamento de logs de auditoria."""

    @classmethod
    async def log_action(
        cls,
        session: AsyncSession,
        tenant_id: UUID,
        user_id: UUID,
        action: str,
        resource_type: str,
        resource_id: Optional[UUID] = None,
        details: Optional[dict] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        status: str = "success",
        error_message: Optional[str] = None,
    ) -> UUID:
        """Registra uma ação no log de auditoria.

        Args:
            session: Sessão do banco de dados
            tenant_id: ID do tenant
            user_id: ID do usuário que executou a ação
            action: Ação executada (ex: 'create_project', 'delete_user')
            resource_type: Tipo do recurso (ex: 'project', 'user', 'workitem')
            resource_id: ID do recurso afetado (opcional)
            details: Detalhes adicionais da ação (opcional)
            ip_address: Endereço IP do usuário (opcional)
            user_agent: User agent do navegador (opcional)
            status: Status da ação ('success', 'failure', 'error')
            error_message: Mensagem de erro se status != 'success' (opcional)

        Returns:
            UUID do log criado
        """
        # Preparar detalhes
        details_json = details or {}

        # Inserir log
        query = text(
            """
            INSERT INTO audit_logs (
                tenant_id, user_id, action, resource_type, resource_id,
                details, ip_address, user_agent, status, error_message,
                created_at, updated_at
            )
            VALUES (
                :tenant_id, :user_id, :action, :resource_type, :resource_id,
                :details, :ip_address, :user_agent, :status, :error_message,
                NOW(), NOW()
            )
            RETURNING id
        """
        )

        result = await session.execute(
            query,
            {
                "tenant_id": str(tenant_id),
                "user_id": str(user_id),
                "action": action,
                "resource_type": resource_type,
                "resource_id": str(resource_id) if resource_id else None,
                "details": details_json,
                "ip_address": ip_address,
                "user_agent": user_agent,
                "status": status,
                "error_message": error_message,
            },
        )

        log_id = result.scalar_one()
        await session.commit()

        return log_id

    @classmethod
    async def get_audit_logs(
        cls,
        session: AsyncSession,
        tenant_id: UUID,
        user_id: Optional[UUID] = None,
        action: Optional[str] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[UUID] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        status: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[dict]:
        """Consulta logs de auditoria com filtros.

        Args:
            session: Sessão do banco de dados
            tenant_id: ID do tenant
            user_id: Filtrar por usuário (opcional)
            action: Filtrar por ação (opcional)
            resource_type: Filtrar por tipo de recurso (opcional)
            resource_id: Filtrar por ID do recurso (opcional)
            start_date: Data inicial (opcional)
            end_date: Data final (opcional)
            status: Filtrar por status (opcional)
            limit: Limite de resultados
            offset: Offset para paginação

        Returns:
            Lista de logs de auditoria
        """
        # Construir query base
        where_clauses = ["tenant_id = :tenant_id"]
        params = {"tenant_id": str(tenant_id), "limit": limit, "offset": offset}

        # Adicionar filtros opcionais
        if user_id:
            where_clauses.append("user_id = :user_id")
            params["user_id"] = str(user_id)

        if action:
            where_clauses.append("action = :action")
            params["action"] = action

        if resource_type:
            where_clauses.append("resource_type = :resource_type")
            params["resource_type"] = resource_type

        if resource_id:
            where_clauses.append("resource_id = :resource_id")
            params["resource_id"] = str(resource_id)

        if start_date:
            where_clauses.append("created_at >= :start_date")
            params["start_date"] = start_date

        if end_date:
            where_clauses.append("created_at <= :end_date")
            params["end_date"] = end_date

        if status:
            where_clauses.append("status = :status")
            params["status"] = status

        # Montar query completa
        where_clause = " AND ".join(where_clauses)
        query = text(
            f"""
            SELECT 
                id, tenant_id, user_id, action, resource_type, resource_id,
                details, ip_address, user_agent, status, error_message,
                created_at, updated_at
            FROM audit_logs
            WHERE {where_clause}
            ORDER BY created_at DESC
            LIMIT :limit OFFSET :offset
        """
        )

        result = await session.execute(query, params)
        rows = result.fetchall()

        # Converter para lista de dicts
        logs = []
        for row in rows:
            logs.append(
                {
                    "id": row[0],
                    "tenant_id": row[1],
                    "user_id": row[2],
                    "action": row[3],
                    "resource_type": row[4],
                    "resource_id": row[5],
                    "details": row[6],
                    "ip_address": row[7],
                    "user_agent": row[8],
                    "status": row[9],
                    "error_message": row[10],
                    "created_at": row[11],
                    "updated_at": row[12],
                }
            )

        return logs

    @classmethod
    async def get_audit_log_count(
        cls,
        session: AsyncSession,
        tenant_id: UUID,
        user_id: Optional[UUID] = None,
        action: Optional[str] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[UUID] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        status: Optional[str] = None,
    ) -> int:
        """Conta o número total de logs que correspondem aos filtros.

        Args:
            session: Sessão do banco de dados
            tenant_id: ID do tenant
            user_id: Filtrar por usuário (opcional)
            action: Filtrar por ação (opcional)
            resource_type: Filtrar por tipo de recurso (opcional)
            resource_id: Filtrar por ID do recurso (opcional)
            start_date: Data inicial (opcional)
            end_date: Data final (opcional)
            status: Filtrar por status (opcional)

        Returns:
            Número total de logs
        """
        # Construir query base
        where_clauses = ["tenant_id = :tenant_id"]
        params = {"tenant_id": str(tenant_id)}

        # Adicionar filtros opcionais
        if user_id:
            where_clauses.append("user_id = :user_id")
            params["user_id"] = str(user_id)

        if action:
            where_clauses.append("action = :action")
            params["action"] = action

        if resource_type:
            where_clauses.append("resource_type = :resource_type")
            params["resource_type"] = resource_type

        if resource_id:
            where_clauses.append("resource_id = :resource_id")
            params["resource_id"] = str(resource_id)

        if start_date:
            where_clauses.append("created_at >= :start_date")
            params["start_date"] = start_date

        if end_date:
            where_clauses.append("created_at <= :end_date")
            params["end_date"] = end_date

        if status:
            where_clauses.append("status = :status")
            params["status"] = status

        # Montar query completa
        where_clause = " AND ".join(where_clauses)
        query = text(
            f"""
            SELECT COUNT(*) 
            FROM audit_logs
            WHERE {where_clause}
        """
        )

        result = await session.execute(query, params)
        count = result.scalar_one()

        return count

    @classmethod
    async def get_user_activity(
        cls,
        session: AsyncSession,
        tenant_id: UUID,
        user_id: UUID,
        days: int = 30,
        limit: int = 50,
    ) -> List[dict]:
        """Obtém atividade recente de um usuário.

        Args:
            session: Sessão do banco de dados
            tenant_id: ID do tenant
            user_id: ID do usuário
            days: Número de dias para buscar (padrão: 30)
            limit: Limite de resultados

        Returns:
            Lista de atividades recentes
        """
        query = text(
            """
            SELECT 
                id, action, resource_type, resource_id,
                details, status, created_at
            FROM audit_logs
            WHERE tenant_id = :tenant_id 
                AND user_id = :user_id
                AND created_at >= NOW() - INTERVAL ':days days'
            ORDER BY created_at DESC
            LIMIT :limit
        """
        )

        result = await session.execute(
            query,
            {"tenant_id": str(tenant_id), "user_id": str(user_id), "days": days, "limit": limit},
        )
        rows = result.fetchall()

        # Converter para lista de dicts
        activities = []
        for row in rows:
            activities.append(
                {
                    "id": row[0],
                    "action": row[1],
                    "resource_type": row[2],
                    "resource_id": row[3],
                    "details": row[4],
                    "status": row[5],
                    "created_at": row[6],
                }
            )

        return activities

    @classmethod
    async def get_resource_history(
        cls,
        session: AsyncSession,
        tenant_id: UUID,
        resource_type: str,
        resource_id: UUID,
        limit: int = 50,
    ) -> List[dict]:
        """Obtém histórico de ações em um recurso específico.

        Args:
            session: Sessão do banco de dados
            tenant_id: ID do tenant
            resource_type: Tipo do recurso
            resource_id: ID do recurso
            limit: Limite de resultados

        Returns:
            Lista de ações no recurso
        """
        query = text(
            """
            SELECT 
                id, user_id, action, details, status, created_at
            FROM audit_logs
            WHERE tenant_id = :tenant_id 
                AND resource_type = :resource_type
                AND resource_id = :resource_id
            ORDER BY created_at DESC
            LIMIT :limit
        """
        )

        result = await session.execute(
            query,
            {
                "tenant_id": str(tenant_id),
                "resource_type": resource_type,
                "resource_id": str(resource_id),
                "limit": limit,
            },
        )
        rows = result.fetchall()

        # Converter para lista de dicts
        history = []
        for row in rows:
            history.append(
                {
                    "id": row[0],
                    "user_id": row[1],
                    "action": row[2],
                    "details": row[3],
                    "status": row[4],
                    "created_at": row[5],
                }
            )

        return history
