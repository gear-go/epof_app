# 🚀 GitHub Pages Setup Guide - EPOF App

## ⚠️ CONFIGURACIÓN CRÍTICA REQUERIDA

Para que el despliegue automático funcione correctamente, necesitas configurar GitHub Pages en el repositorio. Sigue estos pasos **EXACTAMENTE**:

### 1. 🔧 Configurar GitHub Pages

1. **Ve al repositorio**: https://github.com/gear-go/epof_app
2. **Haz clic en Settings** (en la parte superior del repositorio)
3. **Scroll hacia abajo hasta "Pages"** (en el menú lateral izquierdo)
4. **En "Source", selecciona**: `GitHub Actions` (NO selecciones "Deploy from a branch")
5. **Haz clic en "Save"**

### 2. 🛡️ Configurar Permisos de Actions

1. **En el mismo repositorio**, ve a **Settings > Actions > General**
2. **Scroll hacia abajo hasta "Workflow permissions"**
3. **Selecciona**: `Read and write permissions`
4. **Marca la casilla**: `Allow GitHub Actions to create and approve pull requests`
5. **Haz clic en "Save"**

### 3. 🔄 Verificar la Configuración

**Configuración correcta debe verse así:**

```
Settings > Pages:
├── Source: GitHub Actions ✅
└── Custom domain: (vacío) ✅

Settings > Actions > General:
├── Workflow permissions: Read and write permissions ✅
└── Allow GitHub Actions to create and approve pull requests: ✅
```

### 4. 🚀 Desplegar

Una vez configurado correctamente:

1. **Haz cualquier cambio** en el código
2. **Commit y push** a la rama `main`
3. **Ve a Actions** para ver el progreso
4. **Espera 2-3 minutos** para que se complete
5. **Visita**: https://gear-go.github.io/epof_app/

## 📋 Diagnóstico de Problemas

### Si sigue fallando:

1. **Verifica que GitHub Pages esté configurado como "GitHub Actions"**
2. **Revisa que los permisos sean "Read and write permissions"**
3. **Comprueba que el repositorio sea público**
4. **Mira los logs detallados en la pestaña Actions**

### Error común:
```
Permission to gear-go/epof_app.git denied to github-actions[bot]
```

**Solución**: Seguir exactamente los pasos 1 y 2 de arriba.

## 🔧 Configuración Técnica

### Nuevo Workflow (v2 - Recomendado)

Hemos actualizado el workflow para usar la nueva metodología de GitHub Pages:

- ✅ **Separación de jobs**: Build y Deploy separados
- ✅ **Método oficial**: Usa `actions/deploy-pages@v2`
- ✅ **Más confiable**: Mejor manejo de permisos
- ✅ **Configuración moderna**: Sigue las mejores prácticas 2024+

### Workflow anterior vs nuevo:

| Anterior | Nuevo |
|----------|--------|
| `peaceiris/actions-gh-pages@v3` | `actions/deploy-pages@v2` |
| Single job | Separate build/deploy jobs |
| Manual git push | GitHub Pages API |
| Menos confiable | Más confiable |

## 🎯 Resultado Esperado

Una vez configurado correctamente:

1. **GitHub Actions**: ✅ Passing
2. **GitHub Pages**: ✅ Deployed
3. **URL**: https://gear-go.github.io/epof_app/
4. **Tiempo de despliegue**: 2-3 minutos

## 📞 Soporte

Si sigues teniendo problemas después de seguir estos pasos:

1. **Revisa la configuración** paso a paso
2. **Verifica los logs** en GitHub Actions
3. **Asegúrate** de que el repositorio sea público
4. **Espera 5-10 minutos** después de cambiar la configuración

---

**¡Sigue estos pasos y el despliegue funcionará perfectamente!** 🎉
