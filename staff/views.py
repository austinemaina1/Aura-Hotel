from django.shortcuts import render, redirect, get_object_or_404
from .models import Staff
from .forms import StaffForm
from django.shortcuts import render
from .models import Staff
from django.contrib.auth.decorators import login_required

def staff_list(request):

    staff_members = Staff.objects.all()

    return render(
        request,
        'staff_list.html',
        {'staff_members': staff_members}
    )


def create_staff(request):

    if request.method == 'POST':

        form = StaffForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect('staff_list')

    else:
        form = StaffForm()

    return render(
        request,
        'create_staff.html',
        {'form': form}
    )


def edit_staff(request, id):

    staff = get_object_or_404(
        Staff,
        id=id
    )

    if request.method == 'POST':

        form = StaffForm(
            request.POST,
            instance=staff
        )

        if form.is_valid():
            form.save()
            return redirect('staff_list')

    else:

        form = StaffForm(
            instance=staff
        )

    return render(
        request,
        'edit_staff.html',
        {'form': form}
    )


def delete_staff(request, id):

    staff = get_object_or_404(
        Staff,
        id=id
    )

    if request.method == 'POST':
        staff.delete()
        return redirect('staff_list')

    return render(
        request,
        'delete_staff.html',
        {'staff': staff}
    )

@login_required
def staff_dashboard(request):

    total_staff = Staff.objects.count()

    management_staff = Staff.objects.filter(
        department='Management'
    ).count()

    reception_staff = Staff.objects.filter(
        department='Reception'
    ).count()

    housekeeping_staff = Staff.objects.filter(
        department='Housekeeping'
    ).count()

    security_staff = Staff.objects.filter(
        department='Security'
    ).count()

    recent_staff = Staff.objects.order_by('-id')[:10]

    context = {
        'total_staff': total_staff,
        'management_staff': management_staff,
        'reception_staff': reception_staff,
        'housekeeping_staff': housekeeping_staff,
        'security_staff': security_staff,
        'recent_staff': recent_staff,
    }

    return render(
        request,
        'staff_dashboard.html',
        context
    )