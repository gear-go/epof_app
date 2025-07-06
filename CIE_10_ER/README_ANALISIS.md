# 📊 Análisis de Enfermedades Raras Colombia 2023

## 🎯 Descripción
Notebook interactivo de análisis y visualización del listado oficial de enfermedades raras de Colombia 2023, con procesamiento manual y verificación mediante IA generativa.

## 📋 Fuente de Datos
**Resolución 023 de 2023 del Ministerio de Salud y Protección Social de Colombia**

## 🔬 Metodología
- **Extracción manual** de datos del documento oficial
- **Corrección de códigos CIE-10** (códigos 0→Q para malformaciones congénitas)
- **Verificación con IA generativa** (Copilot Agent mode, model Claude Sonnet 4)

## 📁 Archivos Principales

### 📊 Notebook de Análisis
- **`analisis_enfermedades_raras_colombia_2023.ipynb`** - Análisis interactivo completo

### 📄 Datasets
- **`enfermedades_raras_colombia_2023_corregido.csv`** - Dataset principal procesado
- **`enfermedades_raras_huerfanas_listado_2023_colombia.txt`** - Archivo fuente manual

### 📋 Reportes
- **`RESUMEN_EJECUTIVO_FINAL.md`** - Resumen completo del proyecto
- **`enfermedades_raras_colombia_2023_corregido_reporte.txt`** - Reporte técnico detallado

## 🚀 Cómo Usar el Notebook

### 1. Requisitos Previos
```python
# Las siguientes librerías están incluidas:
- pandas
- matplotlib 
- seaborn
- numpy
- collections
```

### 2. Ejecutar el Análisis
1. Abrir `analisis_enfermedades_raras_colombia_2023.ipynb`
2. Ejecutar todas las celdas en orden (`Run All`)
3. Las visualizaciones se generarán automáticamente

### 3. Secciones del Notebook

#### 📦 **Sección 1: Configuración**
- Importación de librerías
- Configuración de visualizaciones

#### 🔍 **Sección 2: Exploración de Datos**
- Carga del CSV procesado
- Estadísticas descriptivas básicas
- Vista general del dataset

#### 📊 **Sección 3: Distribución por Categorías CIE-10**
- Análisis de categorías médicas
- Gráficos de barras y circulares
- Distribución de frecuencias

#### 🔧 **Sección 4: Análisis de Correcciones (0→Q)**
- Impacto de correcciones aplicadas
- Visualización antes/después
- Crecimiento de categoría Q

#### ❌ **Sección 5: Enfermedades sin Código**
- Identificación de casos sin código CIE-10
- Análisis de cobertura
- Comparación con benchmarks

#### ⚖️ **Sección 6: Comparativa Metodológica**
- Procesamiento manual vs automático
- Métricas de efectividad
- Visualizaciones comparativas

#### 💡 **Sección 7: Insights y Hallazgos**
- Resultados principales
- Métricas de impacto
- Recomendaciones

#### 📚 **Sección 8: Fuente y Metodología**
- Información oficial
- Proceso de verificación
- Herramientas utilizadas

## 📈 Resultados Principales

### 🎯 **Estadísticas Clave**
- **2,249 enfermedades** procesadas
- **641 códigos CIE-10 únicos**
- **1,041 correcciones** 0→Q aplicadas
- **96.9% de cobertura** de códigos válidos

### 🏆 **Mejoras Logradas**
- **+133% más enfermedades** vs extracción automática
- **+67% más códigos únicos**
- **+1,764% crecimiento** en categoría Q (malformaciones)

### 📊 **Distribución Principal**
1. **Q (49%)** - Malformaciones congénitas
2. **E (16%)** - Enfermedades endocrinas/metabólicas  
3. **D (10.4%)** - Neoplasias benignas y sangre

## 🔬 Verificación con IA

### **Claude Sonnet 4 (Copilot Agent mode)**
- ✅ Validación de formato CIE-10
- ✅ Verificación enfermedad-código
- ✅ Control de calidad automático
- ✅ Detección de inconsistencias

## 💡 Casos de Uso

### 🏥 **Para Sistemas de Salud**
- Implementación en HIS chilenos
- Clasificación estandarizada
- Estudios epidemiológicos

### 📊 **Para Investigación**
- Análisis de prevalencia
- Estudios comparativos
- Base para publicaciones

### 🎓 **Para Educación**
- Ejemplo de procesamiento manual
- Metodología híbrida humano-IA
- Buenas prácticas en datos médicos

## 🔄 Reproducibilidad

### **Scripts Disponibles**
- `procesar_manual.py` - Procesamiento del archivo manual
- `validar_cie10.py` - Validación y limpieza
- `extraer_cie10.py` - Extracción automática (comparación)

### **Proceso Completo**
1. Extracción manual → Archivo TXT
2. Procesamiento → CSV corregido
3. Validación → Reporte de calidad
4. Análisis → Notebook interactivo

## 📋 Próximos Pasos

### **Validación Médica**
- [ ] Revisión por especialistas
- [ ] Validación cruzada
- [ ] Actualización periódica

### **Implementación**
- [ ] Integración en sistemas chilenos
- [ ] Mapeo con bases internacionales
- [ ] Capacitación a equipos

### **Expansión**
- [ ] Otros países de la región
- [ ] Actualización automática
- [ ] API de consulta

## 📞 Contacto

Para consultas sobre el análisis o la metodología, contactar al equipo de investigación en enfermedades raras UDD.

---

*Proyecto desarrollado en Enero 2025*  
*Universidad del Desarrollo - Investigación en Enfermedades Raras*
