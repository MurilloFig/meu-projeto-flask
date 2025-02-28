import os
import json
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

app = Flask(__name__)

app.secret_key = 'sua-chave-secreta'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# Classe User definida antes da função load_users()
class User(UserMixin):
    def __init__(self, id, username, email, password, telefone="", idade=0, trabalho="", data_criacao=None, casos_investigados=0, casos_solucionados=0, comentarios=0, role="user"):
        self.id = id
        self.username = username
        self.email = email
        self.password = password
        self.telefone = telefone
        self.idade = idade
        self.trabalho = trabalho
        self.data_criacao = data_criacao or datetime.now().strftime("%Y-%m-%d")
        self.casos_investigados = casos_investigados
        self.casos_solucionados = casos_solucionados
        self.comentarios = comentarios
        self.role = role

@property
def tempo_uso(self):
    criacao = datetime.strptime(self.data_criacao, "%Y-%m-%d")
    return (datetime.now() - criacao).days

# Classe Community
class Community:
    def __init__(self, id, name, creator_id, background_image=None, members=None, posts=None):
        self.id = id
        self.name = name
        self.creator_id = creator_id
        self.background_image = background_image
        self.members = members if members else []
        self.posts = posts if posts else []

# Funções de Carregamento e Salvamento de Dados
def load_users():
    try:
        with open("users.json", "r") as file:
            users_data = json.load(file)
            return [User(**user) for user in users_data]
    except FileNotFoundError:
        return []

def save_users(users):
    with open("users.json", "w") as file:
        json.dump([user.__dict__ for user in users], file)

def load_communities():
    try:
        with open("communities.json", "r") as file:
            communities_data = json.load(file)
            return [Community(**community) for community in communities_data]
    except FileNotFoundError:
        return []

def save_communities(communities):
    with open("communities.json", "w") as file:
        json.dump([community.__dict__ for community in communities], file)

@login_manager.user_loader
def load_user(user_id):
    try:
        for user in users:
            if user.id == int(user_id):
                return user
    except ValueError:
        return None
    return None

# Função para carregar usuários de um arquivo JSON
def load_users():
    try:
        with open("users.json", "r") as file:
            users_data = json.load(file)
            return [User(**user) for user in users_data]  # Reconstrói objetos User
    except FileNotFoundError:
        return []

# Função para salvar usuários no arquivo JSON
def save_users(users):
    with open("users.json", "w") as file:
        users_data = [
            {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "password": user.password,
                "telefone": user.telefone,
                "idade": user.idade,
                "trabalho": user.trabalho,
                "data_criacao": user.data_criacao,
                "casos_investigados": user.casos_investigados,
                "casos_solucionados": user.casos_solucionados,
                "comentarios": user.comentarios
            }
            for user in users
        ]
        json.dump(users_data, file)

# Carrega os usuários do arquivo JSON ao iniciar o servidor


# Função para carregar posts de um arquivo JSON
def load_posts():
    try:
        with open("posts.json", "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return []  # Retorna uma lista vazia se o arquivo não existir
    except json.JSONDecodeError:
        print("Erro: O arquivo posts.json está corrompido.")
        return []

# Carrega os usuários do arquivo JSON ao iniciar o servidor    
users = load_users()
communities = load_communities()
posts = load_posts()    

# Funções Auxiliares
@login_manager.user_loader
def load_user(user_id):
    return next((u for u in users if str(u.id) == str(user_id)), None)

def is_admin():
    return current_user.is_authenticated and current_user.role == "admin"

# Rotas de Comunidades
@app.route("/create_community", methods=["GET", "POST"])
@login_required
def create_community():
    if request.method == "POST":
        name = request.form.get("name")
        background_image = request.files.get("background_image")
        background_path = None

        if background_image:
            filename = secure_filename(background_image.filename)
            background_path = os.path.join("static/uploads", filename)
            background_image.save(background_path)
            background_path = f"/{background_path}"

        new_community = Community(id=len(communities), name=name, creator_id=current_user.id, background_image=background_path)
        communities.append(new_community)
        save_communities(communities)
        return redirect(url_for("view_community", community_id=new_community.id))

    return render_template("create_community.html")

@app.route("/community/<int:community_id>")
@login_required
def view_community(community_id):
    community = next((c for c in communities if c.id == community_id), None)
    if not community:
        return "Comunidade não encontrada", 404

    community_posts = [p for p in posts if p.get("community_id") == community_id]
    return render_template("community.html", community=community, posts=community_posts)

@app.route("/community/<int:community_id>/new_post", methods=["GET", "POST"])
@login_required
def new_post_in_community(community_id):
    community = next((c for c in communities if c.id == community_id), None)
    if not community:
        return "Comunidade não encontrada", 404

    if request.method == "POST":
        title = request.form.get("title")
        content = request.form.get("content")
        new_post = {"id": len(posts), "title": title, "content": content, "author": current_user.username, "community_id": community_id}
        posts.append(new_post)
        save_posts(posts)
        return redirect(url_for("view_community", community_id=community_id))

    return render_template("new_post.html", community=community)

# Conta de Administrador
@app.route("/admin")
@login_required
def admin_dashboard():
    if not is_admin():
        return "Acesso negado", 403
    return render_template("admin.html", users=users, communities=communities, posts=posts)
# Função para salvar posts no arquivo JSON
def save_posts(posts):
    with open("posts.json", "w") as file:
        json.dump(posts, file)

# Carrega os posts do arquivo JSON ao iniciar o servidor
posts = load_posts()

# Página inicial
@app.route("/")
def index():
    global posts
    if not isinstance(posts, list):
        print("Erro: `posts` não é uma lista. Resetando para lista vazia.")
        posts = []
        save_posts(posts)
    return render_template("index.html", posts=posts, communities=communities)

# Registro de usuários
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")

        if any(user.email == email for user in users):
            return "E-mail já cadastrado"

        hashed_password = generate_password_hash(password, method="pbkdf2:sha256")
        new_user = User(len(users), username, email, hashed_password)
        users.append(new_user)
        save_users(users)
        return redirect(url_for("login"))
    return render_template("register.html")

# Rota de login
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        for user in users:
            if user.email == email and check_password_hash(user.password, password):
                login_user(user)
                return redirect(url_for("index"))

        return "Credenciais inválidas", 401
    return render_template("login.html")

# Rota de logout
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))

