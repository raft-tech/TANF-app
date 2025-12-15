# Generic Audit Log System - Design Analysis

## Overview

This document analyzes the existing `ChangeRequestAuditLog` model and the proposed `FeatureFlagAuditLog` model to design a **generic, reusable audit logging system** that can track changes to any model in the application.

---

## Current State Analysis

### Existing: ChangeRequestAuditLog

**Location**: `tdrs-backend/tdpservice/users/models.py` (lines 210-242)

```python
class ChangeRequestAuditLog(models.Model):
    """Model to track audit logs for change requests."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    change_request = models.ForeignKey(UserChangeRequest, on_delete=models.CASCADE)
    action = models.CharField(max_length=50)
    performed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    details = models.JSONField(default=dict)
```

**Characteristics**:
- ✅ Simple, focused design
- ✅ Uses JSONField for flexible details
- ✅ Tracks who, when, what action
- ❌ Tightly coupled to `UserChangeRequest`
- ❌ No previous/new value tracking
- ❌ No IP address or user agent tracking
- ❌ Manual creation in views/admin

### Proposed: FeatureFlagAuditLog

**Characteristics**:
- ✅ Detailed previous/new value tracking
- ✅ IP address and user agent tracking
- ✅ Automatic via signals
- ✅ Structured change diff methods
- ❌ Tightly coupled to `FeatureFlag`
- ❌ Duplicates audit logic

---

## Comparison Matrix

| Feature | ChangeRequestAuditLog | FeatureFlagAuditLog | Generic Solution |
|---------|----------------------|---------------------|------------------|
| **Target Model** | UserChangeRequest (FK) | FeatureFlag (implicit) | Any model (GenericFK) |
| **Action Tracking** | String (50 chars) | Enum (CREATE/UPDATE/DELETE) | Enum + extensible |
| **User Tracking** | performed_by (FK) | user (FK) + username | Both |
| **Timestamp** | ✅ auto_now_add | ✅ auto_now_add | ✅ |
| **Previous Values** | ❌ (in details JSON) | ✅ Structured fields | ✅ JSONField |
| **New Values** | ❌ (in details JSON) | ✅ Structured fields | ✅ JSONField |
| **IP Address** | ❌ | ✅ | ✅ |
| **User Agent** | ❌ | ✅ | ✅ |
| **Change Reason** | ❌ | ✅ | ✅ |
| **Details/Metadata** | ✅ JSONField | ❌ | ✅ JSONField |
| **Creation Method** | Manual (views/admin) | Automatic (signals) | Both |
| **Diff Calculation** | ❌ | ✅ get_changes_summary() | ✅ Generic diff |

---

## Recommended Solution: Generic Audit Log

### Design Principles

1. **Use Django's ContentTypes framework** for generic foreign keys
2. **Combine best features** from both existing approaches
3. **Backward compatible** - can replace both existing audit logs
4. **Automatic and manual** - support both signal-based and explicit logging
5. **Extensible** - easy to add new audited models

### Proposed Model: AuditLog

**Location**: `tdrs-backend/tdpservice/core/models/audit_log.py`

