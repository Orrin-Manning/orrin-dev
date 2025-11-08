import strawberry

from .mutations.flavor import FlavorMutation


@strawberry.type
class Query:
    @strawberry.field
    def example(self, info: strawberry.Info) -> str:
        return f"{info.context.name} {info.context.greeting}"


@strawberry.type
class Mutation(FlavorMutation):
    pass


schema = strawberry.Schema(Query, Mutation)
