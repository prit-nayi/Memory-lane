# Memory Lane — Complete Project Implementation Plan

**Project:** Memory Lane – Visitor Photo Slideshow  
**Version:** 1.0  
**Development approach:** Guided, incremental implementation  
**Initial deployment:** Local environment  
**Frontend:** React + Vite (JavaScript)  
**Backend:** Python + FastAPI  
**Database:** PostgreSQL  

---

# 1. Project Overview

## 1.1 What is Memory Lane?

Memory Lane is a visitor photo-sharing and slideshow web application.

The system allows visitors to register, upload their photographs, and have their photographs displayed in a continuously updated slideshow on a TV or computer screen.

Visitors can return later and access their previous photographs using a unique access code. Their previously approved photographs will automatically be included in the slideshow.

The application will also provide an administrative interface to manage visitors, photographs, approvals, and slideshow settings.

## 1.2 Main Objectives

1. Allow new visitors to register easily.
2. Generate a unique access code for each visitor.
3. Allow returning visitors to access their existing profile.
4. Allow visitors to upload multiple photographs.
5. Store photographs securely.
6. Allow administrators to approve or reject photographs.
7. Display approved photographs in a slideshow.
8. Automatically update the slideshow when new photographs are approved.
9. Include previously approved photographs from returning visitors.
10. Provide administrators with controls to manage the application.

## 1.3 User Roles

The application will have three main interfaces:

| Interface | Purpose |
|---|---|
| Visitor | Register, access account, upload photographs |
| Administrator | Manage visitors, photographs, approvals and settings |
| Slideshow Display | Display approved photographs continuously |

The slideshow is a public display interface, not a separate authenticated user role.

---

# 2. Complete System Workflow

## 2.1 New Visitor Workflow

1. Visitor opens the Memory Lane website.
2. Visitor selects the new visitor option.
3. Visitor enters their name.
4. Visitor accepts the photo-sharing consent.
5. Backend generates a unique access code.
6. Visitor information is saved in PostgreSQL.
7. The access code is displayed to the visitor.
8. Visitor is redirected to the upload interface.
9. Visitor selects and uploads multiple photographs.
10. Backend validates and stores the photographs.
11. Photograph records are created in PostgreSQL.
13. validated photographs become available in the slideshow.

## 2.2 Returning Visitor Workflow

1. Visitor opens the website.
2. Visitor selects the returning visitor option.
3. Visitor enters their access code.
4. Backend verifies the access code.
5. Backend retrieves the visitor's information.
6. Visitor can upload additional photographs.
7. Previously approved photographs remain associated with the visitor.
8. Newly added photographs are added to the slideshow.

## 2.3 Photograph Validation Workflow

1. Visitor uploads a photograph.
2. Backend validates its type, size and contents.
3. Original photograph is stored locally.
4. Photograph metadata is stored in PostgreSQL.
5. validated photographs become eligible for slideshow display.
9. The backend notifies connected slideshow screens about the update.

## 2.4 Slideshow Workflow

1. Slideshow screen opens the slideshow page.
2. Frontend requests the validated photographs from the backend.
3. Backend retrieves validated photograph records.
4. Frontend displays photographs in sequence.
5. Each photograph stays visible for the configured duration.
6. Slideshow continues in a loop.
7. WebSocket connection listens for new approval events.
8. When new photographs are validated, the backend sends an update.
9. Slideshow refreshes its photograph queue without requiring a manual browser refresh.
10. If the WebSocket connection disconnects, the frontend reconnects and retrieves the latest photograph list.

---

# 3. Technology Stack

