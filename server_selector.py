"""
Server Selector - a small GUI tool for picking which Heroes & Generals server you connect to.
"""

import ctypes
import concurrent.futures
import io
import json
import math
import os
import re
import subprocess
import sys
import threading
import urllib.request
import webbrowser

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

try:
    from PIL import Image, ImageDraw, ImageTk
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

try:
    import pystray
    TRAY_AVAILABLE = PIL_AVAILABLE
except ImportError:
    TRAY_AVAILABLE = False

APP_NAME = "ServerSelector"
VERSION = "1.2"
GITHUB_API_LATEST = "https://api.github.com/repos/HnG-Server-Picker/HnG-Server-Picker/releases/latest"
GITHUB_RELEASES_URL = "https://github.com/HnG-Server-Picker/HnG-Server-Picker/releases"
RULE_PREFIX = "ServerPicker_"
BLOCK_PORT = 25000
CONFIG_PATH = os.path.join(os.path.expanduser("~"), ".server_selector.json")
CONFIG_VERSION = 5  
SETTINGS_PATH = os.path.join(os.path.expanduser("~"), ".server_selector_settings.json")
FLAG_CACHE_DIR = os.path.join(os.path.expanduser("~"), ".server_selector_flags")

# --------------------------------------------------------------------------
# Language / translations
# --------------------------------------------------------------------------
LANGUAGES = {
    "zh": "中文",
    "en": "English",
    "de": "Deutsch",
    "ko": "한국어",
    "pt": "Português",
    "ru": "Русский",
    "es": "Español",
    "th": "ไทย",
    "vi": "Tiếng Việt",
}

