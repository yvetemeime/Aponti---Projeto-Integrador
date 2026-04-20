from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User, Group
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.http import HttpResponse, JsonResponse
from django.db.models import Q
from django.template.loader import get_template
from django.contrib import messages
from .models import Registro
from xhtml2pdf import pisa
import tablib
import pandas as pd
import json

# --- VIEW PRINCIPAL: DASHBOARD COM FILTRO DE ESCOPO ---


class RegistroList(LoginRequiredMixin, ListView):
    model = Registro
    template_name = 'registro_list.html'
    context_object_name = 'object_list'

    def get_queryset(self):
        user = self.request.user

        # 1. ADMIN / SUPERUSER: Enxerga tudo
        if user.is_staff or user.is_superuser:
            qs = Registro.objects.all()

        # 2. LIDERANÇA: Filtro de Escopo (A com A / B com B)
        elif user.groups.filter(name='Lideranca').exists():
            nome_lider = user.username.upper()

            if "ASSOCIADOA" in nome_lider:
                # Líder A vê ele mesmo e qualquer usuário que tenha "ASSOCIADOA" no nome
                qs = Registro.objects.filter(
                    Q(usuario=user) | Q(usuario__username__icontains="ASSOCIADOA")
                )
            elif "ASSOCIADOB" in nome_lider:
                # Líder B vê ele mesmo e qualquer usuário que tenha "ASSOCIADOB" no nome
                qs = Registro.objects.filter(
                    Q(usuario=user) | Q(usuario__username__icontains="ASSOCIADOB")
                )
            else:
                # Caso o nome não siga o padrão, ele vê apenas o dele para segurança
                qs = Registro.objects.filter(usuario=user)

        # 3. ASSOCIADO: Vê apenas o dele
        else:
            qs = Registro.objects.filter(usuario=user)

        # APLICAÇÃO DOS FILTROS DE TELA (BARRA DE BUSCA)
        usuario_id = self.request.GET.get('usuario')
        data_inicio = self.request.GET.get('data_inicio')
        data_fim = self.request.GET.get('data_fim')

        if usuario_id and usuario_id != 'todos':
            qs = qs.filter(usuario_id=usuario_id)
        if data_inicio:
            qs = qs.filter(data_criacao__date__gte=data_inicio)
        if data_fim:
            qs = qs.filter(data_criacao__date__lte=data_fim)

        return qs.distinct().order_by('-data_criacao')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        qs = self.get_queryset()

        context['total_registros'] = qs.count()
        context['ativos'] = qs.filter(ativo=True).count()
        context['inativos'] = qs.filter(ativo=False).count()

        total = context['total_registros']
        context['taxa_conformidade'] = round(
            (context['ativos'] / total * 100), 1) if total > 0 else 0

        # O filtro de usuários na tela também deve respeitar o escopo do Líder
        user = self.request.user
        if user.is_staff or user.is_superuser:
            context['todos_usuarios'] = User.objects.all().order_by('username')
        elif user.groups.filter(name='Lideranca').exists():
            nome_lider = user.username.upper()
            if "ASSOCIADOA" in nome_lider:
                context['todos_usuarios'] = User.objects.filter(
                    username__icontains="ASSOCIADOA")
            elif "ASSOCIADOB" in nome_lider:
                context['todos_usuarios'] = User.objects.filter(
                    username__icontains="ASSOCIADOB")

        return context

# --- API CHATBOT ---


def chatbot_api(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            pergunta = data.get('mensagem', '').lower()
            total = Registro.objects.filter(usuario=request.user).count()
            resposta = f"Olá! Identifiquei {total} registros sob seu acesso. Como posso ajudar?"
            return JsonResponse({'resposta': resposta})
        except:
            return JsonResponse({'resposta': "Erro na análise."}, status=400)
    return JsonResponse({'error': 'POST apenas'}, status=405)

# --- IMPORT/EXPORT ---


def importar_planilha(request):
    if request.method == 'POST' and request.FILES.get('planilha'):
        try:
            arquivo = request.FILES['planilha']
            df = pd.read_csv(arquivo) if arquivo.name.endswith(
                '.csv') else pd.read_excel(arquivo)
            df = df.dropna(how='all')
            linhas = [" | ".join([str(val) for val in row.values])
                      for _, row in df.iterrows()]
            conteudo_final = " [QUEBRA] ".join(linhas)
            Registro.objects.create(
                usuario=request.user, titulo=f"Lote: {arquivo.name}", descricao=conteudo_final, ativo=True)
            messages.success(request, "Dataset importado com sucesso!")
        except Exception as e:
            messages.error(request, f"Erro: {e}")
    return redirect('registro_list')


def gerar_pdf_auditoria(request):
    ids = request.POST.getlist('registros_ids')
    registros = Registro.objects.filter(
        id__in=ids) if ids else Registro.objects.all()
    for r in registros:
        r.descricao_limpa = r.descricao.replace('[QUEBRA]', ' | ')
    context = {'registros': registros,
               'usuario_gerador': request.user.username}
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="Auditoria_HSBS.pdf"'
    pisa.CreatePDF(get_template(
        'pdf_report.html').render(context), dest=response)
    return response


def exportar_selecionados(request):
    if request.method == 'POST':
        ids = request.POST.getlist('registros_ids')
        dataset = tablib.Dataset(
            headers=['ID', 'Título', 'Responsável', 'Status'])
        for r in Registro.objects.filter(id__in=ids):
            dataset.append([r.id, r.titulo, r.usuario.username,
                           "VALIDADO" if r.ativo else "PENDENTE"])
        response = HttpResponse(
            dataset.xlsx, content_type='application/vnd.ms-excel')
        response['Content-Disposition'] = 'attachment; filename="Export_HSBS.xlsx"'
        return response
    return redirect('registro_list')

# --- GESTÃO DE USUÁRIOS ---


class UsuarioListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = User
    template_name = 'registration/usuario_list.html'
    context_object_name = 'usuarios'
    def test_func(self): return self.request.user.is_staff


class UsuarioCreate(CreateView):
    form_class = UserCreationForm
    template_name = 'registration/registrar.html'
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        user = form.save()
        perfil = self.request.POST.get('perfil_usuario')
        if perfil == 'admin':
            user.is_staff = True
            user.save()
        elif perfil == 'lider':
            grupo, _ = Group.objects.get_or_create(name='Lideranca')
            user.groups.add(grupo)
        return super().form_valid(form)


def usuario_toggle_status(request, pk):
    if not request.user.is_staff:
        return redirect('registro_list')
    u = get_object_or_404(User, pk=pk)
    if not u.is_superuser:
        u.is_active = not u.is_active
        u.save()
    return redirect('usuario_list')

# --- CRUD REGISTROS ---


class RegistroCreate(LoginRequiredMixin, CreateView):
    model = Registro
    fields = ['titulo', 'descricao', 'ativo']
    template_name = 'registro_form.html'
    success_url = reverse_lazy('registro_list')

    def form_valid(self, form):
        form.instance.usuario = self.request.user
        return super().form_valid(form)


class RegistroUpdate(LoginRequiredMixin, UpdateView):
    model = Registro
    fields = ['titulo', 'descricao', 'ativo']
    template_name = 'registro_form.html'
    success_url = reverse_lazy('registro_list')


class RegistroDelete(LoginRequiredMixin, DeleteView):
    model = Registro
    template_name = 'registro_confirm_delete.html'
    success_url = reverse_lazy('registro_list')
