from django.shortcuts import render
from django.db.models import Avg, Count, Sum, F, Case, When, Value, CharField, DecimalField, Q, ExpressionWrapper, fields
from django.db.models.functions import TruncMonth, Coalesce, ExtractDay
from django.utils.dateparse import parse_date
from Applications.Pedidos.models import Pedido
from datetime import timedelta
from decimal import Decimal

# --------------------------
# PORTALES
# --------------------------
def portal_administrador(request):
    return render(request, 'trabajadores/portaladministrador.html')

def portal_trabajadores(request):
    return render(request, 'trabajadores/portaltrabajadores.html')

def agregar_trabajador(request):
    return render(request, 'gestion/agregar_trabajador.html')


# --------------------------
# REPORTES E INDICADORES
# --------------------------
def reportes(request):
    # Filtros por rango de fechas
    desde_str = request.GET.get('desde')
    hasta_str = request.GET.get('hasta')
    desde = parse_date(desde_str) if desde_str else None
    hasta = parse_date(hasta_str) if hasta_str else None

    # Base query - excluimos cancelados
    pedidos_base = Pedido.objects.exclude(estado='CANCELADO')
    if desde:
        pedidos_base = pedidos_base.filter(fecha_pedido__gte=desde)
    if hasta:
        pedidos_base = pedidos_base.filter(fecha_pedido__lte=hasta)

    # 1. Promedio de tiempo de entrega (solo pedidos entregados)
    from django.db.models.functions import ExtractDay, ExtractHour, ExtractMinute
    from django.db.models import DurationField, F, ExpressionWrapper
    
    pedidos_entregados = pedidos_base.filter(estado='ENTREGADO', fecha_entrega__isnull=False)
    
    # Calcular diferencia en días como float
    tiempo_entregas = pedidos_entregados.annotate(
        dias=ExpressionWrapper(
            ExtractDay(F('fecha_entrega') - F('fecha_pedido')) * 24 * 60 +  # Días a minutos
            ExtractHour(F('fecha_entrega') - F('fecha_pedido')) * 60 +       # Horas a minutos
            ExtractMinute(F('fecha_entrega') - F('fecha_pedido')),           # Minutos
            output_field=fields.FloatField()
        ) / (24 * 60)  # Convertir minutos a días
    ).aggregate(promedio=Avg('dias'))['promedio'] or 0

    # 2. Tasa de repetición de clientes
    from django.db.models import Count
    
    pedidos_clientes_registrados = pedidos_base.filter(cliente__isnull=False)
    total_clientes_unicos = pedidos_clientes_registrados.values('cliente').distinct().count()
    
    clientes_recurrentes = 0
    if total_clientes_unicos > 0:
        clientes_recurrentes = pedidos_clientes_registrados.values('cliente').annotate(
            total_pedidos=Count('id')
        ).filter(total_pedidos__gt=1).count()
    
    tasa_repeticion = (clientes_recurrentes / total_clientes_unicos * 100) if total_clientes_unicos > 0 else 0

    # 3. Ventas por tipo de cliente
    from django.db.models import Sum, Q
    from decimal import Decimal
    
# --- Ventas de clientes domiciliarios ---
    ventas_domiciliario_total = pedidos_base.filter(
        Q(cliente__tipo_cliente='D') |
        Q(tipo_cliente__in=['D', 'Domiciliario'])
    ).aggregate(
        total=Coalesce(Sum('monto_total'), Decimal('0'))
    )['total'] or Decimal('0')

# --- Ventas de clientes empresa ---
    ventas_empresa_total = pedidos_base.filter(
        Q(cliente__tipo_cliente='E') |
        Q(tipo_cliente__in=['E', 'Empresa'])
    ).aggregate(
        total=Coalesce(Sum('monto_total'), Decimal('0'))
    )['total'] or Decimal('0')


    # 4. Pedidos por repartidor
    pedidos_por_repartidor = pedidos_base.filter(
        repartidor__isnull=False
    ).values(
        'repartidor__nombre'
    ).annotate(
        total_pedidos=Count('id')
    ).order_by('-total_pedidos')
    
    ppr_labels = list(pedidos_por_repartidor.values_list('repartidor__nombre', flat=True))
    ppr_values = list(pedidos_por_repartidor.values_list('total_pedidos', flat=True))

    # 5. Crecimiento mensual
    ventas_mensuales = pedidos_base.annotate(
        mes=TruncMonth('fecha_pedido')
    ).values('mes').annotate(
        total=Coalesce(Sum('monto_total'), Decimal('0'))
    ).order_by('mes')
    
    vm_labels = [v['mes'].strftime('%b %Y') if v['mes'] else '' for v in ventas_mensuales]
    vm_values = [float(v['total'] or 0) for v in ventas_mensuales]

    contexto = {
        'promedio_tiempo_entrega': round(float(tiempo_entregas), 2),
        'tasa_repeticion': round(tasa_repeticion, 2),
        'ventas_domiciliario_total': ventas_domiciliario_total,
        'ventas_empresa_total': ventas_empresa_total,
        'pedidos_por_repartidor': pedidos_por_repartidor,
        'ventas_por_tipo': [
            {'tipo': 'Domiciliario', 'total': ventas_domiciliario_total},
            {'tipo': 'Empresa', 'total': ventas_empresa_total},
        ],
        'ventas_mensuales': ventas_mensuales,
        'ppr_labels': ppr_labels,
        'ppr_values': ppr_values,
        'vm_labels': vm_labels,
        'vm_values': vm_values,
    }

    return render(request, 'reportes/reportes.html', contexto)