STRINGS = {
    "en": {
        "app_title": "Heroes & Generals - Server Picker",
        "header_text": (
            "A latency of \"N/A\" just means that server can't be pinged directly - "
            "the server itself is fine."
        ),
        "btn_refresh": "Refresh Ping",
        "col_server": "Server",
        "col_latency": "Latency",
        "col_status": "Status",
        "btn_block_all": "Block All \u2715",
        "btn_block_selected": "Block Selected \u2715",
        "btn_unblock_all": "Unblock All \u2713",
        "btn_unblock_selected": "Unblock Selected \u2713",
        "btn_add_server": "Add Server",
        "btn_remove_server": "Remove Server",
        "lang_label": "Language:",
        "status_ready": "Ready.",
        "status_pinging": "Pinging servers...",
        "status_ping_complete": "Ping refresh complete.",
        "status_blocked_action": "Blocked",
        "status_unblocked_action": "Unblocked",
        "status_action_done": "{action} {count} server(s).",
        "status_errors": "Completed with {count} error(s). See popup.",
        "status_added": "Added '{name}'.",
        "status_removed": "Removed {count} server(s).",
        "status_closing": "Removing firewall rules before closing...",
        "msg_select_first": "Select one or more servers first (click a row; Ctrl+click for more).",
        "msg_dup_name": "A server with that name already exists.",
        "prompt_server_name": "Server name (e.g. 'Country: City'):",
        "prompt_name": "Name:",
        "prompt_ip": "IP Address:",
        "prompt_flag": "Flag / Country:",
        "btn_ok": "OK",
        "btn_cancel": "Cancel",
        "btn_save": "Save",
        "msg_ip_required": "Please enter an IP address.",
        "msg_invalid_ip": "The IP address for '{name}' doesn't look valid. Please edit it (right-click > Properties) and try again.",
        "msg_name_required": "Please enter a server name.",
        "menu_properties": "Properties",
        "status_already_blocked": "{count} server(s) already blocked.",
        "status_already_unblocked": "{count} server(s) already unblocked.",
        "row_allowed": "Unblocked",
        "row_blocked": "Blocked",
        "lat_na": "N/A",
        "lat_unit": " ms",
        "tray_open": "Show",
        "tray_quit": "Quit",
        "btn_check_update": "GitHub Releases",
        "msg_confirm_remove": "This will remove {count} server(s) from your server list. Are you sure?",
        "status_undo_done": "Restored {count} server(s).",
        "status_redo_done": "Removed {count} server(s) again.",
        "settings_title": "Settings",
        "settings_check_startup": "Check for new version on startup",
        
    },
    "zh": {
        "app_title": "英雄与将军 - 服务器选择器",
        "header_text": "延迟显示\u201cN/A\u201d只表示无法直接 ping 通该服务器 - 服务器本身没有问题。",
        "btn_refresh": "刷新延迟",
        "col_server": "服务器",
        "col_latency": "延迟",
        "col_status": "状态",
        "btn_block_all": "全部屏蔽 \u2715",
        "btn_block_selected": "屏蔽所选 \u2715",
        "btn_unblock_all": "全部取消屏蔽 \u2713",
        "btn_unblock_selected": "取消屏蔽所选 \u2713",
        "btn_add_server": "添加服务器",
        "btn_remove_server": "删除服务器",
        "lang_label": "语言：",
        "status_ready": "就绪。",
        "status_pinging": "正在测试服务器延迟...",
        "status_ping_complete": "延迟刷新完成。",
        "status_blocked_action": "已屏蔽",
        "status_unblocked_action": "已取消屏蔽",
        "status_action_done": "{action} {count} 个服务器。",
        "status_errors": "完成，其中 {count} 个出错。请查看弹窗。",
        "status_added": "已添加 \u201c{name}\u201d。",
        "status_removed": "已删除 {count} 个服务器。",
        "status_closing": "正在关闭前移除防火墙规则...",
        "msg_select_first": "请先选择一个或多个服务器（点击一行；按住 Ctrl 点击可多选）。",
        "msg_dup_name": "已存在同名的服务器。",
        "prompt_server_name": "服务器名称（例如\u201c国家：城市\u201d）：",
        "prompt_name": "名称：",
        "prompt_ip": "IP 地址：",
        "prompt_flag": "旗帜/国家：",
        "btn_ok": "确定",
        "btn_cancel": "取消",
        "btn_save": "保存",
        "msg_ip_required": "请输入 IP 地址。",
        "msg_name_required": "请输入服务器名称。",
        "menu_properties": "属性",
        "status_already_blocked": "{count} 个服务器已处于屏蔽状态。",
        "status_already_unblocked": "{count} 个服务器已处于未屏蔽状态。",
        "row_allowed": "未屏蔽",
        "row_blocked": "已屏蔽",
        "lat_na": "N/A",
        "lat_unit": " 毫秒",
        "tray_open": "打开服务器选择器",
        "tray_quit": "退出（取消屏蔽所有服务器）",
        "btn_check_update": "GitHub 发布页面",
        "msg_invalid_ip": "'{name}' 的 IP 地址似乎无效。请编辑（右键 > 属性）后重试。",
        "msg_confirm_remove": "这将永久从列表中删除 {count} 个服务器。是否继续？",
        "status_undo_done": "已恢复 {count} 个服务器。",
        "status_redo_done": "已再次删除 {count} 个服务器。",
        "settings_title": "设置",
        "settings_check_startup": "启动时检查新版本",
    },
    "de": {
        "app_title": "Heroes & Generals - Server-Auswahl",
        "header_text": (
            "Eine Latenz von \u201eN/A\u201c bedeutet nur, dass dieser Server nicht direkt "
            "angepingt werden kann - der Server selbst ist in Ordnung."
        ),
        "btn_refresh": "Ping aktualisieren",
        "col_server": "Server",
        "col_latency": "Latenz",
        "col_status": "Status",
        "btn_block_all": "Alle blockieren \u2715",
        "btn_block_selected": "Auswahl blockieren \u2715",
        "btn_unblock_all": "Alle entsperren \u2713",
        "btn_unblock_selected": "Auswahl entsperren \u2713",
        "btn_add_server": "Server hinzuf\u00fcgen",
        "btn_remove_server": "Server entfernen",
        "lang_label": "Sprache:",
        "status_ready": "Bereit.",
        "status_pinging": "Server werden angepingt...",
        "status_ping_complete": "Ping-Aktualisierung abgeschlossen.",
        "status_blocked_action": "Blockiert",
        "status_unblocked_action": "Entsperrt",
        "status_action_done": "{action}: {count} Server.",
        "status_errors": "Abgeschlossen mit {count} Fehler(n). Siehe Popup.",
        "status_added": "\u201e{name}\u201c hinzugef\u00fcgt.",
        "status_removed": "{count} Server entfernt.",
        "status_closing": "Firewall-Regeln werden vor dem Schlie\u00dfen entfernt...",
        "msg_select_first": "W\u00e4hlen Sie zuerst einen oder mehrere Server aus (Zeile anklicken; Strg+Klick f\u00fcr mehrere).",
        "msg_dup_name": "Ein Server mit diesem Namen existiert bereits.",
        "prompt_server_name": "Servername (z. B. \u201eLand: Stadt\u201c):",
        "prompt_name": "Name:",
        "prompt_ip": "IP-Adresse:",
        "prompt_flag": "Flagge / Land:",
        "btn_ok": "OK",
        "btn_cancel": "Abbrechen",
        "btn_save": "Speichern",
        "msg_ip_required": "Bitte geben Sie eine IP-Adresse ein.",
        "msg_name_required": "Bitte geben Sie einen Servernamen ein.",
        "menu_properties": "Eigenschaften",
        "status_already_blocked": "{count} Server bereits blockiert.",
        "status_already_unblocked": "{count} Server bereits entsperrt.",
        "row_allowed": "Entsperrt",
        "row_blocked": "Blockiert",
        "lat_na": "N/A",
        "lat_unit": " ms",
        "tray_open": "Server-Auswahl \u00f6ffnen",
        "tray_quit": "Beenden (entsperrt alle Server)",
        "btn_check_update": "GitHub-Releases",
        "msg_confirm_remove": "Dadurch werden {count} Server endg\u00fcltig aus Ihrer Liste entfernt. Fortfahren?",
        "status_undo_done": "{count} Server wiederhergestellt.",
        "status_redo_done": "{count} Server erneut entfernt.",
        "settings_title": "Einstellungen",
        "settings_check_startup": "Beim Start nach neuer Version suchen",
    },
    "ko": {
        "app_title": "Heroes & Generals - 서버 선택기",
        "header_text": (
            "지연 시간이 \"N/A\"로 표시되는 것은 해당 서버에 직접 핑을 보낼 수 없다는 "
            "의미일 뿐이며, 서버 자체는 정상입니다."
        ),
        "btn_refresh": "핑 새로고침",
        "col_server": "서버",
        "col_latency": "지연 시간",
        "col_status": "상태",
        "btn_block_all": "모두 차단 \u2715",
        "btn_block_selected": "선택 항목 차단 \u2715",
        "btn_unblock_all": "모두 차단 해제 \u2713",
        "btn_unblock_selected": "선택 항목 차단 해제 \u2713",
        "btn_add_server": "서버 추가",
        "btn_remove_server": "서버 삭제",
        "lang_label": "언어:",
        "status_ready": "준비됨.",
        "status_pinging": "서버 핑 확인 중...",
        "status_ping_complete": "핑 새로고침 완료.",
        "status_blocked_action": "차단됨",
        "status_unblocked_action": "차단 해제됨",
        "status_action_done": "서버 {count}개 {action}.",
        "status_errors": "{count}개의 오류와 함께 완료되었습니다. 팝업을 확인하세요.",
        "status_added": "'{name}'을(를) 추가했습니다.",
        "status_removed": "서버 {count}개를 삭제했습니다.",
        "status_closing": "종료하기 전에 방화벽 규칙을 제거하는 중...",
        "msg_select_first": "먼저 하나 이상의 서버를 선택하세요 (행을 클릭; 여러 개는 Ctrl+클릭).",
        "msg_dup_name": "해당 이름의 서버가 이미 존재합니다.",
        "prompt_server_name": "서버 이름 (예: '국가: 도시'):",
        "prompt_name": "이름:",
        "prompt_ip": "IP 주소:",
        "prompt_flag": "깃발 / 국가:",
        "btn_ok": "확인",
        "btn_cancel": "취소",
        "btn_save": "저장",
        "msg_ip_required": "IP 주소를 입력해 주세요.",
        "msg_name_required": "서버 이름을 입력해 주세요.",
        "menu_properties": "속성",
        "status_already_blocked": "{count}개의 서버가 이미 차단되어 있습니다.",
        "status_already_unblocked": "{count}개의 서버가 이미 차단 해제되어 있습니다.",
        "row_allowed": "차단 해제됨",
        "row_blocked": "차단됨",
        "lat_na": "N/A",
        "lat_unit": " ms",
        "tray_open": "서버 선택기 열기",
        "tray_quit": "종료 (모든 서버 차단 해제)",
        "btn_check_update": "GitHub 릴리스",
        "msg_confirm_remove": "이렇게 하면 목록에서 서버 {count}개가 영구적으로 제거됩니다. 계속할까요?",
        "status_undo_done": "서버 {count}개를 복원했습니다.",
        "status_redo_done": "서버 {count}개를 다시 삭제했습니다.",
        "settings_title": "설정",
        "settings_check_startup": "시작 시 새 버전 확인",
    },
    "pt": {
        "app_title": "Heroes & Generals - Seletor de Servidores",
        "header_text": (
            "Uma lat\u00eancia de \"N/A\" apenas significa que esse servidor n\u00e3o pode "
            "ser testado (ping) diretamente - o servidor em si est\u00e1 bem."
        ),
        "btn_refresh": "Atualizar Ping",
        "col_server": "Servidor",
        "col_latency": "Lat\u00eancia",
        "col_status": "Status",
        "btn_block_all": "Bloquear Tudo \u2715",
        "btn_block_selected": "Bloquear Selecionados \u2715",
        "btn_unblock_all": "Desbloquear Tudo \u2713",
        "btn_unblock_selected": "Desbloquear Selecionados \u2713",
        "btn_add_server": "Adicionar Servidor",
        "btn_remove_server": "Remover Servidor",
        "lang_label": "Idioma:",
        "status_ready": "Pronto.",
        "status_pinging": "Testando servidores (ping)...",
        "status_ping_complete": "Atualiza\u00e7\u00e3o de ping conclu\u00edda.",
        "status_blocked_action": "Bloqueado",
        "status_unblocked_action": "Desbloqueado",
        "status_action_done": "{action} {count} servidor(es).",
        "status_errors": "Conclu\u00eddo com {count} erro(s). Veja o pop-up.",
        "status_added": "'{name}' adicionado.",
        "status_removed": "{count} servidor(es) removido(s).",
        "status_closing": "Removendo regras de firewall antes de fechar...",
        "msg_select_first": "Selecione um ou mais servidores primeiro (clique numa linha; Ctrl+clique para mais).",
        "msg_dup_name": "J\u00e1 existe um servidor com esse nome.",
        "prompt_server_name": "Nome do servidor (ex.: 'Pa\u00eds: Cidade'):",
        "prompt_name": "Nome:",
        "prompt_ip": "Endere\u00e7o IP:",
        "prompt_flag": "Bandeira / Pa\u00eds:",
        "btn_ok": "OK",
        "btn_cancel": "Cancelar",
        "btn_save": "Salvar",
        "msg_ip_required": "Por favor, insira um endere\u00e7o IP.",
        "msg_name_required": "Por favor, insira um nome de servidor.",
        "menu_properties": "Propriedades",
        "status_already_blocked": "{count} servidor(es) j\u00e1 bloqueado(s).",
        "status_already_unblocked": "{count} servidor(es) j\u00e1 desbloqueado(s).",
        "row_allowed": "Desbloqueado",
        "row_blocked": "Bloqueado",
        "lat_na": "N/A",
        "lat_unit": " ms",
        "tray_open": "Abrir Seletor de Servidores",
        "tray_quit": "Sair (desbloqueia todos os servidores)",
        "btn_check_update": "Lan\u00e7amentos no GitHub",
        "msg_confirm_remove": "Isso remover\u00e1 {count} servidor(es) da sua lista permanentemente. Continuar?",
        "status_undo_done": "{count} servidor(es) restaurado(s).",
        "status_redo_done": "{count} servidor(es) removido(s) novamente.",
        "settings_title": "Configura\u00e7\u00f5es",
        "settings_check_startup": "Verificar nova vers\u00e3o ao iniciar",
    },
    "ru": {
        "app_title": "Heroes & Generals - Выбор сервера",
        "header_text": (
            "Задержка \"N/A\" означает лишь то, что этот сервер нельзя пропинговать "
            "напрямую - сам сервер в порядке."
        ),
        "btn_refresh": "Обновить пинг",
        "col_server": "Сервер",
        "col_latency": "Задержка",
        "col_status": "Статус",
        "btn_block_all": "Заблокировать все \u2715",
        "btn_block_selected": "Заблокировать выбранные \u2715",
        "btn_unblock_all": "Разблокировать все \u2713",
        "btn_unblock_selected": "Разблокировать выбранные \u2713",
        "btn_add_server": "Добавить сервер",
        "btn_remove_server": "Удалить сервер",
        "lang_label": "Язык:",
        "status_ready": "Готово.",
        "status_pinging": "Проверка пинга серверов...",
        "status_ping_complete": "Обновление пинга завершено.",
        "status_blocked_action": "Заблокировано",
        "status_unblocked_action": "Разблокировано",
        "status_action_done": "{action} серверов: {count}.",
        "status_errors": "Завершено с {count} ошибками. См. всплывающее окно.",
        "status_added": "Добавлено «{name}».",
        "status_removed": "Удалено серверов: {count}.",
        "status_closing": "Удаление правил брандмауэра перед закрытием...",
        "msg_select_first": "Сначала выберите один или несколько серверов (щёлкните строку; Ctrl+щелчок для нескольких).",
        "msg_dup_name": "Сервер с таким именем уже существует.",
        "prompt_server_name": "Название сервера (например, «Страна: Город»):",
        "prompt_name": "Имя:",
        "prompt_ip": "IP-адрес:",
        "prompt_flag": "Флаг / Страна:",
        "btn_ok": "ОК",
        "btn_cancel": "Отмена",
        "btn_save": "Сохранить",
        "msg_ip_required": "Пожалуйста, введите IP-адрес.",
        "msg_name_required": "Пожалуйста, введите имя сервера.",
        "menu_properties": "Свойства",
        "status_already_blocked": "{count} серверов уже заблокировано.",
        "status_already_unblocked": "{count} серверов уже разблокировано.",
        "row_allowed": "Разблокировано",
        "row_blocked": "Заблокировано",
        "lat_na": "N/A",
        "lat_unit": " мс",
        "tray_open": "Открыть выбор сервера",
        "tray_quit": "Выход (разблокирует все серверы)",
        "btn_check_update": "Релизы на GitHub",
        "msg_confirm_remove": "Это навсегда удалит {count} сервер(ов) из списка. Продолжить?",
        "status_undo_done": "Восстановлено серверов: {count}.",
        "status_redo_done": "Снова удалено серверов: {count}.",
        "settings_title": "Настройки",
        "settings_check_startup": "Проверять новую версию при запуске",
    },
    "es": {
        "app_title": "Heroes & Generals - Selector de Servidores",
        "header_text": (
            "Una latencia de \"N/A\" solo significa que no se puede hacer ping "
            "directamente a ese servidor - el servidor en s\u00ed est\u00e1 bien."
        ),
        "btn_refresh": "Actualizar Ping",
        "col_server": "Servidor",
        "col_latency": "Latencia",
        "col_status": "Estado",
        "btn_block_all": "Bloquear Todo \u2715",
        "btn_block_selected": "Bloquear Seleccionados \u2715",
        "btn_unblock_all": "Desbloquear Todo \u2713",
        "btn_unblock_selected": "Desbloquear Seleccionados \u2713",
        "btn_add_server": "Agregar Servidor",
        "btn_remove_server": "Eliminar Servidor",
        "lang_label": "Idioma:",
        "status_ready": "Listo.",
        "status_pinging": "Haciendo ping a los servidores...",
        "status_ping_complete": "Actualizaci\u00f3n de ping completada.",
        "status_blocked_action": "Bloqueado",
        "status_unblocked_action": "Desbloqueado",
        "status_action_done": "{action} {count} servidor(es).",
        "status_errors": "Completado con {count} error(es). Consulte la ventana emergente.",
        "status_added": "Se agreg\u00f3 '{name}'.",
        "status_removed": "Se eliminaron {count} servidor(es).",
        "status_closing": "Eliminando reglas de firewall antes de cerrar...",
        "msg_select_first": "Seleccione uno o m\u00e1s servidores primero (haga clic en una fila; Ctrl+clic para varios).",
        "msg_dup_name": "Ya existe un servidor con ese nombre.",
        "prompt_server_name": "Nombre del servidor (p. ej., 'Pa\u00eds: Ciudad'):",
        "prompt_name": "Nombre:",
        "prompt_ip": "Direcci\u00f3n IP:",
        "prompt_flag": "Bandera / Pa\u00eds:",
        "btn_ok": "OK",
        "btn_cancel": "Cancelar",
        "btn_save": "Guardar",
        "msg_ip_required": "Por favor, ingrese una direcci\u00f3n IP.",
        "msg_name_required": "Por favor, ingrese un nombre de servidor.",
        "menu_properties": "Propiedades",
        "status_already_blocked": "{count} servidor(es) ya bloqueado(s).",
        "status_already_unblocked": "{count} servidor(es) ya desbloqueado(s).",
        "row_allowed": "Desbloqueado",
        "row_blocked": "Bloqueado",
        "lat_na": "N/A",
        "lat_unit": " ms",
        "tray_open": "Abrir Selector de Servidores",
        "tray_quit": "Salir (desbloquea todos los servidores)",
        "btn_check_update": "Versiones de GitHub",
        "msg_confirm_remove": "Esto eliminar\u00e1 {count} servidor(es) de tu lista de forma permanente. \u00bfContinuar?",
        "status_undo_done": "Se restauraron {count} servidor(es).",
        "status_redo_done": "Se eliminaron {count} servidor(es) de nuevo.",
        "settings_title": "Configuraci\u00f3n",
        "settings_check_startup": "Buscar nueva versi\u00f3n al iniciar",
    },
    "th": {
        "app_title": "Heroes & Generals - ตัวเลือกเซิร์ฟเวอร์",
        "header_text": (
            "ค่าความหน่วงที่แสดงสถานะ \"N/A\" หมายความว่าไม่สามารถ ping ไปยังเซิร์ฟเวอร์ได้-แต่เซิร์ฟเวอร์ยังทำงานปกติ"
        ),
        "btn_refresh": "รีเฟรช Ping",
        "col_server": "เซิร์ฟเวอร์",
        "col_latency": "ความหน่วง",
        "col_status": "สถานะ",
        "btn_block_all": "บล็อกทั้งหมด \u2715",
        "btn_block_selected": "บล็อกที่เลือก \u2715",
        "btn_unblock_all": "ปลดบล็อกทั้งหมด \u2713",
        "btn_unblock_selected": "ปลดบล็อกที่เลือก \u2713",
        "btn_add_server": "เพิ่มเซิร์ฟเวอร์",
        "btn_remove_server": "ลบเซิร์ฟเวอร์",
        "lang_label": "ภาษา:",
        "status_ready": "พร้อม",
        "status_pinging": "กำลัง ping เซิร์ฟเวอร์...",
        "status_ping_complete": "รีเฟรช ping เสร็จสิ้น",
        "status_blocked_action": "บล็อกแล้ว",
        "status_unblocked_action": "ปลดบล็อกแล้ว",
        "status_action_done": "{action} {count} เซิร์ฟเวอร์",
        "status_errors": "เสร็จสิ้นโดยมี {count} ข้อผิดพลาด ดูป๊อปอัป",
        "status_added": "เพิ่ม '{name}' แล้ว",
        "status_removed": "ลบ {count} เซิร์ฟเวอร์แล้ว",
        "status_closing": "กำลังลบกฎไฟร์วอลล์ก่อนปิด...",
        "msg_select_first": "โปรดเลือกเซิร์ฟเวอร์หนึ่งรายการหรือมากกว่าก่อน (คลิกที่แถว; Ctrl+คลิกเพื่อเลือกหลายรายการ).",
        "msg_dup_name": "มีเซิร์ฟเวอร์ชื่อนี้อยู่แล้ว",
        "prompt_server_name": "ชื่อเซิร์ฟเวอร์ (เช่น 'ประเทศ: เมือง'):",
        "prompt_name": "ชื่อ:",
        "prompt_ip": "ที่อยู่ IP:",
        "prompt_flag": "ธง / ประเทศ:",
        "btn_ok": "ตกลง",
        "btn_cancel": "ยกเลิก",
        "btn_save": "บันทึก",
        "msg_ip_required": "โปรดกรอกที่อยู่ IP",
        "msg_name_required": "โปรดกรอกชื่อเซิร์ฟเวอร์",
        "menu_properties": "คุณสมบัติ",
        "status_already_blocked": "{count} เซิร์ฟเวอร์ถูกบล็อกอยู่แล้ว",
        "status_already_unblocked": "{count} เซิร์ฟเวอร์ถูกปลดบล็อกอยู่แล้ว",
        "row_allowed": "ปลดบล็อกแล้ว",
        "row_blocked": "บล็อกแล้ว",
        "lat_na": "N/A",
        "lat_unit": " ms",
        "tray_open": "เปิดตัวเลือกเซิร์ฟเวอร์",
        "tray_quit": "ออก (ปลดบล็อกเซิร์ฟเวอร์ทั้งหมด)",
        "btn_check_update": "รุ่นที่เผยแพร่บน GitHub",
        "msg_confirm_remove": "การดำเนินการนี้จะลบเซิร์ฟเวอร์ {count} รายการออกจากรายการอย่างถาวร ต้องการดำเนินการต่อหรือไม่?",
        "status_undo_done": "กู้คืนเซิร์ฟเวอร์ {count} รายการแล้ว",
        "status_redo_done": "ลบเซิร์ฟเวอร์ {count} รายการอีกครั้งแล้ว",
        "settings_title": "การตั้งค่า",
        "settings_check_startup": "ตรวจสอบเวอร์ชันใหม่เมื่อเริ่มต้น",
    },
    "vi": {
        "app_title": "Heroes & Generals - Bộ chọn Máy chủ",
        "header_text": (
            "Độ trễ hiển thị \"N/A\" chỉ có nghĩa là không thể ping trực tiếp đến máy chủ đó "
            "- máy chủ vẫn hoạt động bình thường."
        ),
        "btn_refresh": "Làm mới Ping",
        "col_server": "Máy chủ",
        "col_latency": "Độ trễ",
        "col_status": "Trạng thái",
        "btn_block_all": "Chặn Tất cả \u2715",
        "btn_block_selected": "Chặn Đã chọn \u2715",
        "btn_unblock_all": "Bỏ chặn Tất cả \u2713",
        "btn_unblock_selected": "Bỏ chặn Đã chọn \u2713",
        "btn_add_server": "Thêm Máy chủ",
        "btn_remove_server": "Xóa Máy chủ",
        "lang_label": "Ngôn ngữ:",
        "status_ready": "Sẵn sàng.",
        "status_pinging": "Đang ping máy chủ...",
        "status_ping_complete": "Làm mới ping hoàn tất.",
        "status_blocked_action": "Đã chặn",
        "status_unblocked_action": "Đã bỏ chặn",
        "status_action_done": "Đã {action} {count} máy chủ.",
        "status_errors": "Hoàn tất với {count} lỗi. Xem cửa sổ bật lên.",
        "status_added": "Đã thêm '{name}'.",
        "status_removed": "Đã xóa {count} máy chủ.",
        "status_closing": "Đang xóa quy tắc tường lửa trước khi đóng...",
        "msg_select_first": "Vui lòng chọn một hoặc nhiều máy chủ trước (nhấp vào dòng; Ctrl+nhấp để chọn nhiều).",
        "msg_dup_name": "Đã tồn tại máy chủ với tên đó.",
        "prompt_server_name": "Tên máy chủ (ví dụ: 'Quốc gia: Thành phố'):",
        "prompt_name": "Tên:",
        "prompt_ip": "Địa chỉ IP:",
        "prompt_flag": "Cờ / Quốc gia:",
        "btn_ok": "OK",
        "btn_cancel": "Hủy",
        "btn_save": "Lưu",
        "msg_ip_required": "Vui lòng nhập địa chỉ IP.",
        "msg_name_required": "Vui lòng nhập tên máy chủ.",
        "menu_properties": "Thuộc tính",
        "status_already_blocked": "{count} máy chủ đã bị chặn.",
        "status_already_unblocked": "{count} máy chủ đã được bỏ chặn.",
        "row_allowed": "Đã bỏ chặn",
        "row_blocked": "Đã chặn",
        "lat_na": "N/A",
        "lat_unit": " ms",
        "tray_open": "Mở Bộ chọn Máy chủ",
        "tray_quit": "Thoát (bỏ chặn tất cả máy chủ)",
        "btn_check_update": "Bản phát hành trên GitHub",
        "msg_confirm_remove": "Thao tác này sẽ xóa vĩnh viễn {count} máy chủ khỏi danh sách của bạn. Tiếp tục?",
        "status_undo_done": "Đã khôi phục {count} máy chủ.",
        "status_redo_done": "Đã xóa lại {count} máy chủ.",
        "settings_title": "Cài đặt",
        "settings_check_startup": "Kiểm tra phiên bản mới khi khởi động",
    },
}


