"""Exorcist: an LLM drives out passing mentions and memes, and lays each real recommendation in a crypt.

Reads data/census.json, writes data/videos.json. Progress is saved per batch to data/exorcist.jsonl,
so a run stopped by a rate limit resumes where it left off. Needs OPENROUTER_API_KEY or GROQ_API_KEY.
Usage: python pipeline/exorcise.py [--provider openrouter|groq] [--limit N] [--model openai/gpt-oss-20b] [--batch 20]
"""
import argparse
import json
import os
import sys

from net import load_env, request_json

# Both speak the OpenAI chat API; they differ only in URL, key and how low reasoning effort is requested.
PROVIDERS = {
    "openrouter": ("https://openrouter.ai/api/v1/chat/completions", "OPENROUTER_API_KEY", {"reasoning": {"effort": "low"}}),
    "groq": ("https://api.groq.com/openai/v1/chat/completions", "GROQ_API_KEY", {"reasoning_effort": "low"}),
}
CRYPTS = [
    "Programming Languages", "Software Engineering", "Systems & Performance", "Distributed Systems",
    "Databases", "Security", "AI & Machine Learning", "Web & Frontend", "DevOps & Infrastructure",
    "Networking", "Hardware & Electronics", "Retro Computing", "Computer History", "Graphics & Games",
    "Math", "Physics", "Space", "Biology & Medicine", "Engineering & Making", "Startups & Business",
    "Economics", "Design & UX", "Society & Politics", "History", "Thinking & Learning",
    "Music", "Film & Animation", "Comedy", "Other",
]
PROMPT = f"""You label YouTube videos that at least 3 different Hacker News users linked.
Being linked by many people already means the community values it, so keep is the default.
For each video decide:
- keep: false ONLY for a meme or rickroll, a music video, a product ad, or a short news clip.
  Talks, lectures, speeches, documentaries, tutorials, demos, sketches and short films are true.
  Title null means the video was deleted: judge it from the comments.
- crypt: exactly one of {json.dumps(CRYPTS)}. Pick the closest fit by subject
  (health, nutrition -> Biology & Medicine; law, police, power -> Society & Politics;
  life advice and career talks -> Thinking & Learning). Use "Other" only when nothing is close.
- why: at most 15 words on what the video is and why people recommend it. Plain, no hype.
Reply with JSON only: {{"videos": [{{"id": "...", "keep": true, "crypt": "...", "why": "..."}}]}}"""


def to_prompt(v):
    return {"id": v["id"], "title": v["title"], "channel": v["channel"], "recommenders": v["recommenders"],
            "comments": v["snippets"]}


def parse_labels(content, batch_ids):
    """Keep only well-formed labels for ids we asked about; anything else is retried on the next run."""
    try:
        rows = json.loads(content).get("videos", [])
    except (json.JSONDecodeError, AttributeError, TypeError):  # TypeError: content is null
        return []
    out = []
    for r in rows if isinstance(rows, list) else []:
        if isinstance(r, dict) and r.get("id") in batch_ids and isinstance(r.get("keep"), bool):
            out.append({"id": r["id"], "keep": r["keep"],
                        "crypt": r.get("crypt") if r.get("crypt") in CRYPTS else "Other",
                        "why": str(r.get("why") or "")[:160]})
            batch_ids = batch_ids - {r["id"]}  # first answer per id wins
    return out


def load_jsonl(path):
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--limit", type=int, help="label at most N new videos (sampling)")
    ap.add_argument("--provider", choices=PROVIDERS, default="openrouter")
    ap.add_argument("--model", default="openai/gpt-oss-20b")  # same id on both providers, so labels stay comparable
    ap.add_argument("--batch", type=int, default=20)
    ap.add_argument("--in", dest="inp", default="data/census.json")
    ap.add_argument("--out", default="data/videos.json")
    args = ap.parse_args(argv)
    load_env()
    api, key_name, low_effort = PROVIDERS[args.provider]
    key = os.environ.get(key_name) or sys.exit(f"set {key_name}")
    cache, usage_path = "data/exorcist.jsonl", "data/exorcist_usage.json"

    with open(args.inp, encoding="utf-8") as f:
        census = json.load(f)
    labels = {r["id"]: r for r in load_jsonl(cache)}
    todo = [v for v in census if v["id"] not in labels][:args.limit]
    usage = {"requests": 0, "prompt_tokens": 0, "completion_tokens": 0}
    if os.path.exists(usage_path):
        with open(usage_path, encoding="utf-8") as f:
            usage = json.load(f)

    try:
        for i in range(0, len(todo), args.batch):
            batch = todo[i:i + args.batch]
            extra = low_effort if args.model.startswith("openai/gpt-oss") else {}  # labelling needs little thought
            resp = request_json(api, headers={"Authorization": f"Bearer {key}"}, data={
                **extra, "model": args.model, "temperature": 0, "response_format": {"type": "json_object"},
                "messages": [{"role": "system", "content": PROMPT},
                             {"role": "user", "content": json.dumps([to_prompt(v) for v in batch], ensure_ascii=False)}]})
            usage["requests"] += 1
            usage["prompt_tokens"] += resp["usage"]["prompt_tokens"]
            usage["completion_tokens"] += resp["usage"]["completion_tokens"]
            rows = parse_labels(resp["choices"][0]["message"]["content"], {v["id"] for v in batch})
            with open(cache, "a", encoding="utf-8") as f:
                f.writelines(json.dumps(r, ensure_ascii=False) + "\n" for r in rows)
            labels.update((r["id"], r) for r in rows)
            print(f"exorcist: {min(i + args.batch, len(todo))}/{len(todo)}, {len(rows)}/{len(batch)} labelled, "
                  f"{usage['prompt_tokens'] + usage['completion_tokens']} tokens total", file=sys.stderr)
    finally:  # keep the token count even when a rate limit stops the run
        with open(usage_path, "w", encoding="utf-8") as f:
            json.dump(usage, f, indent=1)

    videos = [{**v, **labels[v["id"]]} for v in census if labels.get(v["id"], {}).get("keep")]
    tmp = args.out + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(videos, f, ensure_ascii=False)
    os.replace(tmp, args.out)
    print(json.dumps({"census": len(census), "labelled": len(labels), "kept": len(videos), **usage}))


if __name__ == "__main__":
    main()
