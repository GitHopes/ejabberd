PYTHON = python3
SCRIPT = setup_ubuntu.py

.PHONY: all install-deps run clean

all: install-deps run

# 1. Paso para instalar las dependencias del sistema (Xvfb)
install-deps:
	@echo "--- Instalando Xvfb y librerías necesarias ---"
	sudo apt-get update
	sudo apt-get install -y xvfb python3-tk

# 2. Paso para ejecutar el script dentro de la pantalla virtual
run:
	@echo "--- Ejecutando el script en modo gráfico virtual ---"
	xvfb-run --auto-servernum --server-args="-screen 0 1024x768x24" $(PYTHON) $(SCRIPT)

# Opcional: Limpieza si el script genera archivos temporales
clean:
	@echo "--- Limpiando archivos temporales (si existen) ---"
	rm -rf __pycache__
