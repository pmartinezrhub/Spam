from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from os.path import basename
from smtplib import SMTP_SSL as SMTP 


class Spam():
    
    def __init__ (self, from_addr, to_addr, subject, username, password, smtp_host, smtp_port, text_subtype, msg_file, attachment=None):
        self.from_addr = from_addr
        self.to_addr = to_addr
        self.username = username 
        self.password = password
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.subject = subject
        # typical values for text_subtype are plain, html, xml
        self.text_subtype = text_subtype
        self.msg_file = msg_file
        self.attachment = attachment
        
    def connect_smtp(self):
        try:
            self.conn_smtp.set_debuglevel(True)
            self.conn_smtp.login(self.username, self.password)
        except Exception as e:
            print(e)
        
    def send_email(self):
        msg = MIMEMultipart()
        bm = open(self.msg_file, 'r')
        body_message = bm.read()
        msg.attach(MIMEText(body_message, self.text_subtype))
        msg['Subject'] = self.subject
        msg['From'] = self.from_addr 
        if self.attachment is not None:
            with open(self.attachment, 'r') as f:
                part = MIMEApplication(f.read(), Name=basename(self.attachment))
            part['Content-Disposition'] = 'attachment; filename="{}"'.format(basename(self.attachment))
            msg.attach(part)
            
        try:
            conn_smtp = SMTP(self.smtp_host, self.smtp_port)
            conn_smtp.login(self.username, self.password)
            conn_smtp.set_debuglevel(False)
            conn_smtp.sendmail(self.from_addr, self.to_addr, msg.as_string())
        except Exception as e:
            print(e)
            return False
        except (conn_smtp.SMTPConnectError):
            print("Error connecting")
        except AttributeError:
            return False
        except UnboundLocalError:
            pass
        finally:
            conn_smtp.quit()
            pass
            return False
        return True
            