| Layer | Technology | Responsibility |
|---|---|---|
| Frontend | React + Vite | User interfaces |
| Language | JavaScript | Frontend development |
| Styling | Bootstrap + Custom CSS | Responsive design |
| Routing | React Router | Frontend navigation |
| API requests | Axios | Frontend-backend communication |
| Icons | React Icons | UI icons |
| Backend | FastAPI | REST API and application logic |
| Backend language | Python | Business logic |
| ORM | SQLAlchemy | Database operations |
| Database | PostgreSQL | Application data |
| Validation | Pydantic | Request and response validation |
| Migrations | Alembic | Database schema versioning |
| Image processing | Pillow | Image validation and processing |
| File storage | Local filesystem | Photograph storage |
| Realtime communication | WebSockets | Live slideshow updates |
| Backend testing | Pytest + HTTPX | API and service testing |
| Version control | Git + GitHub | Source code and history |

**Important:** The application itself does not require an LLM API, LangChain, vector database or machine-learning model. AI tools may be used during development and documented in the AI log.

---

# 4. Development Phases

The project will be developed in the following phases. Each phase has a defined objective, implementation tasks, and expected files.

## Phase 1 — Project Setup and Environment Configuration

**Status: Completed / initial setup verified**

### Objective
Establish the project structure, development environment and documentation.

### Tasks
- Create React frontend using Vite.
- Create FastAPI backend.
- Configure Python virtual environment.
- Install required dependencies.
- Install PostgreSQL and create the database.
- Configure Git and GitHub.
- Create environment configuration files.
- Create initial project documentation.
- Verify frontend, backend and PostgreSQL are running.

### Files

| File | Responsibility |
|---|---|
| `frontend/package.json` | Frontend dependencies and scripts |
| `frontend/package-lock.json` | Locked frontend dependencies |
| `frontend/vite.config.js` | Vite configuration |
| `frontend/src/main.jsx` | React application entry point |
| `frontend/src/App.jsx` | Initial frontend root component |
| `frontend/src/index.css` | Global frontend styling |
| `backend/requirements.txt` | Python dependencies |
| `backend/app/main.py` | FastAPI application entry point |
| `.env.example` | Environment variable template |
| `.gitignore` | Files excluded from Git |
| `README.md` | Project introduction and setup |
| `ASSUMPTIONS.md` | Documented project assumptions |
| `AI_LOG.md` | Record of AI-assisted development |
| `ARCHITECTURE.md` | High-level application architecture |
| `TEST_PLAN.md` | Planned testing strategy |

### Completion Criteria
- Frontend runs successfully.
- Backend runs successfully.
- PostgreSQL server is reachable.
- GitHub repository contains the initial project structure.

---

## Phase 2 — Database Configuration and Visitor Management

**Status: Completed**

### Objective
Build the database foundation and implement visitor registration and returning visitor verification.

### Tasks

**A. Database configuration**
- Configure SQLAlchemy engine.
- Create reusable database sessions.
- Configure database connection settings.
- Create database dependency for FastAPI.

**B. Visitor database model**
- Create Visitor SQLAlchemy model.
- Use UUID as the visitor identifier.
- Store visitor name.
- Store a secure hash of the access code.
- Add creation and update timestamps.
- Add appropriate uniqueness constraints.

**C. Database migrations**
- Configure Alembic.
- Connect Alembic to SQLAlchemy models.
- Generate the initial visitor migration.
- Apply the migration to PostgreSQL.

**D. Visitor schemas**
- Create registration request schema.
- Create registration response schema.
- Create returning visitor verification schema.
- Add validation rules.

**E. Visitor APIs**
- Register a new visitor.
- Generate a unique access code.
- Verify a returning visitor's access code.
- Retrieve visitor information.
- Handle invalid codes and duplicate conditions.

### Expected Files

| File | Responsibility |
|---|---|
| `backend/app/core/config.py` | Application settings and environment configuration |
| `backend/app/db/session.py` | Database engine, session and SQLAlchemy Base |
| `backend/app/models/__init__.py` | Model exports |
| `backend/app/models/visitor.py` | Visitor database model |
| `backend/app/schemas/__init__.py` | Schema exports |
| `backend/app/schemas/visitor.py` | Visitor request and response schemas |
| `backend/app/api/__init__.py` | API package |
| `backend/app/api/v1/__init__.py` | API version package |
| `backend/app/api/v1/visitors.py` | Visitor API endpoints |
| `backend/app/services/visitor_service.py` | Visitor business logic |
| `backend/app/core/security.py` | Access-code generation and verification |
| `backend/app/main.py` | Register API routers and database health check |
| `backend/alembic.ini` | Alembic configuration |
| `backend/alembic/env.py` | Migration environment |
| `backend/alembic/versions/` | Database migration files |
| `backend/tests/test_visitors.py` | Visitor API tests |

