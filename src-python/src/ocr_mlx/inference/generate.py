from typing import Any

import mlx.core as mx

from ocr_mlx.model.nougat import Nougat


def apply_repetition_penalty(logits: mx.array, generated_tokens: Any, penalty: float):
    if len(generated_tokens) > 0:
        indices = mx.array(list(generated_tokens))
        selected_logits = logits[:, indices]
        selected_logits = mx.where(
            selected_logits < 0, selected_logits * penalty, selected_logits / penalty
        )
        logits[:, indices] = selected_logits
    return logits


def top_p_sampling(logits: mx.array, top_p: float, temperature: float) -> mx.array:
    probs = mx.softmax(logits / temperature, axis=-1)

    sorted_indices = mx.argsort(probs, axis=-1)
    sorted_probs = probs[..., sorted_indices.squeeze(0)]

    cumulative_probs = mx.cumsum(sorted_probs, axis=-1)

    top_probs = mx.where(
        cumulative_probs > 1 - top_p,
        sorted_probs,
        mx.zeros_like(sorted_probs),
    )

    sorted_token = mx.random.categorical(mx.log(top_probs))
    return sorted_indices.squeeze(0)[sorted_token]


def sample(logits: mx.array, temperature: float = 0.0, top_p: float = 0.0) -> mx.array:
    if temperature == 0:
        return mx.argmax(logits, axis=-1)
    return (
        top_p_sampling(logits, top_p, temperature)
        if top_p > 0 and top_p < 1
        else mx.random.categorical(logits * (1 / temperature))
    )


def generate(
    model: Nougat,
    pixel_values: mx.array,
    max_new_tokens: int = 4096,
    eos_token_id: int = 2,
    temperature: float = 0.0,
    top_p: float = 0.0,
    repetition_penalty: float | None = None,
    repetition_context_size: int = 10,
):
    encoder_hidden_states = model.encoder(pixel_values)
    new_token = mx.array([0])
    outputs = []
    cache = None
    repetition_context = []
    if repetition_context_size:
        repetition_context = repetition_context[-repetition_context_size:]

    for _ in range(max_new_tokens):
        logits, cache = model.decoder(new_token, cache, encoder_hidden_states)
        logits = logits[:, -1, :]

        if repetition_penalty:
            logits = apply_repetition_penalty(
                logits, repetition_context, repetition_penalty
            )

        new_token = sample(logits, temperature, top_p)

        if repetition_penalty:
            repetition_context.append(new_token.item())

        if new_token == eos_token_id:
            break
        outputs.append(new_token.item())
    return outputs
