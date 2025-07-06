# 🚀 Instrucciones Específicas para gear-go/epof_app

## 📋 Pasos para Subir Todo a GitHub

### 1. **Abrir Terminal en tu Directorio**
```bash
# Navegar al directorio del proyecto
cd "c:\Users\UDD\OneDrive - udd.cl\Documentos\UDD\Research\Enfermedades_Raras\GRD\Semana_I_2025"
```

### 2. **Inicializar Git y Conectar con tu Repositorio**
```bash
# Inicializar repositorio Git
git init

# Agregar todos los archivos
git add .

# Hacer commit inicial
git commit -m "🎉 Initial commit: RAREPol EPOF App - Generador de Trayectorias Sintéticas"

# Conectar con tu repositorio de GitHub
git remote add origin https://github.com/gear-go/epof_app.git

# Cambiar a branch main
git branch -M main

# Subir todo a GitHub
git push -u origin main
```

### 3. **Instalar Dependencias y Probar Localmente**
```bash
# Instalar todas las dependencias
npm install

# Probar que funciona localmente
npm run dev
```

Debería abrirse en: `http://localhost:3000`

### 4. **Construir y Desplegar a GitHub Pages**
```bash
# Construir para producción
npm run build

# Desplegar a GitHub Pages (crea automáticamente la rama gh-pages)
npm run deploy
```

### 5. **Configurar GitHub Pages**
1. Ve a: https://github.com/gear-go/epof_app/settings/pages
2. En "Source" selecciona: **Deploy from a branch**
3. En "Branch" selecciona: **gh-pages** 
4. En "Folder" deja: **/ (root)**
5. Haz clic en **Save**

### 6. **¡Tu App Estará Lista! 🎉**

**URL Final:** https://gear-go.github.io/epof_app/

---

## 🔧 Si Algo Sale Mal

### **Error: "gh-pages branch doesn't exist"**
```bash
# Crear y cambiar a rama gh-pages manualmente
git checkout -b gh-pages
git push origin gh-pages
git checkout main
npm run deploy
```

### **Error: "Permission denied"**
```bash
# Verificar que estás autenticado en GitHub
git config --global user.name "Tu Nombre"
git config --global user.email "tu-email@gmail.com"

# Si usas token personal de GitHub
git remote set-url origin https://tu-token@github.com/gear-go/epof_app.git
```

### **Error: "Module not found"**
```bash
# Limpiar caché e instalar de nuevo
rm -rf node_modules package-lock.json
npm install
```

---

## 📊 Estructura Final en GitHub

Después de seguir estos pasos tendrás:

```
https://github.com/gear-go/epof_app/
├── main branch (código fuente)
│   ├── src/
│   ├── public/
│   ├── package.json
│   ├── README.md
│   └── ...todos los archivos del proyecto
│
└── gh-pages branch (archivos compilados)
    ├── index.html
    ├── assets/
    └── ...archivos de producción
```

---

## 🎯 Verificaciones Finales

✅ **Código subido:** https://github.com/gear-go/epof_app  
✅ **App funcionando:** https://gear-go.github.io/epof_app/  
✅ **GitHub Pages activo:** Settings → Pages → Deploy from gh-pages  

---

## 📞 ¿Necesitas Ayuda?

Si algo no funciona, comparte el error específico y te ayudo a solucionarlo. Los errores más comunes son:

1. **Autenticación** - Configura tu token de GitHub
2. **Permisos** - Verifica que tienes acceso de escritura al repo
3. **Dependencias** - Asegúrate de tener Node.js v16+

¡Tu POC estará live en unos minutos! 🚀
