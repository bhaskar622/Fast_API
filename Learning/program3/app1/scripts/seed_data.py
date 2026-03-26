# scripts/seed_data.py
import asyncio
from app.db.session import AsyncSessionLocal
from app.models.user import User
from app.models.project import Project
from app.models.task import Task


async def seed():
    async with AsyncSessionLocal() as session:
        # Create a user
        user = User(
            email="alice@example.com",
            name="Alice",
            password_hash="$2b$12$hashed_password_here",  # bcrypt hash
        )
        session.add(user)

        # Create a project
        project = Project(name="Website Redesign", description="Q1 goal")
        session.add(project)

        # Flush assigns IDs without committing to DB
        # This lets us use user.id and project.id before committing
        await session.flush()

        # Create tasks linked to user and project
        tasks = [
            Task(title="Design mockups", owner_id=user.id, project_id=project.id),
            Task(title="Write API", status="in_progress", owner_id=user.id, project_id=project.id),
            Task(title="Deploy to staging", owner_id=user.id, project_id=project.id),
        ]
        session.add_all(tasks)

        # Commit writes everything to PostgreSQL
        await session.commit()
        print(f"Seeded: 1 user, 1 project, {len(tasks)} tasks")


asyncio.run(seed())
