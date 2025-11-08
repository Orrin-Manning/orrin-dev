import strawberry


async def notify_new_flavor(name: str):
    print(name)


@strawberry.type
class FlavorMutation:
    @strawberry.mutation
    def create_flavor(self, name: str, info: strawberry.Info) -> bool:
        info.context["background_tasks"].add_task(notify_new_flavor, name)
        return True
