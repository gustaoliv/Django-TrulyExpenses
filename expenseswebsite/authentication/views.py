from django.shortcuts import redirect, render
from django.urls import reverse
from django.views import View
import json
from django.http import JsonResponse
from django.contrib.auth.models import User
from validate_email import validate_email
from django.contrib import messages
from django.core.mail import EmailMessage
from django.utils.encoding import force_bytes, force_str, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib.sites.shortcuts import get_current_site
from .utils import token_generator
from django.contrib import auth
from django.contrib.auth.tokens import PasswordResetTokenGenerator
import threading


class EmailThread(threading.Thread):
    def __init__(self, email):
        self.email = email
        threading.Thread.__init__(self)

    def run(self):
        self.email.send(fail_silently=False)

class UsernameValidationView(View):
    def post(self, request):
        data = json.loads(request.body)
        username = data['username']

        if not str(username).isalnum():
            return JsonResponse({'username_error': 'username should only contain alphanumeric characters'}, status=400)

        if User.objects.filter(username=username).exists():
            return JsonResponse({'username_error': 'sorry username in use, choose another one'}, status=409)

        return JsonResponse({'username_valid': True})


class EmailValidationView(View):
    def post(self, request):
        data = json.loads(request.body)
        email = data['email']

        if not validate_email(email):
            return JsonResponse({'email_error': 'Email is invalid'}, status=400)

        if User.objects.filter(email=email).exists():
            return JsonResponse({'email_error': 'sorry email in use, choose another one'}, status=409)

        return JsonResponse({'email_valid': True})



class RegistrationView(View):
    def get(self, request):
        return render(request, 'authentication/register.html')


    def post(self, request):
        #GET USER DATA 
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']

        context={
            'fieldValues': request.POST
        }

        #VALIDATE
        if not User.objects.filter(username=username).exists():
            if not User.objects.filter(email=email).exists():
                if len(password) < 6:
                    messages.error(request, 'Password too short')
                    return render(request, 'authentication/register.html', context)
                
                user = User.objects.create_user(username=username, email=email, first_name=first_name, last_name=last_name)
                user.set_password(password)
                user.is_active = False
                user.save()


                domain = get_current_site(request).domain
                uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
                link = reverse('activate', kwargs={'uidb64': uidb64, 'token': token_generator.make_token(user)})

                email_subject = 'Active your account'
                activate_url = f'http://{domain}{link}'
                email_body = f'Hi {user.first_name}! Please use this link to verify your account\n{activate_url}'
                
                email = EmailMessage(
                    email_subject,
                    email_body,
                    'gusta.oliv4@gmail.com',
                    [email, ],
                )  
                
                EmailThread(email).start()

                messages.success(request, 'Account successfully created, Please Check Your Email')
                return render(request, 'authentication/login.html')

        #CREATE USER ACCOUNT



        return render(request, 'authentication/register.html')



class VerificationView(View):
    def get(self, request, uidb64, token):

        try:
            id = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=id)

            if not token_generator.check_token(user, token):
                return redirect('login'+'?message='+'User already activated')

            if user.is_active:
                return redirect('login')
            user.is_active = True
            user.save()
            messages.success(request, 'Account activated successfully')
            return redirect('login')

        except Exception as ex:
            pass

        return redirect('login')




class LoginView(View):
    def get(self, request):
        return render(request, 'authentication/login.html')

    def post(self, request):
        username = request.POST['username']
        password = request.POST['password']

        if username and password:
            user = auth.authenticate(username=username, password=password)
            if user:
                if user.is_active:
                    auth.login(request, user)
                    messages.success(request, f'Welcome {user.username}, you are now logged in')
                    return redirect('expenses')
            
                else:
                    messages.error(request, 'Account is not active, please check your email')
            else:
                messages.error(request, 'Invalid credentials, try again')
        else:
            messages.error(request, 'Please fill all fields')
        
        return render(request, 'authentication/login.html')



class LogoutView(View):
    def post(self, request):
        auth.logout(request)
        messages.success(request, 'You have been logged out')
        return redirect('login')



class RequestPasswordResetEmail(View):
    def get(self, request):
        return render(request, 'authentication/reset-password.html')
        


    def post(self, request):
        email = request.POST['email']

        context = {
            'values': request.POST
        }

        if not validate_email(email):
            messages.error(request, 'Pleasy suply a valid email')
            return render(request, 'authentication/reset-password.html', context)


        user = User.objects.filter(email=email)
        if user.exists():
            current_user = user[0]
            domain = get_current_site(request).domain
            uidb64 = urlsafe_base64_encode(force_bytes(current_user.pk))
            link = reverse('reset-user-password', kwargs={'uidb64': uidb64, 'token': PasswordResetTokenGenerator().make_token(current_user)})

            email_subject = 'Password Reset Instructions'
            reset_url = f'http://{domain}{link}'
            email_body = f'Hi {current_user.username}! Please click the link below to reset your password\n{reset_url}'
            

            email = EmailMessage(
                email_subject,
                email_body,
                'gustavodjango25@gmail.com',
                [email, ],
            )  
            EmailThread(email).start()

        messages.success(request, 'We have send you an email to reset the password')            


        

        return render(request, 'authentication/reset-password.html')



class CompletePasswordReset(View):
    def get(self, request, uidb64, token):
        try:
            user_id = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=user_id)
            if not PasswordResetTokenGenerator().check_token(user, token):
                messages.info(request, 'Password link is invalid, please request a new one')
                return render(request, 'authentication/set-new-password.html')

        except Exception as identifier:
            pass

        context = {
            'uidb64': uidb64,
            'token': token,
        }
        return render(request, 'authentication/set-new-password.html', context)

    def post(self, request, uidb64, token):
        context = {
            'uidb64': uidb64,
            'token': token,
        }
        password = request.POST['password']
        password2 = request.POST['password2']

        if password != password2:
            messages.error(request, 'Passwords do not match')
            return render(request, 'authentication/set-new-password.html', context)
        
        if len(password) < 6:
            messages.error(request, 'Password too short')
            return render(request, 'authentication/set-new-password.html', context)

        try:
            user_id = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=user_id)
            user.set_password(password)
            user.save() 
            messages.success(request, 'Password reset successfully, you can login now')
            return redirect('login')
        except Exception as identifier:
             messages.info(request, 'Something went wrong, try again')
             return render(request, 'authentication/set-new-password.html')

        

