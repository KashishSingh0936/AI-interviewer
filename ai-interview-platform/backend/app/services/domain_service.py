"""
Domain and Role service
"""
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import List
from ..models.models import Domain, Role
from ..schemas.schemas import DomainCreate, RoleCreate, DomainResponse, RoleResponse


class DomainService:
    """Domain management service"""
    
    @staticmethod
    def create_domain(db: Session, domain_data: DomainCreate) -> Domain:
        """Create a new domain"""
        existing = db.query(Domain).filter(Domain.name == domain_data.name).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Domain already exists"
            )
        
        domain = Domain(name=domain_data.name, description=domain_data.description)
        db.add(domain)
        db.commit()
        db.refresh(domain)
        return domain
    
    @staticmethod
    def get_all_domains(db: Session) -> List[Domain]:
        """Get all domains with roles"""
        return db.query(Domain).all()
    
    @staticmethod
    def get_domain(db: Session, domain_id: int) -> Domain:
        """Get domain by ID"""
        domain = db.query(Domain).filter(Domain.id == domain_id).first()
        if not domain:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Domain not found"
            )
        return domain


class RoleService:
    """Role management service"""
    
    @staticmethod
    def create_role(db: Session, role_data: RoleCreate) -> Role:
        """Create a new role in a domain"""
        # Verify domain exists
        domain = db.query(Domain).filter(Domain.id == role_data.domain_id).first()
        if not domain:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Domain not found"
            )
        
        # Check if role exists in domain
        existing = db.query(Role).filter(
            Role.domain_id == role_data.domain_id,
            Role.name == role_data.name
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Role already exists in this domain"
            )
        
        role = Role(
            name=role_data.name,
            description=role_data.description,
            domain_id=role_data.domain_id
        )
        db.add(role)
        db.commit()
        db.refresh(role)
        return role
    
    @staticmethod
    def get_roles_by_domain(db: Session, domain_id: int) -> List[Role]:
        """Get all roles in a domain"""
        return db.query(Role).filter(Role.domain_id == domain_id).all()
    
    @staticmethod
    def get_role(db: Session, role_id: int) -> Role:
        """Get role by ID"""
        role = db.query(Role).filter(Role.id == role_id).first()
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Role not found"
            )
        return role


# Predefined domains and roles database
PREDEFINED_DATA = {
    "Data Science": ["Data Scientist", "Data Analyst", "Machine Learning Engineer"],
    "Web Development": ["Frontend Developer", "Backend Developer", "Full Stack Developer"],
    "Machine Learning": ["ML Engineer", "AI Researcher", "Deep Learning Specialist"],
    "Software Engineering": ["Software Engineer", "DevOps Engineer", "Solutions Architect"],
    "Cybersecurity": ["Security Analyst", "Penetration Tester", "Security Engineer"],
    "Cloud Computing": ["Cloud Architect", "AWS Developer", "Cloud Engineer"],
    "Mobile Development": ["Android Developer", "iOS Developer", "React Native Developer"],
    "Game Development": ["Game Developer", "Unity Developer", "Unreal Engine Developer"],
    "Blockchain": ["Blockchain Developer", "Smart Contract Developer", "Crypto Engineer"],
    "AI/NLP": ["AI Engineer", "NLP Specialist", "Computer Vision Engineer"],
    "Database": ["Database Administrator", "Database Designer", "SQL Specialist"],
    "DevOps": ["DevOps Engineer", "Site Reliability Engineer", "Infrastructure Engineer"],
}


class DomainInitializer:
    """Initialize predefined domains and roles"""
    
    @staticmethod
    def initialize_domains(db: Session):
        """Initialize predefined domains and roles"""
        for domain_name, role_names in PREDEFINED_DATA.items():
            # Check if domain exists
            domain = db.query(Domain).filter(Domain.name == domain_name).first()
            if not domain:
                domain = Domain(name=domain_name)
                db.add(domain)
                db.commit()
                db.refresh(domain)
            
            # Add roles for this domain
            for role_name in role_names:
                role_exists = db.query(Role).filter(
                    Role.domain_id == domain.id,
                    Role.name == role_name
                ).first()
                
                if not role_exists:
                    role = Role(name=role_name, domain_id=domain.id)
                    db.add(role)
        
        db.commit()
