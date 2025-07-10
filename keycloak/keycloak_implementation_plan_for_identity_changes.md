# Keycloak Implementation Plan for Handling User Identity Changes

## Overview

This implementation plan outlines how to enhance the existing Keycloak integration to solve the issue of users recreating their IdP accounts with the same email but different `sub` claims. The plan builds upon the current Keycloak MVP implementation.

## Current Implementation Analysis

The current implementation includes:

1. **Keycloak as an Identity Broker**:
   - Configured with two identity providers: Login.gov and ACF AMS
   - Uses `mozilla_django_oidc` for OIDC authentication flow
   - Custom views (`LoginGovKeycloakAuthView` and `AcfAmsKeycloakAuthView`) for initiating authentication with specific IdPs

2. **Custom OIDC Backend**:
   - `CustomOIDCAuthenticationBackend` extends Mozilla's OIDC backend
   - Handles user creation and updates based on claims
   - Currently stores `sub` claim in `login_gov_uuid` field for Login.gov users
   - Stores `hhs_id` for ACF AMS users

3. **Missing Functionality**:
   - No mechanism to handle users with new `sub` claims but the same email
   - No account linking capability for existing users
   - No tracking of previous identity information

## Implementation Plan

### 1. Enhance the User Model

Add fields to track previous identity information:

```python
# tdpservice/users/models.py

class User(AbstractUser):
    # Existing fields
    ...
    
    # New fields for identity management
    previous_identities = models.JSONField(
        default=dict, 
        blank=True, 
        help_text="Dictionary of previous identity information, keyed by provider"
    )
    keycloak_id = models.CharField(
        max_length=255, 
        null=True, 
        blank=True, 
        help_text="Keycloak internal user ID"
    )
    
    # Helper methods for identity management
    def add_previous_identity(self, provider, identity_id):
        """Add a previous identity to the user's record."""
        if not self.previous_identities:
            self.previous_identities = {}
            
        if provider not in self.previous_identities:
            self.previous_identities[provider] = []
            
        if identity_id and identity_id not in self.previous_identities[provider]:
            self.previous_identities[provider].append(identity_id)
            self.save(update_fields=['previous_identities'])
            
    def has_previous_identity(self, provider, identity_id):
        """Check if the user has a specific previous identity."""
        if not self.previous_identities or provider not in self.previous_identities:
            return False
            
        return identity_id in self.previous_identities[provider]
```

### 2. Enhance the OIDC Backend

Modify the OIDC backend to handle identity changes:

```python
# tdpservice/users/oidc_backend.py

class CustomOIDCAuthenticationBackend(OIDCAuthenticationBackend):
    """Custom OIDC Authentication Backend to ensure consistent user mapping."""

    def filter_users_by_claims(self, claims):
        """Find users by claims, prioritizing sub but falling back to email."""
        sub = claims.get('sub')
        email = claims.get('email')
        
        if not email:
            return self.UserModel.objects.none()
        
        # Determine the provider from claims
        provider = self._determine_provider_from_claims(claims)
        
        if provider == 'login-gov':
            users = self.UserModel.objects.filter(login_gov_uuid=sub)
        elif provider == 'acf-ams':
            users = self.UserModel.objects.filter(hhs_id=sub)
        else:
            users = self.UserModel.objects.none()
            
        if users:
            return users
            
        # Then check if this sub is in any user's previous_identities
        users = self.UserModel.objects.filter(
            previous_identities__contains={provider: [sub]}
        )
        if users:
            logger.info(f"Found user by previous identity: {provider}:{sub}")
            return users
            
        # Finally, try to find by email if we're allowed to link accounts
        if settings.ALLOW_EMAIL_ACCOUNT_LINKING and email:
            users = self.UserModel.objects.filter(email=email)
            if users:
                logger.info(f"Found user by email {email} with different {provider} identity")
                return users
                
        return self.UserModel.objects.none()
        
    def _determine_provider_from_claims(self, claims):
        """Determine the identity provider from claims."""
        # This is a simplified version - in production, you'd want more robust logic
        # based on the specific claims or issuer information
        if 'hhs_id' in claims:
            return 'acf-ams'
        return 'login-gov'

    def create_user(self, claims):
        """Create a new user from claims."""
        user = super().create_user(claims)
        user.username = claims.get('preferred_username', '')
        user.email = claims.get('email', '')
        
        # Set the appropriate ID based on provider
        provider = self._determine_provider_from_claims(claims)
        sub = claims.get('sub', '')
        
        if provider == 'login-gov':
            user.login_gov_uuid = sub
        elif provider == 'acf-ams':
            user.hhs_id = claims.get('hhs_id', '')
            
        # Store Keycloak ID if available
        user.keycloak_id = claims.get('keycloak_id', '')
        user.save()
        
        return user

    def update_user(self, user, claims):
        """Update existing user with new claims."""
        provider = self._determine_provider_from_claims(claims)
        sub = claims.get('sub', '')
        
        # Handle identity changes
        if provider == 'login-gov' and user.login_gov_uuid and str(user.login_gov_uuid) != sub:
            # Store the old login.gov UUID
            user.add_previous_identity('login-gov', str(user.login_gov_uuid))
            user.login_gov_uuid = sub
            logger.info(f"Updated user {user.id} with new login.gov identity: {sub}")
            
        elif provider == 'acf-ams' and user.hhs_id and user.hhs_id != claims.get('hhs_id', ''):
            # Store the old HHS ID
            user.add_previous_identity('acf-ams', user.hhs_id)
            user.hhs_id = claims.get('hhs_id', '')
            logger.info(f"Updated user {user.id} with new ACF AMS identity: {user.hhs_id}")
            
        # Update common fields
        user.username = claims.get('preferred_username', '')
        user.email = claims.get('email', '')
        user.keycloak_id = claims.get('keycloak_id', '')
        user.save()
        
        return user
```

