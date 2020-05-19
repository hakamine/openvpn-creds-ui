from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from environs import Env
from io import BytesIO
import os
import mimetypes
from django.http import StreamingHttpResponse, HttpResponseRedirect
from wsgiref.util import FileWrapper
from django.urls import reverse
import logging

from .forms import PKIPasswordForm
import scripts.easyrsa_show_cert
import scripts.easyrsa_build_client
import scripts.gen_ovpn_cli_cfg

logger = logging.getLogger(__name__)


def index(request):

    # if user is authenticated:
    #   check if they are already in the PKI
    #   if user in PKI: provide link to download config
    #   if      not   : provde a link to form
    if request.user.is_authenticated:
        try:
            user_in_pki = True if (scripts.easyrsa_show_cert.show_cert(request.user.username).returncode == 0) else False
        except Exception:
            context = {'show_cert_exc': True}
        else:
            context = {'show_cert_exc': False,
                       'user_in_pki': user_in_pki}

    else:
        # user not authenticated, no need to pass anything to template
        # (will show a link to the login page)
        context = {}
    return render(request, 'app/index.html', context)


@login_required
def pki_register(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = PKIPasswordForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # call the function to build a cert/key pair for the user
            # and generate a configuration file
            try:
                bcrc = scripts.easyrsa_build_client.build_client(request.user.username, form.cleaned_data['password']).returncode
            except Exception:
                return HttpResponseRedirect(reverse('pki_register_conf_error'))
            else:
                if bcrc == 0:
                    # if return code was 0, all is good
                    return HttpResponseRedirect(reverse('pki_register_conf_ok'))
                else:
                    return HttpResponseRedirect(reverse('pki_register_conf_error'))

    # if a GET (or any other method) we'll create a blank form
    else:
        form = PKIPasswordForm()

    return render(request, 'app/pki_register.html', {'form': form})


@login_required
def pki_register_conf_ok(request):

    context = {}
    return render(request, 'app/pki_register_conf_ok.html', context)


@login_required
def pki_register_conf_error(request):

    context = {}
    return render(request, 'app/pki_register_conf_error.html', context)


@login_required
def download_config(request):

    env = Env()
    # generate config file and serve
    try:
        rc, vpncfg = scripts.gen_ovpn_cli_cfg.main([request.user.username,
                                                   os.path.join(env('CRUI_EASYRSA_DIR'), "pki"),
                                                   env('CRUI_OPENVPN_CLIENT_BASE_CFG'),
                                                   env('CRUI_OPENVPN_TA'),
                                                   env('CRUI_CAT')])
    except Exception as e:
        logger.error("Exception: {}".format(e))
        return HttpResponseRedirect(reverse('download_config_error'))

    if rc != 0:
        logger.error("gen_ovpn_cli_cfg() return code: {}".format(rc))
        return HttpResponseRedirect(reverse('download_config_error'))

    the_file = BytesIO(vpncfg)
    filename = "{}.ovpn".format(request.user.username)

    chunk_size = 8192
    response = StreamingHttpResponse(FileWrapper(the_file, chunk_size),
                                     content_type=mimetypes.guess_type(filename)[0])
    response['Content-Length'] = len(vpncfg)
    response['Content-Disposition'] = "attachment; filename={}".format(filename)
    return response


@login_required
def download_config_error(request):

    context = {}
    return render(request, 'app/download_config_error.html', context)
