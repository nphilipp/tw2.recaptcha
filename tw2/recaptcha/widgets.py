from tw2.core import Param, Variable, js_callback
from tw2.forms import InputField, Form
from tw2.jquery.base import jquery_js, jQuery

from recaptcha.client.captcha import API_SERVER, API_SSL_SERVER

class ReCaptchaWidget(InputField):
    template = """<div><script type="text/javascript" src="${w.server}/challenge?k=${w.public_key}${w.error_param}"></script>
<noscript>
  <iframe src="${w.server}/noscript?k=${w.public_key}${w.error_query_string}" height="300" width="500" frameborder="0"></iframe><br />
  <textarea name="recaptcha_challenge_field" rows="3" cols="40"></textarea>
  <input type='hidden' name='recaptcha_response_field' value='manual_challenge' />
</noscript>
<input type='hidden' id='${w.compound_id}:recaptcha_challenge_field' name='${w.compound_id}:recaptcha_challenge_field' />
<input type='hidden' id='${w.compound_id}:recaptcha_response_field' name='${w.compound_id}:recaptcha_response_field' />
</div>
""" 

    inline_engine_name = 'genshi'

    type='text'
    public_key = Param(default=None, attribute=True)
    use_ssl = Param(default=False, attribute=True)
    error_param = Param(default=None, attribute=True)
    server = Param(default=API_SERVER, attribute=True)

    error_query_string = Variable(default="")

    resources = [jquery_js]

    @property
    def form_widget(self):
        if not hasattr(self, '_form_widget'):
            w = self
            while not isinstance(w, Form):
                w = w.parent
                if not w:
                    raise RuntimeError(
                            "Couldn't determine form for widget %r" % self)
            self._form_widget = w
        return self._form_widget

    def prepare(self):
        super(ReCaptchaWidget, self).prepare()

        if self.error_param:
            self.safe_modify('error_query_string')
            self.error_query_string = '&error=%s' % self.error_param

        if self.use_ssl:
            self.server = API_SSL_SERVER

        copy_recaptcha_fields = jQuery(
                "#" + self.form_widget.compound_id.replace(":", r"\:")).submit(
                js_callback(r"""function(){{
$('input#{compound_id}\\:recaptcha_challenge_field').val(
  $('input#recaptcha_challenge_field').val());
$('input#{compound_id}\\:recaptcha_response_field').val(
  $('input#recaptcha_response_field').val());
return true;}}""".format(
                compound_id=self.compound_id.replace(":", r"\\:"))))
        self.add_call(copy_recaptcha_fields)
