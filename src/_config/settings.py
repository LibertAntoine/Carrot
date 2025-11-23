"""
Django settings for Carrot project.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.1/ref/settings/
"""

import logging
import os
import sys
from datetime import timedelta
from pathlib import Path

import dotenv

from .services.jwt_rs256_keys import get_jwt_rs256_keys

dotenv.load_dotenv()

#################
# CORE SETTINGS #
#################

DEFAULT_JUMPER_MAX_VERSION = "0.5"

APP_VERSION = os.getenv("APP_VERSION", "dev")
APP_COMMIT = os.getenv("APP_COMMIT", "unknown")
APP_BUILD_DATE = os.getenv("APP_BUILD_DATE", "unknown")

# SECURITY WARNING: keep the secret keys used in production secret!
SECRET_KEY = os.getenv(
    "SECRET_KEY",
    "django-insecure-w)t6yx_+6a8tw!61gh-7c0w7&y32o=(r)cxi=jpl*z5*95b%6v",
)

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv("DEBUG", "false").lower() in ("true", "1")

BASE_DIR = Path(__file__).resolve().parent.parent
ROOT_URLCONF = "_config.urls"
WSGI_APPLICATION = "_config.wsgi.application"

INSTALLED_APPS = [
    "auths",
    "users",
    "actions",
    "system",
    "workspaces",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "simple_history",
    "django_filters",
    "rest_framework",
    "corsheaders",
    "drf_yasg",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
    "django_user_agents",
    "mozilla_django_oidc",
    "django_scim",
    "django_group_model",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django_user_agents.middleware.UserAgentMiddleware",
    "simple_history.middleware.HistoryRequestMiddleware",
    "django.middleware.http.ConditionalGetMiddleware",
]

REST_FRAMEWORK = {
    # DEFAULT_AUTHENTICATION_CLASSES define in Authentication section
}

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

### SUPERADMIN DEFAULT CREDENTIALS ###

ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@mail.com")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin")

#############
# DATABASES #
#############

# https://docs.djangoproject.com/en/4.2/ref/settings/#databases
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("POSTGRES_DB", "carrot-db"),
        "USER": os.getenv("POSTGRES_USER", "carrot"),
        "PASSWORD": os.getenv("POSTGRES_PASSWORD", "unsecurepassword"),
        "HOST": os.getenv("POSTGRES_HOST", "carrot-postgres"),
        "PORT": os.getenv("POSTGRES_PORT", "5432"),
    }
}

############
# STORAGES #
############

STORAGE_BACKEND_STRATEGIES = {
    "local": "django.core.files.storage.FileSystemStorage",
    "s3": "storages.backends.s3boto3.S3Boto3Storage",
    "swift": "storages.backends.swift.SwiftStorage",
}

STORAGE_BACKEND = os.getenv(
    "OBJECT", list(STORAGE_BACKEND_STRATEGIES.keys())[0]
)

if STORAGE_BACKEND not in list(STORAGE_BACKEND_STRATEGIES.keys()):
    raise ValueError(
        f"Invalid STORAGE_BACKEND '{STORAGE_BACKEND}'. "
        f"Supported backends: {list(STORAGE_BACKEND_STRATEGIES.keys())}"
    )

DEFAULT_FILE_STORAGE = STORAGE_BACKEND_STRATEGIES[STORAGE_BACKEND]

### LOCAL - FILE STORAGE ###

MEDIA_ROOT = os.getenv("LOCAL_MEDIA_ROOT", "/app/files")

### S3 - OBJECT STORAGE ###

AWS_ACCESS_KEY_ID = os.getenv("S3_ACCESS_KEY_ID", None)
AWS_SECRET_ACCESS_KEY = os.getenv("S3_SECRET_ACCESS_KEY", None)
AWS_STORAGE_BUCKET_NAME = os.getenv("S3_BUCKET_NAME", None)
AWS_S3_ENDPOINT_URL = os.getenv("S3_ENDPOINT_URL", None)
AWS_S3_CUSTOM_DOMAIN = os.getenv("S3_SERVER_URL", AWS_S3_ENDPOINT_URL)
AWS_S3_SECURE_URLS = False
AWS_S3_USE_SSL = False
AWS_REGION = os.getenv("S3_REGION", "us-east-1")
PRESIGNED_URL_EXPIRES_IN = int(os.getenv("PRESIGNED_URL_EXPIRES_IN", "7200"))

### SWIFT - OBJECT STORAGE ###

