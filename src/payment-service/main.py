from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import psycopg2
import uuid
from auth_service.auth import protected_route, get_current_user

app = FastAPI()

DB_CONFIG = {
    "host": "postgres",
    "database": "payments",
    "user": "program",
    "password": "test"
}

@app.get("/manage/health")
def health():
    return JSONResponse(content={"status": "OK"})

class CreatePaymentRequest(BaseModel):
    price: int

@app.post("/api/v1/payment")
@protected_route
def create_payment(request: Request, current_user: str, req: CreatePaymentRequest):
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        payment_uid = str(uuid.uuid4())
        cur.execute(
            "INSERT INTO payment (payment_uid, status, price) VALUES (%s, %s, %s)",
            (payment_uid, "PAID", req.price)
        )
        conn.commit()
        cur.close()
        conn.close()
        return JSONResponse(content={"paymentUid": payment_uid, "status": "PAID", "price": req.price})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/payment/{payment_uid}")
@protected_route
def get_payment(request: Request, current_user: str, payment_uid: str):
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        cur.execute("SELECT payment_uid, status, price FROM payment WHERE payment_uid = %s", (payment_uid,))
        row = cur.fetchone()
        cur.close()
        conn.close()
        if not row:
            raise HTTPException(status_code=404, detail="Payment not found")
        return JSONResponse(content={"paymentUid": str(row[0]), "status": row[1], "price": row[2]})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/v1/payment/{payment_uid}")
@protected_route
def cancel_payment(request: Request, current_user: str, payment_uid: str):
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        cur.execute("UPDATE payment SET status = 'CANCELED' WHERE payment_uid = %s", (payment_uid,))
        if cur.rowcount == 0:
            raise HTTPException(status_code=404, detail="Payment not found")
        conn.commit()
        cur.close()
        conn.close()
        return JSONResponse(content={"status": "CANCELED"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
