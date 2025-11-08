from fastapi import Depends
from strawberry.fastapi import BaseContext


class CustomContext(BaseContext):
    def __init__(self, greeting: str, name: str):
        self.greeting = greeting
        self.name = name


async def custom_context_dependency() -> CustomContext:
    return CustomContext(greeting="you rock!", name="John")


async def get_context(
    custom_context=Depends(custom_context_dependency),
):
    return custom_context
