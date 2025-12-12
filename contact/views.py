from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from .form import ContactForm # L'importation est maintenant relative ('.forms')

def contact_view(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        
        if form.is_valid():
            nom = form.cleaned_data['nom']
            email = form.cleaned_data['email']
            sujet = form.cleaned_data['sujet']
            message = form.cleaned_data['message']
            
            email_body = f"De: {nom} <{email}>\n\nSujet: {sujet}\n\nMessage:\n{message}"
            
            try:
                send_mail(
                    subject=f"Tsitsi Store - Nouveau Contact: {sujet}",
                    message=email_body,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=['andrianavalonarolland@gmail.com'], # N'oubliez pas de le remplacer
                    fail_silently=False,
                )
                
                messages.success(request, 'Votre message a été envoyé avec succès ! Nous vous répondrons bientôt.')
                # Redirection vers la même page, mais en utilisant le nom d'URL complet
                return redirect('contact:contact_us') 
                
            except Exception as e:
                messages.error(request, f"Une erreur s'est produite lors de l'envoi de l'email. Détail: {e}")
                
    else:
        form = ContactForm()
        
    context = {
        'form': form,
    }
    # Le template est maintenant dans contact/templates/contact.html
    return render(request, 'contact/contact.html', context)