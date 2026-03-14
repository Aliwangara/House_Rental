from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from .models import Property,Tenant,Payment,MaintenanceRequest,Profile
from .forms import PropertyForm,MaintenanceForm,PaymentForm
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.db.models import Sum
from django.db import models
from django.views.decorators.http import require_POST




# Create your views here.


def home(request):

 properties = Property.objects.filter(is_occupied=False)[:4]  # show latest 4 available
 return render(request, 'home/home.html', {'properties': properties})


@login_required
def dashboard_router(request):
    if hasattr(request.user, 'profile'):
        if request.user.profile.role == 'tenant':
            return redirect('tenant_dashboard')
        elif request.user.profile.role == 'landlord':
            return redirect('landlord_dashboard')
    # fallback in case no profile
    return redirect('home')


@login_required
def landlord_dashboard(request):
    properties = Property.objects.filter()
    tenants = Tenant.objects.all()
    payments = Payment.objects.all()

    return render(request, 'dashboard/landlord_dashboard.html', {
        'properties': properties,
        'tenants': tenants,
        'payments': payments
    })


@login_required
def tenant_dashboard(request):
    tenant, created = Tenant.objects.get_or_create(user=request.user)
    property = tenant.property if tenant.property else None
    payments = Payment.objects.filter(tenant=tenant)

    return render(request, 'dashboard/tenant_dashboard.html', {
        'tenant': tenant,
        'property': property,
        'payments': payments
    })


def all_properties(request):
    properties = Property.objects.filter(is_occupied=False)  # or remove filter to show all
    return render(request, 'home/all_properties.html', {'properties': properties})


def property_detail(request, pk):
    property = get_object_or_404(Property, pk=pk)
    return render(request, 'home/property_detail.html', {'property': property})



@login_required
def property_list(request):
    properties = Property.objects.all()
    return render(request, 'dashboard/landlord_property_list.html', {'properties': properties})

@login_required
def add_property(request):
    if request.method == 'POST':
        form = PropertyForm(request.POST,request.FILES)
        if form.is_valid():
            property = form.save(commit=False)
            property.save()
            return redirect('property_list')
    else:
        form = PropertyForm()
    return render(request, 'dashboard/add_property.html', {'form': form})

@login_required
def edit_property(request, pk):
    property = get_object_or_404(Property, pk=pk)
    form = PropertyForm(request.POST or None,request.FILES, instance=property)
    if form.is_valid():
        form.save()
        return redirect('property_list')
    return render(request, 'dashboard/edit_property.html', {'form': form})

@login_required
def delete_property(request, pk):
    property = get_object_or_404(Property, pk=pk)
    property.delete()
    return redirect('property_list')


@login_required
def submit_maintenance_request(request):
    tenant = Tenant.objects.get(user=request.user)

    if request.method == 'POST':
        form = MaintenanceForm(request.POST)
        if form.is_valid():
            request_obj = form.save(commit=False)
            request_obj.tenant = tenant
            request_obj.save()
            return redirect('tenant_requests')
    else:
        form = MaintenanceForm()

    return render(request, 'dashboard/tenant_submit_request.html', {'form': form})


@login_required
def tenant_requests(request):
    tenant = Tenant.objects.get(user=request.user)
    requests = MaintenanceRequest.objects.filter(tenant=tenant).order_by('-submitted_at')
    return render(request, 'dashboard/tenant_requests.html', {'requests': requests})

@login_required
def all_maintenance_requests(request):
    requests = MaintenanceRequest.objects.all().order_by('-submitted_at')
    return render(request, 'dashboard/landlord_requests.html', {'requests': requests})



@login_required
def submit_payment(request):
    tenant = Tenant.objects.get(user=request.user)
    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.tenant = tenant
            payment.save()
            return redirect('tenant_payments')
    else:
        form = PaymentForm()
    return render(request, 'dashboard/tenant_submit_payment.html', {'form': form})


@login_required
def tenant_payments(request):
    tenant = Tenant.objects.get(user=request.user)
    payments = Payment.objects.filter(tenant=tenant).order_by('-payment_date')
    return render(request, 'dashboard/tenant_payments.html', {'payments': payments})


@login_required
def all_payments(request):
    payments = Payment.objects.all().order_by('-payment_date')
    return render(request, 'dashboard/landlord_payments.html', {'payments': payments})

@require_POST
@login_required
def verify_payment(request, pk):
    if not request.user.is_staff and request.user.profile.role != 'landlord':
        messages.error(request, "You are not authorized to perform this action.")
        return redirect('landlord_payments')

    payment = get_object_or_404(Payment, pk=pk)
    payment.is_verified = True
    payment.save()

    messages.success(request, f"Payment from {payment.tenant.user.get_full_name()} verified.")
    return redirect('landlord_payments')


def generate_pdf_receipt(request, pk):
    payment = get_object_or_404(Payment, pk=pk)

    if payment.tenant.user != request.user and not request.user.is_staff:
        return HttpResponse("Unauthorized", status=401)

    template_path = 'dashboard/pdf_receipt.html'
    context = {'payment': payment}
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="receipt_{payment.id}.pdf"'

    template = get_template(template_path)
    html = template.render(context)

    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('Error generating PDF')
    return response


@login_required
def reports(request):
    payments = Payment.objects.all().order_by('-payment_date')

    start_date = request.GET.get('start')
    end_date = request.GET.get('end')

    if start_date and end_date:
        try:
            start = parse_date(start_date)
            end = parse_date(end_date)
            payments = payments.filter(payment_date__range=(start, end))
        except ValueError:
            messages.error(request, "Invalid date format.")

    total_collected = payments.aggregate(total=models.Sum('amount'))['total'] or 0

    context = {
        'payments': payments,
        'start_date': start_date,
        'end_date': end_date,
        'total_collected': total_collected,
    }
    return render(request, 'dashboard/reports.html', context)