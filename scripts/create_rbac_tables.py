#!/usr/bin/env python3
"""
Script para criar/atualizar tabelas do sistema RBAC e Multi-Tenant.

Este script:
1. Cria todas as tabelas base do sistema
2. Adiciona campos necessários para RBAC
3. Cria índices de performance
"""

import asyncio
import sys
from pathlib import Path

# Adicionar o diretório raiz ao path
sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy import text
from services.shared.database import engine, init_db


async def add_user_fields():
    """Adiciona novos campos à tabela users."""
    
    # Comandos SQL para adicionar campos
    commands = [
        "ALTER TABLE \"user\" ADD COLUMN IF NOT EXISTS is_super_admin BOOLEAN DEFAULT FALSE;",
        "ALTER TABLE \"user\" ADD COLUMN IF NOT EXISTS last_login_at TIMESTAMP;",
        "ALTER TABLE \"user\" ADD COLUMN IF NOT EXISTS last_login_ip VARCHAR(45);",
        "CREATE INDEX IF NOT EXISTS idx_users_super_admin ON \"user\"(is_super_admin) WHERE is_super_admin = TRUE;",
        "CREATE INDEX IF NOT EXISTS idx_users_last_login ON \"user\"(last_login_at);",
    ]
    
    async with engine.begin() as conn:
        for command in commands:
            try:
                print(f"  Executando: {command[:80]}...")
                await conn.execute(text(command))
            except Exception as e:
                print(f"  ⚠️  Aviso: {e}")
    
    print("✅ Campos adicionados à tabela users")


async def update_tenants_table():
    """Atualiza tabela tenants com novos campos."""
    
    # Comandos SQL para adicionar campos
    commands = [
        "ALTER TABLE \"tenant\" ADD COLUMN IF NOT EXISTS subscription_plan VARCHAR(50) DEFAULT 'free';",
        "ALTER TABLE \"tenant\" ADD COLUMN IF NOT EXISTS subscription_expires_at TIMESTAMP;",
        "ALTER TABLE \"tenant\" ADD COLUMN IF NOT EXISTS max_users INTEGER DEFAULT 10;",
        "ALTER TABLE \"tenant\" ADD COLUMN IF NOT EXISTS max_projects INTEGER DEFAULT 5;",
        "ALTER TABLE \"tenant\" ADD COLUMN IF NOT EXISTS logo_url VARCHAR(500);",
        "ALTER TABLE \"tenant\" ADD COLUMN IF NOT EXISTS domain VARCHAR(255);",
        "CREATE INDEX IF NOT EXISTS idx_tenants_subscription ON \"tenant\"(subscription_plan);",
        "CREATE INDEX IF NOT EXISTS idx_tenants_domain ON \"tenant\"(domain) WHERE domain IS NOT NULL;",
    ]
    
    async with engine.begin() as conn:
        for command in commands:
            try:
                print(f"  Executando: {command[:80]}...")
                await conn.execute(text(command))
            except Exception as e:
                print(f"  ⚠️  Aviso: {e}")
    
    print("✅ Tabela tenants atualizada")


async def update_roles_table():
    """Atualiza tabela roles com novos campos."""
    
    # Comandos SQL para adicionar campos
    commands = [
        "ALTER TABLE \"role\" ADD COLUMN IF NOT EXISTS display_name VARCHAR(100);",
        "ALTER TABLE \"role\" ADD COLUMN IF NOT EXISTS level INTEGER DEFAULT 10;",
        "CREATE INDEX IF NOT EXISTS idx_roles_name ON \"role\"(name);",
        "CREATE INDEX IF NOT EXISTS idx_roles_level ON \"role\"(level);",
        "CREATE INDEX IF NOT EXISTS idx_roles_system ON \"role\"(is_system) WHERE is_system = TRUE;",
    ]
    
    async with engine.begin() as conn:
        for command in commands:
            try:
                print(f"  Executando: {command[:80]}...")
                await conn.execute(text(command))
            except Exception as e:
                print(f"  ⚠️  Aviso: {e}")
    
    print("✅ Tabela roles atualizada")


async def update_user_roles_table():
    """Atualiza tabela user_roles com novos campos."""
    
    # Comandos SQL para adicionar campos
    commands = [
        "ALTER TABLE \"user_role\" ADD COLUMN IF NOT EXISTS tenant_id UUID;",
        "ALTER TABLE \"user_role\" ADD COLUMN IF NOT EXISTS assigned_by UUID;",
        "ALTER TABLE \"user_role\" ADD COLUMN IF NOT EXISTS assigned_at TIMESTAMP DEFAULT NOW();",
        "ALTER TABLE \"user_role\" ADD COLUMN IF NOT EXISTS expires_at TIMESTAMP;",
        "CREATE INDEX IF NOT EXISTS idx_user_roles_tenant ON \"user_role\"(tenant_id);",
        "CREATE INDEX IF NOT EXISTS idx_user_roles_user_tenant ON \"user_role\"(user_id, tenant_id);",
        "CREATE INDEX IF NOT EXISTS idx_user_roles_project ON \"user_role\"(project_id) WHERE project_id IS NOT NULL;",
    ]
    
    async with engine.begin() as conn:
        for command in commands:
            try:
                print(f"  Executando: {command[:80]}...")
                await conn.execute(text(command))
            except Exception as e:
                print(f"  ⚠️  Aviso: {e}")
    
    print("✅ Tabela user_roles atualizada")


