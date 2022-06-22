from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()


class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String))
    website_link = db.Column(db.String(120))
    looking_for_talent = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(300))
    show = db.relationship('Show',backref = 'show-vanues',  lazy=True)

#db.ARRAY(db.String)
    def __repr__(self):
      return f'<Venues: {self.id}, {self.name}, {self.show}, {self.genres}>'

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(500))
    looking_for_venue = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(300))
    show = db.relationship('Show', backref='artists-show', lazy=True)


    def __repr__(self):
      return f'<Artist:  {self.id}, {self.name}, {self.genres}, {self.show}>'

    # TODO: implement any missing fields, as a database migration using Flask-Migrate
class Show(db.Model):
  __tablename__ = 'show'

  id = db.Column(db.Integer, primary_key=True)
  artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)
  venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
  start_time = db.Column(db.DateTime, nullable=False)

  def __repr__(self):
    return f'<show: {self.id}, {self.Artist_id},{self.Venue_id}, {self.Start_time}>'