SWIFT_AUTH_URL = os.getenv("SWIFT_AUTH_URL", None)
SWIFT_USERNAME = os.getenv("SWIFT_USERNAME", None)
SWIFT_PASSWORD = os.getenv("SWIFT_PASSWORD", None)
SWIFT_PROJECT_NAME = os.getenv("SWIFT_PROJECT_NAME", None)
SWIFT_PROJECT_DOMAIN_NAME = os.getenv("SWIFT_PROJECT_DOMAIN_NAME", None)
SWIFT_USER_DOMAIN_NAME = os.getenv("SWIFT_USER_DOMAIN_NAME", None)
SWIFT_REGION_NAME = os.getenv("SWIFT_REGION_NAME", None)
SWIFT_CONTAINER_NAME = os.getenv("SWIFT_CONTAINER_NAME", None)
SWIFT_AUTO_CREATE_CONTAINER = True
SWIFT_USE_TEMP_URLS = True
# to generate one: openstack container set albatross --property Temp-URL-Key=your_key_here
SWIFT_TEMP_URL_KEY = os.getenv("SWIFT_TEMP_URL_KEY", None)
SWIFT_TEMP_URL_DURATION = int(
    os.getenv("SWIFT_TEMP_URL_DURATION", "3600")
)  # 1h
SWIFT_AUTH_VERSION = os.getenv("SWIFT_AUTH_VERSION", "3")

##################
# AUTHENTICATION #
##################

AUTH_USER_MODEL = "users.User"
AUTH_GROUP_MODEL = "users.Group"

REST_FRAMEWORK["DEFAULT_AUTHENTICATION_CLASSES"] = [
    "auths.jwt.jwt_utils.JwtCookiesAuthentication",
]

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
]

### JWT AUTHENTICATION ###

PASSWORD_BASED_AUTHENTICATION = os.getenv(
    "PASSWORD_BASED_AUTHENTICATION", "true"
).lower() in ("true", "1", "t")
ACCESS_TOKEN_LIFETIME = int(os.getenv("ACCESS_TOKEN_LIFETIME", "15"))
REFRESH_TOKEN_LIFETIME = int(os.getenv("REFRESH_TOKEN_LIFETIME", "43200"))

JWT_SIGNING_KEY, JWT_VERIFYING_KEY = get_jwt_rs256_keys()

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=ACCESS_TOKEN_LIFETIME),
    "REFRESH_TOKEN_LIFETIME": timedelta(minutes=REFRESH_TOKEN_LIFETIME),
    "ROTATE_REFRESH_TOKENS": False,
    "BLACKLIST_AFTER_ROTATION": True,
    "ALGORITHM": "RS256",
    "SIGNING_KEY": JWT_SIGNING_KEY,
    "VERIFYING_KEY": JWT_VERIFYING_KEY,
}

# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

### OIDC ###

# https://mozilla-django-oidc.readthedocs.io/en/stable/installation.html
OIDC_ENABLED = os.getenv("OIDC_ENABLED", "false").lower() in ("true", "1")
OIDC_RP_CLIENT_ID = os.getenv("OIDC_RP_CLIENT_ID")
OIDC_RP_CLIENT_SECRET = os.getenv("OIDC_RP_CLIENT_SECRET")
OIDC_OP_AUTHORIZATION_ENDPOINT = os.getenv("OIDC_OP_AUTHORIZATION_ENDPOINT")
OIDC_OP_TOKEN_ENDPOINT = os.getenv("OIDC_OP_TOKEN_ENDPOINT")
OIDC_OP_USER_ENDPOINT = os.getenv("OIDC_OP_USER_ENDPOINT")
OIDC_OP_JWKS_ENDPOINT = os.getenv("OIDC_OP_JWKS_ENDPOINT")
OIDC_OP_LOGOUT_ENDPOINT = os.getenv("OIDC_OP_LOGOUT_ENDPOINT")
OIDC_OP_LOGOUT_URL_METHOD = "users.auth.logout"
ALLOW_LOGOUT_GET_METHOD = True
OIDC_RP_SIGN_ALGO = os.getenv("OIDC_RP_SIGN_ALGO", "HS256")
OIDC_PROVIDER_NAME = os.getenv("OIDC_PROVIDER_NAME", "OIDC")
OIDC_RP_SCOPES = os.getenv("OIDC_RP_SCOPES", "openid email profile")
OIDC_USERNAME_ATTRIBUTE = os.getenv(
    "OIDC_USERNAME_ATTRIBUTE", "preferred_username"
)

if OIDC_ENABLED:
    AUTHENTICATION_BACKENDS.insert(
        0,
        "auths.oidc.custom_oidc_authentication_backend.CustomOIDCAuthenticationBackend",
    )
    REST_FRAMEWORK["DEFAULT_AUTHENTICATION_CLASSES"].append(
        "mozilla_django_oidc.contrib.drf.OIDCAuthentication"
    )

