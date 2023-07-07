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
    p.add_argument("--full_mode", "-n", default=False)
    args = p.parse_args()
    print(args)
    input_file = args.input
    full_mode = bool(args.full_mode)
    model, device = load_model(pretrained_model=args.pretrained_model)

    if full_mode:
        separate(
            input=input_file,
            model=model,
            device=device,
            output_dir=args.output_dir,
        )
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
    else:
        separate(
            input=input_file,
            model=model,
            device=device,
            output_dir=args.output_dir,
            only_no_vocals=True,
        )


if __name__ == "__main__":
    main()
