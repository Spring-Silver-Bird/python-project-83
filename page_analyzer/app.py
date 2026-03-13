from dotenv import load_dotenv
import os
from flask import (
    Flask,
    render_template,
    redirect,
    url_for,
    flash,
    get_flashed_messages,
    request)
from urllib.parse import urlparse


from page_analyzer.url_validator import normalize_url, validate_url
from page_analyzer.data_base import (
    get_existing_urls,
    insert_new_url,
    is_url_existing,
    get_url_id,
    get_url_data,
    get_url_checks,
    add_url_checks,)


load_dotenv()
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
DATABASE_URL = os.getenv('DATABASE_URL')



@app.route('/')
def index():
    """Render main page"""
    return render_template('index.html')

@app.route("/urls", methods=["GET"])
def urls():
    """
    Displays a list of all URLs in the database with their latest check status.
    Sorted by ID in descending order (newest first).
    """

    urls = get_existing_urls()
    return render_template("urls.html", urls=urls)

@app.route("/urls", methods=["POST"])
def add_url():
    new_url = request.form.get('url')
    errors = validate_url(new_url)
    if errors:
        flash("Некорректный URL", "danger")
        return render_template(
            "index.html",
            flashed_messages=get_flashed_messages(with_categories=True),
        ), 422

    normalized_url = normalize_url(new_url)
    if is_url_existing(normalized_url):
        flash("Страница уже существует", "info")
        url_id = get_url_id(normalized_url)
        return redirect(url_for("url_detail", url_id=url_id))

    url_id = insert_new_url(normalized_url)
    flash("Страница успешно добавлена", "success")
    return redirect(url_for("url_detail", url_id=url_id))


@app.route("/urls/<int:url_id>")
def url_detail(url_id):
    """
    Displays detailed information about a specific URL:
    - URL metadata
    - All historical checks (status codes, timestamps)
    """

    url_info = get_url_data(url_id)
    checks = get_url_checks(url_id) or None

    return render_template("url_detail.html", url=url_info, urls_checked=checks)

@app.route("/urls/<int:url_id>/checks", methods=['POST'])
def check_url(url_id):
    url_info = get_url_data(url_id)
    print('Try checked...')
    try:
        check = add_url_checks(url_id)
        flash('Страница успешно проверена', 'success')
        return redirect(url_for('url_detail', url_id=url_id))
    except Exception as e:
        flash('Произошла ошибка при проверке', 'danger')
        return redirect(url_for('url_detail', url_id=url_id))
