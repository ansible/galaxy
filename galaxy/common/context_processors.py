import secrets
import base64


def template_metadata(request):
    return {
        'csp_nonce': base64.b64encode(secrets.token_bytes(32)).decode()
    }
