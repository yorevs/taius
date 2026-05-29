import json
import math
import os


DEFAULT_ROUTING_THRESHOLD = 0.60


def load_router_config(router_config_path, core_dir):
    default_config = {
        "routing_threshold": DEFAULT_ROUTING_THRESHOLD
    }

    if not os.path.exists(router_config_path):
        os.makedirs(core_dir, exist_ok=True)

        with open(router_config_path, "w") as file:
            json.dump(default_config, file, indent=2, sort_keys=True)

        return default_config

    with open(router_config_path, "r") as file:
        config = json.load(file)

    if "routing_threshold" not in config:
        config["routing_threshold"] = DEFAULT_ROUTING_THRESHOLD

    return config


def save_router_config(config, router_config_path, core_dir):
    os.makedirs(core_dir, exist_ok=True)

    with open(router_config_path, "w") as file:
        json.dump(config, file, indent=2, sort_keys=True)


def get_routing_threshold(router_config_path, core_dir):
    config = load_router_config(router_config_path, core_dir)
    return float(config.get("routing_threshold", DEFAULT_ROUTING_THRESHOLD))


def load_router_model(router_model_path):
    with open(router_model_path, "r") as file:
        return json.load(file)


def predict_skill_with_router(input_data: str, skills, router_model_path, tokenize_router_text):
    if not os.path.exists(router_model_path):
        return None, 0.0

    model = load_router_model(router_model_path)
    tokens = tokenize_router_text(input_data)

    labels = model["labels"]
    vocabulary = model["vocabulary"]
    word_counts = model["word_counts"]

    total_docs = sum(labels.values())
    vocab_size = max(1, len(vocabulary))

    scores = {}

    for label, label_count in labels.items():
        score = math.log(label_count / total_docs)
        total_words = sum(word_counts[label].values())

        for token in tokens:
            token_count = word_counts[label].get(token, 0)
            score += math.log((token_count + 1) / (total_words + vocab_size))

        scores[label] = score

    if not scores:
        return None, 0.0

    selected_name = max(scores, key=scores.get)

    max_score = max(scores.values())
    exp_scores = {
        label: math.exp(score - max_score)
        for label, score in scores.items()
    }
    total_exp_score = sum(exp_scores.values())
    confidence = exp_scores[selected_name] / total_exp_score if total_exp_score else 0.0

    for skill in skills:
        if skill["name"] == selected_name:
            return skill, confidence

    return None, 0.0


def route_to_skill(input_data: str, skills, router_model_path, tokenize_router_text, get_routing_threshold):
    for skill in skills:
        module = skill["module"]

        if not hasattr(module, "can_handle"):
            continue

        if module.can_handle(input_data):
            return skill, "direct", 1.0

    routed_skill, confidence = predict_skill_with_router(input_data, skills, router_model_path, tokenize_router_text)

    if routed_skill is None:
        return None, "none", 0.0

    threshold = get_routing_threshold()

    if confidence < threshold:
        return None, "below-threshold", confidence

    return routed_skill, "router", confidence