### SCIM ###

# https://django-scim2.readthedocs.io/en/latest/
SCIM_ENABLED = os.getenv("SCIM_ENABLED", "false").lower() in ("true", "1")
SCIM_ALLOW_USER_DELETION = (
    False if os.getenv("SCIM_ALLOW_USER_DELETION") == "False" else True
)
SCIM_ALLOW_USER_CREATION_CONFLIT = os.getenv(
    "SCIM_ALLOW_USER_CREATION_CONFLIT", "false"
).lower() in ("true", "1")

SCIM_BEARER_TOKEN = os.getenv("SCIM_BEARER_TOKEN", None)

SCIM_SERVICE_PROVIDER = {
    "USER_ADAPTER": "users.scim.SCIMUser",
    "GROUP_ADAPTER": "users.scim.SCIMGroup",
    "GROUP_MODEL": "users.models.Group",
    "BASE_LOCATION_GETTER": "jumper.utils.get_full_domain_from_request",
    "GET_IS_AUTHENTICATED_PREDICATE": lambda _: True,
    "AUTH_CHECK_MIDDLEWARE": "users.scim.SCIMAuthCheckMiddleware",
    "AUTHENTICATION_SCHEMES": [
        {
            "name": "Bearer Token",
            "description": "Static Bearer Token for SCIM API authentication",
            "specUri": "http://www.rfc-editor.org/info/rfc6750",
            "type": "oauthbearertoken",
            "primary": True,
        }
    ],
    "WWW_AUTHENTICATE_HEADER": 'Bearer realm="Carrot SCIM2.0"',
}

ADMIN_GROUP = os.getenv("ADMIN_GROUP", None)

#########
# LOGGING
#########

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{asctime} {levelname} {module} {message} {exc_info}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "stream": sys.stdout,
            "formatter": "verbose",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        }
    },
}

if os.environ.get("DJANGO_LOG_FILE"):
    LOGGING["loggers"]["django"]["handlers"].append("django_file")
    LOGGING["handlers"]["django_file"] = {
        "level": os.getenv("DJANGO_LOG_FILE_LEVEL", "INFO"),
        "class": "logging.FileHandler",
        "filename": os.getenv("DJANGO_LOG_FILE"),
        "formatter": "verbose",
    }

    def handle_uncaught_exception(exc_type, exc_value, exc_traceback):
        logger = logging.getLogger("django")
        logger.error(
            "Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback)
        )

    sys.excepthook = handle_uncaught_exception

#################
# EMAILS - SMTP #
#################

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = os.getenv("EMAIL_HOST", None)
EMAIL_PORT = int(os.getenv("EMAIL_PORT", "25"))
EMAIL_USE_TLS = os.getenv("EMAIL_USE_TLS") == "True"
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER", None)
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD", None)
DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL", "jumper@company.com")

##########
# OTHERS #
##########

### CORS POLICY ###

ALLOWED_HOSTS = ["*"]
CORS_ALLOW_NULL_ORIGIN = True
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_HEADERS = ["*"]
CORS_ALLOW_METHODS = ["*"]

### DEFAULT AUTO FIELD ###
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

### INTERNATIONALIZATION ###
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_TZ = True
USE_I18N = True

### STATIC FILES ###
# https://docs.djangoproject.com/en/4.2/howto/static-files/
STATIC_ROOT = os.path.join(BASE_DIR, "static")
STATIC_URL = "static/"

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

DEFAULT_PAGE_SIZE = 25
DEFAULT_MAX_PAGE_SIZE = 1000
DEFAULT_PAGE_SIZE_QUERY_PARAM = "limit"

### HISTORY ###

SIMPLE_HISTORY_FILEFIELD_TO_CHARFIELD = True

### UPLOADED IMAGES ###

GALLERY_BACKGROUND_IMAGE_RESOLUTION = (1920, 1080)
GALLERY_BACKGROUND_IMAGE_FORMAT = "PNG"

### JUMPER FRONTEND UPDATES ###

ALLOW_FRONTEND_UPDATES = os.getenv(
    "ALLOW_FRONTEND_UPDATES", "true"
).lower() in (
    "true",
    "1",
)
JUMPER_REPOSITORY_URL = os.getenv(
    "JUMPER_REPOSITORY_URL", "https://api.github.com/repos/Jumper-Carrot/Jumper"
)
MAX_ALLOWED_VERSION = os.getenv(
    "MAX_ALLOWED_VERSION", DEFAULT_JUMPER_MAX_VERSION
)