```python
from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import get_user_model
import uuid
import json

User = get_user_model()

class AuditAction(models.TextChoices):
    """Standard audit actions."""
    CREATE = 'CREATE', 'Created'
    UPDATE = 'UPDATE', 'Updated'
    DELETE = 'DELETE', 'Deleted'
    APPROVE = 'APPROVE', 'Approved'
    REJECT = 'REJECT', 'Rejected'
    ENABLE = 'ENABLE', 'Enabled'
    DISABLE = 'DISABLE', 'Disabled'
    # Extensible - add more as needed

class AuditLog(models.Model):
    """
    Generic audit log for tracking changes to any model.

    Uses Django's ContentTypes framework to create a generic foreign key
    that can point to any model instance.

    Example usage:
        # Automatic (via signals)
        @audit_model(fields=['enabled', 'extra_state'])
        class FeatureFlag(models.Model):
            ...

        # Manual
        AuditLog.log_change(
            instance=my_feature_flag,
            action=AuditAction.UPDATE,
            user=request.user,
            previous_values={'enabled': False},
            new_values={'enabled': True}
        )
    """

    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Audit Log'
        verbose_name_plural = 'Audit Logs'
        indexes = [
            models.Index(fields=['content_type', 'object_id', '-timestamp']),
            models.Index(fields=['user', '-timestamp']),
            models.Index(fields=['-timestamp']),
            models.Index(fields=['action', '-timestamp']),
        ]

    # Primary key
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Generic foreign key to any model
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        help_text="Type of object that was changed"
    )
    object_id = models.CharField(
        max_length=255,
        db_index=True,
        help_text="ID of the object that was changed"
    )
    content_object = GenericForeignKey('content_type', 'object_id')

    # What happened
    action = models.CharField(
        max_length=20,
        choices=AuditAction.choices,
        help_text="Action that was performed"
    )

    # Who did it
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audit_logs',
        help_text="User who performed the action"
    )
    username = models.CharField(
        max_length=150,
        help_text="Username at time of action (preserved if user deleted)"
    )

    # When it happened
    timestamp = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        help_text="When the action occurred"
    )

    # What changed
    previous_values = models.JSONField(
        null=True,
        blank=True,
        help_text="Previous values before the change (null for CREATE)"
    )
    new_values = models.JSONField(
        null=True,
        blank=True,
        help_text="New values after the change (null for DELETE)"
    )

    # Context
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        help_text="IP address of the user"
    )
    user_agent = models.TextField(
        blank=True,
        help_text="User agent string"
    )

    # Additional metadata
    change_reason = models.TextField(
        blank=True,
        help_text="Optional reason for the change"
    )
    details = models.JSONField(
        default=dict,
        blank=True,
        help_text="Additional metadata about the action"
    )

    # Object representation at time of change
    object_repr = models.CharField(
        max_length=200,
        help_text="String representation of the object at time of change"
    )

    def __str__(self):
        return f"{self.object_repr} - {self.get_action_display()} by {self.username}"

    @classmethod
    def log_change(cls, instance, action, user=None, request=None,
                   previous_values=None, new_values=None,
                   change_reason='', details=None):
        """
        Create an audit log entry.

        Args:
            instance: The model instance being audited
            action: AuditAction enum value
            user: User performing the action (optional)
            request: HTTP request object (optional, for IP/user agent)
            previous_values: Dict of previous field values
            new_values: Dict of new field values
            change_reason: Optional reason for the change
            details: Additional metadata dict

        Returns:
            AuditLog instance
        """
        # Get user info
        if user is None and request:
            user = getattr(request, 'user', None)

        username = user.username if user and user.is_authenticated else 'system'

        # Get request context
        ip_address = None
        user_agent = ''
        if request:
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                ip_address = x_forwarded_for.split(',')[0].strip()
            else:
                ip_address = request.META.get('REMOTE_ADDR')
            user_agent = request.META.get('HTTP_USER_AGENT', '')[:500]

        # Create audit log
        return cls.objects.create(
            content_object=instance,
            action=action,
            user=user if user and user.is_authenticated else None,
            username=username,
            previous_values=previous_values or {},
            new_values=new_values or {},
            ip_address=ip_address,
            user_agent=user_agent,
            change_reason=change_reason,
            details=details or {},
            object_repr=str(instance)[:200]
        )

    def get_changes_summary(self):
        """Generate human-readable summary of changes."""
        if self.action == AuditAction.CREATE:
            return f"Created with {len(self.new_values or {})} fields"

        if self.action == AuditAction.DELETE:
            return f"Deleted (had {len(self.previous_values or {})} fields)"

        # For UPDATE and other actions, show what changed
        prev = self.previous_values or {}
        new = self.new_values or {}

        changes = []
        for key in set(prev.keys()) | set(new.keys()):
            if key not in prev:
                changes.append(f"{key} added")
            elif key not in new:
                changes.append(f"{key} removed")
            elif prev[key] != new[key]:
                changes.append(f"{key}: {prev[key]} → {new[key]}")

        return "; ".join(changes) if changes else "No field changes"

    def get_field_diff(self, field_name):
        """Get the diff for a specific field."""
        prev = (self.previous_values or {}).get(field_name)
        new = (self.new_values or {}).get(field_name)

        if prev == new:
            return None

        return {
            'field': field_name,
            'previous': prev,
            'new': new,
            'changed': prev != new
        }

    def get_all_changed_fields(self):
        """Get list of all fields that changed."""
        prev = self.previous_values or {}
        new = self.new_values or {}

        changed = []
        for key in set(prev.keys()) | set(new.keys()):
            if prev.get(key) != new.get(key):
                changed.append(key)

        return changed
```

