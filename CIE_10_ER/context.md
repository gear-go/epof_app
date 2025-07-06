# Contexto para Extracción de Códigos CIE-10 de Resolución Colombia

## **Objetivo de la Tarea**
Extraer todos los códigos CIE-10 y sus enfermedades correspondientes de la Resolución del Ministerio de Salud y Protección Social de Colombia sobre enfermedades huérfanas.

## **Características de los Códigos CIE-10**

### **Formato Estándar:**
- **Estructura:** Una letra seguida de tres dígitos (ejemplo: A15.2, B67.1, C78.3)
- **Primer carácter:** Siempre una letra mayúscula (A-Z)
- **Siguientes caracteres:** Tres dígitos numéricos (0-9)
- **Excepción:** El último dígito ocasionalmente puede ser una "X" (ejemplo: T45.X)

### **Ejemplos válidos:**
- A15.2, B67.1, C78.3, D12.1, E10.9, F84.0, G71.2, H35.1, I27.0, J44.1, K50.9, L93.2, M30.1, N18.6, O99.1, P27.1, Q21.3, R06.0, S72.1, T78.4, Z87.5
- T45.X, M79.X (casos especiales con X)

### **Formatos NO válidos:**
- Números solos: 123, 456
- Solo letras: ABC, XYZ  
- Más de 4 caracteres: A15.23, B67.12
- Menos de 4 caracteres: A15, B6

## **Particularidades del Documento**

### **Enfermedades sin código:**
- ⚠️ **IMPORTANTE:** Algunas enfermedades listadas NO tienen código CIE-10 asignado
- Estas aparecen en el listado pero sin código asociado
- **Instrucción:** Marcar estas como "SIN CÓDIGO" o "N/A"

### **Estructura esperada del documento:**
- Lista numerada de enfermedades
- Nombre de la enfermedad
- Código CIE-10 (cuando existe)
- Posibles sinónimos o descripciones adicionales

## **Formato de Salida Requerido**

### **Estructura CSV/Tabla:**
```
Número | Nombre_Enfermedad | Código_CIE10 | Observaciones
1 | Anemia de Fanconi | D61.0 | 
2 | Síndrome de Prader-Willi | Q87.1 |
3 | Enfermedad de Huntington | G10 |
4 | [Nombre enfermedad] | SIN CÓDIGO | Sin código asignado
```

### **Campos requeridos:**
1. **Número:** Número consecutivo en la resolución
2. **Nombre_Enfermedad:** Denominación oficial completa
3. **Código_CIE10:** Código en formato estándar o "SIN CÓDIGO"
4. **Observaciones:** Notas adicionales si existen

## **Instrucciones Específicas de Extracción**

### **Validación de códigos:**
- ✅ Verificar que cada código sigue el formato: [Letra][Dígito][Dígito].[Dígito o X]
- ✅ Asegurar que no se incluyan códigos malformados
- ✅ Distinguir entre códigos CIE-10 y otros tipos de numeración

### **Manejo de duplicados:**
- Si una enfermedad aparece múltiples veces, conservar todas las instancias
- Marcar duplicados en observaciones si es necesario

### **Sinónimos y descripciones:**
- Extraer el nombre principal de la enfermedad
- Si hay sinónimos, incluirlos en observaciones o campo separado

## **Casos Especiales a Considerar**

### **Rangos de códigos:**
- Algunos pueden aparecer como rangos (ej: A15.0-A15.9)
- **Instrucción:** Extraer como código único o expandir el rango según se requiera

### **Subcategorías:**
- Códigos con subcategorías específicas (ej: E10.1, E10.2, E10.9)
- Mantener la especificidad completa del código

### **Códigos con asterisco o comentarios:**
- Algunos códigos pueden tener anotaciones especiales
- Preservar la información adicional en observaciones

## **Control de Calidad**

### **Verificaciones finales:**
1. **Conteo total:** Verificar número total de enfermedades extraídas
2. **Códigos válidos:** Confirmar formato correcto de todos los códigos CIE-10
3. **Enfermedades sin código:** Contar y reportar cuántas no tienen código
4. **Duplicados:** Identificar posibles repeticiones

### **Reporte de resultados:**
- Total de enfermedades procesadas
- Total de códigos CIE-10 válidos extraídos  
- Total de enfermedades sin código
- Lista de códigos que requieren verificación manual

**Nota importante:** La precisión es crítica ya que estos códigos serán utilizados para mapeo de enfermedades raras en sistemas de salud chilenos.