# Toolbar Auto-Annotation Toggle Implementation

## Overview
Modified the toolbar behavior to replace non-interactive tools with interactive (smart) tools when auto-annotation is turned on, instead of showing both simultaneously.

## Implementation Date
October 5, 2025

## Modified Files
- `/Users/reading/Developer/label-studio-custom/web/libs/editor/src/components/Toolbar/Toolbar.jsx`
- `/Users/reading/Developer/label-studio-custom/web/libs/editor/src/tools/Base.jsx`

## Changes Made

### Previous Behavior
- Regular tools (Brush, Polygon, etc.) were ALWAYS visible in the toolbar
- Smart/interactive tools (KeyPoint, Rectangle with ML) were ADDED when auto-annotation was enabled
- Both tool types appeared simultaneously when auto-annotation was ON
- Regular versions of smart tools (KeyPoint, Rectangle) were hidden when auto-annotation was OFF

### New Behavior
- **Auto-annotation OFF**: Shows ALL regular tool versions (Brush, Polygon, KeyPoint, Rectangle, etc.) for manual annotation
- **Auto-annotation ON**: Shows ONLY smart/interactive tool versions that trigger ML predictions
- Tools are mutually exclusive based on the auto-annotation toggle state
- Regular versions of smart tools now properly display when auto-annotation is OFF

### Code Changes

#### Change 1: Toolbar Component

**File**: `web/libs/editor/src/components/Toolbar/Toolbar.jsx`  
**Lines**: 46-72

Changed from:
```jsx
return (
  <ToolbarProvider value={{ expanded, alignment }}>
    <Block ref={(el) => setToolbar(el)} name="toolbar" mod={{ alignment, expanded }}>
      {Object.entries(toolGroups).map(([name, tools], i) => {
        // Always renders regular tools
      })}
      {store.autoAnnotation && <SmartTools tools={smartTools} />}
    </Block>
  </ToolbarProvider>
);
```

To:
```jsx
return (
  <ToolbarProvider value={{ expanded, alignment }}>
    <Block ref={(el) => setToolbar(el)} name="toolbar" mod={{ alignment, expanded }}>
      {store.autoAnnotation ? (
        // When auto-annotation is ON, show only smart/interactive tools
        smartTools.length > 0 && <SmartTools tools={smartTools} />
      ) : (
        // When auto-annotation is OFF, show regular tools
        Object.entries(toolGroups).map(([name, tools], i) => {
          // Renders regular tools
        })
      )}
    </Block>
  </ToolbarProvider>
);
```

#### Change 2: Tool Rendering Logic

**File**: `web/libs/editor/src/tools/Base.jsx`  
**Lines**: 51-58

Changed from:
```jsx
get shouldRenderView() {
  return (self.isSeparated || self.smartEnabled) && self.iconClass;
}
```

To:
```jsx
get shouldRenderView() {
  // Regular tools (non-dynamic) should always render if they have an icon
  // Smart tools (dynamic) should only render when smartEnabled
  if (!self.dynamic) {
    return (self.isSeparated || self.iconClass);
  }
  return (self.isSeparated || self.smartEnabled) && self.iconClass;
}
```

**Why this change was needed**: 
The original logic prevented regular versions of smart tools (like KeyPoint and Rectangle) from rendering when auto-annotation was OFF, because `smartEnabled` would be false. Now regular tools (`dynamic: false`) always render if they have an icon, regardless of the auto-annotation state.

## How It Works

### Tool Classification
1. **Regular Tools** (`dynamic: false`):
   - Standard annotation tools for manual use
   - Includes: Brush, Polygon, and regular versions of KeyPoint, Rectangle
   - Used for manual annotation without ML assistance
   - Visible when `store.autoAnnotation === false`
   - Now properly render regardless of auto-annotation state

2. **Smart Tools** (`dynamic: true`):
   - ML-powered interactive tools created from tags with `smart="true"`
   - Includes: Smart versions of KeyPointLabels, RectangleLabels
   - Trigger backend predictions from SAM model
   - Visible when `store.autoAnnotation === true`
   - Only render when `smartEnabled` is true

