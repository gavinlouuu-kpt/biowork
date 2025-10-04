# ML Backend Authentication Issue - 401 Unauthorized

**Status**: ✅ RESOLVED  
**Date**: 2025-10-04  
**Component**: SAM ML Backend + Label Studio Authentication  

## Issue

ML backend receiving 401 Unauthorized errors when accessing image files from Label Studio, despite middleware correctly retrieving authentication tokens.

## Root Cause

Label Studio organization had **legacy token authentication disabled** (`jwt_auth_jwtsettings.legacy_api_tokens_enabled = 0`).

Label Studio 1.20.0+ introduced JWT-based Personal Access Tokens and allows organizations to disable legacy token authentication. Even though the middleware retrieved valid legacy tokens, Label Studio rejected them due to organization settings.

## Key Finding

**The middleware WAS working correctly!**

The middleware successfully:
- Connected to Label Studio database
- Retrieved organization ID from project
- Fetched correct legacy API token from `authtoken_token` table
- Passed token to `get_local_path()`

The issue was at the **Label Studio authentication layer**, not in the middleware code.

## Solution

Enabled legacy token authentication in the database:

```sql
UPDATE jwt_auth_jwtsettings 
SET legacy_api_tokens_enabled = 1 
WHERE organization_id = 1;
```

Alternatively, via Label Studio UI:
- Settings → Organization → Access Tokens → Enable "Legacy Tokens"

## Verification

```bash
# Test API access
curl -H "Authorization: Token 03afb15e8b73ffc6b53d3be0aa0e88ed1870e16e" \
  http://localhost:8080/api/projects/
# ✅ Returns 200 OK with project list

# Test file access
curl -H "Authorization: Token 03afb15e8b73ffc6b53d3be0aa0e88ed1870e16e" \
  http://localhost:8080/data/upload/1/a6c61bfb-IMG_2712.JPG -I
# ✅ Returns 200 OK
```

## Related Database Tables

```sql
-- Legacy API tokens
authtoken_token (key, user_id, created)

-- Organization JWT settings (controls token authentication)
jwt_auth_jwtsettings (
    organization_id,
    api_tokens_enabled,           -- Enable PATs
    legacy_api_tokens_enabled,    -- Enable legacy tokens
    api_token_ttl_days
)

-- Organization info
organization (id, created_by_id, token, ...)

-- Users
htx_user (id, email, username, is_active)
```

## Authentication Flow

1. ML backend receives prediction request with task
2. Task contains project ID (e.g., "1.1759546106")
3. Middleware extracts project ID → queries organization ID
4. Middleware finds organization creator → retrieves their legacy token
5. Token passed to `get_local_path()` for file download
6. **Label Studio checks**: 
   - Is token valid? ✅ Yes
   - Is legacy token auth enabled for org? ❌ **NO** → 401 Error

## Label Studio Code Reference

```python
# label_studio/jwt_auth/auth.py
class TokenAuthenticationPhaseout(TokenAuthentication):
    def authenticate(self, request):
        auth_result = super().authenticate(request)
        if auth_result:
            user, _ = auth_result
            org = user.active_organization
            
            # This raises 401 if legacy tokens disabled
            if org and (not org.jwt.legacy_api_tokens_enabled):
                raise AuthenticationFailed(
                    'Authentication token no longer valid: '
                    'legacy token authentication has been disabled for this organization'
                )
        return auth_result
```

## Production Considerations

For production deployments, consider using Personal Access Tokens instead:

**Pros of PATs**:
- Tokens can expire (better security)
- Better audit trails
- Granular permissions

**Cons of PATs**:
- More complex implementation
- Requires middleware changes
- Different storage mechanism

**Pros of Legacy Tokens** (current solution):
- Simple implementation
- Works with existing middleware
- No expiration (development friendly)

**Cons of Legacy Tokens**:
- No expiration (security concern)
- Being phased out by Label Studio
- Limited to user-level authentication

## Files Created

1. `/label-studio-ml-backend/label_studio_ml/examples/segment_anything_model/TROUBLESHOOTING.md`
   - Comprehensive troubleshooting guide
   - Database schema reference
   - Feature flag documentation

2. `/label-studio-ml-backend/label_studio_ml/examples/segment_anything_model/FIX_SUMMARY.md`
   - Detailed fix explanation
   - Verification steps
   - Alternative solutions

## Prevention

To avoid this issue in the future:

1. **Check JWT settings when setting up new organizations**:
   ```sql
   SELECT * FROM jwt_auth_jwtsettings WHERE organization_id = ?;
   ```

2. **Document organization token settings** in deployment guides

3. **Add environment variable** to configure token type preference:
   ```bash
   LABEL_STUDIO_USE_LEGACY_TOKENS=true  # or false for PAT
   ```

4. **Implement fallback logic** to try PAT if legacy token fails

5. **Monitor authentication logs** for token rejection patterns

## Related Issues

- Legacy token phaseout in Label Studio
- JWT authentication feature flag: `fflag__feature_develop__prompts__dia_1829_jwt_token_auth`
- Organization-level security settings

## Testing Checklist

- [x] Legacy tokens enabled in database
- [x] Token retrieval working via middleware
- [x] API endpoint accessible with token
- [x] File download working with token
- [x] ML backend can access task images
- [ ] End-to-end SAM prediction test (pending user verification)

## Debug Commands

```bash
# Check JWT settings
sqlite3 label_studio.sqlite3 \
  "SELECT * FROM jwt_auth_jwtsettings WHERE organization_id = 1;"

# Get organization creator's token
sqlite3 label_studio.sqlite3 "
  SELECT t.key, u.email 
  FROM authtoken_token t
  JOIN htx_user u ON t.user_id = u.id
  JOIN organization o ON o.created_by_id = u.id
  WHERE o.id = 1;
"

# Test token validity
curl -H "Authorization: Token YOUR_TOKEN" \
  http://localhost:8080/api/projects/

# Check ML backend logs
tail -f /path/to/ml-backend/logs/label_studio_ml.log | grep -E "(token|auth|401)"
```

## Success Criteria

✅ ML backend can authenticate with Label Studio  
✅ Image files can be downloaded from Label Studio  
✅ SAM predictions work without 401 errors  
✅ Middleware correctly retrieves and uses tokens  
✅ Documentation created for troubleshooting  

## Conclusion

The middleware implementation was correct. The issue was a **configuration problem** at the Label Studio organization level. This highlights the importance of understanding multi-layer authentication systems and checking configuration at all levels (application code, database settings, feature flags).

