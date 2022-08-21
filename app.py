import json
import babel
import datetime
import dateutil.parser
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
import datetime

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
db.init_app(app)

# TODO: connect to a local postgresql database
migrate = Migrate(app,db)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#
db = SQLAlchemy()

class Venue(db.Model):
  __tablename__ = 'venue'

  id = db.Column(db.Integer, primary_key=True,nullable=False)
  name = db.Column(db.String)
  city = db.Column(db.String(120))
  state = db.Column(db.String(120))
  address = db.Column(db.String(120))
  phone = db.Column(db.String(120))
  image_link = db.Column(db.String(500))
  facebook_link = db.Column(db.String(120))
  # TODO: implement any missing fields, as a database migration using Flask-Migrate
  website_link = db.Column(db.String(120))
  description = db.Column(db.String)
  is_talent =db.Column(db.Boolean, default=False) 
  genres = db.Column(db.ARRAY(db.String(120)))
  created_at = db.Column(db.DateTime, default= datetime.datetime.utcnow())
  shows = db.relationship('Show',backref='venue',lazy=True,cascade="all,delete",passive_deletes=True)
  def __repr__(self):
    return f'<Venue id={self.id} name={self.name}>'



class Artist(db.Model):
  __tablename__ = 'artist'
  id = db.Column(db.Integer, primary_key=True,nullable=False)
  name = db.Column(db.String)
  city = db.Column(db.String(120))
  state = db.Column(db.String(120))
  phone = db.Column(db.String(120))
  image_link = db.Column(db.String(500))
  facebook_link = db.Column(db.String(120))
  genres = db.Column(db.ARRAY(db.String(120)))
  created_at = db.Column(db.DateTime, default= datetime.datetime.utcnow())

  # TODO: implement any missing fields, as a database migration using Flask-Migrate
  website_link = db.Column(db.String(120))
  description = db.Column(db.String)
  is_venue =db.Column(db.Boolean, default=False) #looking for venue
  shows = db.relationship('Show',backref='artist',lazy=True,cascade="all,delete",passive_deletes=True)

  def __repr__(self):
    return f'<Artist id={self.id} name={self.name}>'



# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
class Show(db.Model):
  __tablename__ ='show'
  id = db.Column(db.Integer, primary_key=True,nullable=False)
  start_time= db.Column(db.String)
  artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'),nullable=False)
  venue_id = db.Column(db.Integer, db.ForeignKey('venue.id'),nullable=False)
  created_at = db.Column(db.DateTime, default= datetime.datetime.utcnow())

  def __repr__(self):
    return f'<show id={self.id} artist={self.artist_id} venue={self.venue_id}>'


#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

with app.app_context():
  db.create_all()

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
  cities_state = set()
  all_venues = Venue.query.all()

  for venue in all_venues:
    cities_state.add((venue.city,venue.state))

  cities = []
  for city,state in cities_state:
    cities.append({
      "city":city,
      "state":state,
      "venues":[]
    })

  for venue in all_venues:
    for city_object in cities:
      if venue.city == city_object.get('city') and venue.state == city_object.get('state'):
          upcoming_shows = len(Show.query.join(Venue).filter(Show.start_time > datetime.datetime.utcnow()).all())

          city_object['venues'].append({
            "id": venue.id,
            "name": venue.name,
            "num_upcoming_shows": upcoming_shows
          })

  return render_template('pages/venues.html', areas=cities);


@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  search_query = request.form.get('search_term') # get search query
  search_result = Venue.query.filter(Venue.name.ilike('%' + search_query + '%')).all() # get venue by query results
  search_array= []

  for data in search_result:
    num_upcoming_shows= Show.query.filter(Show.venue_id == data.id).count() 
    search_array.append({
      "id":data.id,
      "name":data.name,
     "num_upcoming_shows":num_upcoming_shows 
    })

  response={
    "count": len(search_array),
    "data": search_array
  }
 
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  venue = Venue.query.filter(Venue.id == venue_id ).first()
  past_shows_all = Show.query.join(Venue, Show.venue_id == venue_id).filter(Show.start_time <= datetime.datetime.utcnow()).all()
  upcoming_shows_all = Show.query.join(Venue, Show.venue_id == venue_id).filter(Show.start_time > datetime.datetime.utcnow()).all()
  past_shows=[] #prepare list of past shows
  for show in past_shows_all:
    past_shows.append({
      "artist_id": show.artist_id,
      "artist_name": show.artist.name,
      "artist_image_link":show.artist.image_link,
      "start_time": show.start_time
    })
  #prepare list of upcoming shows
  upcoming_shows=[]
  for show in upcoming_shows_all:
    upcoming_shows.append({
      "artist_id": show.artist_id,
      "artist_name": show.artist.name,
      "artist_image_link":show.artist.image_link,
      "start_time": show.start_time
    })

