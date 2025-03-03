
#Importing Libraries

from PIL import Image, ImageDraw, ImageFilter,ImageFont
import numpy as np
import matplotlib.pyplot as plt
import sys

def im_load(image_path):
    
    im = Image.open(image_path).convert("L")  
    return im



# Convert image to binary using a threshold (Inverted Colors: Black Bacground and White color for Staff Lines and Notes)

def inv_col(image):
    image_array = np.array(image)
    threshold =200
    bin_img = (image_array < threshold).astype(np.uint8) * 255  # Invert binary colors

    #Debugging Purpose 
    #np.savetxt('binary_image.csv', binary_image, delimiter=',', fmt='%d')

    return Image.fromarray(bin_img)

def inv_col_distort(image):
    img_arr = np.array(image)
    threshold =50
    bin_img = (img_arr < threshold).astype(np.uint8) * 255  # Invert binary color

    return Image.fromarray(bin_img)



def staff_line_detect(image,line_threshold=0.5):
    
    bin = np.array(image)

    h, w = bin.shape

    # 1. Edge Detection (Simple Horizontal Gradient)
    gradient = np.zeros_like(bin)
    for y in range(1, h - 1):
        gradient[y, :] = np.abs(bin[y, :] - bin[y - 1, :])  # Difference between consecutive rows

    # Step 2 
    theta = 180  # Only check for Hoz. Lines
    rho_max = int(np.hypot(h, w))  #
    accumulator = np.zeros((2 * rho_max, theta)) 

    # Iterating on edge pixels
    for y in range(h):
        for x in range(w):
            if gradient[y, x] > 0:  
                rho = y  
                accumulator[rho, 0] += 1  
                accumulator[rho, 179] += 1  #

    # Step 3
    threshold_accum = np.max(accumulator) * 0.5  # If the value is >50% of max value, consider it a line
    detected_lines = np.where(accumulator[:, 0] > threshold_accum)[0]  

    # Step 4
    filtered_lines = []
    gp_lines = []
    curr_gp = []

    gap = 4  # Max allowed gap between grouped staff lines
    for y in detected_lines:
        if not curr_gp or y - curr_gp[-1] <= gap:
            curr_gp.append(y)
        else:
            gp_lines.append(curr_gp)
            curr_gp = [y]

    if curr_gp:
        gp_lines.append(curr_gp)

    for group in gp_lines:
        filtered_lines.append(int(np.mean(group))) 

    #print ("filtered Lines:",filtered_lines)
    #print ("Detected Lines:",detected_lines)
    
    expanded_lines = []
    hough_detected_lines=filtered_lines.copy()
    original_lines=detected_lines.copy()
    filtered_lines.extend(detected_lines)
    for y in filtered_lines:  # Use individual y-coordinates directly
        
        # Check the percentage of white pixels in rows above and below
        # Calculating this for scenarios where the width of the staff line is >1 pixel

        white_pixels_above_1 = np.sum(bin[y - 1, :] == 255) / w if y > 0 else 0
        white_pixels_below_1 = np.sum(bin[y + 1, :] == 255) / w if y < h - 1 else 0
        white_pixel_percentage = np.sum(bin[y, :] == 255) / w    

        # Use this for debugging the coordinates for Staff Lines
        
        #print (y,y-1,y+1)
        #print (white_pixel_percentage,white_pixels_above,white_pixels_below) 
        
        # If either row has >50% white pixels, expand removal range to +1 and -1 rows
        if white_pixels_above_1 >= line_threshold and white_pixels_below_1 >= line_threshold:
            
            expanded_range = [y - 1, y, y + 1]  # Expand by ±1 row
            #print("expanded range")
        else:
            # Select the two y-values that are above the threshold
            valid_rows = []
            if white_pixels_above_1 >= line_threshold:
                valid_rows.append(y - 1)
            if white_pixel_percentage >= line_threshold:
                valid_rows.append(y)
            if white_pixels_below_1 >= line_threshold:
                valid_rows.append(y + 1)
            
            
            if len(valid_rows) > 2:
                valid_rows = valid_rows[:2]
            
            expanded_range = valid_rows  
            

        expanded_lines.extend(expanded_range)
        
        #print (expanded_range)
        #expanded_lines.extend(expanded_range)

    return sorted(set(expanded_lines)), original_lines, hough_detected_lines