### Expected APIs

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/api/v1/visitors/register` | Register a new visitor |
| POST | `/api/v1/visitors/verify` | Verify returning visitor |
| GET | `/api/v1/visitors/me` | Retrieve current visitor information |
| GET | `/health/database` | Verify database connectivity |

### Completion Criteria
- Visitor table exists in PostgreSQL.
- New visitor registration works.
- Unique access codes are generated.
- Only access-code hashes are stored.
- Returning visitors can be verified.
- APIs work through Swagger.
- Tests cover successful and unsuccessful cases.

---

## Phase 3 — Photograph Upload and Local Storage

**Status: Completed**

### Objective
Allow visitors to upload photographs and securely associate them with their visitor profiles.

### Tasks
- Design the Photograph database model.
- Associate each photograph with a visitor.
- Implement multiple-file upload.
- Validate image formats.
- Validate image size.
- Validate actual image contents using Pillow.
- Generate unique file names.
- Store files in local storage.
- Save photograph metadata in PostgreSQL.
- Add photograph status management.
- Handle failed uploads and cleanup.
- Prevent unauthorized access to visitor uploads.

### Photograph Statuses

- `pending`
- `approved`
- `rejected`

### Expected Files

| File | Responsibility |
|---|---|
| `backend/app/models/photo.py` | Photograph database model |
| `backend/app/schemas/photo.py` | Photograph request and response schemas |
| `backend/app/api/v1/photos.py` | Photograph API endpoints |
| `backend/app/services/photo_service.py` | Photograph business logic |
| `backend/app/core/storage.py` | Local file storage operations |
| `backend/app/main.py` | Register photograph routes and static file access if needed |
| `backend/tests/test_photos.py` | Photograph upload tests |
| `storage/uploads/` | Uploaded photograph files |

### Expected APIs

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/api/v1/photos/upload` | Upload multiple photographs |
| GET | `/api/v1/photos/my-photos` | Retrieve visitor's photographs |
| GET | `/api/v1/photos/{photo_id}` | Retrieve photograph information |
| DELETE | `/api/v1/photos/{photo_id}` | Delete an eligible photograph |

### Completion Criteria
- Visitors can upload multiple photographs.
- Invalid files are rejected.
- Valid files are stored locally.
- Photograph metadata is saved correctly.
- Each photograph belongs to the correct visitor.
- New photographs have pending approval status.

---

## Phase 4 — Frontend Visitor Interface

### Objective
Build the complete visitor-facing website and connect it to the backend.

### Tasks

**A. Home page**
- Introduce Memory Lane.
- Provide new visitor and returning visitor options.
- Add navigation to the slideshow.

**B. Registration page**
- Visitor name input.
- Consent checkbox.
- Registration API integration.
- Display generated access code.
- Provide a way to retain or copy the code safely.

**C. Returning visitor page**
- Access code input.
- Backend verification.
- Show appropriate error messages.
- Redirect verified visitors to their dashboard.

**D. Visitor dashboard**
- Show visitor information.
- Display previously uploaded photographs.
- Show photograph approval statuses.
- Provide upload navigation.

**E. Upload page**
- Multiple image selection.
- Image preview.
- Remove selected images before upload.
- Upload progress and success/error feedback.

### Expected Frontend Structure

