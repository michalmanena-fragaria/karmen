import base64
import json

from textwrap import dedent
from server import app


class PasswordResetLink:
    variables = {}

    def subject(self):
        return "Karmen - Password reset"

    def prepare_variables(self, variables={}):
        self.variables = variables
        self.variables["pwd_reset_link"] = "%s/reset-password?reset=%s" % (
            app.config["FRONTEND_BASE_URL"],
            base64.b64encode(
                json.dumps(
                    {
                        "pwd_reset_key": variables["pwd_reset_key"],
                        "pwd_reset_key_expires": variables["pwd_reset_key_expires"],
                        "email": variables["email"],
                    }
                ).encode("utf-8")
            ).decode("utf-8"),
        )

    def textbody(self):
        return (
            dedent(
                """
            Hi!

            Someone has requested a link to change your password.

            Change your password on %s

            If you didn't request this, you can safely ignore this email and your password will not be changed.

            If you have any problems or questions, please feel free to reply directly to this email.

            © 2020 Fragaria s.r.o.
            Address …….
            Follow us on Twitter, LinkedIn or Facebook
            """
            )
            % (self.variables["pwd_reset_link"])
        )

    def htmlbody(self):
        return self.textbody()
