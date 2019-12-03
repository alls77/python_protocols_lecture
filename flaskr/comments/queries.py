def get_comment_list(db, post_id):
    return db.execute(
        "SELECT comment.id, text, created, post_id, author_id, username"
        " FROM comment JOIN user ON comment.author_id = user.id"
        " WHERE post_id = ?"
        " ORDER BY created DESC",
        (post_id,)
    ).fetchall()


def get_comment(db, id):
    return db.execute(
        "SELECT comment.id, text, created, post_id, author_id, username"
        " FROM comment JOIN user ON comment.author_id = user.id"
        " WHERE  comment.id = ?",
        (id,)
    ).fetchone()


def create_comment(db, post_id, author_id, text):
    db.execute(
        "INSERT INTO comment (post_id, author_id, text) VALUES (?, ?, ?)", (post_id, author_id, text))
    db.commit()


def update_comment(db, id, text):
    db.execute(
        "UPDATE comment SET text = ? WHERE id = ?", (text, id))
    db.commit()


def delete_comment(db, id):
    db.execute("DELETE FROM comment WHERE id = ?", (id,))
    db.commit()
