from odoo import api, fields, models
from odoo.tools.translate import _

class EventMailScheduler(models.Model):
    _inherit = 'event.mail'

    ticket_ids = fields.Many2many('event.event.ticket','event_mail_ticket_rel','mid','tid',"Ticket Type")

    def execute(self):
        for mail in self:
            now = fields.Datetime.now()
            if mail.interval_type == 'after_sub':
                # update registration lines
                lines = [
                    (0, 0, {'registration_id': registration.id})
                    for registration in (mail.event_id.registration_ids - mail.mapped('mail_registration_ids.registration_id')).filtered(lambda r :r.event_ticket_id.id in mail.ticket_ids.ids)
                ]
                if lines:
                    mail.write({'mail_registration_ids': lines})
                # execute scheduler on registrations
                mail.mail_registration_ids.filtered(lambda r : r.registration_id.event_ticket_id.id in mail.ticket_ids.ids).execute()
            else:
                # Do not send emails if the mailing was scheduled before the event but the event is over
                if not mail.mail_sent and mail.scheduled_date <= now and mail.notification_type == 'mail' and \
                        (mail.interval_type != 'before_event' or mail.event_id.date_end > now):
                    mail.event_id.mail_attendees(mail.template_id.id)
                    mail.write({'mail_sent': True})
        return True



class EventEvent(models.Model):
    _inherit = 'event.event'

    def mail_attendees(self, template_id, force_send=False, filter_func=lambda self: self.state != 'cancel'):
        for event in self:
            for mail in event.event_mail_ids:
                if not mail.interval_type == 'after_sub':
                    registration_ids = event.registration_ids.filtered(lambda r : r.event_ticket_id.id in mail.ticket_ids.ids)
                    for attendee in registration_ids.filtered(filter_func):
                        em = mail.template_id.send_mail(attendee.id, force_send=force_send)
