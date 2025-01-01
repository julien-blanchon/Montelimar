import collections.abc
import inspect
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import cast

import mlx.core as mx
from mlx import nn

from ocr_mlx.utils import custom_roll, window_partition, window_reverse


@dataclass
class DonutSwinModelConfig:
    model_type: str = "donut-swin"
    image_size: int = 224
    patch_size: int = 4
    num_channels: int = 3
    embed_dim: int = 96
    depths: list[int] = field(default_factory=lambda: [2, 2, 6, 2])
    num_heads: list[int] = field(default_factory=lambda: [3, 6, 12, 24])
    window_size: int = 7
    mlp_ratio: float = 4.0
    qkv_bias: bool = True
    hidden_dropout_prob: float = 0.0
    attention_probs_dropout_prob: float = 0.0
    drop_path_rate: float = 0.1
    hidden_act: str = "gelu"
    use_absolute_embeddings: bool = False
    initializer_range: float = 0.02
    layer_norm_eps: float = 1e-5
    hidden_size: int = field(init=False)
    num_hidden_layers: int = field(init=False)
    chunk_size_feed_forward: int = 0

    def __post_init__(self):
        self.hidden_size = int(self.embed_dim * 2 ** (len(self.depths) - 1))
        self.num_hidden_layers = len(self.depths)

    @classmethod
    def from_dict(cls, params):
        return cls(**{
            k: v for k, v in params.items() if k in inspect.signature(cls).parameters
        })


class DonutSwinPatchEmbeddings(nn.Module):
    def __init__(self, config: DonutSwinModelConfig):
        super().__init__()

        image_size, patch_size = config.image_size, config.patch_size
        num_channels, hidden_size = config.num_channels, config.embed_dim
        image_size = (
            image_size
            if isinstance(image_size, collections.abc.Iterable)
            else (image_size, image_size)
        )
        patch_size = (
            patch_size
            if isinstance(patch_size, collections.abc.Iterable)
            else (patch_size, patch_size)
        )
        num_patches = (image_size[1] // patch_size[1]) * (
            image_size[0] // patch_size[0]
        )
        self.image_size = image_size
        self.patch_size = patch_size
        self.num_channels = num_channels
        self.num_patches = num_patches
        self.grid_size = (
            image_size[0] // patch_size[0],
            image_size[1] // patch_size[1],
        )

        self.projection = nn.Conv2d(
            in_channels=num_channels,
            out_channels=hidden_size,
            kernel_size=patch_size,
            stride=patch_size,
            bias=True,
        )

    def maybe_pad(self, pixel_values, height, width):
        pad_width = [(0, 0)] * 4  # Initialize pad_width with zeros for all dimensions
        if width % self.patch_size[1] != 0:
            pad_width[3] = (0, self.patch_size[1] - width % self.patch_size[1])
        if height % self.patch_size[0] != 0:
            pad_width[2] = (0, self.patch_size[0] - height % self.patch_size[0])
        return mx.pad(pixel_values, pad_width=pad_width, constant_values=0)

    def __call__(self, pixel_values: mx.array) -> mx.array:
        batch_size, height, width, num_channels = pixel_values.shape
        pixel_values = self.maybe_pad(pixel_values, height, width)
        embeddings = self.projection(pixel_values)
        batch_size, height, width, hidden_size = embeddings.shape
        embeddings = embeddings.reshape(batch_size, height * width, hidden_size)
        output_dimensions = (height, width)
        return embeddings, output_dimensions


class DonutSwinEmbeddings(nn.Module):
    def __init__(self, config: DonutSwinModelConfig):
        super().__init__()

        self.patch_embeddings = DonutSwinPatchEmbeddings(config)
        self.patch_grid = self.patch_embeddings.grid_size

        self.norm = nn.LayerNorm(config.embed_dim)

    def __call__(self, pixel_values: mx.array) -> mx.array:
        embeddings, output_dimensions = self.patch_embeddings(pixel_values)
        embeddings = self.norm(embeddings)
        return embeddings, output_dimensions


