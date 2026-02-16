from django.db import models


class StudentMarks(models.Model):
    """Model to store student marks"""
    semester = models.CharField(max_length=50, default='')
    batch = models.CharField(max_length=50, default='')
    subject_name = models.CharField(max_length=100, default='')
    s_no = models.IntegerField()
    regd_no = models.CharField(max_length=20)
    
    # MID I marks - M1Q1a, M1Q1b, M1Q2a, M1Q2b, M1Q3a, M1Q3b, M1Qu1, M1A1
    m1q1a = models.IntegerField(default=0, null=True, blank=True)
    m1q1b = models.IntegerField(default=0, null=True, blank=True)
    m1q2a = models.IntegerField(default=0, null=True, blank=True)
    m1q2b = models.IntegerField(default=0, null=True, blank=True)
    m1q3a = models.IntegerField(default=0, null=True, blank=True)
    m1q3b = models.IntegerField(default=0, null=True, blank=True)
    m1qu1 = models.IntegerField(default=0, null=True, blank=True)
    m1a1 = models.IntegerField(default=0, null=True, blank=True)
    
    # MID II marks - M2Q1a, M2Q1b, M2Q2a, M2Q2b, M2Q3a, M2Q3b, M2Qu2, M2A2
    m2q1a = models.IntegerField(default=0, null=True, blank=True)
    m2q1b = models.IntegerField(default=0, null=True, blank=True)
    m2q2a = models.IntegerField(default=0, null=True, blank=True)
    m2q2b = models.IntegerField(default=0, null=True, blank=True)
    m2q3a = models.IntegerField(default=0, null=True, blank=True)
    m2q3b = models.IntegerField(default=0, null=True, blank=True)
    m2qu2 = models.IntegerField(default=0, null=True, blank=True)
    m2a2 = models.IntegerField(default=0, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'student_marks'
        ordering = ['s_no']
    
    def __str__(self):
        return f"{self.regd_no} - {self.subject_name}"
