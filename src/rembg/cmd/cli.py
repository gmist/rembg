import argparse
import glob
import os
from distutils.util import strtobool

from tqdm import tqdm

from ..bg import remove
from ..tools import is_image, heic_to_bytes


def main():
    model_path = os.environ.get(
        "U2NETP_PATH",
        os.path.expanduser(os.path.join("~", ".u2net")),
    )
    model_choices = [os.path.splitext(os.path.basename(x))[0] for x in set(glob.glob(model_path + "/*"))]
    if len(model_choices) == 0:
        model_choices = ["u2net", "u2netp", "u2net_human_seg"]

    ap = argparse.ArgumentParser()

    ap.add_argument(
        "-m",
        "--model",
        default="u2net",
        type=str,
        choices=model_choices,
        help="The model name.",
    )

    ap.add_argument(
        "-a",
        "--alpha-matting",
        nargs="?",
        const=True,
        default=False,
        type=lambda x: bool(strtobool(x)),
        help="When true use alpha matting cutout.",
    )

    ap.add_argument(
        "-af",
        "--alpha-matting-foreground-threshold",
        default=240,
        type=int,
        help="The trimap foreground threshold.",
    )

    ap.add_argument(
        "-ab",
        "--alpha-matting-background-threshold",
        default=10,
        type=int,
        help="The trimap background threshold.",
    )

    ap.add_argument(
        "-ae",
        "--alpha-matting-erode-size",
        default=10,
        type=int,
        help="Size of element used for the erosion.",
    )

    ap.add_argument(
        "-az",
        "--alpha-matting-base-size",
        default=1000,
        type=int,
        help="The image base size.",
    )

    ap.add_argument(
        "-p",
        "--path",
        nargs=2,
        help="An input folder and an output folder.",
    )

    ap.add_argument(
        "-o",
        "--output",
        nargs="?",
        default="-",
        type=argparse.FileType("wb"),
        help="Path to the output png image.",
    )

    ap.add_argument(
        "input",
        nargs="?",
        default="-",
        help="Path to the input image.",
    )

    ap.add_argument(
        "-eb",
        "--enhance_brightness",
        default=1.0,
        type=float,
        help="Enhance brightness (0.0 gives a black image, factor of 1.0 gives the original image.",
    )

    ap.add_argument(
        "-ee",
        "--enhance_edge",
        nargs="?",
        const=True,
        default=False,
        type=lambda x: bool(strtobool(x)),
        help="Increasing the contrast of the pixels around the specific edges.",
    )

    args = ap.parse_args()

    r = lambda i: i.buffer.read() if hasattr(i, "buffer") else i.read()
    w = lambda o, data: o.buffer.write(data) if hasattr(o, "buffer") else o.write(data)

    if args.path:
        full_paths = [os.path.abspath(path) for path in args.path]

        input_paths = [full_paths[0]]
        output_path = full_paths[1]

        if not os.path.exists(output_path):
            os.makedirs(output_path)

        files = set()

        for path in input_paths:
            if os.path.isfile(path):
                files.add(path)
            else:
                input_paths += set(glob.glob(path + "/*"))

        for fi in tqdm(files):
            fi_type = is_image(fi)
            if not fi_type:
                continue

            with open(fi, "rb") as input_data:
                if fi_type == 'image/heic':
                    input_data = heic_to_bytes(input_data)

                s_folders = os.path.join(output_path, *os.path.dirname(fi.split(full_paths[0])[1]).split(os.sep))
                if not os.path.exists(s_folders):
                    os.makedirs(s_folders)
                with open(os.path.join(s_folders, os.path.splitext(os.path.basename(fi))[0] + ".png"), "wb") as output:
                    w(
                        output,
                        remove(
                            r(input_data),
                            model_name=args.model,
                            alpha_matting=args.alpha_matting,
                            alpha_matting_foreground_threshold=args.alpha_matting_foreground_threshold,
                            alpha_matting_background_threshold=args.alpha_matting_background_threshold,
                            alpha_matting_erode_structure_size=args.alpha_matting_erode_size,
                            alpha_matting_base_size=args.alpha_matting_base_size,
                            enhance_brightness=args.enhance_brightness,
                            enhance_edge=args.enhance_edge,
                        ),
                    )

    else:
        fi_type = is_image(args.input)
        if not fi_type:
            return

        with open(args.input, "rb") as input_data:
            if fi_type == 'image/heic':
                input_data = heic_to_bytes(input_data)

            w(
                args.output,
                remove(
                    r(input_data),
                    model_name=args.model,
                    alpha_matting=args.alpha_matting,
                    alpha_matting_foreground_threshold=args.alpha_matting_foreground_threshold,
                    alpha_matting_background_threshold=args.alpha_matting_background_threshold,
                    alpha_matting_erode_structure_size=args.alpha_matting_erode_size,
                    alpha_matting_base_size=args.alpha_matting_base_size,
                    enhance_brightness=args.enhance_brightness,
                    enhance_edge=args.enhance_edge,
                ),
            )


if __name__ == "__main__":
    main()
