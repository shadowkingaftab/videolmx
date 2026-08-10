"""Asset service."""

from typing import Optional, List, Tuple, Dict, Any
from uuid import UUID
from fastapi import UploadFile

from app.models.asset import Asset
from app.repositories.asset_repository import AssetRepository
from app.repositories.project_repository import ProjectRepository
from app.core.errors import NotFoundError, ValidationError
from app.storage.object_store import get_storage
from app.core.task_queue import get_queue


class AssetService:
    """Asset service."""
    
    def __init__(
        self,
        asset_repo: AssetRepository,
        project_repo: ProjectRepository
    ):
        self.asset_repo = asset_repo
        self.project_repo = project_repo
    
    async def upload_asset(
        self,
        project_id: UUID,
        user_id: UUID,
        file: UploadFile,
        asset_type: str,
        name: Optional[str] = None
    ) -> Asset:
        """Upload a new asset."""
        project = await self.project_repo.get(project_id)
        if not project:
            raise NotFoundError("Project not found")
        
        # Validate file type
        if asset_type == "image" and not file.content_type.startswith("image/"):
            raise ValidationError("Invalid image file")
        elif asset_type == "video" and not file.content_type.startswith("video/"):
            raise ValidationError("Invalid video file")
        
        # Generate storage key
        storage_key = f"projects/{project_id}/assets/{UUID(int=0)}/{file.filename}"
        
        # Upload to storage
        storage = await get_storage()
        content = await file.read()
        await storage.upload(
            bucket="assets",
            key=storage_key,
            data=content,
            content_type=file.content_type,
        )
        
        # Create asset record
        asset = Asset(
            project_id=project_id,
            name=name or file.filename or "untitled",
            type=asset_type,
            storage_key=storage_key,
            size=len(content),
            content_type=file.content_type,
            metadata={"original_filename": file.filename},
        )
        
        return await self.asset_repo.create(asset)
    
    async def get_asset(self, asset_id: UUID) -> Optional[Asset]:
        """Get asset by ID."""
        return await self.asset_repo.get(asset_id)
    
    async def list_assets(
        self,
        user_id: UUID,
        project_id: Optional[UUID] = None,
        asset_type: Optional[str] = None,
        skip: int = 0,
        limit: int = 20
    ) -> Tuple[List[Asset], int]:
        """List assets."""
        return await self.asset_repo.list_by_user(
            user_id=user_id,
            project_id=project_id,
            asset_type=asset_type,
            skip=skip,
            limit=limit
        )
    
    async def update_asset(
        self,
        asset_id: UUID,
        updates: Dict[str, Any]
    ) -> Asset:
        """Update asset metadata."""
        asset = await self.asset_repo.get(asset_id)
        if not asset:
            raise NotFoundError("Asset not found")
        
        for key, value in updates.items():
            if hasattr(asset, key):
                setattr(asset, key, value)
        
        return await self.asset_repo.update(asset)
    
    async def delete_asset(self, asset_id: UUID) -> None:
        """Delete asset."""
        asset = await self.asset_repo.get(asset_id)
        if not asset:
            raise NotFoundError("Asset not found")
        
        # Delete from storage
        storage = await get_storage()
        await storage.delete(
            bucket="assets",
            key=asset.storage_key,
        )
        
        await self.asset_repo.delete(asset)
    
    async def get_download_url(self, asset_id: UUID) -> Optional[str]:
        """Get asset download URL."""
        asset = await self.asset_repo.get(asset_id)
        if not asset:
            raise NotFoundError("Asset not found")
        
        storage = await get_storage()
        return await storage.get_presigned_url(
            bucket="assets",
            key=asset.storage_key,
            expiry=3600,
        )
    
    async def get_preview_url(self, asset_id: UUID) -> Optional[str]:
        """Get asset preview URL."""
        asset = await self.asset_repo.get(asset_id)
        if not asset:
            raise NotFoundError("Asset not found")
        
        if asset.thumbnail_key:
            storage = await get_storage()
            return await storage.get_presigned_url(
                bucket="assets",
                key=asset.thumbnail_key,
                expiry=3600,
            )
        
        return asset.url
    
    async def process_asset(self, asset_id: UUID) -> UUID:
        """Process asset (generate thumbnails, optimize, etc.)."""
        asset = await self.asset_repo.get(asset_id)
        if not asset:
            raise NotFoundError("Asset not found")
        
        # Queue processing job
        queue = await get_queue()
        await queue.enqueue(
            'crawl_worker.process_asset',
            args=[str(asset_id)],
            queue='crawler',
        )
        
        return asset_id
    
    async def search_assets(
        self,
        user_id: UUID,
        query: str,
        project_id: Optional[UUID] = None,
        asset_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Search assets."""
        return await self.asset_repo.search(
            user_id=user_id,
            query=query,
            project_id=project_id,
            asset_type=asset_type,
        )
    
    async def get_project(self, project_id: UUID) -> Optional[Project]:
        """Get project by ID."""
        return await self.project_repo.get(project_id)