# Contributing to Chinese Immersion Library

Thanks for helping other learners find good Chinese content. Anyone can contribute, and you don't need to know how to code.

## Two ways to add a resource

### 1. Suggest it (no code)

[Open an "Add a resource" issue](https://github.com/krmanik/chinese-immersion-library/issues/new?template=add-resource.yml) and fill in the form: link, category, a one-line description and level. A maintainer will add it.

### 2. Add it yourself (pull request)

1. Fork the repo and open the file for the right category in [`data/`](data/), for example `data/food.json`. The category ids are listed in [`categories.json`](categories.json).
2. Add an entry to the end of the list (see the [examples](#examples) below).
3. Run the scripts (Python 3.9 or newer; no packages needed):

   ```sh
   python3 scripts/enrich.py   # fills in feed, image and channel/podcast ids
   python3 scripts/build.py    # validates, then regenerates README.md, the website and the JSON
   ```

4. Commit everything that changed (`data/`, `README.md` and `dist/`) and open a pull request.

If you can't run the scripts, open the pull request anyway with only your `data/` change, and a maintainer will run them.

> **Don't edit the list in `README.md` or anything in `dist/` by hand.** They are generated from `data/`, and CI fails when they are out of sync.

## What belongs here

A resource should:

- **Be in Chinese, or teach Chinese.** Mandarin first; Cantonese is welcome when marked with `"dialect": "cantonese"`.
- **Be official, licensed or original.** Use the creator's own channel or the rights holder's site.
- **Be useful to a learner** at some level, including native-level content for advanced learners.
- **Still be active or worth keeping as an archive.** Say "archive" in the description if it no longer updates.

Please don't add:

- Piracy sites, unofficial re-uploads of shows or films, or "free manhua/novel" aggregators
- Adult content, gambling, or scams
- Pages that need a paid account before you can see anything (paid services with a free tier are fine; mark them `freemium` or `paid`)
- Your own product without saying so in the pull request (self-promotion is allowed if it's genuinely useful, and disclosed)
- Duplicates. Search `data/` for the URL or channel first.

## Fields

Required: `id`, `name`, `url`, `description`, `category`, `type`, `level`, `script`, `region`, `language`, `pricing`.

| Field | How to fill it |
|---|---|
| `id` | Lowercase letters, digits and dashes, unique across all files. Use the English name, or pinyin for Chinese-only names: `chef-wang`, `gu-shi-fm`. Never rename an existing id, because apps store it. |
| `name` | The name as the creator writes it; add the English name if there is one: `美食作家王刚 Chef Wang` |
| `url` | Homepage or channel page. YouTube: `https://www.youtube.com/@handle`. Bilibili: `https://space.bilibili.com/<uid>`. Podcasts: `https://podcasts.apple.com/podcast/id<number>` |
| `description` | One short English sentence, under 300 characters. Say what it is and why it helps. |
| `category` | Must match the file name, e.g. `food` in `data/food.json` |
| `type` | `website`, `youtube`, `bilibili`, `podcast`, `app` or `newsletter` |
| `level` | Who can follow it: any of `beginner`, `intermediate`, `advanced`. Native content for adults is usually `["advanced"]`; slow, clear native content can be `["intermediate", "advanced"]`; kids' shows are `["beginner"]`. |
| `for_learners` | `true` only if it's made for people learning Chinese |
| `script` | `simplified`, `traditional` or `both` (on-screen text or subtitles) |
| `region` | `cn`, `tw`, `hk`, `sg`, `my` or `global` |
| `dialect` | `mandarin` (default) or `cantonese` |
| `language` | `zh` if all in Chinese, `zh+en` if bilingual or explained in English, `en` if in English about Chinese |
| `pricing` | `free`, `freemium` or `paid` |
| `platforms` | Any of `web`, `ios`, `android` |
| `tags` | Optional, lowercase kebab-case: `comprehensible-input`, `street-food`, `taiwan` |
| `notes` | Optional caveats, e.g. "May load slowly or be unavailable outside mainland China." |

Leave out `feed`, `image` and `ids` and let `scripts/enrich.py` fill them in. For Bilibili, add `"ids": {"bilibili_mid": "<uid>"}` yourself. For podcasts, add `"ids": {"apple_podcast_id": "<number>"}`.

The full schema is in [`schema/resource.schema.json`](schema/resource.schema.json).

## Examples

A YouTube channel (`data/food.json`):

```json
{
  "id": "chef-wang",
  "name": "美食作家王刚 Chef Wang",
  "url": "https://www.youtube.com/@chefwang",
  "description": "Professional Sichuan chef's detailed, no-nonsense recipes.",
  "category": "food",
  "type": "youtube",
  "level": ["intermediate", "advanced"],
  "script": "simplified",
  "region": "cn",
  "language": "zh",
  "pricing": "free",
  "tags": ["recipes", "sichuan"],
  "platforms": ["web", "ios", "android"]
}
```

A podcast for learners (`data/learn_podcast.json`):

```json
{
  "id": "teatime-chinese",
  "name": "TeaTime Chinese 茶歇中文",
  "url": "https://podcasts.apple.com/podcast/id1557463835",
  "description": "Slow, clear Chinese monologues on language, culture and current affairs.",
  "category": "learn_podcast",
  "type": "podcast",
  "level": ["intermediate"],
  "for_learners": true,
  "script": "simplified",
  "region": "cn",
  "language": "zh",
  "pricing": "free",
  "ids": {"apple_podcast_id": "1557463835"}
}
```

A Bilibili creator (`data/science.json`):

```json
{
  "id": "wu-qiong-xiao-liang-de-ke-pu-ri-chang",
  "name": "无穷小亮的科普日常",
  "url": "https://space.bilibili.com/14804670",
  "description": "Biologist Zhang Chenliang identifies strange creatures and debunks myths.",
  "category": "science",
  "type": "bilibili",
  "level": ["advanced"],
  "script": "simplified",
  "region": "cn",
  "language": "zh",
  "pricing": "free",
  "ids": {"bilibili_mid": "14804670"}
}
```

## Fixing or removing an entry

- **Broken link or moved channel:** update `url` and run `enrich.py --force --only youtube` (or the matching type) to refresh its feed.
- **Wrong level or category:** edit the fields. To move an entry to another category, move the object to that file and change `category`; keep the same `id`.
- **Dead resource:** delete the object and say why in the pull request.

## Proposing a new category

Open an issue first. A new category needs an entry in `categories.json` (`id`, `group`, `name`, `name_zh`, an [SF Symbols](https://developer.apple.com/sf-symbols/) `icon` and `description`), a matching `data/<id>.json`, and at least five resources.

## Checks

On every pull request, CI runs `python3 scripts/build.py --check`, which fails on:

- missing or invalid fields, unknown categories, or duplicate ids
- the same URL twice in one category
- `README.md`, `dist/index.html` or `dist/v1/` not regenerated after a data change

`python3 scripts/check_links.py` checks every link. It is also run weekly. Many mainland Chinese sites block bots or time out from outside China. Those show as `blocked` or `unreachable` and are not treated as broken.
