import os
import re
import json
import html
import xmlrpc.client
import requests
from dotenv import load_dotenv

load_dotenv()


class WordPressClient:
    def __init__(self):
        self.site = os.getenv("WP_SITE", "8bitlegends.com")
        self.username = os.getenv("WP_USERNAME")
        self.app_password = os.getenv("WP_APP_PASSWORD")
        self.api_base = f"https://public-api.wordpress.com/rest/v1.1/sites/{self.site}"
        self.xmlrpc_url = f"https://{self.site}/xmlrpc.php"

    # ── Reading (public API, no auth) ────────────────────────────

    def get_posts(self, count=10, offset=0):
        """Fetch recent posts from the public API."""
        resp = requests.get(
            f"{self.api_base}/posts/",
            params={
                "number": count,
                "offset": offset,
                "fields": "ID,title,date,URL,slug,content,excerpt,tags,categories,featured_image",
            },
        )
        resp.raise_for_status()
        return resp.json()

    def get_all_posts(self):
        """Fetch all posts (paginated)."""
        all_posts = []
        offset = 0
        while True:
            data = self.get_posts(count=20, offset=offset)
            posts = data.get("posts", [])
            if not posts:
                break
            all_posts.extend(posts)
            offset += len(posts)
            if offset >= data.get("found", 0):
                break
        return all_posts

    def get_post(self, post_id):
        """Fetch a single post by ID."""
        resp = requests.get(f"{self.api_base}/posts/{post_id}")
        resp.raise_for_status()
        return resp.json()

    def get_categories(self):
        """Fetch all categories."""
        resp = requests.get(f"{self.api_base}/categories")
        resp.raise_for_status()
        return resp.json()

    def get_tags(self):
        """Fetch all tags."""
        resp = requests.get(f"{self.api_base}/tags", params={"number": 100})
        resp.raise_for_status()
        return resp.json()

    # ── Writing (XML-RPC with application password) ──────────────

    def _get_xmlrpc(self):
        """Get an XML-RPC server proxy."""
        return xmlrpc.client.ServerProxy(self.xmlrpc_url)

    def create_post(self, title, content_html, tags=None, status="draft", featured_image_id=None):
        """Create a new post via XML-RPC.

        Args:
            title: Post title
            content_html: HTML content body
            tags: List of tag strings
            status: 'draft' or 'publish'
            featured_image_id: Media ID for featured image (optional)
        """
        server = self._get_xmlrpc()

        post_data = {
            "post_type": "post",
            "post_status": status,
            "post_title": title,
            "post_content": content_html,
            "terms_names": {
                "category": ["memories"],
            },
        }

        if tags:
            post_data["terms_names"]["post_tag"] = tags

        if featured_image_id:
            post_data["post_thumbnail"] = featured_image_id

        # XML-RPC wp.newPost: blog_id, username, password, content
        post_id = server.wp.newPost(
            0,  # blog_id (0 = default)
            self.username,
            self.app_password,
            post_data,
        )
        return post_id

    def update_post(self, post_id, title, content_html, tags=None, status="publish", featured_image_id=None):
        """Update an existing post via XML-RPC.

        Args:
            post_id: WordPress post ID to update
            title: Post title
            content_html: HTML content body
            tags: List of tag strings
            status: 'draft' or 'publish'
            featured_image_id: Media ID for featured image (optional)
        """
        server = self._get_xmlrpc()

        post_data = {
            "post_status": status,
            "post_title": title,
            "post_content": content_html,
            "terms_names": {
                "category": ["memories"],
            },
        }

        if tags:
            post_data["terms_names"]["post_tag"] = tags

        if featured_image_id:
            post_data["post_thumbnail"] = featured_image_id

        result = server.wp.editPost(
            0,
            self.username,
            self.app_password,
            int(post_id),
            post_data,
        )
        return result  # True on success

    def upload_image(self, image_path):
        """Upload an image via XML-RPC and return the media ID."""
        server = self._get_xmlrpc()

        filename = os.path.basename(image_path)
        ext = os.path.splitext(filename)[1].lower()
        mime_types = {
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".png": "image/png",
            ".gif": "image/gif",
            ".webp": "image/webp",
        }
        mime_type = mime_types.get(ext, "image/jpeg")

        with open(image_path, "rb") as f:
            image_data = f.read()

        media_data = {
            "name": filename,
            "type": mime_type,
            "bits": xmlrpc.client.Binary(image_data),
        }

        result = server.wp.uploadFile(0, self.username, self.app_password, media_data)
        return result  # {'id': ..., 'url': ..., 'file': ..., 'type': ...}

    # ── Helpers ───────────────────────────────────────────────────

    @staticmethod
    def html_to_text(html_content):
        """Strip HTML tags for plain-text preview."""
        text = re.sub(r"<[^>]+>", "", html_content)
        text = html.unescape(text)
        text = re.sub(r"\n{3,}", "\n\n", text).strip()
        return text

    @staticmethod
    def post_to_markdown(post):
        """Convert a WP API post dict to markdown with frontmatter."""
        title = html.unescape(post.get("title", ""))
        date = post.get("date", "")[:10]
        url = post.get("URL", "")
        slug = post.get("slug", "")
        tags = list(post.get("tags", {}).keys())
        categories = list(post.get("categories", {}).keys())
        featured = post.get("featured_image", "")

        frontmatter = [
            "---",
            f"title: \"{title}\"",
            f"date: {date}",
            f"slug: {slug}",
            f"url: {url}",
            f"categories: {json.dumps(categories)}",
            f"tags: {json.dumps(tags)}",
        ]
        if featured:
            frontmatter.append(f"featured_image: {featured}")
        frontmatter.append("---")

        content_text = WordPressClient.html_to_text(post.get("content", ""))

        return "\n".join(frontmatter) + "\n\n" + content_text
