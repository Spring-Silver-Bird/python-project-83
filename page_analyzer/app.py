import os

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from flask import (
    Flask,
    abort,
    flash,
    get_flashed_messages,
    redirect,
    render_template,
    request,
    url_for,
)

from page_analyzer.data_base import UrlData
from page_analyzer.url_validator import normalize_url, validate_url

load_dotenv()
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
DATABASE_URL = os.getenv('DATABASE_URL')

url_data = UrlData(DATABASE_URL)


def parse_seo(html):
    soup = BeautifulSoup(html, 'html.parser')
    h1 = soup.h1.get_text(strip=True) if soup.h1 else ''
    title = soup.title.get_text(strip=True) if soup.title else ''
    meta_description = soup.find('meta', attrs={'name': 'description'})
    description = (
        meta_description.get('content', '') if meta_description else ''
    )
    return h1, title, description


@app.route('/')
def index():
    """Render main page"""
    messages = get_flashed_messages()
    return render_template('index.html', messages=messages, url='')


@app.route("/urls", methods=["GET"])
def urls():
    """
    Displays a list of all URLs in the database with their latest check status.
    Sorted by ID in descending order (newest first).
    """
    urls = url_data.get_existing_urls()
    return render_template("urls.html", urls=urls)


@app.route("/urls", methods=["POST"])
def add_url():
    url = request.form.to_dict()
    errors = validate_url(url['url'])

    if errors:
        flash("Некорректный URL", "danger")
        return render_template(
            "index.html",
            url=url.get('url', ''),
        ), 422

    normalized_url = normalize_url(url['url'])
    repo = UrlData(DATABASE_URL)
    url_info = repo.find_url(normalized_url)
    if url_info is not None:
        flash('Страница уже существует', 'danger')
        return redirect(url_for('url_detail', url_id=url_info.get('id')))
    url_id = repo.insert_new_url(normalized_url)
    flash("Страница успешно добавлена", "success")
    return redirect(url_for("url_detail", url_id=url_id))


@app.route("/urls/<int:url_id>")
def url_detail(url_id):
    """
    Displays detailed information about a specific URL:
    - URL metadata
    - All historical checks (status codes, timestamps)
    """
    url_info = url_data.find_id(url_id)
    checks = url_data.get_url_checks(url_id)

    if not url_info:
        abort(404)

    return render_template(
        'url_detail.html', url=url_info, urls_checked=checks
    )


@app.route("/urls/<int:url_id>/checks", methods=['POST'])
def check_url(url_id):
    url_row = url_data.find_id(url_id)
    if not url_row:
        abort(404)
    url = url_row['name']
    try:
        r = requests.get(url, timeout=10)
    except requests.exceptions.RequestException:
        flash('Произошла ошибка при проверке', 'danger')
        return redirect(url_for('url_detail', url_id=url_id))

    status_code = r.status_code
    if str(status_code)[0] in {'4', '5'}:
        flash('Произошла ошибка при проверке', 'danger')
        return redirect(url_for('url_detail', url_id=url_id))

    h1, title, desc = parse_seo(r.text)

    url_data.add_url_check(
        {
            'status': status_code,
            'h1': h1,
            'title': title,
            'description': desc,
        },
        {'id': url_id},
    )
    flash('Страница успешно проверена', 'success')
    return redirect(url_for('url_detail', url_id=url_id))


@app.errorhandler(404)
def page_not_found(_error):
    return render_template('404.html'), 404


@app.errorhandler(500)
def server_error(_e):
    return render_template('500.html'), 500
