# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Environment Notes

- **Platform**: Windows environment
- **Port**: Application runs on port 5000 by default (Flask backend), port 3000 (Vue frontend dev server)
- **Background Execution**: Always run commands in background mode on Windows to avoid encoding issues
- **Output Formatting**: Avoid using emoji in output messages to prevent character encoding errors on Windows

## Codebase Architecture

This is a Flask web application with a Vue.js 3 frontend, featuring blog-like functionality and Thino-like thought management. The application uses a hybrid architecture with Flask serving both traditional web pages and REST API endpoints, while Vue acts as a modern SPA frontend.

### Backend Architecture (Flask)

**Flask Application Structure**:
- `app/__init__.py`: Application factory with Flask extensions initialization and CORS configuration
- `app/models.py`: Database models (User, Role, Post, Thought, Mood, Comment) with SQLAlchemy
- `app/main/`: Main blueprint with views split into multiple modules:
  - `views.py`: Main homepage, user profiles, and comprehensive API endpoints
  - `post_views.py`: Blog post management
  - `thought_views.py`: Thought management functionality
  - `mood_views.py`: Mood tracking with calendar visualization
- `app/auth/`: Authentication blueprint with forms and views
- `app/api_1_0/`: REST API blueprint with authentication and user management:
  - `authentication.py`: HTTP Basic Auth with token verification
  - `users.py`: User registration, login, profile management
  - `posts.py`: Blog post CRUD operations
  - `thoughts.py`: Thought CRUD operations
  - `errors.py`: API error handling
- `app/services/`: Business logic layer:
  - `auth_service.py`: Authentication service
  - `permission_service.py`: Permission checking
  - `ajax_service.py`: AJAX helpers
- `app/decorator.py`: Custom decorators for permissions
- `app/exceptions.py`: Custom exception handlers
- `config.py`: Configuration classes for different environments
- `manage.py`: Enhanced Flask-CLI manager with comprehensive database commands

### Frontend Architecture (Vue.js 3)

**Vue SPA Structure**:
- `frontend/src/main.js`: Vue 3 entry point with Pinia state management and plugin initialization
- `frontend/src/App.vue`: Main application component with navigation, flash messages, and responsive layout
- `frontend/src/router/`: Vue Router with lazy-loaded components, route guards, and meta handling
- `frontend/src/stores/`: Pinia stores for state management:
  - `auth.js`: Authentication state with token management
  - `blog.js`: Blog post management
  - `thoughts.js`: Thought CRUD and filtering
  - `ui.js`: Global UI state (loading, flash messages)
- `frontend/src/api/`: Centralized API layer with Axios interceptors and error handling:
  - `index.js`: Base API configuration with interceptors
  - `auth.js`: Authentication API calls
  - `blog.js`: Blog post API calls
  - `thoughts.js`: Thought API calls
  - `mood.js`: Mood tracking API calls
  - `user.js`: User profile management
- `frontend/src/views/`: Page components organized by feature:
  - `Home.vue`: Dashboard with recent posts, thoughts, and mood calendar
  - `blog/`: Blog management (list, detail, create)
  - `thoughts/`: Thought management interface
  - `mood/`: Mood tracking with calendar and history views
  - `auth/`: Login, register, profile pages
- `frontend/src/components/`: Reusable UI components:
  - `ui/`: Base UI components (SkeletonCard, etc.)
  - `QuickThoughtForm.vue`: Rapid thought creation
  - `ThoughtList.vue`: Thought display with filtering

**Key Frontend Features**:
- Modern Vue 3 Composition API with `<script setup>` syntax
- Pinia for centralized state management with persistent auth state
- Responsive design with Tailwind CSS and mobile-first approach
- Comprehensive loading states, error handling, and smooth transitions
- Lazy-loaded routes for better performance
- Real-time flash messaging system
- Calendar-based mood visualization with Chart.js integration

### Core Features

**Authentication & Permissions**:
- User authentication with role-based permissions (User, Moderator, Admin)
- Granular permission system with bit flags (FOLLOW, COMMENT, WRITE_ARTICLES, WRITE_THOUGHTS, MODERATE_COMMENTS, ADMIN)
- Token-based API authentication with Bearer tokens
- Email confirmation and password reset functionality (planned)

**Blog System**:
- Blog post creation, editing, and deletion with markdown support
- Pagination, view counting, and comment system
- Real-time updates via REST API
- HTML sanitization with bleach and markdown-it processing

**Thought Management (Thino-like)**:
- Quick thought recording with types (note, quote, idea, task)
- Tag-based organization and filtering
- Privacy controls (public/private thoughts) with soft deletion
- Search functionality and source URL attachment
- Real-time thought updates with optimistic UI

