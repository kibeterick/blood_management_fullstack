"""
Laboratory Testing Module
Manages blood testing, quality control, and disease screening
"""
from django.db import models
from django.utils import timezone
from .models import BloodDonation, Donor


class BloodTest(models.Model):
    """
    Blood test results for donated blood
    """
    TEST_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    RESULT_CHOICES = [
        ('pass', 'Pass'),
        ('fail', 'Fail'),
        ('inconclusive', 'Inconclusive'),
    ]
    
    donation = models.OneToOneField(
        BloodDonation,
        on_delete=models.CASCADE,
        related_name='blood_test'
    )
    test_date = models.DateTimeField(default=timezone.now)
    tested_by = models.CharField(max_length=200, help_text="Lab technician name")
    
    # Test status
    status = models.CharField(
        max_length=20,
        choices=TEST_STATUS_CHOICES,
        default='pending'
    )
    
    # Disease screening tests
    hiv_test = models.CharField(max_length=20, choices=RESULT_CHOICES, default='pending')
    hepatitis_b_test = models.CharField(max_length=20, choices=RESULT_CHOICES, default='pending')
    hepatitis_c_test = models.CharField(max_length=20, choices=RESULT_CHOICES, default='pending')
    syphilis_test = models.CharField(max_length=20, choices=RESULT_CHOICES, default='pending')
    malaria_test = models.CharField(max_length=20, choices=RESULT_CHOICES, default='pending')
    
    # Blood quality tests
    hemoglobin_level = models.FloatField(
        null=True,
        blank=True,
        help_text="Hemoglobin level in g/dL (normal: 12.5-17.5)"
    )
    blood_pressure_systolic = models.IntegerField(
        null=True,
        blank=True,
        help_text="Systolic BP (normal: 90-140)"
    )
    blood_pressure_diastolic = models.IntegerField(
        null=True,
        blank=True,
        help_text="Diastolic BP (normal: 60-90)"
    )
    temperature = models.FloatField(
        null=True,
        blank=True,
        help_text="Body temperature in °C (normal: 36.5-37.5)"
    )
    weight = models.FloatField(
        null=True,
        blank=True,
        help_text="Weight in kg (minimum: 50kg)"
    )
    
    # Overall result
    overall_result = models.CharField(
        max_length=20,
        choices=RESULT_CHOICES,
        default='inconclusive'
    )
    
    # Additional notes
    notes = models.TextField(blank=True, null=True)
    rejection_reason = models.TextField(
        blank=True,
        null=True,
        help_text="Reason if blood is rejected"
    )
    
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-test_date']
    
    def __str__(self):
        return f"Test for {self.donation.donor} - {self.overall_result}"
    
    def check_disease_screening(self):
        """
        Check if all disease screening tests passed
        """
        tests = [
            self.hiv_test,
            self.hepatitis_b_test,
            self.hepatitis_c_test,
            self.syphilis_test,
            self.malaria_test,
        ]
        
        # If any test failed, blood is rejected
        if 'fail' in tests:
            return False, "Disease screening failed"
        
        # If any test is inconclusive, need retest
        if 'inconclusive' in tests:
            return False, "Inconclusive results - retest required"
        
        # If any test is still pending
        if 'pending' in tests:
            return False, "Tests not completed"
        
        # All tests passed
        return True, "All disease screening tests passed"
    
    def check_blood_quality(self):
        """
        Check if blood quality parameters are within acceptable range
        """
        issues = []
        
        # Check hemoglobin
        if self.hemoglobin_level:
            if self.hemoglobin_level < 12.5:
                issues.append("Low hemoglobin level")
            elif self.hemoglobin_level > 17.5:
                issues.append("High hemoglobin level")
        
        # Check blood pressure
        if self.blood_pressure_systolic and self.blood_pressure_diastolic:
            if self.blood_pressure_systolic < 90 or self.blood_pressure_systolic > 140:
                issues.append("Abnormal systolic blood pressure")
            if self.blood_pressure_diastolic < 60 or self.blood_pressure_diastolic > 90:
                issues.append("Abnormal diastolic blood pressure")
        
        # Check temperature
        if self.temperature:
            if self.temperature < 36.5 or self.temperature > 37.5:
                issues.append("Abnormal body temperature")
        
        # Check weight
        if self.weight:
            if self.weight < 50:
                issues.append("Weight below minimum requirement (50kg)")
        
        if issues:
            return False, "; ".join(issues)
        
        return True, "Blood quality parameters normal"
    
    def evaluate_test_results(self):
        """
        Evaluate all test results and determine overall result
        """
        # Check disease screening
        disease_pass, disease_msg = self.check_disease_screening()
        
        # Check blood quality
        quality_pass, quality_msg = self.check_blood_quality()
        
        # Determine overall result
        if disease_pass and quality_pass:
            self.overall_result = 'pass'
            self.status = 'completed'
            self.completed_at = timezone.now()
            
            # Approve the donation
            self.donation.status = 'approved'
            self.donation.save()
            
            return True, "Blood test passed - safe for transfusion"
        else:
            self.overall_result = 'fail'
            self.status = 'completed'
            self.completed_at = timezone.now()
            
            # Reject the donation
            self.donation.status = 'rejected'
            rejection_reasons = []
            if not disease_pass:
                rejection_reasons.append(disease_msg)
            if not quality_pass:
                rejection_reasons.append(quality_msg)
            
            self.rejection_reason = "; ".join(rejection_reasons)
            self.donation.rejection_reason = self.rejection_reason
            self.donation.save()
            
            return False, self.rejection_reason
    
    def save(self, *args, **kwargs):
        """Auto-evaluate results when all tests are complete"""
        super().save(*args, **kwargs)
        
        # If all required fields are filled, evaluate
        if (self.hiv_test != 'pending' and 
            self.hepatitis_b_test != 'pending' and 
            self.hepatitis_c_test != 'pending' and
            self.status != 'completed'):
            self.evaluate_test_results()
            super().save(*args, **kwargs)


