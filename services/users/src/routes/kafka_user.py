from fastapi_mail import MessageSchema, MessageType
from faststream.kafka.fastapi import Logger

from common.broker import kafka_router
from schema.general import WelcomeUser
from utils.fastapi.email.email_sender import fm
from utils.fastapi.utils import url_with_token


@kafka_router.subscriber("user.created")
@kafka_router.publisher("user.verification_token.created")
async def user_created_sub(message: WelcomeUser, logger: Logger) -> WelcomeUser:
	logger.info(f"Received user with username {message.user} and id {message.id}")
	logger.info(f"Sending email to user {message.user}")
	email_message = MessageSchema(
		subject="Welcome Email to Datahub",
		recipients=[message.user],
		template_body={"full_name": message.full_name},
		subtype=MessageType.html,
	)
	await fm.send_message(message=email_message, template_name="welcome_mail.html")
	return message


@kafka_router.subscriber("user.verification_token.created")
async def create_token_verification(message: WelcomeUser, logger: Logger) -> None:
	logger.info(f"Sending verification email to {message.id}")
	token = url_with_token(
		{**message.model_dump(exclude={"id"}),"id": str(message.id)}
	)
	link = f"localhost/users/auth/verify-email?token={token}"
	email_message = MessageSchema(
		subject="Verification email",
		recipients=[message.user],
		template_body={"verification_link": link, "expires_in": 60},
		subtype=MessageType.html,
	)
	await fm.send_message(
		message=email_message, template_name="email_verification.html"
	)