# Rota para o perfil do usuário logado
@app.route("/profile")
@login_required
def profile():
    return render_template("profile.html", user=current_user)

# Rota para o perfil de outro usuário
@app.route("/profile/<username>")
@login_required
def profile_user(username):
    user = next((u for u in users if u.username == username), None)
    if not user:
        return "Usuário não encontrado", 404
    return render_template("profile.html", user=user)

# Criação de novos posts
@app.route("/new_post", methods=["GET", "POST"])
@login_required
def new_post():
    if request.method == "POST":
        title = request.form.get("title")
        content = request.form.get("content")
        author = current_user.username if current_user.is_authenticated else "Anônimo"

        new_post = {"title": title, "content": content, "author": author}
        posts.append(new_post)
        save_posts(posts)
        return redirect(url_for("index"))

    return render_template("new_post.html")

# Visualização de posts
@app.route("/post/<int:post_id>", methods=["GET", "POST"])
def post(post_id):
    if post_id >= len(posts) or post_id < 0:
        return "Post não encontrado.", 404

    if request.method == "POST":
        comment = request.form.get("comment")
        if comment:
            if "comments" not in posts[post_id]:
                posts[post_id]["comments"] = []

            posts[post_id]["comments"].append({
                "author": current_user.username if current_user.is_authenticated else "Anônimo",
                "content": comment
            })

            # Atualiza contagem de casos investigados e comentários
            if current_user.is_authenticated:
                current_user.casos_investigados += 1
                current_user.comentarios += 1
                save_users(users)

            save_posts(posts)

    post = posts[post_id]
    return render_template("post.html", post=post, post_id=post_id)

# Exclusão de posts
@app.route("/delete_post/<int:post_id>", methods=["POST"])
@login_required
def delete_post(post_id):
    if post_id >= len(posts) or post_id < 0:
        return "Post não encontrado.", 404

    if posts[post_id]["author"] != current_user.username:
        return "Você não tem permissão para deletar este post.", 403

    posts.pop(post_id)
    save_posts(posts)
    return redirect(url_for("index"))

@app.route("/upload_photo", methods=["POST"])
@login_required
def upload_photo():
    # Obtém o arquivo enviado
    photo = request.files.get("photo")

    if not photo:
        return "Nenhuma foto foi enviada.", 400

    # Define o caminho onde a foto será salva
    photo_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{current_user.id}.jpg")

    # Salva a foto no servidor
    try:
        photo.save(photo_path)
    except Exception as e:
        print(f"Erro ao salvar a foto: {e}")
        return "Erro ao salvar a foto.", 500

    return redirect(url_for("profile"))

@app.route("/update_profile", methods=["POST"])
@login_required
def update_profile():
    # Obtém os dados enviados no formulário
    telefone = request.form.get("telefone")
    idade = request.form.get("idade")
    email = request.form.get("email")
    trabalho = request.form.get("trabalho")

    # Atualiza os dados do usuário logado
    current_user.telefone = telefone
    current_user.idade = int(idade) if idade.isdigit() else 0
    current_user.email = email
    current_user.trabalho = trabalho

    # Atualiza os dados no arquivo JSON
    save_users(users)

    return redirect(url_for("profile"))

@app.route("/post/<int:post_id>/solve/<int:comment_id>", methods=["POST"])
@login_required
def solve_case(post_id, comment_id):
    if post_id >= len(posts) or post_id < 0:
        return "Post não encontrado.", 404

    if posts[post_id]["author"] != current_user.username:
        return "Você não tem permissão para marcar este caso como solucionado.", 403

    comments = posts[post_id].get("comments", [])
    if comment_id >= len(comments) or comment_id < 0:
        return "Comentário não encontrado.", 404

    solver_username = comments[comment_id]["author"]
    solver = next((u for u in users if u.username == solver_username), None)
    if solver:
        solver.casos_solucionados += 1
        save_users(users)

    return redirect(url_for("post", post_id=post_id))

if __name__ == "__main__":
    app.config['UPLOAD_FOLDER'] = 'static/uploads'
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(debug=True, host='0.0.0.0')