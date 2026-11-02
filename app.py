from flask import Flask, jsonify, request
import db

app = Flask(__name__)
db.init_db()

def validate_post(data):
    errors = []

    if not isinstance(data, dict):
        return ["Request body must be a JSON object"]

    for field in  ["title", "content", "category"]:
        value = data.get(field)
        if not isinstance(value, str) or not value.strip():
            errors.append(f"'{field}' is required and must be a non-empty string")

    tags = data.get("tags")
    if not isinstance(tags, list) or not all(isinstance(tag, str) for tag in tags):
        errors.append("'tags' is required and must be a list of strings")

    return errors


@app.route("/posts", methods = ["GET"])
def list_posts():
    term = request.args.get("term")
    posts = db.get_all_posts(term)
    return jsonify(posts), 200


@app.route("/posts", methods = ["POST"])
def create_post():
    data = request.get_json(silent=True)

    errors = validate_post(data)

    if errors:
        return jsonify({"errors": errors}), 400
    post = db.create_post(
        data["title"].strip(),
        data["content"].strip(),
        data["category"].strip(),
        data["tags"]
    )
    return jsonify(post), 201

@app.route("/posts/<int:post_id>", methods = ["GET"])
def get_post(post_id):
    post = db.get_post(post_id)
    if post is None:
         return jsonify({"error": "Post not found"}), 404
    return jsonify(post), 200


@app.route("/posts/<int:post_id>", methods = ["PUT"])
def update_post(post_id):

    data = request.get_json(silent=True)
    errors = validate_post(data)
    if errors:
        return jsonify({"errors": errors}), 400
    
    post = db.update_post(
        post_id,
        data["title"].strip(),
        data["content"].strip(),
        data["category"].strip(),
        data["tags"],
    )

    if post is None:
        return jsonify({"error": "Post not found"}), 404
    return jsonify(post), 200


@app.route("/posts/<int:post_id>", methods = ["DELETE"])
def delete_post(post_id):
    if not db.delete_post(post_id):
        return jsonify({"error": "Post not found"}), 404
    return "", 204


@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Resource not found"}), 404


@app.errorhandler(405)
def method_not_allowed(e):
    return jsonify({"error": "Method not allowed"}), 405



if __name__ == "__main__":
    app.run(debug=True, port=5002)