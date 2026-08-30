import json
import os
import sys

from collections import Counter, defaultdict
from pathlib import Path
from urllib import request

from dotenv import load_dotenv

from prompts import (
    CONTENT_CATEGORIES,
    CONTENT_CLASSIFICATION_SYSTEM,
    INTERVENTION_SYSTEM,
    build_classification_prompt,
    build_intervention_prompt
)


# =========================================================
# PATH SETUP
# =========================================================

CURRENT_DIR = Path(__file__).resolve().parent

load_dotenv(CURRENT_DIR / ".env")
load_dotenv(CURRENT_DIR.parent / ".env")


def find_project_file(filename):

    possible_paths = [
        CURRENT_DIR / filename,
        CURRENT_DIR.parent / filename
    ]

    for path in possible_paths:

        if path.exists():
            return path

    raise FileNotFoundError(
        f"{filename} could not be found."
    )


PROFILE_PATH = find_project_file(
    "profile.json"
)

SIGNALS_PATH = find_project_file(
    "signals.json"
)


# =========================================================
# OLLAMA
# =========================================================

OLLAMA_URL = os.getenv(
    "OLLAMA_URL",
    "http://localhost:11434/api/chat"
)

OLLAMA_MODEL = os.getenv(
    "OLLAMA_MODEL",
    "llama3.2:3b"
)


def call_ollama(
    system_prompt,
    user_prompt,
    json_mode=False
):

    body = {
        "model": OLLAMA_MODEL,
        "stream": False,

        "messages": [
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": user_prompt
            }
        ]
    }

    if json_mode:
        body["format"] = "json"

    req = request.Request(
        OLLAMA_URL,

        data=json.dumps(
            body
        ).encode(
            "utf-8"
        ),

        headers={
            "Content-Type":
                "application/json"
        },

        method="POST"
    )

    with request.urlopen(
        req,
        timeout=120
    ) as response:

        result = json.loads(
            response
            .read()
            .decode(
                "utf-8"
            )
        )

    return result[
        "message"
    ][
        "content"
    ].strip()


# =========================================================
# JSON HELPERS
# =========================================================

