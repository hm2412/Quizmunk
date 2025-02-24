from django.shortcuts import render, redirect
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from app.forms import PasswordResetForm
from django.views.decorators.cache import never_cache

@login_required
@never_cache
def password_reset(request):
    if request.method == "POST":
        form = PasswordResetForm(request.POST, user=request.user)
        if form.is_valid():
            request.user.set_password(form.cleaned_data["new_password"])
            request.user.save()
            update_session_auth_hash(request, request.user)  # Prevents logout
            messages.success(request, "Your password has been successfully changed.")
            return redirect("homepage")
    else:
        form = PasswordResetForm(user=request.user)

    return render(request, "password_reset.html", {"form": form})
