# Requirements Document

## Introduction

This document specifies requirements for three priority enhancements to the Blood Management System: Blood Bank Inventory Management, SMS/Email Notifications, and Donor Eligibility Checker. These features will improve operational efficiency, donor engagement, and safety compliance within the existing Django-based system deployed on PythonAnywhere.

## Glossary

- **Blood_Inventory_System**: The subsystem managing real-time stock levels for all blood types
- **Notification_Service**: The subsystem handling email and SMS communications to users
- **Eligibility_Checker**: The subsystem that validates donor eligibility based on health and timing criteria
- **Admin_User**: A user with administrative privileges to manage inventory and system settings
- **Donor_User**: A registered user who can donate blood
- **Blood_Unit**: A single bag or unit of donated blood (typically 450-500ml)
- **Blood_Type**: One of eight blood classifications: A+, A-, B+, B-, AB+, AB-, O+, O-
- **Stock_Threshold**: The minimum quantity of blood units that triggers a low stock alert
- **Donation_Interval**: The required waiting period between donations (56 days for men, 84 days for women)
- **Appointment**: A scheduled time slot for blood donation
- **Dashboard**: The main interface displaying system information and controls

## Requirements

### Requirement 1: Blood Type Inventory Tracking

**User Story:** As an Admin_User, I want to track real-time stock levels for each Blood_Type, so that I can maintain adequate blood supplies and respond to shortages.

#### Acceptance Criteria

1. THE Blood_Inventory_System SHALL store the quantity in Blood_Units for each of the eight Blood_Types
2. WHEN a donation is received, THE Blood_Inventory_System SHALL increment the stock quantity for the corresponding Blood_Type
3. WHEN blood is requested or used, THE Blood_Inventory_System SHALL decrement the stock quantity for the corresponding Blood_Type
4. THE Blood_Inventory_System SHALL display current stock levels for all Blood_Types on the Admin Dashboard
5. WHERE the Admin_User requests inventory data, THE Blood_Inventory_System SHALL provide real-time stock information without requiring page refresh

### Requirement 2: Expiration Date Management

**User Story:** As an Admin_User, I want to track expiration dates for blood units, so that I can prevent the use of expired blood and minimize waste.

#### Acceptance Criteria

1. WHEN a Blood_Unit is added to inventory, THE Blood_Inventory_System SHALL record the expiration date
2. THE Blood_Inventory_System SHALL display expiration dates for all Blood_Units in the inventory
3. WHEN the current date is within 7 days of a Blood_Unit expiration date, THE Blood_Inventory_System SHALL flag the unit as expiring soon
4. WHEN a Blood_Unit expiration date has passed, THE Blood_Inventory_System SHALL mark the unit as expired
5. THE Blood_Inventory_System SHALL sort Blood_Units by expiration date with earliest expiration first

### Requirement 3: Low Stock Alerting

**User Story:** As an Admin_User, I want to receive alerts when blood inventory falls below threshold levels, so that I can take action to replenish supplies before critical shortages occur.

#### Acceptance Criteria

1. WHERE a Blood_Type is configured with a Stock_Threshold, THE Blood_Inventory_System SHALL monitor the quantity against that threshold
2. WHEN a Blood_Type quantity falls below its Stock_Threshold, THE Blood_Inventory_System SHALL generate a low stock alert
3. WHEN a low stock alert is generated, THE Notification_Service SHALL send an email notification to all Admin_Users
4. THE Blood_Inventory_System SHALL display visual indicators on the Dashboard for Blood_Types below Stock_Threshold
5. THE Blood_Inventory_System SHALL allow Admin_Users to configure Stock_Threshold values for each Blood_Type

### Requirement 4: Inventory Visualization

**User Story:** As an Admin_User, I want to view visual charts of blood stock levels, so that I can quickly assess inventory status at a glance.

#### Acceptance Criteria

