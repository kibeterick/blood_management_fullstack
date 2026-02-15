from django.db.models import Q

def all_requests(request):
    query = request.GET.get('q', '')
    reqs = BloodRequest.objects.filter(
        Q(blood_group__icontains=query) | Q(username__icontains=query)
    ).order_by('-id') if query else BloodRequest.objects.all().order_by('-id')
    return render(request, 'all_requests.html', {'requests': reqs, 'query': query})

def donor_list(request):
    query = request.GET.get('q', '')
    donors = Donor.objects.filter(
        Q(blood_group__icontains=query) | Q(name__icontains=query)
    ) if query else Donor.objects.all()
    return render(request, 'donor_list.html', {'donors': donors, 'query': query})
