from django.contrib import admin
from .models import StudentMarks

@admin.register(StudentMarks)
class StudentMarksAdmin(admin.ModelAdmin):
    list_display = ('s_no', 'regd_no', 'semester', 'batch', 'subject_name', 
                    'display_m1q1a', 'display_m1q1b', 'display_m1q2a', 'display_m1q2b', 
                    'display_m1q3a', 'display_m1q3b', 'display_m1qu1', 'display_m1a1',
                    'display_m2q1a', 'display_m2q1b', 'display_m2q2a', 'display_m2q2b', 
                    'display_m2q3a', 'display_m2q3b', 'display_m2qu2', 'display_m2a2')
    search_fields = ('regd_no', 'subject_name', 'batch')
    list_filter = ('semester', 'batch', 'subject_name')
    ordering = ('s_no',)
    empty_value_display = ''
    
    # Custom display methods to show empty string instead of hyphen for null values
    def display_m1q1a(self, obj):
        return obj.m1q1a if obj.m1q1a is not None else ''
    display_m1q1a.short_description = 'M1Q1a'
    display_m1q1a.empty_value_display = ''
    
    def display_m1q1b(self, obj):
        return obj.m1q1b if obj.m1q1b is not None else ''
    display_m1q1b.short_description = 'M1Q1b'
    display_m1q1b.empty_value_display = ''
    
    def display_m1q2a(self, obj):
        return obj.m1q2a if obj.m1q2a is not None else ''
    display_m1q2a.short_description = 'M1Q2a'
    display_m1q2a.empty_value_display = ''
    
    def display_m1q2b(self, obj):
        return obj.m1q2b if obj.m1q2b is not None else ''
    display_m1q2b.short_description = 'M1Q2b'
    display_m1q2b.empty_value_display = ''
    
    def display_m1q3a(self, obj):
        return obj.m1q3a if obj.m1q3a is not None else ''
    display_m1q3a.short_description = 'M1Q3a'
    display_m1q3a.empty_value_display = ''
    
    def display_m1q3b(self, obj):
        return obj.m1q3b if obj.m1q3b is not None else ''
    display_m1q3b.short_description = 'M1Q3b'
    display_m1q3b.empty_value_display = ''
    
    def display_m1qu1(self, obj):
        return obj.m1qu1 if obj.m1qu1 is not None else ''
    display_m1qu1.short_description = 'M1Qu1'
    display_m1qu1.empty_value_display = ''
    
    def display_m1a1(self, obj):
        return obj.m1a1 if obj.m1a1 is not None else ''
    display_m1a1.short_description = 'M1A1'
    display_m1a1.empty_value_display = ''
    
    def display_m2q1a(self, obj):
        return obj.m2q1a if obj.m2q1a is not None else ''
    display_m2q1a.short_description = 'M2Q1a'
    display_m2q1a.empty_value_display = ''
    
    def display_m2q1b(self, obj):
        return obj.m2q1b if obj.m2q1b is not None else ''
    display_m2q1b.short_description = 'M2Q1b'
    display_m2q1b.empty_value_display = ''
    
    def display_m2q2a(self, obj):
        return obj.m2q2a if obj.m2q2a is not None else ''
    display_m2q2a.short_description = 'M2Q2a'
    display_m2q2a.empty_value_display = ''
    
    def display_m2q2b(self, obj):
        return obj.m2q2b if obj.m2q2b is not None else ''
    display_m2q2b.short_description = 'M2Q2b'
    display_m2q2b.empty_value_display = ''
    
    def display_m2q3a(self, obj):
        return obj.m2q3a if obj.m2q3a is not None else ''
    display_m2q3a.short_description = 'M2Q3a'
    display_m2q3a.empty_value_display = ''
    
    def display_m2q3b(self, obj):
        return obj.m2q3b if obj.m2q3b is not None else ''
    display_m2q3b.short_description = 'M2Q3b'
    display_m2q3b.empty_value_display = ''
    
    def display_m2qu2(self, obj):
        return obj.m2qu2 if obj.m2qu2 is not None else ''
    display_m2qu2.short_description = 'M2Qu2'
    display_m2qu2.empty_value_display = ''
    
    def display_m2a2(self, obj):
        return obj.m2a2 if obj.m2a2 is not None else ''
    display_m2a2.short_description = 'M2A2'
    display_m2a2.empty_value_display = ''