class DonutSwinSelfAttention(nn.Module):
    def __init__(self, config, dim, num_heads, window_size):
        super().__init__()
        if dim % num_heads != 0:
            msg = (
                f"The hidden size ({dim}) is not a multiple of the number of "
                f"attention heads ({num_heads})"
            )
            raise ValueError(msg) from None

        self.num_attention_heads = num_heads
        self.attention_head_size = int(dim / num_heads)
        self.all_head_size = self.num_attention_heads * self.attention_head_size
        self.window_size = (
            window_size
            if isinstance(window_size, collections.abc.Iterable)
            else (window_size, window_size)
        )

        self.relative_position_bias_table = mx.zeros((
            (2 * self.window_size[0] - 1) * (2 * self.window_size[1] - 1),
            num_heads,
        ))
        coords_h = mx.arange(self.window_size[0])
        coords_w = mx.arange(self.window_size[1])
        coords = mx.stack(mx.meshgrid(coords_h, coords_w, indexing="ij"), axis=0)
        coords_flatten = coords.reshape(2, -1)
        relative_coords = coords_flatten[:, :, None] - coords_flatten[:, None, :]
        relative_coords = mx.transpose(relative_coords, (1, 2, 0))
        relative_coords[:, :, 0] += self.window_size[0] - 1
        relative_coords[:, :, 1] += self.window_size[1] - 1
        relative_coords[:, :, 0] *= 2 * self.window_size[1] - 1
        self.relative_position_index = mx.sum(relative_coords, axis=-1)
        self.query = nn.Linear(
            self.all_head_size, self.all_head_size, bias=config.qkv_bias
        )
        self.key = nn.Linear(
            self.all_head_size, self.all_head_size, bias=config.qkv_bias
        )
        self.value = nn.Linear(
            self.all_head_size, self.all_head_size, bias=config.qkv_bias
        )

    def transpose_for_scores(self, x):
        new_x_shape = x.shape[:-1] + (
            self.num_attention_heads,
            self.attention_head_size,
        )
        x = x.reshape(new_x_shape)
        return x.transpose(0, 2, 1, 3)

    def __call__(
        self, hidden_states: mx.array, attention_mask: mx.array | None = None
    ) -> mx.array:
        batch_size, dim, _ = hidden_states.shape
        mixed_query_layer = self.query(hidden_states)

        key_layer = self.transpose_for_scores(self.key(hidden_states))
        value_layer = self.transpose_for_scores(self.value(hidden_states))
        query_layer = self.transpose_for_scores(mixed_query_layer)

        attention_scores = query_layer @ key_layer.transpose(0, 1, 3, 2)
        attention_scores /= mx.sqrt(float(self.attention_head_size))

        relative_position_bias = self.relative_position_bias_table[
            self.relative_position_index.reshape(-1)
        ]
        relative_position_bias = relative_position_bias.reshape((
            self.window_size[0] * self.window_size[1],
            self.window_size[0] * self.window_size[1],
            -1,
        ))

        relative_position_bias = relative_position_bias.transpose(2, 0, 1)
        attention_scores += mx.expand_dims(relative_position_bias, 0)
        if attention_mask is not None:
            mask_shape = attention_mask.shape[0]
            attention_scores = attention_scores.reshape(
                batch_size // mask_shape, mask_shape, self.num_attention_heads, dim, dim
            )
            attention_scores += mx.expand_dims(mx.expand_dims(attention_mask, 1), 0)
            attention_scores = attention_scores.reshape(
                -1, self.num_attention_heads, dim, dim
            )

        attention_probs = mx.softmax(
            attention_scores.astype(mx.float32), axis=-1
        ).astype(attention_scores.dtype)
        context_layer = attention_probs @ value_layer
        context_layer = context_layer.transpose(0, 2, 1, 3)
        new_context_layer_shape = context_layer.shape[:-2] + (self.all_head_size,)
        context_layer = context_layer.reshape(new_context_layer_shape)

        return (context_layer,)


class DonutSwinSelfOutput(nn.Module):
    def __init__(self, config, dim):
        super().__init__()
        self.dense = nn.Linear(dim, dim)

    def __call__(self, hidden_states: mx.array, input_tensor: mx.array) -> mx.array:
        return self.dense(hidden_states)


