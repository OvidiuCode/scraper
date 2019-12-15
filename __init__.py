import toml
import os
import smtplib

instance_path = os.path.abspath(os.path.dirname(__file__))
config_file = os.path.join(instance_path, 'configs/production.toml')

config = toml.load(config_file)

smtp_client = None
if config.get('smtp'):
    # set up the SMTP server
    try:
        smtp_client = smtplib.SMTP(host=config['smtp']['host'])
        smtp_client.starttls()
        smtp_client.login(config['smtp']['address'], config['smtp']['password'])
    except Exception:
        pass
