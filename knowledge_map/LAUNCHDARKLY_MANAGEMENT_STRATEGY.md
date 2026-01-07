# LaunchDarkly Management Strategy

## Executive Summary

This document outlines the investigation findings and recommended strategy for managing LaunchDarkly feature flags inherited from the open source Label Studio project. The codebase includes LaunchDarkly SDK integration but is designed to work in multiple modes, allowing flexibility in how feature flags are managed.

## Current State Analysis

### Implementation Overview

The LaunchDarkly integration is implemented in `label_studio/core/feature_flags/base.py` and supports three operational modes:

1. **File-based mode** (`FEATURE_FLAGS_FROM_FILE=true`)
   - Reads flags from a YAML/JSON file
   - No LaunchDarkly account required
   - Useful for local development and on-premise deployments

2. **Offline mode** (`FEATURE_FLAGS_OFFLINE=true`, default)
   - Uses LaunchDarkly SDK in offline mode
   - No API calls to LaunchDarkly servers
   - Default value for all flags is `False` (base settings) or `True` (Community edition)
   - No LaunchDarkly account required

3. **Production mode** (`FEATURE_FLAGS_OFFLINE=false`)
   - Requires `FEATURE_FLAGS_API_KEY` environment variable
   - Connects to LaunchDarkly API
   - Supports Redis caching for performance
   - Requires a LaunchDarkly account

### Key Findings

#### 1. Hardcoded LaunchDarkly URLs in Frontend Code

**Issue**: Multiple frontend files contain hardcoded references to the open source project's LaunchDarkly dashboard:
- `web/libs/editor/src/utils/feature-flags.ts` - Contains 20+ links to `app.launchdarkly.com/default/production/features/...`
- `web/libs/frontend-test/src/feature-flags.ts` - Contains 8+ links
- `web/libs/datamanager/src/utils/feature-flags.js` - Contains 5+ links

**Impact**: These links point to the HumanSignal/Label Studio LaunchDarkly account, which you likely don't have access to.

**Example**:
```typescript
/**
 * @link https://app.launchdarkly.com/default/production/features/fflag_fix_front_dev_1284_auto_detect_undo_281022_short
 */
export const FF_DEV_1284 = "fflag_fix_front_dev_1284_auto_detect_undo_281022_short";
```

#### 2. Stale Feature Flags System

The codebase includes a `stale_feature_flags.py` file that maintains a dictionary of deprecated flags with their final values. This is an intermediary step before removing flag references entirely.

**Location**: `label_studio/core/feature_flags/stale_feature_flags.py`

**Purpose**: Prevents deprecated flags from being changed while code cleanup is in progress.

#### 3. Environment Variable Override Support

The system supports overriding any feature flag via environment variables with prefixes:
- `ff_*`
- `fflag_*`
- `fflag-*`
- `feat_*`

This allows local control without LaunchDarkly account access.

#### 4. Default Configuration

- **Base settings** (`label_studio/core/settings/base.py`):
  - `FEATURE_FLAGS_OFFLINE = True` (default)
  - `FEATURE_FLAGS_DEFAULT_VALUE = False`
  - `FEATURE_FLAGS_API_KEY = 'any key'` (default, not validated in offline mode)

- **Community edition** (`label_studio/core/settings/label_studio.py`):
  - `FEATURE_FLAGS_DEFAULT_VALUE = True` (all flags on by default)
  - `FEATURE_FLAGS_FROM_FILE = True` (attempts to load from file)

### Current Usage Patterns

#### Backend Usage
Feature flags are used throughout the codebase:
- `label_studio/data_manager/managers.py` - 2 usages
- `label_studio/data_import/api.py` - 1 usage
- `label_studio/core/views.py` - 2 usages
- `label_studio/data_export/models.py` - 1 usage
- `label_studio/data_export/api.py` - 3 usages
- `label_studio/users/views.py` - 4 usages

#### Frontend Usage
Feature flags are bootstrapped via `window.APP_SETTINGS.feature_flags` and used throughout React components.

## Recommended Management Strategy

### Option 1: Continue Using LaunchDarkly (Recommended for Production)

