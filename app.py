reporte_operacion = {
    "id_proyecto": "GAM-2026",
    "tipo": "Consultoría Operativa",
    "metricas": {
        "eficiencia": 0.92,
        "alertas_activas": False
    },
    "etiquetas": ["cierre", "finanzas", "automatizacion"]
}

print("--- PROCESANDO REPORTE DE IA ---")
print(f"Proyecto: {reporte_operacion['id_proyecto']}")
print(f"Eficiencia Operativa: {reporte_operacion['metricas']['eficiencia'] * 100}%")

if not reporte_operacion['metricas']['alertas_activas']:
    print("Estado: Operación limpia y sin alertas.")