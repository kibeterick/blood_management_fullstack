# Implementation Plan: Blood Management Enhancements

## Overview

This implementation plan covers three priority features for the Blood Management System:
1. Blood Bank Inventory Management - Real-time tracking with expiration management
2. SMS/Email Notifications - Multi-channel notification system
3. Donor Eligibility Checker - Pre-screening questionnaire

The implementation follows an incremental approach, building each feature with proper integration points and testing. All features integrate with the existing Django application deployed on PythonAnywhere.

## Tasks

- [x] 1. Set up database models and migrations
  - [x] 1.1 Create BloodUnit model for individual blood unit tracking
    - Add model with fields: blood_type, donation, donation_date, expiration_date, status, unit_number, volume_ml, storage_location, notes
    - Add methods: is_expiring_soon(), is_expired()
    - Add indexes for blood_type/status and expiration_date
    - _Requirements: 1.1, 2.1, 2.2_
  
  - [x] 1.2 Enhance BloodInventory model with threshold fields
    - Add fields: critical_threshold, optimal_level, alert_sent_at
    - Add method: get_status() to return critical/low/adequate/optimal
    - _Requirements: 3.1, 3.5, 4.2_
  
  - [x] 1.3 Create NotificationPreference model for user preferences
    - Add model with fields: user, email_enabled, sms_enabled
    - Add per-notification-type preferences (urgent_blood_email, appointment_reminder_sms, etc.)
    - Add method: get_enabled_channels(notification_type)
    - _Requirements: 11.1, 11.2, 11.3_
  
  - [x] 1.4 Create NotificationLog model for tracking sent notifications
    - Add model with fields: user, notification_type, channel, recipient, subject, message, status, error_message, sent_at, external_id
    - Add indexes for user/notification_type and status/created_at
    - _Requirements: 6.4, 10.3_
  
  - [x] 1.5 Create DonorEligibility model for eligibility tracking
    - Add model with fields: donor, age, weight, last_donation_date, health_conditions, is_eligible, ineligibility_reasons, next_eligible_date, assessment_date
    - Add method: calculate_eligibility() to validate all criteria
    - _Requirements: 13.5, 20.1, 20.2_
  
  - [x] 1.6 Add reminder_sent field to DonationAppointment model
    - Add boolean field to track if reminder was sent
    - _Requirements: 7.4_
  
  - [x] 1.7 Create and run database migrations
    - Generate migrations for all new models and model changes
    - Test migrations on development database
    - _Requirements: 21.8_

- [x] 2. Checkpoint - Verify database setup
  - Ensure all migrations run successfully, ask the user if questions arise.

- [x] 3. Implement inventory management backend
  - [x] 3.1 Create InventoryManager utility class
    - Implement update_inventory_from_donation() to create BloodUnit and update counts
    - Implement mark_expired_units() to mark expired units and update inventory
    - Implement use_blood_unit() to mark units as used and decrement inventory
    - _Requirements: 1.2, 1.3, 2.4_
  
  - [x] 3.2 Create inventory dashboard view
    - Implement inventory_dashboard() view with admin-only access
    - Query all inventory, expiring units, and expired units
    - Prepare chart data for visualization
    - _Requirements: 1.4, 4.1, 4.3, 5.1_
  
  - [x] 3.3 Create add blood unit view and form
    - Implement BloodUnitForm with auto-calculated expiration date
    - Implement add_blood_unit() view to add units and update inventory
    - _Requirements: 1.1, 2.1_
  
  - [x] 3.4 Create expiration management view
    - Implement expiration_list() view to show units by expiration status
    - Categorize units as expired, expiring soon, or good
    - _Requirements: 2.2, 2.3, 2.5_
  
  - [x] 3.5 Create inventory threshold configuration view
    - Implement InventoryThresholdForm for setting thresholds
    - Implement configure_thresholds() view for admin configuration
    - _Requirements: 3.5_
  
  - [x] 3.6 Create inventory API endpoint for real-time updates
    - Implement inventory_api() view returning JSON data
    - Include blood_type, units_available, status, threshold, last_updated
    - _Requirements: 1.5_
  
  - [x] 3.7 Integrate inventory updates with donation approval
    - Modify donation approval logic to call InventoryManager.update_inventory_from_donation()
    - _Requirements: 1.2_

