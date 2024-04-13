"""Library contains some end-user classes for mailing.

Typical use of library could be check, if input email is correct, and send
email by Smtp class.

>>> from falias.smtp import Smtp, Email
>>> smtp = Smtp('smtp://localhost/no-replay@domain.xy')
>>> recipient = get_recipient()     # as get_recipient is your function
>>> if Email.check(recipient):
>>>     try:
>>>         smtp.send_email('Subject', recipient, 'Mail body')
>>>     except SMTPException as e:
>>>         print('Something wrong: %s' % e)
"""

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import re
from smtplib import SMTP, SMTPException
from time import localtime, strftime

# Data Source Name regular expression for smtp server
re_dsn = re.compile(r"""smtp://          # driver
                                ((?P<user>[\w\.@\-]+)?
                                (:(?P<passwd>[\w\.\@\!\?\#]+))?@)?
                                (?P<host>[\w\.]+)?
                                (:(?P<port>[0-9]+))?
                                /(?P<sender>[\w\.\-]+@[\w\.\-]+)?
                                (::(?P<charset>\w+))?
                    """, re.X)
# smtp://localhost/mcbig@localhost


class Smtp:
    """Class for smtp 'connection'.

    In fact, class parse Data Source Name for smtp and not do connection at
    initialization process. But send_* methods do that.
    """
    def __init__(self, dsn):
        """Raise RuntimeError when dsn is not valid.

        Data Source Name for smtp looks like: smtp://localhost/mcbig@localhost
        """
        match = re_dsn.match(dsn)
        if not match:
            raise RuntimeError(f"Bad SMTP Data Source Name `{dsn}`")

        self.host = match.group("host") or "localhost"
        self.port = int(match.group("port") or 25)
        self.sender = match.group("sender") or ""
        self.charset = match.group("charset") or "utf-8"
        self.user = match.group("user") or None
        self.passwd = match.group("passwd") or None

        self.xmailer = "Falias (http://falias.zeropage.cz)"

    def __str__(self):
        """Return Data Source Name of set values."""
        return "smtp://%s%s%s%s:%d/%s::%s" % \
            (self.user or "", self.passwd or "",
             "@" if self.user or self.passwd else "",
             self.host, self.port,
             self.sender, self.charset)

    def send_email_txt(self, subject, recipient, body, logger=None, **kwargs):
        """Send email as text/plain content type.

        Keyword arguments:
            - `logger` loging function, it will be called when is set.
            - `sender` default sender is set by Data Source Name
            - `reply` Reply-To header
            - `xmailer` X-Mailer header, default is Falias
        """
        msg = MIMEText(body)
        msg.set_charset(self.charset)
        msg["Subject"] = subject
        msg["From"] = kwargs.get("sender", self.sender)
        msg["To"] = recipient
        msg["Date"] = strftime("%a, %d %b %Y %X %z", localtime())

        # headers
        if "reply" in kwargs:
            msg["Reply-To"] = kwargs["reply"]

        msg["X-Mailer"] = kwargs.get("xmailer", self.xmailer)

        if logger:
            logger("SMTP: \33[0;32mSub:%s, From:%s, To:%s\33[0m" %
                   (msg["Subject"], msg["From"], msg["To"]))

        smtp = SMTP()
        try:
            smtp.connect(self.host, self.port)

            if self.user:
                smtp.login(self.user, self.passwd)
        except SMTPException as e:
            smtp.close()
            if logger:
                logger("SMTP: \33[3;33mConnection failed\33[0m %s" % str(e))
            raise

        try:
            smtp.sendmail(msg["From"], msg["To"], msg.as_string())
        except SMTPException as e:
            if logger:
                logger("SMTP: \33[3;33mSendig email failed\33[0m %s" % str(e))
            raise
        finally:
            smtp.close()

    def send_email_alternative(self, subject, recipient, txt_body,  html_body,
                               logger=None, **kwargs):
        """Send email as text/html with alternative plain/text content.

        Keyword arguments:
            - `logger` loging function, it will be called when is set.
            - `sender` default sender is set by Data Source Name
            - `reply` Reply-To header
            - `xmailer` X-Mailer header, default is Falias
        """
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = kwargs.get("sender", self.sender)
        msg["To"] = recipient
        msg["Date"] = strftime("%a, %d %b %Y %X %z", localtime())

        # headers
        if "reply" in kwargs:
            msg["Reply-To"] = kwargs["reply"]
        msg["X-Mailer"] = kwargs.get("xmailer", self.xmailer)

        # body
        part1 = MIMEText(txt_body, "plain")
        part1.set_charset(self.charset)
        part2 = MIMEText(html_body, "html")
        part2.set_charset(self.charset)

        msg.attach(part1)
        msg.attach(part2)

        if logger:
            logger("SMTP: \33[0;32mSub:%s, From:%s, To:%s\33[0m" %
                   (msg["Subject"], msg["From"], msg["To"]))

        smtp = SMTP()
        try:
            smtp.connect(self.host, self.port)

            if self.user:
                smtp.login(self.user, self.passwd)
        except SMTPException as e:
            smtp.close()
            if logger:
                logger("SMTP: \33[3;33mConnection failed\33[0m %s" % str(e))
            raise

        try:
            smtp.sendmail(msg["From"], msg["To"], msg.as_string())
        except SMTPException as e:
            if logger:
                logger("SMTP: \33[3;33mSendig email failed\33[0m %s" % str(e))
            raise
        finally:
            smtp.close()


# Regular expression for check valid email address
re_email = re.compile(r"^[\w\.\-]+@[\w\.\-]+$")


class Email:
    """Class for automatic checking email address."""
    def __init__(self, value):
        if not Email.check(value):
            raise RuntimeError("{value} not match as email")
        self.value = value

    def __str__(self):
        return self.value

    @staticmethod
    def check(value):
        """Return True if value could be valid email address."""
        return bool(re_email.match(value))
