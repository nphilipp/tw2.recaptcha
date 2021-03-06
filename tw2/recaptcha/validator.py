from formencode.validators import FancyValidator
from formencode import Invalid
import urllib
if not hasattr(urllib, 'parse'):
    import urlparse
    urllib.parse = urlparse
    urllib.parse.urlencode = urllib.urlencode
    del urlparse
if not hasattr(urllib, 'request'):
    import urllib2
    urllib.request = urllib2
    del urllib2

from pylons.i18n import N_

class ReCaptchaValidator(FancyValidator):
    """
    @see formencode.validators.FieldsMatch
    """

    messages = {
        'incorrect': N_("Incorrect value."),
        'missing':  N_("Missing value."),
    }

    verify_server           = "www.google.com"
    __unpackargs__ = ('*', 'field_names')

    validate_partial_form   = True
    validate_partial_python = None
    validate_partial_other = None

    def __init__(self, private_key, remote_ip, *args, **kw):
        super(ReCaptchaValidator, self).__init__(args, kw)
        self.private_key = private_key
        self.remote_ip = remote_ip
        self.field_names = ['recaptcha_challenge_field',
                            'recaptcha_response_field']

    def validate_partial(self, field_dict, state):
        for name in self.field_names:
            if name not in field_dict:
                return
        self.validate_python(field_dict, state)

    def validate_python(self, field_dict, state):
        challenge = field_dict['recaptcha_challenge_field']
        response = field_dict['recaptcha_response_field']
        if response == '' or challenge == '':
            error = Invalid(self.message('missing', state), field_dict, state)
            error.error_dict = {'recaptcha_response_field':'Missing value'}
            raise error
        params = urllib.parse.urlencode({
            'privatekey': self.private_key,
            'remoteip' : self.remote_ip,
            'challenge': challenge,
            'response' : response,
            })
        request = urllib.request.Request(
            url = "https://%s/recaptcha/api/verify" % self.verify_server,
            data = params,
            headers = {"Content-type": "application/x-www-form-urlencoded",
                       "User-agent": "reCAPTCHA Python"
                      }
            )

        httpresp = urllib.request.urlopen(request)
        return_values = httpresp.read().splitlines();
        httpresp.close();
        return_code = return_values[0]
        if not return_code == "true":
            error = Invalid(self.message('incorrect', state), field_dict, state)
            error.error_dict = {'recaptcha_response_field':self.message('incorrect', state)}
            raise error
        return True
