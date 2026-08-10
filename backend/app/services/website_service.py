"""Website service."""

from typing import Optional, List, Tuple, Dict, Any
from uuid import UUID

from app.models.website import Website
from app.repositories.website_repository import WebsiteRepository
from app.repositories.project_repository import ProjectRepository
from app.core.errors import NotFoundError, ValidationError
from app.services.job_service import JobService


class WebsiteService:
    """Website service."""
    
    def __init__(
        self,
        website_repo: WebsiteRepository,
        project_repo: ProjectRepository,
        job_service: Optional[JobService] = None
    ):
        self.website_repo = website_repo
        self.project_repo = project_repo
        self.job_service = job_service
    
    async def create_website(
        self,
        project_id: UUID,
        url: str,
        user_id: UUID
    ) -> Website:
        """Create a new website entry."""
        # Validate project exists
        project = await self.project_repo.get(project_id)
        if not project:
            raise NotFoundError("Project not found")
        
        # Validate URL
        if not url.startswith(('http://', 'https://')):
            raise ValidationError("Invalid URL format")
        
        # Check if website already exists in project
        existing = await self.website_repo.get_by_project_url(project_id, url)
        if existing:
            raise ValidationError("Website already exists in this project")
        
        website = Website(
            project_id=project_id,
            url=url,
            status="pending",
        )
        
        return await self.website_repo.create(website)
    
    async def get_website(self, website_id: UUID) -> Optional[Website]:
        """Get website by ID."""
        return await self.website_repo.get(website_id)
    
    async def list_websites(
        self,
        user_id: UUID,
        project_id: Optional[UUID] = None,
        skip: int = 0,
        limit: int = 20
    ) -> Tuple[List[Website], int]:
        """List websites for a user."""
        return await self.website_repo.list_by_user(
            user_id=user_id,
            project_id=project_id,
            skip=skip,
            limit=limit
        )
    
    async def update_website(
        self,
        website_id: UUID,
        updates: Dict[str, Any]
    ) -> Website:
        """Update website."""
        website = await self.website_repo.get(website_id)
        if not website:
            raise NotFoundError("Website not found")
        
        for key, value in updates.items():
            if hasattr(website, key):
                setattr(website, key, value)
        
        return await self.website_repo.update(website)
    
    async def delete_website(self, website_id: UUID) -> None:
        """Delete website."""
        website = await self.website_repo.get(website_id)
        if not website:
            raise NotFoundError("Website not found")
        
        await self.website_repo.delete(website)
    
    async def analyze_website(
        self,
        website_id: UUID,
        max_pages: int = 50,
        depth: int = 3,
        include_assets: bool = True
    ) -> UUID:
        """Analyze website content."""
        website = await self.website_repo.get(website_id)
        if not website:
            raise NotFoundError("Website not found")
        
        # Create crawl job first
        if self.job_service:
            crawl_job = await self.job_service.create_crawl_job(
                website_id=website_id,
                user_id=website.project.user_id,
                max_pages=max_pages,
                depth=depth,
                include_assets=include_assets,
            )
            
            # Then create analysis job
            analysis_job = await self.job_service.create_analysis_job(
                website_id=website_id,
                user_id=website.project.user_id,
                analysis_type="full",
                depth="standard"
            )
            
            return analysis_job.id
        
        return UUID(int=0)
    
    async def get_analysis_status(self, website_id: UUID) -> Dict[str, Any]:
        """Get website analysis status."""
        return {
            "status": "pending",
            "progress": 0,
            "crawled_pages": 0,
            "total_pages": 0,
        }
    
    async def list_pages(
        self,
        website_id: UUID,
        skip: int = 0,
        limit: int = 20
    ) -> Tuple[List[Dict], int]:
        """List pages from a website."""
        # This would be implemented with page repository
        return [], 0
    
    async def list_assets(
        self,
        website_id: UUID,
        asset_type: Optional[str] = None,
        skip: int = 0,
        limit: int = 20
    ) -> Tuple[List[Dict], int]:
        """List assets from a website."""
        # This would be implemented with asset repository
        return [], 0
    
    async def get_digital_twin(self, website_id: UUID) -> Optional[Dict]:
        """Get website digital twin."""
        website = await self.website_repo.get(website_id)
        if not website:
            raise NotFoundError("Website not found")
        
        return website.digital_twin