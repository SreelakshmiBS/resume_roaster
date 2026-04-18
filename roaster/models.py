
from django.db import models

class ResumeRoast(models.Model):
    resume_text =models.TextField(blank=True, null=True)
    uploaded_file = models.FileField(upload_to="resumes/", blank=False, null=False)

    extracted_text = models.TextField(blank=True, null=True)
    roast_result = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"ResumeRoast {self.id}"