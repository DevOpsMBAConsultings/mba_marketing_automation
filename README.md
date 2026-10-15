# mba_marketing_automation

Reglas de inscripcion configurables para [`automation_oca`](https://github.com/OCA/automation)
(Odoo 19 CE, rama 19.0). Modular y agnostico: cada pieza es un addon pequeño que se enchufa a otro.

```
automation_oca  (OCA)
      |
mba_ma_enrollment            nucleo: tipo de inscripcion extensible + conteo en vivo.
      |                      No conoce clientes, facturas ni ventas.
mba_ma_inactivity            regla "cliente inactivo": N dias sin comprar. Sin fuente propia.
      |
mba_ma_inactivity_account    fuente: facturas de cliente publicadas (auto_install con account).
```

## Como se extiende

* **Nueva regla** (ej. cumpleaños, fecha, evento): addon que depende de `mba_ma_enrollment`,
  agrega su valor con `selection_add` a `enrollment_type`, define
  `_enrollment_domain_<tipo>()` (devuelve un dominio) y sobreescribe `_compute_domain`
  con su propio `@api.depends` (Odoo suma las dependencias de todas las sobreescrituras).
* **Nueva fuente de compras** (ej. ventas, TPV): addon que depende de `mba_ma_inactivity`,
  agrega su valor con `selection_add` a `inactivity_source` y define
  `_inactivity_rows_<fuente>(company_ids)` -> `[(partner_id, ultima_fecha, cantidad)]`.

## Estado (rama 19.0)

**Bloqueado:** `automation_oca` todavia no existe en la rama 19.0 de OCA/automation (la rama solo
tiene la estructura inicial). Esta rama deja los addons con version 19.0 pero **no se pueden
instalar** hasta que `automation_oca` este migrado a 19. Pendiente: migrar `automation_oca` a 19
(fork de OCA/automation + PR) y probar en una instancia Odoo 19.

La funcionalidad es la misma de la rama 18.0, aun sin adaptar ni probar en 19.

## Estado (heredado de 18.0)

Escrito contra el codigo de OCA/automation 18.0 y Odoo 18 CE. Verificado: sintaxis Python/XML,
que los `xpath` de las vistas encuentran un unico nodo en el formulario real de `automation_oca`,
y los mecanismos de Odoo usados (suma de `depends`, `auto_install` en lista, `Selection` vacio).
**Sin probar todavia en una instancia de Odoo**: instalar en pruebas antes de usar en un cliente.

Pendiente: re-inscripcion (el motor de `automation_oca` inscribe cada registro una sola vez
por configuracion), fuente de ventas, plantilla de flujo de reactivacion, pruebas automaticas.

Licencia AGPL-3 (igual que `automation_oca`).
