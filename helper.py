import smtplib
from dynaconf import settings

from contextlib import contextmanager


class Helper:
    @contextmanager
    def smtp_client(self):
        # set up the SMTP server
        smtp_client = smtplib.SMTP(host=settings.SMTP.host, port=settings.SMTP.port)
        smtp_client.starttls()
        smtp_client.login(settings.SMTP.address, settings.SMTP.password)

        yield smtp_client
        smtp_client.quit()
