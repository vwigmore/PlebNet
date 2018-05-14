# TODO: deze ook weghalen: eigen implementatie van config gebruiken?
import json
import smtplib

from cloudomate.util.settings import Settings as UserOptions

from plebnet.agent.dna import DNA


def test_mail():
    user_options = UserOptions()
    user_options.read_settings()
    send_mail("Hello world.", user_options.get('user', 'firstname') + ' ' + user_options.get('user', 'lastname'))


def send_child_creation_mail(ip, rootpw, success, config, user_options, transaction_hash):
    mail_message = 'IP: %s\n' % ip
    mail_message += 'Root password: %s\n' % rootpw
    mail_message += 'Success: %s\n' % success
    mail_message += 'Transaction_hash: %s\n' % transaction_hash
    mail_dna = DNA()
    mail_dna.read_dictionary()
    mail_message += '\nDNA\n%s\n' % json.dumps(mail_dna.dictionary)
    mail_message += '\nConfig\n%s\n' % json.dumps(config.config)
    send_mail(mail_message, user_options.get('firstname') + ' ' + user_options.get('lastname'))


def send_mail(mail_message, name):
    sender = 'authentic8989+' + name + '@gmail.com'
    receivers = ['authentic8989+' + name + '@gmail.com']
    mail = """From:""" + name + """<""" + sender + """>
To: """ + name + """ <authentic8989+""" + name + """@gmail.com'>
Subject: New child spawned

"""
    mail += mail_message

    try:
        print("Sending mail: %s" + mail)
        smtp = smtplib.SMTP('gmail-smtp-in.l.google.com:25')
        smtp.helo()
        smtp.set_debuglevel(1)
        #smtp.starttls()
        smtp.sendmail(sender, receivers, mail)
        print("Successfully sent email")
    except smtplib.SMTPException as e:
        print("Error: unable to send email \n\n%s"% repr(e))
