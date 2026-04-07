"""
Domain and Role routes
"""
from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from typing import List, Optional
from ..core.database import get_db
from ..core.security import decode_access_token
from ..models.models import User
from ..schemas.schemas import (
    DomainCreate, RoleCreate, DomainResponse, RoleResponse
)
from ..services.domain_service import (
    DomainService, RoleService, DomainInitializer
)

router = APIRouter(prefix="/api/domains", tags=["domains"])


def get_auth_user(authorization: Optional[str] = Header(None), db: Session = Depends(get_db)) -> User:
    """Extract user from authorization header"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    token = authorization.split(" ")[1]
    payload = decode_access_token(token)
    user_id = payload.get("user_id")
    
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    from ..services.user_service import UserService
    return UserService.get_user_by_id(db, user_id)


@router.get("", response_model=List[DomainResponse])
async def get_domains(db: Session = Depends(get_db)):
    """Get all available domains with roles"""
    domains = DomainService.get_all_domains(db)
    return [
        DomainResponse(
            id=d.id,
            name=d.name,
            description=d.description,
            roles=[RoleResponse.model_validate(r) for r in d.roles]
        )
        for d in domains
    ]


@router.get("/{domain_id}", response_model=DomainResponse)
async def get_domain(domain_id: int, db: Session = Depends(get_db)):
    """Get domain with roles"""
    domain = DomainService.get_domain(db, domain_id)
    return DomainResponse(
        id=domain.id,
        name=domain.name,
        description=domain.description,
        roles=[RoleResponse.model_validate(r) for r in domain.roles]
    )


@router.post("", response_model=DomainResponse)
async def create_domain(
    domain_data: DomainCreate,
    current_user: User = Depends(get_auth_user),
    db: Session = Depends(get_db)
):
    """Create new domain (interviewer only)"""
    if current_user.role.value != "interviewer":
        raise HTTPException(status_code=403, detail="Only interviewers can create domains")
    
    domain = DomainService.create_domain(db, domain_data)
    return DomainResponse(
        id=domain.id,
        name=domain.name,
        description=domain.description,
        roles=[]
    )


@router.get("/{domain_id}/roles", response_model=List[RoleResponse])
async def get_domain_roles(domain_id: int, db: Session = Depends(get_db)):
    """Get all roles in a domain"""
    roles = RoleService.get_roles_by_domain(db, domain_id)
    return [RoleResponse.model_validate(r) for r in roles]


@router.post("/{domain_id}/roles", response_model=RoleResponse)
async def create_role(
    domain_id: int,
    role_data: RoleCreate,
    current_user: User = Depends(get_auth_user),
    db: Session = Depends(get_db)
):
    """Create new role in domain (interviewer only)"""
    if current_user.role.value != "interviewer":
        raise HTTPException(status_code=403, detail="Only interviewers can create roles")
    
    role_data.domain_id = domain_id
    role = RoleService.create_role(db, role_data)
    return RoleResponse.model_validate(role)


@router.post("/init", status_code=201)
async def initialize_domains(
    current_user: User = Depends(get_auth_user),
    db: Session = Depends(get_db)
):
    """Initialize predefined domains and roles (admin only)"""
    if current_user.role.value != "interviewer":
        raise HTTPException(status_code=403, detail="Admin only")
    
    DomainInitializer.initialize_domains(db)
    return {"message": "Domains initialized successfully"}