```text
frontend/src/
├── assets/
├── components/
│   ├── Navbar.jsx
│   ├── Footer.jsx
│   ├── PhotoCard.jsx
│   ├── PhotoUploader.jsx
│   └── Loading.jsx
├── pages/
│   ├── Home.jsx
│   ├── Register.jsx
│   ├── ReturningVisitor.jsx
│   ├── VisitorDashboard.jsx
│   └── UploadPhotos.jsx
├── services/
│   ├── api.js
│   ├── visitorService.js
│   └── photoService.js
├── context/
│   └── VisitorContext.jsx
├── routes/
│   └── AppRoutes.jsx
├── hooks/
├── styles/
├── App.jsx
├── main.jsx
└── index.css
```

### Completion Criteria
- New visitors can register through the UI.
- Returning visitors can verify their access code.
- Visitors can upload photographs.
- Visitors can see their uploaded photographs and statuses.
- Frontend communicates correctly with FastAPI.

---

## Phase 5 — Slideshow Interface

### Objective
Create a dedicated screen for continuously displaying approved photographs.

### Tasks
- Create a full-screen slideshow page.
- Retrieve approved photographs from the backend.
- Display photographs in sequence.
- Implement automatic transitions.
- Configure slide duration.
- Implement continuous looping.
- Handle empty slideshow state.
- Handle missing or unavailable image files.
- Make the interface suitable for TV and desktop displays.
- Prevent accidental navigation and unnecessary controls.

### Expected Files

| File | Responsibility |
|---|---|
| `backend/app/api/v1/slideshow.py` | Slideshow data endpoints |
| `backend/app/services/slideshow_service.py` | Approved-photo retrieval and slideshow logic |
| `backend/app/schemas/slideshow.py` | Slideshow response schema |
| `frontend/src/pages/Slideshow.jsx` | Slideshow screen |
| `frontend/src/components/SlideshowPlayer.jsx` | Photograph transitions and playback |
| `frontend/src/services/slideshowService.js` | Slideshow API requests |
| `frontend/src/styles/slideshow.css` | Slideshow-specific styling |

### Expected APIs

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/v1/slideshow/photos` | Retrieve approved photographs |
| GET | `/api/v1/slideshow/settings` | Retrieve slideshow settings |

### Completion Criteria
- Only approved photographs are displayed.
- Photographs transition automatically.
- Slideshow loops continuously.
- Display works on a TV or computer browser.

---

## Phase 6 — Real-Time Slideshow Updates

### Objective
Ensure the slideshow automatically receives newly approved photographs without manual refresh.

### Tasks
- Configure FastAPI WebSocket endpoint.
- Create WebSocket connection manager.
- Maintain connected slideshow clients.
- Broadcast events when photographs are approved.
- Update the slideshow queue when new photographs arrive.
- Handle WebSocket disconnection.
- Implement automatic reconnection.
- Fetch the latest photograph list after reconnecting.
- Avoid duplicate photographs in the queue.

### Expected Files

| File | Responsibility |
|---|---|
| `backend/app/api/v1/websocket.py` | WebSocket endpoint |
| `backend/app/services/websocket_manager.py` | Manage connected slideshow clients |
| `backend/app/services/photo_service.py` | Trigger events after successful approval |
| `frontend/src/hooks/useSlideshowSocket.js` | WebSocket connection and reconnection |
| `frontend/src/pages/Slideshow.jsx` | React to real-time updates |
| `frontend/src/services/slideshowService.js` | Refresh photograph data |

### Completion Criteria
- Slideshow connects to WebSocket.
- Newly approved photographs are broadcast.
- Slideshow updates without browser refresh.
- Reconnection restores the latest slideshow state.

---

## Phase 7 — Admin Dashboard and Management

### Objective
Provide an administrative interface to control the application and manage uploaded content.

### Tasks

**A. Administrator authentication**
- Implement administrator login.
- Secure password storage.
- Protect administrative endpoints.
- Implement authentication and authorization.

**B. Dashboard**
- Total visitor count.
- Total photograph count.


**C. Visitor management**
- View registered visitors.
- View visitor photograph history.
- Disable or manage visitor records where appropriate.

**D. Slideshow settings**
- Configure photograph display duration.
- Configure slideshow behavior.
- Enable or disable selected display options.

### Expected Files

| File | Responsibility |
|---|---|
| `backend/app/models/admin.py` | Administrator model |
| `backend/app/schemas/admin.py` | Admin schemas |
| `backend/app/api/v1/admin.py` | Admin API endpoints |
| `backend/app/services/admin_service.py` | Administrative business logic |
| `backend/app/core/security.py` | Admin authentication and authorization helpers |
| `backend/app/models/settings.py` | Slideshow settings model |
| `frontend/src/pages/AdminLogin.jsx` | Admin login |
| `frontend/src/pages/AdminDashboard.jsx` | Admin dashboard |
| `frontend/src/pages/AdminVisitors.jsx` | Visitor management |
| `frontend/src/pages/AdminSettings.jsx` | Slideshow settings |
| `frontend/src/components/AdminSidebar.jsx` | Admin navigation |

### Expected APIs

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/api/v1/admin/login` | Administrator login |
| GET | `/api/v1/admin/dashboard` | Dashboard statistics |
| GET | `/api/v1/admin/photos` | Retrieve photographs for moderation |
| DELETE | `/api/v1/admin/photos/{photo_id}` | Delete photograph |
| GET | `/api/v1/admin/visitors` | List visitors |
| GET | `/api/v1/admin/settings` | Retrieve settings |
| PUT | `/api/v1/admin/settings` | Update settings |

