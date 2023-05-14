import os

from django.contrib import messages
from django.contrib.auth import authenticate, update_session_auth_hash
from django.contrib.auth import login
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.core.paginator import Paginator
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models.fields.files import ImageFieldFile
from django.http import HttpResponseRedirect, QueryDict
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render
from django.template.loader import render_to_string
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.utils.encoding import force_bytes
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from django.utils.http import urlsafe_base64_encode
from django.views import View
from django.views.generic import TemplateView, FormView, DeleteView, UpdateView

from SwapSmart.forms import RegistrationForm, ChangePasswordForm, LoginForm
from SwapSmart.models import Ad, Category
from SwapSmart.token import account_activation_token


class IndexView(TemplateView):
    template_name = 'base.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'categories': Category.objects.all(),
        })
        return context


class LoginView(View):
    template_name = 'auth/login.html'

    def get(self, request):
        form = LoginForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = LoginForm(request=request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            if not User.objects.filter(username=username):
                form.add_error('username', 'There is no user with that username.')
            else:
                user = authenticate(request, username=username, password=password)
                if user is not None:
                    login(request, user)
                    return redirect('welcome')
                else:
                    form.add_error('password', 'Invalid password.')
        else:
            for key, error in list(form.errors.items()):
                if key == 'captcha' and error[0] == 'This field is required.':
                    messages.error(request, "You must pass the reCAPTCHA test")
                    continue
                messages.error(request, error)
        return render(request, self.template_name, {'form': form})


class RegisterView(View):
    form_class = RegistrationForm
    template_name = 'auth/register.html'

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            password2 = form.cleaned_data.get('password2')
            user_email = form.cleaned_data.get('email')

            if User.objects.filter(email=user_email).exists():
                form.add_error('email', 'User with that email already exists.')
            elif len(password2) < 8:
                form.add_error('password2', "Password must be at least 8 characters.")
            elif not any(char.isupper() for char in password2):
                form.add_error('password2', "Password must contain at least one uppercase letter.")
            elif not any(char.islower() for char in password2):
                form.add_error('password2', "Password must contain at least one lowercase letter.")
            elif not any(char.isdigit() for char in password2):
                form.add_error('password2', "Password must contain at least one number.")
            else:
                user = form.save(commit=False)
                user.is_active = False
                user.save()

                current_site = get_current_site(request)
                mail_subject = 'Activation link for HireNow'
                message = render_to_string('misc/activation_message.html', {
                    'user': user,
                    'domain': current_site.domain,
                    'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                    'token': account_activation_token.make_token(user),
                })
                to_email = user_email
                email = EmailMessage(
                    mail_subject, message, to=[to_email]
                )
                email.fail_silently = False
                email.content_subtype = 'html'
                email.send()
                return redirect(reverse('confirm_email'))

        return render(request, self.template_name, {'form': form})


class ActivateView(View):
    def get(self, request, uid64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uid64))
            user = User.objects.get(pk=uid)
        except(TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None
        if user is not None and account_activation_token.check_token(user, token):
            user.is_active = True
            user.save()
            login(request, user)
            return redirect(reverse('account_activated'))
        else:
            return redirect(reverse('invalid_token'))


class LogoutView(LoginRequiredMixin, View):
    def get(self, request):
        logout(request)
        messages.error(request, 'You have successfully logged out!')
        return render(request, 'auth/logout.html')


@method_decorator(login_required, name='dispatch')
class ProfileView(View):
    def get(self, request):
        user = request.user

        context = {
            'user': user,
        }
        return render(request, 'profile.html', context)


class ConfirmView(TemplateView):
    template_name = 'misc/confirm_email.html'


class ActivatedView(TemplateView):
    template_name = 'misc/account_activated.html'


class InvalidTokenView(TemplateView):
    template_name = 'misc/invalid_token.html'


class ChangePasswordView(LoginRequiredMixin, FormView):
    template_name = 'auth/change_password.html'
    form_class = ChangePasswordForm
    success_url = reverse_lazy('profile')

    def form_valid(self, form):
        user = form.save()
        update_session_auth_hash(self.request, user)
        return super().form_valid(form)

    def form_invalid(self, form):
        if len(form.cleaned_data.get('new_password1', '')) < 8:
            form.add_error('new_password2', "Password must be at least 8 characters.")
        elif not any(char.isupper() for char in form.cleaned_data.get('new_password1', '')):
            form.add_error('new_password2', "Password must contain at least one uppercase letter.")
        elif not any(char.islower() for char in form.cleaned_data.get('new_password1', '')):
            form.add_error('new_password2', "Password must contain at least one lowercase letter.")
        elif not any(char.isdigit() for char in form.cleaned_data.get('new_password1', '')):
            form.add_error('new_password2', "Password must contain at least one number.")
        return super().form_invalid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs


class ExtendedEncoder(DjangoJSONEncoder):
    def default(self, o):
        if isinstance(o, ImageFieldFile):
            return str(o)
        else:
            return super().default(o)


def ad_list(request, category):
    ads = Ad.objects.filter(category__url_name=category)
    context = {
        'ads': ads,
        'category': category.replace('_', ' ').capitalize()
    }
    return render(request, 'ad/list.html', context)


def ad_detail(request, category, ad):
    return render(request, 'detail.html')


def new_ad(request):
    return render(request, 'base.html')


def delete_ad(request, pk):
    return render(request, 'base.html')


def update_ad(request, pk):
    return render(request, 'base.html')


def send_ad(request, pk):
    return render(request, 'base.html')
