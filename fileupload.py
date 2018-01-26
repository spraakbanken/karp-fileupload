# -*- coding: utf-8 -*-
import os
import glob
import logging
import config
import time
from flask import Flask, request, redirect, flash, render_template, Markup, send_from_directory, url_for
from flask_table import Table, Col
import requests
import urllib2
from werkzeug.utils import secure_filename


"""
Script for file upload
Inspired by: http://flask.pocoo.org/docs/0.11/patterns/fileuploads/
"""

app = Flask(__name__)
app.secret_key = config.SECRET_KEY
log = logging.getLogger('fileupload.' + __name__)


@app.route('/hello')
def hello_world():
    log.info("hello!")
    flash("Hello!", category="success")
    return render_template('index.html', file_extensions=valid_extensions())


@app.route('/', methods=['GET', 'POST'])
def upload_file():
    preview_name = request.args.get('show')

    if request.method == 'POST':
        try:
            user = request.environ['REMOTE_USER']
            # log.info("User: %s", user)

            # URL upload
            # log.info('request %s' % request.form.keys())
            if "url" in request.form:
                # User did not specify any URL
                if not request.form["url"]:
                    flash(u"Du har inte angett någon länk!", category="warning")
                    log.warning("No URL input! User: %s" % user)
                    return redirect(request.url)

                else:
                    upload_url = request.form["url"]
                    try:
                        contenttype = get_content_type(upload_url)
                    except Exception as e:
                        log.exception("Unexpected error with URL: %s User: %s Error was: %s" % (upload_url, user, e))
                        flash(u'Någonting gick fel. Är du säker på att länken går till en bild?', category="error")
                        return redirect(request.url)

                    # Wrong content type
                    if not content_is_image(contenttype):
                        flash(u"Denna länk innehåller ingen bilddata!", category="error")
                        log.info('Invalid content type in %s User: %s' % (upload_url, user))
                        return redirect(request.url)

                    filename = create_filename(contenttype)
                    # filename = create_filename_simple(upload_url)
                    url = os.path.join(config.FILES_URL, filename)
                    log.info("Upload %s from URL: %s User: %s" % (filename, upload_url, user))
                    fileobj = requests.get(upload_url)
                    with open(os.path.join(config.UPLOAD_FOLDER, filename), "wb") as f:
                        f.write(fileobj.content)
                        flash(Markup('<a href="%s">%s</a> har laddats upp!' % (url, filename)), category="success")
                    log.info("uploaded to %s User: %s" % (url, user))

            # Local file upload
            else:
                upload_files = request.files.getlist("file[]")

                # User did not select a file
                if not upload_files[0]:
                    flash(u"Du har inte valt någon fil!", category="warning")
                    log.warning("No file selected! User: %s" % user)
                    return redirect(request.url)
                else:
                    for fileobj in upload_files:
                        filename = secure_filename(fileobj.filename)
                        # File looks good, upload!
                        if file_valid(filename, user):
                            url = os.path.join(config.FILES_URL, filename)
                            log.info("uploading file %s User: %s" % (filename, user))
                            fileobj.save(os.path.join(config.UPLOAD_FOLDER, filename))
                            flash(Markup('<a href="%s">%s</a> har laddats upp!' % (url, filename)), category="success")

        # Unexpected error
        except Exception as e:
            log.exception("Unexpected error: %s User: %s" % (e, user))
            flash(u'Någonting gick fel. Försök igen eller kontakta sb-karp@svenska.gu.se.', category="error")
            return redirect(request.url)

    table = make_table()
    return render_template('index.html', preview=preview_name, table=table, file_extensions=valid_extensions())


@app.route('/files/<path:filename>')
def send_file(filename):
    """Serve images from upload folder."""
    return send_from_directory("files", filename)


def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in config.ALLOWED_EXTENSIONS


def file_valid(filename, user):
    """Checks if a file is valid for upload. Prints error messages otherwise."""
    # File already exists
    if filename in os.listdir(config.UPLOAD_FOLDER):
        flash("%s: fil finns redan!" % filename, category="error")
        log.error("%s: file already exists! User: %s" % (filename, user))
        return False
    # Invalid file extension
    if not allowed_file(filename):
        log.error("Invalid file extension for file %s User: %s" % (filename, user))
        flash(u"%s: ogiltig filändelse! Följande filändelser är tillåtna: %s" %
              (filename, valid_extensions()), category="error")
        return False
    return True


