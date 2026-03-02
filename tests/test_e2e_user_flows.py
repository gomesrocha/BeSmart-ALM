"""End-to-end tests for user flows by profile."""
import pytest
from httpx import AsyncClient
from uuid import uuid4

from services.shared.database import get_session
from services.identity.models import User, Tenant, Role, UserRole
from services.identity.security import create_access_token
from services.project.models import Project
from services.work_item.models import WorkItem, WorkItemType, WorkItemPriority, WorkItemStatus


class TestE2EUserFlows:
    """End-to-end tests for complete user workflows."""

    @pytest.fixture
    async def setup_company(self, session):
        """Set up a complete company with users and roles."""
        # Create tenant
        tenant = Tenant(
            id=uuid4(),
            name="Acme Corp",
            domain="acme.com",
            is_active=True,
        )
        session.add(tenant)
        await session.commit()
        
        # Create roles
        roles = {}
        for role_name, display_name, description in [
            ("admin", "Administrator", "Full system access"),
            ("po", "Product Owner", "Product management"),
            ("dev", "Developer", "Development tasks"),
            ("qa", "QA Engineer", "Quality assurance"),
            ("auditor", "Auditor", "Read-only access"),
        ]:
            role = Role(
                id=uuid4(),
                tenant_id=tenant.id,
                name=role_name,
                display_name=display_name,
                description=description,
            )
            session.add(role)
            roles[role_name] = role
        
        await session.commit()
        
        # Create users
        users = {}
        for role_name, email, full_name in [
            ("admin", "admin@acme.com", "Alice Admin"),
            ("po", "po@acme.com", "Bob Product"),
            ("dev", "dev@acme.com", "Charlie Developer"),
            ("qa", "qa@acme.com", "Diana QA"),
            ("auditor", "auditor@acme.com", "Eve Auditor"),
        ]:
            user = User(
                id=uuid4(),
                tenant_id=tenant.id,
                email=email,
                full_name=full_name,
                is_active=True,
            )
            user.set_password("password123")
            session.add(user)
            users[role_name] = user
        
        await session.commit()
        
        # Assign roles to users
        for role_name in users.keys():
            user_role = UserRole(
                tenant_id=tenant.id,
                user_id=users[role_name].id,
                role_id=roles[role_name].id,
            )
            session.add(user_role)
        
        await session.commit()
        
        return {
            "tenant": tenant,
            "roles": roles,
            "users": users,
        }

    def get_auth_headers(self, user: User) -> dict:
        """Get authorization headers for user."""
        token = create_access_token(
            data={
                "sub": str(user.id),
                "tenant_id": str(user.tenant_id),
                "email": user.email,
                "is_super_admin": False,
            }
        )
        return {"Authorization": f"Bearer {token}"}

    @pytest.mark.asyncio
    async def test_complete_project_lifecycle(self, client: AsyncClient, setup_company, session):
        """Test complete project lifecycle with different user roles."""
        users = setup_company["users"]
        
        admin_headers = self.get_auth_headers(users["admin"])
        po_headers = self.get_auth_headers(users["po"])
        dev_headers = self.get_auth_headers(users["dev"])
        qa_headers = self.get_auth_headers(users["qa"])
        auditor_headers = self.get_auth_headers(users["auditor"])
        
        # 1. PO creates a project
        response = await client.post(
            "/api/v1/projects",
            json={
                "name": "E-Commerce Platform",
                "description": "New e-commerce platform",
                "settings": {},
            },
            headers=po_headers,
        )
        assert response.status_code == 201
        project = response.json()
        project_id = project["id"]
        
        # 2. PO creates user stories
        user_story_response = await client.post(
            "/api/v1/work-items",
            json={
                "title": "User can add items to cart",
                "description": "As a customer, I want to add items to my cart",
                "type": "user_story",
                "priority": "high",
                "project_id": project_id,
            },
            headers=po_headers,
        )
        assert user_story_response.status_code == 201
        user_story = user_story_response.json()
        
        # 3. PO approves the user story
        response = await client.post(
            f"/api/v1/work-items/{user_story['id']}/transition",
            json={"new_status": "in_review"},
            headers=po_headers,
        )
        assert response.status_code == 200
        
        response = await client.post(
            f"/api/v1/work-items/{user_story['id']}/transition",
            json={"new_status": "approved"},
            headers=po_headers,
        )
        assert response.status_code == 200
        
        # 4. Developer picks up the work
        response = await client.post(
            f"/api/v1/work-items/{user_story['id']}/transition",
            json={"new_status": "in_progress"},
            headers=dev_headers,
        )
        assert response.status_code == 200
        
        # 5. Developer completes the work
        response = await client.post(
            f"/api/v1/work-items/{user_story['id']}/transition",
            json={"new_status": "done"},
            headers=dev_headers,
        )
        assert response.status_code == 200
        
        # 6. QA creates test cases
        test_response = await client.post(
            "/api/v1/work-items",
            json={
                "title": "Test cart functionality",
                "description": "Verify cart operations",
                "type": "test",
                "priority": "high",
                "project_id": project_id,
            },
            headers=qa_headers,
        )
        assert test_response.status_code == 201
        
        # 7. Auditor can view everything but not modify
        response = await client.get("/api/v1/projects", headers=auditor_headers)
        assert response.status_code == 200
        projects = response.json()
        assert any(p["id"] == project_id for p in projects)
        
        response = await client.get("/api/v1/work-items", headers=auditor_headers)
        assert response.status_code == 200
        
        # Auditor cannot create
        response = await client.post(
            "/api/v1/work-items",
            json={
                "title": "Should fail",
                "type": "task",
                "project_id": project_id,
            },
            headers=auditor_headers,
        )
        assert response.status_code == 403
        
        # 8. Admin can view audit logs
        response = await client.get("/api/v1/audit-logs", headers=admin_headers)
        assert response.status_code == 200
        audit_data = response.json()
        
        # Should have logs for all actions
        assert audit_data["pagination"]["total"] >= 5