def create_blood_test(donation, tested_by):
    """
    Create a new blood test record for a donation
    """
    test, created = BloodTest.objects.get_or_create(
        donation=donation,
        defaults={'tested_by': tested_by}
    )
    return test


def get_pending_tests():
    """
    Get all pending blood tests
    """
    return BloodTest.objects.filter(
        status__in=['pending', 'in_progress']
    ).select_related('donation', 'donation__donor')


def get_failed_tests():
    """
    Get all failed blood tests
    """
    return BloodTest.objects.filter(
        overall_result='fail'
    ).select_related('donation', 'donation__donor')


def get_test_statistics():
    """
    Get statistics about blood tests
    """
    total_tests = BloodTest.objects.count()
    passed = BloodTest.objects.filter(overall_result='pass').count()
    failed = BloodTest.objects.filter(overall_result='fail').count()
    pending = BloodTest.objects.filter(status__in=['pending', 'in_progress']).count()
    
    pass_rate = (passed / total_tests * 100) if total_tests > 0 else 0
    
    # Disease-specific statistics
    hiv_positive = BloodTest.objects.filter(hiv_test='fail').count()
    hep_b_positive = BloodTest.objects.filter(hepatitis_b_test='fail').count()
    hep_c_positive = BloodTest.objects.filter(hepatitis_c_test='fail').count()
    
    return {
        'total_tests': total_tests,
        'passed': passed,
        'failed': failed,
        'pending': pending,
        'pass_rate': round(pass_rate, 2),
        'disease_stats': {
            'hiv_positive': hiv_positive,
            'hepatitis_b_positive': hep_b_positive,
            'hepatitis_c_positive': hep_c_positive,
        }
    }


def mark_donor_ineligible_due_to_disease(donor, disease_name):
    """
    Mark a donor as permanently ineligible due to disease detection
    """
    donor.is_available = False
    donor.save()
    
    # Send notification to donor (handled separately for privacy)
    return True
