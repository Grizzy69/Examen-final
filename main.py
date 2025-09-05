from datetime import date
from typing import List
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr, Field

app = FastAPI(
    title="STD24120",
    description="This is a specification of STD24120",
    version="1.0.0"
)

# --- Modèles (mémoire vive, pas de DB) ---

class Customer(BaseModel):
    name: str = Field(..., description="Nom du client")
    phone: str = Field(..., description="Téléphone du client")
    email: EmailStr = Field(..., description="Email du client")

class Room(BaseModel):
    roomNumber: int = Field(..., ge=1, le=9, description="Numéro de chambre entre 1 et 9")
    roomName: str | None = Field(None, description="Libellé de la chambre")
    description: str | None = Field(None, description="Description de la chambre")

class BookingCreate(Customer, Room):
    bookingDate: date = Field(..., description="Date de réservation (YYYY-MM-DD)")

class Booking(BookingCreate):
    id: int = Field(..., description="Identifiant interne de la réservation")

# Mémoire vive
BOOKINGS: List[Booking] = []
_next_id = 1

def _already_reserved(room_number: int, day: date) -> bool:
    return any(b.roomNumber == room_number and b.bookingDate == day for b in BOOKINGS)

# --- Routes ---

@app.get("/booking", response_model=List[Booking], summary="Lister les réservations")
def list_bookings():
    return BOOKINGS

@app.post("/booking", response_model=List[Booking], summary="Créer des réservations (liste)")
def create_bookings(payload: List[BookingCreate]):
    """
    Crée une *liste* de réservations.
    - Refuse une réservation si la même chambre est déjà réservée à la même date.
    - Les chambres valides sont *1..9*.
    - Retourne la *liste complète* des réservations en mémoire (statut 200).
    """
    global _next_id

    # Validations + disponibilités
    for item in payload:
        # bonus: plage 1..9 déjà garantie par Pydantic (ge/le)
        if _already_reserved(item.roomNumber, item.bookingDate):
            raise HTTPException(
                status_code=409,
                detail=f"La chambre {item.roomNumber} n'est pas disponible le {item.bookingDate}."
            )

    # Création
    for item in payload:
        BOOKINGS.append(Booking(id=_next_id, **item.model_dump()))
        _next_id += 1

    return BOOKINGS