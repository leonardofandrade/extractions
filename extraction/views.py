from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, TemplateView
from django.contrib import messages
from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy, reverse
from django.http import JsonResponse, HttpResponseRedirect
from django.db.models import Q
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from .models import (
    ExtractionRequest, 
    ExtractionRequestProcedure, 
    ExtractionRequestDocument,
    OrganizationUnit
)
from .forms import (
    ExtractionRequestForm, 
    ExtractionRequestProcedureForm, 
    ExtractionRequestDocumentForm
)

class LandingPageView(TemplateView):
    template_name = 'extraction/landing.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return HttpResponseRedirect(reverse('extraction:request_list'))
        return super().dispatch(request, *args, **kwargs)

class CustomLoginView(LoginView):
    template_name = 'extraction/login.html'
    redirect_authenticated_user = True
    
    def get_success_url(self):
        return reverse('extraction:request_list')

class ExtractionRequestListView(LoginRequiredMixin, ListView):
    paginate_by = 10  # Set the number of items per page
    model = ExtractionRequest
    template_name = 'extraction/extraction_request_list.html'
    context_object_name = 'requests'

    def get_queryset(self):
        queryset = ExtractionRequest.objects.all()
        
        # Filtrar por status
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        # Filtrar por número
        number = self.request.GET.get('number')
        if number:
            procedure_ids = ExtractionRequestProcedure.objects.filter(
                number=number).values_list('extraction_request_id', flat=True)
            document_ids = ExtractionRequestDocument.objects.filter(
                number=number).values_list('extraction_request_id', flat=True)
            queryset = queryset.filter(Q(id__in=procedure_ids) | Q(id__in=document_ids))
        
        # Filtrar por ano
        year = self.request.GET.get('year')
        if year:
            procedure_ids = ExtractionRequestProcedure.objects.filter(
                year=year).values_list('extraction_request_id', flat=True)
            document_ids = ExtractionRequestDocument.objects.filter(
                year=year).values_list('extraction_request_id', flat=True)
            queryset = queryset.filter(Q(id__in=procedure_ids) | Q(id__in=document_ids))
        
        # Filtrar por unidade organizacional
        org_unit = self.request.GET.get('organization_unit')
        if org_unit:
            queryset = queryset.filter(organization_unit_id=org_unit)
        
        # Ordenação
        ordering = self.request.GET.get('ordering', '-id')
        if ordering:
            queryset = queryset.order_by(ordering)
        
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_choices'] = ExtractionRequest.EXTRACTION_REQUEST_STATUS_CODES
        context['organization_units'] = OrganizationUnit.objects.all()
        context['filters'] = {
            'status': self.request.GET.get('status', ''),
            'number': self.request.GET.get('number', ''),
            'year': self.request.GET.get('year', ''),
            'organization_unit': self.request.GET.get('organization_unit', ''),
        }
        context['ordering'] = self.request.GET.get('ordering', '-id')
        return context

class ExtractionRequestDetailView(LoginRequiredMixin, DetailView):
    model = ExtractionRequest
    template_name = 'extraction/extraction_request_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = ExtractionRequestForm(instance=self.object)
        context['procedure_form'] = ExtractionRequestProcedureForm()
        context['document_form'] = ExtractionRequestDocumentForm()
        context['procedures'] = self.object.procedures.all()
        context['documents'] = self.object.documents.all()
        context['can_edit'] = self.object.status == ExtractionRequest.STATUS_DRAFT
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.status != ExtractionRequest.STATUS_DRAFT:
            messages.error(request, 'Não é possível editar uma solicitação que já foi enviada para análise.')
            return redirect('extraction:request_detail', pk=self.object.pk)

        form = ExtractionRequestForm(request.POST, instance=self.object)
        if form.is_valid():
            form.save()
            messages.success(request, 'Solicitação atualizada com sucesso.')
        return self.get(request, *args, **kwargs)

