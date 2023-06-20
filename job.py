import uuid

import llm

from app import app
from db import ModelStatus, db, EmbeddedIndex, Model, model_embedded_index


def create_model(urls, current_user_id, model_name):
    with app.app_context():
        unique_id_index = str(uuid.uuid4())
        entry_model = Model(unique_id_index, model_name, current_user_id)
        db.session.add(entry_model)
        db.session.commit()

        try:
            # Create index
            llm.create_index_from_urls(urls, unique_id_index)
            entry_index = EmbeddedIndex(unique_id_index, current_user_id)
            db.session.add(entry_index)
            db.session.commit()

            entry_model.status = ModelStatus.SUCCESS
            db.session.commit()

            new_entry = model_embedded_index.insert().values(
                model_id=entry_model.id, embedded_index_id=entry_index.id
            )
            db.session.execute(new_entry)
            db.session.commit()

        except Exception:
            entry_model.status = ModelStatus.FAILURE
            db.session.commit()
            raise Exception("Failed to create index")
