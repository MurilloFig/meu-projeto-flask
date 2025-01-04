from flask import Flask, render_template, request, redirect, url_for
import json

app = Flask(__name__)

# Função para carregar posts de um arquivo JSON
def load_posts():
    try:
        with open("posts.json", "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return []

# Função para salvar posts no arquivo JSON
def save_posts(posts):
    with open("posts.json", "w") as file:
        json.dump(posts, file)

# Carrega os posts do arquivo JSON ao iniciar o servidor
posts = load_posts()

@app.route("/")
def home():
    return render_template("index.html", posts=posts)

@app.route("/post/<int:post_id>")
def post(post_id):
    if post_id < len(posts):
        post = posts[post_id]
        return render_template("post.html", post=post)
    else:
        return "Post não encontrado.", 404

@app.route("/new_post", methods=["GET", "POST"])
def new_post():
    if request.method == "POST":
        title = request.form.get("title")
        content = request.form.get("content")
        author = request.form.get("author")
        new_post = {"title": title, "content": content, "author": author}
        posts.append(new_post)
        save_posts(posts)  # Salva os posts no arquivo JSON
        return redirect(url_for("home"))
    return render_template("new_post.html")

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0') 