from app import app, db
import sqlalchemy as sa
import sqlalchemy.orm as orm
from app.models import Building, Expense, Group, Unit, Resident


@app.shell_context_processor
def make_shell_context():
    return {
        "sa": sa,
        "orm": orm,
        "db": db,
        "Building": Building,
        "Expense": Expense,
        "Group": Group,
        "Resident": Resident,
        "Unit": Unit,
    }
