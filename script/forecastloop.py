from PIL import Image
import argparse
import os

def main():
    parser = argparse.ArgumentParser(description="Generate a loop of forecast images rising up in hour in a given folder.")
    parser.add_argument('folder_path', type=str, help='Path to forecast product folder. Will sort each PNG in the folder in order of forecast hour and turn it into a GIF.')
    parser.add_argument('-o', '--output', type=str, default=None, help='Path to put the finished GIF loop. Defaults to folder_path.')
    parser.add_argument('-d', '--duration', type=float, default=700, help='Time, in ms, for each frame of the GIF to take. Defaults to 700ms.')
    args = parser.parse_args()
    file_list = sorted(os.listdir(args.folder_path))
    file_paths = []
    for image in file_list:
        if image.endswith(".png"):
            file_paths.append(f'{args.folder_path}/{image}')
    images = [Image.open(file) for file in file_paths]
    if args.output != None:
        output_path = args.output
    else:
        output_path = args.folder_path
    images[0].save(f"{output_path}/loop.gif", append_images=images[1:], duration=args.duration, save_all=True, loop=0)
    print(f"GIF loop saved to {output_path}/loop.gif!")

if __name__ == '__main__':
    main()