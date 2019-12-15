from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.header import Header
from email.utils import formataddr

from models.alert import Alert
from models.product import Product
from models.database import OBJ_MANAGER

from . import smtp_client, config


class AlertDispatcher:
    ALERT_DAYS_DELTA = 365

    async def work(self):
        alert_delta = datetime.now() - timedelta(days=self.ALERT_DAYS_DELTA)
        alerts = await OBJ_MANAGER.execute(
            Alert.select(
                Alert.email,
                Product.title.alias('product_title'),
                Product.link.aliast('product_link'),
                Product.price.aliast('product_price'),
            )
            .join(Product)
            .where(
                Product.price <= Alert.price,
                Alert.created_at > alert_delta,
                ~Alert.satisfied,
            )
            .naive()
        )

        for alert in alerts:
            await self.process_alert(alert)

        await OBJ_MANAGER.execute(
            Alert.update(satisfied=True).where(Alert.id.in_(alerts))
        )

    @staticmethod
    async def process_alert(alert):
        msg = MIMEMultipart()

        message = config['email']['message'].format(
            produs=alert.product_title,
            pret=alert.product_price,
            link=alert.product_link,
        )

        from_addr = str(Header(config['smtp']['from_name'], 'utf-8'))
        msg['From'] = formataddr(from_addr, config['smtp']['address'])
        msg['To'] = alert.email
        msg['Subject'] = config['email']['subject']

        msg.attach(MIMEText(message, 'plain'))

        smtp_client.send_message(msg)
        del msg
