from django.shortcuts import redirect, render
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required


@login_required(login_url='login')
def profile_settings(request):
    if request.method == 'GET':
        return render(request, 'users/profile.html')
    else:
        user = User.objects.get(id=request.user.id)

        if request.POST.get('username'):
            username = request.POST.get('username')
            if len(User.objects.filter(username=username)) != 0:
                if User.objects.get(username=username).id != request.user.id:
                    messages.error(request, 'This username is already been used, plase choose a different one')
                    return render(request, 'users/profile.html')
            user.username = username
        else:
            messages.error(request, 'Username is required')
            return render(request, 'users/profile.html')

        if request.POST.get('first_name'):
            first_name = request.POST.get('first_name')
            user.first_name = first_name


        if request.POST.get('last_name'):
            last_name = request.POST.get('last_name')
            user.last_name = last_name


        if request.POST.get('email'):
            email = request.POST.get('email')
            if len(User.objects.filter(email=email)) != 0:
                if User.objects.get(email=email).id != request.user.id:
                    messages.error(request, 'This email is already been used, plase choose a different one')
                    return render(request, 'users/profile.html')
            user.email = email

        else:
            messages.error(request, 'Email is required')
            return render(request, 'users/profile.html')

        
        user.save()
        messages.success(request, 'Profile updated successfully')
        return redirect('profile-settings')