def load_settings() -> dict:
    if os.path.exists(SETTINGS_PATH):
        try:
            with open(SETTINGS_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, dict):
                return data
        except Exception:
            pass
    return {}


def save_settings(settings: dict):
    try:
        with open(SETTINGS_PATH, "w", encoding="utf-8") as f:
            json.dump(settings, f, indent=2, ensure_ascii=False)
    except Exception:
        pass


COL_FLAG_W = 46
COL_NAME_W = 260
COL_LATENCY_W = 90
COL_STATUS_W = 110
ROW_H = 32
TABLE_W = COL_FLAG_W + COL_NAME_W + COL_LATENCY_W + COL_STATUS_W

PING_GREEN_MAX = 110
PING_YELLOW_MAX = 180
PING_RED_MAX = 230

COLOR_WHITE = "#ffffff"
COLOR_BLACK = "#000000"
COLOR_GREEN = "#2e7d32"
COLOR_GREEN_ACTIVE = "#1b5e20"
COLOR_YELLOW = "#eab308"
COLOR_RED_BRIGHT = "#ff3b30"
COLOR_PING_RED_DARK = "#7f0000"
COLOR_RED = "#c62828"
COLOR_RED_ACTIVE = "#8e1c1c"

# Known Heroes & Generals servers
DEFAULT_SERVERS = {
    "France: Roubaix 1":      {"ip": "37.187.226.17",  "region": "EU", "flag_type": "stripes", "flag_colors": ["#0055A4", "#FFFFFF", "#EF4135"], "flag_orientation": "vertical"},
    "France: Roubaix 2":      {"ip": "149.202.215.48", "region": "EU", "flag_type": "stripes", "flag_colors": ["#0055A4", "#FFFFFF", "#EF4135"], "flag_orientation": "vertical"},
    "France: Roubaix 3":      {"ip": "51.75.119.5",    "region": "EU", "flag_type": "stripes", "flag_colors": ["#0055A4", "#FFFFFF", "#EF4135"], "flag_orientation": "vertical"},
    "France: Roubaix 4":      {"ip": "51.91.74.237",   "region": "EU", "flag_type": "stripes", "flag_colors": ["#0055A4", "#FFFFFF", "#EF4135"], "flag_orientation": "vertical"},
    "France: Roubaix 5":      {"ip": "51.91.214.145",  "region": "EU", "flag_type": "stripes", "flag_colors": ["#0055A4", "#FFFFFF", "#EF4135"], "flag_orientation": "vertical"},
    "France: Roubaix 6":      {"ip": "51.91.214.138",  "region": "EU", "flag_type": "stripes", "flag_colors": ["#0055A4", "#FFFFFF", "#EF4135"], "flag_orientation": "vertical"},
    "France: Roubaix 7":      {"ip": "164.132.206.197","region": "EU", "flag_type": "stripes", "flag_colors": ["#0055A4", "#FFFFFF", "#EF4135"], "flag_orientation": "vertical"},
    "France: Roubaix 8":      {"ip": "164.132.200.214","region": "EU", "flag_type": "stripes", "flag_colors": ["#0055A4", "#FFFFFF", "#EF4135"], "flag_orientation": "vertical"},
    "Poland: Warsaw":         {"ip": "51.83.236.30",   "region": "EU", "flag_type": "stripes", "flag_colors": ["#FFFFFF", "#DC143C"], "flag_orientation": "horizontal"},
    "Germany: Wehlheiden":    {"ip": "51.77.67.200",   "region": "EU", "flag_type": "stripes", "flag_colors": ["#000000", "#DD0000", "#FFCE00"], "flag_orientation": "horizontal"},
    "Germany: Dietkirchen 1": {"ip": "51.89.21.239",   "region": "EU", "flag_type": "stripes", "flag_colors": ["#000000", "#DD0000", "#FFCE00"], "flag_orientation": "horizontal"},
    "Germany: Dietkirchen 2": {"ip": "135.125.188.83", "region": "EU", "flag_type": "stripes", "flag_colors": ["#000000", "#DD0000", "#FFCE00"], "flag_orientation": "horizontal"},
    "Germany: Dietkirchen 3": {"ip": "135.125.188.85", "region": "EU", "flag_type": "stripes", "flag_colors": ["#000000", "#DD0000", "#FFCE00"], "flag_orientation": "horizontal"},
    "Germany: Dietkirchen 4": {"ip": "135.125.188.42", "region": "EU", "flag_type": "stripes", "flag_colors": ["#000000", "#DD0000", "#FFCE00"], "flag_orientation": "horizontal"},
    "England: London 1":      {"ip": "54.37.245.86",   "region": "EU", "flag_type": "england", "flag_colors": [], "flag_orientation": "solid"},
    "England: London 2":      {"ip": "54.37.245.98",   "region": "EU", "flag_type": "england", "flag_colors": [], "flag_orientation": "solid"},
    "England: London 3":      {"ip": "145.239.204.99", "region": "EU", "flag_type": "england", "flag_colors": [], "flag_orientation": "solid"},
    "England: London 4":      {"ip": "145.239.204.144","region": "EU", "flag_type": "england", "flag_colors": [], "flag_orientation": "solid"},
    "Canada: Beauharnois":         {"ip": "144.217.77.9",   "region": "Canada", "flag_type": "stripes", "flag_colors": ["#FF0000", "#FFFFFF", "#FF0000"], "flag_orientation": "vertical"},
    "USA: Dallas":            {"ip": "23.29.125.122",  "region": "USA", "flag_type": "us", "flag_colors": [], "flag_orientation": "solid"},
    "USA: Atlanta":           {"ip": "162.213.248.83", "region": "USA", "flag_type": "us", "flag_colors": [], "flag_orientation": "solid"},
    "Australia: Sydney":      {"ip": "139.99.149.14",  "region": "APAC", "flag_type": "au", "flag_colors": [], "flag_orientation": "solid"},
    "Singapore":               {"ip": "139.99.120.230", "region": "APAC", "flag_type": "stripes", "flag_colors": ["#EF3340", "#FFFFFF"], "flag_orientation": "horizontal"},
    "Hong Kong":               {"ip": "135.136.10.86",  "region": "APAC", "flag_type": "hk", "flag_colors": [], "flag_orientation": "solid"},
}