**Mood Tracking**:
- Daily mood recording with intensity levels (1-10)
- Calendar visualization with color-coded mood types
- Historical data analysis and trend tracking
- Statistical analysis with mood distribution charts
- Custom mood types with predefined configurations

### Database Models
- `User`: Authentication, profile info, relationships to posts, thoughts, and moods
- `Role`: Permission-based roles with granular bit flag permissions
- `Post`: Blog posts with markdown support, HTML conversion, view counting, and edit tracking
- `Thought`: Short thoughts/notes with tags, types, privacy settings, and soft deletion
- `Mood`: Daily mood records with intensity, custom types, and journal entries
- `Comment`: Blog post comments with HTML sanitization and moderation support

## Development Commands

### Backend Development

**Running the Flask Application**:
```bash
python manage.py runserver
```
The application runs on port 5000 by default. When running on Windows, always start the application in background mode to avoid console encoding issues.

**Database Management**:
```bash
# Create migration
python manage.py db migrate -m "Migration message"

# Apply migrations
python manage.py db upgrade

# Rollback migration
python manage.py db downgrade

# View migration history
python manage.py db history

# Check current migration
python manage.py db current
```

**Running Tests**:
```bash
python manage.py test
```

**Shell Access**:
```bash
python manage.py shell
```

### Frontend Development

**Frontend Development Server**:
```bash
cd frontend
npm run dev
```
The Vite development server runs on port 3000 and hot reloads changes.

**Build for Production**:
```bash
cd frontend
npm run build
```

**Linting**:
```bash
cd frontend
npm run lint
```

### Full Development Workflow

**Starting both services** (recommended):
```bash
# Terminal 1: Start Flask backend
python manage.py runserver

# Terminal 2: Start Vue frontend
cd frontend
npm run dev
```

The Vue application proxies API requests to the Flask backend during development via Vite proxy configuration.

## Key Dependencies

### Backend Dependencies
- **Flask 3.1.2**: Core web framework with application factory pattern
- **Flask-SQLAlchemy 3.1.1**: ORM integration with SQLAlchemy 2.0
- **Flask-Login 0.6.3**: User session management
- **Flask-Migrate 4.1.0**: Database migration support with Alembic
- **Flask-CORS**: Cross-origin resource sharing for API
- **Flask-HTTPAuth 4.8.0**: HTTP authentication for API endpoints
- **Flask-WTF 1.2.1**: Form handling and CSRF protection
- **Flask-Bootstrap 3.3.7.1**: Bootstrap integration for templates
- **Flask-Moment 1.0.6**: Date/time handling
- **SQLAlchemy 2.0.43**: Modern database ORM
- **PyMySQL 1.1.2**: MySQL database driver
- **Markdown 3.9**: Markdown text processing with extensions
- **Bleach 6.2.0**: HTML sanitization and cleaning
- **Werkzeug 3.1.3**: WSGI utilities and security functions

### Frontend Dependencies
- **Vue 3.4.15**: Modern JavaScript framework with Composition API
- **Vue Router 4.2.5**: Client-side routing with navigation guards
- **Pinia 2.1.7**: State management with persistence
- **Vite 5.0.11**: Build tool and development server with HMR
- **Tailwind CSS 3.4.1**: Utility-first CSS framework with custom configuration
- **Axios 1.6.7**: HTTP client for API requests with interceptors
- **Chart.js 4.5.0**: Data visualization for mood tracking
- **vue-chartjs 5.3.2**: Vue 3 integration for Chart.js
- **Heroicons 2.2.0**: Consistent iconography
- **Headless UI 1.7.23**: Accessible UI components
- **markdown-it 13.0.2**: Markdown parsing in frontend
- **@vueuse/core 13.9.0**: Vue composition utilities

## API Architecture and Endpoints

The application uses a comprehensive RESTful API architecture with multiple endpoint patterns.

### Authentication API
**API v1.0 Endpoints** (`/api/v1.0/`):
- `POST /api/v1.0/token` - Get authentication token
- `POST /api/v1.0/register` - User registration
- `GET /api/v1.0/me` - Get current user info

**Main API Endpoints** (`/api/`):
- `POST /api/auth/login` - User login (returns `real_token_<user_id>_*` format)
- `POST /api/auth/register` - User registration
- `GET /api/auth/me` - Get current user info from Authorization header

**Missing endpoints** (frontend implemented but backend not available):
- `/api/auth/logout`, `/api/auth/change-password`, `/api/auth/forgot-password`