**When to use**: If you need dynamic feature flag management, A/B testing, or user targeting in production.

**Requirements**:
1. Create your own LaunchDarkly account
2. Set `FEATURE_FLAGS_API_KEY` environment variable with your SDK key
3. Set `FEATURE_FLAGS_OFFLINE=false` for production
4. Recreate necessary feature flags in your LaunchDarkly project
5. Update frontend documentation links (optional, for developer convenience)

**Benefits**:
- Full feature flag management capabilities
- User targeting and segmentation
- A/B testing support
- Real-time flag updates without code deployment
- Analytics and insights

**Configuration**:
```bash
# Production environment
FEATURE_FLAGS_API_KEY=your-sdk-key-here
FEATURE_FLAGS_OFFLINE=false
```

**Redis Integration**: If using Redis, the system automatically uses it for caching:
```python
# Automatically configured if REDIS_LOCATION is set
# Uses 'feature-flags' prefix with 30-second cache expiration
```

### Option 2: File-Based Management (Recommended for Development/On-Premise)

**When to use**: For local development, testing, or on-premise deployments where you don't need dynamic flag management.

**Requirements**:
1. Create a `feature_flags.json` or `feature_flags.yml` file
2. Set `FEATURE_FLAGS_FROM_FILE=true`
3. Set `FEATURE_FLAGS_FILE=path/to/your/flags.yml`

**Benefits**:
- No external service dependency
- Version controlled flags
- Simple to manage
- No API costs

**Configuration**:
```bash
FEATURE_FLAGS_FROM_FILE=true
FEATURE_FLAGS_FILE=feature_flags.yml
```

**Example file format** (`feature_flags.yml`):
```yaml
flagValues:
  fflag_fix_front_dev_1284_auto_detect_undo_281022_short: true
  ff_front_dev_2715_audio_3_280722_short: true
  fflag_feat_optic_2123_audio_spectrograms: false
```

### Option 3: Environment Variable Override (Recommended for Simple Cases)

**When to use**: For quick testing or when you only need to toggle a few flags.

**Benefits**:
- No configuration files needed
- Quick to set up
- Works with any mode

**Configuration**:
```bash
# Override specific flags
fflag_fix_front_dev_1284_auto_detect_undo_281022_short=true
ff_front_dev_2715_audio_3_280722_short=false
```

### Option 4: Offline Mode with Defaults (Current Default)

**When to use**: When you don't need feature flags at all or want all flags to use default values.

**Current behavior**:
- Base settings: All flags default to `False`
- Community edition: All flags default to `True`
- No external dependencies
- No API calls

**Configuration**:
```bash
FEATURE_FLAGS_OFFLINE=true  # This is the default
FEATURE_FLAGS_DEFAULT_VALUE=false  # or true for Community edition
```

## Action Items

### Immediate Actions

1. **Document Current Flag Usage**
   - Audit all feature flags currently in use
   - Identify which flags are critical vs. optional
   - Document flag purposes and dependencies

2. **Clean Up Frontend Documentation Links**
   - Remove or update hardcoded LaunchDarkly dashboard URLs in frontend code
   - Replace with internal documentation or remove if not needed
   - Files to update:
     - `web/libs/editor/src/utils/feature-flags.ts`
     - `web/libs/frontend-test/src/feature-flags.ts`
     - `web/libs/datamanager/src/utils/feature-flags.js`

3. **Decide on Management Strategy**
   - Choose one of the four options above based on your needs
   - Document the decision and rationale

### Short-Term Actions

4. **Create Feature Flag Inventory**
   - List all flags currently referenced in code
   - Categorize by purpose (bug fix, feature, experiment, etc.)
   - Identify flags that can be removed (always on/off)

5. **Set Up Flag Management**
   - If using LaunchDarkly: Create account and configure
   - If using file-based: Create initial flags file
   - If using env vars: Document required variables

6. **Update Environment Configuration**
   - Add LaunchDarkly configuration to `.env.example`
   - Document in deployment guides
   - Set appropriate defaults for each environment

### Long-Term Actions

