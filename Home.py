import streamlit as st
from pymongo import MongoClient
from bson import ObjectId

st.set_page_config(
    page_title="Tech Blogs",
    layout="wide"
)

# ---------------- DB with Caching ----------------
@st.cache_resource
def get_mongo_client():
    # return MongoClient("mongodb://localhost:27017")
    return MongoClient(st.secrets["MONGO_URI"])

client = get_mongo_client()
collection = client["markdown-db"]["markdown-collection"]

# ---------------- Query Params ----------------
params = st.query_params
slug = params.get("slug")

# ---------------- Cached Query Function ----------------
@st.cache_data(ttl=300)  # Cache for 5 minutes
def fetch_posts(search_term=None):
    query = {}
    if search_term:
        query = {
            "$or": [
                {"title": {"$regex": search_term, "$options": "i"}},
                {"slug": {"$regex": search_term, "$options": "i"}}
            ]
        }
    return list(
        collection.find(query, {"title": 1, "description": 1, "slug": 1})
    )

@st.cache_data(ttl=300)
def fetch_blog(blog_slug):
    return collection.find_one({"slug": blog_slug})

# ---------------- Sidebar ----------------
st.sidebar.markdown('<h3><a href="/" target="_self" style="text-decoration:none; color:inherit;">📚 Tech Blogs</a></h3>', unsafe_allow_html=True)

search = st.sidebar.text_input("🔍 Search by title or slug")

posts = fetch_posts(search if search else None)

st.sidebar.divider()

for post in posts:
    st.sidebar.markdown(
        f"""
        <a href="?slug={post['slug']}" target="_self" style="text-decoration:none; color:inherit;">
            <strong>{post['title']}</strong>
        </a>
        <br>
        <span style="color:#6b7280; font-size:13px;">
        {post.get('description','')}
        </span>
        <br><br>
        """,
        unsafe_allow_html=True
    )

# ---------------- Main Content ----------------
if not slug:
    st.title("👋 Welcome to Tech Blogs")
    st.write(
        "Deep dives into distributed systems, databases, and backend engineering."
    )

    for post in posts:
        st.subheader(f"{post['title']}")
        st.write(post.get("description", ""))

        st.markdown(
            f'<a href="?slug={post["slug"]}" target="_self">Read more →</a>',
            unsafe_allow_html=True
        )
        st.divider()

else:
    blog = fetch_blog(slug)

    if not blog:
        st.error("Blog not found")
        st.stop()

    st.markdown('<a href="/" target="_self">← Back to Home</a>', unsafe_allow_html=True)

    st.title(blog["title"])
    st.caption(f"📅 {blog.get('date','')}")

    if "tags" in blog:
        st.markdown(" ".join([f"`{t}`" for t in blog["tags"]]))

    st.divider()
    st.markdown(blog["content"])
    st.divider()

# ---------------- Footer ----------------
# st.divider()
st.markdown(
    """
    <div style="text-align: center; padding: 20px 0; color: #6b7280; font-size: 14px;">
        <p style="margin: 5px 0;">
            Built with ❤️ by <strong>Chinmay Ku Jena</strong>
        </p>
        <p style="margin: 5px 0;">
            📧 <a href="mailto:chinmay.jena7878@gmail.com" style="color: #6b7280; text-decoration: none;">chinmay.jena7878@gmail.com</a>
            &nbsp;&nbsp;|&nbsp;&nbsp;
            🐙 <a href="https://github.com/ChinmayKuJena" target="_blank" style="color: #6b7280; text-decoration: none;">GitHub</a>
        </p>
    </div>
    """,
    unsafe_allow_html=True
)
