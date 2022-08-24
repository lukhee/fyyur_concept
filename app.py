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
  get_all_venues = Venue.query.all()
  cities = []

  for venue in get_all_venues:
    cities.append({"city": venue.city,"state":venue.state, "venues":[]})

  for venue in get_all_venues:
    for city in cities:
      if venue.city == city.get('city') and venue.state == city.get('state'):
          upcoming_shows = len(Show.query.join(Venue).filter(Show.start_time > datetime.datetime.utcnow()).all())

          city['venues'].append({
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

  structure_search_result= []
  # get search data
  search_result = request.form.get('search_term') 
  search_query_result = Venue.query.filter(Venue.name.ilike('%' + search_result + '%')).all()

  for result in search_query_result:
    num_upcoming_shows= Show.query.filter(Show.venue_id == result.id).count() 
    structure_search_result.append({
      "id":result.id,
      "name":result.name,
     "num_upcoming_shows":num_upcoming_shows 
    })

  response={
    "count": len(structure_search_result),
    "data": structure_search_result
  }
 
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id

  venue = Venue.query.filter(Venue.id == venue_id ).first()
  get_all_past_show = Show.query.join(Venue, Show.venue_id == venue_id).filter(Show.start_time <= datetime.datetime.utcnow()).all()
  get_upcoming_shows = Show.query.join(Venue, Show.venue_id == venue_id).filter(Show.start_time > datetime.datetime.utcnow()).all()

  upcoming_shows=[] #prepare list of upcoming shows
  past_shows=[] #prepare list of past shows
  
  # set past_show data
  for show in get_all_past_show:
    past_shows.append({
      "artist_id": show.artist_id,
      "artist_name": show.artist.name,
      "artist_image_link":show.artist.image_link,
      "start_time": show.start_time
    })

  # set coming_show data
  for show in get_upcoming_shows:
    upcoming_shows.append({
      "artist_id": show.artist_id,
      "artist_name": show.artist.name,
      "artist_image_link":show.artist.image_link,
      "start_time": show.start_time
    })

# artist object data
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
    "image_link": venue.image_link,
    "seeking_talent":venue.is_talent,
    "seeking_description": venue.description,
    "past_shows":  past_shows,
    "upcoming_shows":   upcoming_shows,
    "past_shows_count":len(past_shows),
    "upcoming_shows_count":len(upcoming_shows), 
  }
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
  # TODO: modify data to be the data object returned from db insertion
  try:
    venue_data = Venue(name=name,description=seeking_description,city=city, state=state, address=address, phone=phone, genres=genres, facebook_link=facebook_link,website_link=website_link, image_link=image_link,  is_talent=seeking_talent)
    db.session.add(venue_data)
    db.session.commit()
    # on successful db insert, flash success
    flash('Venue ' + venue_data.name + ' was successfully listed!')
  except:
    db.session.rollback()
  # TODO: on unsuccessful db insert, flash an error instead.
    flash('An error occurred. Venue ' + venue_data.name+ ' could not be listed.','error')
  finally:
    db.session.close()
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    return render_template('pages/home.html')


@app.route('/venues/<venue_id>', methods=['POST'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  
  try:
    venue = Venue.query.filter(Venue.id == venue_id).first()
    db.session.delete(venue)
    db.session.commit()
    flash('Venue ' + venue.name + ' was deleted successfully')
  except:
    db.session.rollback()
    flash("Backend error when deliting")
  finally:
    db.session.close()
  return redirect(url_for('index'))


#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  get_artist = Artist.query.all()

  artist_arr= []
  for data in get_artist:
    artist_arr.append({
      "id":data.id,
      "name":data.name,
    })
  return render_template('pages/artists.html', artists= artist_arr)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # get search data
  search_data = request.form.get('search_term') 
  get_search_result = Artist.query.filter(Artist.name.ilike('%' + search_data + '%')).all() 

  search_arr= []
  for data in get_search_result:
    search_arr.append({
      "id":data.id,
      "name":data.name,
    })

  response={
    "count": len(search_arr),
    "data": search_arr
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  get_artist = Artist.query.filter(Artist.id == artist_id).first()
  get_past_shows = Show.query.join(Artist, Show.artist_id == get_artist.id).filter(Show.start_time <= datetime.datetime.utcnow()).all()
  get_upcoming_shows = Show.query.join(Artist, Show.artist_id == get_artist.id).filter(Show.start_time > datetime.datetime.utcnow()).all()

  upcoming_shows=[] #prepare list of upcoming shows
  past_shows=[] #prepare list of past shows
  
  # set past_show data
  for show in get_past_shows:
    past_shows.append({
      "venue_id": show.venue_id,
      "venue_name": show.venue.name,
      "venue_image_link":show.venue.image_link,
      "start_time": show.start_time
    })
  
  # set coming_show data
  for show in get_upcoming_shows:
    upcoming_shows.append({
      "venue_id": show.venue_id,
      "venue_name": show.venue.name,
      "venue_image_link":show.venue.image_link,
      "start_time": show.start_time
    })

# setting data object for artist
  data ={
    "id": get_artist.id,
    "name": get_artist.name,
    "genres": get_artist.genres,
    "city":get_artist.city,
    "state": get_artist.state,
    "phone": get_artist.phone,
    "website": get_artist.website_link,
    "facebook_link":get_artist.facebook_link,
    "seeking_venue":get_artist.is_venue,
    "seeking_description": get_artist.description,
    "image_link": get_artist.image_link,
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
  get_artist = Artist.query.filter(Artist.id==artist_id).first()
  form = ArtistForm()
  form.name.data = get_artist.name
  form.genres.data  = get_artist.genres
  form.city.data  = get_artist.city
  form.state.data  = get_artist.state
  form.phone.data  = get_artist.phone
  form.image_link.data  = get_artist.image_link
  form.facebook_link.data  = get_artist.facebook_link
  form.seeking_venue.data  = get_artist.is_venue
  form.seeking_description.data  =get_artist.description
  form.website_link.data = get_artist.website_link
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=get_artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> 
  get_artist = Artist.query.filter(Artist.id==artist_id).first()
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
  get_artist.name = name
  get_artist.genres = genres
  get_artist.city = city
  get_artist.state =state
  get_artist.phone = phone
  get_artist.is_venue = seeking_venue
  get_artist.website_link = website_link
  get_artist.image_link = image_link
  get_artist.facebook_link = facebook_link
  get_artist.description = seeking_description
  try:
    db.session.commit()
    flash(f'{get_artist.name} update is successfull')
  except:
    db.session.rollback()
    flash('error in updating')
  finally:
    db.session.close()
  return redirect(url_for('show_artist',artist_id=get_artist.id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  # TODO: populate form with fields from artist with ID <artist_id>
  form = VenueForm()
  get_venue = Venue.query.filter(Venue.id==venue_id).first()
  form.name.data = get_venue.name
  form.genres.data  = get_venue.genres
  form.city.data  = get_venue.city
  form.address.data = get_venue.address
  form.state.data  = get_venue.state
  form.phone.data  = get_venue.phone
  form.image_link.data  = get_venue.image_link
  form.facebook_link.data  = get_venue.facebook_link
  form.seeking_talent.data  = get_venue.is_talent
  form.seeking_description.data  =get_venue.description
  form.website_link.data = get_venue.website_link
  return render_template('forms/edit_venue.html', form=form, venue=get_venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  get_venue = Venue.query.filter(Venue.id==venue_id).first()
   # populate Venue data with new  data
  name = request.form.get('name')
  city = request.form.get('city')
  state = request.form.get('state')
  address = request.form.get('address')
  phone = request.form.get('phone')
  genres = request.form.getlist('genres')
  seeking_description = request.form.get('seeking_description')
  seeking_talent = True if request.form.get('seeking_talent') == 'y' else False  
  facebook_link = request.form.get('facebook_link')
  image_link = request.form.get('image_link')
  website_link = request.form.get('website_link')

# Setting Venue Data
  get_venue.name = name
  get_venue.genres = genres
  get_venue.city = city
  get_venue.state =state
  get_venue.address = address
  get_venue.phone = phone
  get_venue.image_link = image_link
  get_venue.facebook_link = facebook_link
  get_venue.description = seeking_description
  get_venue.website_link = website_link
  get_venue.is_talent = seeking_talent
  try:
    db.session.commit()
    flash(f'{get_venue.name} update is successfull')
  except:
    db.session.rollback()
    flash('error while updating please try again')
  finally:
    db.session.close()
  return redirect(url_for('show_venue',venue_id=get_venue.id))

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
  seeking_description = request.form.get('seeking_description')
  seeking_venue = True if request.form.get('seeking_talent') =='y' else False 
  facebook_link = request.form.get('facebook_link')
  image_link = request.form.get('image_link')
  website_link = request.form.get('website_link')
  
  # TODO: modify data to be the data object returned from db insertion
  try:
    artist_data = Artist(name=name,description=seeking_description,city=city, state=state, phone=phone, genres=genres, facebook_link=facebook_link,website_link=website_link, image_link=image_link,  is_venue=seeking_venue)
    db.session.add(artist_data)
    db.session.commit()
    # on successful db insert, flash success
    flash('Artist ' + artist_data.name + ' was successfully !')
  except:
    db.session.rollback()
  # TODO: on unsuccessful db insert, flash an error instead.
    flash('Error occured while listing Artist ' + artist_data.name,'error')
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
  get_show_data = Show.query.all()
  data=[]

  for show in get_show_data:
    clone_show = {
      "venue_id": show.venue_id,
      "venue_name": show.venue.name,
      "artist_id": show.artist_id,
      "artist_name": show.artist.name,
      "artist_image_link":show.artist.image_link,
      "start_time": show.start_time
    }
    data.append(clone_show)
  
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
  new_show = Show(artist_id=artist_id, venue_id=venue_id, start_time=start_time)

  try:
    db.session.add(new_show)
    db.session.commit()
    flash('New Show created successfully!')
  except:
    # TODO: on unsuccessful db insert, flash an error instead.
    db.session.rollback()
    flash('An error occurred while creating new show','error')
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