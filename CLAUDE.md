# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Codebase Architecture

This is a Flask web application with a blog-like structure. The main components are:

1. **Application Structure**:
   - `app/__init__.py`: Main application factory with Flask extensions initialization
   - `app/models.py`: Database models (User, Role, Post) with SQLAlchemy
   - `app/main/`: Main blueprint with views for blog functionality
   - `app/auth/`: Authentication blueprint
   - `app/api_1_0/`: REST API blueprint
   - `config.py`: Configuration classes for different environments
   - `manage.py`: Flask-Script manager for CLI commands

2. **Key Features**:
   - User authentication and roles (User, Role models with permissions)
   - Blog post creation, editing, and deletion
   - File upload functionality
   - REST API for posts
   - Pagination for blog posts

3. **Database Models**:
   - `User`: Authentication, profile info, posts relationship
   - `Role`: Permission-based roles (User, Moderator, Admin)
   - `Post`: Blog posts with markdown support

## Development Commands

### Running the Application
```bash
python manage.py runserver
```

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

- Flask 0.11.1
- SQLAlchemy for ORM
- Flask-Login for authentication
- Flask-Migrate for database migrations
- Flask-Script for CLI commands
- Markdown and bleach for post formatting
- PyMySQL for MySQL database connection

## Configuration

The application uses different configuration classes in `config.py`:
- DevelopmentConfig: Development environment with debug
- TestingConfig: Testing environment
- ProductionConfig: Production environment
- Default: DevelopmentConfig

Database connections are configured for MySQL with PyMySQL driver.