### Completion Criteria
- Admin login works.
- Unauthorized users cannot access admin functionality.
- Administrators can manage visitors and photographs.
- Slideshow settings can be changed.

---

## Phase 8 — Testing, Security and Error Handling

### Objective
Ensure the application is stable, secure and ready for demonstration.

### Tasks

**Functional testing**
- Visitor registration.
- Returning visitor verification.
- Photograph upload.
- Photograph approval and rejection.
- Slideshow playback.
- Real-time updates.
- Admin operations.

**Security testing**
- Secure access-code hashing.
- Admin authentication and authorization.
- File type and file size validation.
- Protection against unauthorized photograph access.
- Input validation.
- Safe file naming and path handling.
- CORS configuration.
- Avoid exposing secrets.
- Rate limiting for sensitive endpoints where appropriate.

**Reliability testing**
- Database connection failures.
- Missing image files.
- Failed uploads.
- Multiple concurrent uploads.
- WebSocket disconnection and reconnection.
- Empty slideshow.
- Large photograph collections.

### Expected Files

| File | Responsibility |
|---|---|
| `backend/tests/` | Backend automated tests |
| `frontend/` | Frontend testing files as required |
| `TEST_PLAN.md` | Test cases and test results |
| `backend/app/core/config.py` | Production-safe configuration |
| `backend/app/main.py` | Middleware and application configuration |
| `AI_LOG.md` | Record of testing-related AI assistance |

### Completion Criteria
- Main workflows pass testing.
- Critical security checks pass.
- Errors are handled gracefully.
- No secrets or uploaded private photographs are committed to Git.

---

## Phase 9 — Documentation, Finalization and Deployment Preparation

### Objective
Prepare Memory Lane for final demonstration and future deployment.

### Tasks
- Complete project README.
- Document architecture.
- Document database structure.
- Document API endpoints.
- Document installation and execution steps.
- Complete AI usage log.
- Record assumptions and design decisions.
- Add screenshots.
- Prepare test results.
- Verify a fresh local setup.
- Prepare deployment configuration if required later.

### Files

| File | Responsibility |
|---|---|
| `README.md` | Complete setup and usage documentation |
| `ARCHITECTURE.md` | Final architecture |
| `ASSUMPTIONS.md` | Confirmed assumptions and decisions |
| `AI_LOG.md` | Complete AI development history |
| `TEST_PLAN.md` | Testing and verification results |
| `PROJECT_IMPLEMENTATION_PLAN.md` | Overall implementation roadmap |
| `.env.example` | Final environment variable template |

