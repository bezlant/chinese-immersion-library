# Chinese Immersion Library: JSON API

A curated, filterable JSON directory of **Chinese-language content for learners**: YouTube and Bilibili channels, podcasts, news sites, dramas, manhua, web novels, music, kids' content, dictionaries, apps and more.

It powers the Feed tab in [Hanzi Popup](https://github.com/krmanik/Hanzi-Popup-iOS), but it's plain static JSON, so any app or site can use it.

- **700+ resources** in **34 categories** (live counts in `index.json`)
- **400+ with a machine-readable feed** (YouTube channel feeds, podcast RSS, site RSS/Atom, RSSHub routes for Bilibili), ready for a "latest items" feed
- Filter by level, script, region, dialect, language, pricing, type and tag
- Validated in CI, served from GitHub Pages, no backend

## Endpoints

Base URL (GitHub Pages, after the first deploy):

```
https://krmanik.github.io/chinese-immersion-library/v1/
```

| Path | Contents |
|---|---|
| `index.json` | Manifest: `data_version`, the category list (with counts, icons and paths) and the facet values available for filtering |
| `all.json` | Every resource |
| `feeds.json` | Only resources that have a feed: `{id, name, category, type, feed, image}` |
| `categories/{id}.json` | One category, e.g. `categories/news.json` |

`v1` is the API version. Breaking schema changes go to `v2/`, so app builds already shipped keep working.

### Other ways to fetch the same files

| Option | URL | Notes |
|---|---|---|
| **GitHub Pages** (recommended) | `https://krmanik.github.io/chinese-immersion-library/v1/all.json` | CDN, gzip, `Access-Control-Allow-Origin: *`, about 10 min cache. Updates on every push to `main`. |
| **jsDelivr** | `https://cdn.jsdelivr.net/gh/krmanik/chinese-immersion-library@main/dist/v1/all.json` | Global CDN. Branch URLs are cached up to 12 h. Pin a tag (`@v1.0.0`) for immutable URLs, or purge with `https://purge.jsdelivr.net/gh/krmanik/chinese-immersion-library@main/dist/v1/all.json`. |
| **raw.githubusercontent.com** | `https://raw.githubusercontent.com/krmanik/chinese-immersion-library/main/dist/v1/all.json` | Simplest. 5 min cache, rate-limited, served as `text/plain`, and often unreachable from mainland China. Good for testing. |

Clients should cache the response and compare `data_version` (a content hash that changes only when the data changes) instead of downloading `all.json` every launch. GitHub Pages also sends an `ETag`, so `If-None-Match` requests return `304 Not Modified`.

## Resource schema

Full JSON Schema: [`schema/resource.schema.json`](../schema/resource.schema.json).

```json
{
  "id": "mandarin-corner-youtube",
  "name": "Mandarin Corner",
  "url": "https://www.youtube.com/@MandarinCorner2",
  "description": "Street interviews and long conversations with detailed Chinese/pinyin/English subtitles.",
  "category": "learn_video",
  "type": "youtube",
  "level": ["beginner", "intermediate", "advanced"],
  "script": "simplified",
  "region": "cn",
  "language": "zh",
  "pricing": "free",
  "tags": ["interviews", "subtitles"],
  "for_learners": true,
  "dialect": "mandarin",
  "platforms": ["web", "ios", "android"],
  "feed": {"format": "youtube", "url": "https://www.youtube.com/feeds/videos.xml?channel_id=UC2fAiRQHRQT9aj9P_ijYeow"},
  "ids": {"youtube_channel_id": "UC2fAiRQHRQT9aj9P_ijYeow"},
  "image": "https://yt3.googleusercontent.com/..."
}
```

| Field | Values |
|---|---|
| `type` | `website` `youtube` `bilibili` `podcast` `app` `newsletter` |
| `level` | any of `beginner` `intermediate` `advanced`. Native content is usually `advanced`; kids' content is `beginner`. |
| `for_learners` | `true` when made for learners of Chinese (graded, slow or explained) |
| `script` | `simplified` `traditional` `both` |
| `region` | `cn` `tw` `hk` `sg` `my` `global` |
| `dialect` | `mandarin` (default) `cantonese` |
| `language` | `zh`, `zh+en` (bilingual or English explanations) or `en` |
| `pricing` | `free` `freemium` `paid` |
| `feed.format` | `youtube` (Atom), `podcast` (RSS), `rss`, `atom`, `rsshub` |
| `notes` | Caveats such as "may be slow or unavailable outside mainland China" |

`id`s are stable: once published, an id is never renamed, so apps can store bookmarks and "followed" state by id.

### A note on Bilibili feeds

Bilibili has no public RSS, so Bilibili entries point at [RSSHub](https://docs.rsshub.app/) routes on `rsshub.app`. The public instance is rate-limited. For production, self-host RSSHub and rewrite the host, or fetch Bilibili's own API in the app.

## Categories

Grouped in `categories.json` as **learn**, **read**, **watch** and **listen**. Each category has an `icon` (an SF Symbols name) so the iOS app can render it directly.

| Group | Categories |
|---|---|
| learn | Learn Chinese: Video · Learn Chinese: Podcasts · Graded Reading · Courses & Grammar · Dictionaries & Tools · Learning Apps · HSK & TOCFL · Tutors & Community · About China (English) |
| read | News · Tech · Business & Finance · Science & Knowledge · History & Culture · Web Novels · Literature & Classics · Books & E-books · Comics & Manhua · Social & Forums |
| watch | Streaming Platforms · Drama & Film · Variety & Talk Shows · Comedy & Crosstalk · Documentaries · Vlogs & Lifestyle · Food & Cooking · Travel · Animation (Donghua) · Kids & Family · Gaming · Sports & Fitness |
| listen | Music · Chinese Podcasts · Radio & Audiobooks |

## Using it from Swift

```swift
struct Feed: Decodable { let format: String; let url: URL }
struct Resource: Decodable, Identifiable {
    let id, name, description, category, type, script, region, language, pricing: String
    let url: URL
    let level: [String]
    let tags: [String]
    let forLearners: Bool
    let feed: Feed?
    let image: URL?
}
struct AllResponse: Decodable { let dataVersion: String; let resources: [Resource] }

func loadResources() async throws -> [Resource] {
    let url = URL(string: "https://krmanik.github.io/chinese-immersion-library/v1/all.json")!
    var request = URLRequest(url: url)
    request.cachePolicy = .reloadRevalidatingCacheData   // uses ETag, gets 304 when unchanged
    let (data, _) = try await URLSession.shared.data(for: request)
    let decoder = JSONDecoder()
    decoder.keyDecodingStrategy = .convertFromSnakeCase
    return try decoder.decode(AllResponse.self, from: data).resources
}

// Filtering example: beginner-friendly, made for learners, simplified script
let resources = try await loadResources()
let picks = resources.filter { $0.forLearners && $0.level.contains("beginner") && $0.script != "traditional" }
```

## Repository layout

```
README.md                  intro (hand-written) + the full list (generated between markers)
CONTRIBUTING.md            how to add or fix resources
categories.json            category ids, names, icons, groups (order = display order)
data/<category>.json       the source of truth: edit these
schema/                    JSON Schema for one resource
scripts/build.py           validate data/, generate dist/ and the README list (no dependencies)
scripts/render.py          README list + GitHub Pages site templates
scripts/enrich.py          resolve YouTube channel ids, podcast RSS, artwork, site RSS
scripts/check_links.py     check every URL (and feed with --feeds)
dist/index.html            generated website with search and filters (GitHub Pages root)
dist/v1/                   generated JSON API: do not edit by hand
```

## Contributing

See [CONTRIBUTING.md](../CONTRIBUTING.md). CI runs `build.py --check` on every push and pull request (fails on invalid data or stale generated files), then deploys `dist/` to GitHub Pages. A weekly workflow runs `check_links.py` and uploads a report.

## How the list was built

Seeded from learner resource round-ups (Hacking Chinese, HSK Lord, LTL, The Chairman's Bao, Discover Discomfort and others), then extended across native genres. Every YouTube channel was resolved through YouTube search or its handle page, every podcast through the iTunes lookup API, every Bilibili account through Bilibili's card API, and every URL was link-checked. Dead entries were removed.

## License

Code is MIT. The data (names, descriptions and links) is CC0. Linked content belongs to its owners.