- [x] 4. Implement inventory management frontend
  - [x] 4.1 Create inventory dashboard template
    - Build responsive layout with Bootstrap 5 following red theme
    - Display inventory table with color-coded status indicators
    - Show expiring soon and expired units sections
    - Add Chart.js bar chart for visual inventory display
    - _Requirements: 4.1, 4.2, 4.3, 4.5_
  
  - [x] 4.2 Create add blood unit template
    - Build form with date pickers and auto-calculation
    - Add validation and error display
    - _Requirements: 2.1_
  
  - [x] 4.3 Create expiration list template
    - Display units in three categories with color coding
    - Show unit details and action buttons
    - _Requirements: 2.2, 2.3, 2.5_
  
  - [x] 4.4 Add Chart.js visualization script
    - Implement bar chart with color coding (green/yellow/red)
    - Add real-time update functionality using inventory API
    - _Requirements: 4.1, 4.2, 4.4_
  
  - [x] 4.5 Add inventory navigation links to admin dashboard
    - Add links to inventory dashboard, add unit, expiration list
    - _Requirements: 5.1_

- [x] 5. Checkpoint - Test inventory management
  - Ensure all inventory features work correctly, ask the user if questions arise.

- [x] 6. Implement email notification service
  - [x] 6.1 Create EmailNotificationService class
    - Implement send_urgent_blood_notification() for urgent blood needs
    - Implement send_appointment_confirmation() with ICS calendar attachment
    - Implement send_request_status_notification() for request updates
    - Implement send_low_stock_alert() for admin alerts
    - All methods should check user preferences and log results
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 8.1, 8.2, 9.1, 9.2, 10.1, 10.2_
  
  - [x] 6.2 Create email templates for notifications
    - Create urgent_blood_email.html and .txt templates
    - Create appointment_confirmation.html and .txt templates
    - Create request_status_email.html and .txt templates
    - Create low_stock_alert.html and .txt templates
    - Follow existing red theme and mobile-responsive design
    - _Requirements: 6.2, 8.2, 9.3_
  
  - [x] 6.3 Implement ICS calendar file generation
    - Create generate_ics_file() utility function
    - Generate proper ICS format with appointment details
    - _Requirements: 8.4_
  
  - [x] 6.4 Integrate email notifications with existing workflows
    - Add notification call to blood request approval/rejection
    - Add notification call to appointment booking
    - Add notification call to low stock detection
    - _Requirements: 6.1, 8.3, 9.1, 9.2, 10.3_

- [x] 7. Implement SMS notification service
  - [x] 7.1 Create SMSNotificationService class
    - Implement send_sms_twilio() for Twilio integration
    - Implement send_sms_africas_talking() for Africa's Talking integration
    - Implement send_sms() with provider selection and preference checking
    - Implement send_appointment_reminder() for appointment reminders
    - All methods should log results to NotificationLog
    - _Requirements: 7.1, 7.2, 12.1, 12.2_
  
  - [x] 7.2 Add SMS configuration to Django settings
    - Add SMS_PROVIDER setting (twilio or africas_talking)
    - Add provider-specific credentials (TWILIO_ACCOUNT_SID, AFRICAS_TALKING_API_KEY, etc.)
    - Add configuration validation on startup
    - _Requirements: 12.3, 12.4, 12.5_
  
  - [x] 7.3 Integrate SMS notifications with appointment system
    - Add SMS notification call to appointment booking
    - _Requirements: 7.1, 7.5_

- [x] 8. Implement scheduled notification tasks
  - [x] 8.1 Set up Celery configuration
    - Create celery.py with app configuration
    - Configure beat schedule for appointment reminders (daily at 9 AM)
    - Configure beat schedule for marking expired units (daily at midnight)
    - Update Django settings with Celery configuration
    - _Requirements: 7.1, 2.4_
  
  - [x] 8.2 Create send_appointment_reminders Celery task
    - Query appointments 24 hours away
    - Send email and SMS reminders
    - Mark reminder_sent flag
    - _Requirements: 7.1, 7.2, 7.3, 7.4_
  
  - [x] 8.3 Create mark_expired_units Celery task
    - Call InventoryManager.mark_expired_units()
    - _Requirements: 2.4_
  
  - [x] 8.4 Create send_low_stock_alert Celery task
    - Check inventory thresholds
    - Send alerts to admins if below threshold
    - Respect 24-hour notification limit
    - _Requirements: 3.1, 3.2, 3.3, 10.4_

