import os
import smtplib
from email.message import EmailMessage
from html import escape

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(title="Newcastle Repair Centre Contact API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://192.168.1.230:8090",
        "http://localhost:8090",
        "http://127.0.0.1:5500",
        "http://localhost:5500",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


MAX_IMAGES = 5
MAX_IMAGE_SIZE_MB = 8
MAX_IMAGE_SIZE_BYTES = MAX_IMAGE_SIZE_MB * 1024 * 1024


@app.get("/api/health")
def health_check():
    return {"status": "ok"}


@app.post("/api/contact")
async def submit_contact_form(
    name: str = Form(...),
    phone: str = Form(...),
    vehicle: str = Form(""),
    message: str = Form(...),
    company: str = Form(""),
    images: list[UploadFile] = File(default=[]),
):
    # Honeypot spam protection. Real users should not fill this in.
    if company:
        return {"success": True, "message": "Enquiry received"}

    if len(name.strip()) < 2:
        raise HTTPException(status_code=400, detail="Name is too short")

    if len(phone.strip()) < 5:
        raise HTTPException(status_code=400, detail="Phone number is too short")

    if len(message.strip()) < 5:
        raise HTTPException(status_code=400, detail="Message is too short")

    if len(images) > MAX_IMAGES:
        raise HTTPException(
            status_code=400,
            detail=f"Please upload no more than {MAX_IMAGES} images",
        )

    smtp_host = os.getenv("SMTP_HOST")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_username = os.getenv("SMTP_USERNAME")
    smtp_password = os.getenv("SMTP_PASSWORD")
    from_email = os.getenv("FROM_EMAIL")
    company_email = os.getenv("COMPANY_EMAIL")

    if not all([smtp_host, smtp_username, smtp_password, from_email, company_email]):
        raise HTTPException(
            status_code=500,
            detail="Email settings are missing on the server",
        )

    email = EmailMessage()
    email["Subject"] = f"Website enquiry from {name}"
    email["From"] = from_email
    email["To"] = company_email
    email["Reply-To"] = from_email

    plain_body = f"""
New website enquiry

Name: {name}
Phone: {phone}
Vehicle: {vehicle or "Not provided"}

Message:
{message}
"""

    html_body = f"""
    <h2>New website enquiry</h2>

    <p><strong>Name:</strong> {escape(name)}</p>
    <p><strong>Phone:</strong> {escape(phone)}</p>
    <p><strong>Vehicle:</strong> {escape(vehicle or "Not provided")}</p>

    <p><strong>Message:</strong></p>
    <p>{escape(message).replace(chr(10), "<br>")}</p>
    """

    email.set_content(plain_body)
    email.add_alternative(html_body, subtype="html")

    for image in images:
        if not image.filename:
            continue

        if not image.content_type or not image.content_type.startswith("image/"):
            raise HTTPException(
                status_code=400,
                detail="Only image uploads are allowed",
            )

        image_bytes = await image.read()

        if len(image_bytes) > MAX_IMAGE_SIZE_BYTES:
            raise HTTPException(
                status_code=400,
                detail=f"Each image must be under {MAX_IMAGE_SIZE_MB}MB",
            )

        image_type = image.content_type.split("/")[-1]

        email.add_attachment(
            image_bytes,
            maintype="image",
            subtype=image_type,
            filename=image.filename,
        )

    try:
        with smtplib.SMTP(smtp_host, smtp_port) as smtp:
            smtp.starttls()
            smtp.login(smtp_username, smtp_password)
            smtp.send_message(email)
    except Exception as error:
        print("Email sending failed:", error)
        raise HTTPException(
            status_code=500,
            detail="Could not send enquiry email",
        )

    return {
        "success": True,
        "message": "Thank you. Your enquiry has been sent.",
    }