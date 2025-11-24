# AD-Census Python Wrapper

Python wrapper for the AD-Census stereo matching algorithm. This package allows you to compute disparity maps from stereo image pairs using a simple Python interface.

## Features

- Easy-to-use Python API
- Takes two images (left and right stereo pair) as input
- Outputs disparity map as PNG image
- Optimized C++ implementation with Python bindings
- Compatible with Raspberry Pi

## Requirements

### System Requirements

- Python 3.6 or higher
- CMake 3.12 or higher
- C++ compiler with C++11 support
- OpenCV 4.x or higher

### Raspberry Pi Requirements

For Raspberry Pi, you'll need:
```bash
sudo apt-get update
sudo apt-get install -y \
    python3-dev \
    python3-pip \
    cmake \
    build-essential \
    libopencv-dev \
    python3-opencv
```

## Installation

### Option 1: Install from source (Recommended)

1. Clone or navigate to the repository:
```bash
cd /path/to/AD-Census
```

2. Install Python dependencies:
```bash
pip3 install -r requirements.txt
```

3. Build and install the package:
```bash
pip3 install .
```

### Option 2: Development installation

For development, use editable mode:
```bash
pip3 install -e .
```

## Usage

### Basic Example

```python
import adcensus
import cv2

# Option 1: Using file paths
disparity = adcensus.compute_disparity(
    'left.png',
    'right.png',
    min_disparity=0,
    max_disparity=64
)

# Save disparity map
adcensus.save_disparity(disparity, 'output')

# Option 2: Using numpy arrays
import numpy as np

left_img = cv2.imread('left.png')
right_img = cv2.imread('right.png')

disparity = adcensus.compute_disparity(left_img, right_img)
adcensus.save_disparity(disparity, 'output')
```

### Advanced Usage with Custom Parameters

```python
from adcensus import ADCensusStereo

# Create stereo matcher with custom parameters
stereo = ADCensusStereo(
    min_disparity=0,
    max_disparity=128,
    lambda_ad=10,
    lambda_census=30,
    do_lr_check=True,
    do_filling=True
)

# Compute disparity
disparity = stereo.compute('left.png', 'right.png')

# Save result
import cv2
cv2.imwrite('disparity.png', disparity)
```

### Complete Example Script

See `examples/example_usage.py` for a complete working example.

## API Reference

### `compute_disparity(left_image, right_image, **kwargs)`

Convenience function to compute disparity map.

**Parameters:**
- `left_image`: Left image as file path (str) or numpy array
- `right_image`: Right image as file path (str) or numpy array
- `min_disparity`: Minimum disparity value (default: 0)
- `max_disparity`: Maximum disparity value (default: 64)
- Additional keyword arguments for algorithm parameters

**Returns:**
- Disparity map as numpy array (float32)

### `save_disparity(disparity, output_path, colormap=True)`

Save disparity map to file.

**Parameters:**
- `disparity`: Disparity map as numpy array
- `output_path`: Output file path (without extension)
- `colormap`: If True, also save colorized version (default: True)

### `ADCensusStereo` Class

Main class for stereo matching.

**Constructor Parameters:**
- `min_disparity` (int): Minimum disparity value (default: 0)
- `max_disparity` (int): Maximum disparity value (default: 64)
- `lambda_ad` (int): AD cost parameter (default: 10)
- `lambda_census` (int): Census cost parameter (default: 30)
- `cross_L1` (int): Cross window spatial parameter L1 (default: 34)
- `cross_L2` (int): Cross window spatial parameter L2 (default: 17)
- `cross_t1` (int): Cross window color threshold t1 (default: 20)
- `cross_t2` (int): Cross window color threshold t2 (default: 6)
- `so_p1` (float): Scanline optimization parameter p1 (default: 1.0)
- `so_p2` (float): Scanline optimization parameter p2 (default: 3.0)
- `so_tso` (int): Scanline optimization parameter tso (default: 15)
- `irv_ts` (int): Iterative Region Voting parameter ts (default: 20)
- `irv_th` (float): Iterative Region Voting parameter th (default: 0.4)
- `lrcheck_thres` (float): Left-right consistency check threshold (default: 1.0)
- `do_lr_check` (bool): Enable left-right consistency check (default: True)
- `do_filling` (bool): Enable disparity filling (default: True)
- `do_discontinuity_adjustment` (bool): Enable discontinuity adjustment (default: False)

**Methods:**
- `compute(left_image, right_image)`: Compute disparity map from stereo pair

## Performance Tips

### Raspberry Pi Optimization

1. **Use smaller images**: Downscale images before processing for faster computation
```python
import cv2
left = cv2.imread('left.png')
right = cv2.imread('right.png')

# Downscale by 2x
left_small = cv2.resize(left, None, fx=0.5, fy=0.5)
right_small = cv2.resize(right, None, fx=0.5, fy=0.5)

disparity = adcensus.compute_disparity(left_small, right_small)
```

2. **Reduce disparity range**: Use smaller max_disparity for faster computation
```python
disparity = adcensus.compute_disparity(
    'left.png', 'right.png',
    min_disparity=0,
    max_disparity=32  # Instead of 64 or 128
)
```

3. **Disable optional features**: Turn off left-right check and filling for speed
```python
stereo = ADCensusStereo(
    do_lr_check=False,
    do_filling=False
)
```

## Troubleshooting

### Build Errors

**Error: "Could not find OpenCV"**
```bash
# Install OpenCV development files
sudo apt-get install libopencv-dev
```

**Error: "Could not find pybind11"**
```bash
pip3 install pybind11
```

### Runtime Errors

**Error: "Image dimensions don't match"**
- Ensure left and right images have the same dimensions

**Error: "Images must be 3-channel color images"**
- Convert grayscale images to BGR:
```python
img = cv2.imread('image.png', cv2.IMREAD_COLOR)
```

## Testing

Run the example script to verify installation:
```bash
cd examples
python3 example_usage.py
```

## Performance Benchmarks

Approximate processing times (640x480 images, disparity range 0-64):

- Desktop (Intel i7): ~2-3 seconds
- Raspberry Pi 4: ~10-15 seconds
- Raspberry Pi 3: ~25-35 seconds

## License

See LICENSE file for details.

## References

Original paper:
Mei X, Sun X, Zhou M, et al. **On building an accurate stereo matching system on graphics hardware**. IEEE International Conference on Computer Vision Workshops, 2012.

Original C++ implementation:
https://github.com/ethan-li-coding/AD-Census

