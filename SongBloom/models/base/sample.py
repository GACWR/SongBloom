import torch


def multinomial(input: torch.Tensor, num_samples: int, replacement=False, *, generator=None):
    """torch.multinomial with arbitrary number of dimensions, and number of candidates on the last dimension.

    Args:
        input (torch.Tensor): The input tensor containing probabilities.
        num_samples (int): Number of samples to draw.
        replacement (bool): Whether to draw with replacement or not.
    Keywords args:
        generator (torch.Generator): A pseudorandom number generator for sampling.
    Returns:
        torch.Tensor: Last dimension contains num_samples indices
            sampled from the multinomial probability distribution
            located in the last dimension of tensor input.
    """
    input_ = input.reshape(-1, input.shape[-1])
    output_ = torch.multinomial(input_, num_samples=num_samples, replacement=replacement, generator=generator)
    output = output_.reshape(*list(input.shape[:-1]), -1)
    return output


def sample_top_k(probs: torch.Tensor, k: int) -> torch.Tensor:
    """Sample next token from top K values along the last dimension of the input probs tensor.

    Args:
        probs (torch.Tensor): Input probabilities with token candidates on the last dimension.
        k (int): The k in “top-k”.
    Returns:
        torch.Tensor: Sampled tokens.
    """
    top_k_value, _ = torch.topk(probs, k, dim=-1)
    min_value_top_k = top_k_value[..., [-1]]
    probs *= (probs >= min_value_top_k).float()
    probs.div_(probs.sum(dim=-1, keepdim=True))
    next_token = multinomial(probs, num_samples=1)
    return next_token


def sample_top_p(probs: torch.Tensor, p: float) -> torch.Tensor:
    """Sample next token from top P probabilities along the last dimension of the input probs tensor.

    Args:
        probs (torch.Tensor): Input probabilities with token candidates on the last dimension.
        p (int): The p in “top-p”.
    Returns:
        torch.Tensor: Sampled tokens.
    """
    probs_sort, probs_idx = torch.sort(probs, dim=-1, descending=True)
    probs_sum = torch.cumsum(probs_sort, dim=-1)
    mask = probs_sum - probs_sort > p
    probs_sort *= (~mask).float()
    probs_sort.div_(probs_sort.sum(dim=-1, keepdim=True))
    next_token = multinomial(probs_sort, num_samples=1)
    next_token = torch.gather(probs_idx, -1, next_token)
    return next_token
