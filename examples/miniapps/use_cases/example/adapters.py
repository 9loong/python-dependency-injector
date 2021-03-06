"""Example adapters package."""


class EmailSender:
    """Abstract email sender."""

    def send(self, to, body):
        """Send email to specified email."""
        raise NotImplementedError()


class SmtpEmailSender:
    """SMTP email sender uses SMTP protocol for sending emails."""

    def send(self, to, body):
        """Send email to specified email."""
        # Send email via SMTP


class EchoEmailSender:
    """Echo email sender prints emails to stdout."""

    def send(self, to, body):
        """Send email to specified email."""
        print('Sending email to "{0}", body = "{1}"'.format(to, body))