### Blog API (`/api/posts`)
- `GET /api/posts` - Get paginated blog posts with metadata
- `GET /api/posts/<id>` - Get single post with view counting
- `POST /api/posts` - Create new post (requires authentication)
- `PUT /api/posts/<id>` - Update post (author/admin only)
- `DELETE /api/posts/<id>` - Delete post (author/admin only)

**Missing endpoints** (frontend expects but not implemented):
- `/api/posts/search`, `/api/posts/user/<username>`, `/api/posts/categories`

### Thoughts API
**Dual API Pattern**:
- `GET /api/thoughts` - Get thoughts with pagination and limit support
- `POST /api/thoughts` - Create thought (requires authentication)
- `DELETE /api/thoughts/<id>` - Soft delete thought (author/admin only)
- `GET /api/v1.0/thoughts` - Alternative thoughts endpoint
- `POST /api/v1.0/thoughts` - Create thought (alternative)
- `PUT /api/v1.0/thoughts/<id>` - Update thought
- `DELETE /api/v1.0/thoughts/<id>` - Delete thought

### Mood API (`/api/moods`)
- `GET /api/moods` - Get mood records with pagination and date filtering
- `GET /api/moods/today` - Get today's mood record
- `POST /api/moods` - Record mood (requires authentication)
- `PUT /api/moods/<id>` - Update mood record (author/admin only)
- `DELETE /api/moods/<id>` - Delete mood record (author/admin only)
- `GET /api/moods/stats` - Get mood statistics and analytics

### Legacy Routes (Flask templates)
- `/` - Home page (serves Vue SPA)
- `/thoughts` - Traditional thoughts management interface
- `/auth/*` - Authentication routes
- `/user/<username>` - User profile pages

### API Integration Patterns

**Frontend API Layer** (`frontend/src/api/index.js`):
- Centralized Axios configuration with request/response interceptors
- Automatic token handling and refresh with Authorization headers
- Global error handling with user-friendly flash messages
- Request/response transformation and standardization
- Loading state management integration

**State Management Integration**:
- Pinia stores directly call API modules with proper error handling
- Automatic loading state management with UI store integration
- Error boundaries and fallback handling
- Optimistic updates for better UX
- Token persistence and automatic retry logic

## Thought Management System

The application includes a comprehensive Thino-like thought management feature:

- **Thought Types**: `note`, `quote`, `idea`, `task` with color coding
- **Tags**: Comma-separated tags for organization and filtering
- **Privacy**: Public/private thoughts with `is_public` flag
- **Soft Delete**: Thoughts are marked as deleted rather than removed
- **Search**: Full-text search across thought content (planned)
- **Source URLs**: Attach reference links to thoughts
- **Real-time Updates**: Instant UI updates with optimistic rendering

## Permissions System

Granular permission system with bit flags for fine-grained access control:
- `FOLLOW` (0x01): Follow other users
- `COMMENT` (0x02): Comment on posts
- `WRITE_ARTICLES` (0x04): Create blog posts
- `MODERATE_COMMENTS` (0x08): Moderate comments
- `WRITE_THOUGHTS` (0x10): Create and manage thoughts
- `ADMIN` (0x80): Full administrative access

**Role Definitions**:
- **User**: FOLLOW, COMMENT, WRITE_ARTICLES, WRITE_THOUGHTS
- **Moderator**: All User permissions + MODERATE_COMMENTS
- **Admin**: All permissions (0xff)

## Configuration

The application uses environment-based configuration classes in `config.py`:
- **DevelopmentConfig**: Development environment with debug, MySQL dev database
- **TestingConfig**: Testing environment with SQLite database
- **ProductionConfig**: Production environment with MySQL production database
- **Default**: DevelopmentConfig

**Database Configuration**:
- MySQL with PyMySQL driver
- Connection pooling and UTF-8 charset
- Environment-specific database URLs
- Automatic commit on teardown

## File Organization

### Backend Structure
- `app/`: Main application package
  - `api_1_0/`: REST API v1.0 blueprint
  - `auth/`: Authentication blueprint
  - `main/`: Main application blueprint
  - `services/`: Business logic layer
  - `static/`: Static assets (CSS, JS, images)
  - `templates/`: Jinja2 templates organized by blueprint

### Frontend Structure
- `frontend/src/`: Vue.js source code
  - `api/`: API layer with organized modules
  - `assets/`: Static assets and global styles
  - `components/`: Reusable Vue components
  - `router/`: Vue Router configuration
  - `stores/`: Pinia state management
  - `views/`: Page components by feature

### Database
- `migrations/`: Alembic database migration files
  - Multiple migrations for users, posts, thoughts, and moods
  - Latest migrations include comprehensive schema updates

## Additional Features