FLAG_PRESETS = {
    "France":          {"flag_type": "stripes", "flag_colors": ["#0055A4", "#FFFFFF", "#EF4135"], "flag_orientation": "vertical"},
    "Poland":          {"flag_type": "stripes", "flag_colors": ["#FFFFFF", "#DC143C"], "flag_orientation": "horizontal"},
    "Germany":         {"flag_type": "stripes", "flag_colors": ["#000000", "#DD0000", "#FFCE00"], "flag_orientation": "horizontal"},
    "England":         {"flag_type": "england", "flag_colors": [], "flag_orientation": "solid"},
    "Canada":          {"flag_type": "stripes", "flag_colors": ["#FF0000", "#FFFFFF", "#FF0000"], "flag_orientation": "vertical"},
    "USA":             {"flag_type": "us", "flag_colors": [], "flag_orientation": "solid"},
    "Australia":       {"flag_type": "au", "flag_colors": [], "flag_orientation": "solid"},
    "Singapore":       {"flag_type": "stripes", "flag_colors": ["#EF3340", "#FFFFFF"], "flag_orientation": "horizontal"},
    "Hong Kong":       {"flag_type": "hk", "flag_colors": [], "flag_orientation": "solid"},
    "Other / Unknown": {"flag_type": "stripes", "flag_colors": ["#9AA0A6"], "flag_orientation": "solid"},
}

_FLAG_COUNTRY_CODES = {
    "France":          "fr",
    "Poland":          "pl",
    "Germany":         "de",
    "England":         "gb-eng",
    "Canada":          "ca",
    "USA":             "us",
    "Australia":       "au",
    "Singapore":       "sg",
    "Hong Kong":       "hk",
}


def get_resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


def _exe_dir():
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.abspath(".")


def is_admin() -> bool:
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except Exception:
        return False


def relaunch_as_admin():
    script_path = os.path.abspath(sys.argv[0])
    script_dir = os.path.dirname(script_path)
    extra_args = " ".join(f'"{a}"' for a in sys.argv[1:])
    params = f'"{script_path}" {extra_args}'.strip()

    executable = sys.executable
    pythonw = os.path.join(os.path.dirname(sys.executable), "pythonw.exe")
    if os.path.exists(pythonw):
        executable = pythonw

    result = ctypes.windll.shell32.ShellExecuteW(None, "runas", executable, params, script_dir, 1)
    if int(result) <= 32:
        print(f"Failed to relaunch as admin (ShellExecuteW returned {result}).")
        input("Press Enter to exit...")
    sys.exit(0)


def _is_valid_server_record(value) -> bool:
    return isinstance(value, dict) and "ip" in value and "flag_type" in value


def load_servers() -> dict:
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
            if (isinstance(data, dict)
                    and data.get("version") == CONFIG_VERSION
                    and isinstance(data.get("servers"), dict)
                    and data["servers"]
                    and all(_is_valid_server_record(v) for v in data["servers"].values())):
                return data["servers"]
        except Exception:
            pass
    servers = json.loads(json.dumps(DEFAULT_SERVERS))
    save_servers(servers)
    return servers


def save_servers(servers: dict):
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump({"version": CONFIG_VERSION, "servers": servers}, f, indent=2)


CREATE_NO_WINDOW = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0

SINGLE_RULE_NAME = f"{RULE_PREFIX}Block"


def sync_block_rule(ips) -> tuple:
    subprocess.run(
        ["netsh", "advfirewall", "firewall", "delete", "rule", f"name={SINGLE_RULE_NAME}"],
        capture_output=True, text=True, creationflags=CREATE_NO_WINDOW
    )
    if not ips:
        return True, ""
    cmd = [
        "netsh", "advfirewall", "firewall", "add", "rule",
        f"name={SINGLE_RULE_NAME}", "dir=out", "action=block", "protocol=UDP",
        f"remoteip={','.join(ips)}", f"remoteport={BLOCK_PORT}", "profile=any", "enable=yes",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, creationflags=CREATE_NO_WINDOW)
    ok = result.returncode == 0
    return ok, (result.stdout if ok else (result.stderr or result.stdout))


def cleanup_all_rules():
    subprocess.run(
        ["netsh", "advfirewall", "firewall", "delete", "rule", f"name={SINGLE_RULE_NAME}"],
        capture_output=True, text=True, creationflags=CREATE_NO_WINDOW
    )

_TIME_RE = re.compile(r"[=<]\s*(\d+)\s*ms", re.IGNORECASE)
_IPV4_RE = re.compile(r"^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})$")


def is_valid_ipv4(ip: str) -> bool:
    match = _IPV4_RE.match(ip.strip())
    if not match:
        return False
    return all(0 <= int(part) <= 255 for part in match.groups())


def ping_host(ip: str, timeout_ms: int = 1000):
    try:
        result = subprocess.run(
            ["ping", "-n", "1", "-w", str(timeout_ms), ip],
            capture_output=True, text=True,
            creationflags=CREATE_NO_WINDOW
        )
        match = _TIME_RE.search(result.stdout)
        if match:
            return int(round(float(match.group(1))))
        return None
    except Exception:
        return None


def ping_color(ms):
    if ms is None:
        return COLOR_BLACK
    if ms <= PING_GREEN_MAX:
        return COLOR_GREEN
    elif ms <= PING_YELLOW_MAX:
        return COLOR_YELLOW
    elif ms <= PING_RED_MAX:
        return COLOR_RED_BRIGHT
    else:
        return COLOR_PING_RED_DARK


def _region_group(name: str, info: dict) -> int:
    region = info.get("region", "")
    if region == "EU":
        return 0
    if region in ("USA", "Canada"):
        return 1
    if region == "APAC":
        if info.get("flag_type") == "au" or name.startswith("Australia"):
            return 3
        return 2
    return 4


