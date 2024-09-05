import argparse

from PIL import Image
import numpy as np

def clean_isolated_pixels(image_array):

    cleaned_image = image_array.copy()
    height, width, _ = image_array.shape

    # Iterate every pixel avoiding edges
    for i in range(1, height - 1):
        for j in range(1, width - 1):

            current_pixel = image_array[i, j]

            neighbours = [
                image_array[i - 1, j],  # up
                image_array[i + 1, j],  # down
                image_array[i, j - 1],  # left
                image_array[i, j + 1],  # right
            ]

            # Calculate the colour difference with neighbours
            difference = [np.sum(np.abs(current_pixel - neighbour)) for neighbour in neighbours]

            # If the difference with all neighbours is too great, it is likely to be isolated.
            if all(dif > 100 for dif in difference):
                cleaned_image[i, j] = [0, 0, 0]

    return cleaned_image

def es_pixel_negro(pixel, tolerancia=254):
    return all(val <= tolerancia for val in pixel)


# Función principal
def main(width, height, path, keep_aspect_ratio, output_file, show_output, clean_pixels, tolerance):

    # Load the image and convert it to RGB
    image = Image.open(path).convert('RGB')

    # Resize image according to aspect ratio option
    if keep_aspect_ratio:
        image.thumbnail((width, height), Image.Resampling.NEAREST)
    else:
        image = image.resize((width, height), Image.Resampling.NEAREST)

    image_array = np.asarray(image)

    if clean_pixels:
        image_array = clean_isolated_pixels(image_array)

    # for row in image_array:
    #     for pixel in row:
    #         print(pixel)

    # Create tuples from non-black pixels
    tuples = [(x % image_array.shape[1], x // image_array.shape[1])
              for x, value in enumerate(image_array.reshape(-1, 3))
              if not es_pixel_negro(value, tolerance)]

    # Save tuple array to the output file
    with open(output_file, 'w') as f:
        f.write(str(tuples))
        f.write("\n")

    if show_output:
        print(tuples)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="This script processes an image by resizing it and optionally cleaning isolated pixels. It extracts the coordinates of non-black pixels, outputting them as tuples. These tuples can be used with the Pillow ImageDraw.point(xy, fill=None) method to recreate the image by drawing points.")
    parser.add_argument("-W", "--width", type=int, default=128, help="The width to which the image will be resized in pixels (default 128).")
    parser.add_argument("-H", "--height", type=int, default=64, help="The height to which the image will be resized in pixels (default 64). ")
    parser.add_argument("-p", "--path", type=str, required=True, help="The full path to the image file that you want to process.")
    parser.add_argument("-k", "--keep-aspect-ratio", action='store_true', help="Maintain the original aspect ratio of the image during resizing. If set, the image will be resized while preserving its proportions.")
    parser.add_argument("-o", "--output-file", type=str, default='tuple_array.txt', help="Specify the name of the file where the processed tuple array of pixel coordinates will be saved.")
    parser.add_argument("-s", "--show-output", action='store_true', help="If set, the tuple array of pixel coordinates will also be printed to the console in addition to being saved to a file.")
    parser.add_argument("-c", "--clean-pixels", action='store_true', help="Enable this option to remove isolated or 'noisy' pixels from the image, replacing them with a default color (black).")
    parser.add_argument("-t", "--tolerance", type=int, default=10, help="Tolerance for identifying black pixels.")

    args = parser.parse_args()

    main(args.width, args.height, args.path, args.keep_aspect_ratio, args.output_file, args.show_output, args.clean_pixels, args.tolerance)