---

## Migration Strategy

### Phase 1: Create Generic AuditLog

1. Create new `AuditLog` model
2. Run migrations
3. Test with new features (e.g., FeatureFlag)

### Phase 2: Migrate ChangeRequestAuditLog

**Option A: Keep both (Recommended for now)**
- Keep `ChangeRequestAuditLog` for backward compatibility
- New change requests use `AuditLog`
- Gradually migrate old data

**Option B: Full migration**
- Create data migration to convert `ChangeRequestAuditLog` → `AuditLog`
- Update all views/serializers
- Remove old model

### Phase 3: Extend to Other Models

Add audit logging to:
- User model changes
- Feedback status changes
- STT/Region changes
- Data file operations
- Any other critical models

---

## Usage Examples

### Automatic Auditing (Decorator Pattern)

```python
# tdrs-backend/tdpservice/core/decorators.py

from functools import wraps
from django.db.models.signals import post_save, post_delete, pre_save

def audit_model(fields=None, actions=None):
    """
    Decorator to automatically audit model changes.

    Usage:
        @audit_model(fields=['enabled', 'extra_state'])
        class FeatureFlag(models.Model):
            ...
    """
    def decorator(model_class):
        # Store previous state
        def store_previous(sender, instance, **kwargs):
            if instance.pk and fields:
                try:
                    previous = sender.objects.get(pk=instance.pk)
                    instance._audit_previous = {
                        field: getattr(previous, field)
                        for field in fields
                    }
                except sender.DoesNotExist:
                    instance._audit_previous = None

        # Log changes
        def log_change(sender, instance, created, **kwargs):
            from .models.audit_log import AuditLog, AuditAction
            from .signals import get_current_request

            action = AuditAction.CREATE if created else AuditAction.UPDATE
            request = get_current_request()

            previous_values = getattr(instance, '_audit_previous', None) if not created else None
            new_values = {field: getattr(instance, field) for field in fields} if fields else None

            AuditLog.log_change(
                instance=instance,
                action=action,
                request=request,
                previous_values=previous_values,
                new_values=new_values
            )

        # Log deletions
        def log_deletion(sender, instance, **kwargs):
            from .models.audit_log import AuditLog, AuditAction
            from .signals import get_current_request

            previous_values = {field: getattr(instance, field) for field in fields} if fields else None

            AuditLog.log_change(
                instance=instance,
                action=AuditAction.DELETE,
                request=get_current_request(),
                previous_values=previous_values
            )

        # Connect signals
        pre_save.connect(store_previous, sender=model_class)
        post_save.connect(log_change, sender=model_class)
        post_delete.connect(log_deletion, sender=model_class)

        return model_class

    return decorator
```

### Manual Auditing

```python
from tdpservice.core.models.audit_log import AuditLog, AuditAction

# In a view
def approve_change_request(request, pk):
    change_request = UserChangeRequest.objects.get(pk=pk)

    # Perform the action
    change_request.approve(request.user)

    # Log it
    AuditLog.log_change(
        instance=change_request,
        action=AuditAction.APPROVE,
        request=request,
        previous_values={'status': 'pending'},
        new_values={'status': 'approved'},
        change_reason='Approved via admin interface'
    )
```

### Querying Audit Logs

