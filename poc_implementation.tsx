import React, { useState, useEffect } from 'react';
import { Network, AlertCircle, Users, FileText, Brain, Zap, Download, Plus, Trash2, RefreshCw } from 'lucide-react';

const RareDiseasePOC = () => {
  const [selectedCommunity, setSelectedCommunity] = useState('');
  const [generatedTrajectories, setGeneratedTrajectories] = useState([]);
  const [isGenerating, setIsGenerating] = useState(false);
  const [communities, setCommunities] = useState([]);
  const [currentPatientCount, setCurrentPatientCount] = useState(1);
  const [showCSVModal, setShowCSVModal] = useState(false);
  const [csvContent, setCsvContent] = useState('');

  const epofCommunities = {
    'metabolicas_raras': {
      name: 'Enfermedades Metabólicas Raras',
      codes: ['E84.0', 'E84.1', 'E70.0', 'E84.9'],
      description: 'Fibrosis quística, fenilcetonuria y trastornos metabólicos',
      prevalence: '1:2500',
      avgDiagnosisTime: 24,
      commonSpecialties: ['pediatria', 'genetica', 'neumologia', 'gastroenterologia']
    },
    'hematologicas_raras': {
      name: 'Enfermedades Hematológicas Raras', 
      codes: ['D56.0', 'D56.1', 'D57.0', 'D57.1'],
      description: 'Talasemias, anemia falciforme y trastornos sanguíneos',
      prevalence: '1:1000',
      avgDiagnosisTime: 18,
      commonSpecialties: ['hematologia', 'pediatria', 'medicina_interna']
    },
    'neurologicas_raras': {
      name: 'Enfermedades Neurológicas Raras',
      codes: ['G10', 'F02.2', 'G71.0'],
      description: 'Huntington, distrofias musculares',
      prevalence: '1:10000',
      avgDiagnosisTime: 60,
      commonSpecialties: ['neurologia', 'genetica', 'psiquiatria']
    },
    'congenitas_raras': {
      name: 'Malformaciones Congénitas Raras',
      codes: ['Q87.4', 'Q96.9', 'Q98.0', 'Q78.0'],
      description: 'Marfan, Turner, Klinefelter, osteogénesis imperfecta',
      prevalence: '1:5000', 
      avgDiagnosisTime: 36,
      commonSpecialties: ['genetica', 'cardiologia', 'traumatologia', 'endocrinologia']
    }
  };

  useEffect(() => {
    setCommunities(Object.entries(epofCommunities));
  }, []);

  const generateUniqueTrajectory = async (communityKey, patientNumber) => {
    const community = epofCommunities[communityKey];
    const patientId = `POC_${communityKey.substring(0,3).toUpperCase()}_${String(patientNumber).padStart(3, '0')}`;
    
    const ages = [1, 3, 7, 12, 16, 23, 28, 35, 42];
    const sexes = ['M', 'F'];
    const regions = ['Región Metropolitana', 'Valparaíso', 'Biobío', 'La Araucanía', 'Antofagasta', 'Los Lagos'];
    const socioeconomic = ['bajo', 'medio-bajo', 'medio', 'medio-alto'];
    const severities = ['leve', 'moderado', 'severo'];
    
    const randomAge = ages[Math.floor(Math.random() * ages.length)];
    const randomSex = sexes[Math.floor(Math.random() * sexes.length)];
    const randomRegion = regions[Math.floor(Math.random() * regions.length)];
    const randomSocio = socioeconomic[Math.floor(Math.random() * socioeconomic.length)];
    const randomSeverity = severities[Math.floor(Math.random() * severities.length)];

    const startDate = new Date();
    startDate.setMonth(startDate.getMonth() - Math.floor(Math.random() * 60));

    const prompt = `Eres un especialista en genética médica escribiendo un caso clínico detallado. Genera una trayectoria diagnóstica COMPLETA y REALISTA para un paciente chileno.

DATOS DEL PACIENTE:
- ID: ${patientId}
- Edad al inicio de síntomas: ${randomAge} años
- Sexo: ${randomSex}
- Región: ${randomRegion}
- Nivel socioeconómico: ${randomSocio}
- Severidad: ${randomSeverity}
- Fecha inicio síntomas: ${startDate.toISOString().split('T')[0]}

COMUNIDAD DIAGNÓSTICA: ${community.name}
- Enfermedades: ${community.description}
- Códigos CIE-10: ${community.codes.join(', ')}
- Especialidades típicas: ${community.commonSpecialties.join(', ')}

Responde ÚNICAMENTE con JSON válido en este formato:
{
  "paciente_id": "${patientId}",
  "comunidad_epof": "${communityKey}",
  "fecha_inicio_sintomas": "${startDate.toISOString().split('T')[0]}",
  "demografia": {
    "edad_inicio": ${randomAge},
    "sexo": "${randomSex}",
    "region": "${randomRegion}",
    "contexto_socioeconomico": "${randomSocio}",
    "severidad_caso": "${randomSeverity}"
  },
  "odisea_narrativa": "Narrativa completa de 200-300 palabras describiendo toda la experiencia diagnóstica",
  "resultado_final": {
    "fecha_diagnostico": "YYYY-MM-DD",
    "tiempo_diagnostico_meses": 24,
    "diagnostico_final": "Nombre completo de la enfermedad",
    "codigo_cie10_final": "código del diagnóstico final",
    "medico_diagnostico": "Dr. [Apellido], Genetista en [Hospital]",
    "metodo_diagnostico": "Exoma/Panel genético/Biopsia/etc",
    "costo_total_clp": 850000
  },
  "impacto_familiar": {
    "satisfaccion_proceso": 3.2,
    "estres_financiero": 7.5,
    "tiempo_trabajo_perdido_dias": 45,
    "calidad_vida_durante_proceso": 4.2,
    "apoyo_recibido": "Descripción del apoyo de organizaciones/familia"
  },
  "metricas_sistema": {
    "numero_especialistas": 6,
    "hospitalizaciones": 2,
    "examenes_realizados": 12,
    "derivaciones_fallidas": 3,
    "centros_visitados": 4
  }
}

NO agregues texto fuera del JSON. Solo el objeto JSON completo y válido.`;

    // Intentar primero con la API interna
    try {
      console.log('Intentando con window.claude.complete...');
      const response = await window.claude.complete(prompt);
      const result = JSON.parse(response);
      result.generacion_metodo = "API_INTERNA";
      return result;
    } catch (error) {
      console.log('API interna falló, intentando con API directa...', error);
    }

    // Intentar con API directa de Anthropic
    try {
      const response = await fetch('https://api.anthropic.com/v1/messages', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'x-api-key': 'TU_API_KEY_AQUI', // Reemplazar con tu API key
          'anthropic-version': '2023-06-01'
        },
        body: JSON.stringify({
          model: 'claude-3-sonnet-20240229',
          max_tokens: 4000,
          messages: [
            {
              role: 'user',
              content: prompt
            }
          ]
        })
      });

      if (response.ok) {
        const data = await response.json();
        const result = JSON.parse(data.content[0].text);
        result.generacion_metodo = "API_DIRECTA";
        return result;
      } else {
        console.log('API directa falló:', response.status, response.statusText);
      }
    } catch (error) {
      console.log('Error en API directa:', error);
    }

    // Fallback mejorado si ambas APIs fallan
    console.log('Usando fallback local...');
    const monthsToAdd = Math.floor(Math.random() * 36) + 6;
    const diagnosisDate = new Date(startDate);
    diagnosisDate.setMonth(diagnosisDate.getMonth() + monthsToAdd);
    
    const getPersonReference = (age, sex) => {
      if (age <= 12) return sex === 'M' ? 'el niño' : 'la niña';
      if (age <= 17) return sex === 'M' ? 'el adolescente' : 'la adolescente';
      return sex === 'M' ? 'él' : 'ella';
    };
    
    const narratives = [
      `Los primeros síntomas aparecieron cuando ${getPersonReference(randomAge, randomSex)} tenía ${randomAge} años. La familia de ${randomRegion} comenzó consultando en el sistema público local. El caso de severidad ${randomSeverity} implicó ${randomSeverity === 'severo' ? 'múltiples hospitalizaciones de urgencia y un proceso diagnóstico complejo que duró años' : randomSeverity === 'moderado' ? 'varias derivaciones entre especialistas y exámenes repetidos' : 'un proceso relativamente directo pero con algunas derivaciones innecesarias'}. La experiencia familiar fue marcada por la incertidumbre inicial, pero finalmente lograron acceder al diagnóstico correcto que cambió completamente el manejo de la condición.`,
      
      `La historia comenzó de manera sutil en ${randomRegion}, cuando la familia notó cambios en ${getPersonReference(randomAge, randomSex)} a los ${randomAge} años. El contexto socioeconómico ${randomSocio} influyó en el acceso a especialistas. Pasaron por ${randomSeverity === 'severo' ? 'un calvario de consultas, hospitalizaciones, y diagnósticos erróneos' : randomSeverity === 'moderado' ? 'un proceso extenuante con múltiples opiniones médicas' : 'algunas consultas y derivaciones hasta dar con el diagnóstico'}. La familia destaca ${randomSeverity === 'severo' ? 'el desgaste emocional y financiero extremo' : 'el apoyo crucial de las organizaciones de pacientes'} durante todo el proceso.`,
      
      `En ${randomRegion}, los síntomas iniciales a los ${randomAge} años fueron interpretados de múltiples maneras por diferentes profesionales. La gravedad ${randomSeverity} del cuadro se manifestó ${randomSeverity === 'severo' ? 'con complicaciones graves que requirieron atención de urgencia repetidamente' : randomSeverity === 'moderado' ? 'gradualmente, lo que dificultó el diagnóstico inicial' : 'de forma más evidente, facilitando el proceso diagnóstico'}. El sistema de salud público mostró ${randomSeverity === 'severo' ? 'limitaciones importantes en coordinación entre niveles' : 'funcionamiento adecuado pero con tiempos prolongados'}. Finalmente, el diagnóstico correcto permitió acceder a tratamiento especializado.`
    ];
    
    const randomNarrative = narratives[Math.floor(Math.random() * narratives.length)];
    
    return {
      paciente_id: patientId,
      comunidad_epof: communityKey,
      fecha_inicio_sintomas: startDate.toISOString().split('T')[0],
      demografia: {
        edad_inicio: randomAge,
        sexo: randomSex,
        region: randomRegion,
        contexto_socioeconomico: randomSocio,
        severidad_caso: randomSeverity
      },
      odisea_narrativa: randomNarrative,
      resultado_final: {
        fecha_diagnostico: diagnosisDate.toISOString().split('T')[0],
        tiempo_diagnostico_meses: monthsToAdd,
        diagnostico_final: `${community.description.split(',')[0]} - severidad ${randomSeverity}`,
        codigo_cie10_final: community.codes[Math.floor(Math.random() * community.codes.length)],
        medico_diagnostico: `Dr. ${['González', 'Martínez', 'López', 'Silva', 'Pérez'][Math.floor(Math.random() * 5)]}, ${community.commonSpecialties[0]} - Hospital ${randomRegion}`,
        metodo_diagnostico: randomSeverity === 'severo' ? 'Estudios genéticos complejos' : randomSeverity === 'moderado' ? 'Panel genético específico' : 'Examen clínico especializado',
        costo_total_clp: Math.floor(Math.random() * 1500000) + (randomSeverity === 'severo' ? 800000 : randomSeverity === 'moderado' ? 500000 : 300000)
      },
      impacto_familiar: {
        satisfaccion_proceso: Math.round((randomSeverity === 'severo' ? Math.random() * 2 + 2 : randomSeverity === 'moderado' ? Math.random() * 2 + 3 : Math.random() * 2 + 3.5) * 10) / 10,
        estres_financiero: Math.round((randomSeverity === 'severo' ? Math.random() * 2 + 8 : randomSeverity === 'moderado' ? Math.random() * 3 + 6 : Math.random() * 3 + 4) * 10) / 10,
        tiempo_trabajo_perdido_dias: randomSeverity === 'severo' ? Math.floor(Math.random() * 80) + 40 : randomSeverity === 'moderado' ? Math.floor(Math.random() * 40) + 20 : Math.floor(Math.random() * 20) + 10,
        calidad_vida_durante_proceso: Math.round((randomSeverity === 'severo' ? Math.random() * 3 + 2 : randomSeverity === 'moderado' ? Math.random() * 3 + 4 : Math.random() * 3 + 6) * 10) / 10,
        apoyo_recibido: `Apoyo de ${['FECHER', 'FENPOF', 'organizaciones locales', 'familia extendida', 'grupos de pacientes'][Math.floor(Math.random() * 5)]} y redes de ${randomRegion}`
      },
      metricas_sistema: {
        numero_especialistas: randomSeverity === 'severo' ? Math.floor(Math.random() * 4) + 6 : randomSeverity === 'moderado' ? Math.floor(Math.random() * 3) + 4 : Math.floor(Math.random() * 2) + 3,
        hospitalizaciones: randomSeverity === 'severo' ? Math.floor(Math.random() * 3) + 2 : randomSeverity === 'moderado' ? Math.floor(Math.random() * 2) + 1 : Math.floor(Math.random() * 2),
        examenes_realizados: randomSeverity === 'severo' ? Math.floor(Math.random() * 15) + 10 : randomSeverity === 'moderado' ? Math.floor(Math.random() * 8) + 6 : Math.floor(Math.random() * 5) + 4,
        derivaciones_fallidas: randomSeverity === 'severo' ? Math.floor(Math.random() * 4) + 2 : randomSeverity === 'moderado' ? Math.floor(Math.random() * 3) + 1 : Math.floor(Math.random() * 2),
        centros_visitados: randomSeverity === 'severo' ? Math.floor(Math.random() * 3) + 4 : randomSeverity === 'moderado' ? Math.floor(Math.random() * 2) + 3 : Math.floor(Math.random() * 2) + 2
      },
      generacion_metodo: "FALLBACK_LOCAL"
    };
  };

  const generateMultipleTrajectories = async (count = 3) => {
    if (!selectedCommunity) return;
    
    setIsGenerating(true);
    const newTrajectories = [];
    
    for (let i = 0; i < count; i++) {
      try {
        const trajectory = await generateUniqueTrajectory(selectedCommunity, currentPatientCount + i);
        newTrajectories.push(trajectory);
        await new Promise(resolve => setTimeout(resolve, 1000));
      } catch (error) {
        console.error(`Error generando trayectoria ${i + 1}:`, error);
      }
    }
    
    setGeneratedTrajectories(prev => [...prev, ...newTrajectories]);
    setCurrentPatientCount(prev => prev + count);
    setIsGenerating(false);
  };

  const exportToCSV = () => {
    if (generatedTrajectories.length === 0) return;

    const csvData = generatedTrajectories.map(trajectory => ({
      paciente_id: trajectory.paciente_id,
      comunidad: trajectory.comunidad_epof,
      fecha_inicio_sintomas: trajectory.fecha_inicio_sintomas || 'N/A',
      metodo_generacion: trajectory.generacion_metodo || 'N/A',
      edad_inicio: trajectory.demografia.edad_inicio,
      sexo: trajectory.demografia.sexo,
      region: trajectory.demografia.region,
      contexto_socioeconomico: trajectory.demografia.contexto_socioeconomico,
      severidad: trajectory.demografia.severidad_caso || 'N/A',
      odisea_narrativa: trajectory.odisea_narrativa || 'No disponible',
      fecha_diagnostico: trajectory.resultado_final?.fecha_diagnostico || 'N/A',
      tiempo_diagnostico_meses: trajectory.resultado_final.tiempo_diagnostico_meses,
      diagnostico_final: trajectory.resultado_final.diagnostico_final,
      codigo_cie10_final: trajectory.resultado_final.codigo_cie10_final,
      medico_diagnostico: trajectory.resultado_final?.medico_diagnostico || 'N/A',
      metodo_diagnostico: trajectory.resultado_final?.metodo_diagnostico || 'N/A',
      costo_total_clp: trajectory.resultado_final.costo_total_clp,
      numero_especialistas: trajectory.metricas_sistema?.numero_especialistas || 0,
      hospitalizaciones: trajectory.metricas_sistema?.hospitalizaciones || 0,
      examenes_realizados: trajectory.metricas_sistema?.examenes_realizados || 'N/A',
      derivaciones_fallidas: trajectory.metricas_sistema?.derivaciones_fallidas || 'N/A',
      centros_visitados: trajectory.metricas_sistema?.centros_visitados || 'N/A',
      satisfaccion_proceso: trajectory.impacto_familiar?.satisfaccion_proceso || 'N/A',
      estres_financiero: trajectory.impacto_familiar?.estres_financiero || 'N/A',
      tiempo_trabajo_perdido_dias: trajectory.impacto_familiar?.tiempo_trabajo_perdido_dias || 'N/A',
      calidad_vida_durante_proceso: trajectory.impacto_familiar?.calidad_vida_durante_proceso || 'N/A',
      apoyo_recibido: trajectory.impacto_familiar?.apoyo_recibido || 'N/A'
    }));

    const headers = Object.keys(csvData[0]);
    const csvText = [
      headers.join(','),
      ...csvData.map(row => headers.map(header => `"${String(row[header]).replace(/"/g, '""')}"`).join(','))
    ].join('\n');

    setCsvContent(csvText);
    setShowCSVModal(true);
  };

  const copyToClipboard = async () => {
    try {
      if (navigator.clipboard && window.isSecureContext) {
        await navigator.clipboard.writeText(csvContent);
        alert('¡CSV copiado al portapapeles! Pégalo en Excel o Google Sheets.');
      } else {
        const textArea = document.createElement('textarea');
        textArea.value = csvContent;
        textArea.style.position = 'fixed';
        textArea.style.left = '-999999px';
        textArea.style.top = '-999999px';
        document.body.appendChild(textArea);
        textArea.focus();
        textArea.select();
        document.execCommand('copy');
        textArea.remove();
        alert('¡CSV copiado al portapapeles! Pégalo en Excel o Google Sheets.');
      }
    } catch (error) {
      alert('No se pudo copiar automáticamente. Selecciona todo el texto de abajo y cópialo manualmente (Ctrl+C).');
      console.log('Error copying to clipboard:', error);
    }
  };

  const clearTrajectories = () => {
    setGeneratedTrajectories([]);
    setCurrentPatientCount(1);
  };

  const TrajectoryCard = ({ trajectory, index }) => (
    <div className="bg-white rounded-lg border p-4 mb-4 shadow-sm">
      <div className="flex justify-between items-start mb-3">
        <h3 className="text-lg font-semibold text-blue-900">
          {trajectory.paciente_id}
        </h3>
        <div className="flex gap-2">
          <span className={`px-2 py-1 rounded text-xs font-medium ${
            trajectory.demografia.severidad_caso === 'severo' ? 'bg-red-100 text-red-800' :
            trajectory.demografia.severidad_caso === 'moderado' ? 'bg-yellow-100 text-yellow-800' :
            'bg-green-100 text-green-800'
          }`}>
            {trajectory.demografia.severidad_caso || 'N/A'}
          </span>
          <span className={`px-2 py-1 rounded text-xs font-medium ${
            trajectory.generacion_metodo === 'API_DIRECTA' ? 'bg-blue-100 text-blue-800' :
            trajectory.generacion_metodo === 'API_INTERNA' ? 'bg-purple-100 text-purple-800' :
            'bg-gray-100 text-gray-800'
          }`}>
            {trajectory.generacion_metodo === 'API_DIRECTA' ? '🚀 API Directa' :
             trajectory.generacion_metodo === 'API_INTERNA' ? '🔗 API Interna' :
             '💻 Fallback Local'}
          </span>
        </div>
      </div>
      
      <div className="grid grid-cols-2 gap-4 text-sm mb-3">
        <div><span className="font-medium">Edad inicio:</span> {trajectory.demografia.edad_inicio} años</div>
        <div><span className="font-medium">Sexo:</span> {trajectory.demografia.sexo}</div>
        <div><span className="font-medium">Región:</span> {trajectory.demografia.region}</div>
        <div><span className="font-medium">Nivel SE:</span> {trajectory.demografia.contexto_socioeconomico}</div>
      </div>

      {trajectory.fecha_inicio_sintomas && (
        <div className="bg-gray-50 rounded p-3 mb-3 text-sm">
          <div className="grid grid-cols-2 gap-2">
            <div><span className="font-medium">Inicio síntomas:</span> {trajectory.fecha_inicio_sintomas}</div>
            <div><span className="font-medium">Diagnóstico:</span> {trajectory.resultado_final?.fecha_diagnostico || 'No disponible'}</div>
          </div>
        </div>
      )}

      {trajectory.odisea_narrativa && (
        <div className="bg-blue-50 rounded p-3 mb-3">
          <h4 className="text-sm font-medium text-blue-800 mb-2">📖 Historia de la Odisea Diagnóstica</h4>
          <p className="text-sm text-blue-700 leading-relaxed">{trajectory.odisea_narrativa}</p>
        </div>
      )}

      <div className="bg-green-50 rounded p-3 mb-3">
        <div className="text-sm font-medium text-green-800 mb-2">🎯 Diagnóstico Final</div>
        <div className="text-sm space-y-1">
          <div><span className="font-medium">Diagnóstico:</span> {trajectory.resultado_final.diagnostico_final}</div>
          <div><span className="font-medium">Tiempo total:</span> {trajectory.resultado_final.tiempo_diagnostico_meses} meses</div>
          <div><span className="font-medium">Médico:</span> {trajectory.resultado_final?.medico_diagnostico || 'No especificado'}</div>
          <div><span className="font-medium">Método:</span> {trajectory.resultado_final?.metodo_diagnostico || 'Examen clínico'}</div>
          <div><span className="font-medium">Costo total:</span> ${trajectory.resultado_final.costo_total_clp?.toLocaleString()} CLP</div>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-2 text-xs mb-3">
        <div className="text-center p-2 bg-gray-50 rounded">
          <div className="font-bold text-gray-800">{trajectory.metricas_sistema?.numero_especialistas || 0}</div>
          <div className="text-gray-600">Especialistas</div>
        </div>
        <div className="text-center p-2 bg-gray-50 rounded">
          <div className="font-bold text-gray-800">{trajectory.metricas_sistema?.hospitalizaciones || 0}</div>
          <div className="text-gray-600">Hospitalizaciones</div>
        </div>
        <div className="text-center p-2 bg-gray-50 rounded">
          <div className="font-bold text-gray-800">{trajectory.metricas_sistema?.examenes_realizados || 'N/A'}</div>
          <div className="text-gray-600">Exámenes</div>
        </div>
        <div className="text-center p-2 bg-gray-50 rounded">
          <div className="font-bold text-gray-800">{trajectory.metricas_sistema?.centros_visitados || 'N/A'}</div>
          <div className="text-gray-600">Centros</div>
        </div>
      </div>

      {trajectory.impacto_familiar && (
        <div className="bg-purple-50 rounded p-3">
          <h4 className="text-sm font-medium text-purple-800 mb-2">👨‍👩‍👧‍👦 Impacto Familiar</h4>
          <div className="grid grid-cols-2 gap-2 text-xs">
            <div><span className="font-medium">Satisfacción:</span> {trajectory.impacto_familiar.satisfaccion_proceso}/5</div>
            <div><span className="font-medium">Estrés financiero:</span> {trajectory.impacto_familiar.estres_financiero}/10</div>
            <div><span className="font-medium">Días trabajo perdidos:</span> {trajectory.impacto_familiar.tiempo_trabajo_perdido_dias}</div>
            <div><span className="font-medium">Calidad vida:</span> {trajectory.impacto_familiar.calidad_vida_durante_proceso}/10</div>
          </div>
          {trajectory.impacto_familiar.apoyo_recibido && (
            <div className="mt-2 text-xs text-purple-700">
              <span className="font-medium">Apoyo:</span> {trajectory.impacto_familiar.apoyo_recibido}
            </div>
          )}
        </div>
      )}
    </div>
  );

  return (
    <div className="max-w-6xl mx-auto p-6 bg-gray-50 min-h-screen">
      <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
        <div className="flex items-center mb-4">
          <Brain className="w-8 h-8 text-blue-600 mr-3" />
          <div>
            <h1 className="text-2xl font-bold text-gray-900">RAREPol - Generador de Trayectorias EPOF</h1>
            <p className="text-gray-600">Herramienta de investigación para análisis de enfermedades poco frecuentes</p>
          </div>
        </div>
      </div>

      <div className="bg-red-50 border-l-4 border-red-400 p-4 mb-6">
        <div className="flex">
          <AlertCircle className="w-5 h-5 text-red-400 mr-2 mt-0.5" />
          <div>
            <h3 className="text-lg font-medium text-red-800">⚠️ Aviso de Seguridad</h3>
            <p className="text-red-700 text-sm mt-1">
              <strong>SOLO PARA DEMOSTRACIÓN:</strong> Esta POC incluye una API key visible en el código frontend. 
              En un entorno de producción, las API keys deben estar en el backend protegidas. 
              Esta configuración es solo para testing de la metodología RAREPol.
            </p>
          </div>
        </div>
      </div>

      <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4 mb-6">
        <div className="flex">
          <AlertCircle className="w-5 h-5 text-yellow-400 mr-2 mt-0.5" />
          <div>
            <h3 className="text-lg font-medium text-yellow-800">Estado de Generación de Datos</h3>
            <p className="text-yellow-700 text-sm mt-1 mb-2">
              Esta POC intenta usar tres métodos de generación en orden de preferencia:
            </p>
            <ul className="text-yellow-700 text-sm list-disc list-inside space-y-1">
              <li><span className="font-medium">🚀 API Directa:</span> Tu API key de Anthropic - historias más sofisticadas</li>
              <li><span className="font-medium">🔗 API Interna:</span> API integrada de Claude - calidad premium</li>
              <li><span className="font-medium">💻 Fallback Local:</span> Generación local - demostración del concepto</li>
            </ul>
            <p className="text-yellow-700 text-sm mt-2">
              Cada trayectoria muestra qué método se usó. El concepto y estructura de datos son representativos del potencial completo.
            </p>
          </div>
        </div>
      </div>

      <div className="bg-blue-50 border-l-4 border-blue-400 p-4 mb-6">
        <div className="flex">
          <AlertCircle className="w-5 h-5 text-blue-400 mr-2 mt-0.5" />
          <div>
            <h3 className="text-lg font-medium text-blue-800">Instrucciones de Uso</h3>
            <ol className="text-blue-700 text-sm mt-2 list-decimal list-inside space-y-1">
              <li>Selecciona una comunidad de enfermedades raras del menú desplegable</li>
              <li>Haz clic en "Generar 3 Trayectorias" para crear historias clínicas únicas y detalladas</li>
              <li>Cada trayectoria incluye: fechas específicas, narrativa de la odisea diagnóstica, impacto familiar</li>
              <li>Revisa cada historia en las tarjetas expandidas con todos los detalles</li>
              <li>Descarga datos completos en CSV con 25+ campos para análisis estadístico</li>
              <li>Las historias son generadas por IA y varían en severidad, región, y contexto socioeconómico</li>
            </ol>
          </div>
        </div>
      </div>

      <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
        <h2 className="text-xl font-semibold mb-4">🎯 Panel de Control</h2>
        
        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Comunidad de Enfermedades Raras:
          </label>
          <select 
            value={selectedCommunity} 
            onChange={(e) => setSelectedCommunity(e.target.value)}
            className="w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          >
            <option value="">-- Selecciona una comunidad --</option>
            {communities.map(([key, community]) => (
              <option key={key} value={key}>
                {community.name} | Prevalencia: {community.prevalence} | Tiempo dx: ~{community.avgDiagnosisTime} meses
              </option>
            ))}
          </select>
        </div>

        {selectedCommunity && (
          <div className="bg-gray-50 rounded-lg p-4 mb-4">
            <h3 className="font-medium mb-2">{epofCommunities[selectedCommunity].name}</h3>
            <p className="text-sm text-gray-600 mb-2">{epofCommunities[selectedCommunity].description}</p>
            <div className="text-xs text-gray-500 space-y-1">
              <div><span className="font-medium">Códigos CIE-10:</span> {epofCommunities[selectedCommunity].codes.join(', ')}</div>
              <div><span className="font-medium">Especialidades:</span> {epofCommunities[selectedCommunity].commonSpecialties.join(', ')}</div>
            </div>
          </div>
        )}

        <div className="flex flex-wrap gap-3">
          <button
            onClick={() => generateMultipleTrajectories(3)}
            disabled={!selectedCommunity || isGenerating}
            className="bg-blue-600 text-white py-3 px-6 rounded-md hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed flex items-center"
          >
            {isGenerating ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                Generando...
              </>
            ) : (
              <>
                <Plus className="w-4 h-4 mr-2" />
                Generar 3 Trayectorias
              </>
            )}
          </button>

          <button
            onClick={() => generateMultipleTrajectories(1)}
            disabled={!selectedCommunity || isGenerating}
            className="bg-green-600 text-white py-3 px-6 rounded-md hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed flex items-center"
          >
            <Plus className="w-4 h-4 mr-2" />
            Generar 1 Más
          </button>

          <button
            onClick={exportToCSV}
            disabled={generatedTrajectories.length === 0}
            className="bg-purple-600 text-white py-3 px-6 rounded-md hover:bg-purple-700 disabled:bg-gray-400 disabled:cursor-not-allowed flex items-center"
          >
            <Download className="w-4 h-4 mr-2" />
            Ver/Copiar CSV ({generatedTrajectories.length})
          </button>

          <button
            onClick={clearTrajectories}
            disabled={generatedTrajectories.length === 0}
            className="bg-red-600 text-white py-3 px-6 rounded-md hover:bg-red-700 disabled:bg-gray-400 disabled:cursor-not-allowed flex items-center"
          >
            <Trash2 className="w-4 h-4 mr-2" />
            Limpiar Todo
          </button>
        </div>
      </div>

      {generatedTrajectories.length > 0 && (
        <div className="bg-white rounded-lg shadow-lg p-6">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-semibold">📊 Trayectorias Generadas ({generatedTrajectories.length})</h2>
            <div className="flex items-center gap-4 text-sm">
              <span className="text-gray-500">Última generación: {new Date().toLocaleTimeString()}</span>
              <div className="flex gap-2">
                {['API_DIRECTA', 'API_INTERNA', 'FALLBACK_LOCAL'].map(method => {
                  const count = generatedTrajectories.filter(t => t.generacion_metodo === method).length;
                  if (count === 0) return null;
                  return (
                    <span key={method} className={`px-2 py-1 rounded text-xs font-medium ${
                      method === 'API_DIRECTA' ? 'bg-blue-100 text-blue-800' :
                      method === 'API_INTERNA' ? 'bg-purple-100 text-purple-800' :
                      'bg-gray-100 text-gray-800'
                    }`}>
                      {method === 'API_DIRECTA' ? '🚀' : method === 'API_INTERNA' ? '🔗' : '💻'} {count}
                    </span>
                  );
                })}
              </div>
            </div>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {generatedTrajectories.map((trajectory, index) => (
              <TrajectoryCard key={trajectory.paciente_id} trajectory={trajectory} index={index} />
            ))}
          </div>
        </div>
      )}

      {showCSVModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg p-6 max-w-5xl w-full max-h-[90vh] overflow-hidden">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-semibold">📊 Datos CSV - {generatedTrajectories.length} trayectorias</h3>
              <button 
                onClick={() => setShowCSVModal(false)}
                className="text-gray-500 hover:text-gray-700 text-xl font-bold"
              >
                ✕
              </button>
            </div>
            
            <div className="mb-4 p-4 bg-blue-50 rounded-lg">
              <h4 className="font-medium text-blue-800 mb-2">📋 Instrucciones:</h4>
              <ol className="text-blue-700 text-sm list-decimal list-inside space-y-1">
                <li><strong>Opción 1:</strong> Haz clic en "Copiar CSV" y pega en Excel/Google Sheets</li>
                <li><strong>Opción 2:</strong> Selecciona todo el texto de abajo y cópialo manualmente (Ctrl+A, Ctrl+C)</li>
                <li><strong>Opción 3:</strong> Intenta "Descargar como archivo" (puede no funcionar en todos los navegadores)</li>
              </ol>
            </div>

            <div className="flex gap-3 mb-4">
              <button 
                onClick={copyToClipboard}
                className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700 flex items-center"
              >
                📋 Copiar CSV
              </button>
              <button 
                onClick={() => {
                  try {
                    const element = document.createElement('a');
                    const file = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
                    element.href = URL.createObjectURL(file);
                    element.download = `trayectorias_epof_${new Date().toISOString().split('T')[0]}.csv`;
                    document.body.appendChild(element);
                    element.click();
                    document.body.removeChild(element);
                    URL.revokeObjectURL(element.href);
                  } catch (error) {
                    alert('Descarga no disponible. Usa la opción de copiar.');
                  }
                }}
                className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 flex items-center"
              >
                💾 Descargar como archivo
              </button>
              <button 
                onClick={() => setShowCSVModal(false)}
                className="bg-gray-500 text-white px-4 py-2 rounded hover:bg-gray-600"
              >
                Cerrar
              </button>
            </div>

            <div className="border border-gray-300 rounded">
              <div className="bg-gray-100 px-3 py-2 text-sm font-medium text-gray-700">
                Datos CSV - Selecciona todo y copia (Ctrl+A, Ctrl+C)
              </div>
              <textarea 
                value={csvContent}
                readOnly
                className="w-full h-80 p-3 text-xs font-mono resize-none focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Datos CSV aparecerán aquí..."
                onClick={(e) => e.target.select()}
              />
            </div>
          </div>
        </div>
      )}

      <div className="mt-6 text-center text-sm text-gray-500">
        <p>RAREPol - Centro de Investigación en Enfermedades Raras y Políticas Públicas</p>
        <p>Universidad del Desarrollo | ICIM | Generado con Claude AI</p>
      </div>
    </div>
  );
};

export default RareDiseasePOC;