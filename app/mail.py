from flask_mail import Message
from flask import render_template, current_app
from settings import Config
from .exetensions import mail
from threading import Thread


def send_async_mail(app, msg):
    with app.app_context():
        mail.send(msg)


def send_mail(to, subject, template, **kwargs):
    # kwargs['token'] = str(kwargs['token'])
    user = kwargs.get('user')
    token = kwargs.get('token').decode('utf-8')
    app = current_app._get_current_object()
    msg = Message(Config.MAIL_SUBJECT_PREFIX + ' ' + subject,
                  sender=Config.MAIL_SENDER,
                  recipients=[to])
    msg.body = render_template(template + '.txt', user=user, token=token)
    msg.html = render_template(template + '.html', user=user, token=token)
    thr = Thread(target=send_async_mail, args=[app, msg])
    thr.start()
    return thr
