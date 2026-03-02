"""Project document router."""
import hashlib
import os
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from services.identity.dependencies import (
    PermissionChecker,
    get_current_user,
    get_tenant_id,
)
from services.identity.models import User
from services.identity.permissions import Permission
from services.project.document_models import DocumentType, ProjectDocument
from services.project.document_schemas import (
    ProjectDocumentCreate,
    ProjectDocumentResponse,
    ProjectDocumentUpdate,
)
from services.project.models import Project
from services.requirements.document_processor import DocumentProcessor
from services.shared.database import get_session

router = APIRouter(prefix="/projects", tags=["Project Documents"])

# Directory for storing uploaded files
UPLOAD_DIR = "uploads/documents"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.get("/{project_id}/documents", response_model=list[ProjectDocumentResponse])
async def list_project_documents(
    project_id: UUID,
    session: Annotated[AsyncSession, Depends(get_session)],
    tenant_id: Annotated[UUID, Depends(get_tenant_id)],
    current_user: Annotated[User, Depends(PermissionChecker(Permission.PROJECT_READ))],
    category: str | None = None,
) -> list[ProjectDocumentResponse]:
    """List project documents."""
    # Verify project exists and user has access
    project = await session.get(Project, project_id)
    if not project or project.tenant_id != tenant_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    query = select(ProjectDocument).where(
        ProjectDocument.project_id == project_id,
        ProjectDocument.tenant_id == tenant_id,
    )
    
    if category:
        query = query.where(ProjectDocument.category == category)
    
    query = query.order_by(ProjectDocument.uploaded_at.desc())
    
    result = await session.execute(query)
    documents = result.scalars().all()
    
    return [ProjectDocumentResponse.model_validate(doc) for doc in documents]


@router.post("/{project_id}/documents/upload", response_model=ProjectDocumentResponse)
async def upload_document(
    project_id: UUID,
    session: Annotated[AsyncSession, Depends(get_session)],
    tenant_id: Annotated[UUID, Depends(get_tenant_id)],
    current_user: Annotated[User, Depends(PermissionChecker(Permission.PROJECT_UPDATE))],
    file: UploadFile = File(...),
    category: str = Form("other"),
    description: str | None = Form(None),
) -> ProjectDocumentResponse:
    """Upload document to project."""
    # Verify project exists
    project = await session.get(Project, project_id)
    if not project or project.tenant_id != tenant_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    # Read file content
    content = await file.read()
    
    # Calculate hash
    content_hash = hashlib.sha256(content).hexdigest()
    
    # Determine document type
    file_ext = os.path.splitext(file.filename)[1].lower()
    doc_type_map = {
        ".pdf": DocumentType.PDF,
        ".docx": DocumentType.DOCX,
        ".doc": DocumentType.DOCX,
        ".txt": DocumentType.TXT,
    }
    doc_type = doc_type_map.get(file_ext, DocumentType.OTHER)
    
    # Save file
    file_path = os.path.join(UPLOAD_DIR, f"{tenant_id}_{project_id}_{content_hash}{file_ext}")
    with open(file_path, "wb") as f:
        f.write(content)
    
    # Extract and index content
    processor = DocumentProcessor()
    try:
        extracted_text = processor.process_document(file.filename, content)
        chunks = processor.chunk_text(extracted_text, chunk_size=512, overlap=50)
        is_indexed = True
        chunk_count = len(chunks)
    except Exception:
        is_indexed = False
        chunk_count = 0
    
    # Create document record
    document = ProjectDocument(
        tenant_id=tenant_id,
        project_id=project_id,
        name=file.filename,
        type=doc_type,
        category=category,
        file_path=file_path,
        file_size=len(content),
        content_hash=content_hash,
        description=description,
        uploaded_by=current_user.id,
        is_indexed=is_indexed,
        chunk_count=chunk_count,
    )
    
    session.add(document)
    await session.commit()
    await session.refresh(document)
    
    return ProjectDocumentResponse.model_validate(document)


