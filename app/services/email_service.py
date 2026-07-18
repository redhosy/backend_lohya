from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from app.core.config import settings
from app.core.logging import logger


def get_mail_config() -> ConnectionConfig:
    return ConnectionConfig(
        MAIL_USERNAME=settings.MAIL_USERNAME,
        MAIL_PASSWORD=settings.MAIL_PASSWORD,
        MAIL_FROM=settings.MAIL_USERNAME,
        MAIL_SERVER=settings.MAIL_SERVER,
        MAIL_PORT=settings.MAIL_PORT,
        MAIL_STARTTLS=True,
        MAIL_SSL_TLS=False,
        USE_CREDENTIALS=True,
    )


async def kirim_otp_email(email: str, otp: str):
    if not settings.MAIL_USERNAME or not settings.MAIL_PASSWORD:
        logger.warning(f"Email tidak dikonfigurasi. OTP untuk {email}: {otp}")
        return

    try:
        conf = get_mail_config()
        message = MessageSchema(
            subject="Verifikasi Akun Pantau Cabai",
            recipients=[email],
            body=f"Kode OTP Anda:\n\n{otp}\n\nBerlaku selama 5 menit.",
            subtype="plain",
        )

        fm = FastMail(conf)
        await fm.send_message(message)
        logger.info(f"OTP berhasil dikirim ke {email}")
    except Exception as e:
        logger.error(f"Gagal kirim email ke {email}: {str(e)}")