def _country_code_for_server(name: str, info: dict) -> str:
    """Best-effort: check name prefix then flag_type fallback."""
    for country, code in _FLAG_COUNTRY_CODES.items():
        if name.startswith(country):
            return code
    ft = info.get("flag_type", "")
    return {
        "us": "us", "au": "au", "hk": "hk", "england": "gb-eng",
    }.get(ft, "")


def _fetch_flag_png(country_code: str, width: int = 40):
    """Download a PNG from flagcdn.com and return the raw bytes, or None on failure."""
    if not country_code:
        return None
    os.makedirs(FLAG_CACHE_DIR, exist_ok=True)
    cache_file = os.path.join(FLAG_CACHE_DIR, f"{country_code}_{width}.png")
    if os.path.exists(cache_file):
        with open(cache_file, "rb") as f:
            return f.read()
    url = f"https://flagcdn.com/w{width}/{country_code}.png"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "HnG-ServerPicker/1"})
        with urllib.request.urlopen(req, timeout=6) as resp:
            data = resp.read()
        with open(cache_file, "wb") as f:
            f.write(data)
        return data
    except Exception:
        return None


def make_flag_image(info: dict, name: str = "", width: int = 40, height: int = 26):
    if PIL_AVAILABLE:
        code = _country_code_for_server(name, info)
        if code:
            data = _fetch_flag_png(code, width=width * 4)  # fetch 4x - detailed flags (AU, GB-ENG, FR) need the extra source resolution to downscale cleanly
            if data:
                try:
                    img = Image.open(io.BytesIO(data)).convert("RGBA")
                    img = img.resize((width, height), Image.LANCZOS)
                    draw = ImageDraw.Draw(img)
                    draw.rectangle(
                        [0, 0, width - 1, height - 1],
                        outline=(0, 0, 0, 130), width=1
                    )
                    return ImageTk.PhotoImage(img)
                except Exception:
                    pass

    # Fallback: plain grey box with a thin border
    img = tk.PhotoImage(width=width, height=height)
    img.put("#9AA0A6", to=(0, 0, width, height))
    img.put("#888888", to=(0, 0, width, 1))
    img.put("#888888", to=(0, height - 1, width, height))
    img.put("#888888", to=(0, 0, 1, height))
    img.put("#888888", to=(width - 1, 0, width, height))
    return img


class FlagPickerDialog(simpledialog.Dialog):
    
    def __init__(self, parent, title, prompt, values, initial=None):
        self.prompt = prompt
        self.values = values
        self.initial = initial if initial in values else values[0]
        self.result = None
        super().__init__(parent, title)

    def body(self, master):
        tk.Label(master, text=self.prompt, justify="left").grid(
            row=0, column=0, padx=5, pady=(5, 8), sticky="w"
        )
        self.var = tk.StringVar(value=self.initial)
        self.combo = ttk.Combobox(
            master, textvariable=self.var, values=self.values,
            state="readonly", width=24
        )
        self.combo.grid(row=1, column=0, padx=5, pady=(0, 5), sticky="ew")
        return self.combo

    def apply(self):
        self.result = self.var.get()