### Markdown Processing
- Posts and thoughts support comprehensive markdown formatting
- Automatic HTML conversion with bleach sanitization
- Code highlighting, table support, and extension system
- Link processing and XSS protection

### Authentication System
- Token-based authentication for API endpoints
- Bearer token support with Authorization headers
- Session management with Flask-Login
- Role-based access control with permissions
- Email confirmation system (implemented but needs SMTP configuration)

### Data Visualization
- Mood tracking with Chart.js integration
- Calendar-based mood visualization
- Statistical analysis with mood distribution
- Historical trend tracking
- Custom mood type configurations

### Development Tools
- Comprehensive CLI with `manage.py`
- Database migration management
- Shell context for debugging
- Test runner integration
- Debug endpoints for development

## Development Notes and Critical Issues

### 🚨 Critical Security Issues

**Token Forgery Vulnerability**:
- `app/main/views.py:1310-1477` accepts any token matching `real_token_<user_id>_*` pattern
- This allows easy token forgery and unauthorized access
- **IMMEDIATE ACTION REQUIRED**: Implement proper token validation

**Hardcoded Backdoor**:
- Special handling for `finaltest@example.com` with password `finalpass123`
- Hard-coded password hash rewrite creates security vulnerability
- **IMMEDIATE ACTION REQUIRED**: Remove test backdoor credentials

### 🐛 Technical Issues

**Frontend Import Errors**:
- `frontend/src/main.js:23` - `useUIStore` import after runtime statements breaks Vite parsing
- `frontend/src/api/index.js:89` - `useAuthStore()` called but never imported, causing ReferenceError on 401 responses
- **Impact**: Build failures and runtime errors

**API Endpoint Inconsistencies**:
- Frontend auth API expects `/api/auth/logout`, `/api/auth/change-password` but backend only implements `/api/auth/login`, `/api/auth/register`, `/api/auth/me`
- Blog API endpoints like `/posts/search`, `/posts/user/<username>`, `/posts/categories` are called by frontend but not implemented
- Thoughts API has dual endpoints (`/api/thoughts` and `/api/v1.0/thoughts`) with inconsistent pagination

**Database Migration Issues**:
- Migration files may not be in sync with model definitions
- Some migrations reference non-existent tables or columns
- **Impact**: Potential deployment failures

### ⚠️ Development Environment Issues

**Configuration Management**:
- Hardcoded database credentials in `config.py`
- Missing environment variable support for sensitive configuration
- No configuration validation on startup

**Error Handling**:
- Inconsistent error response formats across API endpoints
- Missing proper HTTP status codes in some responses
- Limited error logging and monitoring

**Code Quality**:
- Mixed Chinese and English comments throughout codebase
- Inconsistent code style and patterns
- Missing type hints and documentation

### 🔧 Recommended Improvements

**Security Enhancements**:
1. Implement proper JWT token validation with expiration
2. Remove all hardcoded test credentials and backdoors
3. Add CSRF protection for API endpoints
4. Implement proper input validation and sanitization
5. Add rate limiting for authentication endpoints

**API Consistency**:
1. Standardize response formats across all endpoints
2. Implement missing frontend-expected endpoints
3. Consolidate dual API patterns for thoughts
4. Add proper API versioning strategy
5. Implement comprehensive error handling

**Frontend Fixes**:
1. Fix import order issues in `main.js`
2. Add missing imports in API layer
3. Implement proper error boundaries
4. Add loading states for all async operations
5. Improve TypeScript-like prop validation

**Development Workflow**:
1. Set up proper environment configuration
2. Add pre-commit hooks for code quality
3. Implement comprehensive testing suite
4. Add proper logging and monitoring
5. Create deployment documentation

### Development Best Practices

**State Management Patterns**:
- Use Pinia stores consistently across components
- Implement proper error boundaries and loading states
- Follow optimistic updates for better UX
- Maintain proper separation of concerns

**Frontend Development**:
- Always run `npm run lint` before commits
- Use composition API with `<script setup>` syntax
- Implement proper prop validation and error handling
- Follow responsive design principles

**Backend Development**:
- Follow Flask blueprint structure for new features
- Implement proper API versioning and documentation
- Use SQLAlchemy models for all database operations
- Follow RESTful API design principles

### Configuration Management

**Development Environment Setup**:
1. Copy `config.example.py` to `config.py` for local development
2. Configure MySQL database connection parameters
3. Set up proper environment variables for sensitive data
4. Run `python manage.py db upgrade` after pulling changes
5. Initialize roles with `Role.insert_roles()`

**Frontend Configuration**:
- Vite dev server proxies API requests to Flask backend
- Tailwind CSS configured with custom design tokens
- Hot module replacement enabled for rapid development
- Proper CORS configuration for API communication