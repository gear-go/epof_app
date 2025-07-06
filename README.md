# 🧠 RAREPol - Generador de Trayectorias EPOF

## 📋 Descripción

**POC (Prueba de Concepto)** para la generación de trayectorias diagnósticas sintéticas de Enfermedades Poco Frecuentes (EPOF) utilizando Inteligencia Artificial Generativa. Desarrollado en el marco del proyecto **RAREPol** (Centro de Investigación en Enfermedades Raras y Políticas Públicas).

### 🎯 Objetivo

Crear historias clínicas realistas para acelerar el desarrollo de métodos de análisis antes de contar con datos masivos reales, permitiendo:

- 🔬 **Experimentar** con técnicas de análisis (HMM, Process Mining, redes)
- 📊 **Identificar gaps** en instrumentos de recolección
- 📈 **Desarrollar métricas** específicas para el contexto chileno
- 🎯 **Crear gold standards** para comparar con datos reales

## 🚀 Demo en Vivo

👉 **[Ver Demo](https://gear-go.github.io/epof_app/)** 

## 🛠️ Tecnologías

- **React** con Hooks
- **Tailwind CSS** para estilos
- **Lucide React** para iconos
- **Anthropic Claude API** para generación de narrativas
- **Vite** para desarrollo y build

## 🏗️ Arquitectura

### Métodos de Generación (en orden de preferencia):

1. **🚀 API Directa Anthropic**: Máxima calidad narrativa
2. **🔗 API Interna Claude**: Calidad premium integrada  
3. **💻 Fallback Local**: Demostración robusta del concepto

### Comunidades EPOF Implementadas:

- 🧬 **Metabólicas Raras**: Fibrosis quística, fenilcetonuria
- 🩸 **Hematológicas Raras**: Talasemias, anemia falciforme
- 🧠 **Neurológicas Raras**: Huntington, distrofias musculares
- 👶 **Congénitas Raras**: Marfan, Turner, Klinefelter

## 📊 Estructura de Datos Generados

Cada trayectoria incluye:

- **Demografía**: Edad, sexo, región, contexto socioeconómico
- **Narrativa**: Historia completa de la odisea diagnóstica (200-300 palabras)
- **Trayectoria Detallada**: Fechas, eventos, diagnósticos, costos
- **Métricas del Sistema**: Especialistas, hospitalizaciones, exámenes
- **Impacto Familiar**: Satisfacción, estrés financiero, calidad de vida

## 🚀 Instalación y Uso

### Prerrequisitos

- Node.js (v16 o superior)
- npm o yarn

### Pasos

1. **Clonar el repositorio**
```bash
git clone https://github.com/gear-go/epof_app.git
cd epof_app
```

2. **Instalar dependencias**
```bash
npm install
```

3. **Configurar API (opcional)**
```bash
# Editar src/components/RareDiseasePOC.jsx línea 120
# Reemplazar con tu API key de Anthropic para mejor calidad
```

4. **Ejecutar en desarrollo**
```bash
npm run dev
```

5. **Construir para producción**
```bash
npm run build
```

## 📱 Cómo Usar la Aplicación

1. **Selecciona** una comunidad de enfermedades raras
2. **Haz clic** en "Generar 3 Trayectorias"
3. **Revisa** cada historia en las tarjetas expandidas
4. **Exporta** los datos a CSV para análisis
5. **Analiza** las métricas y patrones generados

## 🎯 Casos de Uso

### Para Investigadores
- Probar algoritmos de detección de patrones
- Desarrollar dashboards y visualizaciones
- Entrenar modelos predictivos preliminares

### Para Clínicos
- Identificar puntos críticos en procesos actuales
- Proponer mejoras basadas en patrones
- Entrenar personal con casos sintéticos

### Para Formuladores de Política
- Estimar impacto de intervenciones
- Justificar inversiones con evidencia
- Modelar escenarios de mejora

## 📂 Estructura del Proyecto

```
rarepol-poc/
├── public/
│   ├── index.html
│   └── favicon.ico
├── src/
│   ├── components/
│   │   └── RareDiseasePOC.jsx
│   ├── App.jsx
│   ├── main.jsx
│   └── index.css
├── package.json
├── vite.config.js
└── README.md
```

## 🔧 Configuración Avanzada

### Variables de Entorno

```bash
# .env.local
VITE_ANTHROPIC_API_KEY=tu_api_key_aqui
VITE_APP_TITLE=RAREPol POC
```

### Personalización

- **Comunidades**: Editar `epofCommunities` en el componente
- **Regiones**: Modificar array `regions` para otros países
- **Métricas**: Ajustar cálculos en `generateUniqueTrajectory`

## 📊 Validación y Métricas

### Validación Clínica
- Revisión por genetistas del ICIM
- Contrastación con encuestas reales
- Feedback de organizaciones de pacientes

### Métricas de Calidad
- Coherencia narrativa
- Realismo de costos y tiempos
- Variabilidad regional apropiada

## 🤝 Contribuciones

¡Las contribuciones son bienvenidas! Por favor:

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit tus cambios (`git commit -m 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para detalles.

## 👥 Equipo

**Desarrollado por:** Germán Gómez Vargas, PhD  
**Proyecto:** RAREPol - Centro de Investigación en Enfermedades Raras y Políticas Públicas  
**Institución:** Universidad del Desarrollo, Instituto Data Science

**Colaboradores:**
- Dra. Gabriela Repetto (Directora ICIM)
- Dra. Isabel Matute (Especialista en trayectorias)
- Maurizio Mattoni (LSP)
- Juan Alberto Lecaros (LSP)

## 🔗 Enlaces Útiles

- [Documentación del Proyecto RAREPol](link-a-documentacion)
- [API de Anthropic](https://docs.anthropic.com/)
- [React Documentation](https://reactjs.org/)
- [Vite Documentation](https://vitejs.dev/)

## 📞 Contacto

**Email:** gagomezv@gmail.com  
**Proyecto:** RAREPol  
**Workspace:** SemanaI_2025

---

*"Transformando la investigación en enfermedades raras a través de la inteligencia artificial: de la intuición clínica a la evidencia sintética validada"*

## 🔄 Historial de Despliegues

- **📅 Julio 6, 2025**: Prueba de configuración GitHub Pages - Verificando workflow actualizado