7. **Flag Lifecycle Management**
   - Establish process for flag creation, deprecation, and removal
   - Regularly review `stale_feature_flags.py` for cleanup opportunities
   - Remove flags that are permanently enabled/disabled

8. **Monitoring and Alerting**
   - If using LaunchDarkly: Set up monitoring for API health
   - Track flag usage and impact
   - Alert on flag evaluation failures

9. **Documentation**
   - Create developer guide for adding new flags
   - Document flag naming conventions
   - Maintain flag registry/runbook

## Flag Naming Convention

The codebase follows this naming pattern (inherited from open source):

```
fflag_<back|front|all>_<issue_id>_short_description_<date>_<short|long>
```

- `back`: Backend-only flag
- `front`: Frontend-only flag
- `all`: Both backend and frontend
- `short`: Short-term flag (temporary)
- `long`: Permanent flag or killswitch

**Best Practice**: Use `short` for temporary flags that will be removed, `long` for permanent feature toggles.

## Migration Considerations

### If Migrating Away from LaunchDarkly

If you decide to remove LaunchDarkly dependency entirely:

1. **Phase 1: Identify All Flags**
   - Search codebase for all `flag_set()` calls
   - Document current flag states
   - Determine final desired state for each flag

2. **Phase 2: Replace with Simple Implementation**
   - Create a simple feature flag module that reads from environment/config
   - Maintain same API (`flag_set()`, `all_flags()`) for compatibility
   - Gradually migrate flags to permanent code paths

3. **Phase 3: Remove LaunchDarkly SDK**
   - Remove `launchdarkly-server-sdk` from `pyproject.toml`
   - Remove LaunchDarkly-specific code
   - Update documentation

### If Keeping LaunchDarkly

1. **Set Up Your Account**
   - Create LaunchDarkly project
   - Generate SDK keys for each environment
   - Configure user targeting if needed

2. **Recreate Critical Flags**
   - Import flag definitions from codebase
   - Set appropriate default values
   - Configure targeting rules if needed

3. **Update Configuration**
   - Set `FEATURE_FLAGS_API_KEY` in production
   - Set `FEATURE_FLAGS_OFFLINE=false` for production
   - Configure Redis caching if available

## Security Considerations

1. **API Key Management**
   - Store `FEATURE_FLAGS_API_KEY` securely (environment variables, secrets manager)
   - Use different keys for dev/staging/production
   - Rotate keys periodically

2. **User Data Privacy**
   - Review `get_user_repr()` function in `label_studio/core/feature_flags/utils.py`
   - Ensure only necessary user data is sent to LaunchDarkly
   - Consider GDPR/privacy implications

3. **Offline Mode Security**
   - In offline mode, flags use default values
   - Ensure defaults are secure (fail-safe defaults)

## Cost Considerations

- **LaunchDarkly**: Pricing based on monthly active users (MAU)
- **File-based/Offline**: No additional costs
- **Environment variables**: No additional costs

## Recommendations Summary

1. **For Development**: Use file-based or environment variable overrides
2. **For Production (if needed)**: Set up your own LaunchDarkly account
3. **For On-Premise**: Use file-based or offline mode
4. **Clean Up**: Remove hardcoded LaunchDarkly dashboard URLs from frontend code
5. **Document**: Create internal documentation for flag management process

## Related Files

- `label_studio/core/feature_flags/base.py` - Main implementation
- `label_studio/core/feature_flags/utils.py` - User representation
- `label_studio/core/feature_flags/stale_feature_flags.py` - Deprecated flags
- `label_studio/core/feature_flags/README.md` - Original documentation
- `label_studio/core/settings/base.py` - Base configuration
- `label_studio/core/settings/label_studio.py` - Community edition overrides
- `pyproject.toml` - Dependencies (line 67: `launchdarkly-server-sdk (==8.2.1)`)

## Questions to Answer

1. Do you need dynamic feature flag management in production?
2. Do you have access to the original LaunchDarkly account?
3. What is your deployment model (cloud, on-premise, hybrid)?
4. How many users/environments need flag management?
5. What is your budget for feature flag services?

Answering these questions will help determine the best management strategy for your use case.
