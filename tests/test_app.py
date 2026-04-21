"""
Tests automatizados para Esteticai
====================================
Ejecutar: pytest tests/ -v
"""

import os
import sys
import json
import pytest
import sqlite3
import tempfile
from pathlib import Path

# Configurar entorno antes de importar la app
os.environ["TESTING"] = "1"

# Añadir raíz del proyecto al path
sys.path.insert(0, str(Path(__file__).parent.parent))


# ============================================================
# TESTS UNITARIOS DE FUNCIONES AUXILIARES
# ============================================================

class TestValidacion:
    """Tests de funciones de validación."""

    def test_validar_email_valido(self):
        from web.app import validar_email
        assert validar_email("test@example.com") is True
        assert validar_email("user.name+tag@domain.co.uk") is True

    def test_validar_email_invalido(self):
        from web.app import validar_email
        assert validar_email("") is False
        assert validar_email("noarroba.com") is False
        assert validar_email("@dominio.com") is False
        assert validar_email("user@") is False

    def test_sanitizar_texto(self):
        from web.app import sanitizar_texto
        assert sanitizar_texto("  hola  ") == "hola"
        assert sanitizar_texto("a" * 600, 500) == "a" * 500
        assert sanitizar_texto("") == ""
        assert sanitizar_texto(None) == ""

    def test_validar_registro_ok(self):
        from web.app import validar_registro
        assert validar_registro("Laura", "laura@test.com", "password123") is None

    def test_validar_registro_nombre_corto(self):
        from web.app import validar_registro
        result = validar_registro("L", "laura@test.com", "password123")
        assert result is not None
        assert "nombre" in result.lower()

    def test_validar_registro_email_invalido(self):
        from web.app import validar_registro
        result = validar_registro("Laura", "no-es-email", "password123")
        assert result is not None
        assert "email" in result.lower()

    def test_validar_registro_password_corta(self):
        from web.app import validar_registro
        result = validar_registro("Laura", "laura@test.com", "12345")
        assert result is not None
        assert "contrase" in result.lower()

    def test_validar_registro_nombre_largo(self):
        from web.app import validar_registro
        result = validar_registro("A" * 101, "laura@test.com", "password123")
        assert result is not None


class TestPassword:
    """Tests de hashing y verificación de contraseñas."""

    def test_hash_y_verificar_bcrypt(self):
        from web.app import hash_password, verificar_password
        hashed = hash_password("mi_password_segura")
        assert hashed.startswith("$2b$")
        assert verificar_password("mi_password_segura", hashed) is True
        assert verificar_password("password_incorrecta", hashed) is False

    def test_verificar_sha256_legacy(self):
        from web.app import verificar_password
        import hashlib
        legacy_hash = hashlib.sha256("oldpassword".encode()).hexdigest()
        assert verificar_password("oldpassword", legacy_hash) is True
        assert verificar_password("wrong", legacy_hash) is False


class TestPlanes:
    """Tests del sistema de planes."""

    def test_planes_definidos(self):
        from web.app import PLANES
        assert "free" in PLANES
        assert "trial" in PLANES
        assert "starter" in PLANES
        assert "pro" in PLANES
        assert "business" in PLANES

    def test_planes_tienen_limites(self):
        from web.app import PLANES
        for plan_id, plan in PLANES.items():
            assert "nombre" in plan
            assert "precio" in plan
            assert "limites" in plan
            assert "copys" in plan["limites"]
            assert "imagenes" in plan["limites"]

    def test_plan_free_limitado(self):
        from web.app import PLANES
        free = PLANES["free"]
        assert free["precio"] == 0
        assert free["limites"]["copys"] > 0  # Tiene algunos
        assert free["limites"]["videos"] == 0  # No incluido

    def test_plan_business_ilimitado(self):
        from web.app import PLANES
        biz = PLANES["business"]
        assert biz["limites"]["copys"] == -1  # Ilimitado
        assert biz["limites"]["imagenes"] == -1

    def test_tipo_a_campo_uso(self):
        from web.app import TIPO_A_CAMPO_USO
        assert TIPO_A_CAMPO_USO["copy"] == "copys"
        assert TIPO_A_CAMPO_USO["imagen"] == "imagenes"
        assert TIPO_A_CAMPO_USO["video"] == "videos"


class TestCSRF:
    """Tests de protección CSRF."""

    def test_csrf_rutas_definidas(self):
        from web.app import CSRF_FORM_ROUTES, CSRF_PREFIX_ROUTES
        assert "/login" in CSRF_FORM_ROUTES
        assert "/registro" in CSRF_FORM_ROUTES
        assert "/perfil/crear" in CSRF_FORM_ROUTES
        assert "/cuenta/eliminar" in CSRF_FORM_ROUTES
        assert "/reset/" in CSRF_PREFIX_ROUTES


class TestAdmin:
    """Tests del panel de administración."""

    def test_admin_emails_configurados(self):
        from web.app import ADMIN_EMAILS
        assert len(ADMIN_EMAILS) > 0

    def test_es_admin(self):
        from web.app import es_admin, ADMIN_EMAILS
        admin_email = list(ADMIN_EMAILS)[0]
        # Simular user dict
        assert es_admin({"email": admin_email}) is True
        assert es_admin({"email": "nonadmin@test.com"}) is False
        assert es_admin(None) is False


class TestEmailService:
    """Tests del servicio de email."""

    def test_plantilla_base_html(self):
        from web.email_service import _plantilla_base
        html = _plantilla_base("<p>Hola</p>")
        assert "<!DOCTYPE html>" in html
        assert "Esteticai" in html
        assert "<p>Hola</p>" in html

    def test_enviar_sin_api_key(self):
        from web.email_service import enviar_email
        # Sin RESEND_API_KEY, debe retornar False (modo dev)
        original = os.environ.get("RESEND_API_KEY", "")
        os.environ["RESEND_API_KEY"] = ""
        result = enviar_email("test@test.com", "Test", "<p>Test</p>")
        assert result is False
        if original:
            os.environ["RESEND_API_KEY"] = original


class TestWhitelists:
    """Tests de whitelists de validación."""

    def test_tipos_negocio_validos(self):
        from web.app import TIPOS_NEGOCIO_VALIDOS
        assert "Centro de estetica" in TIPOS_NEGOCIO_VALIDOS
        assert len(TIPOS_NEGOCIO_VALIDOS) >= 5

    def test_tonos_validos(self):
        from web.app import TONOS_VALIDOS
        assert "cercano" in TONOS_VALIDOS
        assert "profesional" in TONOS_VALIDOS

    def test_redes_validas(self):
        from web.app import REDES_VALIDAS
        assert "Instagram" in REDES_VALIDAS
        assert "TikTok" in REDES_VALIDAS


class TestRateLimits:
    """Tests de rate limiting."""

    def test_rate_limits_definidos(self):
        from web.app import RATE_LIMITS
        assert "/api/generar/copy" in RATE_LIMITS
        assert "/api/generar/imagen" in RATE_LIMITS
        assert "/api/generar/video" in RATE_LIMITS

    def test_check_rate_limit_ok(self):
        from web.app import check_rate_limit, _rate_limits
        _rate_limits.clear()
        assert check_rate_limit(999, "/api/generar/copy") is True

    def test_check_rate_limit_unknown_endpoint(self):
        from web.app import check_rate_limit
        assert check_rate_limit(999, "/ruta/desconocida") is True
