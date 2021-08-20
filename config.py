def get_token(path):
    with open(path=path, mode="r") as f:
        return f.read()