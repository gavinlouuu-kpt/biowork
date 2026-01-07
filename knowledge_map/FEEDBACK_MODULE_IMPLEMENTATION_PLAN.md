# Feedback Module Implementation Plan

## Overview
This document outlines the plan for implementing a feedback module in Django that allows users to easily submit feedback about the application.

## Architecture Overview

### Module Structure
Following the existing Django app pattern in this project:
- `label_studio/feedback/` - New Django app
  - `models.py` - Feedback data models
  - `api.py` - REST API views
  - `serializers.py` - DRF serializers
  - `urls.py` - URL routing
  - `admin.py` - Django admin configuration
  - `migrations/` - Database migrations
  - `apps.py` - App configuration

## Data Model Design

### Feedback Model
```python
class Feedback(models.Model):
    """
    User feedback submission model
    """
    # User association (nullable for anonymous feedback)
    user = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='feedback_submissions'
    )
    
    # Organization context (optional, for organization-specific feedback)
    organization = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='feedback_submissions'
    )
    
    # Project context (optional, for project-specific feedback)
    project = models.ForeignKey(
        'projects.Project',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='feedback_submissions'
    )
    
    # Feedback content
    title = models.CharField(max_length=255, blank=True)
    message = models.TextField(help_text='Feedback message')
    
    # Feedback type/category
    FEEDBACK_TYPES = [
        ('bug', 'Bug Report'),
        ('feature', 'Feature Request'),
        ('improvement', 'Improvement Suggestion'),
        ('question', 'Question'),
        ('other', 'Other'),
    ]
    feedback_type = models.CharField(
        max_length=20,
        choices=FEEDBACK_TYPES,
        default='other'
    )
    
    # Priority/Urgency (optional)
    PRIORITY_LEVELS = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    priority = models.CharField(
        max_length=20,
        choices=PRIORITY_LEVELS,
        default='medium',
        blank=True
    )
    
    # Status tracking
    STATUS_CHOICES = [
        ('new', 'New'),
        ('acknowledged', 'Acknowledged'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    ]
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='new'
    )
    
    # Additional metadata
    user_email = models.EmailField(blank=True, help_text='Email if user not logged in')
    user_name = models.CharField(max_length=255, blank=True)
    page_url = models.URLField(blank=True, help_text='URL where feedback was submitted from')
    browser_info = models.CharField(max_length=255, blank=True)
    user_agent = models.TextField(blank=True)
    
    # Admin response
    admin_response = models.TextField(blank=True, help_text='Response from admin/team')
    responded_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='feedback_responses'
    )
    responded_at = models.DateTimeField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'feedback'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['feedback_type', '-created_at']),
            models.Index(fields=['organization', '-created_at']),
        ]
    
    def __str__(self):
        return f"Feedback #{self.id} - {self.get_feedback_type_display()}"
```

### FeedbackAttachment Model (Optional)
```python
class FeedbackAttachment(models.Model):
    """
    File attachments for feedback submissions
    """
    feedback = models.ForeignKey(
        Feedback,
        on_delete=models.CASCADE,
        related_name='attachments'
    )
    file = models.FileField(upload_to='feedback/attachments/')
    filename = models.CharField(max_length=255)
    file_size = models.IntegerField()
    content_type = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'feedback_attachment'
```

## API Design

### Endpoints

#### 1. Submit Feedback (POST)
- **URL**: `/api/feedback/`
- **Method**: POST
- **Authentication**: Optional (allows anonymous feedback)
- **Permissions**: AllowAny
- **Request Body**:
  ```json
  {
    "title": "Optional title",
    "message": "Feedback message (required)",
    "feedback_type": "bug|feature|improvement|question|other",
    "priority": "low|medium|high|critical",
    "user_email": "email@example.com",  // if not authenticated
    "user_name": "Name",  // if not authenticated
    "page_url": "https://...",
    "project": 123,  // optional project ID
    "attachments": [file1, file2]  // optional files
  }
  ```
- **Response**: 201 Created with feedback object

#### 2. List Feedback (GET)
- **URL**: `/api/feedback/`
- **Method**: GET
- **Authentication**: Required
- **Permissions**: 
  - Users can see their own feedback
  - Staff/Admins can see all feedback
