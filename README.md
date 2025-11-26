# Detecting and Analyzing Embryo Cardiac Activity

This project detects and analyzes the cardiac activity of an embryonic medaka fish using standard computer vision techniques applied to time-series microscopy images. The pipeline automatically identifies the embryo, locates the beating heart, and estimates heart rate—all without requiring labeled training data.

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![OpenCV](https://img.shields.io/badge/OpenCV-4.x-green.svg)

## 📋 Table of Contents
- [Overview](#overview)
- [Key Assumptions](#key-assumptions)
- [Methodology](#methodology)
  - [Data Loading and Preprocessing](#data-loading-and-preprocessing)
  - [Heart Detection](#heart-detection)
  - [Heart Rate Estimation](#heart-rate-estimation)
- [Results](#results)
- [Limitations and Future Improvements](#limitations-and-future-improvements)
- [Installation and Usage](#installation-and-usage)
- [Project Structure](#project-structure)

## 🔬 Overview

This computer vision pipeline processes time-lapse TIFF images of embryonic medaka fish to automatically detect and analyze cardiac activity. The approach leverages motion-based analysis to identify the beating heart and extract physiological measurements, demonstrating how classical computer vision techniques can effectively solve biological image analysis problems.

**Technologies Used:** Python, OpenCV, NumPy, Matplotlib, SciPy

## 🎯 Key Assumptions

The pipeline operates under the following biological and imaging assumptions:

- **Circular embryo structure**: The embryo appears as a circular region in the images, making it detectable using geometric shape detection methods
- **Cardiac motion dominance**: The heart is the primary source of periodic motion within the embryo
- **Static background**: Surrounding tissues and the embryo body remain relatively static compared to the beating heart
- **Temporal consistency**: Images are captured at regular intervals with embedded timestamps

These assumptions allow us to use motion as the primary signal for heart detection without requiring complex segmentation models.

## 🔍 Methodology

### Data Loading and Preprocessing

**Purpose**: Prepare raw microscopy images for analysis by isolating the embryo region and enhancing image quality.

#### Step 1: Image Loading
Raw TIFF images are loaded from `data/raw_Tiff/`. Each filename contains a timestamp (T-field) that tracks temporal information across frames, enabling time-series analysis of cardiac activity.

#### Step 2: Region of Interest Extraction
The full microscopy images are quite large, but the embryo occupies only a small portion. To improve computational efficiency and focus analysis on the relevant area, the images are cropped to a smaller region of interest (ROI) containing the embryo.

**Why this matters**: Analyzing only the relevant region reduces processing time and eliminates background noise that could interfere with subsequent detection steps.

#### Step 3: Embryo Detection Using Hough Circle Transform
Since the embryo has a circular shape, we use:
- **Canny edge detection** to identify boundaries in the image
- **Hough Circle Transform** to automatically detect circular structures

The algorithm finds multiple candidate circles and uses the averaged center with the largest detected radius to define the embryo boundary.

**Why Hough Circles?** This classical computer vision technique is perfect for detecting well-defined geometric shapes without training data. The parameters were tuned using the interactive `CannyTuner.py` tool to find optimal edge detection thresholds (minThres=52, maxThres=118).

#### Step 4: Noise Reduction and Normalization
Two preprocessing techniques enhance image quality:

1. **Bilateral Filtering**: Reduces noise while preserving important edge details of the heart structure
   - Unlike standard blurring, bilateral filters smooth regions while keeping sharp boundaries intact
   
2. **CLAHE (Contrast Limited Adaptive Histogram Equalization)**: Normalizes brightness and enhances contrast
   - Addresses the low-contrast problem common in microscopy images
   - Makes subtle intensity changes (like heartbeats) more visible
   - Ensures consistent brightness across all frames for reliable temporal analysis

**Output**: Preprocessed images are saved to `data/processed_Tiff/` for inspection and validation.

### Heart Detection

**Purpose**: Identify the location of the beating heart within the embryo using motion-based analysis.

#### The Motion Accumulation Approach

Since the heart beats periodically while surrounding tissues remain relatively still, we can detect it by analyzing movement:

1. **Frame Differencing**: Calculate pixel-wise differences between consecutive frames to identify regions with change
   - Areas with motion (the beating heart) show high difference values
   - Static regions show near-zero differences

2. **Motion Accumulation**: Sum all frame differences across the entire time series
   - Creates a "heat map" showing which pixels changed most throughout the recording
   - The heart region accumulates the highest motion values

3. **Smoothing and Thresholding**: 
   - Apply Gaussian blur to reduce noise in the motion map
   - Use Otsu's automatic thresholding to separate high-motion regions from static background
   - This creates a binary mask highlighting moving structures

4. **Morphological Refinement**:
   - **Closing operations** fill small gaps in the detected region
   - **Opening operations** remove small noise artifacts
   - Ensures we get a clean, continuous heart region

5. **Contour Detection**: Find the largest connected high-motion region
   - This is identified as the heart
   - A bounding box with padding defines the heart's region of interest (ROI)

**Why this works**: The beating heart is the dominant source of periodic motion in the embryo, making motion accumulation an effective and simple detection method without requiring labeled training data.

### Heart Rate Estimation

**Purpose**: Extract heart rate from the temporal intensity changes in the detected heart region.

#### Signal Extraction and Processing

1. **Intensity Signal Extraction**: Calculate the mean pixel intensity of the heart ROI across all frames
   - As the heart contracts and relaxes, the tissue density and light absorption change
   - This creates a periodic intensity signal synchronized with heartbeats

2. **Signal Normalization**: Apply z-score normalization to standardize the signal
   - Removes baseline intensity variations
   - Centers the signal around zero for easier peak detection

3. **Detrending**: Remove slow, long-term variations in the signal
   - Isolates the periodic heartbeat component
   - Makes peaks more uniform and easier to detect

4. **Peak Detection**: Use `scipy.signal.find_peaks` to identify heartbeats
   - **Peaks** represent systole (heart contraction)
   - **Valleys** represent diastole (heart relaxation)
   - Minimum distance and prominence parameters prevent false positives

## 📊 Results

The method successfully detected and analyzed the embryo's cardiac activity:

### Detection Performance
- ✅ **Embryo localization**: The Hough Circle Transform accurately captured the circular embryo region
- ✅ **Automatic cropping**: Using the largest detected radius ensured the entire embryo stayed centered in all frames
- ✅ **Image enhancement**: CLAHE normalization significantly improved visibility in the low-contrast microscopy images

### Heart Detection
- ✅ **Motion-based segmentation**: Motion accumulation clearly highlighted movement areas
- ✅ **Robust isolation**: Thresholding and morphological operations successfully isolated the heart region without labeled data
- ✅ **Accurate localization**: The largest contour consistently identified the heart across different frames

### Heart Rate Analysis
- ✅ **Clear periodic signal**: The extracted intensity signal showed distinct periodic changes corresponding to heartbeats
- ✅ **Reliable peak detection**: The algorithm accurately identified heartbeat events with consistent spacing
- ✅ **Quantitative measurement**: Heart rate was successfully estimated from the temporal signal

**Key Insight**: By leveraging the fact that the heart is the primary moving structure, classical computer vision techniques achieved reliable cardiac detection and measurement without requiring deep learning or manual annotation.

## ⚠️ Limitations and Future Improvements

### Current Limitations

1. **Motion assumption dependency**: The approach assumes the heart is the region with the most motion
   - May fail if other structures move significantly (e.g., if the embryo itself moves)
   - Limited to well-controlled experimental conditions with stable imaging

2. **Generalization constraints**: 
   - Pipeline is tuned for this specific dataset with certain embryo sizes and orientations
   - Different embryo positions or rotations may require parameter adjustments
   - Edge detection thresholds were manually tuned and may not transfer to other imaging conditions

3. **Temporal resolution**: Small timing differences between frames exist but were not corrected
   - Currently adequate for heart rate estimation
   - Could be improved for more precise measurements

### Potential Improvements

- **Machine learning integration**: Deep learning segmentation models could provide more robust heart detection across varying conditions
- **Optical flow analysis**: Advanced motion tracking (e.g., Lucas-Kanade) could capture finer heart movement patterns
- **Time interpolation**: Resampling frames to uniform time intervals would produce cleaner periodic signals
- **Multi-embryo support**: Extend the pipeline to analyze multiple embryos simultaneously
- **Parameter optimization**: Implement automatic parameter tuning instead of manual adjustment
- **3D analysis**: If volumetric data is available, extend to 3D cardiac analysis

## 🚀 Installation and Usage

### Prerequisites

```bash
pip install numpy opencv-python matplotlib scipy
```

Or install from requirements file:
```bash
pip install -r requirements.txt
```

**Required packages**: `numpy`, `opencv-python`, `matplotlib`, `scipy`

### Data Preparation

Place raw TIFF images in `data/raw_Tiff/` with the format:
```
<name>--T<timestamp>.tif
```

Example: `embryo_001--T0000.tif`, `embryo_001--T0100.tif`, etc.

### Running the Analysis

#### Option 1: Jupyter Notebook (Recommended)
```bash
jupyter notebook notebook.ipynb
```

Execute all cells sequentially. The notebook will:
1. Load images from `data/raw_Tiff/`
2. Detect and crop embryo regions
3. Apply preprocessing and normalization
4. Detect the heart using motion analysis
5. Estimate heart rate from temporal signals
6. Save processed images to `data/processed_Tiff/`
7. Generate visualizations for each step

#### Option 2: Parameter Tuning (Optional)

If working with new data, use the interactive Canny edge detector tuner:

```bash
python CannyTuner.py
```

Adjust the trackbar sliders to find optimal edge detection thresholds for your images, then update the values in the notebook (cell 9).

### Output

- **Processed images**: `data/processed_Tiff/` - Cropped and normalized embryo images
- **Visualizations**: Generated inline in the notebook
  - Motion accumulation maps
  - Heart detection overlays
  - Temporal intensity signals
  - Heartbeat peak detection plots

## 📁 Project Structure

```
embryo-heart-rate-analysis/
│
├── data/
│   ├── raw_Tiff/           # Input: Raw microscopy TIFF images
│   └── processed_Tiff/     # Output: Preprocessed embryo images
│
├── notebook.ipynb          # Main analysis pipeline
├── CannyTuner.py           # Interactive edge detection parameter tuner
├── .gitignore              # Git ignore file
├── README.md               # This file
└── requirements.txt        # Python dependencies
```

