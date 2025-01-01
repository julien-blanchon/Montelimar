import inspect
import math
from dataclasses import dataclass, field

import mlx.core as mx
from mlx import nn


@dataclass
class MBartConfig:
    model_type: str = "mbart"
    vocab_size: int = 50265
    d_model: int = 1024
    encoder_layers: int = 12
    decoder_layers: int = 12
    encoder_attention_heads: int = 16
    decoder_attention_heads: int = 16
    decoder_ffn_dim: int = 4096
    encoder_ffn_dim: int = 4096
    activation_function: str = "gelu"
    dropout: float = 0.1
    attention_dropout: float = 0.0
    activation_dropout: float = 0.0
    classifier_dropout: float = 0.0
    max_position_embeddings: int = 1024
    init_std: float = 0.02
    encoder_layerdrop: float = 0.0
    decoder_layerdrop: float = 0.0
    scale_embedding: bool = False
    use_cache: bool = True
    forced_eos_token_id: int = 2
    pad_token_id: int = 1
    bos_token_id: int = 0
    eos_token_id: int = 2
    is_encoder_decoder: bool = True
    keys_to_ignore_at_inference: list[str] = field(
        default_factory=lambda: ["past_key_values"]
    )
    attribute_map: dict = field(
        default_factory=lambda: {
            "num_attention_heads": "encoder_attention_heads",
            "hidden_size": "d_model",
        }
    )

    def __post_init__(self):
        self.num_hidden_layers = self.encoder_layers

    @classmethod
    def from_dict(cls, params):
        return cls(**{
            k: v for k, v in params.items() if k in inspect.signature(cls).parameters
        })


class MBartAttention(nn.Module):
    def __init__(self, config: MBartConfig):
        super().__init__()
        self.num_heads = config.encoder_attention_heads
        self.embed_dim = config.d_model
        self.head_dim = self.embed_dim // self.num_heads
        self.scaling = self.head_dim**-0.5
        self.k_proj = nn.Linear(self.embed_dim, self.embed_dim, bias=True)
        self.v_proj = nn.Linear(self.embed_dim, self.embed_dim, bias=True)
        self.q_proj = nn.Linear(self.embed_dim, self.embed_dim, bias=True)
        self.out_proj = nn.Linear(self.embed_dim, self.embed_dim, bias=True)

    def _shape(self, proj: mx.array, seq_len: int, bsz: int):
        # hardcode as bs=1, seqlen=1
        return proj.reshape(bsz, seq_len, self.num_heads, self.head_dim).transpose(
            0, 2, 1, 3
        )

    def __call__(
        self,
        hidden_states: mx.array,
        past_key_value: list[list[mx.array]] | None = None,
        encoder_hidden_states: mx.array | None = None,
    ) -> tuple[mx.array, list[list[mx.array]]]:
        is_cross_attention = encoder_hidden_states is not None

        bsz, tgt_len, _ = hidden_states.shape

        # get query proj
        query_states = self.q_proj(hidden_states)
        # get key, value proj
        # `past_key_value[0].shape[2] == key_value_states.shape[1]`
        # is checking that the `sequence_length` of the `past_key_value` is the same as
        # the provided `key_value_states` to support prefix tuning
        if (
            is_cross_attention
            and past_key_value is not None
            and past_key_value[0].shape[2] == encoder_hidden_states.shape[1]
        ):
            # reuse k,v, cross_attentions
            key_states = past_key_value[0]
            value_states = past_key_value[1]
        elif is_cross_attention:
            # cross_attentions
            key_states = self._shape(self.k_proj(encoder_hidden_states), -1, bsz)
            value_states = self._shape(self.v_proj(encoder_hidden_states), -1, bsz)
        elif past_key_value is not None:
            # reuse k, v, self_attention
            key_cache, value_cache = past_key_value
            key_states = self._shape(self.k_proj(hidden_states), -1, bsz)
            value_states = self._shape(self.v_proj(hidden_states), -1, bsz)
            key_states = mx.concatenate([key_cache, key_states], axis=2)
            value_states = mx.concatenate([value_cache, value_states], axis=2)
        else:
            # self_attention
            key_states = self._shape(self.k_proj(hidden_states), -1, bsz)
            value_states = self._shape(self.v_proj(hidden_states), -1, bsz)

        _past_key_value = (key_states, value_states)

        query_states = self._shape(query_states, tgt_len, bsz)

        attn_output = mx.fast.scaled_dot_product_attention(
            query_states, key_states, value_states, scale=self.scaling
        )

        attn_output = attn_output.transpose(0, 2, 1, 3)

        # Use the `embed_dim` from the config (stored in the class) rather than `hidden_state` because `attn_output` can be
        # partitioned across GPUs when using tensor-parallelism.
        attn_output = attn_output.reshape(bsz, tgt_len, self.embed_dim)

        attn_output = self.out_proj(attn_output)

        return attn_output, _past_key_value


