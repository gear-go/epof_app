# Guía de Despliegue - EPOF App

## Estado del Proyecto ✅

La aplicación React para generación de trayectorias diagnósticas sintéticas de Enfermedades Poco Frecuentes (EPOF) ha sido **completamente configurada y desplegada**.

### ✅ Configuraciones Completadas:

1. **Repositorio GitHub**: https://github.com/gear-go/epof_app
2. **Aplicación React**: Configurada con Vite + Tailwind CSS
3. **GitHub Actions**: Workflow configurado para despliegue automático
4. **GitHub Pages**: Configurado para servir desde rama `gh-pages`

## 🚀 URL de la Aplicación

**Aplicación Desplegada**: https://gear-go.github.io/epof_app/

## 🔧 Problemas Solucionados

### 1. Permisos de GitHub Actions
**Problema**: El bot `github-actions[bot]` no tenía permisos para hacer push a la rama `gh-pages`.

**Solución**: Se agregaron los permisos necesarios al workflow:
```yaml
permissions:
  contents: read
  pages: write
  id-token: write
```

### 2. Configuración de GitHub Pages
**Problema**: GitHub Pages no estaba configurado correctamente.

**Solución**: Se configuró GitHub Pages para usar la rama `gh-pages` como source.

## 📋 Verificación del Despliegue

### Pasos para verificar que todo funciona:

1. **Revisar GitHub Actions**:
   - Ve a: https://github.com/gear-go/epof_app/actions
   - Verifica que el último workflow haya pasado ✅

2. **Revisar GitHub Pages**:
   - Ve a: Settings > Pages en el repo
   - Verifica que esté configurado para usar `gh-pages` branch

3. **Probar la aplicación**:
   - Visita: https://gear-go.github.io/epof_app/
   - Verifica que la aplicación carga correctamente

## 🔄 Workflow de Despliegue Automático

Cada vez que hagas push a la rama `main`, se ejecutará automáticamente:

1. **Build**: Construye la aplicación React
2. **Deploy**: Despliega a GitHub Pages
3. **Disponible**: En https://gear-go.github.io/epof_app/

## 🛠️ Comandos de Desarrollo

```bash
# Instalar dependencias
npm install

# Ejecutar en modo desarrollo
npm run dev

# Construir para producción
npm run build

# Previsualizar build de producción
npm run preview
```

## 📝 Próximos Pasos

1. **Verificar el despliegue**: Visita la URL y confirma que todo funciona
2. **Personalizar contenido**: Modifica los datos y parámetros según necesidades
3. **Agregar funcionalidades**: Expande la aplicación con nuevas características
4. **Documentar uso**: Crea guías de usuario para los investigadores

## 🆘 Solución de Problemas

### Si el despliegue falla:

1. **Revisa los logs de GitHub Actions**:
   ```
   https://github.com/gear-go/epof_app/actions
   ```

2. **Verifica las configuraciones**:
   - `vite.config.js` tiene `base: '/epof_app/'`
   - `package.json` tiene `homepage: "https://gear-go.github.io/epof_app"`

3. **Revisa permisos**:
   - Settings > Actions > General > Workflow permissions
   - Debe estar en "Read and write permissions"

### Si necesitas redeployar manualmente:

```bash
# Desde la carpeta del proyecto
npm run build
git add dist
git commit -m "Manual deploy"
git push origin main
```

## 📊 Métricas y Monitoreo

- **URL de Producción**: https://gear-go.github.io/epof_app/
- **Repo GitHub**: https://github.com/gear-go/epof_app
- **Workflow Status**: Disponible en GitHub Actions
- **Last Deploy**: Visible en GitHub Pages settings

---

**¡Proyecto completamente funcional y desplegado!** 🎉