class DonutSwinAttention(nn.Module):
    def __init__(self, config, dim, num_heads, window_size):
        super().__init__()
        self.self = DonutSwinSelfAttention(config, dim, num_heads, window_size)
        self.output = DonutSwinSelfOutput(config, dim)

    def __call__(
        self, hidden_states: mx.array, attention_mask: mx.array | None = None
    ) -> mx.array:
        self_outputs = self.self(hidden_states, attention_mask)
        attention_output = self.output(self_outputs[0], hidden_states)
        return (attention_output,) + self_outputs[1:]


class DonutSwinIntermediate(nn.Module):
    def __init__(self, config, dim):
        super().__init__()
        self.dense = nn.Linear(dim, int(config.mlp_ratio * dim))
        self.intermediate_act_fn = nn.GELU()

    def __call__(self, hidden_states: mx.array) -> mx.array:
        hidden_states = self.dense(hidden_states)
        return self.intermediate_act_fn(hidden_states)


class DonutSwinOutput(nn.Module):
    def __init__(self, config, dim):
        super().__init__()
        self.dense = nn.Linear(int(config.mlp_ratio * dim), dim)

    def __call__(
        self,
        hidden_states: mx.array,
    ) -> mx.array:
        return self.dense(hidden_states)


class DonutSwinLayer(nn.Module):
    def __init__(
        self,
        config: DonutSwinModelConfig,
        dim: int,
        input_resolution: tuple,
        num_heads: int,
        shift_size: int,
    ):
        super().__init__()
        self.chunk_size_feed_forward = config.chunk_size_feed_forward
        self.shift_size = shift_size
        self.window_size = config.window_size
        self.input_resolution = input_resolution
        self.layernorm_before = nn.LayerNorm(dim, eps=config.layer_norm_eps)
        self.attention = DonutSwinAttention(
            config, dim, num_heads, window_size=self.window_size
        )
        self.layernorm_after = nn.LayerNorm(dim, eps=config.layer_norm_eps)
        self.intermediate = DonutSwinIntermediate(config, dim)
        self.output = DonutSwinOutput(config, dim)

    def set_shift_and_window_size(self, input_resolution):
        if min(input_resolution) <= self.window_size:
            # if window size is larger than input resolution, we don't partition windows
            self.shift_size = 0
            self.window_size = min(input_resolution)

    def maybe_pad(self, hidden_states, height, width):
        pad_right = (self.window_size - width % self.window_size) % self.window_size
        pad_bottom = (self.window_size - height % self.window_size) % self.window_size
        pad_values = [(0, 0), (0, pad_bottom), (0, pad_right), (0, 0)]
        hidden_states = mx.pad(hidden_states, pad_width=pad_values, constant_values=0)
        return hidden_states, pad_values

    def get_attn_mask(self, height, width):
        if self.shift_size > 0:
            img_mask = mx.zeros((1, height, width, 1))
            height_slices = (
                slice(0, -self.window_size),
                slice(-self.window_size, -self.shift_size),
                slice(-self.shift_size, None),
            )
            width_slices = (
                slice(0, -self.window_size),
                slice(-self.window_size, -self.shift_size),
                slice(-self.shift_size, None),
            )
            count = 0
            for height_slice in height_slices:
                for width_slice in width_slices:
                    img_mask[:, height_slice, width_slice, :] = count
                    count += 1
            mask_windows = window_partition(img_mask, self.window_size)
            mask_windows = mask_windows.reshape(-1, self.window_size * self.window_size)
            attn_mask = mask_windows[:, mx.newaxis, :] - mask_windows[:, :, mx.newaxis]
            attn_mask = mx.where(attn_mask != 0, -100.0, 0.0).astype(mx.float32)
        else:
            attn_mask = None
        return attn_mask

    def __call__(
        self,
        hidden_states: mx.array,
        input_dimensions: tuple[int, int],
        attention_mask: mx.array | None = None,
    ) -> mx.array:
        self.set_shift_and_window_size(input_dimensions)
        height, width = input_dimensions
        batch_size, _, channels = hidden_states.shape
        shortcut = hidden_states
        hidden_states = self.layernorm_before(hidden_states)

        hidden_states = hidden_states.reshape(batch_size, height, width, channels)

        hidden_states, pad_values = self.maybe_pad(hidden_states, height, width)
        _, height_pad, width_pad, _ = hidden_states.shape
        # cyclic shift
        if self.shift_size > 0:
            shifted_hidden_states = custom_roll(
                hidden_states, shift=(-self.shift_size, -self.shift_size), axis=(1, 2)
            )
        else:
            shifted_hidden_states = hidden_states

        hidden_states_windows = window_partition(
            shifted_hidden_states, self.window_size
        )
        hidden_states_windows = hidden_states_windows.reshape(
            -1, self.window_size * self.window_size, channels
        )
        attn_mask = self.get_attn_mask(height_pad, width_pad)
        attention_outputs = self.attention(hidden_states_windows, attn_mask)

        attention_output = attention_outputs[0]
        attention_windows = attention_output.reshape(
            -1, self.window_size, self.window_size, channels
        )
        shifted_windows = window_reverse(
            attention_windows, self.window_size, height_pad, width_pad
        )

        if self.shift_size > 0:
            attention_windows = custom_roll(
                shifted_windows, shift=(self.shift_size, self.shift_size), axis=(1, 2)
            )
        else:
            attention_windows = shifted_windows

        was_padded = pad_values[1][1] > 0 or pad_values[2][1] > 0
        if was_padded:
            attention_windows = attention_windows[:, :height, :width, :]

        attention_windows = attention_windows.reshape(
            batch_size, height * width, channels
        )

        hidden_states = shortcut + attention_windows
        layer_output = self.layernorm_after(hidden_states)
        layer_output = self.intermediate(layer_output)
        return hidden_states + self.output(layer_output)