# prepare data object for artist
  data ={
    "id": venue.id,
    "name": venue.name,
    "genres": venue.genres,
    "address":venue.address,
    "city":venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website": venue.website_link,
    "facebook_link":venue.facebook_link,
    "seeking_talent":venue.is_talent,
    "seeking_description": venue.description,
    "image_link": venue.image_link,
    "past_shows":  past_shows,
    "upcoming_shows":   upcoming_shows,
    "past_shows_count":len(past_shows),
    "upcoming_shows_count":len(upcoming_shows), 
  }


  # data = list(filter(lambda d: d['id'] == venue_id, [data1]))[0]
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
  name = request.form.get('name')
  city = request.form.get('city')
  state = request.form.get('state')
  address = request.form.get('address')
  phone = request.form.get('phone')
  genres = request.form.getlist('genres')
  facebook_link = request.form.get('facebook_link')
  image_link = request.form.get('image_link')
  website_link = request.form.get('website_link')
  seeking_description = request.form.get('seeking_description')
  seeking_talent = True if request.form.get('seeking_talent') == 'y' else False 
  venue_form =VenueForm(request.form)
  # TODO: modify data to be the data object returned from db insertion
  try:
    new_venue = Venue(name=name,description=seeking_description,city=city, state=state, address=address, phone=phone, genres=genres, facebook_link=facebook_link,website_link=website_link, image_link=image_link,  is_talent=seeking_talent)
    db.session.add(new_venue)
    db.session.commit()
    # on successful db insert, flash success
    flash('Venue ' + new_venue.name + ' was successfully listed!')
  except:
    db.session.rollback()
  # TODO: on unsuccessful db insert, flash an error instead.
    flash('An error occurred. Venue ' + new_venue.name+ ' could not be listed.','error')
  finally:
    db.session.close()
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    return render_template('pages/home.html')


