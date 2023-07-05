import argparse
from pathlib import Path

import warnings
from app.service.vocal_remover.runner import load_model, separate
from app.service.demucs_runner import separator

warnings.simplefilter("ignore", UserWarning)
warnings.simplefilter("ignore", FutureWarning)
warnings.filterwarnings("ignore", module="streamlit")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--gpu", "-g", type=int, default=-1)
    p.add_argument("--pretrained_model", "-P", type=str, default="baseline.pth")
    p.add_argument("--input", "-i", required=True)
    p.add_argument("--output_dir", "-o", type=str, default="")
    p.add_argument("--only_no_vocals", "-n", action="store_true")
    args = p.parse_args()

    input_file = args.input

    model, device = load_model(pretrained_model=args.pretrained_model)
    separate(
        input=input_file,
        model=model,
        device=device,
        output_dir=args.output_dir,
        only_no_vocals=args.only_no_vocals,
    )
    if not args.only_no_vocals:
        for stem, model_name in [("vocals", "htdemucs"), (None, "htdemucs"), (None, "htdemucs_6s")]:
            separator(
                tracks=[Path(input_file)],
                out=Path(args.output_dir),
                model=model_name,
                shifts=1,
                overlap=0.5,
                stem=stem,
                int24=False,
                float32=False,
                clip_mode="rescale",
                mp3=True,
                mp3_bitrate=320,
                verbose=False,
            )


if __name__ == "__main__":
    main()