class DonutSwinStage(nn.Module):
    def __init__(
        self,
        config: DonutSwinModelConfig,
        dim: int,
        input_resolution: tuple,
        depth: int,
        num_heads: int,
        drop_path: list[float],
        downsample: nn.Module | None = None,
    ):
        super().__init__()
        self.config = config
        self.dim = dim
        self.blocks = [
            DonutSwinLayer(
                config=config,
                dim=dim,
                input_resolution=input_resolution,
                num_heads=num_heads,
                shift_size=0 if (i % 2 == 0) else config.window_size // 2,
            )
            for i in range(depth)
        ]

        if downsample is not None:
            self.downsample = downsample(
                input_resolution, dim=dim, norm_layer_maker=nn.LayerNorm
            )
        else:
            self.downsample = None

        self.pointing = False

    def __call__(
        self,
        hidden_states: mx.array,
        input_dimensions: tuple[int, int],
        head_mask: mx.array | None = None,
    ) -> mx.array:
        height, width = input_dimensions
        for i, layer_module in enumerate(self.blocks):
            layer_head_mask = head_mask[i] if head_mask is not None else None

            hidden_states = layer_module(
                hidden_states, input_dimensions, layer_head_mask
            )

        hidden_states_before_downsampling = hidden_states

        if self.downsample is not None:
            height_downsampled, width_downsampled = (height + 1) // 2, (width + 1) // 2
            output_dimensions = (height, width, height_downsampled, width_downsampled)
            hidden_states = self.downsample(
                hidden_states_before_downsampling, input_dimensions
            )
        else:
            output_dimensions = (height, width, height, width)

        stage_outputs = (
            hidden_states,
            hidden_states_before_downsampling,
            output_dimensions,
        )

        return stage_outputs


class DonutSwinPatchMerging(nn.Module):
    def __init__(
        self,
        input_resolution: tuple[int],
        dim: int,
        norm_layer_maker: Callable[[int], nn.Module] = nn.LayerNorm,
    ) -> None:
        super().__init__()
        self.input_resolution = input_resolution
        self.dim = dim
        self.reduction = nn.Linear(4 * dim, 2 * dim, bias=False)
        self.norm = norm_layer_maker(4 * dim)

    def maybe_pad(self, input_feature, height, width):  # noqa: PLR6301
        should_pad = (height % 2 == 1) or (width % 2 == 1)
        if should_pad:
            pad_height = height % 2
            pad_width = width % 2
            pad_values = [(0, 0), (0, pad_height), (0, pad_width), (0, 0)]
            input_feature = mx.pad(
                input_feature, pad_width=pad_values, constant_values=0
            )

        return input_feature

    def __call__(
        self, input_feature: mx.array, input_dimensions: tuple[int, int]
    ) -> mx.array:
        height, width = input_dimensions
        # `dim` is height * width
        batch_size, _, num_channels = input_feature.shape

        input_feature = input_feature.reshape(batch_size, height, width, num_channels)
        # pad input to be divisible by width and height, if needed
        input_feature = self.maybe_pad(input_feature, height, width)
        # ** [batch_size, height/2, width/2, num_channels]
        input_feature_0 = input_feature[:, 0::2, 0::2, :]
        # ** [batch_size, height/2, width/2, num_channels]
        input_feature_1 = input_feature[:, 1::2, 0::2, :]
        # ** [batch_size, height/2, width/2, num_channels]
        input_feature_2 = input_feature[:, 0::2, 1::2, :]
        # ** [batch_size, height/2, width/2, num_channels]
        input_feature_3 = input_feature[:, 1::2, 1::2, :]
        # ** [batch_size, height/2, width/2, 4*num_channels]
        input_feature = mx.concatenate(
            [input_feature_0, input_feature_1, input_feature_2, input_feature_3],
            axis=-1,
        )
        input_feature = input_feature.reshape(
            batch_size, -1, 4 * num_channels
        )  # batch_size height/2*width/2 4*C

        input_feature = self.norm(input_feature)
        return self.reduction(input_feature)


