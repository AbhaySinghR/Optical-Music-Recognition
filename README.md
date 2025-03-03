Optical Music Recognition (OMR) - Flow Overview

## **OMR Flow Diagram**
![Screenshot 2025-03-03 at 2 41 32 AM](https://github.com/user-attachments/assets/b4e80b50-ab2e-4012-814c-ec05be0f3081)

--

## **Step-by-Step Process**

### ** Load the Image**
 **Description:** This function loads the input image and converts it into a **grayscale format**, making it easier for further processing.

### **Convert to a Binary Image**
 **Description:**  
- Invert colors to enhance the visibility of **staff lines** and **notes**.   **White (255):** Staff Lines & Notes and **Black (0):** Background. A separate function **inv_col_distort** is created to handle images with varying thickness of images with cluttered notes.

### **Detect Staff Lines using Hough Transformation**
 **Description:**  
- Use **Hough Transform** to detect **horizontal staff lines**.Assumes **θ = 180°** (horizontal lines). Thresholds are applied so that if **50% of the pixels are white**, it is classified as a **staff line**. A brute-force implementation is included to handle **varying line thickness (>1 pixel).**

### **Removing Staff Lines**
**Description:**  
- Uses the **y-coordinates of detected staff lines** (from Step 3) to **remove** them. Converts the **white pixels (255) of the detected lines to black (0).**

### **Detecting Noteheads using Flood Fill Algorithm**
 **Description:**  
- Implements the **Flood Fill algorithm** to detect **musical noteheads**. Extends in **all 8 directions** to find **connected components**. Stores the **bounding boxes** around detected noteheads.

### **Assigning Note Names**
 **Description:**  
- Uses **detected staff lines (Step 3)** and **noteheads (Step 5)** to **assign note names**. Determines if a note is **on a line** or **in a space**. Maps the note position to a **musical note (A-G).**

### **Drawing Note Names on the Final Image**
 **Description:**  
- Uses the **assigned note names (Step 6)** to **label** detected notes on the image. Draws **bounding boxes** and overlays **note names**.

### **Calculating Confidence Score & Other Metrics**
 **Description:**  
- Saves detection results to a **text file (`Detected.txt`)**. The text file includes:
  - **Row, Column, Height, Width** (Bounding Box Info). **Pitch** (Detected Note). **Confidence Score** (Accuracy Estimation)
- Confidence is evaluated based on:
  - **Staff Line Detection Accuracy**
  - **Bounding Box Precision** for Note Detection
  - **Correct Note Assignment**
---

##  How to Run `omr.py`
## ** Running the Program**
Run the following command in the terminal:
```sh
python3 ./omr.py "../test_images/input.png"
```
If the image is in the same directory as the program omr.py then:
```sh
python3 ./omr.py input.png
```
### **Output Files Generated**
After execution, the program will generate:

✔ **`detected.png`** → The processed image with detected notes and labels. 

✔ **`Detected.txt`** → A text file listing the detection results, including coordinates, note names and confidence number.



##  Evaluation Results

 Quantitative Results

Case 1: Clear and Concise Images

For a test case where there were 10 staff lines and 38 filled musical notes, the program performed as follows:

 Staff Line Detection:

The program correctly identified all 10 staff lines and accurately retrieved their y-coordinates.
Detection Accuracy: Close to 100%.

 Musical Note Detection:

Out of 38 musical notes, the program successfully detected 30.
False Positives: 21 incorrectly detected notes.
Correct Note Detection Rate: 78%.
False Positive Rate: 65%.

#OMR Detected Image
<img width="1184" alt="Screenshot 2025-02-27 at 12 25 16 AM" src="https://github.com/user-attachments/assets/9f6c993e-6472-4743-b1c8-7596118e5f77" />


 Case 2: Distorted/Cluttered Images (Staff Line Thickness > 1 Pixel)

When processing images with thicker staff lines or distortions, the performance changed:

Staff Line Detection:

The program relied on the expanded range method to account for thickness.
If the image had 10 actual staff lines, the program detected around 32 y-coordinates, indicating potential staff line positions.

 Musical Note Detection:

For 50-60 musical notes, the program detected only 20 notes correctly.
Correct Note Detection Rate: 33%.
False Positive Rate: 50%.

#OMR Detected Image (Before any fix/approach implementation)
<img width="1177" alt="Screenshot 2025-02-27 at 12 29 27 AM" src="https://github.com/user-attachments/assets/120e2924-cebf-401d-addf-0365ae634caf" />


Here, you can observe the right side of the image has a lot of notes undetected due to the reason that the staff line removal is not happening properly. 

Staff Line Removal:
<img width="1193" alt="Screenshot 2025-02-27 at 12 35 11 AM" src="https://github.com/user-attachments/assets/737ecb78-be0d-43ed-bf43-863755526859" />




 Qualitative Analysis: Bottlenecks & Approaches

 Problem: How to Handle Staff Lines with Thickness > 1 Pixel?

 Approach 1: Using Plain Hough Transformation
Method: Applied Hough Transform to detect horizontal staff lines.
Why It Failed: While it worked well for clean and sharp images, it struggled with thicker lines where a single y-coordinate was insufficient to remove the staff line. This resulted in failed note detection for distorted cases.

 Approach 2: Row-Wise Pixel Counting & Averaging After Hough Transform

After obtaining y-coordinates from Hough Transform, we applied a threshold-based grouping.
Nearby lines (within a few pixels) were grouped together, and we calculated the mean y-position.
Why It Failed:
For thicker staff lines, taking the mean was insufficient because different parts of the same thick line had multiple detected y-coordinates.
This approach misidentified staff lines in distorted cases.

Final Approach: Brute Force Detection of Thickness

We refined our detection method by analyzing the binary image array and accounting for thicker lines using a flexible y-coordinate range:

Steps in Our Final Approach:

 1. Detect a line where 50% of the pixels are white and get the y-coordinate.

 2. Check adjacent lines (y±1, y±2, y±3) for white pixel percentage.

 3. Remove staff lines based on thickness:

If y, y-1, and y+1 all have >50% white pixels, remove all.
If two out of three have >50% white pixels, remove those two.
If only y itself crosses the threshold, remove only y (ideal for clear images).

 Implemented a separate function **inv_col_distort()** for processing images where the thickness of the staff lines vary. 

Before understanding this approach, we need to understand how each lists of Y co-ordinates changes according to the input image
There are 2 main Lists that are used for Staff line detection function (staff_line_detect())
1. Expanded Lines
2. hough_detected_lines



**How these changes when the input image is clear and concise. Let's say it has 10 staff lines:**

Expanded Lines: It will have y-coordinates detected and the count will be around 10 only, most probably more not less.
hough_detected_lines: these are the lines which have the exact count of y-coordinates detected i.e. =10

**How these changes when the input image is not clear and staff lines have variable thickness:**

Expanded Lines: It will have y-coordinates detected and the count will be double of the actual staff lines in the image or maybe more. Why? because we are checking a row above and below for potential white line detection for fixing thickness problem.
hough_detected_lines: these are the lines which have the exact count of y-coordinates detected i.e. =10

**Now, how does this help?**

For clear images we follow the normal procedure but for the second case I've implemented a condition that ** if(abs(len(expanded_lines)-len(hough_detected_line))>20)** then completely remove the staff lines from background and then detect the notes. **Using this we can easily identify cases where staff lines have varying thickness because the difference will be more for these cases.**

Using this approach this is how the staff line removal is done for varying thickness:
<img width="1191" alt="Screenshot 2025-02-27 at 12 57 37 AM" src="https://github.com/user-attachments/assets/da5e75dc-719a-496d-8652-51c096b25a62" />

And note detection is much better than before:
<img width="1189" alt="Screenshot 2025-02-27 at 12 59 27 AM" src="https://github.com/user-attachments/assets/72e8a2ad-6e83-4cdf-a286-2311ceb06f21" />



Impact of This Approach:

Improved staff line detection, making removal more reliable.
Enhanced note detection, as the noteheads were no longer affected by incomplete staff line removal.


## Calculating Confidence Number
![Screenshot 2025-03-03 at 2 43 47 AM](https://github.com/user-attachments/assets/1944f344-6dba-4a79-8079-dc46aa685b22)


 Staff Line Detection Accuracy

1. We compare detected staff lines against expected values. The confidence score decreases if there is a significant difference between detected and expected staff lines.

2. If the difference is small (<10 lines), confidence remains high.

 Notehead Detection Quality

1. Confidence is influenced by the number of correctly detected noteheads. We evaluate false positives and filter out incorrectly identified notes.

2. Aspect Ratio Validation: Ensures detected noteheads match expected oval shapes (aspect ratio between 1 to 4). If aspect ratio deviates, confidence decreases.

 Final Confidence Calculation

The final confidence score is computed as the average of these two metrics.

This helps determine the overall reliability of the detection process.

## Sources


[Flood Fill Algorithm](https://medium.com/@koray.kara98.kk/understanding-and-implementing-flood-fill-algorithm-60ab81538d54)

[Hough Transformation (OpenCV)](https://docs.opencv.org/3.4/d9/db0/tutorial_hough_lines.html)

[Reddit OpenCV](https://www.reddit.com/r/opencv/)

[StackOverflow](https://stackoverflow.com/questions)


## Contribution for Part2

**Abhay**: Understanding the Problem & Planning. Defined the problem scope and requirements.

**Abhay**: Created the initial processing flow for the OMR system. Conducted experiments and tested multiple approaches for detecting staff lines.

**Abhay**: Implemented Hough Transform and fine-tuned methods for handling varying staff line thickness.

**Abhay**: Explored different strategies for detecting noteheads using flood-fill algorithms. Tried different aspect ratio filtering for better note identification.

**Abhay**: Brainstormed solutions for difficult cases such as distorted images and varying staff line thickness.

**Abhay**: Designed a confidence scoring mechanism for staff line detection and notehead accuracy.

**Abhay**: Testing on different Test Images and evaluating the results and areas to improve. Testing on Burrow.

**Abhay**: Documentation and ReadMe file update (Flow diagrams and Report).


## Areas to Improve 

  1. Handling False Positives

  2. Improving Staff Line Removal for Cluttered Images

  3. Exploring Template Matching for Note Detection


 Refining Confidence Evaluation


