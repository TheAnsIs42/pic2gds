import gdstk
import cv2
import numpy as np


def create_striped_regions(gray, pixel_size, min_spacing, stripe_width, main_cell):
    # Define gray level thresholds
    thresholds = [50, 100, 150, 200, 250]

    for i in range(len(thresholds)):
        lower = thresholds[i - 1] if i > 0 else 0
        upper = thresholds[i]

        cell_name = f"gray_level_{lower}_to_{upper}"
        gray_cell = gdstk.Cell(cell_name)
        # Create binary mask for this gray level range
        mask = (np.array(gray, dtype=np.uint8) >= lower) & (
            np.array(gray, dtype=np.uint8) < upper
        )
        mask = mask.astype(np.uint8) * 255  # Convert boolean mask to uint8

        # Find contours in the mask
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Calculate stripe spacing for this gray level
        avg_intensity = (lower + upper) / 2
        spacing = min_spacing + (pixel_size * avg_intensity / 255)

        # Create a copy of the original gray image for contour labeling
        labeled_image = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)

        # Process each contour
        for contour_index, contour in enumerate(contours):
            # Approximate the contour to a polygon
            approx_polygon = cv2.approxPolyDP(contour, 1, True)

            # Create a mask for the polygon
            polygon_mask = np.zeros_like(mask)
            cv2.fillPoly(polygon_mask, [approx_polygon], 255)

            # Iterate over the x positions within the polygon's x range
            for x_pos in range(
                np.min(approx_polygon[:, 0, 0]),
                np.max(approx_polygon[:, 0, 0]),
                int(spacing / pixel_size),
            ):
                # Find intersection points with the polygon at this x position
                intersections = []
                for i in range(len(approx_polygon)):
                    p1 = approx_polygon[i][0]
                    p2 = approx_polygon[(i + 1) % len(approx_polygon)][0]

                    # Check if the vertical line at x_pos intersects with this segment
                    if (p1[0] <= x_pos <= p2[0]) or (p2[0] <= x_pos <= p1[0]):
                        if p2[0] - p1[0] != 0:  # Avoid division by zero
                            y_intersect = p1[1] + (p2[1] - p1[1]) * (x_pos - p1[0]) / (
                                p2[0] - p1[0]
                            )
                            intersections.append(y_intersect)

                if len(intersections) >= 2:
                    # Sort intersections to get top and bottom points
                    intersections.sort()
                    for i in range(0, len(intersections), 2):
                        if i + 1 < len(intersections):
                            stripe = gdstk.rectangle(
                                (
                                    x_pos * pixel_size,
                                    (gray.shape[0] - intersections[i]) * pixel_size,
                                ),
                                (
                                    x_pos * pixel_size + stripe_width,
                                    (gray.shape[0] - intersections[i + 1]) * pixel_size,
                                ),
                            )

                            gray_cell.add(stripe)

            # Draw the contour
            cv2.drawContours(
                labeled_image, [approx_polygon], -1, (0, 255, 0), 2
            )  # Draw contour in green

        if len(gray_cell.polygons) > 0:  # Only add if the cell contains polygons
            main_cell.add(gdstk.Reference(gray_cell))

    # Save the labeled image
    cv2.imwrite("labeled_contours.jpg", labeled_image)


# Example usage
if __name__ == "__main__":
    lib = gdstk.Library()
    cell = gdstk.Cell("general")
    gray = cv2.imread("image.jpg")
    if gray is None:
        print(
            f"Error: Could not load image."
        )
        exit(1)
    gray = cv2.GaussianBlur(gray, (5, 5), 0)  # Adjust kernel size as needed
    cv2.imwrite("processed_image.jpg", gray)
    create_striped_regions(gray, 1, 2, 1, cell)
    lib.add(cell, *cell.dependencies(True))
    lib.write_gds("image_contour.gds")
