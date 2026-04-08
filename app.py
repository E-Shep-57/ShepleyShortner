from flask import Flask, render_template, request, redirect, url_for
from flask_bootstrap import Bootstrap5
import re
import os

app = Flask(__name__)
bootstrap = Bootstrap5(app)

@app.route('/')
def index():
    return render_template('index.html')


def generate_shortcode(url):
    clean_url = re.sub(r'[^a-zA-Z]', '', url).lower()
    shortened = clean_url

    while len(shortened) > 8:
        new_version = ""
        for i in range(0, len(shortened) - 1, 2):
            char1 = shortened[i]
            char2 = shortened[i + 1]
            combined_ascii = (ord(char1) + ord(char2)) // 2
            new_version += chr(combined_ascii)

        shortened = new_version

    return shortened


@app.route('/create', methods=['GET', 'POST'])
def create_link():
    shortcode = None
    original_url = None

    if request.method == 'POST':
        original_url = request.form.get('url')
        if original_url:
            shortcode = generate_shortcode(original_url)

            # Store in mappings.txt
            file_path = os.path.join(app.root_path, 'mappings.txt')
            with open(file_path, 'a') as f:
                f.write(f"{shortcode}|{original_url}\n")
        return redirect(url_for('directory'))

    return render_template('create.html', shortcode=shortcode, original=original_url)


@app.route('/go/<shortcode>')
def go_to_url(shortcode):
    file_path = os.path.join(app.root_path, 'mappings.txt')
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            for line in f:
                if '|' in line:
                    stored_code, original_url = line.strip().split('|')
                    if stored_code == shortcode:
                        return redirect(original_url)
    return render_template('bad_link.html', code=shortcode)

@app.route('/directory')
def directory():
    links_data = []
    file_path = os.path.join(app.root_path, 'mappings.txt')

    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            for line in f:
                if '|' in line:
                    shortcode, original_url = line.strip().split('|')
                    links_data.append({
                        'shortcode': shortcode,
                        'original': original_url
                    })

    return render_template('directory.html', links=links_data)
@app.errorhandler(404)
def page_not_found(e):
    # This remains for global errors (like /random-address)
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(e):
    # This catches logic crashes and file errors
    return render_template('500.html'), 500

if __name__ == '__main__':
    app.run()
