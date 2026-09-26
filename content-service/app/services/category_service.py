from fastapi.exceptions import HTTPException
from app.schemas import CategoryCreateRequest
from app.schemas import CategoryResponse
from app.utils.slug import generate_slug
from app.repositories.category import CategoryRepository
from app.models.category import Category


class CategoryService:
    def __init__(self, repo: CategoryRepository):
        self.repo = repo

    async def create(self, payload: CategoryCreateRequest) -> CategoryResponse:
        slug = generate_slug(payload.name)
        existing = await self.repo.get_by_slug(slug)
        if existing:
            raise HTTPException(
                status_code=400, detail="Category with this name already exists"
            )

        category = Category(
            name=payload.name,
            slug=slug,
            description=payload.description,
        )
        category = await self.repo.create(category)
        await self.repo.session.commit()
        return CategoryResponse.model_validate(category)
