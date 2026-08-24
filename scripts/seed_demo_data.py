import asyncio
import os
import sys
from datetime import datetime, timedelta, timezone

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from app.db.database import AsyncSessionLocal, engine, Base
from app.models.models import User, Apartment, Complaint, ComplaintHistory, Notice
from app.core.security import get_password_hash

async def seed_data():
    print("Initializing Database Tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as db:
        print("Seeding Apartments & Users...")
        apt_admin = Apartment(building="Block A", floor=5, unit_number="501")
        apt_res1 = Apartment(building="Block A", floor=1, unit_number="101")
        apt_res2 = Apartment(building="Block C", floor=2, unit_number="204")
        apt_res3 = Apartment(building="Block B", floor=3, unit_number="302")
        db.add_all([apt_admin, apt_res1, apt_res2, apt_res3])
        await db.flush()

        admin = User(
            name="Society Admin",
            email="admin@nexus.society",
            password_hash=get_password_hash("admin123"),
            role="admin",
            apartment_id=apt_admin.id
        )
        res1 = User(
            name="Rahul Sharma",
            email="resident@nexus.society",
            password_hash=get_password_hash("resident123"),
            role="resident",
            apartment_id=apt_res1.id
        )
        res2 = User(
            name="Priya Patel",
            email="resident2@nexus.society",
            password_hash=get_password_hash("resident123"),
            role="resident",
            apartment_id=apt_res2.id
        )
        res3 = User(
            name="Anish Kumar",
            email="resident3@nexus.society",
            password_hash=get_password_hash("resident123"),
            role="resident",
            apartment_id=apt_res3.id
        )
        db.add_all([admin, res1, res2, res3])
        await db.flush()

        now = datetime.now(timezone.utc)

        print("Seeding Scenario 1: Strong Pattern ('Post-Rain Structural Moisture — Block C')...")
        strong_complaints_data = [
            ("Plumbing", "Water collecting and pooling near C-204 ceiling joint after heavy rain", "Heavy Rain", 0.1),
            ("Plumbing", "Water seepage through outer wall in C-205 hallway following rainfall", "Heavy Rain", 0.2),
            ("Cleaning", "Damp wall after rainfall causing ceiling mold and water stains", "Heavy Rain", 0.25),
            ("Cleaning", "Floor requires repeated cleaning due to rainwater dripping from corridor beam", "Heavy Rain", 0.3),
            ("General", "Moisture appearing near Block C stairwell and plaster peeling post rain", "Heavy Rain", 0.35),
            ("General", "Wall stain and damp patch forming after heavy rain near elevator shaft C", "Heavy Rain", 0.4),
            ("Electrical", "Water seepage near Block C electric distribution box causing short circuit risk", "Heavy Rain", 0.45),
            ("Electrical", "Dampness leaking into corridor light fixture near Block C 2nd floor post rainfall", "Heavy Rain", 0.5),
            ("Plumbing", "Water trickling down Block C pipe duct shaft after heavy rain", "Heavy Rain", 0.52),
            ("Cleaning", "Persistent water puddle and moisture smell in Block C lobby post heavy rain", "Heavy Rain", 0.55),
        ]

        for cat, desc, weather, delta_hours in strong_complaints_data:
            c = Complaint(
                resident_id=res2.id,
                apartment_id=apt_res2.id,
                category=cat,
                description=desc,
                priority="High",
                status="Open",
                weather_event=weather,
                created_at=now - timedelta(hours=delta_hours)
            )
            db.add(c)
            await db.flush()
            db.add(ComplaintHistory(
                complaint_id=c.id,
                actor_id=res2.id,
                from_status="None",
                to_status="Open",
                note="Reported post rainfall",
                timestamp=c.created_at
            ))

        print("Seeding Scenario 2: Weak Pattern...")
        weak_data = [
            ("Plumbing", "Minor pipe vibration noise in kitchen tap", 6.0),
            ("General", "Slight metallic hum near basement pipe", 3.0),
            ("Plumbing", "Low water pressure in kitchen faucet late night", 0.5)
        ]
        for cat, desc, delta_days in weak_data:
            c = Complaint(
                resident_id=res1.id,
                apartment_id=apt_res1.id,
                category=cat,
                description=desc,
                priority="Low",
                status="Open",
                created_at=now - timedelta(days=delta_days)
            )
            db.add(c)
            await db.flush()
            db.add(ComplaintHistory(
                complaint_id=c.id,
                actor_id=res1.id,
                from_status="None",
                to_status="Open",
                timestamp=c.created_at
            ))

        print("Seeding Scenario 3: Null Pattern (Uncorrelated noise)...")
        null_data = [
            ("Cosmetic", "Gym treadmill display screen flickering", 5.0),
            ("General", "Visitor parking tag lost near main security gate", 4.0),
            ("Electrical", "Lobby chandelier bulb dimming", 2.0),
            ("Cleaning", "Dog waste found near garden footpath", 1.0)
        ]
        for cat, desc, delta_days in null_data:
            c = Complaint(
                resident_id=res3.id,
                apartment_id=apt_res3.id,
                category=cat,
                description=desc,
                priority="Medium",
                status="Open",
                created_at=now - timedelta(days=delta_days)
            )
            db.add(c)
            await db.flush()
            db.add(ComplaintHistory(
                complaint_id=c.id,
                actor_id=res3.id,
                from_status="None",
                to_status="Open",
                timestamp=c.created_at
            ))

        print("Seeding Scenario 4: Single Category Plumbing Cluster in Block B...")
        for i in range(6):
            c = Complaint(
                resident_id=res3.id,
                apartment_id=apt_res3.id,
                category="Plumbing",
                description=f"Block B water pressure drop in unit {301+i} bathroom",
                priority="Low",
                status="Open",
                created_at=now - timedelta(days=1, hours=i)
            )
            db.add(c)

        print("Seeding Scenario 5: Duplicate Complaints (Identical Plumbing text across residents)...")
        dup_residents = [res1, res2, res3, res1, res2]
        for i, res in enumerate(dup_residents):
            c = Complaint(
                resident_id=res.id,
                apartment_id=res.apartment_id,
                category="Plumbing",
                description="Water leaking from main kitchen pipe duct shaft",
                priority="Medium",
                status="Open",
                created_at=now - timedelta(hours=i * 2)
            )
            db.add(c)
            await db.flush()
            db.add(ComplaintHistory(
                complaint_id=c.id,
                actor_id=res.id,
                from_status="None",
                to_status="Open",
                timestamp=c.created_at
            ))

        print("Seeding Notices...")
        n1 = Notice(
            admin_id=admin.id,
            title="Annual Society Water Tank Cleaning Schedule",
            body="Water supply will be suspended on Sunday from 9:00 AM to 2:00 PM for overhead tank sanitization.",
            is_important=True,
            created_at=now - timedelta(days=1)
        )
        n2 = Notice(
            admin_id=admin.id,
            title="Clubhouse Gym Equipment Upgrade",
            body="New elliptical trainers and dumbbell sets have been installed in the clubhouse gym.",
            is_important=False,
            created_at=now - timedelta(days=3)
        )
        db.add_all([n1, n2])

        overdue_c = Complaint(
            resident_id=res1.id,
            apartment_id=apt_res1.id,
            category="Electrical",
            description="Main circuit breaker tripping repeatedly in A-101 panel",
            priority="High",
            status="Open",
            created_at=now - timedelta(days=5)
        )
        db.add(overdue_c)
        await db.flush()
        db.add(ComplaintHistory(
            complaint_id=overdue_c.id,
            actor_id=res1.id,
            from_status="None",
            to_status="Open",
            note="Urgent electrical fault reported",
            timestamp=overdue_c.created_at
        ))

        await db.commit()
        print("\nSeed completed successfully!")
        print("Demo Credentials:")
        print("  Admin Account:    admin@nexus.society    / admin123")
        print("  Resident Account: resident@nexus.society / resident123")

if __name__ == "__main__":
    asyncio.run(seed_data())