- [x] 9. Implement notification preferences interface
  - [x] 9.1 Create NotificationPreferenceForm
    - Add form fields for all notification type preferences
    - Group by email and SMS channels
    - _Requirements: 11.1, 11.2, 11.3_
  
  - [x] 9.2 Create notification preferences view
    - Implement notification_preferences() view
    - Create or update NotificationPreference on form submission
    - _Requirements: 11.4, 11.5_
  
  - [x] 9.3 Create notification preferences template
    - Build responsive form with clear channel/type organization
    - Add explanations for each notification type
    - Follow red theme design
    - _Requirements: 11.5_
  
  - [x] 9.4 Add notification preferences link to user dashboard
    - Add navigation link to preferences page
    - _Requirements: 11.5_

- [x] 10. Checkpoint - Test notification system
  - Ensure all notification features work correctly, ask the user if questions arise.

- [x] 11. Implement donor eligibility checker backend
  - [ ] 11.1 Create EligibilityChecker utility class
    - Implement check_age_eligibility() for 18-65 age range
    - Implement check_weight_eligibility() for minimum 50kg
    - Implement check_donation_interval() for 56/84 day intervals
    - Implement check_health_conditions() for disqualifying conditions
    - Implement calculate_next_eligible_date() for temporary ineligibility
    - Implement calculate_eligibility() to run all checks and return result
    - _Requirements: 13.3, 14.1, 14.2, 15.1, 15.2, 16.1, 17.1, 17.2, 17.3, 17.4, 17.5_
  
  - [ ] 11.2 Create DonorEligibilityForm
    - Add fields: age, weight, last_donation_date, recent_illness, current_medication, anemia, blood_pressure_issues
    - Add validation for required fields and value ranges
    - _Requirements: 13.2_
  
  - [ ] 11.3 Create eligibility check view
    - Implement check_eligibility() view to process questionnaire
    - Calculate eligibility using EligibilityChecker
    - Save results to DonorEligibility model
    - Return eligibility result with specific reasons
    - _Requirements: 13.3, 13.4, 13.5, 20.1_
  
  - [ ] 11.4 Integrate eligibility check with appointment booking
    - Modify appointment booking flow to require eligibility check first
    - Disable booking button if donor is ineligible
    - _Requirements: 19.1, 19.2, 19.3, 19.4_
  
  - [ ] 11.5 Create eligibility history view
    - Implement eligibility_history() view to show past assessments
    - Display assessment dates and results
    - _Requirements: 20.3, 20.4_

- [ ] 12. Implement donor eligibility checker frontend
  - [ ] 12.1 Create eligibility questionnaire template
    - Build multi-step form with clear questions
    - Add input validation and help text
    - Follow red theme and mobile-responsive design
    - _Requirements: 13.1, 13.2_
  
  - [ ] 12.2 Create eligibility results template
    - Display clear eligible/ineligible status with color coding
    - Show specific ineligibility reasons if applicable
    - Display next eligible date for temporary ineligibility
    - Add educational information about eligibility criteria
    - _Requirements: 18.1, 18.2, 18.3, 18.4, 18.5_
  
  - [ ] 12.3 Create eligibility history template
    - Display past assessments in chronological order
    - Show assessment dates and results
    - _Requirements: 20.4_
  
  - [ ] 12.4 Modify appointment booking template
    - Add eligibility check requirement before booking
    - Disable booking button with explanation if ineligible
    - Show next eligible date if temporarily ineligible
    - _Requirements: 19.1, 19.2, 19.3_
  
  - [ ] 12.5 Add eligibility check link to donor dashboard
    - Add prominent link to eligibility checker
    - _Requirements: 13.1_

- [ ] 13. Checkpoint - Test eligibility checker
  - Ensure all eligibility features work correctly, ask the user if questions arise.

- [ ] 14. Add URL patterns for all new views
  - [ ] 14.1 Add inventory management URLs
    - Add paths for inventory_dashboard, add_blood_unit, expiration_list, configure_thresholds, inventory_api
    - _Requirements: 5.1_
  
  - [ ] 14.2 Add notification URLs
    - Add paths for notification_preferences, notification_logs (admin)
    - _Requirements: 11.5_
  
  - [ ] 14.3 Add eligibility checker URLs
    - Add paths for check_eligibility, eligibility_results, eligibility_history
    - _Requirements: 13.1, 19.4_