- **Query Parameters**:
  - `status`: Filter by status
  - `feedback_type`: Filter by type
  - `project`: Filter by project ID
  - `organization`: Filter by organization ID
  - `user`: Filter by user ID (staff only)
- **Response**: Paginated list of feedback

#### 3. Get Feedback Detail (GET)
- **URL**: `/api/feedback/<id>/`
- **Method**: GET
- **Authentication**: Required
- **Permissions**: 
  - Users can view their own feedback
  - Staff can view any feedback
- **Response**: Feedback object with details

#### 4. Update Feedback Status (PATCH/PUT)
- **URL**: `/api/feedback/<id>/`
- **Method**: PATCH/PUT
- **Authentication**: Required
- **Permissions**: Staff only
- **Request Body**:
  ```json
  {
    "status": "acknowledged|in_progress|resolved|closed",
    "admin_response": "Response message",
    "priority": "low|medium|high|critical"
  }
  ```
- **Response**: Updated feedback object

#### 5. Get Current User Feedback (GET)
- **URL**: `/api/current-user/feedback/`
- **Method**: GET
- **Authentication**: Required
- **Permissions**: IsAuthenticated
- **Response**: List of current user's feedback submissions

## Serializers

### FeedbackSerializer (for creation)
- Fields: title, message, feedback_type, priority, user_email, user_name, page_url, project
- Validation: message is required, feedback_type must be valid choice

### FeedbackListSerializer (for list views)
- Fields: id, title, message (truncated), feedback_type, status, priority, created_at, user, project
- Read-only fields: id, created_at, user

### FeedbackDetailSerializer (for detail views)
- All fields including admin_response, responded_by, responded_at
- Includes attachments if implemented

### FeedbackUpdateSerializer (for staff updates)
- Fields: status, admin_response, priority
- Validation: status transitions, admin_response required when status changes to resolved

## Permissions

### Permission Classes
- `AllowAny` - For submitting feedback (public endpoint)
- `IsAuthenticated` - For viewing own feedback
- `IsStaffOrReadOnly` - For staff to manage all feedback
- Custom permission: Users can only view/edit their own feedback unless staff

### Permission Strings (add to core/permissions.py)
```python
feedback_create: str = 'feedback.create'
feedback_view: str = 'feedback.view'
feedback_change: str = 'feedback.change'
feedback_delete: str = 'feedback.delete'
```

## URL Configuration

### feedback/urls.py
```python
from django.urls import include, path
from . import api

app_name = 'feedback'

_api_urlpatterns = [
    path('', api.FeedbackListCreateAPI.as_view(), name='feedback-list-create'),
    path('<int:pk>/', api.FeedbackDetailAPI.as_view(), name='feedback-detail'),
    path('current-user/', api.CurrentUserFeedbackAPI.as_view(), name='current-user-feedback'),
]

urlpatterns = [
    path('api/feedback/', include((_api_urlpatterns, app_name), namespace='api')),
]
```

### Update core/urls.py
Add: `re_path(r'^', include('feedback.urls')),`

## Django Admin Integration

### Admin Configuration
- List display: id, title, feedback_type, status, user, created_at
- List filters: status, feedback_type, priority, created_at
- Search fields: title, message, user_email
- Read-only fields: created_at, updated_at
- Actions: Bulk status updates, export to CSV

## Frontend Integration Points

### React Components Needed
1. **FeedbackForm Component**
   - Modal or dedicated page
   - Form fields: type, title, message, priority, optional email/name
   - File upload support (if attachments implemented)
   - Submit button with loading state

2. **FeedbackButton Component**
   - Floating action button or header button
   - Opens feedback form modal
   - Can be placed in navigation or footer

3. **FeedbackList Component** (for user dashboard)
   - Display user's submitted feedback
   - Status indicators
   - Filter by type/status

4. **Admin Feedback Management** (for staff)
   - Full CRUD interface
   - Status management
   - Response functionality

### API Integration
- Use existing TanStack Query (React Query) setup
- Create hooks: `useSubmitFeedback`, `useFeedbackList`, `useFeedbackDetail`
- Error handling and success notifications

## Database Migration Strategy

