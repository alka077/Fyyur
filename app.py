#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler

from forms import *
from flask_migrate import Migrate
from models import *

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app,db)
# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():

  # TODO: replace with real venues data.
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
  data = []
  places = db.session.query(Venue.city, Venue.state).distinct(Venue.city, Venue.state).all()
  for place in places:
    city = place.city
    state =place.state
    venues = Venue.query.filter(Venue.state == place.state).filter(Venue.city == place.city).all()
    upcoming_shows = []
    for venue in venues:
      upcoming_shows.append({
        "id": venue.id,
        "name": venue.name,
        "new_upcoming_shows" : len(db.session.query(Show).filter(Show.start_time > datetime.now()).all())
      })
      data.append({
        "city": city,
        "state": state,
        "venues": upcoming_shows
      })

  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  search_term = request.form.get('search_term','')
  venues = db.session.query(Venue).filter(Venue.name.ilike('%{}%'.format(search_term))).all()
  data =[]
  for venue in venues:
    num_upcoming_shows = 0
    shows = db.session.query(Show).filter(Show.venue_id == venue.id)
    for show in shows:
      if (show.start_time > datetime.now()):
        num_upcoming_shows += 1

    data.append({
        "id": venue.id,
        "name": venue.name,
        "num_upcoming_shows": num_upcoming_shows
    })
  response={
    "count": len(venues),
    "data": data
    # "data": [{
    #   "id": 2,
    #   "name": "The Dueling Pianos Bar",
    #   "num_upcoming_shows": 0,
    # }]
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id

  venue = Venue.query.get_or_404(venue_id)
  shows = db.session.query(Show, Artist).join(Artist).filter(Artist.id==Show.artist_id).filter(Show.venue_id==venue_id)
  upcoming_shows = []
  past_shows = []
  for show, artist in shows:
    tmp_show = {
        'artist_id': artist.id,
        'artist_name': artist.name,
        'artist_image_link': artist.image_link,
        'start_time': str(show.start_time)
    }
    if show.start_time <= datetime.now():
        past_shows.append(tmp_show)
    else:
        upcoming_shows.append(tmp_show)
  #data = vars(venue)
  data={
      "id": venue.id,
      "name": venue.name,
      "genres": [venue.genres],
      "address": venue.address,
      "city": venue.city,
      "state": venue.state,
      "phone": venue.phone,
      "website_link": venue.website_link,
      "facebook_link": venue.facebook_link,
      #"seeking_talent": venue.seeking_talent,
      "seeking_description": venue.seeking_description,
      "image_link": venue.image_link,}
  data['past_shows'] = past_shows
  data['upcoming_shows'] = upcoming_shows
  data['past_shows_count'] = len(past_shows)
  data['upcoming_shows_count'] = len(upcoming_shows)

  return render_template('pages/show_venue.html', venue=data)
#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  form = VenueForm(request.form)
  venue = Venue(
      name = form.name.data,
      city = form.city.data,
      state= form.state.data,
      address = form.address.data,
      phone = form.phone.data,
      website_link = form.website_link.data,
      facebook_link = form.facebook_link.data,
      genres = ','.join(form.genres.data),
      image_link = form.image_link.data,
      #seeking_talent = form.seeking_talent.data,
      seeking_description = form.seeking_description.data
    )
  try:
    db.session.add(venue)
    db.session.commit()
     # on successful db insert, flash success
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  except:
    db.session.rollback()
    # TODO: on unsuccessful db insert, flash an error instead.
    flash('An error occurred. Venue ' + venue.name + ' could not be listed.')
  finally:
    db.session.close()

 
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  try:
    Venue.query.filter_by(id=venue_id).delete()
    db.session.commit()
    flash('Venue was successfully deleted!')
  
  except:
    db.session.rollback()
    flash('issue occured! could not be deleted')
  finally:
    db.session.close()

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database

  data = db.session.query(Artist).order_by('id')
  
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # search for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".5

  search_term = request.form.get('search_term','')
  artists = db.session.query(Artist).filter(Artist.name.ilike('%{}%'.format(search_term))).all()
  response={
    "count": len(artists),
    "data": artists
    # "data": [{
    #   "id": 4,
    #   "name": "Guns N Petals",
    #   "num_upcoming_shows": 0,
    # }]
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  
  artist = Artist.query.get_or_404(artist_id)
  shows = db.session.query(Show, Venue).join(Venue).filter(Show.venue_id==Venue.id).filter(Show.artist_id == artist_id)
  #shows = db.session.query(Show,Venue).join(Venue).filter(Show.venue_id==Venue.id).all()
  upcoming_shows = []
  past_shows = []  
  for show, venue in shows:
    tmp_show = {
      'venue_id': venue.id,
      'venue_name': venue.name,
      'venue_image_link': venue.image_link,
      'start_time': str(show.start_time)
    }
    if show.start_time <= datetime.now():
      past_shows.append(tmp_show)
    else:
      upcoming_shows.append(tmp_show)
  data = vars(artist)
  data['past_shows'] = past_shows
  data['upcoming_shows'] = upcoming_shows
  data['past_shows_count'] = len(past_shows)
  data['upcoming_shows_count'] = len(upcoming_shows)
  
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm(request.form)
  artist = db.session.query(Artist).filter(Artist.id == artist_id).one()

  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

  form = ArtistForm(request.form)
  artist = db.session.query(Artist).get(artist_id)
  artist.name = form.name.data
  artist.city = form.city.data
  artist.state = form.state.data
  artist.phone = form.phone.data
  artist.genres = form.genres.data
  artist.facebook_link = form.facebook_link.data
  artist.website_link = form.website_link.data
  artist.image_link = form.image_link.data
  artist.seeking_description = form.seeking_description.data

  try:
    db.session.add(artist)
    db.session.commit()
    flash('Artist ' + artist.name + ' was successfully edited!')
  except:
    flash('An error occurred. Artist ' + artist.data + 'could not be edited')
    db.session.rollback()
  finally:
    db.session.close()

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm(request.form)
  venue = db.session.query(Venue).filter(Venue.id == venue_id).one()
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  form = VenueForm(request.form)
  venue = db.session.query(Venue).get(venue_id)
  venue.name = form.name.data
  venue.city = form.city.data
  venue.state = form.state.data
  venue.phone = form.phone.data
  venue.genres = ','.join(form.genres.data)
  venue.facebook_link = form.facebook_link.data
  venue.website_link = form.website_link.data
  venue.seeking_description = form.seeking_description.data

  try:
    db.session.add(venue)
    db.session.commit()
    flash('Venue ' + venue.name + ' was successfully edited!')
  except:
    flash('An error occurred. Venue ' + venue.data + 'could not be edited')
    db.session.rollback()

  finally:
    db.session.close()
  
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion

  form = ArtistForm(request.form)
  artist = Artist(
      name = form.name.data,
      city = form.city.data,
      state = form.state.data,
      phone = form.phone.data,
      genres = ','.join(form.genres.data),
      image_link = form.image_link.data,
      facebook_link = form.facebook_link.data,
      website_link = form.website_link.data,
      #seeking_venue = form.seeking_venue.data,
      seeking_description = form.seeking_description.data
    )
  try:
    db.session.add(artist)
    db.session.commit()
    flash('Artist ' + form.name.data + ' was successfully listed!')
  except:
    db.session.rollback()
    flash('An error occurred. Artist ' + artist.name + ' could not be listed.')
  finally:
    db.session.close()

  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  data = []
  shows = db.session.query(Show).all()
  for show in shows:
    venue_id = show.venue_id
    artist_id = show.artist_id
    start_time = str(show.start_time)
    venue = db.session.query(Venue).get(show.venue_id)
    venue_name = venue.name
    artist = db.session.query(Artist).get(show.artist_id)
    artist_name = artist.name
    artist_image_link = artist.image_link
    
    data.append({
      "venue_id": venue_id,
      "venue_name": venue_name,
      "artist_id": artist_id,
      "artist_name": artist_name,
      "artist_image_link": artist_image_link,
      "start_time": start_time
    })

  # data=[{
  #   "venue_id": 1,
  #   "venue_name": "The Musical Hop",
  #   "artist_id": 4,
  #   "artist_name": "Guns N Petals",
  #   "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
  #   "start_time": "2019-05-21T21:30:00.000Z"
  # }]
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  
  form = ShowForm(request.form)
  shows = Show(
    artist_id = form.artist_id.data,
    venue_id = form.venue_id.data,
    start_time = form.start_time.data   
  )
  try:
    db.session.add(shows)
    db.session.commit()
    flash('Show was successfully listed!')
  except:
    db.session.rollback()
    flash('An error occurred. Show could not be listed.')
  
  finally:
    db.session.close()

  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
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
