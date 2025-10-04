# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Environment Notes

- **Platform**: Windows environment
- **Port**: Application runs on port 5000 by default
- **Background Execution**: Always run commands in background mode on Windows to avoid encoding issues
- **Output Formatting**: Avoid using emoji in output messages to prevent character encoding errors on Windows

## Codebase Architecture

This is a Flask web application with blog-like functionality and Thino-like thought management. The main components are:

1. **Application Structure**:
   - `app/__init__.py`: Main application factory with Flask extensions initialization
   - `app/models.py`: Database models (User, Role, Post, Thought) with SQLAlchemy
   - `app/main/`: Main blueprint with views for blog and thought functionality
   - `app/auth/`: Authentication blueprint with forms and views
   - `app/api_1_0/`: REST API blueprint for posts and authentication
   - `app/decorator.py`: Custom decorators for permissions
   - `app/exceptions.py`: Custom exception handlers
   - `config.py`: Configuration classes for different environments
   - `manage.py`: Flask-Script manager for CLI commands
   - `scripts/scrawler.py`: Web scraping utilities
   - `requirements.txt`: Project dependencies

2. **Key Features**:
   - User authentication and role-based permissions (User, Moderator, Admin)
   - Blog post creation, editing, and deletion with markdown support
   - Thino-like thought management system with tags, types, and privacy controls
   - File upload functionality
   - REST API for posts and authentication
   - Pagination for blog posts and thoughts
   - Thought search and filtering by tags
   - Web scraping capabilities

3. **Database Models**:
   - `User`: Authentication, profile info, posts and thoughts relationships
   - `Role`: Permission-based roles (User, Moderator, Admin) with granular permissions
   - `Post`: Blog posts with markdown support and HTML conversion
   - `Thought`: Short thoughts/notes with tags, types (note, quote, idea, task), privacy settings

## Development Commands

### Running the Application
```bash
python manage.py runserver
```
The application runs on port 5000 by default. When running on Windows, always start the application in background mode to avoid console encoding issues.

### Database Migrations
```bash
# Create migration
python manage.py db migrate -m "Migration message"

# Apply migrations
python manage.py db upgrade
```

### Running Tests
```bash
python manage.py test
```

## Key Dependencies

- Flask 3.1.2 - Web framework
- Flask-SQLAlchemy 3.1.1 - ORM integration
- Flask-Login 0.6.3 - User session management
- Flask-Migrate 4.1.0 - Database migration support
- Flask-Script 2.0.5 - CLI command support
- Flask-WTF 1.2.1 - Form handling and CSRF protection
- Flask-Bootstrap 3.3.7.1 - Frontend framework integration
- Flask-HTTPAuth 4.8.0 - HTTP authentication
- Flask-Moment 1.0.5 - Date/time handling
- SQLAlchemy 2.0.43 - Database ORM
- PyMySQL 0.7.9 - MySQL database driver
- Markdown 3.9 - Markdown text processing
- Bleach 6.2.0 - HTML sanitization
- BeautifulSoup4 4.14.0 - Web scraping
- Pandas 2.3.2 - Data manipulation
- Requests 2.32.5 - HTTP client library

## Key Routes and Endpoints

### Main Routes (`/main`)
- `/` - Home page with recent posts and thoughts
- `/thoughts` - Create and view thoughts (GET, POST)
- `/thought/<int:id>/delete` - Soft delete a thought (POST)
- `/thoughts/tag/<tag>` - View thoughts filtered by tag
- `/thoughts/search` - Search thoughts

### Authentication Routes (`/auth`)
- `/login` - User login
- `/logout` - User logout
- `/register` - User registration
- `/confirm/<token>` - Email confirmation
- `/change-password` - Change password
- `/reset` - Password reset request
- `/reset/<token>` - Password reset confirmation

### API Routes (`/api/v1.0`)
- `/api/v1.0/posts` - Get/create posts
- `/api/v1.0/posts/<id>` - Get/update/delete post
- `/api/v1.0/users/<id>/posts` - Get posts by user
- `/api/v1.0/token` - Get authentication token

## Thought Management System

The application includes a Thino-like thought management feature:

- **Thought Types**: `note`, `quote`, `idea`, `task`
- **Tags**: Comma-separated tags for organization
- **Privacy**: Public/private thoughts with `is_public` flag
- **Soft Delete**: Thoughts are marked as deleted rather than removed
- **Search**: Full-text search across thought content
- **Source URLs**: Attach reference links to thoughts

## Permissions System

Granular permission system with the following permissions:
- `FOLLOW` (0x01): Follow other users
- `COMMENT` (0x02): Comment on posts
- `WRITE_ARTICLES` (0x04): Create blog posts
- `MODERATE_COMMENTS` (0x08): Moderate comments
- `WRITE_THOUGHTS` (0x10): Create and manage thoughts
- `ADMIN` (0x80): Full administrative access

## Configuration

The application uses different configuration classes in `config.py`:
- DevelopmentConfig: Development environment with debug
- TestingConfig: Testing environment
- ProductionConfig: Production environment
- Default: DevelopmentConfig

Database connections are configured for MySQL with PyMySQL driver.

## File Organization

### Templates
- `templates/`: Jinja2 templates organized by blueprint
  - `base.html`: Base template with Bootstrap integration
  - `auth/`: Authentication-related templates
  - `main/`: Main application templates including thoughts UI

### Static Files
- `static/`: CSS, JavaScript, and image assets
  - Bootstrap integration through Flask-Bootstrap
  - Custom styles for thought management interface

### Migrations
- `migrations/`: Alembic database migration files
  - Latest migration adds `thoughts` table (revision: 9aa327f4b400)

## Additional Features

### Markdown Processing
- Posts and thoughts support markdown formatting
- Automatic HTML conversion with bleach sanitization
- Code highlighting and link processing

### Authentication
- Token-based authentication for API endpoints
- Email confirmation for new registrations
- Password reset functionality
- Role-based access control

### Testing
- Test suite in `tests/` directory
- Run with `python manage.py test`