1. Create initial migration for Feedback model
2. Create migration for FeedbackAttachment (if implemented)
3. Add indexes for performance
4. Consider adding full-text search index on message field if needed

## Security Considerations

1. **Rate Limiting**: Implement rate limiting on feedback submission endpoint
   - Use django-ratelimit or similar
   - Limit: e.g., 10 submissions per hour per IP/user

2. **File Upload Security** (if attachments implemented)
   - Validate file types (images, PDFs, text files)
   - Limit file size (e.g., 10MB per file, 50MB total)
   - Scan for malware if possible
   - Store in secure location

3. **Input Validation**
   - Sanitize HTML in messages (use bleach)
   - Validate email format
   - Limit message length (e.g., 5000 characters)

4. **Privacy**
   - Allow anonymous submissions
   - Don't expose user emails in list views (unless staff)
   - GDPR compliance considerations

## Notification System (Optional Enhancement)

1. **Email Notifications**
   - Notify admins when new feedback is submitted
   - Notify users when their feedback status changes
   - Use django-rq for async email sending

2. **In-App Notifications**
   - Show notification badge for new feedback (admin)
   - Show status updates to users

## Testing Strategy

### Unit Tests
- Model validation
- Serializer validation
- Permission checks
- API endpoint responses

### Integration Tests
- Full feedback submission flow
- Authentication scenarios
- Permission scenarios
- File upload (if implemented)

### Test Files
- `feedback/tests/test_models.py`
- `feedback/tests/test_serializers.py`
- `feedback/tests/test_api.py`
- `feedback/tests/test_permissions.py`

## Implementation Steps

### Phase 1: Core Backend (MVP)
1. Create Django app structure
2. Implement Feedback model
3. Create migrations
4. Implement basic serializers
5. Create API endpoints (submit, list own feedback)
6. Add URL routing
7. Register app in INSTALLED_APPS
8. Add permissions
9. Basic admin configuration

### Phase 2: Enhanced Features
1. Add FeedbackAttachment model (if needed)
2. Implement file upload handling
3. Add admin response functionality
4. Enhanced admin interface
5. Add filtering and search

### Phase 3: Frontend Integration
1. Create FeedbackForm React component
2. Create FeedbackButton component
3. Integrate with existing UI (Ant Design)
4. Add to navigation/footer
5. Create user feedback list view
6. Create admin management interface

### Phase 4: Polish & Security
1. Add rate limiting
2. Implement security measures
3. Add email notifications
4. Performance optimization
5. Documentation

## Configuration Options

### Settings (core/settings/base.py)
```python
# Feedback module settings
FEEDBACK_ENABLE_ANONYMOUS = True
FEEDBACK_ENABLE_ATTACHMENTS = True
FEEDBACK_MAX_ATTACHMENT_SIZE = 10 * 1024 * 1024  # 10MB
FEEDBACK_ALLOWED_FILE_TYPES = ['image/*', 'application/pdf', 'text/*']
FEEDBACK_RATE_LIMIT = '10/h'  # 10 per hour
FEEDBACK_NOTIFY_ADMINS = True
FEEDBACK_ADMIN_EMAILS = []  # List of admin emails to notify
```

## Future Enhancements

1. **Feedback Categories/Tags**: Allow custom categorization
2. **Voting System**: Users can upvote feature requests
3. **Public Feedback Board**: Public view of feature requests (with voting)
4. **Integration with Issue Trackers**: Auto-create GitHub/Jira issues
5. **Analytics Dashboard**: Feedback metrics and trends
6. **Screenshot Tool**: Built-in screenshot capture for bug reports
7. **Feedback Templates**: Pre-filled templates for common feedback types

## Dependencies

No new dependencies required - uses existing:
- Django REST Framework
- drf-yasg (for API docs)
- django-filter (for filtering)
- Existing authentication system

## Documentation

1. API documentation (auto-generated via drf-yasg)
2. User guide for submitting feedback
3. Admin guide for managing feedback
4. Developer documentation for extending the module

## Success Metrics

1. Number of feedback submissions
2. Response time to feedback
3. User satisfaction with feedback process
4. Bug reports vs feature requests ratio
5. Resolution rate
