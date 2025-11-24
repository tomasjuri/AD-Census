"""
AD-Census Stereo Matching Algorithm Python Package

This package provides a Python interface to the AD-Census stereo matching algorithm,
which computes disparity maps from stereo image pairs.
"""

import numpy as np
import cv2
from typing import Union, Tuple, Optional
import os

# Import the C++ extension module
try:
    from .adcensus_py import ADCensus as _ADCensus
except ImportError:
    # If not built yet, provide helpful error message
    raise ImportError(
        "The adcensus_py module is not built. Please run 'pip install .' "
        "from the project root directory to build and install the package."
    )

__version__ = "0.1.0"
__all__ = ['ADCensusStereo', 'compute_disparity', 'save_disparity']


class ADCensusStereo:
    """
    AD-Census Stereo Matching Algorithm
    
    This class provides a high-level interface to the AD-Census stereo matching algorithm.
    It handles image loading, preprocessing, and disparity computation.
    
    Parameters:
        min_disparity (int): Minimum disparity value (default: 0)
        max_disparity (int): Maximum disparity value (default: 64)
        lambda_ad (int): AD cost parameter (default: 10)
        lambda_census (int): Census cost parameter (default: 30)
        cross_L1 (int): Cross window spatial parameter L1 (default: 34)
        cross_L2 (int): Cross window spatial parameter L2 (default: 17)
        cross_t1 (int): Cross window color threshold t1 (default: 20)
        cross_t2 (int): Cross window color threshold t2 (default: 6)
        so_p1 (float): Scanline optimization parameter p1 (default: 1.0)
        so_p2 (float): Scanline optimization parameter p2 (default: 3.0)
        so_tso (int): Scanline optimization parameter tso (default: 15)
        irv_ts (int): Iterative Region Voting parameter ts (default: 20)
        irv_th (float): Iterative Region Voting parameter th (default: 0.4)
        lrcheck_thres (float): Left-right consistency check threshold (default: 1.0)
        do_lr_check (bool): Enable left-right consistency check (default: True)
        do_filling (bool): Enable disparity filling (default: True)
        do_discontinuity_adjustment (bool): Enable discontinuity adjustment (default: False)
    """
    
    def __init__(self, 
                 min_disparity: int = 0,
                 max_disparity: int = 64,
                 lambda_ad: int = 10,
                 lambda_census: int = 30,
                 cross_L1: int = 34,
                 cross_L2: int = 17,
                 cross_t1: int = 20,
                 cross_t2: int = 6,
                 so_p1: float = 1.0,
                 so_p2: float = 3.0,
                 so_tso: int = 15,
                 irv_ts: int = 20,
                 irv_th: float = 0.4,
                 lrcheck_thres: float = 1.0,
                 do_lr_check: bool = True,
                 do_filling: bool = True,
                 do_discontinuity_adjustment: bool = False):
        
        self.min_disparity = min_disparity
        self.max_disparity = max_disparity
        self.lambda_ad = lambda_ad
        self.lambda_census = lambda_census
        self.cross_L1 = cross_L1
        self.cross_L2 = cross_L2
        self.cross_t1 = cross_t1
        self.cross_t2 = cross_t2
        self.so_p1 = so_p1
        self.so_p2 = so_p2
        self.so_tso = so_tso
        self.irv_ts = irv_ts
        self.irv_th = irv_th
        self.lrcheck_thres = lrcheck_thres
        self.do_lr_check = do_lr_check
        self.do_filling = do_filling
        self.do_discontinuity_adjustment = do_discontinuity_adjustment
        
        self._stereo = _ADCensus()
        self._initialized = False
        
    def compute(self, 
                left_image: Union[str, np.ndarray], 
                right_image: Union[str, np.ndarray]) -> np.ndarray:
        """
        Compute disparity map from stereo image pair.
        
        Parameters:
            left_image: Left image as file path (str) or numpy array
            right_image: Right image as file path (str) or numpy array
            
        Returns:
            Disparity map as numpy array (float32, shape: [height, width])
        """
        # Load images if they are file paths
        if isinstance(left_image, str):
            if not os.path.exists(left_image):
                raise FileNotFoundError(f"Left image not found: {left_image}")
            img_left = cv2.imread(left_image, cv2.IMREAD_COLOR)
            if img_left is None:
                raise ValueError(f"Failed to load left image: {left_image}")
        else:
            img_left = left_image
            
        if isinstance(right_image, str):
            if not os.path.exists(right_image):
                raise FileNotFoundError(f"Right image not found: {right_image}")
            img_right = cv2.imread(right_image, cv2.IMREAD_COLOR)
            if img_right is None:
                raise ValueError(f"Failed to load right image: {right_image}")
        else:
            img_right = right_image
        
        # Validate images
        if img_left.shape != img_right.shape:
            raise ValueError(f"Image dimensions must match: {img_left.shape} vs {img_right.shape}")
        
        if len(img_left.shape) != 3 or img_left.shape[2] != 3:
            raise ValueError(f"Images must be 3-channel color images, got shape: {img_left.shape}")
        
        height, width = img_left.shape[:2]
        
        # Initialize if needed
        if not self._initialized:
            self._initialized = self._stereo.initialize(
                width, height,
                self.min_disparity, self.max_disparity,
                self.lambda_ad, self.lambda_census,
                self.cross_L1, self.cross_L2,
                self.cross_t1, self.cross_t2,
                self.so_p1, self.so_p2,
                self.so_tso, self.irv_ts, self.irv_th,
                self.lrcheck_thres,
                self.do_lr_check, self.do_filling,
                self.do_discontinuity_adjustment
            )
            if not self._initialized:
                raise RuntimeError("Failed to initialize AD-Census stereo matcher")
        
        # Ensure images are contiguous and in the right format
        img_left = np.ascontiguousarray(img_left, dtype=np.uint8)
        img_right = np.ascontiguousarray(img_right, dtype=np.uint8)
        
        # Compute disparity
        disparity = self._stereo.compute_disparity(img_left, img_right)
        
        return disparity