async def create_audit_logs_table():
    """Cria tabela de audit_logs."""
    
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS audit_logs (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        tenant_id UUID NOT NULL,
        user_id UUID NOT NULL,
        action VARCHAR(100) NOT NULL,
        resource_type VARCHAR(50) NOT NULL,
        resource_id UUID,
        details JSONB DEFAULT '{}',
        ip_address VARCHAR(45),
        user_agent VARCHAR(500),
        status VARCHAR(20) DEFAULT 'success',
        error_message TEXT,
        created_at TIMESTAMP DEFAULT NOW(),
        updated_at TIMESTAMP DEFAULT NOW()
    );
    """
    
    indexes = [
        "CREATE INDEX IF NOT EXISTS idx_audit_logs_tenant ON audit_logs(tenant_id);",
        "CREATE INDEX IF NOT EXISTS idx_audit_logs_user ON audit_logs(user_id);",
        "CREATE INDEX IF NOT EXISTS idx_audit_logs_action ON audit_logs(action);",
        "CREATE INDEX IF NOT EXISTS idx_audit_logs_resource ON audit_logs(resource_type);",
        "CREATE INDEX IF NOT EXISTS idx_audit_logs_created ON audit_logs(created_at);",
        "CREATE INDEX IF NOT EXISTS idx_audit_logs_tenant_created ON audit_logs(tenant_id, created_at);",
        "CREATE INDEX IF NOT EXISTS idx_audit_logs_action_resource ON audit_logs(action, resource_type);",
        "CREATE INDEX IF NOT EXISTS idx_audit_logs_user_action ON audit_logs(user_id, action);",
    ]
    
    async with engine.begin() as conn:
        print("  Criando tabela audit_logs...")
        await conn.execute(text(create_table_sql))
        
        for index_sql in indexes:
            try:
                print(f"  Criando índice: {index_sql[:80]}...")
                await conn.execute(text(index_sql))
            except Exception as e:
                print(f"  ⚠️  Aviso: {e}")
    
    print("✅ Tabela audit_logs criada")


async def create_performance_indexes():
    """Cria índices adicionais para performance."""
    
    # Índices adicionais
    indexes = [
        # Índices para tenant_id em tabelas existentes (se não existirem)
        "CREATE INDEX IF NOT EXISTS idx_projects_tenant_id ON project(tenant_id);",
        "CREATE INDEX IF NOT EXISTS idx_work_items_tenant_id ON work_item(tenant_id);",
        
        # Índices compostos para queries comuns
        "CREATE INDEX IF NOT EXISTS idx_work_items_project_status ON work_item(project_id, status);",
        "CREATE INDEX IF NOT EXISTS idx_work_items_assignee_status ON work_item(assigned_to, status) WHERE assigned_to IS NOT NULL;",
    ]
    
    async with engine.begin() as conn:
        for index_sql in indexes:
            try:
                print(f"  Criando índice: {index_sql[:80]}...")
                await conn.execute(text(index_sql))
            except Exception as e:
                print(f"  ⚠️  Aviso (pode já existir): {str(e)[:100]}")
    
    print("✅ Índices de performance criados")


async def verify_tables():
    """Verifica se as tabelas foram criadas corretamente."""
    
    tables_to_check = ['user', 'tenant', 'role', 'user_role', 'audit_logs']
    
    async with engine.begin() as conn:
        for table in tables_to_check:
            result = await conn.execute(text(f"""
                SELECT COUNT(*) as count 
                FROM information_schema.tables 
                WHERE table_name = '{table}'
            """))
            count = result.scalar()
            
            if count > 0:
                print(f"  ✅ Tabela {table} existe")
            else:
                print(f"  ❌ Tabela {table} NÃO existe")
                return False
    
    return True


async def main():
    """Função principal."""
    print("🚀 Iniciando criação/atualização das tabelas RBAC...")
    print("")
    
    try:
        # 1. Criar todas as tabelas base primeiro
        print("1️⃣ Criando tabelas base do sistema...")
        await init_db()
        print("✅ Tabelas base criadas/verificadas")
        print("")
        
        # 2. Atualizar tabela users
        print("2️⃣ Atualizando tabela users...")
        await add_user_fields()
        print("")
        
        # 3. Atualizar tabela tenants
        print("3️⃣ Atualizando tabela tenants...")
        await update_tenants_table()
        print("")
        
        # 4. Atualizar tabela roles
        print("4️⃣ Atualizando tabela roles...")
        await update_roles_table()
        print("")
        
        # 5. Atualizar tabela user_roles
        print("5️⃣ Atualizando tabela user_roles...")
        await update_user_roles_table()
        print("")
        
        # 6. Criar tabela audit_logs
        print("6️⃣ Criando tabela audit_logs...")
        await create_audit_logs_table()
        print("")
        
        # 7. Criar índices de performance
        print("7️⃣ Criando índices de performance...")
        await create_performance_indexes()
        print("")
        
        # 8. Verificar criação
        print("8️⃣ Verificando tabelas...")
        success = await verify_tables()
        print("")
        
        if success:
            print("🎉 Todas as tabelas RBAC foram criadas/atualizadas com sucesso!")
            print("")
            print("📋 Próximos passos:")
            print("   1. Execute: uv run python scripts/seed_roles.py seed")
            print("   2. Implemente os serviços de permissão")
            print("   3. Atualize as rotas com verificação de permissão")
        else:
            print("❌ Erro na criação das tabelas")
            return 1
            
    except Exception as e:
        print(f"❌ Erro durante a execução: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
