class Link:
    def __init__(self, name: str, url: str):
        self.name = name
        self.url = url

    def __str__(self):
        return self.url

    @property
    def markdown(self):
        return f"[{self.name}]({self.url})"