def compute_disparity(left_image: Union[str, np.ndarray], 
                     right_image: Union[str, np.ndarray],
                     min_disparity: int = 0,
                     max_disparity: int = 64,
                     **kwargs) -> np.ndarray:
    """
    Convenience function to compute disparity map from stereo image pair.
    
    Parameters:
        left_image: Left image as file path (str) or numpy array
        right_image: Right image as file path (str) or numpy array
        min_disparity: Minimum disparity value (default: 0)
        max_disparity: Maximum disparity value (default: 64)
        **kwargs: Additional parameters to pass to ADCensusStereo
        
    Returns:
        Disparity map as numpy array (float32, shape: [height, width])
    """
    stereo = ADCensusStereo(min_disparity=min_disparity, 
                           max_disparity=max_disparity,
                           **kwargs)
    return stereo.compute(left_image, right_image)


def save_disparity(disparity: np.ndarray, 
                   output_path: str,
                   colormap: bool = True,
                   invalid_value: float = float('inf')) -> None:
    """
    Save disparity map to file.
    
    Parameters:
        disparity: Disparity map as numpy array
        output_path: Output file path (without extension)
        colormap: If True, also save a colorized version (default: True)
        invalid_value: Value representing invalid disparities (default: inf)
    """
    # Normalize disparity for visualization
    valid_mask = np.isfinite(disparity)
    
    if not np.any(valid_mask):
        raise ValueError("No valid disparity values found")
    
    min_disp = np.min(disparity[valid_mask])
    max_disp = np.max(disparity[valid_mask])
    
    # Create normalized disparity map
    disp_normalized = np.zeros_like(disparity, dtype=np.uint8)
    if max_disp > min_disp:
        disp_normalized[valid_mask] = ((disparity[valid_mask] - min_disp) / 
                                       (max_disp - min_disp) * 255).astype(np.uint8)
    
    # Save grayscale disparity
    base_path = output_path.rsplit('.', 1)[0] if '.' in output_path else output_path
    cv2.imwrite(f"{base_path}-disparity.png", disp_normalized)
    
    # Save colorized version if requested
    if colormap:
        disp_color = cv2.applyColorMap(disp_normalized, cv2.COLORMAP_JET)
        cv2.imwrite(f"{base_path}-disparity-color.png", disp_color)
    
    print(f"Disparity map saved to {base_path}-disparity.png")
    if colormap:
        print(f"Colorized disparity map saved to {base_path}-disparity-color.png")

