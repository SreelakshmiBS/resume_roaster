from django.shortcuts import render
import requests
import os

from .models import ResumeRoast

# File processing libraries
import PyPDF2
import docx


OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")


# HOME PAGE
def home(request):
    return render(request, "home.html")


# EXTRACT TEXT FROM PDF
def extract_pdf(file):
    try:
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        return text
    except:
        return "Error reading PDF"


# EXTRACT TEXT FROM DOCX
def extract_docx(file):
    try:
        doc = docx.Document(file)
        return "\n".join([p.text for p in doc.paragraphs])
    except:
        return "Error reading DOCX 😅"

# MAIN ROAST FUNCTION
def roast_resume(request):
    result = ""
    extracted_text = ""

    # ❌ API key missing
    if not OPENROUTER_API_KEY:
        return render(request, "roast.html", {
            "result": "API key not configured 😢"
        })

    if request.method == "POST":

        resume_text = request.POST.get("resume_text", "")
        file = request.FILES.get("resume_file")

        # 🗄 Save initial data
        obj = ResumeRoast.objects.create(
            resume_text=resume_text,
            uploaded_file=file
        )

        # 📂 Extract text from uploaded file
        if file:
            file_name = file.name.lower()

            if file_name.endswith(".pdf"):
                extracted_text = extract_pdf(file)

            elif file_name.endswith(".docx"):
                extracted_text = extract_docx(file)

            else:
                extracted_text = "Unsupported file type 😅"

        # 📝 Add manual text input
        if resume_text:
            extracted_text += "\n" + resume_text

        # Save extracted text
        obj.extracted_text = extracted_text
        obj.save()

        # ❌ Empty input
        if not extracted_text.strip():
            return render(request, "roast.html", {
                "result": "No resume provided 😅"
            })

        # 🧠 AI PROMPT
        prompt = f"""
You are a funny but respectful AI resume reviewer.

Your job is to review resumes like a friendly tech recruiter who uses humor.

Rules:
- Be funny and light-hearted (NO disrespect)
- Do NOT insult the user
- Give both GOOD and BAD points
- Friendly roast tone with emojis

Output format:

🔥 GOOD POINTS:
- 2-3 strengths

⚠️ NEEDS IMPROVEMENT:
- 2-3 weaknesses

😂 FUNNY ROAST:
- one light joke

📊 SCORE:
- X/10 with short explanation

Resume:
{extracted_text}
"""

        # 🌐 API HEADERS
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://127.0.0.1:8000",
            "X-Title": "Resume Roaster"
        }

        # 📡 API PAYLOAD
        payload = {
            "model": "openai/gpt-4o-mini",
            "messages": [
                {"role": "user", "content": prompt}
            ]
        }

        # 🚀 CALL OPENROUTER API
        try:
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=15
            )

            if response.status_code == 200:
                data = response.json()
                result = data.get("choices", [{}])[0].get("message", {}).get("content", "No response from AI")
            else:
                result = f"Error: {response.status_code} - {response.text}"

        except Exception as e:
            result = f"Something went wrong 😢: {str(e)}"

        # 💾 Save AI result
        obj.roast_result = result
        obj.save()

    return render(request, "roast.html", {"result": result})