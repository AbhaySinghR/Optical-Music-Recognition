## Part 1: Staff Normalizer

Flow Diagram
![Screenshot 2025-02-27 at 11 33 14 PM](https://github.iu.edu/cs-b657-sp2025/nikkarth-abhasing-singarju-a1/assets/28627/0e88ac1f-3275-445f-bb83-57e3342d22b8)



### How to Run the Code
To run the `staff_normalizer.py` script, follow these steps:

1. **Generate a Test Case using `denormalizer.py`**
   - Run `denormalizer.py` using any image from the `test_images` folder with the following command:
     ```bash
     python3 denormalizer.py [input_image] [output_image] [angle] [factor]
     ```
   - This will create a test case named `output_image` based on the name you provided.

2. **Run the `staff_normalizer.py` script**
   - Using the generated test case (ensure the test case image is in the correct directory), execute the following command:
     ```bash
     python3 staff_normalizer.py input.png output.png
     ```

### Design Decisions
- The implementation first applies **edge detection** using the Sobel filter to identify strong edges in the image.
- The Hough Transform is then applied to detect lines and determine the rotation angle of the staff.
- The detected angle is used to **correct the image orientation** by rotating it to align the staff horizontally.
- The final corrected image is saved as `output.png`.


### Step by Step Flow
1. Convert the image to grayscale.
2. Compute horizontal and vertical edge gradients using a NumPy array.
3. Compute rows, columns, diagonals, and **Hough space for voting**.
4. Identify the most voted pair of rho and theta and rotate the image using `angle-90`.
5. Adjust the image size to fit the rotated content.
6. Use bicubic interpolation for improved image quality.
7. Save the final image.

### Results

Test Cases & Observations

Case 1: Successful Rotation Correction
When an image is rotated using denormalize.py by any angle between 0° and 360° and then processed through staff_normalizer.py, the rotation is corrected successfully.

Rotating the image by 60 degrees:
![music1_test](https://github.iu.edu/cs-b657-sp2025/nikkarth-abhasing-singarju-a1/assets/28627/9ed22211-f076-45ee-8f5e-025c1a0c9004)



Staff Normalizer Auto Rotating the Image by -60 Degrees

![music1_n](https://github.iu.edu/cs-b657-sp2025/nikkarth-abhasing-singarju-a1/assets/28627/9188a92e-acc1-4b37-a9eb-f2e193ea8cd8)


Case 2: Failure with Negative Rotations
When an image is rotated by a negative angle, staff_normalizer.py fails to apply the correct rotation, leaving the image misaligned.

Rotating the image by -30 degrees:

![music1_test-1](https://github.iu.edu/cs-b657-sp2025/nikkarth-abhasing-singarju-a1/assets/28627/43b4b864-41e6-4b01-8e92-dd977f3df2a8)

Incorrect Rotation:

![music1_o](https://github.iu.edu/cs-b657-sp2025/nikkarth-abhasing-singarju-a1/assets/28627/12accb19-154d-498c-807b-d10c5c9c7936)



## Approach to Fix Rotation

Approach 1: Hough Transform-Based Angle Detection

What we did:

Applied the Hough Transform to detect the most prominent lines in the image and used the highest peak in the accumulator to determine the dominant rotation angle.
Outcome:

This method worked well for minor skews but failed for images rotated at 270° or negative angles, as the detected angles were sometimes incorrectly mapped.

Approach 2: Dominant Angle Voting in Hough Accumulator

What we did:

Instead of relying on a single peak from the Hough Transform, we summed votes for angles in defined ranges:
0° range (for horizontal lines)
±90° range (for vertical lines)
This approach helped differentiate between skewed vs. fully rotated images.

Outcome:

This improved handling for 90° and 270° rotations, correctly aligning images where staff lines appeared vertical. However, negative rotations still failed.
Approach 3: Gradient-Based Line Orientation Detection (Sobel Filtering)

What we did:

Applied Sobel filters to compute edge gradients and used the perpendicular orientation of gradients to determine the dominant rotation angle. This method reduced dependency on the Hough Transform.
Outcome:

This approach successfully corrected most 0–360° rotations but failed for negative rotations, likely due to inconsistencies in how angle signs were interpreted in the rotation function.

## Potential Fixes

Refine angle normalization for better quadrant handling.
Investigate PIL’s .rotate() behavior with negative angles.
Use aspect ratio checks as a fallback for incorrect orientations.
Explore Fourier Transform-based detection for staff line alignment.


## Future Improvements
- Implement adaptive thresholding to handle low-contrast images better.
- Use deep learning-based approaches (e.g., CNNs) for improved accuracy.
- Optimize the performance to reduce execution time.

## Contribution Part1

**Abhay**: Understanding the problem and identifying failure cases in staff_normalizer.py.

**Abhay**: Developed and tested multiple approaches for rotation correction, including Hough Transform-based angle detection.

**Abhay**: Implemented dominant angle voting in the Hough accumulator to improve handling of 90° and 270° rotations.

**Abhay**: Investigated failure cases with negative rotations and explored different strategies to normalize detected angles.

**Arju**: Conducted experiments and analyzed results for accuracy.

**Abhay**: Proposed potential future improvements, including refining angle normalization, aspect ratio-based corrections, and alternative rotation detection methods.

**Abhay**: Documented findings, prepared the ReadMe file, and summarized attempted solutions and outcomes.

--

## Part 2 Optical Music Recognition (OMR) - Flow Overview

## **OMR Flow Diagram**
![Screenshot 2025-02-27 at 12 22 53 AM](https://github.iu.edu/cs-b657-sp2025/nikkarth-abhasing-singarju-a1/assets/28627/74d32393-e146-4e66-bbff-809ff44ccee8)

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
<img width="1184" alt="Screenshot 2025-02-27 at 12 25 16 AM" src="https://github.iu.edu/cs-b657-sp2025/nikkarth-abhasing-singarju-a1/assets/28627/3d08077f-7199-4dda-857e-fda878dcccf7">


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
<img width="1177" alt="Screenshot 2025-02-27 at 12 29 27 AM" src="https://github.iu.edu/cs-b657-sp2025/nikkarth-abhasing-singarju-a1/assets/28627/a41da860-e7a6-497c-a884-bac453c96299">

Here, you can observe the right side of the image has a lot of notes undetected due to the reason that the staff line removal is not happening properly. 

Staff Line Removal:
<img width="1193" alt="Screenshot 2025-02-27 at 12 35 11 AM" src="https://github.iu.edu/cs-b657-sp2025/nikkarth-abhasing-singarju-a1/assets/28627/c2d2ec7a-065e-4aa5-9444-c2021a800e1b">



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
<img width="1191" alt="Screenshot 2025-02-27 at 12 57 37 AM" src="https://github.iu.edu/cs-b657-sp2025/nikkarth-abhasing-singarju-a1/assets/28627/a37c7c92-a1f2-42e4-a41f-231367141108">

And note detection is much better than before:
<img width="1189" alt="Screenshot 2025-02-27 at 12 59 27 AM" src="https://github.iu.edu/cs-b657-sp2025/nikkarth-abhasing-singarju-a1/assets/28627/8319f6b0-fc8c-4c2b-abff-19a6275f150e">


Impact of This Approach:

Improved staff line detection, making removal more reliable.
Enhanced note detection, as the noteheads were no longer affected by incomplete staff line removal.


## Calculating Confidence Number
![Screenshot 2025-02-27 at 2 29 09 PM](https://github.iu.edu/cs-b657-sp2025/nikkarth-abhasing-singarju-a1/assets/28627/4d89c0c1-9582-4d8f-aeb8-14d1ac034d14)


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

--



## Part 3 Sheet Music Jigsaw Reassembly

## **🛠️ Step-by-Step Process**

### **1️⃣ Load the Image**
🔹 **Description:** This function loads the input image in grayscale mode to empshaize on the shape of the music sheet.
The image is then split into tiles and the location of each tile is stored in the corners list.

### **2️⃣ Locate the Staff Lines**
🔹 **Description:** For every tile, we have to find if any staff lines pass through it and the calc_staff_rows function gives the vertical or row location of each predicted staff line in the tile.

### **3️⃣ Find Tiles belonging to the same Staff**
Between two tiles, we need to verify if they belong to the same staff. If they do, their staff lines will have the same row location. The calc_staff_mse assigns an error for two tiles based on the staff lines. It penalizes any distance betweem two staff lines. The tiles belonging to the same staff should have a lower mse( mean squared error).


### **4️⃣ Sorting the tiles of the same staff and same row**

Then the image is broken down into rows, where the tiles in the same row belong to the same group. The first tile for each row is chosen randomly from the group. This group is determined using get_row_groups function.

Once the tiles of the same staff have been gathered, they need to be sorted from left to right. Cosine Similarity of the histogram of pixels is used to determine which tiles are neighbours.

The get_better_img_grid function uses cosine similarity to sort out the tiles in the same group.

### **5️⃣ Finding the Optimal Top Row Iteratively**
To further refine the process the first corner tile sorts all the tiles according to staff similarity and keeps enough tiles to fit in a row. The remaining tiles are treated as a new image and the process is repeated.

Finally all the rows are combined to form the final Unscrambled Image.



## 🚀 How to Run `reassemble.py`
```sh
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh

bash Miniconda3-latest-Linux-x86_64.sh

conda create --name <env> --file req.txt
```
Please refer to req.txt in part3. Please ignore the packages that can't be installed, and only install the needed ones, pillow, numpy, scipy, sklearn and scikit-image.

**Please keep the libraries on the correct/latest version for the code to run.**
## **🛠️ Running the Program**
Run the following command in the terminal:
```sh
python3 ./reassemble.py "../test_images/input.png" output.png tile_size
```

If the image is in the same directory as the program omr.py then:
```sh
python3 ./reassemble.py input.png output.png tile_size
```
### **Output Files Generated**
After execution, the program will generate:

✔ **`output.png`** → The unscrambled image. 



## 🎯 Evaluation Results

📊 Quantitative Results

Four test cases were used.

Structural similarity index measure (SSIM) was used to measure similarity between two images, as it considers both structure or shape and contrast of the images, where a 1 indicates identical images, and -1 indicates nearly opposite.

The similarity between the 
✔ Original and Scrambled Images

 'music1': np.float64(0.5446838039550642)
 'music2': np.float64(0.4071169444339614)
 'music3': np.float64(0.270071846829558)
 'music4': np.float64(0.34248531079263167)

✔ Original and Reassembled Images

 'music1': np.float64(0.799770663785539)
 'music2': np.float64(0.4309726915081676)
 'music3': np.float64(0.3541997074351872)
 'music4': np.float64(0.3185931766662456)


For the first three images there is a clear improvement, the fourth image is nearly as it is, though slightly worse.

## Sources

[Sobel_OpenCV](https://docs.opencv.org/4.x/d2/d2c/tutorial_sobel_derivatives.html)

[SSIM_Wikipedia](https://en.wikipedia.org/wiki/Structural_similarity_index_measure)


## Contribution for Part3

**Nikita**: Experimented with the problem to gain a better understanding.

**Nikita**: Tried to match tiles based of margin, ie, matching the left and right margin of two tiles to see if they were neighbours. Making the margin very thin gave better results. Ths method worked well if the tile_size was rather large.

**Nikita**: Realised that as only music images were being dealt with, identifying the staff lines would help group the tiles. A group of tiles had to be on a single staff line as these were music sheets, and this was used as a prior knowledge.

**Nikita**: Went thorugh edge detectors like canny edge detector, and understood how the Sobel Edge detection works, and used a similar concept. Used Gaussian Blurring along with truncation to detect staff lines, the value for blurring and truncating were chosen by trial and error, and mostly gave good results.

**Nikita**:  After grouping the edges, experimented with ways to order them, finally taking cosine similarity of the histogram of pixels as the entire tile needed to be considered. Similar looking tiles were more likely to be neighbours.

**Nikita**: Chose the corner tile among the non padded or filled tiles as a better starting point.

**Nikita**: At first sorted all the tiles based on a corner tile, then reshaped them to form an image. This seemed to work, but it was better to start with a new corner tile for each staff.  Then kept finding the rows from top to bottom and joined them to give the final result.

**Nikita**: Chose SSIM as a similarity measure after among other similarity score like cosine similarity. Evaluated on four test images, the rach.png was taking too much time. Tested the file on Burrow.


**Arju**: Conducted experiments and analyzed results for accuracy. Summarized the ReadMe.

**Nikita**: Updated the ReadME file.

## Areas to Improve 

✅ Better ways to sort tiles of a single staff

✅ Better way to chose a corner tile.

✅ Reduce the time taken to unscramble the image.









