from dotenv import load_dotenv
import os
from flask import (
    Flask,
    render_template,
    redirect,
    url_for,
    flash,
    request)


from page_analyzer.url_validator import validate_and_normalize_url as validate_url
from page_analyzer.data_base import (
    get_connection,
    insert_new_url,
    get_existing_urls)

load_dotenv()
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')



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
    url_input = request.form.get("url", "").strip()

    try:
        normalized_url = validate_url(url_input)
        domain = urlparse(normalized_url).netloc.lower()

    except ValueError as e:
        flash(str(e), "danger")
        return render_template("index.html", error_message=str(e)), 422

    if is_url_existing(domain):

        return redirect(url_for("url_detail", id=get_url_id(domain)))

    try:
        new_id = insert_new_url(domain)
        flash("Страница успешно добавлена", "success")
        return redirect(url_for("url_detail", id=new_id))

    except Exception as e:
        flash(f"Ошибка при добавлении"
              f" страницы в базу данных: {str(e)}", "danger")
        return redirect(url_for("index"))


@app.route("/urls/<int:id>")
def url_detail(id):
    """
    Displays detailed information about a specific URL:
    - URL metadata
    - All historical checks (status codes, timestamps)
    """

    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM urls WHERE id = %s", (id,))
        url_row = cur.fetchone()
        url = {
            'id': url_row[0],
            'name': url_row[1],
            'created_at': url_row[2]
        } if url_row else None

        cur.execute("SELECT * FROM url_checks"
                    " WHERE url_id = %s ORDER BY id DESC", (id,))
        checks = []
        for check_row in cur.fetchall():
            checks.append({
                'id': check_row[0],
                'status_code': check_row[2],
                'h1': check_row[3],
                'title': check_row[4],
                'description': check_row[5],
                'created_at': check_row[6]
            })

    return render_template("url_detail.html", url=url, checks=checks)