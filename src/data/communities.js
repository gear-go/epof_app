export const communities = [
  {
    id: 'mito_disorders',
    nombre: 'Enfermedades Mitocondriales',
    enfermedades: ['Enfermedad mitocondrial, no especificada', 'Distrofia muscular'],
    cie10: ['G71.3'],
    especialidades: ['neurologia', 'genetica', 'medicina_interna'],
    // Insights del notebook GRD_Odiseas_Diagnosticas_EPOF.ipynb
    insights: {
      tiempo_promedio_diagnostico_meses: 48,
      eventos_previos_promedio: 8,
      indice_odisea: 85, // Alto
      diagnosticos_inespecificos_comunes: ['R53', 'M79.7', 'F41.9'], // Malestar y fatiga, Fibromialgia, Trastorno de ansiedad
      diagnosticos_seuelo: ['G93.3', 'F32.9'], // Síndrome de fatiga crónica, Depresión
      diagnosticos_puente: ['M62.8'] // Otros trastornos musculares especificados
    }
  },
  {
    id: 'ehlers_danlos',
    nombre: 'Síndrome de Ehlers-Danlos',
    enfermedades: ['Síndrome de Ehlers-Danlos'],
    cie10: ['Q79.6'],
    especialidades: ['reumatologia', 'genetica', 'dermatologia'],
    insights: {
      tiempo_promedio_diagnostico_meses: 60,
      eventos_previos_promedio: 12,
      indice_odisea: 92, // Muy Alto
      diagnosticos_inespecificos_comunes: ['M25.5', 'R52', 'M54.5'], // Dolor articular, Dolor no especificado, Dolor lumbar bajo
      diagnosticos_seuelo: ['M79.7', 'M35.9', 'F41.9'], // Fibromialgia, Enf. no especificada del tejido conectivo, Trastorno de ansiedad
      diagnosticos_puente: ['M35.7'] // Síndrome de hiperlaxitud
    }
  },
  {
    id: 'porphyrias',
    nombre: 'Porfirias',
    enfermedades: ['Porfiria eritropoyética', 'Porfiria cutánea tarda'],
    cie10: ['E80.0', 'E80.1'],
    especialidades: ['hematologia', 'gastroenterologia', 'dermatologia'],
    insights: {
      tiempo_promedio_diagnostico_meses: 36,
      eventos_previos_promedio: 6,
      indice_odisea: 78, // Alto
      diagnosticos_inespecificos_comunes: ['R10.4', 'K59.0', 'R11'], // Dolor abdominal, Estreñimiento, Náuseas y vómitos
      diagnosticos_seuelo: ['K80.2', 'F45.3', 'K29.7'], // Colecistitis, Trastorno somatomorfo, Gastritis
      diagnosticos_puente: ['E80.2'] // Porfiria, no especificada
    }
  },
  {
    id: 'autoinflammatory',
    nombre: 'Enfermedades Autoinflamatorias',
    enfermedades: ['Fiebre mediterránea familiar', 'Síndromes autoinflamatorios no especificados'],
    cie10: ['E85.0', 'M04.9'],
    especialidades: ['reumatologia', 'inmunologia', 'pediatria'],
    insights: {
      tiempo_promedio_diagnostico_meses: 42,
      eventos_previos_promedio: 10,
      indice_odisea: 88, // Muy Alto
      diagnosticos_inespecificos_comunes: ['R50.9', 'M25.5', 'R10.4'], // Fiebre, Dolor articular, Dolor abdominal
      diagnosticos_seuelo: ['M06.9', 'J06.9', 'L03.9'], // Artritis reumatoide, Infección respiratoria aguda, Celulitis
      diagnosticos_puente: ['D89.9'] // Trastorno inmunitario, no especificado
    }
  }
];