@router.post("/{project_id}/documents/url", response_model=ProjectDocumentResponse)
async def add_url_document(
    project_id: UUID,
    session: Annotated[AsyncSession, Depends(get_session)],
    tenant_id: Annotated[UUID, Depends(get_tenant_id)],
    current_user: Annotated[User, Depends(PermissionChecker(Permission.PROJECT_UPDATE))],
    url: str = Form(...),
    name: str = Form(...),
    category: str = Form("other"),
    description: str | None = Form(None),
) -> ProjectDocumentResponse:
    """Add URL document to project."""
    # Verify project exists
    project = await session.get(Project, project_id)
    if not project or project.tenant_id != tenant_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )
    
    # Scrape and index URL
    from services.requirements.web_scraper import WebScraper
    
    scraper = WebScraper()
    try:
        extracted_text = await scraper.scrape_url(url)
        processor = DocumentProcessor()
        chunks = processor.chunk_text(extracted_text, chunk_size=512, overlap=50)
        is_indexed = True
        chunk_count = len(chunks)
    except Exception:
        is_indexed = False
        chunk_count = 0
    
    # Calculate hash of URL
    content_hash = hashlib.sha256(url.encode()).hexdigest()
    
    # Create document record
    document = ProjectDocument(
        tenant_id=tenant_id,
        project_id=project_id,
        name=name,
        type=DocumentType.URL,
        category=category,
        url=url,
        content_hash=content_hash,
        description=description,
        uploaded_by=current_user.id,
        is_indexed=is_indexed,
        chunk_count=chunk_count,
    )
    
    session.add(document)
    await session.commit()
    await session.refresh(document)
    
    return ProjectDocumentResponse.model_validate(document)


@router.patch("/{project_id}/documents/{document_id}", response_model=ProjectDocumentResponse)
async def update_document(
    project_id: UUID,
    document_id: UUID,
    document_data: ProjectDocumentUpdate,
    session: Annotated[AsyncSession, Depends(get_session)],
    tenant_id: Annotated[UUID, Depends(get_tenant_id)],
    current_user: Annotated[User, Depends(PermissionChecker(Permission.PROJECT_UPDATE))],
) -> ProjectDocumentResponse:
    """Update document metadata."""
    document = await session.get(ProjectDocument, document_id)
    if not document or document.tenant_id != tenant_id or document.project_id != project_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )
    
    if document_data.name is not None:
        document.name = document_data.name
    if document_data.category is not None:
        document.category = document_data.category
    if document_data.description is not None:
        document.description = document_data.description
    
    session.add(document)
    await session.commit()
    await session.refresh(document)
    
    return ProjectDocumentResponse.model_validate(document)


@router.delete("/{project_id}/documents/{document_id}")
async def delete_document(
    project_id: UUID,
    document_id: UUID,
    session: Annotated[AsyncSession, Depends(get_session)],
    tenant_id: Annotated[UUID, Depends(get_tenant_id)],
    current_user: Annotated[User, Depends(PermissionChecker(Permission.PROJECT_UPDATE))],
) -> dict[str, str]:
    """Delete document."""
    document = await session.get(ProjectDocument, document_id)
    if not document or document.tenant_id != tenant_id or document.project_id != project_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )
    
    # Delete file if exists
    if document.file_path and os.path.exists(document.file_path):
        os.remove(document.file_path)
    
    await session.delete(document)
    await session.commit()
    
    return {"message": "Document deleted"}


@router.patch("/{project_id}/documents/{document_id}/content")
async def update_document_content(
    project_id: UUID,
    document_id: UUID,
    content: Annotated[str, Form()],
    session: Annotated[AsyncSession, Depends(get_session)],
    tenant_id: Annotated[UUID, Depends(get_tenant_id)],
    current_user: Annotated[User, Depends(PermissionChecker(Permission.PROJECT_UPDATE))],
) -> ProjectDocumentResponse:
    """Update content of a generated/editable document."""
    document = await session.get(ProjectDocument, document_id)
    if not document or document.tenant_id != tenant_id or document.project_id != project_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )
    
    if not document.is_editable:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This document is not editable",
        )
    
    # Update content and increment version
    document.content = content
    document.version += 1
    
    session.add(document)
    await session.commit()
    await session.refresh(document)
    
    return ProjectDocumentResponse.model_validate(document)


@router.get("/{project_id}/documents/{document_id}/content")
async def get_document_content(
    project_id: UUID,
    document_id: UUID,
    session: Annotated[AsyncSession, Depends(get_session)],
    tenant_id: Annotated[UUID, Depends(get_tenant_id)],
    current_user: Annotated[User, Depends(PermissionChecker(Permission.PROJECT_READ))],
):
    """Get content of a document."""
    document = await session.get(ProjectDocument, document_id)
    if not document or document.tenant_id != tenant_id or document.project_id != project_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )
    
    return {
        "content": document.content or "",
        "version": str(document.version) if document.version else "1",
        "is_editable": str(document.is_editable).lower() if document.is_editable is not None else "true",
    }
