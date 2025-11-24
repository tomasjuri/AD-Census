#!/bin/bash
# Installation script for AD-Census Python wrapper

set -e  # Exit on error

echo "=========================================="
echo "AD-Census Python Wrapper Installation"
echo "=========================================="
echo ""

# Detect platform
if [ -f /proc/device-tree/model ]; then
    MODEL=$(cat /proc/device-tree/model)
    if [[ $MODEL == *"Raspberry Pi"* ]]; then
        IS_RASPI=true
        echo "Platform: Raspberry Pi detected"
    else
        IS_RASPI=false
        echo "Platform: Linux"
    fi
else
    IS_RASPI=false
    echo "Platform: Linux"
fi

echo ""
echo "Step 1: Checking system dependencies..."
echo ""

# Check for required commands
MISSING_DEPS=false

if ! command -v cmake &> /dev/null; then
    echo "  [!] CMake not found"
    MISSING_DEPS=true
else
    echo "  [✓] CMake found: $(cmake --version | head -n1)"
fi

if ! command -v python3 &> /dev/null; then
    echo "  [!] Python3 not found"
    MISSING_DEPS=true
else
    echo "  [✓] Python3 found: $(python3 --version)"
fi

if ! command -v g++ &> /dev/null; then
    echo "  [!] C++ compiler not found"
    MISSING_DEPS=true
else
    echo "  [✓] C++ compiler found: $(g++ --version | head -n1)"
fi

if ! pkg-config --exists opencv4 && ! pkg-config --exists opencv; then
    echo "  [!] OpenCV not found"
    MISSING_DEPS=true
else
    if pkg-config --exists opencv4; then
        echo "  [✓] OpenCV found: $(pkg-config --modversion opencv4)"
    else
        echo "  [✓] OpenCV found: $(pkg-config --modversion opencv)"
    fi
fi

if [ "$MISSING_DEPS" = true ]; then
    echo ""
    echo "Some dependencies are missing. Would you like to install them? (y/n)"
    read -r response
    if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
        echo ""
        echo "Installing dependencies..."
        
        if [ "$IS_RASPI" = true ]; then
            sudo apt-get update
            sudo apt-get install -y \
                python3-dev \
                python3-pip \
                cmake \
                build-essential \
                libopencv-dev \
                python3-opencv \
                pkg-config
        else
            sudo apt-get update
            sudo apt-get install -y \
                python3-dev \
                python3-pip \
                cmake \
                build-essential \
                libopencv-dev \
                pkg-config
        fi
    else
        echo "Please install missing dependencies manually and run this script again."
        exit 1
    fi
fi

echo ""
echo "Step 2: Installing Python dependencies..."
echo ""

pip3 install --upgrade pip
pip3 install -r requirements.txt

echo ""
echo "Step 3: Building and installing AD-Census Python package..."
echo ""

if [ "$IS_RASPI" = true ]; then
    # On Raspberry Pi, limit parallel jobs to avoid out-of-memory errors
    echo "  (Building with limited parallelism for Raspberry Pi)"
    export MAKEFLAGS="-j2"
fi

# Clean previous build
rm -rf build/
rm -rf *.egg-info

# Install
pip3 install .

echo ""
echo "Step 4: Verifying installation..."
echo ""

# Test import
python3 -c "import adcensus; print(f'AD-Census version: {adcensus.__version__}')" && \
    echo "  [✓] Installation successful!" || \
    (echo "  [!] Installation verification failed!" && exit 1)

echo ""
echo "=========================================="
echo "Installation Complete!"
echo "=========================================="
echo ""
echo "You can now use the adcensus package in Python:"
echo "  import adcensus"
echo ""
echo "Try the examples:"
echo "  cd examples"
echo "  python3 simple_example.py"
echo ""
echo "For more information, see PYTHON_README.md"
if [ "$IS_RASPI" = true ]; then
    echo "For Raspberry Pi specific tips, see RASPBERRY_PI.md"
fi
echo ""

