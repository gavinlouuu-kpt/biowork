---
title: VectorLabels
type: tags
hide_menu: true
order: 433
meta_title: Vector Label Tag for Labeling Vectors in Images
meta_description: Use the VectorLabels tag and label vectors in images for semantic segmentation machine learning and data science projects.
---

The `VectorLabels` tag is used to create labeled vectors. 

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

## Usage Examples

### Basic Vector Path

```html
<View>
 <Image name="image" value="$image" />
 <VectorLabels name="labels" toName="image">
   <Label value="Road" />
   <Label value="Boundary" />
 </VectorLabels>
</View>
```

### Polygon with Bezier Support

```html
<View>
 <Image name="image" value="$image" />
 <VectorLabels
   name="polygons"
   toName="image"
   closable="true"
   curves="true"
   minPoints="3"
   maxPoints="20"
 >
   <Label value="Building" />
   <Label value="Park" />
 </VectorLabels>
</View>
```

### Skeleton Mode for Branching Paths

```html
<View>
 <Image name="image" value="$image" />
 <VectorLabels
   name="skeleton"
   toName="image"
   skeleton="true"
   closable="false"
   curves="true"
 >
   <Label value="Tree" />
   <Label value="Branch" />
 </VectorLabels>
</View>
```


### Keypoint Annotation Tool

```html
<View>
 <Image name="image" value="$image" />
 <VectorLabels
   name="keypoints"
   toName="image"
   closable="false"
   curves="false"
   minPoints="1"
   maxPoints="1"
 >
   <Label value="Eye" />
   <Label value="Nose" />
   <Label value="Mouth" />
 </VectorLabels>
</View>
```

### Constrained Drawing

```html
<View>
 <Image name="image" value="$image" />
 <VectorLabels
   name="constrained"
   toName="image"
   closable="true"
   curves="true"
   constraintoBounds="true"
   snap="pixel"
   minPoints="4"
   maxPoints="12"
 >
   <Label value="Region" />
 </VectorLabels>
</View>
```

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

{% insertmd includes/tags/vectorlabels.md %}


### Result parameters

**Kind**: global typedef  
**Returns**: <code>VectorRegionResult</code> - The serialized vector region data in Label Studio format  
**Properties**

| Name | Type | Description |
| --- | --- | --- |
| original_width | <code>number</code> | width of the original image (px) |
| original_height | <code>number</code> | height of the original image (px) |
| image_rotation | <code>number</code> | rotation degree of the image (deg) |
| value | <code>Object</code> |  |
| value.vertices | <code>Array.&lt;Object&gt;</code> | array of point objects with coordinates, bezier curve information, and point relationships |
| value.closed | <code>boolean</code> | whether the vector is closed (polygon) or open (polyline) |
| value.vectorlabels | <code>Array.&lt;string&gt;</code> | array of label names assigned to this vector |

#### Example results JSON export

```json
{
  "original_width": 1920,
  "original_height": 1280,
  "image_rotation": 0,
  "value": {
    "vertices": [
      { "id": "point-1", "x": 25.0, "y": 30.0, "prevPointId": null, "isBezier": false },
      { "id": "point-2", "x": 75.0, "y": 70.0, "prevPointId": "point-1", "isBezier": true,
        "controlPoint1": {"x": 50.0, "y": 40.0}, "controlPoint2": {"x": 60.0, "y": 60.0} }
    ],
    "closed": false,
    "vectorlabels": ["Road"]
  }
}
```