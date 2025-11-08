import strawberry


@strawberry.type
class HelloQueries:
    @strawberry.field
    def hello(self, info: strawberry.Info) -> str:
        return "Hello World"