class ExtractionRequestCreateView(LoginRequiredMixin, CreateView):
    model = ExtractionRequest
    form_class = ExtractionRequestForm
    template_name = 'extraction/extraction_request_form.html'
    success_url = reverse_lazy('extraction:request_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['organization_units'] = OrganizationUnit.objects.all()
        return context

    def form_valid(self, form):
        form.instance.request_date = timezone.now()
        messages.success(self.request, 'Solicitação criada com sucesso.')
        return super().form_valid(form)

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['organization_unit'].queryset = OrganizationUnit.objects.all()
        return form

@login_required
def add_procedure(request, pk):
    if request.method == 'POST':
        extraction_request = get_object_or_404(ExtractionRequest, pk=pk)
        form = ExtractionRequestProcedureForm(request.POST)
        if form.is_valid():
            procedure = form.save(commit=False)
            procedure.extraction_request = extraction_request
            procedure.save()
            messages.success(request, 'Procedimento adicionado com sucesso.')
            return JsonResponse({'status': 'success'})
        messages.error(request, 'Erro ao adicionar procedimento.')
        return JsonResponse({'status': 'error'})

@login_required
def edit_procedure(request, pk, procedure_id):
    procedure = get_object_or_404(ExtractionRequestProcedure, pk=procedure_id)
    if request.method == 'POST':
        form = ExtractionRequestProcedureForm(request.POST, instance=procedure)
        if form.is_valid():
            form.save()
            messages.success(request, 'Procedimento atualizado com sucesso.')
            return JsonResponse({'status': 'success'})
        messages.error(request, 'Erro ao atualizar procedimento.')
        return JsonResponse({'status': 'error'})
    else:
        form = ExtractionRequestProcedureForm(instance=procedure)
        return render(request, 'extraction/includes/procedure_form.html', {'procedure_form': form})

@login_required
def delete_procedure(request, pk, procedure_id):
    if request.method == 'POST':
        procedure = get_object_or_404(ExtractionRequestProcedure, pk=procedure_id)
        procedure.delete()
        messages.success(request, 'Procedimento excluído com sucesso.')
        return JsonResponse({'status': 'success'})
    messages.error(request, 'Erro ao excluir procedimento.')
    return JsonResponse({'status': 'error'})

@login_required
def add_document(request, pk):
    if request.method == 'POST':
        extraction_request = get_object_or_404(ExtractionRequest, pk=pk)
        form = ExtractionRequestDocumentForm(request.POST, request.FILES)
        if form.is_valid():
            document = form.save(commit=False)
            document.extraction_request = extraction_request
            document.save()
            messages.success(request, 'Documento adicionado com sucesso.')
            return JsonResponse({'status': 'success'})
        messages.error(request, 'Erro ao adicionar documento.')
        return JsonResponse({'status': 'error'})

@login_required
def edit_document(request, pk, document_id):
    document = get_object_or_404(ExtractionRequestDocument, pk=document_id)
    if request.method == 'POST':
        form = ExtractionRequestDocumentForm(request.POST, request.FILES, instance=document)
        if form.is_valid():
            form.save()
            messages.success(request, 'Documento atualizado com sucesso.')
            return JsonResponse({'status': 'success'})
        messages.error(request, 'Erro ao atualizar documento.')
        return JsonResponse({'status': 'error'})
    else:
        form = ExtractionRequestDocumentForm(instance=document)
        return render(request, 'extraction/includes/document_form.html', {'document_form': form})

@login_required
def delete_document(request, pk, document_id):
    if request.method == 'POST':
        document = get_object_or_404(ExtractionRequestDocument, pk=document_id)
        document.delete()
        messages.success(request, 'Documento excluído com sucesso.')
        return JsonResponse({'status': 'success'})
    messages.error(request, 'Erro ao excluir documento.')
    return JsonResponse({'status': 'error'})

@login_required
def view_request(request, pk):
    request_detail = get_object_or_404(ExtractionRequest, pk=pk)
    context = {
        'request': request_detail,
        'procedures': request_detail.procedures.all(),
        'documents': request_detail.documents.all()
    }
    return render(request, 'extraction/extraction_request_view.html', context)

@login_required
def send_to_analysis(request, pk):
    extraction_request = get_object_or_404(ExtractionRequest, pk=pk)
    try:
        extraction_request.send_to_analysis()
        messages.success(request, 'Solicitação enviada para análise com sucesso.')
    except Exception as e:
        messages.error(request, str(e))
    return redirect('extraction:request_detail', pk=pk)

@login_required
def review_request(request, pk):
    request_detail = get_object_or_404(ExtractionRequest, pk=pk)
    if request.method == 'POST':
        action = request.POST.get('action')
        justification = request.POST.get('justification')
        if action == 'approve':
            request_detail.status = ExtractionRequest.STATUS_APPROVED
            request_detail.justification = justification
        elif action == 'reject':
            request_detail.status = ExtractionRequest.STATUS_REJECTED
            request_detail.justification = justification
        request_detail.save()
        messages.success(request, 'Solicitação atualizada com sucesso.')
        return redirect('extraction:request_list')
    
    return render(request, 'extraction/review_request.html', {'request': request_detail})