### Completion Criteria
- Another developer can set up the application using the documentation.
- Project functionality is demonstrated successfully.
- Documentation matches the actual implementation.
- GitHub repository is organized and complete.

---

# 5. Complete Target Backend Structure

The following is the planned structure after all backend phases. We will create folders and files gradually, not all at once.

```text
backend/
├── app/
│   ├── __init__.py
│   ├── main.py
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   └── security.py
│   │
│   ├── db/
│   │   ├── __init__.py
│   │   └── session.py
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── visitor.py
│   │   ├── photo.py
│   │   ├── admin.py
│   │   └── settings.py
│   │
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── visitor.py
│   │   ├── photo.py
│   │   ├── admin.py
│   │   └── slideshow.py
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── visitors.py
│   │       ├── photos.py
│   │       ├── slideshow.py
│   │       ├── admin.py
│   │       └── websocket.py
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── visitor_service.py
│   │   ├── photo_service.py
│   │   ├── slideshow_service.py
│   │   ├── admin_service.py
│   │   └── websocket_manager.py
│   │
│   └── tests/
│       ├── __init__.py
│       ├── test_visitors.py
│       ├── test_photos.py
│       ├── test_slideshow.py
│       └── test_admin.py
│
├── alembic/
│   ├── versions/
│   ├── env.py
│   └── script.py.mako
│
├── alembic.ini
├── requirements.txt
└── venv/
```

---

# 6. Complete Target Frontend Structure

```text
frontend/
├── public/
├── src/
│   ├── assets/
│   │
│   ├── components/
│   │   ├── Navbar.jsx
│   │   ├── Footer.jsx
│   │   ├── PhotoCard.jsx
│   │   ├── PhotoUploader.jsx
│   │   ├── SlideshowPlayer.jsx
│   │   ├── Loading.jsx
│   │   └── AdminSidebar.jsx
│   │
│   ├── pages/
│   │   ├── Home.jsx
│   │   ├── Register.jsx
│   │   ├── ReturningVisitor.jsx
│   │   ├── VisitorDashboard.jsx
│   │   ├── UploadPhotos.jsx
│   │   ├── Slideshow.jsx
│   │   ├── AdminLogin.jsx
│   │   ├── AdminDashboard.jsx
│   │   ├── AdminPhotos.jsx
│   │   ├── AdminVisitors.jsx
│   │   └── AdminSettings.jsx
│   │
│   ├── services/
│   │   ├── api.js
│   │   ├── visitorService.js
│   │   ├── photoService.js
│   │   └── slideshowService.js
│   │
│   ├── context/
│   │   └── VisitorContext.jsx
│   │
│   ├── hooks/
│   │   └── useSlideshowSocket.js
│   │
│   ├── routes/
│   │   └── AppRoutes.jsx
│   │
│   ├── styles/
│   │   └── slideshow.css
│   │
│   ├── App.jsx
│   ├── main.jsx
│   └── index.css
│
├── package.json
└── vite.config.js
```

---

# 7. Root Project Structure

```text
Memory-Lane/
│
├── frontend/
├── backend/
├── docs/
├── storage/
│   └── uploads/
│
├── README.md
├── PROJECT_IMPLEMENTATION_PLAN.md
├── ARCHITECTURE.md
├── ASSUMPTIONS.md
├── AI_LOG.md
├── TEST_PLAN.md
├── .env
├── .env.example
└── .gitignore
```

---

# 8. Important Files That Must Be Maintained Throughout the Project

These files are not just for the final submission. They must be updated as the application develops.

