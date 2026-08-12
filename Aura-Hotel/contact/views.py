from django.shortcuts import render, redirect
from .models import Contact
from django.shortcuts import render, get_object_or_404, redirect

def contact(request):

    if request.method == 'POST':

        print("CONTACT FORM SUBMITTED")

        Contact.objects.create(
            full_name=request.POST.get('full_name'),
            phone_number=request.POST.get('phone_number'),
            email=request.POST.get('email'),
            message=request.POST.get('message')
        )

        return redirect('contact_success')

    return render(request, 'contact.html')


def contact_success(request):
   return render(request, 'contact_success.html')



def messages_list(request):
    messages = Contact.objects.all().order_by('-created_at')

    context = {
        'messages': messages
    }

    return render(
        request,
        'contact/messages_list.html',
        context
    )


from django.shortcuts import render, get_object_or_404
from .models import Contact


def message_detail(request, pk):

    message = get_object_or_404(
        Contact,
        pk=pk
    )

    if not message.is_read:

        message.is_read = True
        message.save()

    context = {
        'message': message
    }

    return render(
        request,
        'contact/message_detail.html',
        context
    )


def delete_message(request, pk):
    message = get_object_or_404(Contact, pk=pk)
    message.delete()

    return redirect('messages_list')