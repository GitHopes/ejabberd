#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════╗
║     Ejabberd Automation Installer — Ubuntu 24.04     ║
║     Script de instalación y configuración XMPP      ║
╚══════════════════════════════════════════════════════╝
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, font as tkfont
import subprocess
import threading
import os
import sys
import shutil
import textwrap
from pathlib import Path
from datetime import datetime

# ── Paleta de colores (terminal dark + verde neón) ────────────────────────────
BG       = "#0d1117"
BG2      = "#161b22"
BG3      = "#21262d"
ACCENT   = "#39d353"   # verde vivo
ACCENT2  = "#58a6ff"   # azul info
WARN     = "#f0883e"   # naranja advertencia
ERR      = "#f85149"   # rojo error
FG       = "#e6edf3"
FG2      = "#8b949e"
BORDER   = "#30363d"
BTN_FG   = "#0d1117"


# ══════════════════════════════════════════════════════════════════════════════
#  Utilidades de ejecución
# ══════════════════════════════════════════════════════════════════════════════

def run_cmd(cmd: str, log_fn, sudo_password: str = "") -> tuple[int, str]:
    """
    Ejecuta un comando de shell.  Si empieza por 'sudo', inyecta la contraseña
    vía stdin para evitar bloqueos en scripts no interactivos.
    Devuelve (returncode, output_combinado).
    """
    env = os.environ.copy()
    env["DEBIAN_FRONTEND"] = "noninteractive"

    use_sudo_pipe = cmd.strip().startswith("sudo ") and sudo_password

    if use_sudo_pipe:
        full = f"echo {sudo_password!r} | sudo -S {cmd.strip()[5:]}"
    else:
        full = cmd

    log_fn(f"$ {cmd}", tag="cmd")
    proc = subprocess.Popen(
        full,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        env=env,
        text=True,
    )
    output_lines = []
    for line in proc.stdout:
        line = line.rstrip()
        output_lines.append(line)
        log_fn(line, tag="out")
    proc.wait()
    return proc.returncode, "\n".join(output_lines)


# ══════════════════════════════════════════════════════════════════════════════
#  Ventana principal
# ══════════════════════════════════════════════════════════════════════════════