def rm_stafflines(image, staff_lines):
    
    img_arr = np.array(image)  
    for y in staff_lines:
        
        img_arr[max(0, y - 2): min(img_arr.shape[0], y + 3), :] = 0  

    return Image.fromarray(img_arr)  



def noteheads_detect(image):
    
    img_arr = np.array(image)
    h, w = img_arr.shape
    visited = np.zeros_like(img_arr, dtype=bool)
    noteh_contour = []

    def floodfill(x, y):
        
        stack = [(x, y)]
        coords = []
        while stack:
            cx, cy = stack.pop()
            if cx < 0 or cy < 0 or cx >= w or cy >= h:
                continue
            if visited[cy, cx] or img_arr[cy, cx] == 0:
                continue
            visited[cy, cx] = True
            coords.append((cx, cy))
            stack.extend([
            (cx+1, cy), (cx-1, cy), (cx, cy+1), (cx, cy-1),  # Left, Right, Up, Down
            (cx+1, cy+1), (cx-1, cy+1), (cx+1, cy-1), (cx-1, cy-1)  # Diagonal directions
        ])
        
        return coords

    for y in range(h):
        for x in range(w):
            if img_arr[y, x] == 255 and not visited[y, x]:  
                comp = floodfill(x, y)
                if 40 < len(comp) < 400:  # Filterin small noise & large objects
                    min_x = min(p[0] for p in comp)
                    max_x = max(p[0] for p in comp)
                    min_y = min(p[1] for p in comp)
                    max_y = max(p[1] for p in comp)

                    # Oval/Circular Components
                    w_comp = max_x - min_x
                    h_comp = max_y - min_y
                    asp_ratio = w_comp / max(h_comp, 1)

                    if 1 < asp_ratio < 4:  # Roughly circular/oval
                        padding = 10 
                        noteh_contour.append((
                            max(0, min_x - padding), max(0, min_y - padding), 
                            min(w, max_x + padding) - min_x, 
                            min(h, max_y + padding) - min_y
                        ))

    return noteh_contour




def note_names(notes, staff_lines):
    
    
    names = ["E", "F", "G", "A", "B", "C", "D", "E", "F", "G"]  
    notes_detected = []

    #
    staff_lines = sorted(set(staff_lines))  # Remove duplicates & sort
    num_staves = len(staff_lines) // 5  

    for i in range(num_staves):
        s_batch = staff_lines[i * 5:(i + 1) * 5]  # Process staff in batches of 5
        s_spacing = (s_batch[-1] - s_batch[0]) / 4 

        for x, y, w, h in notes:
            if s_batch[0] - s_spacing <= y <= s_batch[-1] + s_spacing:  # Allow space notes
               
                d = [abs(y - line) for line in s_batch]
                closest_ind = d.index(min(d))

                
                if min(d) <= s_spacing / 2:
                    note_name = names[closest_ind]  # Note on a line
                else:
                    note_name = names[closest_ind + 1]  # Note is in space

                notes_detected.append((x, y, w, h, note_name))

    return notes_detected


def draw_notes(image, det_notes):
     

    im_draw = image.convert("RGB")  
    draw = ImageDraw.Draw(im_draw)

    

    for x, y, w, h, note_name in det_notes:
        # Draw bounding box around note
        draw.rectangle([x, y, x + w, y + h], outline="red", width=2)
        # Add text label (note name)
        draw.text((x, y - 20), note_name, fill="green", font_size=18)  

    return im_draw



