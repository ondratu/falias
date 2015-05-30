
from email.MIMEText import MIMEText
from smtplib import SMTP, SMTPException

import re

# smtp://localhost/mcbig@localhost
re_dsn = re.compile("""smtp://          # driver
                                ((?P<user>[\w\.]+)?
                                (:(?P<passwd>[\w\.]+))?@)?
                                (?P<host>[\w\.]+)?
                                (:(?P<port>[0-9]+))?
                                /(?P<sender>[\w\.\-]+@[\w\.\-]+)?
                                (::(?P<charset>\w+))?
                    """, re.X)

class Smtp:
    def __init__(self, dsn):
        match = re_dsn.match(dsn)
        if not match:
            raise RuntimeError("Bad SMTP Data Source Name `%s`", dsn)

        self.host   = match.group('host') or "localhost"
        self.port   = int(match.group('port') or 25)
        self.sender = match.group('sender') or ''
        self.charset= match.group('charset') or 'utf-8'
        self.user   = match.group('user') or None
        self.passwd = match.group('passwd') or None

        self.xmailer = 'Falias (http://falias.zeropage.cz)'
    #enddef

    def __str__(self):
        return "smtp://%s%s%s%s:%d/%s::%s" % \
                (self.user or '', self.passwd or '',
                 '@' if self.user or self.passwd else '', self.host, self.port,
                 self.sender, self.charset)


    def send_email_txt(self, subject, recipient, body, logger = None, **kwargs):
        msg = MIMEText(body)

        msg.set_charset(self.charset)
        msg['Subject']  = subject
        msg['From']     = kwargs['sender'] if 'sender' in kwargs else self.sender
        msg['To']       = recipient

        # headers
        if 'reply' in kwargs:
            msg['Reply-To'] = kwargs['reply']
        if 'xmailer' in kwargs:
            msg['X-Mailer'] = kwargs['xmailer']
        elif self.xmailer:
            msg['X-Mailer'] = self.xmailer

        if not logger is None:
            logger("SMTP: \33[0;32mSub:%s, From:%s, To:%s\33[0m" % \
                            (msg['Subject'], msg['From'], msg['To']))

        smtp = SMTP()
        try:
            smtp.connect(self.host, self.port)

            print self.user, self.passwd
            if not self.user is None:
                smtp.login(self.user, self.passwd)
        except SMTPException as e:
            smtp.close()
            if not logger is None:
                logger("SMTP: \33[3;33mConnection failed\33[0m %s" % str(e))
            raise e

        try:
            rv = smtp.sendmail(msg['From'], msg['To'], msg.as_string())
        except SMTPException as e:
            if not logger is None:
                logger("SMTP: \33[3;33mSendig email failed\33[0m %s" % str(e))
            raise e
        finally:
            smtp.close()
    #enddef

#endclass


re_email = re.compile("^[\w\.\-]+@[\w\.\-]+$")

class Email:
    def __init__(self, value):
        if not Email.check(value):
            raise RuntimeError("%s not match as email" % value)
        self.value = value

    def __str__(self):
        return self.value

    @staticmethod
    def check(value):
        return True if re_email.match(value) else False
#enddef
