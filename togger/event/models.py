import uuid

from sqlalchemy.ext.declarative import declared_attr

from togger import db
from togger.database import GUID, same_as


class EventBase(db.Model):
    __abstract__ = True

    title = db.Column(db.String(256), nullable=False)
    description = db.Column(db.Text, nullable=False)
    start = db.Column(db.DateTime, nullable=False)
    end = db.Column(db.DateTime, nullable=False)
    all_day = db.Column(db.Boolean, default=False, nullable=False)

    @declared_attr
    def calendar_id(self):
        return db.Column(GUID(), db.ForeignKey('calendar.id'), nullable=False)


class Event(EventBase):
    id = db.Column(GUID(), primary_key=True, default=uuid.uuid4)
    group_id = db.Column(GUID(), db.ForeignKey('recur_event.id'))
    recur_event = db.relationship('RecurEvent')
    shifts = db.relationship('Shift', backref='Event', cascade="all,delete", lazy=True)
    init_start = db.Column(db.DateTime, default=same_as('start'))

    @property
    def serialized(self):
        dict = {
            'title': self.title,
            'description': self.description,
            'start': self.start.isoformat() + 'Z',
            'end': self.end.isoformat() + 'Z',
            'color': self.get_color(),
            'allDay': self.all_day
        }
        if self.id:
            dict['id'] = self.id
        if self.group_id:
            dict['groupId'] = self.group_id
        return dict

    def get_color(self):
        if len(self.shifts) > 1:
            return "#88B04B"
        elif len(self.shifts) > 0:
            return "#E08119"
        else:
            return "#9F9C99"


class RecurEvent(EventBase):
    id = db.Column(GUID(), primary_key=True, default=uuid.uuid4)
    start_recur = db.Column(db.DateTime, nullable=False)
    end_recur = db.Column(db.DateTime)
    rrule = db.Column(db.String(256), nullable=False)


class Shift(db.Model):
    id = db.Column(GUID(), primary_key=True, default=uuid.uuid4)
    person = db.Column(db.String(80), nullable=False)
    event_id = db.Column(GUID(), db.ForeignKey('event.id'), nullable=False)

    @property
    def serialized(self):
        return {
            'id': self.id,
            'person': self.person
        }