| File | When to update | What to record |
|---|---|---|
| `README.md` | Every major phase | New features, setup, dependencies and usage |
| `PROJECT_IMPLEMENTATION_PLAN.md` | At phase completion or when scope changes | Phase status, decisions and changes to the roadmap |
| `ARCHITECTURE.md` | Whenever architecture changes | New modules, data flow, APIs and relationships |
| `ASSUMPTIONS.md` | When an assumption is confirmed or changed | Constraints, limits, decisions and reasons |
| `AI_LOG.md` | Every meaningful AI-assisted task | Prompt/task, AI contribution, corrections and learning |
| `TEST_PLAN.md` | Whenever functionality is implemented | Test cases, expected results and actual results |
| `.env.example` | Whenever a new environment variable is added | Variable name and safe placeholder |
| `backend/requirements.txt` | Whenever backend dependencies change | Required Python packages |
| `frontend/package.json` | Whenever frontend dependencies change | Required JavaScript packages |

**Important documentation rule:** Do not claim a feature is complete just because code has been generated. Mark a phase complete only after its functionality has been tested.

---

# 9. Database Design Overview

The database will gradually include the following main entities:

| Table | Purpose |
|---|---|
| `visitors` | Registered visitors and access-code hashes |
| `photos` | Photograph metadata, file path and approval status |
| `admins` | Administrator credentials and account details |
| `slideshow_settings` | Slideshow configuration |

### Main Relationships

- One visitor can have multiple photographs.
- Each photograph belongs to one visitor.
- Administrators manage photographs and visitors.
- Slideshow settings control how approved photographs are displayed.

The final schema will be refined when implementing each model and migration.

---

# 10. Important Development Rules

To maintain code quality and avoid unnecessary rework, follow these rules throughout the project.

1. **Understand before implementing:** Every major module should have a clear purpose before code generation.
2. **Follow the architecture:** Keep API routes, business logic, database models and schemas separate.
3. **No unnecessary dependencies:** Add packages only when the project actually needs them.
4. **Security first:** Never store plain access codes or admin passwords.
5. **Validate uploads:** Never trust file extensions alone.
6. **Approval before display:** Only approved photographs should appear on the public slideshow.
7. **Reliable real-time updates:** Store and commit photograph changes before broadcasting slideshow events.
8. **Test every module:** Verify backend APIs and frontend behavior before proceeding.
9. **Document AI assistance:** Record meaningful prompts, generated code, corrections and learning.
10. **Use Git commits:** Commit working features with clear messages.
11. **Keep deployment local initially:** Do not introduce cloud services until the local application works.
12. **Update documentation:** Keep the implementation plan and architecture aligned with the actual code.

---

# 11. How We Will Execute the Project

For every development phase, we will follow this process:

1. Review the phase objective and required functionality.
2. Understand the architecture and data flow.
3. Identify all files that need to be created or modified.
4. Prepare a complete implementation task for that module.
5. Implement the module.
6. Review the generated code and explain important decisions.
7. Run the application and test the functionality.
8. Fix errors and verify the final behavior.
9. Update the relevant documentation.
10. Commit the completed work to GitHub.
11. Update the phase status in this implementation plan.

We will not jump to the next phase until the current phase is working correctly.

---

# 12. Current Project Status

| Phase | Description | Status |
|---|---|---|
| Phase 1 | Project setup and environment | Completed |
| Phase 2 | Database and visitor management | Completed |
| Phase 3 | Photograph upload and storage | Completed |
| Phase 4 | Visitor frontend | Not started |
| Phase 5 | Slideshow interface | Not started |
| Phase 6 | Real-time slideshow updates | Not started |
| Phase 7 | Admin dashboard | Not started |
| Phase 8 | Testing and security | Not started |
| Phase 9 | Documentation and finalization | Not started |

**Current verified position:** Phase 2 visitor functionality and Phase 3 photo
upload APIs pass automated tests. PostgreSQL migrations through
`20261111_02` are applied.

**Next development milestone:** Implement Phase 4 visitor-facing frontend
registration, returning visitor, dashboard, and upload workflows.

---

# Final Project Goal

Deliver a working local application in which a new visitor can register, receive an access code, upload photographs, and later return using that code. Administrators can moderate uploaded photographs, and approved photographs automatically appear on a continuously running slideshow screen.

The system should be modular, maintainable, secure, documented and ready for a future deployment if required.
