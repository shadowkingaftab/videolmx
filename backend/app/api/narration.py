"""Narration management API endpoints."""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query

from app.dependencies import (
    get_current_user,
    get_narration_service,
)
from app.models.user import User
from app.services.narration_service import NarrationService
from app.schemas.narration import (
    NarrationCreate,
    NarrationUpdate,
    NarrationResponse,
    NarrationListResponse,
    NarrationGenerateRequest,
    VoicePreviewRequest,
    VoicePreviewResponse,
)
from app.schemas.common import PaginatedResponse
from app.core.errors import NotFoundError, ValidationError

router = APIRouter()


@router.get("/", response_model=PaginatedResponse[NarrationListResponse])
async def list_narrations(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    script_id: Optional[UUID] = None,
    current_user: User = Depends(get_current_user),
    narration_service: NarrationService = Depends(get_narration_service),
):
    """List narrations."""
    skip = (page - 1) * page_size
    
    narrations, total = await narration_service.list_narrations(
        user_id=current_user.id,
        script_id=script_id,
        skip=skip,
        limit=page_size,
    )
    
    return PaginatedResponse(
        items=narrations,
        total=total,
        page=page,
        page_size=page_size,
        pages=(total + page_size - 1) // page_size,
    )


@router.post("/", response_model=NarrationResponse, status_code=status.HTTP_201_CREATED)
async def create_narration(
    request: NarrationCreate,
    current_user: User = Depends(get_current_user),
    narration_service: NarrationService = Depends(get_narration_service),
):
    """Create a new narration."""
    try:
        narration = await narration_service.create_narration(
            script_id=request.script_id,
            user_id=current_user.id,
            name=request.name,
            voice_id=request.voice_id,
            language=request.language,
        )
        return narration
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.get("/{narration_id}", response_model=NarrationResponse)
async def get_narration(
    narration_id: UUID,
    current_user: User = Depends(get_current_user),
    narration_service: NarrationService = Depends(get_narration_service),
):
    """Get narration by ID."""
    narration = await narration_service.get_narration(narration_id)
    if not narration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Narration not found",
        )
    
    # Check access
    script = await narration_service.get_script(narration.script_id)
    storyboard = await narration_service.get_storyboard(script.storyboard_id)
    project = await narration_service.get_project(storyboard.project_id)
    if project.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )
    
    return narration


@router.patch("/{narration_id}", response_model=NarrationResponse)
async def update_narration(
    narration_id: UUID,
    request: NarrationUpdate,
    current_user: User = Depends(get_current_user),
    narration_service: NarrationService = Depends(get_narration_service),
):
    """Update narration."""
    narration = await narration_service.get_narration(narration_id)
    if not narration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Narration not found",
        )
    
    # Check access
    script = await narration_service.get_script(narration.script_id)
    storyboard = await narration_service.get_storyboard(script.storyboard_id)
    project = await narration_service.get_project(storyboard.project_id)
    if project.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )
    
    updated = await narration_service.update_narration(
        narration_id=narration_id,
        updates=request.dict(exclude_unset=True),
    )
    return updated


@router.delete("/{narration_id}")
async def delete_narration(
    narration_id: UUID,
    current_user: User = Depends(get_current_user),
    narration_service: NarrationService = Depends(get_narration_service),
):
    """Delete narration."""
    narration = await narration_service.get_narration(narration_id)
    if not narration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Narration not found",
        )
    
    # Check access
    script = await narration_service.get_script(narration.script_id)
    storyboard = await narration_service.get_storyboard(script.storyboard_id)
    project = await narration_service.get_project(storyboard.project_id)
    if project.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )
    
    await narration_service.delete_narration(narration_id)
    return {"message": "Narration deleted successfully"}


@router.post("/{narration_id}/generate")
async def generate_narration(
    narration_id: UUID,
    request: NarrationGenerateRequest,
    current_user: User = Depends(get_current_user),
    narration_service: NarrationService = Depends(get_narration_service),
):
    """Generate narration audio."""
    narration = await narration_service.get_narration(narration_id)
    if not narration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Narration not found",
        )
    
    # Check access
    script = await narration_service.get_script(narration.script_id)
    storyboard = await narration_service.get_storyboard(script.storyboard_id)
    project = await narration_service.get_project(storyboard.project_id)
    if project.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )
    
    job_id = await narration_service.generate_narration(
        narration_id=narration_id,
        voice_id=request.voice_id,
        speed=request.speed,
        pitch=request.pitch,
        emotion=request.emotion,
    )
    return {
        "message": "Narration generation started",
        "job_id": job_id,
        "narration_id": narration_id,
    }


@router.get("/{narration_id}/audio")
async def get_narration_audio(
    narration_id: UUID,
    current_user: User = Depends(get_current_user),
    narration_service: NarrationService = Depends(get_narration_service),
):
    """Get narration audio stream."""
    narration = await narration_service.get_narration(narration_id)
    if not narration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Narration not found",
        )
    
    audio_url = await narration_service.get_audio_url(narration_id)
    return {"audio_url": audio_url}


@router.post("/voice/preview", response_model=VoicePreviewResponse)
async def preview_voice(
    request: VoicePreviewRequest,
    narration_service: NarrationService = Depends(get_narration_service),
):
    """Preview a voice with sample text."""
    preview = await narration_service.preview_voice(
        voice_id=request.voice_id,
        text=request.text,
        speed=request.speed,
        pitch=request.pitch,
    )
    return preview


@router.get("/voices")
async def list_voices(
    current_user: User = Depends(get_current_user),
    narration_service: NarrationService = Depends(get_narration_service),
):
    """List available voices."""
    voices = await narration_service.list_voices()
    return voices


@router.get("/voices/{voice_id}")
async def get_voice(
    voice_id: str,
    current_user: User = Depends(get_current_user),
    narration_service: NarrationService = Depends(get_narration_service),
):
    """Get voice details."""
    voice = await narration_service.get_voice(voice_id)
    if not voice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Voice not found",
        )
    return voice