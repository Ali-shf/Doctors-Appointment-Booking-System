# Doctor Timesheet System - Usage Guide

## Overview
This system has been updated to handle doctor timesheets in a more structured way, separating available and booked time slots for better user experience.

## Key Features

### 1. Non-JSON Timesheet Data
- Timesheets are now processed in the view to separate available and booked slots
- Each timesheet has its own time slots displayed separately
- Better organization for multiple timesheets

### 2. Template Improvements
- Each timesheet is displayed in its own card
- Available time slots are clearly separated from booked ones
- Visual feedback with hover effects and animations
- Responsive design for different screen sizes

### 3. API Endpoint
- New API endpoint: `/reservation/api/clinic/<clinic_id>/doctor/<doctor_id>/timesheets/`
- Returns structured JSON data for timesheets
- Useful for AJAX requests or mobile apps

## Usage Examples

### Getting Timesheets in Template
```python
# In your view
timesheets = TimeSheet.objects.filter(doctor=doctor, clinic=clinic)
processed_timesheets = [ts.get_timesheet_data() for ts in timesheets]
```

### API Usage
```javascript
// Fetch timesheets via AJAX
fetch('/reservation/api/clinic/1/doctor/2/timesheets/')
  .then(response => response.json())
  .then(data => {
    console.log(data.timesheets);
    // Each timesheet has: available_slots, booked_slots, total_slots
  });
```

### Template Structure
```html
{% for ts in timesheets %}
  <div class="timesheet-card">
    <h3>{{ ts.clinic.name }} - {{ ts.end|date:"Y/m/d" }}</h3>
    
    <!-- Available slots -->
    {% for slot in ts.available_slots %}
      <button class="time-slot-btn">{{ slot }}</button>
    {% endfor %}
    
    <!-- Booked slots -->
    {% for slot in ts.booked_slots %}
      <button disabled>{{ slot }} (Booked)</button>
    {% endfor %}
  </div>
{% endfor %}
```

## Model Methods

### TimeSheet Model
- `available_slots`: Property that returns available time slots
- `booked_slots`: Property that returns booked time slots  
- `get_timesheet_data()`: Method that returns structured data for templates

## CSS Classes
- `.timesheet-form`: Styling for timesheet forms
- `.time-slot-btn`: Styling for time slot buttons
- `.available-slots`: Container for available time slots
- `.booked-slots`: Container for booked time slots
- `.timesheet-date`: Styling for date badges

## JavaScript Features
- Click animations on time slot buttons
- Hover effects on cards
- Loading states during form submission
- Prevention of double submissions

## Benefits
1. **Better UX**: Clear separation of available vs booked slots
2. **Multiple Timesheets**: Each timesheet is handled independently
3. **Visual Feedback**: Animations and hover effects
4. **API Support**: JSON endpoint for dynamic loading
5. **Responsive**: Works on all screen sizes
6. **Accessibility**: Proper button states and feedback
