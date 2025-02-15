import gdstk
import cv2
import numpy as np


def create_striped_regions(
    gray, pixel_size, min_spacing, stripe_width, main_cell, min_length=3
):
    # Define gray level thresholds
    # TODO: non-linear convert from gray level to density
    thresholds = [15, 55, 95, 135, 175, 215, 255]

    height, width = gray.shape

    # Create binary mask for all gray level ranges at once
    masks = [
        (gray >= thresholds[i - 1]) & (gray < thresholds[i])
        for i in range(len(thresholds))
    ]

    for i, mask in enumerate(masks):
        spacing = i + min_spacing
        cell_name = (
            f"gray_level_{thresholds[i - 1] if i > 0 else 0:03}_to_{thresholds[i]:03}"
        )
        gray_cell = gdstk.Cell(cell_name)

        for x in range(0, width, spacing):
            # Get the column of mask at x
            column = mask[:, x]

            # Find transitions (where values change from False to True or True to False)
            transitions = np.where(np.diff(column.astype(int)))[0]

            # Group transitions into pairs (start, end)
            if len(transitions) == 0:
                continue
            # Add column start if first transition is ending (True to False)
            if column[0]:
                transitions = np.insert(transitions, 0, 0)
            # Add column end if last transition is starting (False to True)
            if column[-1]:
                transitions = np.append(transitions, len(column) - 1)

            # Create rectangles for each pair of transitions
            for j in range(0, len(transitions) - 1, 2):
                y_start = transitions[j]
                y_end = transitions[j + 1] + 1

                if y_end - y_start < min_length:
                    continue

                rect = gdstk.rectangle(
                    (x * pixel_size, (height - y_end) * pixel_size),
                    ((x + stripe_width) * pixel_size, (height - y_start) * pixel_size),
                    layer=1,
                )
                gray_cell.add(rect)

        main_cell.add(gdstk.Reference(gray_cell))  # Add the gray cell to the main cell


# Example usage
if __name__ == "__main__":
    lib = gdstk.Library()
    cell = gdstk.Cell("general")
    scaling_factor = 2  # Define your scaling factor here
    gray = cv2.imread("image.jpg", cv2.IMREAD_GRAYSCALE)
    if gray is None:
        print(f"Error: Could not load image.")
        exit(1)
    gray = cv2.resize(
        gray, (0, 0), fx=scaling_factor, fy=scaling_factor
    )  # Scale the image
    # gray = cv2.GaussianBlur(gray, (5, 5), 0)  # Adjust kernel size as needed
    # cv2.imwrite("processed_image.jpg", gray)
    create_striped_regions(gray, 1, 2, 1, cell, 5)
    cell.write_svg(
        "test.svg",
        background="white",
        shape_style={(1, 0): {"fill": "black", "stroke": "none"}},
        scaling=1,
        pad=0,
    )
    lib.add(cell, *cell.dependencies(True))
    lib.write_gds("image.gds")
