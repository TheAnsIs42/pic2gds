# pic2gds

Python scripts for converting images into GDSII files. The conversion process involves creating striped regions based on the gray levels of the image.

## Overview

Two scripts included:

1. **`pic2gds.py` (recommanded)**: This script processes generates a GDS file with stripes regions based on defined gray level thresholds and fills them with different densities.
2. **`pic2gds_contour.py` (experimental)**: This script enhances the conversion by detecting contours in the grayscale image and creating stripes within those contours.

## Advantages

Comparing to the [kadomoto/picture-to-gds](https://github.com/kadomoto/picture-to-gds) repository, this project offers stripes filling according to the gray level of the image instead of pixel-by-pixel. Which offers smaller GDS file size, better performance, and is more litho-limit-reaching friendly.


## Requirements

Following Python packages are required:

- `gdstk`
- `opencv-python`
- `numpy`

You can install the required packages using pip:

```bash
pip install -r requirements.txt
```

## Usage

You can run the script with the following command:

```bash
python3 pic2gds.py
```

or

```bash
python3 pic2gds_contour.py
```

## TODOs

- [ ] non-linear gray level to density
- [ ] gradio interface

## Contributing

Contributions are welcomed! If you have suggestions for improvements or new features, feel free to open an issue or submit a pull request.


## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