@app.route('/venues/<venue_id>', methods=['POST'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  venue = Venue.query.filter(Venue.id == venue_id).first()
  
  try:
    for show in venue.shows:
      db.session.delete(show)
    db.session.delete(venue)
    db.session.commit()
    flash('Venue ' + venue.name + ' was deleted')
  except:
    db.session.rollback()
    flash("Error deleting venue")
  finally:
    db.session.close()
  return redirect(url_for('index'))

  
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage


#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  artist_arr= []
  for data in Artist.query.all():
    artist_arr.append({
      "id":data.id,
      "name":data.name,
    })
  return render_template('pages/artists.html', artists= artist_arr)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  search_query = request.form.get('search_term') # get search query
  search_result = Artist.query.filter(Artist.name.ilike('%' + search_query + '%')).all() 
  search_array= []
  for data in search_result:
    search_array.append({
      "id":data.id,
      "name":data.name,
    })

  response={
    "count": len(search_array),
    "data": search_array
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  artist = Artist.query.filter(Artist.id == artist_id).first()
  past_shows_all = Show.query.join(Artist, Show.artist_id == artist.id).filter(Show.start_time <= datetime.datetime.utcnow()).all()
  upcoming_shows_all = Show.query.join(Artist, Show.artist_id == artist.id).filter(Show.start_time > datetime.datetime.utcnow()).all()

  past_shows=[]
  for show in past_shows_all:
    past_shows.append({
      "venue_id": show.venue_id,
      "venue_name": show.venue.name,
      "venue_image_link":show.venue.image_link,
      "start_time": show.start_time
    })
  
  upcoming_shows=[]
  for show in upcoming_shows_all:
    upcoming_shows.append({
      "venue_id": show.venue_id,
      "venue_name": show.venue.name,
      "venue_image_link":show.venue.image_link,
      "start_time": show.start_time
    })

# setting data object for artist
  data ={
    "id": artist.id,
    "name": artist.name,
    "genres": artist.genres,
    "city":artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website": artist.website_link,
    "facebook_link":artist.facebook_link,
    "seeking_venue":artist.is_venue,
    "seeking_description": artist.description,
    "image_link": artist.image_link,
    "past_shows":  past_shows,
    "upcoming_shows":   upcoming_shows,
    "past_shows_count":len(past_shows),
    "upcoming_shows_count":len(upcoming_shows), 
  }
  
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  artist = Artist.query.filter(Artist.id==artist_id).first()
  form = ArtistForm()
  form.name.data = artist.name
  form.genres.data  = artist.genres
  form.city.data  = artist.city
  form.state.data  = artist.state
  form.phone.data  = artist.phone
  form.image_link.data  = artist.image_link
  form.facebook_link.data  = artist.facebook_link
  form.seeking_venue.data  = artist.is_venue
  form.seeking_description.data  =artist.description
  form.website_link.data = artist.website_link
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> 
  artist_form =  ArtistForm(request.form)
  artist = Artist.query.filter(Artist.id==artist_id).first()
  name = request.form.get('name')
  city = request.form.get('city')
  state = request.form.get('state')
  address = request.form.get('address')
  phone = request.form.get('phone')
  genres = request.form.getlist('genres')
  facebook_link = request.form.get('facebook_link')
  image_link = request.form.get('image_link')
  website_link = request.form.get('website_link')
  seeking_description = request.form.get('seeking_description')
  seeking_venue = True if request.form.get('seeking_venue') == 'y' else False 

# Setting new  Value for artist
  artist.name = name
  artist.genres = genres
  artist.city = city
  artist.state =state
  artist.phone = phone
  artist.image_link = image_link
  artist.facebook_link = facebook_link
  artist.description = seeking_description
  artist.website_link = website_link
  artist.is_venue = seeking_venue
  try:
    db.session.commit()
    flash(f'update to artist {artist.name} successfull')
  except:
    db.session.rollback()
    flash('an error occurred while updating')
  finally:
    db.session.close()
  return redirect(url_for('show_artist',artist_id=artist.id))

  return redirect(url_for('show_artist', artist_id=artist.id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.filter(Venue.id==venue_id).first()
  form.name.data = venue.name
  form.genres.data  = venue.genres
  form.city.data  = venue.city
  form.address.data = venue.address
  form.state.data  = venue.state
  form.phone.data  = venue.phone
  form.image_link.data  = venue.image_link
  form.facebook_link.data  = venue.facebook_link
  form.seeking_talent.data  = venue.is_talent
  form.seeking_description.data  =venue.description
  form.website_link.data = venue.website_link
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  venue = Venue.query.filter(Venue.id==venue_id).first() # find the venue to be edited

  name = request.form.get('name')
  city = request.form.get('city')
  state = request.form.get('state')
  address = request.form.get('address')
  phone = request.form.get('phone')
  genres = request.form.getlist('genres')
  facebook_link = request.form.get('facebook_link')
  image_link = request.form.get('image_link')
  website_link = request.form.get('website_link')
  seeking_description = request.form.get('seeking_description')
  seeking_talent = True if request.form.get('seeking_talent') == 'y' else False  

# Setting Venue Data
  venue.name = name
  venue.genres = genres
  venue.city = city
  venue.state =state
  venue.address = address
  venue.phone = phone
  venue.image_link = image_link
  venue.facebook_link = facebook_link
  venue.description = seeking_description
  venue.website_link = website_link
  venue.is_talent = seeking_talent
  try:
    db.session.commit()
    flash(f'update to venue {venue.name} successfull')
  except:
    db.session.rollback()
    flash('an error occurred while updating')
  finally:
    db.session.close()
  return redirect(url_for('show_venue',venue_id=venue.id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # TODO: insert form data as a new Artist record in the db, instead
  # get form data
  name = request.form.get('name')
  city = request.form.get('city')
  state = request.form.get('state')
  phone = request.form.get('phone')
  genres = request.form.getlist('genres')
  facebook_link = request.form.get('facebook_link')
  image_link = request.form.get('image_link')
  website_link = request.form.get('website_link')
  seeking_description = request.form.get('seeking_description')
  seeking_venue = True if request.form.get('seeking_talent') =='y' else False 
  
  # TODO: modify data to be the data object returned from db insertion
  try:
    new_artist = Artist(name=name,description=seeking_description,city=city, state=state, phone=phone, genres=genres, facebook_link=facebook_link,website_link=website_link, image_link=image_link,  is_venue=seeking_venue)
    db.session.add(new_artist)
    db.session.commit()
    # on successful db insert, flash success
    flash('Artist ' + new_artist.name + ' was successfully listed!')
  except:
    db.session.rollback()
  # TODO: on unsuccessful db insert, flash an error instead.
    flash('An error occurred. Artist ' + new_artist.name+ ' could not be listed.','error')
  finally:
    db.session.close()
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')
    


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  data=[]

  for show in Show.query.filter(Show.artist_id != None).filter(Show.venue_id != None ).all(): 
    print(show.start_time)
    new_show = {
      "venue_id": show.venue_id,
      "venue_name": show.venue.name,
      "artist_id": show.artist_id,
      "artist_name": show.artist.name,
      "artist_image_link":show.artist.image_link,
      "start_time": show.start_time
    }
    data.append(new_show)
  
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
  artist_id = request.form.get('artist_id')
  venue_id = request.form.get('venue_id')
  start_time = request.form.get('start_time')
  # new_show = Show(artist_id=artist_id, venue_id=venue_id, start_time=start_time)
  new_show = Show(artist_id=artist_id, venue_id=venue_id)

  try:
    db.session.add(new_show)
    db.session.commit()
    # on successful db insert, flash success
    flash('Show was successfully listed!')
  except:
    # TODO: on unsuccessful db insert, flash an error instead.
    db.session.rollback()
    flash('An error occurred. Show could not be listed.','error')
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