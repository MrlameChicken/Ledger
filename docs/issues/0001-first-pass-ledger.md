# Build first pass of the Ledger application

## Summary
Create the foundation of the Ledger application so that both backend and frontend teams have a working baseline to build on. This issue tracks the initial implementation across core services, data models, and user interface scaffolding.

## Goals
- Establish the backend service with project scaffolding, dependency management, and a health-check endpoint.
- Define initial database schema or migration plan for ledger entries and user accounts.
- Set up frontend project structure with routing, shared layout, and placeholder pages for key flows (dashboard, transactions, settings).
- Implement CI configuration for running linting and automated tests.

## Non-Goals
- Implementing advanced business logic such as reconciliation or reporting dashboards.
- Integrating with external payment providers or APIs.
- Designing final UI/UX beyond functional placeholders.

## Acceptance Criteria
- Backend application boots locally with a documented start command and passes health-check endpoint tests.
- Database migrations or schema definitions are committed with instructions for applying them locally.
- Frontend renders the shell layout with navigation to placeholder views for core sections.
- CI pipeline runs linting and unit tests for both backend and frontend on pull requests.
- README (or dedicated docs) updated with setup instructions for backend, frontend, and database.

## Dependencies / Blockers
- Selection of primary database technology (PostgreSQL, SQLite, etc.).
- Availability of CI secrets or credentials if required.

## Additional Context
Capture decisions about technology choices in documentation to ensure future contributors understand the baseline architecture.
