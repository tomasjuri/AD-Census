#!/usr/bin/env python3
"""
Test script to verify AD-Census Python wrapper installation
"""

import sys
import os

def test_imports():
    """Test if packages can be imported"""
    print("Testing imports...")
    
    try:
        import numpy as np
        print("  ✓ numpy imported")
    except ImportError as e:
        print(f"  ✗ Failed to import numpy: {e}")
        return False
    
    try:
        import cv2
        print(f"  ✓ opencv imported (version: {cv2.__version__})")
    except ImportError as e:
        print(f"  ✗ Failed to import opencv: {e}")
        return False
    
    try:
        import adcensus
        print(f"  ✓ adcensus imported (version: {adcensus.__version__})")
    except ImportError as e:
        print(f"  ✗ Failed to import adcensus: {e}")
        print("\nThe package may not be installed properly.")
        print("Please run: pip install .")
        return False
    
    return True


def test_functionality():
    """Test basic functionality"""
    print("\nTesting functionality...")
    
    import adcensus
    import numpy as np
    
    # Create synthetic stereo pair
    print("  Creating synthetic test images...")
    height, width = 100, 100
    
    # Simple pattern
    left = np.zeros((height, width, 3), dtype=np.uint8)
    right = np.zeros((height, width, 3), dtype=np.uint8)
    
    # Add some pattern
    for i in range(0, width, 10):
        left[:, i:i+5] = 255
        right[:, i:i+5] = 255
    
    # Shift right image slightly to create disparity
    right[:, 5:] = right[:, :-5]
    
    try:
        print("  Computing disparity...")
        stereo = adcensus.ADCensusStereo(
            min_disparity=0,
            max_disparity=16
        )
        disparity = stereo.compute(left, right)
        print("  ✓ Disparity computation successful")
        
        # Check output
        if disparity.shape == (height, width):
            print(f"  ✓ Output shape correct: {disparity.shape}")
        else:
            print(f"  ✗ Unexpected output shape: {disparity.shape}")
            return False
        
        return True
        
    except Exception as e:
        print(f"  ✗ Error during computation: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_example_data():
    """Test with example data if available"""
    print("\nTesting with example data...")
    
    example_left = 'Data/Cone/im2.png'
    example_right = 'Data/Cone/im6.png'
    
    if not os.path.exists(example_left) or not os.path.exists(example_right):
        print("  ⚠ Example data not found, skipping")
        return True
    
    try:
        import adcensus
        import cv2
        
        print(f"  Loading {example_left} and {example_right}...")
        left = cv2.imread(example_left)
        right = cv2.imread(example_right)
        
        if left is None or right is None:
            print("  ✗ Failed to load example images")
            return False
        
        print(f"  Image size: {left.shape[1]}x{left.shape[0]}")
        print("  Computing disparity (this may take a few seconds)...")
        
        disparity = adcensus.compute_disparity(
            left, right,
            min_disparity=0,
            max_disparity=64
        )
        
        print("  ✓ Disparity computed successfully")
        
        # Try to save
        print("  Saving result to test_output.png...")
        adcensus.save_disparity(disparity, 'test_output')
        
        if os.path.exists('test_output-disparity.png'):
            print("  ✓ Output file created successfully")
            # Clean up
            os.remove('test_output-disparity.png')
            if os.path.exists('test_output-disparity-color.png'):
                os.remove('test_output-disparity-color.png')
            return True
        else:
            print("  ✗ Output file was not created")
            return False
            
    except Exception as e:
        print(f"  ✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    print("=" * 70)
    print("AD-Census Python Wrapper - Installation Test")
    print("=" * 70)
    print()
    
    # Run tests
    results = []
    
    results.append(("Import Test", test_imports()))
    
    if results[0][1]:  # Only continue if imports work
        results.append(("Functionality Test", test_functionality()))
        results.append(("Example Data Test", test_example_data()))
    
    # Summary
    print("\n" + "=" * 70)
    print("Test Summary")
    print("=" * 70)
    
    for test_name, result in results:
        status = "PASSED" if result else "FAILED"
        symbol = "✓" if result else "✗"
        print(f"{symbol} {test_name}: {status}")
    
    print("=" * 70)
    
    all_passed = all(result for _, result in results)
    
    if all_passed:
        print("\n✓ All tests passed! Installation is working correctly.")
        print("\nYou can now use the adcensus package:")
        print("  import adcensus")
        print("  disparity = adcensus.compute_disparity('left.png', 'right.png')")
        print("\nTry the examples:")
        print("  cd examples")
        print("  python3 simple_example.py")
        return 0
    else:
        print("\n✗ Some tests failed. Please check the errors above.")
        print("\nTroubleshooting:")
        print("  1. Make sure all dependencies are installed:")
        print("     pip3 install -r requirements.txt")
        print("  2. Rebuild the package:")
        print("     pip3 install --force-reinstall .")
        print("  3. Check the documentation in PYTHON_README.md")
        return 1


if __name__ == '__main__':
    sys.exit(main())

