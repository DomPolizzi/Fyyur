#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import (
    Flask,
    render_template,
    request,
    Response, 
    flash, 
    redirect, 
    url_for,
)
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from flask_migrate import Migrate
from forms import ShowForm, VenueForm, ArtistForm
from models import *
import sys
from sqlalchemy.dialects.postgresql import ARRAY
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

# Located in models.py

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#


def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format)


app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#


@app.route('/')
def index():
    return render_template('pages/home.html')

# =================================================================
#  Venues
# =================================================================

@app.route('/venues')
def venues():
    cities = db.session.query(Venue.city, Venue.state).all()
    venues = []
    for city in cities:
      venues_in_city = db.session.query(Venue.id, Venue.name).filter(Venue.city == city[0]).filter(Venue.state == city[1])
      venues.append({
        "city": city[0],
        "state": city[1],
        "venues": venues_in_city
      })
    return render_template('pages/venues.html', areas=venues)

#  ---------------------------------------------------------------
#  Search for Venue
#  ----------------------------------------------------------------

@app.route('/venues/search', methods=['POST'])
def search_venues():
    search_term = request.form.get('search_term', '')
    data = []
    venues = db.session.query(Venue).filter(Venue.name.ilike('%' + search_term + '%')).all()
    
    for venue in venues:
        data.append({
            "id": venue.id,
            "name": venue.name
        })

    response = {
        "count": len(venues),
        "data": data
    }
    return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

#  ---------------------------------------------------------------
#  Define and show Venue
#  ----------------------------------------------------------------

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    venue = db.session.query(Venue).filter(Venue.id == venue_id).one()
    data = {
        "id": venue.id,
        "name": venue.name,
        "genres": venue.genres,
        "address": venue.address,
        "city": venue.city,
        "state": venue.state,
        "webiste": venue.website,
        "phone": venue.phone,
        "facebook_link": venue.facebook_link,
        "seeking_talent": venue.seeking_talent,
        "seeking_description": venue.seeking_description
    }  
    return render_template('pages/show_venue.html', venue=data)

#  ---------------------------------------------------------------
#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)

#  ---------------------------------------------------------------
#  Post Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
   
    form = VenueForm()
    error = False
    print("About to go into venue creation")
    try:
        print("Instantiating venue")
        data = Venue(
            name=form.name.data,
            city=form.city.data,
            genres=form.genres.data,
            state=form.state.data,
            address=form.address.data,
            phone=form.phone.data,
            image_link=form.image_link.data,
            website=form.website.data,
            facebook_link=form.facebook_link.data,
            seeking_talent=form.seeking_talent.data,
            seeking_description=form.seeking_description.data
        )
        print("Adding to database")
        db.session.add(data)
        print("Committing data")
        db.session.commit()
        print("Persisted data")
        flash('Venue ' + request.form['name'] + ' was successfully listed!')
    except Exception as e:
        print(("Rolling back transaction"))
        print(e)
        print(e.args)
        error = True
        db.session.rollback()
    # TODO: on unsuccessful db insert, flash an error instead.
        flash('An error occurred. Venue ' +
              data.name + ' could not be listed.')
        return render_template('pages/home.html')
        print(sys.exc_info())
    finally:
        print("Closing session")
        db.session.close()
        return render_template('pages/home.html')

#  ---------------------------------------------------------------
#  Delete Venue
#  ----------------------------------------------------------------

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):

    try:
        db.session.query(Venue).filter(Venue.id == venue_id).delete()
        print("Committing data")
        db.session.commit()
        flash('Venue was Removed')
    except:
        flash(' an error occured, did not delete venue. ')

    finally:
        db.session.close()
    return redirect(url_for('venues'))

#  ---------------------------------------------------------------
#  Edit Venue
#  ----------------------------------------------------------------

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()
    venue = db.session.query(Venue).filter(Venue.id == venue_id).one()

    return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    form = VenueForm(request.form)
    venue = db.session.query(Venue).filter(Venue.id == venue_id).one()
    
    try:
        print("Instantiating venue edit")
        updated_venue = {
            "name": form.name.data,
            "city": form.city.data,
            "genres": form.genres.data,
            "state": form.state.data,
            "address": form.address.data,
            "phone": form.phone.data,
            "image_link": form.image_link.data,
            "website": form.website.data,
            "facebook_link": form.facebook_link.data,
            "seeking_talent": form.seeking_talent.data,
            "seeking_description": form.seeking_description.data  
        }
        print("Adding to database")
        db.session.query(Venue).filter(Venue.id == venue_id).update(updated_venue)
        
        print("Committing data")
        db.session.commit()
        
        print("Persisted data")
        flash('Venue ' + form.name.data + ' was successfully listed!')
    
    except Exception as e:  
        print(("Rolling back transaction"))
        print(e)
        print(e.args)
        error = True
        db.session.rollback()
        flash('An error occurred. Venue ' +
              form.name.data + ' could not be listed.')
    finally:
        print("Closing session")
        db.session.close()
    return redirect(url_for('show_venue', venue_id=venue_id))

# =================================================================
#  Artists
# =================================================================

@app.route('/artists')
def artists():
    artists = db.session.query(Artist.name, Artist.id).all()
    return render_template('pages/artists.html', artists=artists)

#  ----------------------------------------------------------------
#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)

