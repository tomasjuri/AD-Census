#!/usr/bin/env python3
"""
Simple example of using the AD-Census Python wrapper
"""

import adcensus

# Method 1: Simple one-line usage
print("Computing disparity map...")
disparity = adcensus.compute_disparity(
    '/home/azureuser/projects/AD-Census/left.jpg',
    '/home/azureuser/projects/AD-Census/right.jpg',
    min_disparity=0,
    max_disparity=150
)

# Save the result
adcensus.save_disparity(disparity, 'output')

print("Done! Check 'output-disparity.png' and 'output-disparity-color.png'")