def detect_txt(detected_notes,note_name, staff_cnf,conf_notes,conf_asp_ratio,output_file="Detected.txt"):
    
    avg_confidence = (staff_cnf + conf_notes + conf_asp_ratio) / 3
    with open(output_file, "w") as file:
        file.write(f"Overall Confidence number for Staff Detection: {staff_cnf}\n")
        file.write(f"Overall Confidence number for Notes Detection: {conf_notes}\n")
        file.write(f"Overall Confidence number for Aspect Ratio: {conf_asp_ratio}\n")
        file.write("\n")  
        file.write("Row Col Height Width Pitch Avg_Confidence\n")
        for x, y, w, h, note_name in detected_notes:
            avg_note_conf = (staff_cnf + conf_notes + conf_asp_ratio) / 3
            file.write(f"{y} {x} {h} {w} {note_name} {avg_note_conf:.2f}\n")




def confidence_number(ogLines, expanded_lines,notes):
    ## Metric1: Staff Line Detection
    conf_staff=0
    diff = abs(ogLines - expanded_lines)
    
    if diff < 10:
        conf_staff= 9
    elif diff < 15:
        conf_staff= 8
    elif diff < 25:
        conf_staff= 7
    elif diff < 35:
        conf_staff= 6
    elif diff < 45:
        conf_staff= 5
    else:
        conf_staff= 4  

    total_notes = len(notes)
    conf_notes = 9  
    
    # Metric2: Note Detection
    if total_notes < 5:
        conf_notes = 4  # Too few detected notes
    elif total_notes < 10:
        conf_notes = 6
    elif total_notes < 20:
        conf_notes = 7
    elif total_notes < 30:
        conf_notes = 8
    else:
        conf_notes = 9  

    #Metric3: Aspect Ratio
    conf_aspr=9
    asp_ratio_cnt = 0
    for (x, y, w, h) in notes:
        asp_ratio = w / max(h, 1)
        if 1 <= asp_ratio <= 4:
            asp_ratio_cnt += 1
    
    aspect_ratio = asp_ratio_cnt / max(total_notes, 1)
    

    if aspect_ratio < 0.5:
        conf_aspr -= 3  
    elif aspect_ratio < 0.7:
        conf_aspr -= 2  
    elif aspect_ratio < 0.9:
        conf_aspr -= 1  
    
    return max(conf_staff, 4), max(conf_notes, 4), max(conf_aspr, 4)
    


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 ./omr.py input.png")
        sys.exit(1)
    
    im_path = sys.argv[1]  
    
    # Step1: Function for Loading the Image and converting into Gray Scale
    image = im_load(im_path)

    # Step2: Function for Inverting the colors of the Image; Takes input from Step1
    bin_img = inv_col(image)
    
    # Step3: Function for Detecting Staff Lines; Takes input from Step2
    staff_lines, oglines, hough_detected_lines = staff_line_detect(bin_img)
    
    # Step4: Condition for Removing Staff Lines Based on Image type (Clear and concise or Cluttered and Distorted); Takes input from Step2 and Step3
    if abs(len(staff_lines) - len(hough_detected_lines)) > 20:
        bin_img = inv_col_distort(image)
        staff_lines, oglines, hough_detected_lines = staff_line_detect(bin_img)
    
    # Step5: Function for Detecting Noteheads; Takes input from Step3
    lines_removed = rm_stafflines(bin_img, staff_lines)

    # Step6: Function for Detecting Noteheads; Takes input from Step5
    notes = noteheads_detect(lines_removed)
    
    # Step7: Function for Detecting Note Names; Takes input from Step6 and Step3
    intermediate_im = note_names(notes, oglines)

    # Step8: Function for Drawing Notes; Takes input from Step7 and Step1
    final_image = draw_notes(image, intermediate_im)

    # Step9: Saving the Image
    final_image.save("detected.png")

    # Step10: Confidence Number Calculation
    staff_cnf_n, conf_notes,conf_asp_ratio=confidence_number(len(oglines),len(staff_lines),notes)


    # Step11: Function for Detecting Text; Takes input from Step7, Staff Confidence Number, Note Confidence Number, Aspect Ratio Confidence Number
    detect_txt(intermediate_im,notes,staff_cnf_n,conf_notes,conf_asp_ratio)

    print ("Detection Done")

    
if __name__ == "__main__":
    main()
