from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user

ia_bp = Blueprint("ia", __name__, url_prefix="/ia")


@ia_bp.route("/", methods=["GET", "POST"])
@login_required
def index():
    # somente professor, admin e super admin
    if current_user.role not in ("ADMIN", "COACH", "SUPER_ADMIN"):
        flash("Você não tem permissão para acessar a área de IA.", "danger")
        return redirect(url_for("dashboard.index"))

    resposta = None
    if request.method == "POST":
        tipo = request.form.get("tipo") or "treino"
        pergunta = (request.form.get("pergunta") or "").strip()

        if not pergunta:
            flash("Descreva o que você precisa da IA.", "danger")
        else:
            # Aqui futuramente você integra com a API de IA (OpenAI, etc.)
            resposta = (
                "Sugestão de resposta da IA (stub):\n\n"
                f"Tipo: {tipo}\n"
                f"Pergunta: {pergunta}\n\n"
                "Aqui entrariam os detalhes gerados pela IA de verdade."
            )

    return render_template("ia_index.html", resposta=resposta)
