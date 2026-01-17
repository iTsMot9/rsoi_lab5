from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import psycopg2
import uuid
from auth_service.auth import protected_route, get_current_user

app = FastAPI()

DB_CONFIG = {
    "host": "postgres",
    "database": "rentals",
    "user": "program",
    "password": "test"
}

@app.get("/manage/health")
def health():
    return JSONResponse(content={"status": "OK"})

class RentalCreateRequest(BaseModel):
    carUid: str
    dateFrom: str
    dateTo: str
    paymentUid: str

@app.post("/api/v1/rental")
@protected_route
def create_rental(
    request: Request,
    current_user: str,
    req: RentalCreateRequest
):
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        rental_uid = str(uuid.uuid4())
        cur.execute("""
            INSERT INTO rental (rental_uid, username, payment_uid, car_uid, date_from, date_to, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (rental_uid, current_user, req.paymentUid, req.carUid, req.dateFrom, req.dateTo, "IN_PROGRESS"))
        conn.commit()
        cur.close()
        conn.close()
        return JSONResponse(content={"rentalUid": rental_uid})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/rental")
@protected_route
def get_user_rentals(request: Request, current_user: str):
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        cur.execute("""
            SELECT rental_uid, payment_uid, car_uid, date_from, date_to, status
            FROM rental WHERE username = %s
        """, (current_user,))
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return JSONResponse(content=[
            {
                "rentalUid": str(r[0]),
                "paymentUid": str(r[1]),
                "carUid": str(r[2]),
                "dateFrom": r[3].isoformat(),
                "dateTo": r[4].isoformat(),
                "status": r[5]
            }
            for r in rows
        ])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/rental/{rental_uid}")
@protected_route
def get_rental(request: Request, current_user: str, rental_uid: str):
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        cur.execute("""
            SELECT rental_uid, payment_uid, car_uid, date_from, date_to, status
            FROM rental WHERE rental_uid = %s AND username = %s
        """, (rental_uid, current_user))
        row = cur.fetchone()
        cur.close()
        conn.close()
        if not row:
            raise HTTPException(status_code=404, detail="Rental not found or access denied")
        return JSONResponse(content={
            "rentalUid": str(row[0]),
            "paymentUid": str(row[1]),
            "carUid": str(row[2]),
            "dateFrom": row[3].isoformat(),
            "dateTo": row[4].isoformat(),
            "status": row[5]
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/rental/{rental_uid}/finish")
@protected_route
def finish_rental(request: Request, current_user: str, rental_uid: str):
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        cur.execute("UPDATE rental SET status = 'FINISHED' WHERE rental_uid = %s AND username = %s", (rental_uid, current_user))
        if cur.rowcount == 0:
            raise HTTPException(status_code=404, detail="Rental not found or access denied")
        conn.commit()
        cur.close()
        conn.close()
        return JSONResponse(content={"status": "FINISHED"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/v1/rental/{rental_uid}")
@protected_route
def cancel_rental(request: Request, current_user: str, rental_uid: str):
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        cur.execute("UPDATE rental SET status = 'CANCELED' WHERE rental_uid = %s AND username = %s", (rental_uid, current_user))
        if cur.rowcount == 0:
            raise HTTPException(status_code=404, detail="Rental not found or access denied")
        conn.commit()
        cur.close()
        conn.close()
        return JSONResponse(content={"status": "CANCELED"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
