from pydantic_settings import BaseSettings


class RabbitSettings(BaseSettings):
    mq_host: str = "localhost"
    mq_username: str = "guest"
    mq_password: str = "guest"
    queue: str = "merchant_data"
    update_queue: str = "merchant_offer_update"


rabbit_settings = RabbitSettings()
