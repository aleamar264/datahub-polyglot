from fastapi_mail import MessageSchema, MessageType
from faststream.kafka.fastapi import Logger

from common.broker import kafka_router
from schema.general import ResponseCreationUser
from utils.fastapi.utils import url_with_token
from utils.fastapi.email.email_sender import fm


@kafka_router.subscriber("user.created")
@kafka_router.publisher("user.verification_token.created")
async def user_created_sub(
	message: ResponseCreationUser, logger: Logger
) -> None:
	logger.info(f"Received user with username {message.user} and id {message.id}")
	logger.info(f"Sending email to user {message.user}")
	email_message = MessageSchema(
		subject="Welcome Email to Datahub",
		recipients=[message.user],
		template_body={},
		subtype=MessageType.html,
	)
	await fm.send_message(message=email_message, html_template="welcome_mail.html")


@kafka_router.subscriber("user.verification_token.created")
async def create_token_verification(
	message: ResponseCreationUser, logger: Logger
) -> None:
	token = url_with_token(message.user)
