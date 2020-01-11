import toml
import os
import smtplib

from contextlib import contextmanager


class Helper:
    @staticmethod
    def get_config():
        instance_path = os.path.abspath(os.path.dirname(__file__))
        config_file = os.path.join(instance_path, 'configs/production.toml')

        return toml.load(config_file)

    @contextmanager
    def smtp_client(self):
        config = self.get_config()

        # set up the SMTP server
        smtp_client = smtplib.SMTP(
            host=config['smtp']['host'], port=config['smtp']['port']
        )
        smtp_client.starttls()
        smtp_client.login(config['smtp']['address'], config['smtp']['password'])

        yield smtp_client
        smtp_client.quit()
