class CategoryNotFoundError(Exception):
    def __init__(self, missing_slugs: list[str]):
        self.missing_slugs = missing_slugs
        super().__init__(f"Unknown categories: {missing_slugs}")


class CategoryAlreadyExistsError(Exception):
    def __init__(self, field: str, value: str):
        self.field = field
        self.value = value
        super().__init__(f"Category with {field} '{value}' already exists")