def load_json(path):

    with open(
        path,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


def save_json(
    path,
    data
):

    with open(
        path,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            data,
            file,
            ensure_ascii=False,
            indent=2
        )


def extract_json(text):

    text = text.strip()

    if text.startswith("```"):

        text = text.replace(
            "```json",
            "",
            1
        )

        text = text.replace(
            "```",
            "",
            1
        )

    start = text.find("{")
    end = text.rfind("}")

    if start == -1 or end == -1:

        raise ValueError(
            "Model did not return JSON."
        )

    return json.loads(
        text[start:end + 1]
    )


# =========================================================
# FALLBACK CLASSIFIER
# =========================================================

KEYWORDS = {

    "food_cooking": [
        "yemek",
        "tarif",
        "mutfak",
        "tavuk",
        "recipe",
        "cooking"
    ],

    "fitness": [
        "spor",
        "fitness",
        "antrenman",
        "kosu",
        "workout",
        "exercise"
    ],

    "travel_outdoors": [
        "gezi",
        "seyahat",
        "kamp",
        "doga",
        "yayla",
        "travel"
    ],

    "music": [
        "muzik",
        "gitar",
        "akor",
        "vinil",
        "plak",
        "music"
    ],

    "art_crafts": [
        "sanat",
        "resim",
        "suluboya",
        "seramik",
        "atolye",
        "craft"
    ],

    "technology_learning": [
        "python",
        "yazilim",
        "kodlama",
        "teknoloji",
        "yapayzeka",
        "ai",
        "coding"
    ],

    "gaming": [
        "oyun",
        "gaming",
        "game"
    ],

    "fashion_beauty": [
        "moda",
        "stil",
        "guzellik",
        "ciltbakimi",
        "fashion",
        "beauty"
    ],

    "entertainment": [
        "dizi",
        "eglence",
        "film",
        "movie",
        "series"
    ],

    "study_productivity": [
        "egitim",
        "calisma",
        "verimlilik",
        "study",
        "productivity"
    ],

    "lifestyle_social": [
        "yasam",
        "arkadaslik",
        "rutin",
        "lifestyle"
    ]
}


def fallback_classify(post):

    text = " ".join(
        [
            str(
                post.get(
                    "title",
                    ""
                )
            ),

            str(
                post.get(
                    "caption",
                    ""
                )
            ),

            " ".join(
                post.get(
                    "hashtags",
                    []
                )
            )
        ]
    ).lower()

    best_category = "other"
    best_score = 0

    for category, keywords in KEYWORDS.items():

        score = sum(
            1
            for keyword in keywords
            if keyword in text
        )

        if score > best_score:

            best_category = category
            best_score = score

    return best_category


# =========================================================
# UNIQUE CONTENT
# =========================================================

def content_key(post):

    return (
        str(
            post.get(
                "title",
                ""
            )
        ),
        tuple(
            sorted(
                post.get(
                    "hashtags",
                    []
                )
            )
        )
    )


def get_unique_content(posts):

    unique = {}

    for post in posts:

        key = content_key(
            post
        )

        if key not in unique:

            unique[key] = {
                "id": len(unique),

                "title":
                    post.get(
                        "title",
                        ""
                    ),

                "caption":
                    post.get(
                        "caption",
                        ""
                    ),

                "hashtags":
                    post.get(
                        "hashtags",
                        []
                    )
            }

    return list(
        unique.values()
    )


# =========================================================
# AI CONTENT CLASSIFICATION
# =========================================================

def classify_unique_content(
    unique_items,
    batch_size=10
):

    result_by_id = {}

    for start in range(
        0,
        len(unique_items),
        batch_size
    ):

        batch = unique_items[
            start:start + batch_size
        ]

        prompt = (
            build_classification_prompt(
                batch
            )
        )

        try:

            response = call_ollama(
                CONTENT_CLASSIFICATION_SYSTEM,
                prompt,
                json_mode=True
            )

            parsed = extract_json(
                response
            )

            for item in parsed.get(
                "items",
                []
            ):

                item_id = item.get(
                    "id"
                )

                category = item.get(
                    "category"
                )

                if (
                    item_id is not None
                    and
                    category in CONTENT_CATEGORIES
                ):

                    result_by_id[
                        int(item_id)
                    ] = {
                        "category":
                            category,

                        "confidence":
                            item.get(
                                "confidence",
                                None
                            ),

                        "source":
                            "ai"
                    }

        except Exception as error:

            print(
                "[UNHOOK] AI classification "
                f"fallback: {error}",
                file=sys.stderr
            )

    for item in unique_items:

        if item["id"] not in result_by_id:

            result_by_id[
                item["id"]
            ] = {
                "category":
                    fallback_classify(
                        item
                    ),

                "confidence":
                    None,

                "source":
                    "fallback"
            }

    return result_by_id


# =========================================================
# APPLY CATEGORIES TO PROFILE
# =========================================================

def categorize_posts(
    posts,
    unique_items,
    classification
):

    category_by_key = {}

    for item in unique_items:

        category_by_key[
            (
                item["title"],
                tuple(
                    sorted(
                        item["hashtags"]
                    )
                )
            )
        ] = classification[
            item["id"]
        ]

    categorized_posts = []

    for post in posts:

        new_post = dict(
            post
        )

        result = category_by_key.get(
            content_key(
                post
            )
        )

        if result:

            new_post[
                "category"
            ] = result[
                "category"
            ]

            new_post[
                "category_source"
            ] = result[
                "source"
            ]

        categorized_posts.append(
            new_post
        )

    return categorized_posts


# =========================================================
# CATEGORY PROFILE
# =========================================================

def build_category_summary(
    posts
):

    counter = Counter(
        post.get(
            "category",
            "other"
        )
        for post in posts
    )

    total = (
        len(posts)
        or 1
    )

    distribution = []

    for category, count in counter.most_common():

        distribution.append(
            {
                "category":
                    category,

                "viewed_posts":
                    count,

                "share_percent":
                    round(
                        count
                        / total
                        * 100,
                        1
                    )
            }
        )

    dominant_category = (
        distribution[0][
            "category"
        ]
        if distribution
        else "other"
    )

    return {
        "total_viewed_posts":
            len(posts),

        "dominant_category":
            dominant_category,

        "distribution":
            distribution
    }


# =========================================================
# ACCOUNT CATEGORY
# =========================================================

def categorize_accounts(
    top_accounts,
    posts
):

    account_categories = defaultdict(
        Counter
    )

    for post in posts:

        account = post.get(
            "owner_hash"
        )

        category = post.get(
            "category"
        )

        if account and category:

            account_categories[
                account
            ][
                category
            ] += 1

    result = []

    for account in top_accounts:

        new_account = dict(
            account
        )

        account_hash = (
            account.get(
                "account_hash"
            )
        )

        categories = (
            account_categories.get(
                account_hash
            )
        )

        if categories:

            new_account[
                "category"
            ] = (
                categories
                .most_common(
                    1
                )[0][0]
            )

        result.append(
            new_account
        )

    return result


# =========================================================
# EXAMPLE POSTS FOR PERSONALIZATION
# =========================================================

def get_examples(
    posts,
    category,
    limit=3
):

    examples = []

    for post in posts:

        if (
            post.get(
                "category"
            )
            == category
        ):

            examples.append(
                {
                    "title":
                        post.get(
                            "title"
                        ),

                    "hashtags":
                        post.get(
                            "hashtags",
                            []
                        )
                }
            )

        if len(
            examples
        ) >= limit:

            break

    return examples


# =========================================================
# SIGNAL TRANSLATION
# =========================================================

FLAG_EXPLANATIONS = {

    "gece_agirlikli_kullanim":
        "A meaningful share of recent viewing occurred late at night.",

    "yatis_oncesi_yogunlasma":
        "Recent viewing activity peaks around late evening or bedtime.",

    "dar_hesap_dongusu":
        "Viewing repeatedly concentrates around a relatively small group of accounts.",

    "tek_temada_yogunlasma":
        "Recent viewing shows concentration around a recurring theme."
}


def build_signal_context(
    signals
):

    flags = signals.get(
        "flags",
        []
    )

    return {
        "attention":
            signals.get(
                "attention",
                {}
            ),

        "flags": [
            {
                "id":
                    flag,

                "meaning":
                    FLAG_EXPLANATIONS.get(
                        flag,
                        flag
                    )
            }
            for flag in flags
        ]
    }


# =========================================================
# FALLBACK PERSONALIZED MESSAGE
# =========================================================

def fallback_intervention(
    dominant_category,
    signal_context
):

    late_night = any(
        flag["id"]
        in [
            "gece_agirlikli_kullanim",
            "yatis_oncesi_yogunlasma"
        ]

        for flag
        in signal_context[
            "flags"
        ]
    )

    if late_night:

        if dominant_category == "food_cooking":

            return {
                "message":
                    "Your recent viewing has leaned toward cooking content, and a noticeable part of your activity happens late in the day. How about saving one recipe you liked and actually trying it tomorrow instead of watching another one?",

                "suggested_action":
                    "Save one recipe and try it tomorrow.",

                "used_category":
                    dominant_category
            }

        if dominant_category == "music":

            return {
                "message":
                    "Music shows up often in your recent viewing, especially around a late-evening usage pattern. This could be a good point to leave the feed and save one song or guitar idea to try tomorrow.",

                "suggested_action":
                    "Save one music idea for tomorrow.",

                "used_category":
                    dominant_category
            }

        return {
            "message":
                "Your recent viewing tends to become more concentrated late in the day. Pick one thing you genuinely want to return to tomorrow, save it, and leave the feed there.",

            "suggested_action":
                "Save one item and stop for tonight.",

            "used_category":
                dominant_category
        }

    ACTIONS = {

        "food_cooking":
            "Instead of watching another recipe, how about choosing one you liked and trying to make it?",

        "music":
            "Instead of another music post, how about trying one of the chords or songs yourself?",

        "art_crafts":
            "How about turning one of those art ideas into a quick sketch or small creation of your own?",

        "fitness":
            "How about turning one of those fitness posts into a short real movement break?",

        "technology_learning":
            "How about trying one of the coding or technology ideas yourself before watching another explanation?",

        "travel_outdoors":
            "How about saving one place that caught your attention and turning it into a real future plan?",

        "fashion_beauty":
            "How about stepping away from the feed and actually trying one of the ideas that caught your attention?",

        "gaming":
            "How about choosing intentional play instead of continuing through gaming clips?",

        "study_productivity":
            "How about putting the phone aside and trying a short focused work block?",

        "entertainment":
            "How about choosing one specific thing you actually want to watch instead of continuing through the feed?"
    }

    action = ACTIONS.get(
        dominant_category,
        "How about turning one thing that caught your attention into a real activity away from the feed?"
    )

    return {
        "message":
            action,

        "suggested_action":
            action,

        "used_category":
            dominant_category
    }


# =========================================================
# GENERATIVE INTERVENTION
# =========================================================

def generate_intervention(
    signals,
    category_summary,
    example_posts
):

    signal_context = (
        build_signal_context(
            signals
        )
    )

    prompt = (
        build_intervention_prompt(
            signal_context,
            category_summary,
            example_posts
        )
    )

    try:

        response = call_ollama(
            INTERVENTION_SYSTEM,
            prompt,
            json_mode=True
        )

        parsed = extract_json(
            response
        )

        if not parsed.get(
            "message"
        ):

            raise ValueError(
                "Empty intervention."
            )

        return parsed

    except Exception as error:

        print(
            "[UNHOOK] Intervention AI "
            f"fallback: {error}",
            file=sys.stderr
        )

        return fallback_intervention(
            category_summary[
                "dominant_category"
            ],
            signal_context
        )


# =========================================================
# MAIN PIPELINE
# =========================================================

def run():

    profile = load_json(
        PROFILE_PATH
    )

    signals = load_json(
        SIGNALS_PATH
    )

    posts = profile.get(
        "posts",
        []
    )

    # 1. Find unique post types
    unique_items = (
        get_unique_content(
            posts
        )
    )

    # 2. AI semantic classification
    classification = (
        classify_unique_content(
            unique_items
        )
    )

    # 3. Apply categories
    categorized_posts = (
        categorize_posts(
            posts,
            unique_items,
            classification
        )
    )

    # 4. Create content-interest profile
    category_summary = (
        build_category_summary(
            categorized_posts
        )
    )

    # 5. Fill account categories
    enriched_profile = dict(
        profile
    )

    enriched_profile[
        "posts"
    ] = categorized_posts

    enriched_profile[
        "top_accounts"
    ] = categorize_accounts(
        profile.get(
            "top_accounts",
            []
        ),
        categorized_posts
    )

    enriched_profile[
        "ai_content_summary"
    ] = category_summary

    # 6. Example content from dominant interest
    examples = get_examples(
        categorized_posts,
        category_summary[
            "dominant_category"
        ]
    )

    # 7. Personalized intervention
    intervention = (
        generate_intervention(
            signals,
            category_summary,
            examples
        )
    )

    # 8. Final AI output
    output = {

        "schema_version":
            profile.get(
                "schema_version"
            ),

        "user_id":
            profile.get(
                "user_id"
            ),

        "content_profile":
            category_summary,

        "behavioral_flags":
            signals.get(
                "flags",
                []
            ),

        "intervention":
            intervention
    }

    # Do not overwrite team files.
    categorized_path = (
        PROFILE_PATH.parent
        /
        "profile_categorized.json"
    )

    output_path = (
        PROFILE_PATH.parent
        /
        "ai_output.json"
    )

    save_json(
        categorized_path,
        enriched_profile
    )

    save_json(
        output_path,
        output
    )

    print(
        "\n=== UNHOOK AI ==="
    )

    print(
        "Dominant category:",
        category_summary[
            "dominant_category"
        ]
    )

    print(
        "\nCategory distribution:"
    )

    for item in category_summary[
        "distribution"
    ][:5]:

        print(
            f"- {item['category']}: "
            f"{item['viewed_posts']} posts "
            f"({item['share_percent']}%)"
        )

    print(
        "\nBehavioral flags:"
    )

    for flag in signals.get(
        "flags",
        []
    ):

        print(
            "-",
            flag
        )

    print(
        "\n=== PERSONALIZED INTERVENTION ==="
    )

    print(
        intervention[
            "message"
        ]
    )

    print(
        "\nSuggested action:"
    )

    print(
        intervention.get(
            "suggested_action",
            ""
        )
    )

    print(
        "\nGenerated:"
    )

    print(
        "- profile_categorized.json"
    )

    print(
        "- ai_output.json"
    )


if __name__ == "__main__":
    run()