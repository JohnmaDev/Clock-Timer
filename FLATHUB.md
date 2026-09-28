# 🚀 Guía de Publicación en Flathub (Flatpak)

Esta guía explica en detalle la diferencia entre **Flatpak** y **Flathub**, y el paso a paso exacto para publicar **Clock & Timer** en la tienda oficial de Linux.

---

## 1. ¿Flathub es lo mismo que Flatpak?

No son exactamente lo mismo, pero van de la mano:

| Concepto | ¿Qué es? | Equivalencia en el mundo real |
| :--- | :--- | :--- |
| **Flatpak** | Es la **tecnología / formato** de empaquetado y sandbox. Empaqueta tu app con todas sus librerías para que funcione de forma idéntica y segura en cualquier distribución de Linux (Ubuntu, Fedora, Arch, Debian, SteamOS, etc.). | Es como el formato **APK** en Android o un contenedor **Docker**. |
| **Flathub** | Es la **tienda / repositorio central** oficial donde se publican y descargan los Flatpaks. | Es como la **Google Play Store** o la **App Store**, pero abierta y comunitaria. |

> **En resumen:** Creas un **Flatpak** de tu reloj y lo publicas en **Flathub** para que millones de usuarios lo puedan instalar con un solo clic desde la tienda de software de Ubuntu, Fedora o Steam Deck.

---

## 2. ¿Aceptan este tipo de aplicaciones en Flathub?

**¡Sí, totalmente!** Flathub tiene una categoría dedicada a utilidades de escritorio (`Utility;Clock;`). Cientos de apps de nicho (temporizadores pomodoro, calculadoras flotantes, widgets de notas rápidas, monitores de recursos) son aprobadas regularmente.

Flathub solo exige:
1. ✅ **Licencia libre / Open Source** (tenemos licencia MIT en el repositorio).
2. ✅ **Identificador único de aplicación (App ID)** en formato reverse-DNS (`io.github.JohnmaDev.ClockTimer`).
3. ✅ **Archivo de metadatos AppStream válido** (`io.github.JohnmaDev.ClockTimer.metainfo.xml`), validado con `appstreamcli`.
4. ✅ **Archivo `.desktop` estándar** (`io.github.JohnmaDev.ClockTimer.desktop`).
5. ✅ **Icono PNG de 512x512** con transparencia (`io.github.JohnmaDev.ClockTimer.png`).
6. ✅ **Manifiesto de compilación Flatpak** (`io.github.JohnmaDev.ClockTimer.yaml`).

¡Tu proyecto ya cuenta con todos estos requisitos preparados y validados!

---

## 3. Paso a Paso para Enviar a Flathub

### Paso 1: Subir tu código a GitHub
Asegúrate de que tu repositorio en GitHub tenga el código y las imágenes:
```bash
git push -u origin main
```

Crea tu primer release en GitHub:
1. Ve a tu repositorio: [github.com/JohnmaDev/Clock-Timer](https://github.com/JohnmaDev/Clock-Timer)
2. Crea un Tag o Release llamado `v1.0.0`.
3. El GitHub Action que dejamos configurado compilará automáticamente los ejecutables de Linux y Windows.

---

### Paso 2: Crear el Fork de Flathub
1. Entra al repositorio oficial de Flathub: [github.com/flathub/flathub](https://github.com/flathub/flathub)
2. Haz clic en el botón superior derecho **Fork** para clonarlo a tu cuenta de GitHub (`JohnmaDev/flathub`).

---

### Paso 3: Crear una rama con tu App ID
En tu computadora o directamente en la interfaz web de GitHub de tu fork:
1. Crea una rama llamada `io.github.JohnmaDev.ClockTimer`:
   ```bash
   git clone https://github.com/JohnmaDev/flathub.git
   cd flathub
   git checkout -b io.github.JohnmaDev.ClockTimer
   ```

2. Agrega el manifiesto de la aplicación `io.github.JohnmaDev.ClockTimer.yaml`:
   Copia el archivo `io.github.JohnmaDev.ClockTimer.yaml` de este repositorio a la raíz de la rama en el fork.

3. Haz commit y push:
   ```bash
   git add io.github.JohnmaDev.ClockTimer.yaml
   git commit -m "Add io.github.JohnmaDev.ClockTimer"
   git push -u origin io.github.JohnmaDev.ClockTimer
   ```

---

### Paso 4: Abrir el Pull Request en Flathub
1. Entra a [github.com/flathub/flathub/pulls](https://github.com/flathub/flathub/pulls).
2. Haz clic en **New Pull Request**.
3. Selecciona tu rama `JohnmaDev:io.github.JohnmaDev.ClockTimer` contra `flathub:new-pr` (o `flathub:master`).
4. Ponle como título: `Add io.github.JohnmaDev.ClockTimer`.
5. En la descripción, explica brevemente:
   > *"Clock & Timer is an always-on-top, resizable floating clock and countdown timer widget with bilingual support and opacity controls."*

---

### Paso 5: Revisión automática del Bot de Flathub
1. El bot de Flathub (`@flathubbot`) compilará tu aplicación en sus servidores (x86_64 y aarch64).
2. El bot te dejará un comentario con un enlace de prueba para instalar la versión preliminar.
3. Un revisor humano de Flathub verificará que la licencia y el AppStream sean correctos.
4. Cuando aprueben el Pull Request, crearán un repositorio oficial:
   `https://github.com/flathub/io.github.JohnmaDev.ClockTimer`
   del cual serás el mantenedor oficial.

---

### Paso 6: ¡En vivo para todo el mundo! 🎉
Tu aplicación aparecerá indexada en [flathub.org](https://flathub.org) y cualquier persona en Linux podrá instalarla con:
```bash
flatpak install flathub io.github.JohnmaDev.ClockTimer
```
o buscándola directamente en la tienda de apps de Ubuntu o Fedora.
