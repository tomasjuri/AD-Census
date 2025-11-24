/* Python wrapper for AD-Census stereo matching algorithm */

#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include <pybind11/stl.h>
#include "ADCensusStereo.h"
#include <vector>
#include <stdexcept>

namespace py = pybind11;

class ADCensusPython {
private:
    ADCensusStereo stereo_;
    sint32 width_;
    sint32 height_;
    bool initialized_;

public:
    ADCensusPython() : width_(0), height_(0), initialized_(false) {}

    bool initialize(int width, int height, 
                   int min_disparity = 0, 
                   int max_disparity = 64,
                   int lambda_ad = 10,
                   int lambda_census = 30,
                   int cross_L1 = 34,
                   int cross_L2 = 17,
                   int cross_t1 = 20,
                   int cross_t2 = 6,
                   float so_p1 = 1.0f,
                   float so_p2 = 3.0f,
                   int so_tso = 15,
                   int irv_ts = 20,
                   float irv_th = 0.4f,
                   float lrcheck_thres = 1.0f,
                   bool do_lr_check = true,
                   bool do_filling = true,
                   bool do_discontinuity_adjustment = false) {
        
        width_ = width;
        height_ = height;
        
        ADCensusOption option;
        option.min_disparity = min_disparity;
        option.max_disparity = max_disparity;
        option.lambda_ad = lambda_ad;
        option.lambda_census = lambda_census;
        option.cross_L1 = cross_L1;
        option.cross_L2 = cross_L2;
        option.cross_t1 = cross_t1;
        option.cross_t2 = cross_t2;
        option.so_p1 = so_p1;
        option.so_p2 = so_p2;
        option.so_tso = so_tso;
        option.irv_ts = irv_ts;
        option.irv_th = irv_th;
        option.lrcheck_thres = lrcheck_thres;
        option.do_lr_check = do_lr_check;
        option.do_filling = do_filling;
        option.do_discontinuity_adjustment = do_discontinuity_adjustment;
        
        initialized_ = stereo_.Initialize(width, height, option);
        return initialized_;
    }

    py::array_t<float> compute_disparity(py::array_t<uint8_t> img_left, 
                                          py::array_t<uint8_t> img_right) {
        if (!initialized_) {
            throw std::runtime_error("ADCensus not initialized. Call initialize() first.");
        }

        // Check input dimensions
        auto buf_left = img_left.request();
        auto buf_right = img_right.request();

        if (buf_left.ndim != 3 || buf_right.ndim != 3) {
            throw std::runtime_error("Input images must be 3-dimensional (height, width, channels)");
        }

        if (buf_left.shape[2] != 3 || buf_right.shape[2] != 3) {
            throw std::runtime_error("Input images must have 3 channels (BGR)");
        }

        int height = buf_left.shape[0];
        int width = buf_left.shape[1];

        if (height != height_ || width != width_) {
            throw std::runtime_error("Image dimensions don't match initialized dimensions");
        }

        if (height != buf_right.shape[0] || width != buf_right.shape[1]) {
            throw std::runtime_error("Left and right images must have the same dimensions");
        }

        // Get pointers to image data
        uint8_t* ptr_left = static_cast<uint8_t*>(buf_left.ptr);
        uint8_t* ptr_right = static_cast<uint8_t*>(buf_right.ptr);

        // Allocate disparity map
        auto disparity = py::array_t<float>(width * height);
        auto buf_disp = disparity.request();
        float* ptr_disp = static_cast<float*>(buf_disp.ptr);

        // Compute disparity
        if (!stereo_.Match(ptr_left, ptr_right, ptr_disp)) {
            throw std::runtime_error("Stereo matching failed");
        }

        // Reshape to 2D
        disparity.resize({height, width});
        return disparity;
    }
};

PYBIND11_MODULE(adcensus_py, m) {
    m.doc() = "AD-Census stereo matching algorithm Python bindings";

    py::class_<ADCensusPython>(m, "ADCensus")
        .def(py::init<>())
        .def("initialize", &ADCensusPython::initialize,
             py::arg("width"),
             py::arg("height"),
             py::arg("min_disparity") = 0,
             py::arg("max_disparity") = 64,
             py::arg("lambda_ad") = 10,
             py::arg("lambda_census") = 30,
             py::arg("cross_L1") = 34,
             py::arg("cross_L2") = 17,
             py::arg("cross_t1") = 20,
             py::arg("cross_t2") = 6,
             py::arg("so_p1") = 1.0f,
             py::arg("so_p2") = 3.0f,
             py::arg("so_tso") = 15,
             py::arg("irv_ts") = 20,
             py::arg("irv_th") = 0.4f,
             py::arg("lrcheck_thres") = 1.0f,
             py::arg("do_lr_check") = true,
             py::arg("do_filling") = true,
             py::arg("do_discontinuity_adjustment") = false,
             "Initialize the AD-Census stereo matcher with given parameters")
        .def("compute_disparity", &ADCensusPython::compute_disparity,
             py::arg("img_left"),
             py::arg("img_right"),
             "Compute disparity map from left and right stereo images");
}

