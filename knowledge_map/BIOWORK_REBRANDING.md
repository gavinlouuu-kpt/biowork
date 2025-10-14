# bioWork Rebranding Implementation Guide

## Overview

This document details the complete rebranding of Label Studio to bioWork. The rebranding focuses on user-facing elements while preserving all internal code structure and functionality.

## Table of Contents

1. [Rebranding Scope](#rebranding-scope)
2. [Completed Changes](#completed-changes)
3. [Assets Needed](#assets-needed)
4. [Testing Instructions](#testing-instructions)
5. [Technical Details](#technical-details)
6. [Future Maintenance](#future-maintenance)

---

## Rebranding Scope

### ✅ What Was Changed (User-Facing Only)

- **UI Text**: All visible text references to "Label Studio" changed to "bioWork"
- **Page Titles**: Browser tab titles show "bioWork"
- **Meta Tags**: HTML meta descriptions updated
- **Popup Notifications**: All tips and announcements use bioWork branding
- **Documentation**: README and help content updated
- **Package Metadata**: Description and author information

### ❌ What Was Preserved (Internal Structure)

- **Package Name**: `label-studio` (for backward compatibility)
- **Directory Structure**: All `label_studio/` paths maintained
- **Python Imports**: All import statements unchanged
- **API Endpoints**: All URLs and database references intact
- **CLI Commands**: `label-studio` command preserved
- **Configuration Keys**: All environment variables unchanged

---

## Completed Changes

### 1. Django Backend Templates

**Files Updated:**
- `label_studio/templates/base.html`
- `label_studio/users/templates/users/user_base.html`
- `label_studio/users/templates/users/new-ui/user_base.html`
- `label_studio/users/templates/users/new-ui/user_signup.html`

**Changes:**
- Meta author tags: `content="bioWork"`
- Page titles: `<title>bioWork</title>`
- Welcome messages: "Welcome to bioWork"
- Form labels: "How did you hear about bioWork?"

### 2. React Frontend Components

**Files Updated:**
- `web/apps/labelstudio/src/pages/Home/HomePage.tsx`
- `web/apps/labelstudio/src/pages/Organization/PeoplePage/InviteLink.tsx`
- `web/apps/labelstudio/src/pages/Organization/PeoplePage/PeoplePage.jsx`
- `web/apps/labelstudio/src/components/HeidiTips/content.ts`
- `web/apps/labelstudio/src/components/HeidiTips/liveContent.json`
- `web/apps/labelstudio/src/components/HeidiTips/utils.ts`

**Changes:**
- Version display: "bioWork Version: Community"
- Invitation text: "Invite people to join your bioWork instance"
- All popup tips: "Label Studio" → "bioWork"
- **Critical**: Disabled external GitHub fetch for tips

### 3. Configuration Files

**Files Updated:**
- `pyproject.toml`
- `README.md`

**Changes:**
- Package description: "bioWork annotation tool"
- Authors: "bioWork" organization
- README: Complete rebranding of all user-facing content
- Technical commands preserved (e.g., `pip install label-studio`)

### 4. Heidi Tips System (Critical Fix)

**Problem**: Popup notifications were fetching from Label Studio's GitHub endpoint, overriding local content.

**Solution**:
- Disabled external fetch in `utils.ts`
- Now uses only local `content.ts` with bioWork branding
- All tips updated to reference "bioWork Enterprise", "bioWork Starter Cloud", etc.

**Impact**: Users with cached tips need to clear browser cache to see changes.

---

## Assets Needed

You need to provide bioWork branding assets for these 11 locations:

### Logo Files (6 locations)
1. `web/apps/labelstudio/src/assets/images/logo.svg` - Main app logo
2. `label_studio/core/static/images/label_studio_logo.svg` - Backend logo
3. `label_studio/core/static/images/human_signal_logo.svg` - Company logo
4. `web/libs/editor/public/images/logo.png` - Editor logo
5. `web/libs/editor/public/images/ls_logo.png` - Editor logo variant
6. `web/libs/editor/images/logo.png` - Editor images logo

### Favicon Files (5 locations)
7. `web/apps/labelstudio/src/favicon.ico` - Main app (16x16, 32x32, 48x48, 64x64)
8. `label_studio/core/static/images/favicon.ico` - Backend static
9. `label_studio/core/static/images/favicon.png` - Backend PNG (180x180px)
10. `web/libs/editor/public/favicon.ico` - Editor favicon
11. `docs/themes/v2/source/images/favicon.ico` - Documentation favicon

### Specifications

**Logo Requirements:**
- SVG format preferred (scalable)
- Transparent background
- Work on light/dark backgrounds
- PNG variants: 200x50px, 400x100px (maintain aspect ratio)

**Favicon Requirements:**
- ICO file with multiple sizes: 16x16, 32x32, 48x48, 64x64
- PNG: 180x180px (iOS) or 512x512px (Android/PWA)

---

## Testing Instructions

### Pre-Deployment Verification

1. **Run Automated Verification**:
   ```bash
   python verify_rebranding.py
   ```
   This script checks all text changes and reports any issues.

2. **Build Frontend**:
   ```bash
   cd web
   yarn install
   yarn build
   ```

3. **Clear Browser Cache** ⚠️ **CRITICAL**:
   - Open DevTools (F12)
   - Application/Storage tab
   - Clear localStorage OR run in console:
     ```javascript
     localStorage.removeItem('heidi_live_tips_collection');
     localStorage.removeItem('heidi_live_tips_collection_fetched_at');
     ```
   - Hard refresh: Ctrl+Shift+R

3. **Verify Branding**:
   - [ ] Login page: "Welcome to bioWork"
   - [ ] Page titles: "bioWork" in browser tabs
   - [ ] Home page: "bioWork Version: Community"
   - [ ] Popup tips: Show "bioWork" (not "Label Studio")
   - [ ] Invitation modals: "bioWork instance"
   - [ ] Logos display (once replaced)
   - [ ] Favicons show (once replaced)

### Functional Testing

- [ ] Application starts: `label-studio` command works
- [ ] Package installs: `pip install label-studio`
- [ ] Database migrations: `python manage.py migrate`
- [ ] API endpoints respond
- [ ] User registration/login works
- [ ] Project creation works
- [ ] ML backend connections work

---

## Technical Details

### Heidi Tips System Architecture

**Before (Broken)**:
```
Frontend → /heidi-tips endpoint → GitHub raw file → Label Studio content
```

**After (Fixed)**:
```
Frontend → loadLiveTipsCollection() → defaultTipsCollection (bioWork content)
```

**Code Changes**:
- `utils.ts`: `loadLiveTipsCollection()` returns `defaultTipsCollection`
- External fetch code commented out with clear documentation
- All tip content updated in `content.ts`

### Cache Management

**Keys to Clear**:
- `heidi_live_tips_collection`
- `heidi_live_tips_collection_fetched_at`
- Cache stale time: 1 hour (3600000ms)

**Why Cache Clearing Required**:
- Old tips cached from GitHub persist until cleared
- Users may see "Label Studio" references until cache expires or is manually cleared

### Re-enabling External Fetch (Future)

When bioWork has its own tips endpoint:

1. Uncomment code in `utils.ts`
2. Update fetch URL: `/heidi-tips` → your bioWork endpoint
3. Ensure endpoint returns JSON matching `content.ts` format
4. Test thoroughly before deploying

---

## Future Maintenance

### Adding New Tips

**Location**: `web/apps/labelstudio/src/components/HeidiTips/content.ts`

**Format**:
```typescript
{
  title: "Your Tip Title",
  content: "Content mentioning bioWork...",
  closable: true,
  link: {
    label: "Learn more",
    url: "https://your-biowork-docs.com/...",
    params: {
      experiment: "your_experiment",
      treatment: "your_treatment"
    }
  }
}
```

### Updating External URLs

When bioWork has its own:
- Documentation site
- API documentation
- Community/Slack
- Company website

Update these files:
- `web/apps/labelstudio/src/pages/Home/HomePage.tsx`
- `README.md`
- Tip URLs in `content.ts`

### Version Management

- Keep package name as `label-studio` for backward compatibility
- Update version numbers in `pyproject.toml` as needed
- Consider bioWork-specific version scheme if desired

---

## Files Modified

### Core Application Files
- `label_studio/templates/base.html`
- `label_studio/users/templates/users/user_base.html`
- `label_studio/users/templates/users/new-ui/user_base.html`
- `label_studio/users/templates/users/new-ui/user_signup.html`
- `pyproject.toml`
- `README.md`

### Frontend Files
- `web/apps/labelstudio/src/pages/Home/HomePage.tsx`
- `web/apps/labelstudio/src/pages/Organization/PeoplePage/InviteLink.tsx`
- `web/apps/labelstudio/src/pages/Organization/PeoplePage/PeoplePage.jsx`
- `web/apps/labelstudio/src/components/HeidiTips/content.ts`
- `web/apps/labelstudio/src/components/HeidiTips/liveContent.json`
- `web/apps/labelstudio/src/components/HeidiTips/utils.ts`

### Verification Tools
- `verify_rebranding.py` - Automated verification script

---

## Support

### Common Issues

**Still seeing "Label Studio" in tips?**
- Clear browser localStorage (see testing instructions)
- Hard refresh the page

**Logos not displaying?**
- Check file formats and paths
- Verify files are in correct locations
- Clear browser cache

**Application not starting?**
- Verify no code imports were broken
- Check Python environment
- Ensure `label-studio` command works

### Rollback Plan

If issues occur:
1. All changes are text-only (except tips fetch disable)
2. Revert `utils.ts` to re-enable external fetch
3. Restore original content files
4. Rebuild frontend

### Contact

For questions about this rebranding:
- Check this document first
- Verify testing steps were followed
- Check browser cache was cleared
- Confirm asset files are in place

---

## Status Summary

✅ **Text Rebranding**: Complete
✅ **Popup Notifications**: Fixed (external fetch disabled)
✅ **Configuration**: Updated
✅ **Documentation**: Complete
⏳ **Assets**: Waiting for bioWork logo/favicon files
⏳ **Testing**: Ready for verification
⏳ **Deployment**: Ready when assets provided

**Next Steps**:
1. Provide bioWork logo and favicon assets
2. Place assets in specified locations (11 files)
3. Build and test application
4. Deploy to production
5. Clear user browser caches (important!)

---

*Document Version: 1.0*
*Last Updated: [Current Date]*
*Status: Implementation Complete, Assets Pending*
