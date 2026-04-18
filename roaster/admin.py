from django.contrib import admin
from .models import ResumeRoast

# admin.site.register(ResumeRoast)


@admin.register(ResumeRoast)
class ResumeRoastAdmin(admin.ModelAdmin):
    list_display = ('id', 'created_at', 'short_text')
    search_fields = ('resume_text', 'extracted_text')
    list_filter = ('created_at',)
    

    def short_text(self, obj):
        return obj.extracted_text[:50]