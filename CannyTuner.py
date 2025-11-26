import cv2 as cv
import os


def nothing(x):
    pass


def cannyThresholdTuner():
    """Interactive Canny edge detection threshold tuner"""
    # Load the first image from rawTiff folder
    folder_path = 'data/raw_Tiff'
    files = sorted([f for f in os.listdir(folder_path) if f.endswith('.tif')])
    
    if len(files) == 0:
        print("Error: No images found")
        return
    
    # Load first image
    img_path = os.path.join(folder_path, files[0])
    img = cv.imread(img_path, cv.IMREAD_GRAYSCALE)
    #img = cv.normalize(img, None, 0, 255, cv.NORM_MINMAX)
    
    if img is None:
        print(f"Error: Could not load {files[0]}")
        return
    
    # Crop the region of interest
    img = img[500:1500, 600:1600]
    
    # Create window and trackbars
    winname = 'Canny Edge Detection Tuner'
    cv.namedWindow(winname)
    cv.createTrackbar('minThres', winname, 0, 255, nothing)
    cv.createTrackbar('maxThres', winname, 0, 255, nothing)
    
    print("Adjust the trackbars to tune Canny edge detection")
    print("Press 'q' to quit")
    
    while True:
        key = cv.waitKey(1)
        if key == ord('q'):
            break
        
        # Check if window was closed
        if cv.getWindowProperty(winname, cv.WND_PROP_VISIBLE) < 1:
            break
        
        # Get current trackbar positions
        minThres = cv.getTrackbarPos('minThres', winname)
        maxThres = cv.getTrackbarPos('maxThres', winname)
        
        # Apply Canny edge detection
        cannyEdge = cv.Canny(img, minThres, maxThres)
        
        # Display the result
        cv.imshow(winname, cannyEdge)
    
    cv.destroyAllWindows()
    print(f"\nFinal Canny parameters:")
    print(f"minThres = {minThres}")
    print(f"maxThres = {maxThres}")


# Run the tuner
cannyThresholdTuner()