class SettingsDialog(tk.Toplevel):

    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app

        self.title(app.tr("settings_title"))
        self.configure(bg=COLOR_WHITE)
        self.resizable(False, False)
        try:
            self.iconbitmap(get_resource_path("my_logo.ico"))
        except Exception:
            pass

        body = tk.Frame(self, bg=COLOR_WHITE)
        body.pack(fill="both", expand=True, padx=18, pady=16)

        self.check_startup_var = tk.BooleanVar(
            value=app._settings.get("check_updates_on_startup", True)
        )
        tk.Checkbutton(
            body, text=app.tr("settings_check_startup"), variable=self.check_startup_var,
            bg=COLOR_WHITE, fg=COLOR_BLACK, activebackground=COLOR_WHITE, anchor="w",
            command=self._on_toggle_check_startup,
        ).pack(anchor="w")

        tk.Button(body, text=app.tr("btn_ok"), command=self.destroy).pack(anchor="e", pady=(16, 0))

        self.protocol("WM_DELETE_WINDOW", self.destroy)

        self.update_idletasks()
        w, h = self.winfo_width(), self.winfo_height()
        px, py = parent.winfo_rootx(), parent.winfo_rooty()
        pw, ph = parent.winfo_width(), parent.winfo_height()
        x = px + (pw - w) // 2
        y = py + (ph - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")
        self.lift()

    def _on_toggle_check_startup(self):
        self.app._settings["check_updates_on_startup"] = self.check_startup_var.get()
        save_settings(self.app._settings)


class ServerSelectorApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.withdraw()
        self._style = ttk.Style(self)
        try:

            self._style.theme_use("clam")
        except Exception:
            pass
        try:
            self._style.map(
                "TCombobox",
                fieldbackground=[("readonly", COLOR_WHITE)],
                selectbackground=[("readonly", COLOR_WHITE), ("!disabled", COLOR_WHITE)],
                selectforeground=[("readonly", COLOR_BLACK), ("!disabled", COLOR_BLACK)],
                foreground=[("readonly", COLOR_BLACK)],
                background=[("readonly", COLOR_WHITE)],
            )
        except Exception:
            pass
        try:
            self._style.configure(
                "Fat.Vertical.TScrollbar",
                gripcount=0, width=16, arrowsize=16,
                background="#c1c1c1", troughcolor="#f0f0f0", bordercolor="#f0f0f0",
                relief="flat",
            )
            self._style.map("Fat.Vertical.TScrollbar", background=[("!disabled", "#c1c1c1")])
        except Exception:
            pass

        try:
            my_app_id = "serverselector.hng.1.1"
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(my_app_id)
        except Exception:
            pass

        self._settings = load_settings()
        self.language = self._settings.get("language", "en")
        if self.language not in LANGUAGES:
            self.language = "en"
        self.title(self.tr("app_title"))

        try:
            icon_path_ico = get_resource_path("my_logo.ico")
            self.iconbitmap(icon_path_ico)
        except Exception:
            pass

        self._tray_pil_image = None
        try:
            if not PIL_AVAILABLE:
                raise RuntimeError("PIL/Pillow not available - was it bundled into the build?")
            icon_path_png = get_resource_path("my_logo.png")
            base_img = Image.open(icon_path_png).convert("RGBA")

            sizes = [16, 20, 24, 32, 40, 48, 64, 96, 128, 256]
            self._icon_photos = []
            for s in sizes:
                resized = base_img.resize((s, s), Image.LANCZOS)
                self._icon_photos.append(ImageTk.PhotoImage(resized))

            self.iconphoto(True, *self._icon_photos)
            self._tray_pil_image = base_img.resize((64, 64), Image.LANCZOS)
        except Exception:
            pass

        self.resizable(True, True)
        self.configure(bg=COLOR_WHITE)

        win_w, win_h = TABLE_W + 40, 520
        self.minsize(TABLE_W + 30, 360)
        self.update_idletasks()
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()
        x = (screen_w - win_w) // 2
        y = (screen_h - win_h) // 2
        self.geometry(f"{win_w}x{win_h}+{x}+{y}")

        self.servers = load_servers()
        self.latencies = {name: None for name in self.servers}
        self.blocked_state = {name: False for name in self.servers}
        self.best_ping_name = None
        self.tray_icon = None
        self._flag_images = {}
        self.selected = set()
        self.row_frames = {}
        self.status_cells = {}
        self.header_labels = {}
        saved_sort = self._settings.get("sort_state")
        if (isinstance(saved_sort, dict)
                and saved_sort.get("column") in ("name", "ping", "status")
                and isinstance(saved_sort.get("reverse"), bool)):
            self.sort_state = saved_sort
        else:
            self.sort_state = {"column": "name", "reverse": False}
        self._last_clicked_name = None
        self._undo_stack = []  
        self._redo_stack = []  

        self._build_ui()
        self._render_rows()
        self._update_header_labels()
        self.protocol("WM_DELETE_WINDOW", self._on_close)

        # Arrow-key navigation between server rows
        self.bind_all("<Up>", self._on_arrow_up)
        self.bind_all("<Down>", self._on_arrow_down)

        # Undo / redo for server removal
        self.bind_all("<Control-z>", self._undo_last_action)
        self.bind_all("<Control-y>", self._redo_last_action)

        self.after(150, self.refresh_pings)
        threading.Thread(target=self._check_for_updates, daemon=True).start()
        # Restore previously blocked servers (persisted across restarts)
        self.after(200, self._restore_blocked_state)

        self._start_tray_icon()

        # Pre-warm the flag image cache in the background so real flags swap in without freezing the UI on first launch.
        threading.Thread(target=self._prefetch_flags, daemon=True).start()

        self.deiconify()

    def tr(self, key, **kwargs):
        lang_dict = STRINGS.get(self.language, STRINGS["en"])
        text = lang_dict.get(key, STRINGS["en"].get(key, key))
        if kwargs:
            text = text.format(**kwargs)
        return text

    def _build_ui(self):
        header = tk.Label(
            self, bg=COLOR_WHITE, fg=COLOR_BLACK, justify="left", anchor="w",
            text=self.tr("header_text", port=BLOCK_PORT),
        )
        header.pack(fill="x", padx=12, pady=(12, 6))
        self.header_label = header

        toolbar = tk.Frame(self, bg="#ffffff")
        toolbar.pack(fill="x", padx=12, pady=(0, 4))
        self.btn_refresh = tk.Button(toolbar, text=self.tr("btn_refresh"), command=self.refresh_pings)
        self.btn_refresh.pack(side="right")

        lang_frame = tk.Frame(toolbar, bg="#ffffff")
        lang_frame.pack(side="left")
        self.lang_label_widget = tk.Label(lang_frame, text=self.tr("lang_label"), bg="#ffffff", fg=COLOR_BLACK)
        self.lang_label_widget.pack(side="left", padx=(0, 4))
        self._lang_display_to_code = {v: k for k, v in LANGUAGES.items()}
        self.lang_display_var = tk.StringVar(value=LANGUAGES.get(self.language, "English"))
        self.lang_combo = ttk.Combobox(
            lang_frame, textvariable=self.lang_display_var,
            values=list(LANGUAGES.values()), state="readonly", width=10
        )
        self.lang_combo.pack(side="left")
        self.lang_combo.bind("<<ComboboxSelected>>", self._on_language_change)

        table_header = tk.Frame(self, bg="#f0f0f0")
        table_header.pack(fill="x", padx=12)
        self._make_header_cell(table_header, None, COL_FLAG_W)
        self._make_header_cell(table_header, "col_server", COL_NAME_W, sort_key="name")
        self._make_header_cell(table_header, "col_latency", COL_LATENCY_W, sort_key="ping")
        self._make_header_cell(table_header, "col_status", COL_STATUS_W, sort_key="status")

        body_container = tk.Frame(self, bg="#ffffff")
        body_container.pack(fill="both", expand=True, padx=12, pady=(0, 6))

        self.canvas = tk.Canvas(body_container, bg="#ffffff", highlightthickness=0, width=TABLE_W)
        vsb = ttk.Scrollbar(
            body_container, orient="vertical", command=self.canvas.yview,
            style="Fat.Vertical.TScrollbar",
        )
        self.canvas.configure(yscrollcommand=vsb.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        vsb.pack(side="left", fill="y")

        self.table_body = tk.Frame(self.canvas, bg="#ffffff")
        self._body_window = self.canvas.create_window((0, 0), window=self.table_body, anchor="nw")
        self.table_body.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind(
            "<Configure>",
            lambda e: self.canvas.itemconfig(self._body_window, width=max(e.width, TABLE_W))
        )
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

        btn_frame1 = tk.Frame(self, bg=COLOR_WHITE)
        btn_frame1.pack(fill="x", padx=12, pady=(0, 4))

        block_frame = tk.Frame(btn_frame1, bg=COLOR_WHITE)
        block_frame.pack(side="left")
        self.btn_block_all = tk.Button(block_frame, text=self.tr("btn_block_all"), command=self.block_all,
                  bg=COLOR_RED, fg=COLOR_WHITE, activebackground=COLOR_RED_ACTIVE,
                  activeforeground=COLOR_WHITE)
        self.btn_block_all.pack(side="left")
        self.btn_block_selected = tk.Button(block_frame, text=self.tr("btn_block_selected"), command=self.block_selected,
                  bg=COLOR_RED, fg=COLOR_WHITE, activebackground=COLOR_RED_ACTIVE,
                  activeforeground=COLOR_WHITE)
        self.btn_block_selected.pack(side="left", padx=6)

        unblock_frame = tk.Frame(btn_frame1, bg=COLOR_WHITE)
        unblock_frame.pack(side="right")
        self.btn_unblock_all = tk.Button(unblock_frame, text=self.tr("btn_unblock_all"), command=self.unblock_all,
                  bg=COLOR_GREEN, fg=COLOR_WHITE, activebackground=COLOR_GREEN_ACTIVE,
                  activeforeground=COLOR_WHITE)
        self.btn_unblock_all.pack(side="left")
        self.btn_unblock_selected = tk.Button(unblock_frame, text=self.tr("btn_unblock_selected"), command=self.unblock_selected,
                  bg=COLOR_GREEN, fg=COLOR_WHITE, activebackground=COLOR_GREEN_ACTIVE,
                  activeforeground=COLOR_WHITE)
        self.btn_unblock_selected.pack(side="left", padx=(6, 0))

        btn_frame2 = tk.Frame(self, bg="#ffffff")
        btn_frame2.pack(fill="x", padx=12, pady=(0, 8))
        self.btn_add_server = tk.Button(btn_frame2, text=self.tr("btn_add_server"), command=self.add_server)
        self.btn_add_server.pack(side="left")
        self.btn_remove_server = tk.Button(btn_frame2, text=self.tr("btn_remove_server"), command=self.remove_server)
        self.btn_remove_server.pack(side="left", padx=6)
        # Just takes the user to the GitHub releases page - no auto-update
        # checking happens here.
        self.btn_check_update = tk.Button(btn_frame2, text=self.tr("btn_check_update"), command=self._open_releases_page)
        self.btn_check_update.pack(side="right")

        bottom_frame = tk.Frame(self, bg="#ffffff")
        bottom_frame.pack(fill="x", padx=12, pady=(0, 10))
        self.status_var = tk.StringVar(value=self.tr("status_ready"))
        tk.Label(bottom_frame, textvariable=self.status_var, bg="#ffffff", fg="#555555", anchor="w").pack(
            side="left", fill="x", expand=True
        )
        self.btn_settings = tk.Button(
            bottom_frame, text="\u2699", command=self._open_settings_dialog,
            bg="#ffffff", fg="#555555", activeforeground="#000000", activebackground="#ffffff",
            relief="flat", bd=0, font=("Segoe UI", 12), cursor="hand2",
        )
        self.btn_settings.pack(side="right", padx=(6, 0))
        tk.Label(bottom_frame, text=f"v{VERSION}", bg="#ffffff", fg="#999999", anchor="e").pack(side="right")


    def _show_update_banner(self, latest_tag: str):
        """Shows a slim yellow banner under the header when a new version is available."""
        banner = tk.Frame(self, bg="#fef08a", pady=4)
        # Insert it just below the header label, above the toolbar
        banner.pack(fill="x", padx=12, after=self.header_label)

        msg = tk.Label(
            banner,
            text=f"A new version ({latest_tag}) is available!",
            bg="#fef08a", fg="#713f12",
            font=("Segoe UI", 9),
        )
        msg.pack(side="left", padx=(6, 0))

        def open_and_dismiss():
            webbrowser.open(GITHUB_RELEASES_URL)
            banner.destroy()

        tk.Button(
            banner, text="Download", command=open_and_dismiss,
            bg="#ca8a04", fg=COLOR_WHITE, activebackground="#a16207",
            activeforeground=COLOR_WHITE, relief="flat", padx=6, pady=1,
            font=("Segoe UI", 9),
        ).pack(side="left", padx=6)

        tk.Button(
            banner, text="✕", command=banner.destroy,
            bg="#fef08a", fg="#713f12", activebackground="#fde047",
            relief="flat", bd=0, font=("Segoe UI", 9), cursor="hand2",
        ).pack(side="right", padx=4)

    def _check_for_updates(self):
        """Runs on a background thread; posts to main thread if update found."""
        if not self._settings.get("check_updates_on_startup", True):
            return
        latest = fetch_latest_version()
        if latest is None:
            return
        if _version_tuple(latest) > _version_tuple(VERSION):
            self.after(0, self._show_update_banner, latest)



    def _open_releases_page(self):
        """Opens the GitHub releases page in the user's default browser so
        they can see what's new and grab a newer build manually if they
        want to."""
        try:
            webbrowser.open(GITHUB_RELEASES_URL)
        except Exception as e:
            messagebox.showerror(APP_NAME, f"Couldn't open the releases page: {e}")

    def _open_settings_dialog(self):
        SettingsDialog(self, self)

    def _on_language_change(self, event=None):
        try:
            self.lang_combo.selection_clear()
        except Exception:
            pass
        self.focus_set()
        display = self.lang_display_var.get()
        code = self._lang_display_to_code.get(display, "en")
        if code == self.language:
            return
        self.language = code
        self._settings["language"] = code
        save_settings(self._settings)
        self._apply_language()

    def _apply_language(self):
        self.title(self.tr("app_title"))
        self.header_label.config(text=self.tr("header_text", port=BLOCK_PORT))
        self.btn_refresh.config(text=self.tr("btn_refresh"))
        self.lang_label_widget.config(text=self.tr("lang_label"))
        self.btn_block_all.config(text=self.tr("btn_block_all"))
        self.btn_block_selected.config(text=self.tr("btn_block_selected"))
        self.btn_unblock_all.config(text=self.tr("btn_unblock_all"))
        self.btn_unblock_selected.config(text=self.tr("btn_unblock_selected"))
        self.btn_add_server.config(text=self.tr("btn_add_server"))
        self.btn_remove_server.config(text=self.tr("btn_remove_server"))
        self.btn_check_update.config(text=self.tr("btn_check_update"))
        self._update_header_labels()
        self._render_rows()
        self.status_var.set(self.tr("status_ready"))

    def _make_header_cell(self, parent, key, width, sort_key=None):
        text = self.tr(key) if key else ""
        cell = tk.Frame(parent, width=width, height=28, bg="#f0f0f0",
                         cursor="hand2" if sort_key else "arrow")
        cell.pack_propagate(False)
        cell.pack(side="left")
        label = tk.Label(cell, text=text, bg="#f0f0f0", fg=COLOR_BLACK,
                          font=("Segoe UI", 10, "bold"))
        label.pack(expand=True, fill="both")
        if sort_key:
            for w in (cell, label):
                w.bind("<Button-1>", lambda e, k=sort_key: self._on_sort_click(k))
            self.header_labels[sort_key] = (label, key)
        return label

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _on_sort_click(self, key):
        if self.sort_state["column"] == key:
            self.sort_state["reverse"] = not self.sort_state["reverse"]
        else:
            self.sort_state = {"column": key, "reverse": False}
        self._settings["sort_state"] = dict(self.sort_state)
        save_settings(self._settings)
        self._render_rows()
        self._update_header_labels()

    def _update_header_labels(self):
        for col_key, (label, text_key) in self.header_labels.items():
            text = self.tr(text_key)
            if self.sort_state["column"] == col_key:
                text += " \u25bc" if self.sort_state["reverse"] else " \u25b2"
            label.configure(text=text)

    def _sorted_names(self):
        names = list(self.servers.keys())
        col = self.sort_state["column"]
        rev = self.sort_state["reverse"]
        if col == "ping":
            names.sort(
                key=lambda n: (self.latencies.get(n) is None, self.latencies.get(n) or 0),
                reverse=rev
            )
        elif col == "status":
            names.sort(key=lambda n: (not self.blocked_state.get(n, False), n.lower()), reverse=rev)
        else:
            # "Server" column: grouped by macro-region (Europe, North
            # America, Asia, Australia), alphabetical within each group.
            names.sort(key=lambda n: (_region_group(n, self.servers[n]), n.lower()), reverse=rev)
        return names

    # ------------------------------------------------------------------
    # Keyboard navigation (Up / Down arrows move the single-row selection)
    # ------------------------------------------------------------------
    def _on_arrow_up(self, event):
        self._move_selection(-1)
        return "break"

    def _on_arrow_down(self, event):
        self._move_selection(1)
        return "break"

    def _move_selection(self, delta):
        names = self._sorted_names()
        if not names:
            return
        if not self.selected:
            new_name = names[0] if delta > 0 else names[-1]
        else:
            current = next(iter(self.selected))
            for n in names:
                if n in self.selected:
                    current = n
                    break
            try:
                idx = names.index(current)
            except ValueError:
                idx = 0
            idx = max(0, min(len(names) - 1, idx + delta))
            new_name = names[idx]

        self.selected = {new_name}
        self._last_clicked_name = new_name
        self._refresh_row_visuals()
        self._scroll_row_into_view(new_name)

    def _scroll_row_into_view(self, name):
        row = self.row_frames.get(name)
        if not row:
            return
        self.update_idletasks()
        try:
            bbox = self.canvas.bbox("all")
            if not bbox:
                return
            _, _, _, total_h = bbox
            row_y = row.winfo_y()
            row_h = row.winfo_height() or ROW_H
            canvas_h = self.canvas.winfo_height()
            current_top = self.canvas.canvasy(0)
            current_bottom = current_top + canvas_h

            if row_y < current_top:
                frac = row_y / total_h if total_h else 0
                self.canvas.yview_moveto(frac)
            elif row_y + row_h > current_bottom:
                frac = (row_y + row_h - canvas_h) / total_h if total_h else 0
                self.canvas.yview_moveto(max(0, frac))
        except Exception:
            pass

    def _get_flag_image(self, name, info):
        if name not in self._flag_images:
            self._flag_images[name] = make_flag_image(info, name=name)
        return self._flag_images[name]

    def _prefetch_flags(self):
        """Download all flag images in the background so the UI never stalls."""
        for name, info in list(self.servers.items()):
            code = _country_code_for_server(name, info)
            if code:
                _fetch_flag_png(code, width=80)
        self._flag_images.clear()
        self.after(0, self._render_rows)

    def _render_rows(self):
        for w in self.table_body.winfo_children():
            w.destroy()
        self.row_frames.clear()
        self.status_cells.clear()

        for name in self._sorted_names():
            self._build_row(name, self.servers[name])
        self._refresh_row_visuals()

    def _build_row(self, name, info):
        row = tk.Frame(self.table_body, bg="#ffffff", highlightthickness=2, highlightbackground="#ffffff")
        row.pack(fill="x")
        self.row_frames[name] = row

        flag_cell = tk.Frame(row, width=COL_FLAG_W, height=ROW_H, bg="#ffffff")
        flag_cell.pack_propagate(False)
        flag_cell.pack(side="left")
        flag_img = self._get_flag_image(name, info)
        flag_label = tk.Label(flag_cell, image=flag_img, bg="#ffffff")
        flag_label.pack(expand=True)

        name_cell = tk.Frame(row, width=COL_NAME_W, height=ROW_H, bg="#ffffff")
        name_cell.pack_propagate(False)
        name_cell.pack(side="left")
        name_label = tk.Label(name_cell, text=name, bg="#ffffff", fg="#000000",
                               anchor="w", font=("Segoe UI", 10, "normal"))
        name_label.pack(expand=True, fill="both", padx=(6, 0))

        lat_cell = tk.Frame(row, width=COL_LATENCY_W, height=ROW_H, bg="#ffffff")
        lat_cell.pack_propagate(False)
        lat_cell.pack(side="left")
        lat_inner = tk.Frame(lat_cell, bg="#ffffff")
        lat_inner.pack(expand=True)
        num_label = tk.Label(lat_inner, text=self.tr("lat_na"), bg="#ffffff", fg="#000000",
                              font=("Segoe UI", 10, "bold"))
        num_label.pack(side="left")
        unit_label = tk.Label(lat_inner, text="", bg="#ffffff", fg="#000000", font=("Segoe UI", 10))
        unit_label.pack(side="left")

        status_cell = tk.Frame(row, width=COL_STATUS_W, height=ROW_H, bg="#ffffff")
        status_cell.pack_propagate(False)
        status_cell.pack(side="left")
        status_label = tk.Label(status_cell, text=self.tr("row_allowed"), fg="#000000", font=("Segoe UI", 10, "bold"))
        status_label.pack(expand=True, fill="both")

        self.status_cells[name] = {
            "lat_num": num_label, "lat_unit": unit_label,
            "status": status_label, "status_cell": status_cell,
        }

        # Bind click handling (with Shift+click range-select support) to the row and every descendant widget inside it, so clicking anywhere on the row triggers selection correctly.
        self._bind_row_click_recursive(row, name)

    def _bind_row_click_recursive(self, widget, name):
        widget.bind("<Button-1>", lambda e, n=name: self._on_row_click(n, ctrl=False, shift=bool(e.state & 0x0001)))
        widget.bind("<Control-Button-1>", lambda e, n=name: self._on_row_click(n, ctrl=True, shift=False))
        widget.bind("<Shift-Button-1>", lambda e, n=name: self._on_row_click(n, ctrl=False, shift=True))
        widget.bind("<Button-3>", lambda e, n=name: self._show_row_context_menu(e, n))
        for child in widget.winfo_children():
            self._bind_row_click_recursive(child, name)

    def _show_row_context_menu(self, event, name):
        menu = tk.Menu(self, tearoff=0)
        menu.add_command(label=self.tr("menu_properties"), command=lambda n=name: self._edit_server(n))
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()

    def _on_row_click(self, name, ctrl, shift=False):
        names = self._sorted_names()
        if shift and self._last_clicked_name in names and name in names:
            i1 = names.index(self._last_clicked_name)
            i2 = names.index(name)
            lo, hi = min(i1, i2), max(i1, i2)
            self.selected = set(names[lo:hi + 1])
        elif ctrl:
            if name in self.selected:
                self.selected.discard(name)
            else:
                self.selected.add(name)
            self._last_clicked_name = name
        else:
            self.selected = {name}
            self._last_clicked_name = name
        self._refresh_row_visuals()

    def _refresh_row_visuals(self):
        for name, row in self.row_frames.items():
            selected = name in self.selected
            row.configure(highlightbackground="#000000" if selected else "#ffffff")

            blocked = self.blocked_state.get(name, False)
            ms = self.latencies.get(name)

            cells = self.status_cells[name]
            if ms is None:
                cells["lat_num"].configure(text=self.tr("lat_na"), fg="#000000")
                cells["lat_unit"].configure(text="")
            else:
                cells["lat_num"].configure(text=str(ms), fg=ping_color(ms))
                cells["lat_unit"].configure(text=self.tr("lat_unit"), fg="#000000")

            status_color = COLOR_RED if blocked else COLOR_GREEN
            status_text = self.tr("row_blocked") if blocked else self.tr("row_allowed")
            cells["status_cell"].configure(bg=status_color)
            cells["status"].configure(text=status_text, bg=status_color, fg=COLOR_WHITE)

    def refresh_pings(self):
        self.status_var.set(self.tr("status_pinging"))
        threading.Thread(target=self._ping_worker, daemon=True).start()

    def _ping_worker(self):
        with concurrent.futures.ThreadPoolExecutor(max_workers=12) as executor:
            future_to_name = {
                executor.submit(ping_host, info["ip"]): name
                for name, info in self.servers.items()
            }
            for future in concurrent.futures.as_completed(future_to_name):
                name = future_to_name[future]
                try:
                    ms = future.result()
                except Exception:
                    ms = None
                self.latencies[name] = ms
                self.after(0, self._refresh_row_visuals)
        self.after(0, self._finish_ping_sweep)

    def _finish_ping_sweep(self):
        valid = {n: ms for n, ms in self.latencies.items() if ms is not None}
        self.best_ping_name = min(valid, key=valid.get) if valid else None
        self._render_rows()
        self._update_header_labels()
        self.status_var.set(self.tr("status_ping_complete"))

    # ------------------------------------------------------------------
    # Persisted block state: remember which servers were blocked so they can be restored automatically the next time the app is opened.
    # ------------------------------------------------------------------
    def _save_blocked_state(self):
        blocked_names = [n for n, v in self.blocked_state.items() if v]
        self._settings["blocked_servers"] = blocked_names
        save_settings(self._settings)

    def _restore_blocked_state(self):
        saved_blocked = self._settings.get("blocked_servers", [])
        if not isinstance(saved_blocked, list):
            return
        names_to_restore = [n for n in saved_blocked if n in self.servers]
        if not names_to_restore:
            return
        threading.Thread(target=self._restore_blocked_worker, args=(names_to_restore,), daemon=True).start()

    def _restore_blocked_worker(self, names):
        valid_names = [n for n in names if n in self.servers and is_valid_ipv4(self.servers[n]["ip"])]
        if not valid_names:
            return
        ips = [self.servers[n]["ip"] for n in valid_names]
        ok, _msg = sync_block_rule(ips)
        if ok:
            for n in valid_names:
                self.blocked_state[n] = True
            self.after(0, self._refresh_row_visuals)

    def _apply_block(self, names, block: bool):
        threading.Thread(target=self._apply_block_worker, args=(names, block), daemon=True).start()

    def _apply_block_worker(self, names, block: bool):
        failures = []
        changed = 0
        already = 0
        pending_state = dict(self.blocked_state)

        for name in names:
            if pending_state.get(name, False) == block:
                already += 1
                continue
            if block and not is_valid_ipv4(self.servers[name]["ip"]):
                failures.append(self.tr("msg_invalid_ip", name=name))
                continue
            pending_state[name] = block
            changed += 1

        if changed:
            blocked_ips = [
                self.servers[n]["ip"] for n, is_blk in pending_state.items()
                if is_blk and n in self.servers
            ]
            ok, msg = sync_block_rule(blocked_ips)
            if ok:
                self.blocked_state = pending_state
            else:
                failures.append(msg)
                changed = 0

        self.after(0, self._finish_apply_block, failures, changed, already, block)

    def _finish_apply_block(self, failures, changed, already, block):
        self._refresh_row_visuals()
        self._save_blocked_state()

        if failures:
            self.status_var.set(self.tr("status_errors", count=len(failures)))
            messagebox.showerror(APP_NAME, "\n".join(failures))
            return

        action = self.tr("status_blocked_action") if block else self.tr("status_unblocked_action")
        if changed:
            self.status_var.set(self.tr("status_action_done", action=action, count=changed))
        elif already:
            key = "status_already_blocked" if block else "status_already_unblocked"
            self.status_var.set(self.tr(key, count=already))
        else:
            self.status_var.set(self.tr("status_ready"))

    def block_all(self):
        self._apply_block(list(self.servers.keys()), True)

    def unblock_all(self):
        self._apply_block(list(self.servers.keys()), False)

    def block_selected(self):
        if not self.selected:
            messagebox.showinfo(APP_NAME, self.tr("msg_select_first"))
            return
        self._apply_block(list(self.selected), True)

    def unblock_selected(self):
        if not self.selected:
            messagebox.showinfo(APP_NAME, self.tr("msg_select_first"))
            return
        self._apply_block(list(self.selected), False)

    # ------------------------------------------------------------------
    # Add / remove / edit servers
    # ------------------------------------------------------------------
    def add_server(self):
        name = simpledialog.askstring(APP_NAME, self.tr("prompt_server_name"), parent=self)
        if not name:
            return
        name = name.strip()
        if not name:
            messagebox.showwarning(APP_NAME, self.tr("msg_name_required"))
            return
        if name in self.servers:
            messagebox.showwarning(APP_NAME, self.tr("msg_dup_name"))
            return
        ip = simpledialog.askstring(APP_NAME, self.tr("prompt_ip"), parent=self)
        if not ip or not ip.strip():
            messagebox.showwarning(APP_NAME, self.tr("msg_ip_required"))
            return
        ip = ip.strip()

        preset_names = list(FLAG_PRESETS.keys())
        flag_dialog = FlagPickerDialog(self, APP_NAME, self.tr("prompt_flag"), preset_names)
        flag_choice = flag_dialog.result
        preset = FLAG_PRESETS.get(flag_choice, FLAG_PRESETS["Other / Unknown"])

        info = {"ip": ip, "region": "Custom"}
        info.update(preset)
        self.servers[name] = info
        self.latencies[name] = None
        self.blocked_state[name] = False
        save_servers(self.servers)
        self._render_rows()
        self.status_var.set(self.tr("status_added", name=name))
        self.after(50, self.refresh_pings)

    def remove_server(self):
        if not self.selected:
            messagebox.showinfo(APP_NAME, self.tr("msg_select_first"))
            return
        names = list(self.selected)

        if not messagebox.askyesno(APP_NAME, self.tr("msg_confirm_remove", count=len(names))):
            return

        batch = [
            (name, dict(self.servers[name]), self.latencies.get(name), self.blocked_state.get(name, False))
            for name in names
        ]
        self._undo_stack.append(batch)
        self._redo_stack.clear()

        any_were_blocked = any(self.blocked_state.get(name, False) for name in names)
        for name in names:
            self.servers.pop(name, None)
            self.latencies.pop(name, None)
            self.blocked_state.pop(name, None)
        self.selected.clear()
        save_servers(self.servers)

        if any_were_blocked:
            blocked_ips = [
                info["ip"] for n, info in self.servers.items()
                if self.blocked_state.get(n, False)
            ]
            sync_block_rule(blocked_ips)

        self._save_blocked_state()
        self._render_rows()
        self.status_var.set(self.tr("status_removed", count=len(names)))

    # ------------------------------------------------------------------
    # Undo / redo
    # ------------------------------------------------------------------
    def _undo_last_action(self, event=None):
        if not self._undo_stack:
            return "break"
        batch = self._undo_stack.pop()
        for name, info, latency, blocked in batch:
            self.servers[name] = info
            self.latencies[name] = latency
            self.blocked_state[name] = blocked
        save_servers(self.servers)

        if any(blocked for _, _, _, blocked in batch):
            blocked_ips = [
                info["ip"] for n, info in self.servers.items()
                if self.blocked_state.get(n, False)
            ]
            sync_block_rule(blocked_ips)
            self._save_blocked_state()

        self._redo_stack.append(batch)
        self._render_rows()
        self.status_var.set(self.tr("status_undo_done", count=len(batch)))
        return "break"

    def _redo_last_action(self, event=None):
        if not self._redo_stack:
            return "break"
        batch = self._redo_stack.pop()
        names = [name for name, _, _, _ in batch]
        any_were_blocked = any(self.blocked_state.get(name, False) for name in names)
        for name in names:
            self.servers.pop(name, None)
            self.latencies.pop(name, None)
            self.blocked_state.pop(name, None)
        self.selected.difference_update(names)
        save_servers(self.servers)

        if any_were_blocked:
            blocked_ips = [
                info["ip"] for n, info in self.servers.items()
                if self.blocked_state.get(n, False)
            ]
            sync_block_rule(blocked_ips)
            self._save_blocked_state()

        self._undo_stack.append(batch)
        self._render_rows()
        self.status_var.set(self.tr("status_redo_done", count=len(batch)))
        return "break"

    def _edit_server(self, name):
        info = self.servers.get(name)
        if not info:
            return

        dialog = tk.Toplevel(self)
        dialog.title(self.tr("menu_properties"))
        dialog.configure(bg=COLOR_WHITE)
        dialog.transient(self)
        dialog.resizable(False, False)
        dialog.withdraw()

        name_row = tk.Frame(dialog, bg=COLOR_WHITE)
        name_row.pack(fill="x", padx=12, pady=(12, 6))
        tk.Label(name_row, text=self.tr("prompt_name"), bg=COLOR_WHITE, fg=COLOR_BLACK).pack(side="left")
        name_var = tk.StringVar(value=name)
        name_entry = tk.Entry(name_row, textvariable=name_var, width=24)
        name_entry.pack(side="left", padx=(6, 0), fill="x", expand=True)

        ip_row = tk.Frame(dialog, bg=COLOR_WHITE)
        ip_row.pack(fill="x", padx=12, pady=(0, 12))
        tk.Label(ip_row, text=self.tr("prompt_ip"), bg=COLOR_WHITE, fg=COLOR_BLACK).pack(side="left")
        ip_var = tk.StringVar(value=info.get("ip", ""))
        ip_entry = tk.Entry(ip_row, textvariable=ip_var, width=20)
        ip_entry.pack(side="left", padx=(6, 0), fill="x", expand=True)

        btn_frame = tk.Frame(dialog, bg=COLOR_WHITE)
        btn_frame.pack(fill="x", padx=12, pady=(0, 12))

        def on_save():
            new_ip = ip_var.get().strip()
            new_name = name_var.get().strip()
            if not new_ip:
                messagebox.showerror(APP_NAME, self.tr("msg_ip_required"))
                return
            if not new_name:
                messagebox.showerror(APP_NAME, self.tr("msg_name_required"))
                return
            if new_name != name and new_name in self.servers:
                messagebox.showerror(APP_NAME, self.tr("msg_dup_name"))
                return

            renamed = new_name != name
            was_blocked = self.blocked_state.get(name, False)

            if renamed:
                self.servers[new_name] = self.servers.pop(name)
                self.latencies[new_name] = self.latencies.pop(name, None)
                self.blocked_state[new_name] = self.blocked_state.pop(name, False)
                self._flag_images.pop(name, None)
                if name in self.selected:
                    self.selected.discard(name)
                    self.selected.add(new_name)

            target_name = new_name if renamed else name
            self.servers[target_name]["ip"] = new_ip

            save_servers(self.servers)

            if was_blocked:
                blocked_ips = [
                    info["ip"] for n, info in self.servers.items()
                    if self.blocked_state.get(n, False)
                ]
                ok, msg = sync_block_rule(blocked_ips)
                if not ok:
                    messagebox.showerror(APP_NAME, msg)

            self._save_blocked_state()
            self._render_rows()
            dialog.destroy()
            self.after(50, self.refresh_pings)

        tk.Button(btn_frame, text=self.tr("btn_save"), command=on_save).pack(side="left")
        tk.Button(btn_frame, text=self.tr("btn_cancel"), command=dialog.destroy).pack(side="left", padx=(6, 0))

        dialog.update_idletasks()
        w = dialog.winfo_width()
        h = dialog.winfo_height()
        px = self.winfo_rootx()
        py = self.winfo_rooty()
        pw = self.winfo_width()
        ph = self.winfo_height()
        x = px + (pw - w) // 2
        y = py + (ph - h) // 2
        dialog.geometry(f"{w}x{h}+{x}+{y}")
        dialog.deiconify()

    # ------------------------------------------------------------------
    # Tray icon
    # ------------------------------------------------------------------
    def _start_tray_icon(self):
        if not TRAY_AVAILABLE or self._tray_pil_image is None:
            return
        if self.tray_icon is not None:
            return
        self.tray_icon = self._create_tray_icon()
        threading.Thread(target=self.tray_icon.run, daemon=True).start()

    def _create_tray_icon(self):
        menu = pystray.Menu(
            pystray.MenuItem(self.tr("tray_open"), self._on_tray_open, default=True),
            pystray.MenuItem(self.tr("tray_quit"), self._on_tray_quit),
        )
        return pystray.Icon(APP_NAME, self._tray_pil_image, self.tr("app_title"), menu)

    def _on_tray_open(self, icon, item):
        # Runs on pystray's own thread - hop back onto the Tk main thread.
        self.after(0, self._bring_to_front)

    def _bring_to_front(self):
        self.deiconify()
        self.lift()
        self.focus_force()

    def _on_tray_quit(self, icon, item):
        # Runs on pystray's own thread - hop back onto the Tk main thread.
        self.after(0, self._on_close)

    # ------------------------------------------------------------------
    # Shutdown: unblock everything so the user isn't left with stale firewall rules once the app closes.
    # ------------------------------------------------------------------
    def _on_close(self):
        self.status_var.set(self.tr("status_closing"))
        self.update_idletasks()
        if self.tray_icon is not None:
            try:
                self.tray_icon.stop()
            except Exception:
                pass
        try:
            cleanup_all_rules()
        finally:
            self.destroy()


def fetch_latest_version() -> str | None:
    """Returns the latest release tag from GitHub (e.g. 'v1.1'), or None on failure."""
    try:
        req = urllib.request.Request(
            GITHUB_API_LATEST,
            headers={"User-Agent": "HnG-ServerPicker/" + VERSION}
        )
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        return data.get("tag_name", "").strip()
    except Exception:
        return None


def _version_tuple(tag: str) -> tuple:
    """Converts 'v1.2.3' or '1.2.3' to (1, 2, 3) for comparison."""
    tag = tag.lstrip("v")
    try:
        return tuple(int(x) for x in tag.split("."))
    except Exception:
        return (0,)



def main():
    if os.name == "nt" and not is_admin():
        relaunch_as_admin()
        return
    app = ServerSelectorApp()
    app.mainloop()


if __name__ == "__main__":
    main()