### Tool Creation Process
When a control tag in the XML config has `smart="true"`:
1. The base tool creates TWO versions (see `Base.jsx` lines 72-91)
2. **Regular version** (`dynamic: false`): For manual annotation, always visible when auto-annotation is OFF
3. **Smart version** (`dynamic: true`): Created via `makeDynamic()`, for ML-powered use, only visible when auto-annotation is ON

This means KeyPointLabels and RectangleLabels with `smart="true"` create:
- A regular KeyPoint/Rectangle tool for manual clicking/drawing
- A smart KeyPoint/Rectangle tool that sends data to the ML backend

### XML Configuration
Example from `sam_poly_label_interf.xml`:
```xml
<!-- Smart/Interactive Tools -->
<KeyPointLabels name="tag3" toName="image" smart="true">
  <Label value="Object" smart="true" background="#0000FF"/>
</KeyPointLabels>

<RectangleLabels name="tag4" toName="image" smart="true">
  <Label value="Object" smart="true" background="#0000FF"/>
</RectangleLabels>

<!-- Regular Result Tools -->
<BrushLabels name="tag1" toName="image">
  <Label value="Object" background="#FF0000"/>
</BrushLabels>

<PolygonLabels name="tag2" toName="image">
  <Label value="Object" background="#00FF00"/>
</PolygonLabels>
```

## User Experience

### Workflow
1. User opens a task in Label Studio
2. By default, auto-annotation is OFF - ALL regular tools are shown:
   - Brush (for manual painting)
   - Polygon (for manual polygon drawing)
   - KeyPoint (for manual point placement)
   - Rectangle (for manual rectangle drawing)
3. User toggles "Auto-Annotation" ON via the toggle in the bottom bar
4. Toolbar instantly switches to show ONLY smart/interactive tools:
   - Smart KeyPoint (triggers SAM with point prompts)
   - Smart Rectangle (triggers SAM with box prompts)
5. User can use these smart tools to trigger SAM predictions from the ML backend
6. Toggling auto-annotation OFF returns to showing ALL regular tools

### Benefits
- **Cleaner UI**: Only relevant tools shown at any time
- **Clear mode distinction**: Visual indication of manual vs ML-assisted mode
- **Reduced confusion**: Users don't see duplicate or conflicting tools
- **Better UX**: Focused toolset for each annotation mode
- **Complete toolset**: All regular tools (including KeyPoint and Rectangle) are available for manual annotation when auto-annotation is OFF

## Related Components

### Auto-Annotation Toggle
- **Component**: `DynamicPreannotationsToggle.jsx`
- **Location**: Bottom bar of the annotation interface
- **Controls**: `store.autoAnnotation` state
- **Interface**: Requires `auto-annotation` interface to be enabled

### Tool Manager
- **File**: `tools/Manager.js`
- **Purpose**: Manages tool registration and selection
- **Key method**: `addTool()` - registers both regular and smart versions

### Base Tool
- **File**: `tools/Base.jsx`
- **Key property**: `dynamic` (boolean)
- **Key method**: `makeDynamic()` - marks tool as smart/interactive
- **Key view**: `smartEnabled` - determines if tool should be treated as smart

## Testing Checklist

- [ ] Verify regular tools appear when auto-annotation is OFF
- [ ] Verify smart tools appear when auto-annotation is ON
- [ ] Verify tools switch immediately when toggling auto-annotation
- [ ] Verify smart tools trigger ML backend predictions
- [ ] Verify no tools appear simultaneously from both groups
- [ ] Test with different XML configurations
- [ ] Test with projects that have only regular tools
- [ ] Test with projects that have only smart tools
- [ ] Test with projects that have both tool types

## Dependencies

### Frontend
- MobX state management (`store.autoAnnotation`)
- React hooks (useState, useMemo)
- Label Studio editor components

### Backend
- SAM ML backend must be configured and running
- ML backend must support smart tool predictions
- Proper middleware for handling smart tool requests

## Notes

- The change is purely UI-based - no backend modifications needed
- Existing annotations are not affected
- Tool shortcuts remain functional in both modes
- The SmartTools component groups multiple smart tools into a single "Auto-Detect" button with a dropdown
