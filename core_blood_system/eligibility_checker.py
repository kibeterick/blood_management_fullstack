"""
Donor Eligibility Checker
Validates donor eligibility based on health and timing criteria
"""
from datetime import date, timedelta
from django.utils import timezone


class EligibilityChecker:
    """Utility class for checking donor eligibility"""
    
    # Eligibility constants
    MIN_AGE = 18
    MAX_AGE = 65
    MIN_WEIGHT_KG = 50
    MALE_DONATION_INTERVAL_DAYS = 56
    FEMALE_DONATION_INTERVAL_DAYS = 84
    ILLNESS_RECOVERY_DAYS = 14
    
    # Disqualifying health conditions
    DISQUALIFYING_CONDITIONS = [
        'anemia',
        'blood_pressure_issues',
        'heart_disease',
        'diabetes_insulin',
        'cancer',
        'hiv_aids',
        'hepatitis',
    ]
    
    @staticmethod
    def check_age_eligibility(age):
        """
        Check if donor meets age requirements (18-65 years)
        
        Args:
            age: Donor's age in years
            
        Returns:
            dict: {'eligible': bool, 'reason': str or None}
        """
        if age < EligibilityChecker.MIN_AGE:
            return {
                'eligible': False,
                'reason': f'Donor must be at least {EligibilityChecker.MIN_AGE} years old'
            }
        elif age > EligibilityChecker.MAX_AGE:
            return {
                'eligible': False,
                'reason': f'Donor must be {EligibilityChecker.MAX_AGE} years or younger'
            }
        return {'eligible': True, 'reason': None}
    
    @staticmethod
    def check_weight_eligibility(weight_kg):
        """
        Check if donor meets minimum weight requirement (50kg)
        
        Args:
            weight_kg: Donor's weight in kilograms
            
        Returns:
            dict: {'eligible': bool, 'reason': str or None}
        """
        if weight_kg < EligibilityChecker.MIN_WEIGHT_KG:
            return {
                'eligible': False,
                'reason': f'Donor must weigh at least {EligibilityChecker.MIN_WEIGHT_KG}kg for safety'
            }
        return {'eligible': True, 'reason': None}
    
    @staticmethod
    def check_donation_interval(last_donation_date, gender):
        """
        Check if sufficient time has passed since last donation
        Male: 56 days, Female: 84 days
        
        Args:
            last_donation_date: Date of last donation (date object or None)
            gender: 'male' or 'female'
            
        Returns:
            dict: {'eligible': bool, 'reason': str or None, 'next_eligible_date': date or None}
        """
        if not last_donation_date:
            return {'eligible': True, 'reason': None, 'next_eligible_date': None}
        
        # Determine required interval based on gender
        if gender and gender.lower() == 'female':
            required_interval = EligibilityChecker.FEMALE_DONATION_INTERVAL_DAYS
        else:
            required_interval = EligibilityChecker.MALE_DONATION_INTERVAL_DAYS
        
        # Calculate days since last donation
        days_since_donation = (date.today() - last_donation_date).days
        
        if days_since_donation < required_interval:
            days_remaining = required_interval - days_since_donation
            next_eligible_date = date.today() + timedelta(days=days_remaining)
            
            return {
                'eligible': False,
                'reason': f'Must wait {required_interval} days between donations. {days_remaining} days remaining.',
                'next_eligible_date': next_eligible_date
            }
        
        return {'eligible': True, 'reason': None, 'next_eligible_date': None}
    
    @staticmethod
    def check_health_conditions(health_data):
        """
        Check for disqualifying health conditions
        
        Args:
            health_data: dict with health condition flags
                {
                    'recent_illness': bool,
                    'illness_date': date or None,
                    'current_medication': bool,
                    'medication_details': str,
                    'anemia': bool,
                    'blood_pressure_issues': bool,
                    'heart_disease': bool,
                    'diabetes_insulin': bool,
                    'cancer': bool,
                    'hiv_aids': bool,
                    'hepatitis': bool,
                }
                
        Returns:
            dict: {'eligible': bool, 'reasons': list of str}
        """
        reasons = []
        
        # Check recent illness
        if health_data.get('recent_illness'):
            illness_date = health_data.get('illness_date')
            if illness_date:
                days_since_illness = (date.today() - illness_date).days
                if days_since_illness < EligibilityChecker.ILLNESS_RECOVERY_DAYS:
                    days_remaining = EligibilityChecker.ILLNESS_RECOVERY_DAYS - days_since_illness
                    reasons.append(
                        f'Must wait {EligibilityChecker.ILLNESS_RECOVERY_DAYS} days after illness. '
                        f'{days_remaining} days remaining.'
                    )
            else:
                reasons.append('Recent illness reported. Please wait 14 days after full recovery.')
        
        # Check current medication
        if health_data.get('current_medication'):
            medication_details = health_data.get('medication_details', '')
            if medication_details:
                reasons.append(f'Currently on medication: {medication_details}. Please consult with staff.')
            else:
                reasons.append('Currently on medication. Please consult with staff before donating.')
        
        # Check disqualifying conditions
        for condition in EligibilityChecker.DISQUALIFYING_CONDITIONS:
            if health_data.get(condition):
                condition_name = condition.replace('_', ' ').title()
                reasons.append(f'{condition_name} is a disqualifying condition for blood donation.')
        
        return {
            'eligible': len(reasons) == 0,
            'reasons': reasons
        }
    
    @staticmethod
    def calculate_next_eligible_date(ineligibility_reasons, last_donation_date=None, gender=None):
        """
        Calculate when donor will become eligible again
        
        Args:
            ineligibility_reasons: list of reason strings
            last_donation_date: date of last donation
            gender: 'male' or 'female'
            
        Returns:
            date or None: Next eligible date if temporary ineligibility
        """
        # Check if ineligibility is due to donation interval
        if last_donation_date and gender:
            interval_check = EligibilityChecker.check_donation_interval(last_donation_date, gender)
            if not interval_check['eligible'] and interval_check.get('next_eligible_date'):
                return interval_check['next_eligible_date']
        
        # Check if ineligibility is due to recent illness
        for reason in ineligibility_reasons:
            if 'illness' in reason.lower() and 'days remaining' in reason.lower():
                # Extract days remaining and calculate date
                try:
                    days_remaining = int(reason.split('days remaining')[0].split()[-1])
                    return date.today() + timedelta(days=days_remaining)
                except:
                    pass
        
        # Permanent ineligibility or unable to determine
        return None
    
    @staticmethod
    def calculate_eligibility(donor_data):
        """
        Run all eligibility checks and return comprehensive result
        
        Args:
            donor_data: dict with all donor information
                {
                    'age': int,
                    'weight': float,
                    'last_donation_date': date or None,
                    'gender': str,
                    'health_conditions': dict (see check_health_conditions)
                }
                
        Returns:
            dict: {
                'is_eligible': bool,
                'ineligibility_reasons': list of str,
                'next_eligible_date': date or None,
                'checks': dict of individual check results
            }
        """
        ineligibility_reasons = []
        checks = {}
        
        # Check age
        age_check = EligibilityChecker.check_age_eligibility(donor_data.get('age'))
        checks['age'] = age_check
        if not age_check['eligible']:
            ineligibility_reasons.append(age_check['reason'])
        
        # Check weight
        weight_check = EligibilityChecker.check_weight_eligibility(donor_data.get('weight'))
        checks['weight'] = weight_check
        if not weight_check['eligible']:
            ineligibility_reasons.append(weight_check['reason'])
        
        # Check donation interval
        interval_check = EligibilityChecker.check_donation_interval(
            donor_data.get('last_donation_date'),
            donor_data.get('gender')
        )
        checks['donation_interval'] = interval_check
        if not interval_check['eligible']:
            ineligibility_reasons.append(interval_check['reason'])
        
        # Check health conditions
        health_check = EligibilityChecker.check_health_conditions(
            donor_data.get('health_conditions', {})
        )
        checks['health'] = health_check
        if not health_check['eligible']:
            ineligibility_reasons.extend(health_check['reasons'])
        
        # Calculate next eligible date if temporarily ineligible
        next_eligible_date = None
        if ineligibility_reasons:
            next_eligible_date = EligibilityChecker.calculate_next_eligible_date(
                ineligibility_reasons,
                donor_data.get('last_donation_date'),
                donor_data.get('gender')
            )
        
        return {
            'is_eligible': len(ineligibility_reasons) == 0,
            'ineligibility_reasons': ineligibility_reasons,
            'next_eligible_date': next_eligible_date,
            'checks': checks
        }
