from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from app.forms import PasswordResetForm

@login_required
def password_reset(request):
    if request.method == "POST":
        form = PasswordResetForm(request.POST, user=request.user)
        if form.is_valid():
            # Update the user's password
            request.user.set_password(form.cleaned_data["new_password"])
            request.user.save()
            messages.success(request, "Your password has been successfully changed.")
            return redirect("profile")  # Redirect to profile page after success
    else:
        form = PasswordResetForm(user=request.user)

    return render(request, "password_reset.html", {"form": form})
