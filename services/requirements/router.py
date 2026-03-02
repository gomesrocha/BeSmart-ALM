"""Requirements generation router."""
import json
import logging
import re
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List

from services.identity.dependencies import (
    PermissionChecker,
    get_current_user,
    get_session,
    get_tenant_id,
)
from services.identity.models import User
from services.identity.permissions import Permission
from services.project.models import Project
from services.work_item.models import WorkItem
from services.requirements.schemas import (
    GenerateRequirementsRequest,
    GenerateRequirementsResponse,
    ApproveRequirementsRequest,
    RequirementItem,
)
from services.requirements.schemas_refine import (
    RefineRequirementsRequest,
    RefineRequirementsResponse,
)
from services.requirements.ollama_client import OllamaClient
from services.requirements.document_processor import DocumentProcessor
from services.requirements.embeddings import EmbeddingsClient
from services.requirements.web_scraper import WebScraper
from services.requirements.prompts import (
    REQUIREMENTS_GENERATION_SYSTEM,
    REQUIREMENTS_GENERATION_PROMPT,
)
from sqlmodel import select

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/requirements", tags=["requirements"])


def parse_json_response(response_text: str) -> dict:
    """Parse JSON response from Ollama with error handling and fixes."""
    response_text = response_text.strip()
    
    # Remove markdown code blocks if present
    if response_text.startswith('```'):
        lines = response_text.split('\n')
        lines = lines[1:]  # Remove first line (```json or ```)
        if lines and lines[-1].strip() == '```':
            lines = lines[:-1]  # Remove last line if it's ```
        response_text = '\n'.join(lines).strip()
    
    start_idx = response_text.find('{')
    end_idx = response_text.rfind('}') + 1
    
    if start_idx == -1 or end_idx == 0:
        raise ValueError("No JSON found in AI response")
    
    json_text = response_text[start_idx:end_idx]
    
    try:
        return json.loads(json_text)
    except json.JSONDecodeError as e:
        # Try to fix common JSON issues
        # Remove trailing commas
        json_text = re.sub(r',(\s*[}\]])', r'\1', json_text)
        
        try:
            return json.loads(json_text)
        except json.JSONDecodeError:
            # Try to truncate at last valid closing brace
            last_complete = json_text.rfind('}')
            if last_complete > 0:
                # Try to close the array and object
                json_text = json_text[:last_complete+1] + ']}'
                try:
                    return json.loads(json_text)
                except json.JSONDecodeError:
                    raise ValueError(f"Failed to parse AI response as valid JSON: {str(e)}")
            else:
                raise ValueError(f"Failed to parse AI response as valid JSON: {str(e)}")


@router.post("/generate", response_model=GenerateRequirementsResponse)
async def generate_requirements(
    request: GenerateRequirementsRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """Generate requirements from project description using AI."""
    
    # Verify project exists and user has access
    project = await session.get(Project, UUID(request.project_id))
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    if project.tenant_id != current_user.tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    # Generate requirements using Ollama
    ollama = OllamaClient()
    
    prompt = REQUIREMENTS_GENERATION_PROMPT.format(
        project_name=project.name,
        project_description=request.description
    )
    
    try:
        response_text = await ollama.generate(
            prompt=prompt,
            system=REQUIREMENTS_GENERATION_SYSTEM,
            temperature=0.7,
        )
        
        # Parse JSON response
        # Try to extract JSON from response
        
        # Parse JSON response
        parsed = parse_json_response(response_text)
        
        requirements = [
            RequirementItem(**req) for req in parsed.get("requirements", [])
        ]
        
        return GenerateRequirementsResponse(
            requirements=requirements,
            project_id=request.project_id
        )
        
    except json.JSONDecodeError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to parse AI response: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate requirements: {str(e)}"
        )


