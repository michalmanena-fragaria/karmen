from server.services.mailer.mailers.dummy import Dummy
from server.services.mailer.mailers.mailgun import Mailgun


def get_mailer(key):
    mapping = {
        "DUMMY": Dummy,
        "MAILGUN": Mailgun,
    }
    if key.upper() in mapping:
        return mapping[key.upper()]()

    raise RuntimeError("Unknown mailer %s" % key)