```python
from tdpservice.core.models.audit_log import AuditLog
from tdpservice.core.models import FeatureFlag
from django.contrib.contenttypes.models import ContentType

# Get all logs for a specific instance
feature_flag = FeatureFlag.objects.get(feature_name='pia_submission')
logs = AuditLog.objects.filter(
    content_type=ContentType.objects.get_for_model(FeatureFlag),
    object_id=feature_flag.pk
)

# Get all logs for a model type
feature_flag_ct = ContentType.objects.get_for_model(FeatureFlag)
all_ff_logs = AuditLog.objects.filter(content_type=feature_flag_ct)

# Get all logs by a user
user_logs = AuditLog.objects.filter(username='admin')

# Get all CREATE actions
creates = AuditLog.objects.filter(action=AuditAction.CREATE)

# Get logs with specific field changes
logs_with_enabled_change = AuditLog.objects.filter(
    previous_values__has_key='enabled'
).exclude(
    previous_values__enabled=models.F('new_values__enabled')
)
```

---

## Admin Integration

```python
# tdrs-backend/tdpservice/core/admin.py

from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline
from .models.audit_log import AuditLog

class AuditLogInline(GenericTabularInline):
    """Inline audit logs for any model."""
    model = AuditLog
    ct_field = 'content_type'
    ct_fk_field = 'object_id'
    extra = 0
    can_delete = False
    readonly_fields = [
        'action', 'username', 'timestamp', 'changes_summary',
        'ip_address', 'change_reason'
    ]

    def changes_summary(self, obj):
        return obj.get_changes_summary()

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = [
        'object_repr', 'action', 'username', 'timestamp', 'changes_summary'
    ]
    list_filter = ['action', 'content_type', 'timestamp']
    search_fields = ['username', 'object_repr', 'change_reason']
    readonly_fields = [
        'content_type', 'object_id', 'action', 'user', 'username',
        'timestamp', 'previous_values', 'new_values', 'ip_address',
        'user_agent', 'change_reason', 'details', 'object_repr',
        'changes_summary_display'
    ]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def changes_summary_display(self, obj):
        return obj.get_changes_summary()
    changes_summary_display.short_description = 'Changes'
```

---

## Benefits of Generic Approach

### ✅ Advantages

1. **Single source of truth** - One audit system for entire application
2. **Consistent interface** - Same API for all audited models
3. **Reduced code duplication** - No need for model-specific audit logs
4. **Easier maintenance** - Changes to audit logic in one place
5. **Better queries** - Can query across all audit logs
6. **Flexible** - Works with any model via ContentTypes
7. **Backward compatible** - Can coexist with existing audit logs

### ⚠️ Considerations

1. **Generic FK performance** - Slightly slower than direct FK
   - *Mitigation*: Proper indexing, query optimization
2. **Type safety** - Less type-safe than model-specific FKs
   - *Mitigation*: Helper methods, validation
3. **Migration complexity** - Need to migrate existing data
   - *Mitigation*: Phased rollout, keep old logs

---

## Recommendation

**Implement the generic `AuditLog` model** with the following approach:

### Phase 1 (Immediate)
1. Create `AuditLog` model in `core` app
2. Use for new FeatureFlag auditing
3. Test thoroughly

### Phase 2 (Next sprint)
1. Add `AuditLogInline` to relevant admin pages
2. Create management commands for audit reports
3. Add API endpoints for querying audit logs

### Phase 3 (Future)
1. Gradually migrate `ChangeRequestAuditLog` data
2. Update views/serializers to use `AuditLog`
3. Deprecate old audit log model
4. Extend to other models (User, Feedback, etc.)

This approach gives you:
- ✅ Immediate value for feature flags
- ✅ Path to consolidation
- ✅ Minimal disruption to existing code
- ✅ Future-proof architecture

---

## Next Steps

1. Review this design with team
2. Create `AuditLog` model
3. Update Feature Toggle documentation to use generic audit log
4. Create migration plan for `ChangeRequestAuditLog`
