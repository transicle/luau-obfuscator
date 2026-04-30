import random


_CHARS = "IlJjfFtT"
_REST  = "Il1JjfFtT7"


def random_name(rand: random.Random = None, min_len: int = 13, max_len: int = 21) -> str:
    if rand is None:
        rand = random.SystemRandom()
    return rand.choice(_CHARS) + "".join(
        rand.choice(_REST) for _ in range(rand.randint(min_len, max_len))
    )