#  ----------------------------------------------------------------
#  Post Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    form = ArtistForm()
    error = False
    print("About to go into venue creation")
    try:
        print("Instantiating artist")
        data = Artist(
            name=form.name.data,
            city=form.city.data,
            genres=form.genres.data,
            state=form.state.data,
            phone=form.phone.data,
            image_link=form.image_link.data,
            facebook_link=form.facebook_link.data
        )
        print("Adding to database")
        db.session.add(data)
        print("Committing data")
        db.session.commit()
        print("Persisted data")
    # TODO: modify data to be the data object returned from db insertion
        flash('Artist ' + request.form['name'] + ' was successfully listed!')
    except Exception as e:
        print(("Rolling back transaction"))
        print(e)
        print(e.args)
        error = True
        db.session.rollback()
    # TODO: on unsuccessful db insert, flash an error instead.
        flash('An error occurred. Artist ' +
              data.name + ' could not be listed.')
        return render_template('pages/home.html')
        print(sys.exc_info())
    finally:
        print("Closing session")
        db.session.close()
        return render_template('pages/home.html')

#  ---------------------------------------------------------------
#  Search Artist
#  ----------------------------------------------------------------

@app.route('/artists/search', methods=['POST'])
def search_artists():
    search_term = request.form.get('search_term', '')
    data = []
    artists = db.session.query(Artist).filter(Artist.name.ilike('%' + search_term + '%')).all()
    
    for artist in artists:
        data.append({
            "id": artist.id,
            "name": artist.name
        })
    
    response = {
        "count": len(artists),
        "data": data
    }
    return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

#  ---------------------------------------------------------------
#  Define Artist
#  ----------------------------------------------------------------

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    artist = db.session.query(Artist).filter(Artist.id == artist_id).one()
    print(artist)
    data = {
        "id" : artist.id,
        "name" : artist.name,
        "genres": artist.genres,
        "city" : artist.city,
        "state" : artist.state,
        "website": artist.website,
        "phone" : artist.phone,
        "facebook_link" : artist.facebook_link,
        "seeking_venue" : artist.seeking_venue,
        "seeking_description" : artist.seeking_description
    }
    print(data)
    return render_template('pages/show_artist.html', artist=data)

#  ---------------------------------------------------------------
#  Edit Artist
#  ----------------------------------------------------------------

@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()
    artist = db.session.query(Artist).filter(Artist.id == artist_id).one()

    return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    form = ArtistForm(request.form)
    artist = db.session.query(Artist).filter(Artist.id == artist_id).one()
    try:
        print("Instantiating Artist edit")
        updated_artist = {
            "name": form.name.data,
            "city": form.city.data,
            "genres": form.genres.data,
            "state": form.state.data,
            "address": form.address.data,
            "phone": form.phone.data,
            "image_link": form.image_link.data,
            "website": form.website.data,
            "facebook_link": form.facebook_link.data,
            "seeking_talent": form.seeking_talent.data,
            "seeking_description": form.seeking_description.data  
        }
        print("Adding to database")
        db.session.query(Artist).filter(Artist.id == artist_id).update(updated_artist)
        print("Committing data")
        db.session.commit()
        print("Persisted data")
        flash('Artist ' + form.name.data + ' was successfully listed!')

    except Exception as e:  
        print(("Rolling back transaction"))
        print(e)
        print(e.args)
        error = True
        db.session.rollback()
        flash('An error occurred. Artist ' +
              form.name.data + ' could not be listed.')

    finally:
        print("Closing session")
        db.session.close()
    return redirect(url_for('show_artist', artist_id=artist_id))

#  ---------------------------------------------------------------
#  Delete Artist
#  ----------------------------------------------------------------

@app.route('/artists/<artist_id>', methods=['DELETE'])
def delete_artist(artist_id):

    try:
        db.session.query(Artist).filter(Artist.id == artist_id).delete()
        print("Committing data")
        db.session.commit()
        flash('Venue was Removed')
    except:
        flash(' an error occured, did not delete artist. ')

    finally:
        db.session.close()
   
    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage
    return redirect(url_for('artist'))


# =================================================================
#  Shows
# =================================================================

@app.route('/shows')
def shows():
    shows = db.session.query(Show.artist_id, Show.venue_id, Show.start_time).all()
    print(shows)
    data =[]
    print(data)
    for show in shows:
        artist = db.session.query(Artist.name, Artist.image_link).filter(Artist.id == show[0]).one()
        print(artist)
        venue = db.session.query(Venue.name).filter(Venue.id == show[1]).one()
        print(venue)
        data.append({
            "artist_id": show[0],
            "artist_name": artist[0],
            "artist_image_link":artist[1],
            "venue_id": show[1],
            "venue_name":venue[0],
            "start_time":str(show[2])
        })

    return render_template('pages/shows.html', shows=data)


@app.route('/shows/create')
def create_shows():
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    form = ShowForm(request.form)
    error = False
    print("About to go into Show creation")
    try:
        print("Instantiating Show")
        data = Show(
            name=form.name.data,
            venue_id=form.venue_id.data,
            artist_id=form.artist_id.data,
            start_time=form.start_time.data
        )
        print("Adding to database")
        db.session.add(data)
        print("Committing data")
        db.session.commit()
        print("Persisted data")
    # TODO: modify data to be the data object returned from db insertion
        flash('Show ' + request.form['name'] + ' was successfully listed!')
    except Exception as e:
        print(("Rolling back transaction"))
        print(e)
        print(e.args)
        error = True
        db.session.rollback()
    # TODO: on unsuccessful db insert, flash an error instead.
        flash('An error occurred. Show ' +
              data.name + ' could not be listed.')
        return render_template('pages/home.html')
        print(sys.exc_info())
    finally:
        print("Closing session")
        db.session.close()
        return render_template('pages/home.html')

# =================================================================
#  Error Handlers
# =================================================================

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
