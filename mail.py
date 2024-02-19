import win32com.client

def send_mail(mail_address, repair_number, last_name, price, reminder=False):
    """
    Verzendt een e-mail met de reparatiestatus naar het opgegeven
    e-mailadres.
    :param mail_address: Het e-mailadres van de ontvanger.
    :param repair_number: Het reparatienummer van de reparatie.
    :param last_name: De achternaam van de klant.
    :param price: De prijs van de reparatie.
    """
    with open("static/mail/mail.txt", "r", encoding="utf-8") as file:
        mail_template = file.read()
    outlook = win32com.client.Dispatch('outlook.application')
    mail = outlook.CreateItem(0)
    mail.To = mail_address
    if reminder:
        mail.Subject = "Reparatiestatus J22 heringeren"
        mail.body = mail_template.format(last_name, repair_number, price)
    else:
        mail.Subject = "Reparatiestatus J22"
        mail.body = mail_template.format(last_name, repair_number, price)
    mail.Send()



if __name__ == '__main__':
    send_mail("jaimymohammadi@live.nl", 1223, "Mohammadi", 43)