@router.post("/generate-from-document", response_model=GenerateRequirementsResponse)
async def generate_requirements_from_document(
    project_id: str = Form(...),
    file: UploadFile = File(...),
    additional_context: Optional[str] = Form(None),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """Generate requirements from uploaded document using RAG."""
    
    # Verify project exists and user has access
    project = await session.get(Project, UUID(project_id))
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    if project.tenant_id != current_user.tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    try:
        # Read file content
        file_content = await file.read()
        
        # Extract text from document
        processor = DocumentProcessor()
        extracted_text = processor.process_document(file.filename, file_content)
        
        if not extracted_text:
            raise ValueError("No text could be extracted from the document")
        
        # Save document to project
        import hashlib
        import os
        from services.project.document_models import DocumentType, ProjectDocument
        
        # Calculate hash
        content_hash = hashlib.sha256(file_content).hexdigest()
        
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
        UPLOAD_DIR = "uploads/documents"
        os.makedirs(UPLOAD_DIR, exist_ok=True)
        file_path = os.path.join(UPLOAD_DIR, f"{project.tenant_id}_{project_id}_{content_hash}{file_ext}")
        with open(file_path, "wb") as f:
            f.write(file_content)
        
        # Chunk the text for better processing
        chunks = processor.chunk_text(extracted_text, chunk_size=512, overlap=50)
        
        # Create document record
        document = ProjectDocument(
            tenant_id=project.tenant_id,
            project_id=UUID(project_id),
            name=file.filename,
            type=doc_type,
            category="requirements",  # Default category for uploaded requirements
            file_path=file_path,
            file_size=len(file_content),
            content_hash=content_hash,
            description=f"Uploaded for requirements generation{f': {additional_context}' if additional_context else ''}",
            uploaded_by=current_user.id,
            is_indexed=True,
            chunk_count=len(chunks),
        )
        
        session.add(document)
        await session.commit()
        
        # Use RAG to find most relevant chunks
        embeddings_client = EmbeddingsClient()
        
        # Create query for finding relevant content
        query = f"requirements specifications features functionality for {project.name}"
        if additional_context:
            query += f" {additional_context}"
        
        # Find most relevant chunks
        relevant_chunks = await embeddings_client.find_most_relevant(
            query=query,
            documents=chunks,
            top_k=5
        )
        
        # Combine relevant chunks
        context = "\n\n".join([chunk for chunk, _ in relevant_chunks])
        
        # Generate requirements using the context
        ollama = OllamaClient()
        
        prompt = f"""Based on the following document content about {project.name}, generate comprehensive requirements in Gherkin format:

Document Content:
{context}

{f"Additional Context: {additional_context}" if additional_context else ""}

{REQUIREMENTS_GENERATION_PROMPT.format(
    project_name=project.name,
    project_description=f"Based on the document content above{f' and: {additional_context}' if additional_context else ''}"
)}"""
        
        response_text = await ollama.generate(
            prompt=prompt,
            system=REQUIREMENTS_GENERATION_SYSTEM,
            temperature=0.7,
        )
        
        # Parse JSON response
        parsed = parse_json_response(response_text)
        
        requirements = [
            RequirementItem(**req) for req in parsed.get("requirements", [])
        ]
        
        return GenerateRequirementsResponse(
            requirements=requirements,
            project_id=project_id
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except json.JSONDecodeError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to parse AI response: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate requirements from document: {str(e)}"
        )


@router.post("/approve")
async def approve_requirements(
    request: ApproveRequirementsRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """Approve requirements and create work items."""
    
    # Verify project exists and user has access
    project = await session.get(Project, UUID(request.project_id))
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    if project.tenant_id != current_user.tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    # Create work items from approved requirements
    created_items = []
    
    for req in request.requirements:
        # Create description with acceptance criteria
        description = f"{req.user_story}\n\n"
        description += "Acceptance Criteria:\n"
        for i, criteria in enumerate(req.acceptance_criteria, 1):
            description += f"{i}. {criteria}\n"
        
        work_item = WorkItem(
            tenant_id=current_user.tenant_id,
            project_id=UUID(request.project_id),
            type=req.type,
            title=req.title,
            description=description,
            status="draft",
            version=1,
            created_by=current_user.id,
        )
        
        session.add(work_item)
        created_items.append(work_item)
    
    await session.commit()
    
    return {
        "message": f"Created {len(created_items)} work items",
        "work_items": [
            {
                "id": str(item.id),
                "title": item.title,
                "type": item.type,
            }
            for item in created_items
        ]
    }


@router.post("/generate-from-url", response_model=GenerateRequirementsResponse)
async def generate_requirements_from_url(
    project_id: str = Form(...),
    url: str = Form(...),
    additional_context: Optional[str] = Form(None),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """Generate requirements from web page URL using RAG."""
    
    logger.info(f"Starting URL requirements generation for project {project_id}, URL: {url}")
    
    # Verify project exists and user has access
    project = await session.get(Project, UUID(project_id))
    if not project:
        logger.error(f"Project not found: {project_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    if project.tenant_id != current_user.tenant_id:
        logger.error(f"Access denied for user {current_user.id} to project {project_id}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    try:
        # Check URL whitelist
        whitelist = project.settings.get("whitelist_urls", []) if project.settings else []
        logger.info(f"Project whitelist: {whitelist}")
        
        scraper = WebScraper()
        
        if whitelist and not scraper.is_url_allowed(url, whitelist):
            logger.warning(f"URL {url} not in whitelist {whitelist}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"URL not in project whitelist. Allowed domains: {', '.join(whitelist)}"
            )
        
        # Scrape URL
        logger.info(f"Starting to scrape URL: {url}")
        extracted_text = await scraper.scrape_url(url)
        logger.info(f"Successfully extracted {len(extracted_text)} characters from URL")
        
        if not extracted_text:
            logger.error("No text extracted from URL")
            raise ValueError("No text could be extracted from the URL")
        
        # Chunk the text for better processing
        logger.info("Chunking extracted text")
        processor = DocumentProcessor()
        chunks = processor.chunk_text(extracted_text, chunk_size=512, overlap=50)
        logger.info(f"Created {len(chunks)} chunks from extracted text")
        
        # Use RAG to find most relevant chunks
        logger.info("Finding most relevant chunks using embeddings")
        embeddings_client = EmbeddingsClient()
        
        # Create query for finding relevant content
        query = f"requirements specifications features functionality for {project.name}"
        if additional_context:
            query += f" {additional_context}"
        logger.info(f"Search query: {query}")
        
        # Find most relevant chunks
        relevant_chunks = await embeddings_client.find_most_relevant(
            query=query,
            documents=chunks,
            top_k=5
        )
        logger.info(f"Found {len(relevant_chunks)} relevant chunks")
        
        # Combine relevant chunks
        context = "\n\n".join([chunk for chunk, _ in relevant_chunks])
        logger.info(f"Combined context length: {len(context)} characters")
        
        # Generate requirements using the context
        logger.info("Generating requirements with Ollama")
        ollama = OllamaClient()
        
        prompt = f"""Based on the following web page content about {project.name}, generate comprehensive requirements in Gherkin format:

URL: {url}

Web Page Content:
{context}

{f"Additional Context: {additional_context}" if additional_context else ""}

{REQUIREMENTS_GENERATION_PROMPT.format(
    project_name=project.name,
    project_description=f"Based on the web page content above{f' and: {additional_context}' if additional_context else ''}"
)}"""
        
        logger.info(f"Prompt length: {len(prompt)} characters")
        
        response_text = await ollama.generate(
            prompt=prompt,
            system=REQUIREMENTS_GENERATION_SYSTEM,
            temperature=0.7,
        )
        
        logger.info(f"Received response from Ollama, length: {len(response_text)} characters")
        
        # Parse JSON response
        
        # Parse JSON response
        logger.info(f"Parsing JSON response (length: {len(response_text)} chars)")
        parsed = parse_json_response(response_text)
        logger.info(f"Successfully parsed JSON with {len(parsed.get('requirements', []))} requirements")
        
        requirements = [
            RequirementItem(**req) for req in parsed.get("requirements", [])
        ]
        
        logger.info(f"Successfully generated {len(requirements)} requirements from URL")
        
        return GenerateRequirementsResponse(
            requirements=requirements,
            project_id=project_id
        )
        
    except HTTPException:
        raise
    except ValueError as e:
        logger.error(f"ValueError in URL generation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to parse AI response as JSON. The AI response might be malformed. Error: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Unexpected error in URL generation: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate requirements from URL: {str(e)}"
        )



@router.post("/refine", response_model=RefineRequirementsResponse)
async def refine_requirements(
    request: RefineRequirementsRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """Refine existing requirements based on feedback."""
    
    # Verify project exists and user has access
    project = await session.get(Project, UUID(request.project_id))
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    if project.tenant_id != current_user.tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    try:
        # Build context from existing requirements
        existing_context = "Existing Requirements:\n\n"
        for i, req in enumerate(request.existing_requirements, 1):
            existing_context += f"{i}. {req.title}\n"
            if isinstance(req.user_story, dict):
                existing_context += f"   As a {req.user_story['as_a']}\n"
                existing_context += f"   I want {req.user_story['i_want']}\n"
                existing_context += f"   So that {req.user_story['so_that']}\n"
            else:
                existing_context += f"   {req.user_story}\n"
            existing_context += "\n"
        
        # Create prompt based on operation
        if request.operation == "add_more":
            operation_instruction = f"""Generate ADDITIONAL requirements that complement the existing ones.
Do NOT repeat or modify existing requirements.
Focus on: {request.feedback}"""
        elif request.operation == "improve":
            operation_instruction = f"""Improve and refine the EXISTING requirements based on this feedback:
{request.feedback}

Keep the same number of requirements but make them better, more detailed, and more testable."""
        else:  # refine
            operation_instruction = f"""Based on this feedback: {request.feedback}

Generate refined requirements that address the feedback while maintaining consistency with existing requirements."""
        
        ollama = OllamaClient()
        
        prompt = f"""{existing_context}

{operation_instruction}

Project: {project.name}

{REQUIREMENTS_GENERATION_PROMPT.format(
    project_name=project.name,
    project_description=f"Continue from the existing requirements above. {request.feedback}"
)}"""
        
        response_text = await ollama.generate(
            prompt=prompt,
            system=REQUIREMENTS_GENERATION_SYSTEM,
            temperature=0.7,
        )
        
        # Parse JSON response
        parsed = parse_json_response(response_text)
        
        new_requirements = [
            RequirementItem(**req) for req in parsed.get("requirements", [])
        ]
        
        # Calculate iteration number
        iteration = len(request.existing_requirements) // 5 + 1
        
        return RefineRequirementsResponse(
            requirements=new_requirements,
            project_id=request.project_id,
            iteration=iteration
        )
        
    except json.JSONDecodeError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to parse AI response: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to refine requirements: {str(e)}"
        )
