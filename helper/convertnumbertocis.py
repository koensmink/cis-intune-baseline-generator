def cis_format(n: str) -> str:
    if len(n) <= 3:
        return ".".join(n)
    return f"{n[0]}.{n[1]}.{n[2]}.{n[3:]}"
