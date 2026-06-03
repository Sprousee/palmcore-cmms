# PalmCore CMMS - Copilot Instructions

PalmCore CMMS is an enterprise industrial maintenance management system (CMMS) for palm oil extraction plants.

## Stack

Frontend:

* React
* TypeScript
* TailwindCSS
* Shadcn UI
* Zustand
* React Query

Backend:

* FastAPI
* SQLAlchemy 2.0
* PostgreSQL
* Alembic
* JWT Authentication

## Architecture Rules

* Use Clean Architecture
* Use Repository Pattern
* Use Service Layer
* Never access database directly from routers
* Use dependency injection
* All modules must be multi-tenant using company_id
* Use soft delete with deleted_at
* Use typed SQLAlchemy 2.0 models
* Use Pydantic schemas for validation

## Backend Rules

* Use async FastAPI endpoints
* Use SQLAlchemy 2.0 style
* Use PostgreSQL optimized queries
* Use RBAC permissions
* Use JWT authentication

## Frontend Rules

* Use functional React components
* Use TypeScript everywhere
* Use React Query for server state
* Use Zustand for global state
* Use Tailwind utility classes
* Keep components modular

## Code Quality

* Strong typing required
* Modular architecture
* Reusable components
* Enterprise naming conventions
* Clean and readable code