class MBartDecoderLayer(nn.Module):
    def __init__(self, config: MBartConfig):
        super().__init__()
        self.embed_dim = config.d_model
        self.self_attn = MBartAttention(config)
        self.encoder_attn = MBartAttention(config)
        self.self_attn_layer_norm = nn.LayerNorm(self.embed_dim)
        self.encoder_attn_layer_norm = nn.LayerNorm(self.embed_dim)
        self.activation_fn = nn.gelu
        self.fc1 = nn.Linear(self.embed_dim, config.decoder_ffn_dim)
        self.fc2 = nn.Linear(config.decoder_ffn_dim, self.embed_dim)
        self.final_layer_norm = nn.LayerNorm(self.embed_dim)

    def __call__(
        self,
        hidden_states: mx.array,
        past_key_value: list[list[mx.array]] | None = None,
        encoder_hidden_states: mx.array | None = None,
    ) -> tuple[mx.array, list[list[mx.array]]]:
        residual = hidden_states
        hidden_states = self.self_attn_layer_norm(hidden_states)
        self_attn_past_key_value = (
            past_key_value[:2] if past_key_value is not None else None
        )

        hidden_states, present_key_value = self.self_attn(
            hidden_states=hidden_states,
            past_key_value=self_attn_past_key_value,
        )
        hidden_states = residual + hidden_states

        residual = hidden_states
        hidden_states = self.encoder_attn_layer_norm(hidden_states)
        cross_attn_past_key_value = (
            past_key_value[-2:] if past_key_value is not None else None
        )
        hidden_states, cross_attn_present_key_value = self.encoder_attn(
            hidden_states=hidden_states,
            encoder_hidden_states=encoder_hidden_states,
            past_key_value=cross_attn_past_key_value,
        )
        hidden_states = residual + hidden_states
        present_key_value += cross_attn_present_key_value
        residual = hidden_states
        hidden_states = self.final_layer_norm(hidden_states)
        hidden_states = self.activation_fn(self.fc1(hidden_states))
        hidden_states = self.fc2(hidden_states)
        hidden_states = residual + hidden_states

        return hidden_states, present_key_value


class MBartDecoder(nn.Module):
    def __init__(self, config: MBartConfig):
        super().__init__()
        self.embed_scale = math.sqrt(config.d_model)

        self.embed_tokens = nn.Embedding(config.vocab_size, config.d_model)
        self.embed_positions = nn.Embedding(
            config.max_position_embeddings + 2,
            config.d_model,
        )
        self.layers = [MBartDecoderLayer(config) for _ in range(config.decoder_layers)]
        self.layernorm_embedding = nn.LayerNorm(config.d_model)
        self.layer_norm = nn.LayerNorm(config.d_model)

    def __call__(
        self,
        input_ids: mx.array,
        past_key_value: list[list[mx.array]] | None = None,
        encoder_hidden_states: mx.array | None = None,
    ) -> tuple[mx.array, list[list[mx.array]]]:
        past_key_values_length = (
            past_key_value[0][0].shape[2] if past_key_value is not None else 0
        )
        inputs_embeds = self.embed_tokens(input_ids) * self.embed_scale
        positions = self.embed_positions(mx.array(past_key_values_length + 2))
        hidden_states = inputs_embeds + positions
        hidden_states = self.layernorm_embedding(hidden_states)

        hidden_states = hidden_states.reshape(1, 1, -1)

        if past_key_value is None:
            past_key_value = [None] * len(self.layers)

        for idx, decoder_layer in enumerate(self.layers):
            hidden_states, past_key_value[idx] = decoder_layer(
                hidden_states,
                encoder_hidden_states=encoder_hidden_states,
                past_key_value=past_key_value[idx],
            )

        hidden_states = self.layer_norm(hidden_states)

        return hidden_states, past_key_value


class MBartModel(nn.Module):
    def __init__(self, config: MBartConfig):
        super().__init__()
        self.model = MBartDecoder(config)
        self.lm_head = nn.Linear(config.d_model, config.vocab_size, bias=False)

    def __call__(
        self,
        x: mx.array,
        past_key_value: list[list[mx.array]] | None = None,
        encoder_hidden_states: mx.array | None = None,
    ) -> tuple[mx.array, list[list[mx.array]]]:
        x, past_key_value = self.model(x, past_key_value, encoder_hidden_states)
        x = self.lm_head(x)
        return x, past_key_value

    @staticmethod
    def sanitize(weights):
        sanitized_weights = {}
        for key, v in weights.items():
            if key.startswith("encoder."):
                continue
            # remove `encoder.` prefix in k
            sanitized_key = key.replace("decoder.", "")
            sanitized_weights[sanitized_key] = v
        return sanitized_weights
