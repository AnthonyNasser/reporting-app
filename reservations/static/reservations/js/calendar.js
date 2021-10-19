$(document).ready(function() {
    $('#calendar').fullCalendar({
        aspectRatio: 2.2, // Default is 1.35
        header: {
            left: 'prev,next today',
            center: 'title',
            right: 'month,basicWeek,basicDay'
        },
        fixedWeekCount: false, // Makes the calendar have either 4, 5, or 6 weeks, depending on the month
        hiddenDays: [ 0 ], // Hide Sunday
        timezone: 'local',
        now: moment().format(), // ISO 8601 by default
        eventLimit: true, // limits the number of events to the height of the day cell
        events: {
            url: getMonthlyReservations(),
            textColor: '#fff'
        },
        timeFormat: 'h:mm a',
        displayEventEnd: true,
        eventDataTransform: function(eventData) {
            return {
                title: eventData.project,
                start: moment.utc(eventData.start_date).local(),
                end: moment.utc(eventData.end_date).local(),
                name: eventData.user__first_name + " " + eventData.user__last_name,
                url: getClickURL() + eventData.id + '/',
                color: eventData.user__department__color
            }
        },
        eventRender: function(event, element) {            
            element.find('.fc-time').remove();
            element.find('.fc-title').remove();
            var eventDisplay = '<strong class="text-uppercase">' + event.title + '</strong><span style="float: right;">' +
            					event.start.format("M/D h:mm a") + ' - ' + event.end.format("M/D h:mm a") + '</span><br />' + event.name;
            element.find('.fc-content').append(eventDisplay);
        },
        dayClick: function(date, jsEvent, view) {
            // Link to a blank reservation form with date pre-populated
            window.location.href = getClickURL() + date.format() + '/' //ISO 8601 by default
        },
        eventMouseover: function(event, jsEvent, view) {
            $(this).css('cursor', 'pointer');
        },
        loading: function(isLoading, view) {
            isLoading ? $('#loading').show() : $('#loading').hide();
        }
    });
});