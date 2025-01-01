import json

import mlx.core as mx
from mlx import nn

from ocr_mlx.model.donut import DonutSwinModel, DonutSwinModelConfig
from ocr_mlx.model.mbart import MBartConfig, MBartModel
from ocr_mlx.utils import get_model_path


class Nougat(nn.Module):
    def __init__(self):
        super().__init__()
        self.encoder: DonutSwinModel
        self.decoder: MBartModel

    @staticmethod
    def from_pretrained(path_or_hf_repo: str) -> "Nougat":
        path = get_model_path(path_or_hf_repo)

        with path.joinpath("config.json").open() as f:
            model_config = json.load(f)

        model = Nougat()
        encoder_config = DonutSwinModelConfig.from_dict(model_config["encoder"])
        decoder_config = MBartConfig.from_dict(model_config["decoder"])
        encoder = DonutSwinModel(encoder_config)
        decoder = MBartModel(decoder_config)
        weight_files = path.glob("*.safetensors")
        if not weight_files:
            msg = f"No safetensors found in {path}"
            raise FileNotFoundError(msg)

        weights = {}
        for wf in weight_files:
            weights.update(mx.load(wf.as_posix()))

        model.encoder = encoder
        model.decoder = decoder

        if (quantization := model_config.get("quantization", None)) is not None:

            def class_predicate(p: str, m: nn.Module):  # noqa: ARG001
                return f"{p}.scales" in weights

            nn.quantize(
                model,
                **quantization,
                class_predicate=class_predicate,
            )
            encoder_weights = {
                k.replace("encoder.", "", 1): v
                for k, v in weights.items()
                if not k.startswith("decoder.")
            }
            decoder_weights = {
                k.replace("decoder.", ""): v
                for k, v in weights.items()
                if not k.startswith("encoder.")
            }
        else:
            encoder_weights = DonutSwinModel.sanitize(weights)
            decoder_weights = MBartModel.sanitize(weights)

        model.encoder.load_weights(list(encoder_weights.items()))
        model.decoder.load_weights(list(decoder_weights.items()))

        return model