### 3. Configure Keycloak for Account Linking

#### 3.1 Update Realm Configuration

Update the Keycloak realm configuration to enable account linking:

```json
// keycloak/app/tdp-realm.json (partial)
{
  "identityProviders": [
    {
      "alias": "login-gov",
      "displayName": "Login.gov",
      "providerId": "oidc",
      "enabled": true,
      "updateProfileFirstLoginMode": "on",
      "trustEmail": true,
      "storeToken": true,
      "addReadTokenRoleOnCreate": false,
      "authenticateByDefault": false,
      "linkOnly": false,
      "firstBrokerLoginFlowAlias": "first broker login with email verification",
      "config": {
        // existing config
      }
    },
    {
      "alias": "acf-ams",
      "displayName": "ACF AMS",
      "providerId": "oidc",
      "enabled": true,
      "updateProfileFirstLoginMode": "on",
      "trustEmail": true,
      "storeToken": true,
      "addReadTokenRoleOnCreate": false,
      "authenticateByDefault": false,
      "linkOnly": false,
      "firstBrokerLoginFlowAlias": "first broker login with email verification",
      "config": {
        // existing config
      }
    }
  ]
}
```

#### 3.2 Create Custom Authentication Flow

Create a custom authentication flow in Keycloak for first broker login with email verification:

1. In Keycloak Admin Console, go to "Authentication" > "Flows"
2. Create a copy of the "first broker login" flow and name it "first broker login with email verification"
3. Configure the flow with the following execution steps:
   - Review Profile (REQUIRED)
   - Create User If Unique (ALTERNATIVE)
   - Handle Existing Account (ALTERNATIVE)
   - Confirm Link Existing Account (REQUIRED)
   - Verify Existing Account By Email (REQUIRED)
   - Email Verification (ALTERNATIVE)
   - Password Form (ALTERNATIVE)

#### 3.3 Configure User Federation (Maybe)

Configure Keycloak to use the Django database as a user federation source:

