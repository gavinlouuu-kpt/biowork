---
title: Vector
type: tags
hide_menu: true
order: 430
meta_title: Vector Tag for Adding Vectors to Images
meta_description: Use the Vector tag by adding vectors to images for segmentation machine learning and data science projects.
---

The `Vector` tag is used to add vectors to an image without selecting a label. This can be useful when you have only one label to assign to the vector. 

Use with the following data types: image.

## Key Features

### Point Management
- **Add Points**: Click on empty space, Shift+click on path segments  
- **Edit Points**: Drag to reposition, Shift+click to convert regular ↔ bezier  
- **Delete Points**: Alt+click on existing points  
- **Multi-Selection**: Select multiple points for batch transformations  
- **Break Closed Path**: Alt+click on any segment of a closed path to break it at that specific segment  

### Bezier Curves
- **Create**: Drag while adding points or convert existing points  
- **Edit**: Drag control points, disconnect/reconnect control handles  
- **Control**: `curves` prop to enable/disable bezier functionality  

## Keyboard Shortcuts & Hotkeys

### Point Creation & Editing
- **Click**: Add new point in drawing mode  
- **Shift + Click** on a segment: Add point on path segment (insert between existing points)  
- **Shift + Drag**: Create bezier point with control handles  
- **Shift + Click** on a point: Convert point between regular ↔ bezier  
- **Alt + Click** on a segment: Break closed path at segment (when path is closed)  

### Point Selection
- **Click**: Select single point  
- **Cmd/Ctrl + Click**: Add point to multi-selection  
- **Cmd/Ctrl + Click on shape**: Select all points in the path  
- **Cmd/Ctrl + Click on point**: Toggle point selection in multi-selection  

### Path Management
- **Click on first/last point**: Close path bidirectionally (first→last or last→first)  
- **Shift + Click**: Add point on path segment without closing  
- **Esc** or **Click**: Exit the vector by pressing **Esc** or by clicking on the point that you added last

### Bezier Curve Control
- **Drag control points**: Adjust curve shape  
- **Alt + Drag control point**: Disconnect control handles (make asymmetric)  
- **Shift + Drag**: Create new bezier point with control handles  

### Multi-Selection & Transformation
- **Select multiple points**: Use Cmd/Ctrl + Click to build selection  
- **Transform selection**: Use transformer handles for rotation, scaling, and translation  
- **Clear selection**: Click on any point  

## Advanced Features

### Path Breaking

When a path is closed, you can break it at any segment:
* Alt + Click on any segment of a closed path
* The path breaks at that segment
* The breaking point becomes the first element
* The point before breaking becomes active

### Skeleton Mode
* **Purpose:** Create branching paths instead of linear sequences
* **Behavior:** New points connect to the active point, not the last added point
* **Use Case:** Tree structures, network diagrams, anatomical features

### Bezier Curve Management
* **Symmetric Control:** By default, control points move symmetrically
* **Asymmetric Control:** Hold Alt while dragging to disconnect handles
* **Control Point Visibility:** Control points are shown when editing bezier points

### Multi-Selection Workflow
1.	**Build Selection:** Use Cmd/Ctrl + Click to add points
2.	**Transform:** Use transformer handles for rotation, scaling, translation
3.	**Batch Operations:** Apply transformations to all selected points
4.	**Clear:** Click outside or use programmatic methods

## Tag parameters

{% insertmd includes/tags/vector.md %}

## Example

Basic labeling configuration for vector image segmentation

```html
<View>
    <Vector name="line-1" toName="img-1" />
    <Image name="img-1" value="$img" />
</View>
```

