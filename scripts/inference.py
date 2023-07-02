import argparse

import warnings
from app.service.vocal_remover.runner import load_model, separate

warnings.simplefilter("ignore", UserWarning)
warnings.simplefilter("ignore", FutureWarning)
warnings.filterwarnings("ignore", module="streamlit")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--gpu", "-g", type=int, default=-1)
    p.add_argument("--pretrained_model", "-P", type=str, default="baseline.pth")
    p.add_argument("--input", "-i", required=True)
    p.add_argument("--output_dir", "-o", type=str, default="")
    args = p.parse_args()

    model, device = load_model(pretrained_model=args.pretrained_model)
    separate(
        input=args.input,
        model=model,
        device=device,
        output_dir=args.output_dir,
        only_no_vocals=True,
    )


if __name__ == "__main__":
    main()
