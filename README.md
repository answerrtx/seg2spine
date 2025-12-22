# Seg2spine (Under Construction)

Implementation of **Validity of a fast automated 3d spine reconstruction measurements for biplanar radiographs** https://pubmed.ncbi.nlm.nih.gov/38926172/.

Pipeline: Segmentation x 3 -> Extract the 3D information -> Visualization & Measurement
Because of limited manpower (:<), the open-sourcing of the remaining parts will have to wait until I have time to clean everything up.

### Hugging Face Demo for Visualization: [DEMO](https://huggingface.co/spaces/answerrtx/SpineVis)

#### How to use

- Generate 3D Transforms (17×9)

After obtaining pa.txt and lat.txt after the segmentation, run:
```
python3 tools/transform_2views.py \
  --pa pa_tmp.txt --lat lat_tmp.txt \
  --templ_w 1.0 --templ_h 0.45 --templ_d 0.7 \
  --out transforms.txt
```
or 
```
python3 tools/transform_full.py \
  --pa pa_tmp.txt --lat lat_tmp.txt --ped ped_tmp.txt \
  --templ_w 1.0 --templ_h 0.45 --templ_d 0.7 \
  --out transforms.txt
```
This generates transforms.txt with 17 lines, each containing 9 numbers: sx sy sz ang1 ang2 ang3 tx ty tz

Meaning:
sx sy sz: scale factors that deform the template bbox (templ_w, templ_h, templ_d) to match the predicted bbox size (normalized)
ang1 ang2 ang3: rotations in degrees
tx ty tz: translations in the same normalized units


- Paste into the Demo UI

Open transforms.txt. Copy all numbers (newlines are OK). Paste into the demo field Transformation. The demo accepts 153 numbers (= 17×9) separated by spaces/commas/newlines. 

### Segmentation 

Three segmentations should be applied to create the 3d modeling:
1. vertebrae segmentation on PA view
2. pedicle segmentation on PA view
3. vertebrae segmentation on LAT view

### 3D Info Extraction
From the binary masks, generate 3 txt files. 

The result for PA and LAT vertebrae must be a **17-line** text file (one vertebra per line, ordered **T1..T17**).
Each line contains **5 floats**:

- `cent_x` `cent_y` `width` `height` `ang`

Where:

- `cent_x`, `cent_y`: center coordinates in **pixels**
- `width`, `height`: bounding box size in **pixels**
- `ang`: tilt angle in **degrees** (as produced by the segmentation model)

Example (one line):

512.3 248.7 80.1 42.6 -4.75

The result for Pedile must be a **17-line** text file (one vertebra per line, ordered **T1..T17**).
Each line contains **1 integer and 4 floats**:

- `vert_id` `cent_x1` `cent_y1` `cent_x2` `cent_x2`

The vertebral rotation should be calculated combining the PA and LAT results.


### Preview of the software
Segmentation and Measurement
![image](https://github.com/user-attachments/assets/b28da424-2738-4d8d-b127-3ebdbe37d01f)

Reconstruction
![image](https://github.com/user-attachments/assets/e46adb2e-0f5c-4a25-bffe-b0487dde5bb2)
![image](https://github.com/user-attachments/assets/b56f0285-c920-4ff2-bd65-87938c06cb15)
![image](https://github.com/user-attachments/assets/216a7809-a17d-4b98-8fd6-148b16af50f4)
