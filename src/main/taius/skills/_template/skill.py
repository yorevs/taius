CONFIG = {}


def describe() -> dict:
    return {
        "id": "template.skill",
        "version": "0.1.0",
        "contract_version": "1.0",
        "input_type": "text",
        "output_type": "text",
        "examples": []
    }


def configure(config: dict):
    global CONFIG
    CONFIG = dict(config)


def can_handle(input_data):
    return False


def can_train() -> bool:
    return False


def needs_training() -> bool:
    return False


def train():
    return None


def predict(input_data):
    return str(input_data)


def teach(input_data, expected_output):
    return False


def forget(input_data, expected_output=None):
    return False


def training_examples():
    return []


def export_data():
    return {
        "examples": training_examples()
    }


def import_data(data):
    return None
