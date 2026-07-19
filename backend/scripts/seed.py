"""
Idempotent seed script: creates the Computer Science department and a
default Super Administrator account so the app is usable immediately
after deployment.

Run with:
    python -m scripts.seed
"""
import asyncio
import os
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from sqlalchemy import select  # noqa: E402

from app.core.security import hash_password  # noqa: E402
from app.db.session import AsyncSessionLocal  # noqa: E402
from app.models.academics import Department  # noqa: E402
from app.models.enums import AccountStatus, AIProviderName, UserRole  # noqa: E402
from app.models.system import AIProviderSetting, ApplicationSetting  # noqa: E402
from app.models.user import User  # noqa: E402

DEFAULT_ADMIN_EMAIL = os.getenv("SEED_ADMIN_EMAIL", "admin@cosib.local")
DEFAULT_ADMIN_PASSWORD = os.getenv("SEED_ADMIN_PASSWORD", "ChangeMe123!")


async def seed() -> None:
    async with AsyncSessionLocal() as db:
        # --- Department ---
        result = await db.execute(select(Department).where(Department.name == "Computer Science"))
        department = result.scalar_one_or_none()
        if not department:
            department = Department(
                name="Computer Science",
                faculty="School of Applied Sciences",
                overview="The Computer Science Department of Gateway ICT Polytechnic, Saapade.",
            )
            db.add(department)
            await db.flush()
            print("Created Computer Science department")

        # --- Super admin ---
        result = await db.execute(select(User).where(User.email == DEFAULT_ADMIN_EMAIL))
        admin = result.scalar_one_or_none()
        if not admin:
            admin = User(
                email=DEFAULT_ADMIN_EMAIL,
                username="cosib_admin",
                hashed_password=hash_password(DEFAULT_ADMIN_PASSWORD),
                full_name="COSIB Super Administrator",
                role=UserRole.SUPER_ADMIN,
                status=AccountStatus.ACTIVE,
                is_email_verified=True,
                department_id=department.id,
            )
            db.add(admin)
            print(f"Created super admin: {DEFAULT_ADMIN_EMAIL} / {DEFAULT_ADMIN_PASSWORD} (change immediately)")
        else:
            print("Super admin already exists, skipping")

        # --- AI provider settings (mock active by default until real keys are added) ---
        result = await db.execute(select(AIProviderSetting))
        existing_providers = {row.provider for row in result.scalars().all()}
        for provider in AIProviderName:
            if provider.value in existing_providers:
                continue
            db.add(
                AIProviderSetting(
                    provider=provider.value,
                    is_active=(provider == AIProviderName.MOCK),
                    is_enabled=True,
                    temperature=0.7,
                    max_tokens=1024,
                    streaming_enabled=True,
                    system_prompt=None,
                )
            )
        if AIProviderName.MOCK.value not in existing_providers:
            print("Seeded AI provider settings (mock active by default)")

        # --- Default application settings ---
        default_settings = {
            "app_name": ("COSIB", None, "Displayed application name"),
            "app_logo_url": ("", None, "URL to the application logo"),
            "primary_color": ("#0F172A", None, "Deep Navy — primary brand color"),
            "secondary_color": ("#2563EB", None, "Royal Blue — secondary brand color"),
            "support_email": ("support@cosib.local", None, "Support contact email shown to students"),
            "maintenance_mode": ("false", None, "When 'true', the frontend should show a maintenance page"),
        }
        result = await db.execute(select(ApplicationSetting))
        existing_keys = {row.key for row in result.scalars().all()}
        for key, (value, value_json, description) in default_settings.items():
            if key in existing_keys:
                continue
            db.add(ApplicationSetting(key=key, value=value, value_json=value_json, description=description))
        if "app_name" not in existing_keys:
            print("Seeded default application settings")

        await db.commit()
    print("Seeding complete.")


if __name__ == "__main__":
    asyncio.run(seed())
