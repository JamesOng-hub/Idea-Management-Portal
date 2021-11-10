from django.shortcuts import render
from .forms import ContactUsForm
# Create your views here.
def contact_us(request): 
    
        form = ContactUsForm()
        return render(request, 'contact_us.html', {'form': form})