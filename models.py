from app import db

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    genres = db.Column(db.String())
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    website = db.Column(db.String())
    facebook_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.String())
    seeking_description = db.Column(db.String())

class Artist(db.Model):
    __tablename__ = 'Artist'    

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String())
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String())
    seeking_venue = db.Column(db.String())
    seeking_description = db.Column(db.String())

class Show(db.Model):
    __tablename__ = 'Show'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    start_time = db.Column(db.DateTime())
    artist_id = db.Column(db.Integer, db.ForeignKey("Artist.id"), nullable=False)
    artist_name = db.relationship('Artist')
    venue_id = db.Column(db.Integer, db.ForeignKey("Venue.id"), nullable=False)
    venue_name = db.relationship('Venue')
    start_time = db.Column(db.DateTime())