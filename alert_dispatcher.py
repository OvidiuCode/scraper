from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.header import Header
from email.utils import formataddr

from models.alert import Alert
from models.product import Product

from helper import Helper


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
        with self.smtp_client() as smtp_client:
            for alert in alerts:
                alert_ids.append(alert.id)
                await self.process_alert(alert, smtp_client)

        if alert_ids:
            Alert.update(satisfied=True).where(Alert.id.in_(alert_ids)).execute()

    async def process_alert(self, alert, smtp_client):
        msg = MIMEMultipart()

        config = self.get_config()
        message = config['email']['message'].format(
            produs=alert.product_title,
            pret=float(alert.product_price),
            link=alert.product_link,
        )

        from_addr = str(Header(config['smtp']['from_name'], 'utf-8'))
        msg['From'] = formataddr((from_addr, config['smtp']['address']))
        msg['To'] = alert.email
        msg['Subject'] = config['email']['subject']

        msg.attach(MIMEText(message, 'plain'))

        smtp_client.send_message(msg)
        del msg