- [ ] 15. Create admin interface for new models
  - [ ] 15.1 Register BloodUnit in Django admin
    - Add list display, filters, and search fields
    - Add actions for marking units as used/expired
    - _Requirements: 5.1, 5.4_
  
  - [ ] 15.2 Register NotificationLog in Django admin
    - Add list display with filters for status and notification type
    - Add read-only fields
    - _Requirements: 6.4_
  
  - [ ] 15.3 Register NotificationPreference in Django admin
    - Add inline editing for user preferences
    - _Requirements: 11.5_
  
  - [ ] 15.4 Register DonorEligibility in Django admin
    - Add list display with filters for eligibility status
    - Add search by donor name
    - _Requirements: 20.5_

- [ ] 16. Add access control and permissions
  - [ ] 16.1 Add admin-only decorators to inventory views
    - Apply @user_passes_test(lambda u: u.role == 'admin') to all inventory management views
    - _Requirements: 5.1, 5.2_
  
  - [ ] 16.2 Add authentication to all new views
    - Apply @login_required to all views
    - _Requirements: 5.3_
  
  - [ ] 16.3 Add audit logging for inventory modifications
    - Log all inventory changes with user and timestamp
    - _Requirements: 5.4_

- [ ] 17. Create deployment configuration
  - [ ] 17.1 Update requirements.txt
    - Add celery, redis, twilio, africastalking, icalendar packages
    - Pin versions for stability
    - _Requirements: 22.1, 22.3_
  
  - [ ] 17.2 Create PythonAnywhere deployment guide
    - Document database migration steps
    - Document Celery setup (if supported) or alternative scheduling
    - Document SMS provider configuration
    - Document email backend configuration
    - _Requirements: 22.1, 22.2, 22.3, 22.4, 22.5_
  
  - [ ] 17.3 Create environment variables template
    - Add template for SMS credentials
    - Add template for email configuration
    - Add template for Celery/Redis configuration
    - _Requirements: 12.3_

- [ ] 18. Integration testing and final wiring
  - [ ] 18.1 Test complete inventory workflow
    - Test adding blood units from donations
    - Test expiration tracking and alerts
    - Test low stock alerts
    - Test inventory visualization
    - _Requirements: 1.1, 1.2, 1.3, 2.1, 2.2, 2.3, 3.1, 3.2, 4.1_
  
  - [ ] 18.2 Test complete notification workflow
    - Test email notifications for all types
    - Test SMS notifications (if configured)
    - Test notification preferences
    - Test notification logging
    - Test scheduled reminders
    - _Requirements: 6.1, 7.1, 8.1, 9.1, 10.1, 11.1_
  
  - [ ] 18.3 Test complete eligibility workflow
    - Test eligibility questionnaire
    - Test all eligibility criteria validation
    - Test appointment booking integration
    - Test eligibility history
    - _Requirements: 13.1, 14.1, 15.1, 16.1, 17.1, 18.1, 19.1, 20.1_
  
  - [ ] 18.4 Test cross-feature integration
    - Test donation approval triggering inventory update and notifications
    - Test appointment booking with eligibility check and confirmation notifications
    - Test low stock triggering notifications to eligible donors
    - _Requirements: 21.1, 21.2, 21.3, 21.4_
  
  - [ ] 18.5 Test mobile responsiveness
    - Test all new templates on mobile devices
    - Verify red theme consistency
    - _Requirements: 21.6, 21.7_

- [ ] 19. Final checkpoint - Complete system verification
  - Ensure all tests pass and all features are integrated, ask the user if questions arise.

## Notes

- All tasks reference specific requirements from the requirements document for traceability
- The implementation follows an incremental approach: models → backend → frontend → integration
- Checkpoints ensure validation at key milestones
- The design uses Python/Django as specified in the existing system
- All features integrate with existing models: CustomUser, Donor, BloodRequest, BloodDonation, BloodInventory, DonationAppointment
- SMS functionality is optional and can be configured based on available provider
- Celery/Redis may need alternative scheduling on PythonAnywhere (cron jobs or scheduled tasks)
- All templates follow Bootstrap 5 with the existing red/blood theme
- Mobile responsiveness is required for all new interfaces