1. THE Blood_Inventory_System SHALL display a bar chart showing current quantities for all Blood_Types
2. THE Blood_Inventory_System SHALL use color coding to indicate stock status (green for adequate, yellow for low, red for critical)
3. THE Blood_Inventory_System SHALL display the chart on the Admin Dashboard
4. WHEN stock levels change, THE Blood_Inventory_System SHALL update the chart visualization within 5 seconds
5. THE Blood_Inventory_System SHALL follow the existing red/blood theme design patterns

### Requirement 5: Inventory Access Control

**User Story:** As a system administrator, I want inventory management restricted to Admin_Users only, so that unauthorized users cannot modify stock levels.

#### Acceptance Criteria

1. THE Blood_Inventory_System SHALL restrict inventory modification functions to Admin_Users only
2. WHEN a non-Admin_User attempts to access inventory management functions, THE Blood_Inventory_System SHALL deny access and display an authorization error
3. THE Blood_Inventory_System SHALL allow all authenticated users to view current stock levels
4. THE Blood_Inventory_System SHALL log all inventory modifications with user identification and timestamp

### Requirement 6: Email Notification for Urgent Blood Needs

**User Story:** As an Admin_User, I want to send email notifications to donors when their Blood_Type is urgently needed, so that I can quickly recruit donors during shortages.

#### Acceptance Criteria

1. WHEN an Admin_User initiates an urgent blood request for a specific Blood_Type, THE Notification_Service SHALL send email notifications to all Donor_Users with matching Blood_Type
2. THE Notification_Service SHALL include the Blood_Type, urgency level, and contact information in the email
3. THE Notification_Service SHALL use the configured Django email backend for delivery
4. THE Notification_Service SHALL log all sent notifications with timestamp and recipient count
5. WHEN email delivery fails, THE Notification_Service SHALL log the failure and continue processing remaining recipients

### Requirement 7: Appointment Reminder Notifications

**User Story:** As a Donor_User, I want to receive reminders before my scheduled appointment, so that I don't forget my donation commitment.

#### Acceptance Criteria

