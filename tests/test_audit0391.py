"""Date/export audit regressions; all records are synthetic."""
import datetime as dt
import unittest
from logic import date_hints, export_ics, new_event, search, validate


class DateAndExportAuditTests(unittest.TestCase):
    def event(self, **changes):
        result = new_event(dt.date(2026, 10, 28))
        result.update(title='Synthetic boundary event', **changes)
        validate([result])
        return result

    def test_unsupported_dmy_year_has_no_hint_and_does_not_break_search(self):
        today = dt.date(2026, 10, 29)
        for query in ['1.1.0001', '31.12.0999']:
            self.assertEqual(date_hints(query, today), [])
            self.assertEqual(search([self.event()], query, today), [])

    def test_date_hints_keep_supported_lower_boundary(self):
        result = date_hints('1.1.1000', dt.date(2026, 10, 29))
        self.assertEqual(result[0]['date'], '1000-01-01')

    def test_relative_hints_never_cross_upper_boundary(self):
        last = dt.date(9999, 12, 31)
        for query in ['tomorrow', 'day after tomorrow', 'Monday', 'January']:
            self.assertEqual(date_hints(query, last), [])
        self.assertEqual(date_hints('today', last)[0]['date'], '9999-12-31')

    def test_ics_out_of_range_end_is_an_explained_error(self):
        for changes in [dict(time='23:30', minutes=120), dict(allDay=True),
                        dict(repeat='weekly', weekdays=[0])]:
            with self.subTest(changes=changes):
                event = self.event(date='9999-12-31', **changes)
                with self.assertRaisesRegex(ValueError, '1000–9999') as caught:
                    export_ics([self.event(), event])
                self.assertIn(event['title'], str(caught.exception))

    def test_ics_valid_last_day_end_is_not_rejected(self):
        event = self.event(date='9999-12-31', time='22:00', minutes=60)
        self.assertIn('DTEND:99991231T230000', export_ics([event]))

    def test_ics_all_day_end_before_boundary(self):
        event = self.event(date='9999-12-30', allDay=True)
        self.assertIn('DTEND;VALUE=DATE:99991231', export_ics([event]))

    def test_ics_valid_last_weekly_occurrence_is_not_rejected(self):
        event = self.event(date='9999-12-31', repeat='weekly', weekdays=[4])
        self.assertIn('DTSTART:99991231T090000', export_ics([event]))

    def test_ics_uses_floating_wall_clock_through_dst(self):
        for date, start, expected in [('2026-10-25', '01:30', '03:30'),
                                      ('2026-03-29', '01:30', '03:30')]:
            event = self.event(date=date, time=start, minutes=120)
            self.assertIn('DTEND:'+date.replace('-', '')+'T'+expected.replace(':', '')+'00', export_ics([event]))