1. In Keycloak Admin Console, go to "User Federation"
2. Add a new "ldap" provider (we'll use LDAP as a proxy to our Django database)
3. Configure connection parameters to point to a lightweight LDAP proxy service that connects to Django's database

### 4. Update Django Settings

Add settings to control account linking behavior:

```python
# tdpservice/settings/common.py

# Add settings to control account linking behavior
ALLOW_EMAIL_ACCOUNT_LINKING = strtobool(os.getenv("ALLOW_EMAIL_ACCOUNT_LINKING", "yes"))
REQUIRE_EMAIL_VERIFICATION_FOR_LINKING = strtobool(os.getenv("REQUIRE_EMAIL_VERIFICATION_FOR_LINKING", "yes"))

# Configure Mozilla OIDC settings
OIDC_STORE_ACCESS_TOKEN = True
OIDC_STORE_REFRESH_TOKEN = True
OIDC_STORE_ID_TOKEN = True

# Pass Keycloak ID to the application
OIDC_CLAIMS_MATCH = {
    'keycloak_id': 'sub',  # Map Keycloak's internal sub to our keycloak_id field
}
```

### 5. Implement Account Linking API

Create an API endpoint to handle manual account linking:

```python
# tdpservice/users/api/account_linking.py

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
import logging

logger = logging.getLogger(__name__)

class AccountLinkingView(APIView):
    """API view to handle account linking requests."""
    
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """Link a new identity to the current user."""
        user = request.user
        provider = request.data.get('provider')
        identity_id = request.data.get('identity_id')
        
        if not provider or not identity_id:
            return Response(
                {"error": "Missing provider or identity_id"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        # Store the new identity
        user.add_previous_identity(provider, identity_id)
        
        logger.info(
            f"Manually linked {provider} identity {identity_id} to user {user.id}",
            extra={
                "user_id": user.id,
                "provider": provider,
                "identity_id": identity_id
            }
        )
        
        return Response({"status": "success"}, status=status.HTTP_200_OK)
```

Add the URL pattern:

```python
# tdpservice/users/urls.py

urlpatterns = [
    # existing patterns
    path('account-linking/', AccountLinkingView.as_view(), name='account-linking'),
]
```

### 6. Implement Migration Strategy

#### 6.1 Data Migration

Create a data migration to initialize the new fields:

```python
# tdpservice/users/migrations/XXXX_add_previous_identities.py

from django.db import migrations

def initialize_previous_identities(apps, schema_editor):
    User = apps.get_model('users', 'User')
    
    # For each user, initialize the previous_identities field
    for user in User.objects.all():
        user.previous_identities = {}
        user.save()

class Migration(migrations.Migration):
    dependencies = [
        ('users', 'XXXX_previous_migration'),
    ]
    
    operations = [
        migrations.RunPython(initialize_previous_identities),
    ]
```

### 7. Security Considerations

1. **Email Verification**: Always require email verification before linking accounts to prevent unauthorized access.

2. **Audit Logging**: Implement comprehensive logging for all account linking events:

```python
# tdpservice/users/oidc_backend.py

def update_user(self, user, claims):
    """Update existing user with new claims."""
    provider = self._determine_provider_from_claims(claims)
    sub = claims.get('sub', '')
    
    # If the sub claim has changed, store the old one and log the event
    if provider == 'login-gov' and user.login_gov_uuid and str(user.login_gov_uuid) != sub:
        logger.warning(
            f"Sub claim changed for user {user.id}: {user.login_gov_uuid} -> {sub}",
            extra={
                "user_id": user.id,
                "old_sub": user.login_gov_uuid,
                "new_sub": sub,
                "email": user.email,
                "provider": provider
            }
        )
        user.add_previous_identity('login-gov', str(user.login_gov_uuid))
        user.login_gov_uuid = sub
    
    # Rest of the method...
```

3. **Admin Notifications**: Send notifications to administrators when account linking occurs.

## Request Flow for New Sub Claims

### High-Level Authentication Flow

The following diagram illustrates what happens when a user logs in with a new `sub` claim but the same email address:

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  User logs  │     │  Keycloak   │     │   Django    │     │    Email    │
│  in via IdP │────▶│  processes  │────▶│   OIDC      │────▶│ Verification│
│             │     │   login     │     │  Backend    │     │   Challenge │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
                                                                    │
                                                                    ▼
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────-┐
│  User       │     │  Account    │     │  Previous   │     │ User clicks  │
│  logged in  │◀────│  linked     │◀────│  identity   │◀────│ verification │
│             │     │             │     │  stored     │     │ link in email│
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────-┘
```

### Detailed Flow

1. **Initial Authentication**:
   - User logs in through an IdP (Login.gov or ACF AMS)
   - IdP returns claims including `sub` and `email`
   - Keycloak processes the authentication and passes claims to Django

2. **User Lookup**:
   - Django OIDC backend attempts to find a user with the provided `sub` claim
   - If not found, it checks for users with this `sub` in their previous identities
   - If still not found, it checks for users with the same email (if email linking is allowed)

3. **New Sub Claim Handling**:
   - If a user is found by email but has a different `sub` claim:
     - If email verification is required: Send verification email and deny immediate login
     - If email verification is not required: Link the new identity immediately

4. **Email Verification**:
   - User receives verification email with a secure link/token
   - User clicks the link or enters the verification code
   - System verifies the token and links the new identity to the existing account
   - The old `sub` claim is stored in the user's previous identities

5. **Completion**:
   - User can now log in with either identity
   - All user data and permissions are preserved
   - Audit logs record the identity linking event

This flow ensures that only the legitimate owner of both the email address and the original account can link a new identity, providing strong security while maintaining a good user experience.

## Conclusion

This implementation plan leverages Keycloak's identity federation capabilities to solve the issue of users recreating their IdP accounts with the same email but different `sub` claims. By enhancing the existing implementation with account linking features and proper tracking of previous identities, we can ensure a seamless user experience while maintaining security.

The solution specifically addresses the problem by:

1. Storing previous identity information in a flexible JSON field
2. Enhancing the authentication backend to check for users by previous identities and email
3. Configuring Keycloak to handle account linking with proper security measures
4. Implementing comprehensive testing and monitoring

This approach provides a robust solution that maintains security while improving the user experience.
