"""Specification generation router."""
import logging
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from services.identity.dependencies import (
    PermissionChecker,
    get_current_user,
    get_session,
    get_tenant_id,
)
from services.identity.models import User
from services.identity.permissions import Permission
from services.project.models import Project
from services.project.document_models import ProjectDocument, DocumentType, DocumentCategory
from services.work_item.models import WorkItem
from services.specification.models import ProjectSpecification, ProjectArchitecture
from services.specification.schemas import (
    GenerateSpecificationRequest,
    SpecificationResponse,
    UpdateSpecificationRequest,
)
from services.architecture.schemas import (
    GenerateArchitectureRequest,
    ArchitectureResponse,
    UpdateArchitectureRequest,
)
from services.requirements.ollama_client import OllamaClient
from services.specification.prompts import SPECIFICATION_SYSTEM, SPECIFICATION_PROMPT
from services.architecture.prompts import ARCHITECTURE_SYSTEM, ARCHITECTURE_PROMPT

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/specification", tags=["specification"])


@router.post("/generate", response_model=SpecificationResponse)
async def generate_specification(
    request: GenerateSpecificationRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """Generate specification from project requirements."""
    
    logger.info(f"Generating specification for project {request.project_id}")
    
    # Verify project exists and user has access
    project = await session.get(Project, UUID(request.project_id))
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Projeto não encontrado"
        )
    
    if project.tenant_id != current_user.tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado"
        )
    
    try:
        # Get all requirements (work items) for the project
        result = await session.execute(
            select(WorkItem).where(
                WorkItem.project_id == UUID(request.project_id),
                WorkItem.type == "requirement"
            )
        )
        work_items = result.scalars().all()
        
        if not work_items:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Nenhum requisito encontrado para este projeto. Gere requisitos primeiro."
            )
        
        logger.info(f"Found {len(work_items)} requirements for specification")
        
        # Build requirements summary
        requirements_summary = ""
        for i, item in enumerate(work_items, 1):
            requirements_summary += f"\n{i}. {item.title}\n"
            requirements_summary += f"   {item.description}\n"
        
        # Generate specification using Ollama
        ollama = OllamaClient()
        
        prompt = SPECIFICATION_PROMPT.format(
            project_name=project.name,
            project_description=project.description or "Não especificado",
            target_cloud=project.settings.get("target_cloud", "AWS") if project.settings else "AWS",
            mps_br_level=project.settings.get("mps_br_level", "G") if project.settings else "G",
            requirements_summary=requirements_summary
        )
        
        logger.info("Generating specification with Ollama")
        specification_content = await ollama.generate(
            prompt=prompt,
            system=SPECIFICATION_SYSTEM,
            temperature=0.7,
        )
        
        logger.info(f"Generated specification, length: {len(specification_content)} characters")
        
        # Save specification
        spec = ProjectSpecification(
            tenant_id=current_user.tenant_id,
            project_id=UUID(request.project_id),
            content=specification_content,
            version=1,
            created_by=current_user.id
        )
        
        session.add(spec)
        await session.commit()
        await session.refresh(spec)
        
        logger.info(f"Saved specification with ID {spec.id}")
        
        # Also save as a project document for easy access
        doc = ProjectDocument(
            tenant_id=current_user.tenant_id,
            project_id=UUID(request.project_id),
            name=f"Especificação Técnica - {project.name}",
            type=DocumentType.OTHER,
            category=DocumentCategory.SPECIFICATION,
            content=specification_content,
            is_generated=True,
            generated_from="specification",
            is_editable=True,
            version=1,
            uploaded_by=current_user.id
        )
        
        session.add(doc)
        await session.commit()
        await session.refresh(doc)
        
        logger.info(f"Saved specification as document with ID {doc.id}")
        
        return SpecificationResponse(
            project_id=request.project_id,
            specification=specification_content,
            version=1,
            document_id=str(doc.id)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating specification: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Falha ao gerar especificação: {str(e)}"
        )


@router.get("/{project_id}", response_model=SpecificationResponse)
async def get_specification(
    project_id: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """Get specification for a project."""
    
    # Verify project exists and user has access
    project = await session.get(Project, UUID(project_id))
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Projeto não encontrado"
        )
    
    if project.tenant_id != current_user.tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado"
        )
    
    # Get latest specification
    result = await session.execute(
        select(ProjectSpecification)
        .where(ProjectSpecification.project_id == UUID(project_id))
        .order_by(ProjectSpecification.version.desc())
        .limit(1)
    )
    spec = result.scalar_one_or_none()
    
    if not spec:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Especificação não encontrada. Gere uma especificação primeiro."
        )
    
    return SpecificationResponse(
        project_id=project_id,
        specification=spec.content,
        version=spec.version
    )


