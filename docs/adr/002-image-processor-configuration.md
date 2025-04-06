# ADR 002: Image Processor Configuration

## Status
Accepted

## Context
The system needs to preprocess invoice images before they are passed to various model implementations. Analysis of the existing images shows they are already fairly standardized (all JPG format, RGB mode, similar dimensions around 3000x4000 pixels). We need to define a configuration structure that maintains quality while optimizing for model processing.

## Decision
We will implement an `ImageProcessorConfig` class with the following structure and default values:

```python
@dataclass
class ImageProcessorConfig:
    target_size: Tuple[int, int] = (1024, 1365)  # Maintains ~3:4 aspect ratio
    color_mode: ColorMode = ColorMode.RGB
    normalize: bool = True
    maintain_aspect_ratio: bool = True
    jpeg_quality: int = 95
    contrast_factor: Optional[float] = None
    brightness_factor: Optional[float] = None
    sharpness_factor: Optional[float] = None
```

Key configuration decisions:
1. Target size reduced to 1024x1365 while maintaining aspect ratio
2. Default to RGB color mode (matching source images)
3. Normalize pixel values to [0,1] range by default
4. Maintain aspect ratio during resizing
5. High JPEG quality (95) to preserve details
6. Optional image enhancement parameters (disabled by default)

## Consequences

### Positive
1. Standardized image sizes reduce memory usage and processing time
2. Maintained aspect ratio prevents image distortion
3. Normalized pixel values improve model processing
4. Optional enhancement parameters provide flexibility
5. Configuration validates all numerical parameters
6. High JPEG quality preserves important details

### Negative
1. Reduced image resolution may impact very fine details
2. Memory usage during processing of original high-res images
3. Additional processing time for normalization

## Implementation Notes
1. All numerical parameters have validation in `__post_init__`
2. Enhancement parameters restricted to safe ranges (0.0-2.0)
3. JPEG quality restricted to 0-100 range
4. Clear error messages for invalid configurations

## Related Documents
- Interface Control Document
- Project Directory Structure
- Core Architectural Principles 