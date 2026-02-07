"""Verify JWT configuration is loaded correctly."""
from app.config import settings

print("=" * 60)
print("JWT CONFIGURATION STATUS")
print("=" * 60)
print(f"JWT Secret (first 10 chars): {settings.jwt_secret[:10]}...")
print(f"Better Auth Secret (first 10 chars): {settings.better_auth_secret[:10]}...")
print(f"Algorithm: {settings.jwt_algorithm}")
print(f"Token Expire Minutes: {settings.access_token_expire_minutes}")
print(f"Database URL: {settings.database_url[:30]}...")
print(f"CORS Origins: {settings.cors_origins}")
print(f"Debug Mode: {settings.debug}")
print("=" * 60)

if settings.jwt_secret and settings.better_auth_secret:
    print("[SUCCESS] JWT configuration loaded successfully!")
else:
    print("[ERROR] JWT secrets not loaded!")