1. WHEN an Appointment is 24 hours away, THE Notification_Service SHALL send an SMS reminder to the Donor_User
2. WHEN an Appointment is 24 hours away, THE Notification_Service SHALL send an email reminder to the Donor_User
3. THE Notification_Service SHALL include the appointment date, time, and location in the reminder
4. THE Notification_Service SHALL send reminders only once per Appointment
5. WHERE SMS integration is configured, THE Notification_Service SHALL use the configured SMS provider (Twilio or Africa's Talking)

### Requirement 8: Appointment Confirmation Notifications

**User Story:** As a Donor_User, I want to receive confirmation when I book an appointment, so that I have a record of my scheduled donation.

#### Acceptance Criteria

1. WHEN a Donor_User successfully books an Appointment, THE Notification_Service SHALL send an email confirmation
2. THE Notification_Service SHALL include appointment details, location, and preparation instructions in the confirmation
3. THE Notification_Service SHALL send the confirmation within 60 seconds of booking
4. THE Notification_Service SHALL include a calendar attachment (ICS format) with the confirmation email

### Requirement 9: Blood Request Status Notifications

**User Story:** As a user who submitted a blood request, I want to be notified when my request is approved or rejected, so that I know the status of my request.

#### Acceptance Criteria

1. WHEN a blood request is approved by an Admin_User, THE Notification_Service SHALL send an email notification to the requester
2. WHEN a blood request is rejected by an Admin_User, THE Notification_Service SHALL send an email notification to the requester with rejection reason
3. THE Notification_Service SHALL include request details and next steps in the notification
4. THE Notification_Service SHALL send status notifications within 60 seconds of status change

### Requirement 10: Admin Low Stock Notifications

**User Story:** As an Admin_User, I want to receive notifications when blood stock is low, so that I can take immediate action to address shortages.

#### Acceptance Criteria

1. WHEN a Blood_Type falls below its Stock_Threshold, THE Notification_Service SHALL send an email to all Admin_Users
2. THE Notification_Service SHALL include the Blood_Type, current quantity, and threshold level in the notification
3. THE Notification_Service SHALL send low stock notifications within 5 minutes of threshold breach
4. THE Notification_Service SHALL send at most one notification per Blood_Type per 24-hour period to avoid notification fatigue

### Requirement 11: User Notification Preferences

**User Story:** As a Donor_User, I want to configure my notification preferences, so that I can control which notifications I receive and through which channels.

#### Acceptance Criteria

1. THE Notification_Service SHALL allow users to enable or disable email notifications
2. WHERE SMS integration is available, THE Notification_Service SHALL allow users to enable or disable SMS notifications
3. THE Notification_Service SHALL allow users to specify notification preferences for each notification type (urgent needs, reminders, confirmations)
4. THE Notification_Service SHALL respect user preferences when sending notifications
5. THE Notification_Service SHALL provide a preferences interface accessible from the user Dashboard

### Requirement 12: SMS Integration Configuration

**User Story:** As a system administrator, I want to configure SMS integration with supported providers, so that the system can send SMS notifications to users.

#### Acceptance Criteria

1. WHERE Twilio is selected as the SMS provider, THE Notification_Service SHALL use Twilio API for SMS delivery
2. WHERE Africa's Talking is selected as the SMS provider, THE Notification_Service SHALL use Africa's Talking API for SMS delivery
3. THE Notification_Service SHALL allow configuration of SMS provider credentials through Django settings
4. WHEN SMS integration is not configured, THE Notification_Service SHALL send email notifications only
5. THE Notification_Service SHALL validate SMS provider configuration on system startup

### Requirement 13: Donor Eligibility Pre-Screening

**User Story:** As a Donor_User, I want to complete a pre-screening questionnaire before booking an appointment, so that I know if I'm eligible to donate.

#### Acceptance Criteria

1. WHEN a Donor_User initiates appointment booking, THE Eligibility_Checker SHALL present a pre-screening questionnaire
2. THE Eligibility_Checker SHALL collect responses for age, weight, recent donation date, and health conditions
3. THE Eligibility_Checker SHALL calculate eligibility based on collected responses
4. THE Eligibility_Checker SHALL display eligibility results to the Donor_User before allowing appointment booking
5. THE Eligibility_Checker SHALL save questionnaire responses to the Donor_User profile

### Requirement 14: Donation Interval Validation

**User Story:** As a Donor_User, I want the system to check if I've donated recently, so that I don't donate too frequently and risk my health.

#### Acceptance Criteria

1. WHEN a male Donor_User last donated within 56 days, THE Eligibility_Checker SHALL mark the donor as ineligible
2. WHEN a female Donor_User last donated within 84 days, THE Eligibility_Checker SHALL mark the donor as ineligible
3. THE Eligibility_Checker SHALL calculate the Donation_Interval from the most recent donation date
4. WHEN a Donor_User is ineligible due to Donation_Interval, THE Eligibility_Checker SHALL display the next eligible donation date
5. THE Eligibility_Checker SHALL retrieve donation history from the existing donor management system

### Requirement 15: Age Eligibility Validation

**User Story:** As a system administrator, I want to enforce age requirements for blood donation, so that only age-appropriate donors can book appointments.

#### Acceptance Criteria

1. WHEN a Donor_User age is less than 18 years, THE Eligibility_Checker SHALL mark the donor as ineligible
2. WHEN a Donor_User age is greater than 65 years, THE Eligibility_Checker SHALL mark the donor as ineligible
3. THE Eligibility_Checker SHALL calculate age from the Donor_User date of birth
4. WHEN a Donor_User is ineligible due to age, THE Eligibility_Checker SHALL display an age requirement message

### Requirement 16: Weight Eligibility Validation

**User Story:** As a healthcare administrator, I want to enforce minimum weight requirements, so that donors meet safety standards for blood donation.

#### Acceptance Criteria

1. WHEN a Donor_User weight is less than 50 kilograms, THE Eligibility_Checker SHALL mark the donor as ineligible
2. THE Eligibility_Checker SHALL accept weight input in kilograms
3. WHEN a Donor_User is ineligible due to weight, THE Eligibility_Checker SHALL display the minimum weight requirement

### Requirement 17: Health Conditions Screening

**User Story:** As a Donor_User, I want to be screened for health conditions that affect donation eligibility, so that I can donate safely.

#### Acceptance Criteria

1. THE Eligibility_Checker SHALL screen for anemia indicators
2. THE Eligibility_Checker SHALL screen for blood pressure concerns
3. THE Eligibility_Checker SHALL screen for recent illness within 14 days
4. THE Eligibility_Checker SHALL screen for current medication use
5. WHEN any disqualifying health condition is reported, THE Eligibility_Checker SHALL mark the donor as ineligible
6. THE Eligibility_Checker SHALL provide specific feedback about which health condition caused ineligibility

### Requirement 18: Eligibility Result Display

**User Story:** As a Donor_User, I want to see clear eligibility results, so that I understand whether I can donate and why.

#### Acceptance Criteria

1. WHEN a Donor_User is eligible, THE Eligibility_Checker SHALL display a clear eligibility confirmation message
2. WHEN a Donor_User is ineligible, THE Eligibility_Checker SHALL display specific reasons for ineligibility
3. THE Eligibility_Checker SHALL use color coding (green for eligible, red for ineligible) consistent with the system theme
4. WHEN a Donor_User is temporarily ineligible, THE Eligibility_Checker SHALL display the date when eligibility will be restored
5. THE Eligibility_Checker SHALL provide educational information about eligibility criteria

### Requirement 19: Appointment Booking Prevention

**User Story:** As a system administrator, I want to prevent ineligible donors from booking appointments, so that we maintain donation safety standards.

#### Acceptance Criteria

1. WHEN a Donor_User is marked as ineligible, THE Eligibility_Checker SHALL disable the appointment booking function
2. THE Eligibility_Checker SHALL display an explanation message when booking is disabled
3. WHEN a Donor_User becomes eligible, THE Eligibility_Checker SHALL enable the appointment booking function
4. THE Eligibility_Checker SHALL integrate with the existing appointment booking system

### Requirement 20: Eligibility Profile Storage

**User Story:** As a Donor_User, I want my eligibility information saved to my profile, so that I don't have to re-enter it for future donations.

#### Acceptance Criteria

1. WHEN eligibility screening is completed, THE Eligibility_Checker SHALL save all responses to the Donor_User profile
2. THE Eligibility_Checker SHALL timestamp eligibility assessments
3. THE Eligibility_Checker SHALL allow Donor_Users to update their eligibility information
4. THE Eligibility_Checker SHALL maintain a history of eligibility assessments
5. THE Eligibility_Checker SHALL integrate with the existing donor profile data model

### Requirement 21: System Integration and Compatibility

**User Story:** As a system administrator, I want all new features to integrate seamlessly with existing functionality, so that the system remains stable and consistent.

#### Acceptance Criteria

1. THE Blood_Inventory_System SHALL integrate with the existing donor management system
2. THE Blood_Inventory_System SHALL integrate with the existing appointment system
3. THE Notification_Service SHALL use existing user authentication and authorization mechanisms
4. THE Eligibility_Checker SHALL use existing donor profile data
5. ALL new features SHALL follow existing Django design patterns and code organization
6. ALL new features SHALL maintain the existing red/blood theme and Bootstrap 5 styling
7. ALL new features SHALL be mobile-friendly and responsive
8. ALL new database migrations SHALL be backward compatible with existing data

### Requirement 22: Deployment Compatibility

**User Story:** As a system administrator, I want all new features to be compatible with PythonAnywhere deployment, so that I can deploy updates without infrastructure changes.

#### Acceptance Criteria

1. ALL new features SHALL be compatible with PythonAnywhere hosting environment
2. THE Notification_Service SHALL use Django email backend compatible with PythonAnywhere
3. WHERE SMS integration is used, THE Notification_Service SHALL use HTTPS APIs compatible with PythonAnywhere
4. ALL new features SHALL respect PythonAnywhere resource limitations
5. ALL new features SHALL include deployment instructions specific to PythonAnywhere