def get_content_type(url):
    """Get the content type from a URL."""
    # Add headers to pretend to be a browser, some pages block crawling
    hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
           'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
           'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
           'Accept-Encoding': 'none',
           'Accept-Language': 'en-US,en;q=0.8',
           'Connection': 'keep-alive'}
    # TODO cannot handle other encodings than ascii
    # Dan has some ideas how to solve this with idna
    req = HeadRequest(url, headers=hdr)
    # log.info('request: %s' % req)
    response = urllib2.urlopen(req)
    # log.info('response: %s' % response)
    maintype = response.headers['Content-Type'].split(';')[0].lower()
    # log.info("maintype: %s" % maintype)
    return maintype


class HeadRequest(urllib2.Request):
    def get_method(self):
        return 'HEAD'


def content_is_image(maintype):
    """Check if HTML content type is an image."""
    return maintype in ('image/png', 'image/jpeg', 'image/gif')


def create_filename(contenttype):
    """Create filename from current date and time."""
    log.debug("filename for %s" % contenttype)
    extension = "." + get_file_ext(contenttype)
    filename = time.strftime("%Y-%m-%d_%H%M%S") + extension
    # Filename exists, add int
    n = 0
    while filename in os.listdir(config.UPLOAD_FOLDER):
        n += 1
        filename = time.strftime("%Y-%m-%d_%H%M%S_") + str(n) + extension
    return filename


def create_filename_simple(url):
    if "/" in url:
        filename = url.rsplit("/", 1)[-1]
        if "?" in filename:
            filename = filename.rsplit("?", 1)[0]
    return filename


def get_file_ext(maintype):
    "Extract correct file extension from content type."
    return maintype.split("/")[1]


def valid_extensions():
    """Make a string for allowed file extensions."""
    return ", ".join(config.ALLOWED_EXTENSIONS)


def make_table():
    """Create table of uploaded files."""
    items = [Item(a, b, c) for (a, b, c) in get_filelist()]
    sort = request.args.get('sort', 'date')
    reverse = (request.args.get('direction', 'desc') == 'desc')
    items = sorted(items, key=lambda x: getattr(x, sort), reverse=reverse)
    return UploadTable(items, sort_by=sort, sort_reverse=reverse)


class UploadTable(Table):
    """Sortable table with uploaded files."""
    date = Col('Datum')
    name = Col('Fil',)
    location = Col(u'Länk')
    allow_sort = True

    def sort_url(self, col_key, reverse=False):
        if reverse:
            direction = 'desc'
        else:
            direction = 'asc'
        return url_for('upload_file', sort=col_key, direction=direction)


class Item(object):
    def __init__(self, date, name, location):
        self.date = date
        self.name = name
        self.location = location


def get_filelist():
    """Collect list of files in upload folder and return as tuple: filename, URL, preview_path."""

    def get_filename(filepath):
        return os.path.split(filepath)[-1]

    def get_timestamp(filepath):
        return time.strftime('%y-%m-%d %H:%M:%S', time.gmtime(os.path.getmtime(filepath)))

    def get_preview_link(filepath):
        sort = request.args.get('sort')
        direction = request.args.get('direction')
        filename = get_filename(filepath)
        sortstr = "&sort=%s&direction=%s" % (sort, direction)
        if sort and direction:
            link = Markup("<a href='%s?show=%s%s'> %s</a>") % (config.APP_PATH, filename, sortstr, filename)
        else:
            link = Markup("<a href='%s?show=%s'> %s</a>") % (config.APP_PATH, filename, filename)
        return link

    def get_source_url(filepath):
        return os.path.join(config.FILES_URL, get_filename(filepath))

    return [(get_timestamp(i), get_preview_link(i), get_source_url(i)) for i in glob.glob(config.UPLOAD_FOLDER + "/*.*")]


##################

if __name__ == '__main__':
    app.run(port=5012)
