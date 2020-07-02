from datetime import datetime, timedelta

import logging
import sendgrid
from sendgrid.helpers import mail
from models.alert import Alert
from models.product import Product

from helper import Helper
from dynaconf import settings


class AlertDispatcher(Helper):
    ALERT_DAYS_DELTA = 365

    async def work(self):
        alert_delta = datetime.now() - timedelta(days=self.ALERT_DAYS_DELTA)
        alerts = (
            Alert.select(
                Alert.id,
                Alert.email,
                Product.title.alias('product_title'),
                Product.link.alias('product_link'),
                Product.price.alias('product_price'),
            )
            .join(Product)
            .where(
                Product.price <= Alert.price,
                Alert.created_at > alert_delta,
                ~Alert.satisfied,
            )
            .distinct(Product.product_id)
            .objects()
        )

        alert_ids = []
        for alert in alerts:
            alert_ids.append(alert.id)
            await self.process_alert(alert)

        if alert_ids:
            Alert.update(satisfied=True).where(Alert.id.in_(alert_ids)).execute()

    async def process_alert(self, alert):
        message = settings.EMAIL.message.format(
            produs=alert.product_title,
            pret=float(alert.product_price),
            link=alert.product_link,
        )

        sg = sendgrid.SendGridAPIClient(settings.SMTP.password)
        sgmail = mail.Mail(
            from_email=mail.Email(
                email=settings.SMTP.address, name=settings.SMTP.from_name
            ),
            to_emails=alert.email,
            subject=settings.EMAIL.subject,
            html_content=message,
        )

        try:
            response = sg.send(sgmail)
        except Exception as exc:
            logging.exception(exc)
            if getattr(exc, "read", None):
                logging.error(exc.read())
            if getattr(exc, "body", None):
                logging.error(exc.body)
        else:
            if response.status_code != 202:
                raise Exception(f"An error occurred: {response.body}")
