import os
import smtplib

from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Union
from piscis.config.global_config import global_config
import requests


class SendEmailHandler:
    def __init__(self, email_to: Union[list, str], email_from: str = None, email_cc: list = None,
                 email_bcc: list = None):
        """
        :param email_from: 发送者
        :param email_to: 接受者 []
        :param email_cc: 抄送
        :param email_bcc: 暗抄送 两者的区别在于在BCC栏中的收件人可以看到所有的收件人名(TO,CC,BCC)，而在TO 和CC栏中的收件人看不到BBC的收件人名
        """
        self.email_from = email_from if email_from else "no-reply@17zuoye.com"

        if isinstance(email_to, str):
            email_to = [email_to]
        self.email_to = email_to
        self.email_cc = email_cc
        self.email_bcc = email_bcc

        self.subject_pre = f"【{global_config.mail_subject}】({os.environ.get('stage', 'development')})"

    @staticmethod
    def generate_file_part_by_content(file_content, filename, content_type):
        """生成附件部分"""
        part = MIMEText(file_content, "base64", _charset="utf-8")
        part["Content-Type"] = content_type
        part.add_header("Content-Disposition", "attachment", filename=filename)
        return part

    @staticmethod
    def generate_file_part_by_filename(filename):
        if "http" in filename:
            r = requests.get(filename)
            part = MIMEApplication(r.content)
            file_name = filename
        else:
            part = MIMEApplication(open(filename, "rb").read())
            att_names = filename.split("/")
            file_name = att_names[-1] if att_names else filename
        part.add_header("Content-Disposition", "attachment", filename=file_name)
        return part

    def send_email(self, subject: str, content: str, attachments: list[MIMEApplication] = None, subtype: str = "html"):
        """
        :param subject: 邮件主题
        :param content: 邮件正文
        :param attachments: 附件
        """
        msg = MIMEMultipart()
        msg["Subject"] = self.subject_pre + subject
        msg["From"] = self.email_from
        msg["To"] = ";".join(self.email_to)

        if self.email_cc:
            msg["Cc"] = ";".join(set(self.email_cc) - set(self.email_to))

        if self.email_bcc:
            msg["Bcc"] = ";".join(set(self.email_bcc) - set(self.email_to) - set(self.email_cc or []))

        # 创建一个邮件正文内容
        body = MIMEText(content, _subtype=subtype, _charset="utf-8")
        msg.attach(body)

        # 添加附件
        if attachments:
            for part in attachments:
                msg.attach(part)

        try:
            smtp = smtplib.SMTP()
            smtp.connect("smtp.dc.17zuoye.net")
            smtp.sendmail(
                self.email_from,
                list(set(self.email_to) | set(self.email_cc or []) | set(self.email_bcc or [])),
                msg.as_string(),
            )
            smtp.quit()
        except Exception as exc:
            return False, str(exc)

        return True, ""