class DonutSwinEncoder(nn.Module):
    def __init__(self, config: DonutSwinModelConfig, grid_size: tuple[int, int]):
        super().__init__()

        self.config = config
        self.num_layers = len(config.depths)
        dpr = mx.linspace(
            start=0, stop=config.drop_path_rate, num=sum(config.depths)
        ).tolist()
        dpr = cast(list[float], dpr)
        self.layers = [
            DonutSwinStage(
                config=config,
                dim=int(config.embed_dim * 2**layer_id),
                input_resolution=(
                    grid_size[0] // (2**layer_id),
                    grid_size[1] // (2**layer_id),
                ),
                depth=config.depths[layer_id],
                num_heads=config.num_heads[layer_id],
                drop_path=dpr[
                    sum(config.depths[:layer_id]) : sum(config.depths[: layer_id + 1])
                ],
                downsample=DonutSwinPatchMerging
                if (layer_id < self.num_layers - 1)
                else None,
            )
            for layer_id in range(self.num_layers)
        ]

    def __call__(
        self,
        hidden_states: mx.array,
        input_dimensions: tuple[int, int],
        head_mask: mx.array | None = None,
    ) -> mx.array:
        hidden_states = hidden_states
        for i, layer_module in enumerate(self.layers):
            layer_head_mask = head_mask[i] if head_mask is not None else None
            layer_outputs = layer_module(
                hidden_states, input_dimensions, layer_head_mask
            )
            hidden_states = layer_outputs[0]
            output_dimensions = layer_outputs[2]
            input_dimensions = (int(output_dimensions[-2]), int(output_dimensions[-1]))

        return hidden_states


class DonutSwinModel(nn.Module):
    def __init__(self, config: DonutSwinModelConfig):
        super().__init__()

        self.config = config
        self.num_layers = len(config.depths)
        self.num_features = int(config.embed_dim * 2 ** (self.num_layers - 1))

        self.embeddings = DonutSwinEmbeddings(config)
        self.encoder = DonutSwinEncoder(config, self.embeddings.patch_grid)

    def __call__(
        self, pixel_values: mx.array | None, head_mask: mx.array | None = None
    ) -> mx.array:
        if pixel_values is None:
            msg = "You have to specify pixel_values"
            raise ValueError(msg)
        embedding_output, input_dimensions = self.embeddings(pixel_values)
        encoder_outputs = self.encoder(
            embedding_output,
            (int(input_dimensions[0]), int(input_dimensions[1])),
            head_mask=head_mask,
        )
        return encoder_outputs

    @staticmethod
    def sanitize(weights):
        sanitized_weights = {}
        for k, v in weights.items():
            if k.startswith("decoder."):
                continue
            # remove `encoder.` prefix in k
            k = k.replace("encoder.", "", 1)
            if "projection.weight" in k:
                # PyTorch conv2d weight tensors have shape:
                #   [out_channels, in_channels, kH, KW]
                # MLX conv2d expects the weight be of shape:
                #   [out_channels, kH, KW, in_channels]
                sanitized_weights[k] = v.transpose(0, 2, 3, 1)
            else:
                sanitized_weights[k] = v
        return sanitized_weights