@router.post("/architecture/generate", response_model=ArchitectureResponse)
async def generate_architecture(
    request: GenerateArchitectureRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """Generate architecture from project requirements."""
    
    logger.info(f"Generating architecture for project {request.project_id}")
    
    # Verify project exists and user has access
    project = await session.get(Project, UUID(request.project_id))
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Projeto não encontrado"
        )
    
    if project.tenant_id != current_user.tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado"
        )
    
    try:
        # Get all requirements (work items) for the project
        result = await session.execute(
            select(WorkItem).where(
                WorkItem.project_id == UUID(request.project_id),
                WorkItem.type == "requirement"
            )
        )
        work_items = result.scalars().all()
        
        if not work_items:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Nenhum requisito encontrado para este projeto. Gere requisitos primeiro."
            )
        
        logger.info(f"Found {len(work_items)} requirements for architecture")
        
        # Build requirements summary
        requirements_summary = ""
        for i, item in enumerate(work_items, 1):
            requirements_summary += f"\n{i}. {item.title}\n"
            requirements_summary += f"   {item.description}\n"
        
        # Generate architecture using Ollama
        ollama = OllamaClient()
        
        prompt = ARCHITECTURE_PROMPT.format(
            project_name=project.name,
            project_description=project.description or "Não especificado",
            target_cloud=project.settings.get("target_cloud", "AWS") if project.settings else "AWS",
            mps_br_level=project.settings.get("mps_br_level", "G") if project.settings else "G",
            requirements_summary=requirements_summary
        )
        
        logger.info("Generating architecture with Ollama")
        architecture_content = await ollama.generate(
            prompt=prompt,
            system=ARCHITECTURE_SYSTEM,
            temperature=0.7,
        )
        
        logger.info(f"Generated architecture, length: {len(architecture_content)} characters")
        
        # Extract Mermaid diagrams
        diagrams = []
        lines = architecture_content.split('\n')
        in_mermaid = False
        current_diagram = []
        
        for line in lines:
            if '```mermaid' in line:
                in_mermaid = True
                current_diagram = []
            elif '```' in line and in_mermaid:
                in_mermaid = False
                if current_diagram:
                    diagrams.append('\n'.join(current_diagram))
            elif in_mermaid:
                current_diagram.append(line)
        
        logger.info(f"Extracted {len(diagrams)} Mermaid diagrams")
        
        # Save architecture
        arch = ProjectArchitecture(
            tenant_id=current_user.tenant_id,
            project_id=UUID(request.project_id),
            content=architecture_content,
            version=1,
            created_by=current_user.id
        )
        
        session.add(arch)
        await session.commit()
        await session.refresh(arch)
        
        logger.info(f"Saved architecture with ID {arch.id}")
        
        # Also save as a project document for easy access
        doc = ProjectDocument(
            tenant_id=current_user.tenant_id,
            project_id=UUID(request.project_id),
            name=f"Arquitetura - {project.name}",
            type=DocumentType.OTHER,
            category=DocumentCategory.ARCHITECTURE,
            content=architecture_content,
            is_generated=True,
            generated_from="architecture",
            is_editable=True,
            version=1,
            uploaded_by=current_user.id
        )
        
        session.add(doc)
        await session.commit()
        await session.refresh(doc)
        
        logger.info(f"Saved architecture as document with ID {doc.id}")
        
        return ArchitectureResponse(
            project_id=request.project_id,
            architecture=architecture_content,
            diagrams=diagrams,
            version=1,
            document_id=str(doc.id)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating architecture: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Falha ao gerar arquitetura: {str(e)}"
        )


@router.get("/architecture/{project_id}", response_model=ArchitectureResponse)
async def get_architecture(
    project_id: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """Get architecture for a project."""
    
    # Verify project exists and user has access
    project = await session.get(Project, UUID(project_id))
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Projeto não encontrado"
        )
    
    if project.tenant_id != current_user.tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado"
        )
    
    # Get latest architecture
    result = await session.execute(
        select(ProjectArchitecture)
        .where(ProjectArchitecture.project_id == UUID(project_id))
        .order_by(ProjectArchitecture.version.desc())
        .limit(1)
    )
    arch = result.scalar_one_or_none()
    
    if not arch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Arquitetura não encontrada. Gere uma arquitetura primeiro."
        )
    
    # Extract diagrams
    diagrams = []
    lines = arch.content.split('\n')
    in_mermaid = False
    current_diagram = []
    
    for line in lines:
        if '```mermaid' in line:
            in_mermaid = True
            current_diagram = []
        elif '```' in line and in_mermaid:
            in_mermaid = False
            if current_diagram:
                diagrams.append('\n'.join(current_diagram))
        elif in_mermaid:
            current_diagram.append(line)
    
    return ArchitectureResponse(
        project_id=project_id,
        architecture=arch.content,
        diagrams=diagrams,
        version=arch.version
    )
