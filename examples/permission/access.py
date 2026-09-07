def can_read(actor, record):
    if actor is None:
        return False
    return actor["tenant"] == record["tenant"] and actor["role"] == "reader"