class EjabberdInstaller(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Ejabberd Installer · Ubuntu 24.04")
        self.configure(bg=BG)
        self.resizable(True, True)
        self.minsize(900, 680)

        # ── fuentes ──────────────────────────────────────────────────────────
        self.font_mono  = tkfont.Font(family="Monospace", size=10)
        self.font_ui    = tkfont.Font(family="Sans", size=10)
        self.font_title = tkfont.Font(family="Sans", size=13, weight="bold")
        self.font_label = tkfont.Font(family="Sans", size=9)

        self._build_ui()
        self._center()

    # ─────────────────────────────────────────────────────────────────────────
    #  Construcción de la interfaz
    # ─────────────────────────────────────────────────────────────────────────

    def _build_ui(self):
        # ── cabecera ──────────────────────────────────────────────────────────
        header = tk.Frame(self, bg=BG2, pady=12)
        header.pack(fill="x")
        tk.Label(
            header,
            text="⬡  Ejabberd XMPP Server — Instalador Automático",
            font=self.font_title,
            bg=BG2, fg=ACCENT,
        ).pack(side="left", padx=20)
        tk.Label(
            header,
            text="Ubuntu 24.04",
            font=self.font_label,
            bg=BG2, fg=FG2,
        ).pack(side="right", padx=20)

        # ── panel principal ───────────────────────────────────────────────────
        main = tk.Frame(self, bg=BG)
        main.pack(fill="both", expand=True, padx=0, pady=0)

        # columna izquierda: configuración
        left = tk.Frame(main, bg=BG2, width=320)
        left.pack(side="left", fill="y", padx=(10, 0), pady=10)
        left.pack_propagate(False)

        self._build_config_panel(left)

        # columna derecha: log + botones
        right = tk.Frame(main, bg=BG)
        right.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        self._build_log_panel(right)
        self._build_action_buttons(right)

        # ── barra de estado ───────────────────────────────────────────────────
        self.status_var = tk.StringVar(value="Listo. Configure las opciones y presione Iniciar.")
        status_bar = tk.Label(
            self,
            textvariable=self.status_var,
            bg=BG3, fg=FG2,
            font=self.font_label,
            anchor="w", padx=10, pady=5,
        )
        status_bar.pack(fill="x", side="bottom")

    # ── panel de configuración ────────────────────────────────────────────────

    def _build_config_panel(self, parent):
        def section(text):
            f = tk.Frame(parent, bg=BORDER, height=1)
            f.pack(fill="x", pady=(14, 4), padx=10)
            tk.Label(
                parent,
                text=f"  {text}",
                font=self.font_label,
                bg=BG2, fg=ACCENT2, anchor="w",
            ).pack(fill="x", padx=10)

        def labeled_entry(frame, label, default, show=None):
            tk.Label(frame, text=label, bg=BG2, fg=FG2,
                     font=self.font_label, anchor="w").pack(fill="x", padx=10, pady=(6, 0))
            var = tk.StringVar(value=default)
            e = tk.Entry(
                frame, textvariable=var, bg=BG3, fg=FG,
                insertbackground=ACCENT, relief="flat",
                font=self.font_mono, show=show or "",
            )
            e.pack(fill="x", padx=10, ipady=5)
            return var

        def check_opt(frame, label, default=True):
            var = tk.BooleanVar(value=default)
            c = tk.Checkbutton(
                frame, text=label, variable=var,
                bg=BG2, fg=FG, activebackground=BG2,
                selectcolor=BG3, font=self.font_label,
                activeforeground=ACCENT,
            )
            c.pack(anchor="w", padx=10, pady=2)
            return var

        # ── Dominio ──
        section("Dominio XMPP")
        self.domain_var = labeled_entry(parent, "Dominio principal:", "my.lab.local")
        self.extra_domain_var = labeled_entry(parent, "Dominio adicional (opcional):", "")

        # ── Certificado ──
        section("Certificado TLS")
        self.cn_var = labeled_entry(parent, "Common Name (CN):", "my.lab.local")
        self.cert_days_var = labeled_entry(parent, "Validez (días):", "365")

        # ── Base de datos ──
        section("Base de Datos")
        tk.Label(parent, text="  Tipo:", bg=BG2, fg=FG2,
                 font=self.font_label, anchor="w").pack(fill="x", padx=10, pady=(6, 0))
        self.db_type_var = tk.StringVar(value="sqlite")
        db_frame = tk.Frame(parent, bg=BG2)
        db_frame.pack(fill="x", padx=10)
        for db in ("sqlite", "pgsql", "mysql"):
            tk.Radiobutton(
                db_frame, text=db, variable=self.db_type_var, value=db,
                bg=BG2, fg=FG, activebackground=BG2,
                selectcolor=BG3, font=self.font_label,
            ).pack(side="left", padx=4)

        self.db_path_var = labeled_entry(
            parent, "Ruta SQLite:",
            "/usr/local/ejabberd/var/lib/ejabberd/ejabberd.db"
        )

        # ── /etc/hosts ──
        section("Red (sin DNS)")
        self.etc_hosts_var = check_opt(parent, "Configurar /etc/hosts", default=False)
        self.hosts_ip_var = labeled_entry(parent, "IP del servidor:", "127.0.0.1")

        # ── Opciones extra ──
        section("Opciones")
        self.systemd_var  = check_opt(parent, "Crear servicio systemd")
        self.enable_svc_var = check_opt(parent, "Activar servicio al terminar")
        self.set_perms_var = check_opt(parent, "Aplicar permisos y propietarios")

        # ── Sudo ──
        section("Autenticación")
        self.sudo_pass_var = labeled_entry(parent, "Contraseña sudo:", "", show="*")
        tk.Label(
            parent,
            text="  Se usa solo para comandos sudo.",
            bg=BG2, fg=FG2, font=self.font_label, anchor="w",
        ).pack(fill="x", padx=10)

    # ── panel de log ──────────────────────────────────────────────────────────

    def _build_log_panel(self, parent):
        tk.Label(
            parent, text="Registro de ejecución",
            font=self.font_label, bg=BG, fg=FG2, anchor="w",
        ).pack(fill="x", pady=(0, 4))

        self.log = scrolledtext.ScrolledText(
            parent,
            bg=BG2, fg=FG,
            font=self.font_mono,
            relief="flat",
            borderwidth=0,
            wrap="word",
            state="disabled",
            height=22,
        )
        self.log.pack(fill="both", expand=True)

        # etiquetas de color para el log
        self.log.tag_config("cmd",     foreground=ACCENT2)
        self.log.tag_config("out",     foreground=FG)
        self.log.tag_config("ok",      foreground=ACCENT)
        self.log.tag_config("warn",    foreground=WARN)
        self.log.tag_config("err",     foreground=ERR)
        self.log.tag_config("head",    foreground=ACCENT, font=self.font_title)
        self.log.tag_config("section", foreground=ACCENT2)

    # ── botones de acción ─────────────────────────────────────────────────────

    def _build_action_buttons(self, parent):
        btn_frame = tk.Frame(parent, bg=BG)
        btn_frame.pack(fill="x", pady=(10, 0))

        def btn(text, cmd, color=ACCENT, width=18):
            b = tk.Button(
                btn_frame, text=text,
                command=cmd,
                bg=color, fg=BTN_FG if color == ACCENT else FG,
                activebackground=color,
                activeforeground=BTN_FG,
                font=self.font_ui,
                relief="flat",
                cursor="hand2",
                width=width,
                pady=7,
            )
            b.pack(side="left", padx=(0, 8))
            return b

        self.btn_start  = btn("▶  Instalar todo",   self._start_full)
        self.btn_config = btn("⚙  Solo configurar", self._start_config_only, color=ACCENT2)
        self.btn_cert   = btn("🔒 Solo certificado", self._start_cert_only,   color=ACCENT2)
        btn("✖  Limpiar log",     self._clear_log, color=BG3, width=14)

        # barra de progreso
        self.progress = ttk.Progressbar(
            parent, mode="indeterminate", length=400
        )
        self.progress.pack(fill="x", pady=(10, 0))

    # ─────────────────────────────────────────────────────────────────────────
    #  Helpers de log / UI
    # ─────────────────────────────────────────────────────────────────────────

    def log_msg(self, text: str, tag: str = "out"):
        def _do():
            self.log.config(state="normal")
            ts = datetime.now().strftime("%H:%M:%S")
            self.log.insert("end", f"[{ts}] {text}\n", tag)
            self.log.see("end")
            self.log.config(state="disabled")
        self.after(0, _do)

    def set_status(self, text: str):
        self.after(0, lambda: self.status_var.set(text))

    def _clear_log(self):
        self.log.config(state="normal")
        self.log.delete("1.0", "end")
        self.log.config(state="disabled")

    def _set_buttons(self, enabled: bool):
        state = "normal" if enabled else "disabled"
        for b in (self.btn_start, self.btn_config, self.btn_cert):
            b.config(state=state)

    def _lock(self):
        self._set_buttons(False)
        self.progress.start(12)

    def _unlock(self):
        self._set_buttons(True)
        self.progress.stop()

    def _center(self):
        self.update_idletasks()
        w, h = 980, 700
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        self.geometry(f"{w}x{h}+{(sw-w)//2}+{(sh-h)//2}")

    # ─────────────────────────────────────────────────────────────────────────
    #  Recolección de parámetros
    # ─────────────────────────────────────────────────────────────────────────

    def _params(self) -> dict:
        domain = self.domain_var.get().strip() or "my.lab.local"
        extra  = self.extra_domain_var.get().strip()
        domains = ['"localhost"', f'"{domain}"']
        if extra:
            domains.append(f'"{extra}"')

        return {
            "domain"       : domain,
            "domains_yaml" : "\n".join(f"  - {d}" for d in domains),
            "cn"           : self.cn_var.get().strip() or domain,
            "cert_days"    : self.cert_days_var.get().strip() or "365",
            "db_type"      : self.db_type_var.get(),
            "db_path"      : self.db_path_var.get().strip(),
            "etc_hosts"    : self.etc_hosts_var.get(),
            "hosts_ip"     : self.hosts_ip_var.get().strip(),
            "systemd"      : self.systemd_var.get(),
            "enable_svc"   : self.enable_svc_var.get(),
            "set_perms"    : self.set_perms_var.get(),
            "sudo_pass"    : self.sudo_pass_var.get(),
        }

    # ─────────────────────────────────────────────────────────────────────────
    #  Puntos de entrada de los botones (lanzan hilo)
    # ─────────────────────────────────────────────────────────────────────────

    def _start_full(self):
        if not messagebox.askyesno(
            "Confirmar instalación completa",
            "Se instalarán dependencias, se compilará ejabberd y se configurará el sistema.\n"
            "¿Continuar?"
        ):
            return
        threading.Thread(target=self._run_full, daemon=True).start()

    def _start_config_only(self):
        threading.Thread(target=self._run_config_only, daemon=True).start()

    def _start_cert_only(self):
        threading.Thread(target=self._run_cert_only, daemon=True).start()

    # ─────────────────────────────────────────────────────────────────────────
    #  Pasos individuales
    # ─────────────────────────────────────────────────────────────────────────

    def _step_deps(self, p: dict):
        """Instalación de dependencias del sistema."""
        self.log_msg("━━━  PASO 1: Dependencias del sistema  ━━━", "section")
        cmds = [
            "sudo apt-get update -y",
            "sudo apt-get install -y software-properties-common",
            "sudo add-apt-repository -y ppa:rabbitmq/rabbitmq-erlang",
            "sudo apt-get update -y",
            (
                "sudo apt-get install -y build-essential libexpat1-dev libyaml-dev "
                "libssl-dev automake git erlang-dev erlang-reltool erlang-asn1 "
                "erlang-public-key erlang-ssl erlang-syntax-tools erlang-runtime-tools "
                "erlang-nox erlang-observer erlang-inets erlang-debugger erlang-wx "
                "erlang-os-mon elixir libpam0g-dev zlib1g-dev"
            ),
        ]
        for cmd in cmds:
            rc, _ = run_cmd(cmd, self.log_msg, p["sudo_pass"])
            if rc != 0:
                self.log_msg(f"⚠ Código de salida {rc} en: {cmd}", "warn")
        self.log_msg("✔ Dependencias instaladas.", "ok")

    def _step_clone(self, p: dict) -> Path:
        """Clona o actualiza el repositorio ejabberd."""
        self.log_msg("━━━  PASO 2: Obtención del código fuente  ━━━", "section")
        home = Path.home()
        ejdir = home / "ejabberd"
        if ejdir.exists():
            self.log_msg(f"Directorio {ejdir} ya existe — haciendo git pull.", "warn")
            run_cmd(f"git -C {ejdir} pull", self.log_msg)
        else:
            rc, _ = run_cmd(
                f"git clone https://github.com/processone/ejabberd.git {ejdir}",
                self.log_msg
            )
            if rc != 0:
                raise RuntimeError("Fallo al clonar el repositorio ejabberd.")
        self.log_msg("✔ Código fuente listo.", "ok")
        return ejdir

    def _step_build(self, ejdir: Path, p: dict):
        """Configura y compila ejabberd."""
        self.log_msg("━━━  PASO 3: Compilación  ━━━", "section")
        cmds = [
            f"cd {ejdir} && export CFLAGS='-O2 -std=gnu17' && "
            "./configure --prefix=/usr/local/ejabberd --enable-sqlite --enable-user=ejabberd --enable-all",
            f"cd {ejdir} && make",
            f"cd {ejdir} && sudo make install",
        ]
        for cmd in cmds:
            rc, _ = run_cmd(cmd, self.log_msg, p["sudo_pass"])
            if rc != 0:
                raise RuntimeError(f"Fallo de compilación: {cmd}")
        self.log_msg("✔ ejabberd compilado e instalado.", "ok")

    def _step_user(self, p: dict):
        """Crea el usuario del sistema ejabberd."""
        self.log_msg("━━━  PASO 4: Usuario del sistema  ━━━", "section")
        rc, out = run_cmd(
            "id ejabberd", self.log_msg, p["sudo_pass"]
        )
        if rc == 0:
            self.log_msg("Usuario 'ejabberd' ya existe.", "warn")
        else:
            run_cmd(
                "sudo useradd -m -d /var/lib/ejabberd -s /bin/bash ejabberd",
                self.log_msg, p["sudo_pass"]
            )
        self.log_msg("✔ Usuario listo.", "ok")

    def _step_yaml(self, p: dict):
        """Escribe/actualiza ejabberd.yml con los parámetros del usuario."""
        self.log_msg("━━━  PASO 5: Configuración ejabberd.yml  ━━━", "section")
        conf_path = Path("/usr/local/ejabberd/etc/ejabberd/ejabberd.yml")

        # Si el archivo no existe aún (instalación no completa), creamos una
        # versión mínima funcional.
        yaml_content = textwrap.dedent(f"""\
            ###
            ### ejabberd.yml — generado por Ejabberd Installer
            ### {datetime.now().isoformat(timespec='seconds')}
            ###

            hosts:
            {p['domains_yaml']}

            loglevel: info
            log_rotate_size: 10485760
            log_rotate_count: 1

            certfiles:
              - "/usr/local/ejabberd/etc/ejabberd/server.pem"

            listen:
              -
                port: 5222
                ip: "::"
                module: ejabberd_c2s
                max_stanza_size: 262144
                shaper: c2s_shaper
                access: c2s
                starttls_required: true
              -
                port: 5269
                ip: "::"
                module: ejabberd_s2s_in
                max_stanza_size: 524288
              -
                port: 5280
                ip: "::"
                module: ejabberd_http
                request_handlers:
                  /admin: ejabberd_web_admin
                  /api: mod_http_api
                  /bosh: mod_bosh
                  /captcha: ejabberd_captcha
                  /upload: mod_http_upload
                  /ws: ejabberd_http_ws
              -
                port: 5443
                ip: "::"
                module: ejabberd_http
                tls: true
                request_handlers:
                  /admin: ejabberd_web_admin
                  /api: mod_http_api
                  /bosh: mod_bosh
                  /upload: mod_http_upload
                  /ws: ejabberd_http_ws

            s2s_use_starttls: optional

            acl:
              local:
                user_regexp: ""
              loopback:
                ip:
                  - 127.0.0.0/8
                  - ::1/128
              admin:
                user:
                  - "admin@{p['domain']}"

            access_rules:
              local:
                allow: local
              c2s:
                deny: blocked
                allow: all
              announce:
                allow: admin
              configure:
                allow: admin
              muc_create:
                allow: local
              pubsub_createnode:
                allow: local
              register:
                allow: all
              trusted_network:
                allow: loopback

            api_permissions:
              "console commands":
                from:
                  - ejabberd_ctl
                who: all
                what: "*"
              "admin access":
                who:
                  access:
                    allow:
                      acl: loopback
                      acl: admin
                what:
                  - "*"
                  - "!stop"
                  - "!start"
              "public commands":
                who:
                  ip: 127.0.0.1/8
                what:
                  - status
                  - connected_users_number

            shaper:
              normal:
                rate: 3000
                burst_size: 20000
              fast: 100000

            shaper_rules:
              max_user_sessions: 10
              max_user_offline_messages:
                5000: admin
                100: all
              c2s_shaper:
                none: admin
                normal: all
              s2s_shaper: fast

            default_db: sql
            sql_type: {p['db_type']}
            sql_database: "{p['db_path']}"
            update_sql_schema: true

            acme:
              auto: false

            modules:
              mod_adhoc: {{}}
              mod_announce:
                access: announce
              mod_caps: {{}}
              mod_carboncopy: {{}}
              mod_client_state: {{}}
              mod_configure: {{}}
              mod_disco: {{}}
              mod_fail2ban: {{}}
              mod_http_api: {{}}
              mod_last: {{}}
              mod_mam:
                assume_mam_usage: true
                default: always
              mod_muc:
                access:
                  - allow
                access_admin:
                  - allow: admin
                access_create: muc_create
                access_persistent: muc_create
                access_mam:
                  - allow
                default_room_options:
                  mam: true
              mod_muc_admin: {{}}
              mod_offline:
                access_max_user_messages: max_user_offline_messages
              mod_ping: {{}}
              mod_pubsub:
                access_createnode: pubsub_createnode
                plugins:
                  - flat
                  - pep
                force_node_config:
                  "eu.siacs.conversations.axolotl.*":
                    access_model: open
                  "storage:bookmarks":
                    access_model: whitelist
              mod_push: {{}}
              mod_push_keepalive: {{}}
              mod_register:
                ip_access: trusted_network
              mod_roster:
                versioning: true
              mod_s2s_dialback: {{}}
              mod_shared_roster: {{}}
              mod_stream_mgmt:
                resend_on_timeout: if_offline
              mod_stun_disco: {{}}
              mod_vcard: {{}}
              mod_vcard_xupdate: {{}}
              mod_version:
                show_os: false
              mod_http_upload:
                put_url: "https://@HOST@:5443/upload"
                custom_headers:
                  "Access-Control-Allow-Origin": "https://@HOST@"
                  "Access-Control-Allow-Methods": "GET,HEAD,PUT,OPTIONS"
                  "Access-Control-Allow-Headers": "Content-Type"
        """)

        tmp = Path("/tmp/ejabberd_installer_tmp.yml")
        tmp.write_text(yaml_content)

        conf_dir = conf_path.parent
        rc, _ = run_cmd(
            f"sudo mkdir -p {conf_dir}", self.log_msg, p["sudo_pass"]
        )
        rc, _ = run_cmd(
            f"sudo cp {tmp} {conf_path}", self.log_msg, p["sudo_pass"]
        )
        tmp.unlink(missing_ok=True)

        if rc != 0:
            raise RuntimeError("No se pudo escribir ejabberd.yml")
        self.log_msg(f"✔ {conf_path} escrito correctamente.", "ok")

    def _step_cert(self, p: dict):
        """Genera certificado TLS autofirmado y crea server.pem."""
        self.log_msg("━━━  PASO 6: Certificado TLS  ━━━", "section")
        domain = p["cn"]
        days   = p["cert_days"]
        work   = Path("/tmp/ejabberd_certs")
        run_cmd(f"mkdir -p {work}", self.log_msg)

        key_file = work / "ejabberd.key"
        crt_file = work / "ejabberd.crt"
        pem_dest = "/usr/local/ejabberd/etc/ejabberd/server.pem"

        cmds = [
            (
                f'openssl req -x509 -newkey rsa:4096 -sha256 -days {days} -nodes '
                f'-keyout {key_file} -out {crt_file} '
                f'-subj "/CN={domain}" '
                f'-addext "subjectAltName=DNS:{domain}"'
            ),
            f"cat {key_file} {crt_file} | sudo tee {pem_dest} > /dev/null",
            f"sudo chmod 600 {pem_dest}",
        ]
        for cmd in cmds:
            rc, _ = run_cmd(cmd, self.log_msg, p["sudo_pass"])
            if rc != 0:
                raise RuntimeError(f"Fallo al generar certificado: {cmd}")

        # limpiar temporales
        shutil.rmtree(work, ignore_errors=True)
        self.log_msg(f"✔ server.pem generado en {pem_dest}", "ok")

    def _step_systemd(self, p: dict):
        """Crea y activa el servicio systemd."""
        self.log_msg("━━━  PASO 7: Servicio systemd  ━━━", "section")
        unit = textwrap.dedent("""\
            [Unit]
            Description=ejabberd XMPP Server
            Requires=network.target
            After=network.target

            [Service]
            Type=forking
            User=ejabberd
            Group=ejabberd
            ExecStart=/usr/local/ejabberd/sbin/ejabberdctl start
            ExecStop=/usr/local/ejabberd/sbin/ejabberdctl stop
            Restart=on-failure
            StartLimitInterval=3
            StartLimitBurst=100

            [Install]
            WantedBy=multi-user.target
        """)
        tmp = Path("/tmp/ejabberd.service")
        tmp.write_text(unit)
        dest = "/etc/systemd/system/ejabberd.service"
        run_cmd(f"sudo cp {tmp} {dest}", self.log_msg, p["sudo_pass"])
        run_cmd("sudo systemctl daemon-reload", self.log_msg, p["sudo_pass"])
        tmp.unlink(missing_ok=True)
        self.log_msg(f"✔ Servicio escrito en {dest}", "ok")

        if p["enable_svc"]:
            self.log_msg("Activando y arrancando el servicio…", "out")
            run_cmd("sudo systemctl enable --now ejabberd", self.log_msg, p["sudo_pass"])
            self.log_msg("✔ Servicio ejabberd habilitado.", "ok")

    def _step_permissions(self, p: dict):
        """Ajusta propietarios y permisos."""
        self.log_msg("━━━  PASO 8: Permisos y propietarios  ━━━", "section")
        cmds = [
            "sudo chown -R ejabberd:ejabberd /usr/local/ejabberd",
            "sudo mkdir -p /var/lib/ejabberd",
            "sudo chown -R ejabberd:ejabberd /var/lib/ejabberd",
        ]
        # El cookie solo existe si ejabberd fue arrancado al menos una vez
        cookie = Path("/var/lib/ejabberd/.erlang.cookie")
        for cmd in cmds:
            run_cmd(cmd, self.log_msg, p["sudo_pass"])
        # Solo si existe el cookie
        rc, _ = run_cmd(
            f"sudo test -f {cookie} && sudo chown ejabberd:ejabberd {cookie} "
            f"&& sudo chmod 400 {cookie} || true",
            self.log_msg, p["sudo_pass"]
        )
        self.log_msg("✔ Permisos aplicados.", "ok")

    def _step_etc_hosts(self, p: dict):
        """Agrega entrada a /etc/hosts si se eligió la opción."""
        if not p["etc_hosts"]:
            return
        self.log_msg("━━━  OPCIONAL: /etc/hosts  ━━━", "section")
        domain = p["domain"]
        ip     = p["hosts_ip"]
        entry  = f"{ip}  {domain}"

        # Revisar si ya existe
        rc, out = run_cmd(f"grep -qF '{domain}' /etc/hosts", self.log_msg)
        if rc == 0:
            self.log_msg(f"Entrada para {domain} ya existe en /etc/hosts.", "warn")
        else:
            rc, _ = run_cmd(
                f"echo '{entry}' | sudo tee -a /etc/hosts",
                self.log_msg, p["sudo_pass"]
            )
            if rc == 0:
                self.log_msg(f"✔ '{entry}' añadido a /etc/hosts.", "ok")
            else:
                self.log_msg("⚠ No se pudo editar /etc/hosts.", "warn")

    # ─────────────────────────────────────────────────────────────────────────
    #  Flujos de trabajo
    # ─────────────────────────────────────────────────────────────────────────

    def _run_full(self):
        self._lock()
        p = self._params()
        self.log_msg("╔══ INSTALACIÓN COMPLETA DE EJABBERD ══╗", "head")
        self.set_status("Instalando… por favor espere.")
        try:
            self._step_deps(p)
            ejdir = self._step_clone(p)
            self._step_build(ejdir, p)
            self._step_user(p)
            self._step_etc_hosts(p)
            self._step_yaml(p)
            self._step_cert(p)
            if p["set_perms"]:
                self._step_permissions(p)
            if p["systemd"]:
                self._step_systemd(p)
            self.log_msg("╚══ INSTALACIÓN COMPLETADA ══╝", "head")
            self.set_status("✔ Instalación completada con éxito.")
            self.after(0, lambda: messagebox.showinfo(
                "Listo", "ejabberd se instaló y configuró correctamente."
            ))
        except Exception as exc:
            self.log_msg(f"✖ ERROR: {exc}", "err")
            self.set_status(f"Error: {exc}")
            self.after(0, lambda: messagebox.showerror("Error", str(exc)))
        finally:
            self._unlock()

    def _run_config_only(self):
        self._lock()
        p = self._params()
        self.log_msg("╔══ CONFIGURACIÓN (sin compilar) ══╗", "head")
        self.set_status("Configurando…")
        try:
            self._step_user(p)
            self._step_etc_hosts(p)
            self._step_yaml(p)
            self._step_cert(p)
            if p["set_perms"]:
                self._step_permissions(p)
            if p["systemd"]:
                self._step_systemd(p)
            self.log_msg("╚══ CONFIGURACIÓN COMPLETADA ══╝", "head")
            self.set_status("✔ Configuración aplicada.")
        except Exception as exc:
            self.log_msg(f"✖ ERROR: {exc}", "err")
            self.set_status(f"Error: {exc}")
        finally:
            self._unlock()

    def _run_cert_only(self):
        self._lock()
        p = self._params()
        self.log_msg("╔══ GENERACIÓN DE CERTIFICADO TLS ══╗", "head")
        self.set_status("Generando certificado…")
        try:
            self._step_cert(p)
            if p["set_perms"]:
                self._step_permissions(p)
            self.log_msg("╚══ CERTIFICADO GENERADO ══╝", "head")
            self.set_status("✔ Certificado generado.")
        except Exception as exc:
            self.log_msg(f"✖ ERROR: {exc}", "err")
            self.set_status(f"Error: {exc}")
        finally:
            self._unlock()


# ══════════════════════════════════════════════════════════════════════════════
#  Entry point
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    if sys.platform != "linux":
        print("⚠ Este script está diseñado para Ubuntu/Linux.")
    app = EjabberdInstaller()
    app.mainloop()
