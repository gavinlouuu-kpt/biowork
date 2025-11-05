# Disable Heidi Tips via Feature Flag

- Flag name: `fflag_feat_front_hide_heidi_tips_short`
- Purpose: Hide Heidi mascot tips across all UI surfaces (React HeidiTips, legacy auth page tips, backend /heidi-tips).

## How to enable (disable Heidi tips)

Set environment variable (any of these prefixes work):

```bash
# recommended
export fflag_feat_front_hide_heidi_tips_short=true

# also accepted by backend loader
export FF_FFLAG_FEAT_FRONT_HIDE_HEIDI_TIPS_SHORT=true
export FFLAG_FEAT_FRONT_HIDE_HEIDI_TIPS_SHORT=true
export FEAT_FEFLAG_FEAT_FRONT_HIDE_HEIDI_TIPS_SHORT=true
```

Notes:
- Backend: `core.feature_flags.flag_set()` reads env first; Django templates receive `feature_flags` including env overrides; React reads `window.APP_SETTINGS.feature_flags`.
- React: Component `web/apps/labelstudio/src/components/HeidiTips/HeidiTips.tsx` returns `null` when the flag is active.
- Auth pages: `label_studio/users/templates/users/new-ui/user_base.html` includes login/signup tips only if the flag is NOT set.
- Backend endpoint: `label_studio/core/views.py::heidi_tips` returns 404 when the flag is active.

## Rollback

Unset the variable or set to `false` and restart services. No code removal necessary.
