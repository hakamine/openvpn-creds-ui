from django.shortcuts import render
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from environs import Env
from io import BytesIO
import os
import mimetypes
from django.http import StreamingHttpResponse, HttpResponseRedirect
from wsgiref.util import FileWrapper
from django.urls import reverse
import logging
import sys

from .forms import PKIPasswordForm
import scripts.easyrsa_show_cert
import scripts.easyrsa_build_client
import scripts.cat_file
from django.conf import settings

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
                       'user_in_pki': user_in_pki,
                       'openvpn_client_base_cfg_values': settings.CRUI_OPENVPN_CLIENT_BASE_CFG_VALUES}

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
def download_config(request, config_name):

    # check all the files required exist
    # note that the app user may not have permissions to see some of these files
    # such as the ones in PKI dir unless using sudo
    try:
        ta_key = scripts.cat_file.main(settings.CRUI_CAT, settings.CRUI_OPENVPN_TA)
        ca_cert = scripts.cat_file.main(settings.CRUI_CAT, os.path.join(settings.CRUI_EASYRSA_DIR, "pki", "ca.crt"))
        cli_cert = scripts.cat_file.main(settings.CRUI_CAT, os.path.join(settings.CRUI_EASYRSA_DIR, "pki", "issued", "{}.crt".format(request.user.username)))
        cli_key = scripts.cat_file.main(settings.CRUI_CAT, os.path.join(settings.CRUI_EASYRSA_DIR, "pki", "private", "{}.key".format(request.user.username)))
    except Exception as e:
        sys.stderr.write("Error when trying to open input files: {}\n".format(e))
        logger.error("Error when trying to open input files: {}".format(e))
        return HttpResponseRedirect(reverse('download_config_error'))


    # put all together into a file to download
    try:
        # context: start with the vars for the base config
        context = next((dict for dict in settings.CRUI_OPENVPN_CLIENT_BASE_CFG_VALUES if dict['name'] == config_name), None)
        # context: add the certs and keys info, note that we need to convert bytes object to string (decode)
        context['ca_cert'] = ca_cert.decode("ascii")
        context['cli_cert'] = cli_cert.decode("ascii")
        context['cli_key'] = cli_key.decode("ascii")
        context['ta_key'] = ta_key.decode("ascii")

        # print(settings.CRUI_OPENVPN_CLIENT_BASE_CFG_VALUES)
        # print(config_name)
        # print(context)
        # return HttpResponse(render_to_string('app/ovpn/base_config', context=context))

        vpncfg = render_to_string('app/ovpn/base_config', context=context)
        the_file = BytesIO(bytes(vpncfg, "ascii"))
        filename = "{}-{}.ovpn".format(request.user.username, config_name)

        chunk_size = 8192
        response = StreamingHttpResponse(FileWrapper(the_file, chunk_size),
                                        content_type=mimetypes.guess_type(filename)[0])
        response['Content-Length'] = len(vpncfg)
        response['Content-Disposition'] = "attachment; filename={}".format(filename)
        return response

    except Exception as e:
        sys.stderr.write("Error when trying to open input files: {}\n".format(e))
        logger.error("Error when trying to open input files: {}".format(e))
        return HttpResponseRedirect(reverse('download_config_error'))


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
